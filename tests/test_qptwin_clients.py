# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Unit and subprocess smoke tests for qpTwin multi-client profiles."""
from pathlib import Path
import sys, json, importlib.util, tomllib, subprocess, os
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('universal',ROOT/'scripts/generate_qptwin_configs.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

def _config(tmp_path):
    return mod.generate(tmp_path,Path(sys.executable))

def test_all_profiles_have_expected_structure(tmp_path):
    configs=_config(tmp_path)
    assert len(configs)==12
    simple=['cursor','antigravity','claude-code','gemini-cli','windsurf','cline','roo-code']
    for key in simple:
        c=json.loads(configs[mod.CLIENT_PATHS[key]])
        assert c['mcpServers']['qptwin']['command']==str(Path(sys.executable).resolve())
        assert c['mcpServers']['qptwin']['env']['TWINDEV_WORKSPACE']==str(tmp_path.resolve())
    v=json.loads(configs[mod.CLIENT_PATHS['vscode']])
    assert v['servers']['qptwin']['type']=='stdio'
    c=json.loads(configs[mod.CLIENT_PATHS['openclaw']])['mcp']['servers']['qptwin']
    assert c['transport']=='stdio' and c['enabled'] is True
    c=json.loads(configs[mod.CLIENT_PATHS['opencode']])['mcp']['servers']['qptwin']
    assert c['command']==[str(Path(sys.executable).resolve()),'-m','twindev_mcp.offline_stdio']
    assert c['environment']['TWINDEV_WORKSPACE']==str(tmp_path.resolve())
    c=tomllib.loads(configs[mod.CLIENT_PATHS['codex']])['mcp_servers']['qptwin']
    assert c['env']['TWINDEV_WORKSPACE']==str(tmp_path.resolve())
    h=configs[mod.CLIENT_PATHS['hermes']]
    assert 'mcp_servers:' in h and 'qptwin:' in h and 'TWINDEV_WORKSPACE:' in h

def test_official_mode_uses_sdk_entry_point(tmp_path):
    c=mod.generate(tmp_path,Path(sys.executable),'official')
    for val in c.values():
        assert 'twindev_mcp.server' in val

def test_does_not_overwrite_or_write_outside_destination(tmp_path):
    source=tmp_path/'workspace';source.mkdir()
    out=tmp_path/'out';settings=mod.generate(source,Path(sys.executable))
    paths=mod.write_presets(settings,out)
    assert len(paths)==12
    old=paths[0].read_bytes()
    with pytest.raises(FileExistsError):mod.write_presets(settings,out)
    assert old==paths[0].read_bytes()
    assert not (source/'.cursor').exists()

def test_missing_workspace_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):mod.generate(tmp_path/'missing',Path(sys.executable))

def test_live_stdio_qptwin_workspace(tmp_path):
    env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),TWINDEV_WORKSPACE=str(tmp_path))
    messages=[{'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'qptwin-smoke','version':'0.4'}}},
              {'jsonrpc':'2.0','method':'notifications/initialized','params':{}},
              {'jsonrpc':'2.0','id':2,'method':'tools/list','params':{}},
              {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'workspace_overview','arguments':{}}}]
    with subprocess.Popen([sys.executable,'-m','twindev_mcp.offline_stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env) as p:
        stdout,stderr=p.communicate(''.join(json.dumps(m)+'\n' for m in messages),timeout=15)
    assert p.returncode==0,stderr
    replies=[json.loads(x) for x in stdout.splitlines()]
    assert len(replies)==3
    assert len(replies[1]['result']['tools'])==23
    assert replies[2]['result']['isError'] is False
