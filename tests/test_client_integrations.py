# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Host configuration contract tests plus a real legacy stdio MCP smoke test."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("client_config_generator", ROOT / "scripts/generate_client_configs.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def test_presets_use_one_local_server_for_four_clients(tmp_path):
    configs = mod.generate(tmp_path, Path(sys.executable), "official")
    assert set(configs) == {".cursor/mcp.json", ".codex/config.toml", ".agents/mcp_config.json", ".mcp.json"}
    cursor = json.loads(configs[".cursor/mcp.json"])["mcpServers"]["qptwin"]
    antigravity = json.loads(configs[".agents/mcp_config.json"])["mcpServers"]["qptwin"]
    claude = json.loads(configs[".mcp.json"])["mcpServers"]["qptwin"]
    codex = tomllib.loads(configs[".codex/config.toml"])["mcp_servers"]["qptwin"]
    for config in [cursor, antigravity, claude, codex]:
        assert config["command"] == str(Path(sys.executable).resolve())
        assert config["args"] == ["-m", "twindev_mcp.server"]
        assert config["env"]["TWINDEV_WORKSPACE"] == str(tmp_path.resolve())


def test_legacy_mode(tmp_path):
    configs = mod.generate(tmp_path, Path(sys.executable), "legacy")
    assert "offline_stdio" in configs[".cursor/mcp.json"]


def test_refuses_to_clobber_existing_configs(tmp_path):
    workspace = tmp_path / "repo"
    workspace.mkdir()
    out = tmp_path / "out"
    configs = mod.generate(workspace, Path(sys.executable), "official")
    mod.write_presets(configs, out)
    try:
        mod.write_presets(configs, out)
    except FileExistsError:
        pass
    else:
        raise AssertionError("config overwrite should be refused")


def test_workspace_path_must_exist(tmp_path):
    try:
        mod.generate(tmp_path / "absent", Path(sys.executable), "official")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing workspace should not be silently created")


def test_legacy_mcp_stdio_real_subprocess(tmp_path):
    # This test exercises the underlying protocol, not a proprietary client GUI.
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), TWINDEV_WORKSPACE=str(tmp_path))
    with subprocess.Popen([sys.executable, "-m", "twindev_mcp.offline_stdio"],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          env=env, text=True, bufsize=1) as proc:
        messages = [
            {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"smoke","version":"1.0"}}},
            {"jsonrpc":"2.0","method":"notifications/initialized","params":{}},
            {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}},
            {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"workspace_overview","arguments":{}}},
        ]
        payload = "".join(json.dumps(m) + "\n" for m in messages)
        stdout, stderr = proc.communicate(payload, timeout=15)
        assert proc.returncode == 0, stderr
        replies = [json.loads(x) for x in stdout.splitlines()]
        assert len(replies) == 3
        assert replies[0]["result"]["capabilities"].get("tools") is not None
        assert len(replies[1]["result"]["tools"]) >= 20
        assert replies[2]["result"]["isError"] is False


def test_unicode_workspace_in_toml(tmp_path):
    workspace = tmp_path / "پروژه"
    workspace.mkdir()
    raw = mod.generate(workspace, Path(sys.executable), "official")[".codex/config.toml"]
    obj = tomllib.loads(raw)
    assert obj["mcp_servers"]["qptwin"]["env"]["TWINDEV_WORKSPACE"] == str(workspace.resolve())
