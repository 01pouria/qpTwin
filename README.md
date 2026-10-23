# qpTwin Community

**Architecture intelligence and change-risk analysis for AI-assisted software engineering.**

qpTwin is a Model Context Protocol (MCP) server developed by **Pouriya Khalilian**. It gives coding agents a structured view of a repository before and after a change: architecture discovery, dependency and endpoint analysis, change-impact mapping, API contract review, bounded capacity simulation, quality evidence, and security-oriented review.

Version **0.4.0** is the current Apache-2.0 Community release. It is designed for professional, local-first engineering workflows and integrates with MCP-capable development tools over stdio.

## Core capabilities

- Discover Python, JavaScript, and TypeScript components, imports, and supported HTTP routes without executing project code.
- Analyze the impact of changed files or unified diffs across dependencies and exposed endpoints.
- Inspect and compare OpenAPI JSON contracts for compatibility risks.
- Enforce configurable architecture boundaries.
- Run bounded single-service and multi-stage capacity simulations.
- Calibrate models from aggregate CSV metrics and validate them against time-split holdout data.
- Review JUnit evidence, aggregate selected OTLP trace metrics, and produce change-evidence reports.
- Perform structured architecture and CIA-oriented risk reviews.
- Save and compare sanitized architecture metadata snapshots on explicit request.
- Expose **23 MCP tools** through a local stdio server.
- Generate **12 reviewable MCP client profiles** for Cursor, Codex, Claude Code, Antigravity, Hermes Agent, OpenClaw, OpenCode, Gemini CLI, Windsurf, Cline, Roo Code, and VS Code.

## Design principles

- **Local-first:** source analysis and MCP communication run on the developer machine.
- **Scoped access:** every operation is restricted to one explicitly configured workspace.
- **Safe by default:** project code is parsed, not imported or executed.
- **Bounded processing:** file sizes, scan counts, and simulation workloads are limited.
- **Evidence over automation:** qpTwin supplies engineering evidence while merge and deployment authority remains with the surrounding development process.
- **Transparent models:** simulation assumptions and validation limits are included in tool results.

## Installation

qpTwin requires Python 3.11 or newer.

```bash
git clone https://github.com/01pouria/qpTwin.git
cd qpTwin
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

python -m pip install -e '.[test]'
python -m pytest -q
```

## Run the MCP server

Set the workspace to a repository you are authorized to analyze:

```bash
export TWINDEV_WORKSPACE=/absolute/path/to/repository
python -m twindev_mcp.offline_stdio
```

Windows PowerShell:

```powershell
$env:TWINDEV_WORKSPACE = 'C:\Path\To\Repository'
python -m twindev_mcp.offline_stdio
```

The process communicates through stdio and normally produces no interactive terminal prompt. The internal module name `twindev_mcp` and environment variable `TWINDEV_WORKSPACE` are retained for backward compatibility; the product and CLI branding is qpTwin.

For the optional adapter based on the official MCP SDK:

```bash
python -m pip install -e '.[mcp]'
python -m twindev_mcp.server
```

## Generate client configuration

qpTwin generates configuration files for review; it does not modify live client settings.

```bash
python scripts/generate_qptwin_configs.py \
  --workspace /absolute/path/to/repository \
  --python /absolute/path/to/.venv/bin/python \
  --output ./connection-presets
```

Generated files contain machine-specific absolute paths and are intentionally excluded from Git. Review the generated profile, then merge it into the appropriate client configuration.

See the [Persian client integration guide](README_QPTWIN_FA.md) and [Windows installation guide](docs/INSTALL_WIN_FA.md).

## Validation

The repository CI runs on Python 3.11, 3.12, and 3.13. The suite covers workspace boundaries, protocol behavior, architecture discovery, simulations, contract analysis, evidence review, snapshots, and client configuration generation.

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python scripts/demo_review.py
```

The demo intentionally contains an incompatible API change and should return `BLOCKED_FOR_REVIEW`.

## Operational scope

qpTwin Community v0.4.0 provides local repository intelligence over stdio. It does not execute project tests, modify application source, or expose a hosted multi-tenant endpoint. Runtime synchronization, organization-wide identity controls, and managed hosting belong to separate deployment or commercial layers.

Simulation and static analysis results are engineering inputs. Calibrate models with representative measurements and keep CI, code review, security testing, and release controls in the delivery pipeline.

## Security

Run qpTwin with least privilege and point it only at repositories you are authorized to inspect. MCP responses may contain architecture-derived information. Workspace traversal, symlinks, common secret files, oversized inputs, and unsupported file types are restricted, but operating-system isolation and repository access control remain deployment responsibilities.

See [SECURITY.md](SECURITY.md) and [docs/REDTEAM.md](docs/REDTEAM.md).

## Documentation

- [راهنمای فارسی qpTwin](README_FA.md)
- [راهنمای اتصال کلاینت‌های MCP](README_QPTWIN_FA.md)
- [Agent workflow](docs/AGENT_WORKFLOW_FA.md)
- [Roadmap](docs/PHASES.md)
- [Contributing](CONTRIBUTING.md)
- [Community and commercial editions](COMMERCIAL.md)

## License and ownership

Copyright © 2026 **Pouriya Khalilian**.

qpTwin Community is available under the [Apache License 2.0](LICENSE). See [NOTICE](NOTICE) and [OWNERSHIP.md](OWNERSHIP.md) for attribution, and [COMMERCIAL.md](COMMERCIAL.md) for the edition strategy.
