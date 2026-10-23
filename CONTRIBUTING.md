# Contributing to qpTwin

Thank you for helping improve qpTwin Community. Contributions may include bug reports, reproducible test cases, documentation, integrations, and source changes.

## Before opening a change

- Search existing issues and pull requests.
- Open an issue for substantial features, protocol changes, or architectural changes.
- Keep each pull request focused on one problem.
- Never include credentials, private source code, production telemetry, customer data, or generated machine-specific configuration.

## Development setup

```bash
python -m venv .venv
python -m pip install -e '.[test]'
python -m pytest -q
python scripts/demo_review.py
```

The demo must return `BLOCKED_FOR_REVIEW` for its intentionally incompatible API change.

## Pull-request requirements

- Explain the problem, approach, and compatibility impact.
- Add or update tests for behavioral changes.
- Preserve Python 3.11+ compatibility.
- Preserve workspace safety boundaries and bounded processing.
- Update English and Persian documentation when user-facing behavior changes.
- Use qpTwin as the public product name; retain legacy internal identifiers only where compatibility requires them.
- Confirm that new dependencies and copied materials have compatible licenses.

## Licensing

qpTwin Community is licensed under [Apache License 2.0](LICENSE). Unless a separate written agreement applies, submitted contributions are provided under the project's applicable contribution and licensing terms. Contributors retain copyright in their work.

Commercial or dual-licensed use of a contribution may require an additional contributor agreement. The maintainer will identify that requirement before accepting affected code.

## Security reports

Do not open public issues for vulnerabilities. Follow the private reporting process in [SECURITY.md](SECURITY.md).
