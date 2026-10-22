#!/usr/bin/env python3
# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Generate *reviewable* MCP client presets for one trusted workspace.

No code execution, no installation, no writes into a project unless --output
points there; existing config files are never overwritten without --force.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CLIENTS = {
    "cursor": Path(".cursor/mcp.json"),
    "codex": Path(".codex/config.toml"),
    "antigravity": Path(".agents/mcp_config.json"),
    "claude-code": Path(".mcp.json"),
}


def generate(workspace: Path, python: Path, mode: str) -> dict[str, str]:
    """Return relative file paths mapped to generated UTF-8 contents."""
    workspace = workspace.expanduser().resolve(strict=True)
    if not workspace.is_dir():
        raise ValueError("workspace must be an existing directory")
    python = python.expanduser().resolve(strict=True)
    if not python.is_file():
        raise ValueError("python must be an existing executable file")
    if mode not in {"official", "legacy"}:
        raise ValueError("mode must be official or legacy")
    module = "twindev_mcp.server" if mode == "official" else "twindev_mcp.offline_stdio"
    argv = ["-m", module]
    env = {"TWINDEV_WORKSPACE": str(workspace)}
    server = {"command": str(python), "args": argv, "env": env}
    doc = json.dumps({"mcpServers": {"qptwin": server}}, ensure_ascii=False, indent=2) + "\n"
    # Codex's configuration uses TOML instead of the JSON MCP configuration.
    # JSON quoting is valid for TOML string literals.
    toml = ("[mcp_servers.qptwin]\n"
            + f"command = {json.dumps(str(python), ensure_ascii=False)}\n"
            + f"args = {json.dumps(argv, ensure_ascii=False)}\n"
            + f"env = {{ TWINDEV_WORKSPACE = {json.dumps(str(workspace), ensure_ascii=False)} }}\n"
            + "startup_timeout_sec = 20\n"
            + "tool_timeout_sec = 120\n")
    return {
        CLIENTS["cursor"].as_posix(): doc,
        CLIENTS["codex"].as_posix(): toml,
        CLIENTS["antigravity"].as_posix(): doc,
        CLIENTS["claude-code"].as_posix(): doc,
    }


def write_presets(configs: dict[str, str], output: Path, force: bool = False) -> list[Path]:
    output = output.expanduser().resolve()
    paths = [output / rel for rel in configs]
    existing = [p for p in paths if p.exists()]
    if existing and not force:
        raise FileExistsError("Existing configuration(s); no files changed: " + ", ".join(map(str, existing)))
    for relative, path in zip(configs, paths):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(configs[relative], encoding="utf-8")
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Cursor, Codex, Antigravity and Claude Code MCP configurations")
    parser.add_argument("--workspace", required=True, type=Path, help="existing trusted project path")
    parser.add_argument("--output", required=True, type=Path, help="output directory (review files before copying into a project)")
    parser.add_argument("--python", type=Path, default=Path(sys.executable), help="Python from the installed qpTwin environment")
    parser.add_argument("--mode", choices=("official", "legacy"), default="legacy")
    parser.add_argument("--force", action="store_true", help="overwrite existing output files")
    a = parser.parse_args(argv)
    try:
        paths = write_presets(generate(a.workspace, a.python, a.mode), a.output, a.force)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
