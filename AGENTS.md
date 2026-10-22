# Instructions for Codex and coding agents

This directory is the qpTwin v0.4.0 local MCP source. Preserve Python 3.11+ compatibility and current CLI entrypoints.

## Tests
- `python -m pip install -e '.[test]'`
- `python -m pytest -q`
- `python scripts/demo_review.py` (expect `BLOCKED_FOR_REVIEW` for the intentionally breaking example)

## Safety and publication guardrails
1. Never commit secrets, private environment files, live customer code, telemetry or generated absolute-path client configurations.
2. Do not represent any static simulator as a production-synchronized Digital Twin.
3. Project author and owner is Pouriya Khalilian, as stated by the developer. Do not attribute qpTwin to Rastano or any employer. Confirm legal rights to contributions and third-party materials separately.
4. Apache-2.0 has been selected and the LICENSE/NOTICE files are included. **Before any public push, show the precise files, confirm the target personal GitHub account, and obtain the owner's final approval for public publication.**
5. Do not use `git push --force`, delete repositories, or overwrite existing remotes.
6. `TWINDEV_WORKSPACE` must remain a trusted explicit local repository.
7. The public product name is qpTwin. Keep legacy internal identifiers only where backward compatibility requires them.
