#!/usr/bin/env python3
# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Produce review-only qpTwin local MCP configuration presets.

No program or SDK installs. No network. Does not modify application global
settings and will not overwrite generated files unless --force is specified.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

CLIENT_PATHS = {
    "cursor": "configs/cursor/.cursor/mcp.json",
    "codex": "configs/codex/.codex/config.toml",
    "antigravity": "configs/antigravity/.agents/mcp_config.json",
    "claude-code": "configs/claude-code/.mcp.json",
    "hermes": "configs/hermes/config-snippet.yaml",
    "openclaw": "configs/openclaw/mcp-snippet.json",
    "opencode": "configs/opencode/opencode.json",
    "gemini-cli": "configs/gemini-cli/.gemini/settings.json",
    "windsurf": "configs/windsurf/mcp_config.json",
    "cline": "configs/cline/cline_mcp_settings.json",
    "roo-code": "configs/roo-code/.roo/mcp.json",
    "vscode": "configs/vscode/.vscode/mcp.json",
}
NAME = 'qptwin'

def generate(workspace: Path, python: Path, mode: str = 'legacy') -> dict[str,str]:
    workspace=workspace.expanduser().resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError('workspace must be a directory')
    python=python.expanduser().resolve(strict=True)
    if not python.is_file():
        raise ValueError('Python executable does not exist')
    if mode not in ('legacy','official'):
        raise ValueError('mode must be legacy or official')
    args=['-m', 'twindev_mcp.offline_stdio' if mode=='legacy' else 'twindev_mcp.server']
    cmd=str(python); env={'TWINDEV_WORKSPACE':str(workspace)}
    stdio={'command':cmd,'args':args,'env':env}
    as_json=lambda x: json.dumps(x,ensure_ascii=False,indent=2)+'\n'
    toml=(''+f'[mcp_servers.{NAME}]\n'
          +f'command = {json.dumps(cmd)}\n'
          +f'args = {json.dumps(args)}\n'
          +f'env = {{ TWINDEV_WORKSPACE = {json.dumps(str(workspace),ensure_ascii=False)} }}\n'
          +'startup_timeout_sec = 20\ntool_timeout_sec = 120\n')
    # JSON strings are valid YAML strings. The Hermes config uses mcp_servers (snake case).
    yaml=('mcp_servers:\n'
          f'  {NAME}:\n'
          f'    command: {json.dumps(cmd,ensure_ascii=False)}\n'
          f'    args: {json.dumps(args,ensure_ascii=False)}\n'
          f'    env:\n      TWINDEV_WORKSPACE: {json.dumps(str(workspace),ensure_ascii=False)}\n')
    out={
        'cursor': as_json({'mcpServers':{NAME:{'type':'stdio',**stdio}}}),
        'codex':toml,
        'antigravity':as_json({'mcpServers':{NAME:stdio}}),
        'claude-code':as_json({'mcpServers':{NAME:stdio}}),
        'hermes':yaml,
        'openclaw':as_json({'mcp':{'servers':{NAME:{'transport':'stdio', **stdio, 'enabled':True}}}}),
        'opencode':as_json({'$schema':'https://opencode.ai/config.json','mcp':{'servers':{NAME:{'type':'local','command':[cmd,*args], 'environment':env}}}}),
        'gemini-cli':as_json({'mcpServers':{NAME:stdio}}),
        'windsurf':as_json({'mcpServers':{NAME:stdio}}),
        'cline':as_json({'mcpServers':{NAME:stdio}}),
        'roo-code':as_json({'mcpServers':{NAME:stdio}}),
        'vscode':as_json({'servers':{NAME:{'type':'stdio',**stdio}}}),
    }
    return {CLIENT_PATHS[k]:v for k,v in out.items()}

def write_presets(configs: dict[str,str], output:Path, *,force:bool=False) -> list[Path]:
    out=output.expanduser().resolve()
    paths=[out/rel for rel in configs]
    if not force and any(p.exists() for p in paths):
        raise FileExistsError('Existing config; aborting without changes. Use a fresh output directory.')
    for rel,value in configs.items():
        p=out/rel
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(value,encoding='utf-8')
    return paths

def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description='Generate qpTwin config snippets for 12 MCP clients')
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--python',type=Path,default=Path(sys.executable))
    parser.add_argument('--mode',choices=['legacy','official'],default='legacy')
    parser.add_argument('--force',action='store_true')
    a=parser.parse_args(argv)
    try:
        paths=write_presets(generate(a.workspace,a.python,a.mode),a.output,force=a.force)
    except (ValueError,OSError) as exc:
        parser.exit(2,f'ERROR: {exc}\n')
    print('\n'.join(map(str,paths)))
    return 0
if __name__=='__main__':raise SystemExit(main())
