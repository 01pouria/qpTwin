# qpTwin Universal MCP

**Created and owned by Pouriya Khalilian** · Independent personal project · Not a Rastano product.

**Engineering intelligence for AI coding agents** — architecture discovery, change-impact analysis, bounded simulation, contract checks, quality evidence and risk review via the Model Context Protocol.

> **Release status:** v0.4.0 engineering preview, **Apache-2.0 licensed**. Not production-certified.

## What it does

- Read-only workspace architecture discovery and dependency/endpoint inspection.
- Change impact analysis from modified files or unified diffs.
- OpenAPI JSON contract-change candidates and policy checks.
- Bounded queue / multi-service simulation, telemetry aggregation and holdout analysis.
- JUnit evidence review, advisory release gating, CIA-style architecture review.
- Explicit opt-in architecture snapshot save (the one locally writing operation).
- Local stdio MCP interface exposing **23 tools**.
- Generation of **12 client configuration presets**, including Cursor, Codex, Claude Code, Antigravity, Hermes Agent, OpenClaw, OpenCode, Gemini CLI, Windsurf, Cline, Roo Code, and VS Code.

The Python module remains named `twindev_mcp` for backward compatibility; package/CLI branding is `qpTwin`.

## What it does *not* do yet

- It is **not** a continuously synchronized runtime digital twin.
- No production-grade multi-tenant hosted MCP service, workload isolation, or enterprise auth.
- It does not modify application source or execute test commands in customer workspaces.
- A generated client configuration is not proof of runtime behavior in every installed IDE version.

## Quickstart

Requires Python 3.11+.

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -e '.[test]'
python -m pytest -q
```

To run the local stdio server against a **trusted** repository:

```bash
export TWINDEV_WORKSPACE=/absolute/path/to/repository
python -m twindev_mcp.offline_stdio
```

The server prints no ordinary prompt; an MCP client communicates over stdio. For the optional official SDK adapter, install `python -m pip install -e '.[mcp]'` and use `python -m twindev_mcp.server`, but verify it in your own environment first.

Generate reviewed client configurations (does not change the IDE's live settings):

```bash
python scripts/generate_qptwin_configs.py \
  --workspace /absolute/path/to/repository \
  --python /absolute/path/to/.venv/bin/python \
  --output ./connection-presets
```

See [Persian client guide](README_QPTWIN_FA.md), [developer notes](README_FA.md), and [security policy](SECURITY.md).

## Development / testing

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python scripts/demo_review.py
```

CI checks Python 3.11–3.13; compatibility tests use a local MCP test client, rather than running all third-party client apps.

## Security

The server reads code from a single explicitly scoped workspace, but MCP responses can reveal architecture information. Keep it local to trusted coding agents and never point it at an untrusted or secret-laden repository. Workspace scanning is bounded and excludes common sensitive files, but is not a substitute for repository access control.

## Licensing and ownership

**Copyright © 2026 Pouriya Khalilian.** qpTwin Community is distributed under the [Apache License 2.0](LICENSE). Independent personal project; not a Rastano product. Future proprietary or paid additions may be licensed separately, while already-published Apache-2.0 releases remain available under Apache-2.0. See [COMMERCIAL.md](COMMERCIAL.md), [NOTICE](NOTICE), and [OWNERSHIP.md](OWNERSHIP.md). Third-party and contributed code require a separate rights review.
