# qpTwin product roadmap

This roadmap separates capabilities delivered in qpTwin Community v0.4.0 from planned platform and commercial layers.

## Available in Community v0.4.0

### Architecture intelligence

- Bounded inventory of Python, JavaScript, and TypeScript source trees
- Import, dependency, and supported route discovery
- Change-impact analysis and validation-plan generation
- Configurable architecture-boundary policies
- Sanitized architecture metadata snapshots and comparison

### Contracts, quality, and risk

- OpenAPI JSON inventory and compatibility-risk comparison
- Unified-diff analysis
- JUnit evidence inspection and advisory release evaluation
- Static risk indicators and CIA-oriented architecture review
- Combined change-evidence reports

### Simulation and observability

- Bounded M/M/c-style capacity simulation
- Sequential multi-stage service simulation
- Aggregate CSV calibration
- Time-split holdout evaluation
- Selected OTLP JSON metric aggregation

### MCP and developer experience

- 23 local MCP tools over stdio
- Optional official MCP SDK adapter
- 12 generated client configuration profiles
- Automated tests across Python 3.11, 3.12, and 3.13
- Synthetic example repositories and review workflows

## Planned platform capabilities

### Runtime intelligence

- Streaming telemetry ingestion
- Online calibration, drift detection, and uncertainty reporting
- Richer dependency, retry, fan-out, database, and failure models
- Trace-to-architecture reconciliation

### Enterprise controls

- Authenticated remote transport
- Role-based access control and policy administration
- Tenant isolation, quotas, and tamper-evident audit
- Deployment automation, backup, restore, and operational health controls

### Engineering ecosystem

- CI and pull-request integrations with artifact provenance
- Broader framework and language coverage
- Organization-level architecture baselines
- Extended reporting, dashboards, and governance workflows

## Release principles

- Community capabilities remain documented, testable, and reproducible.
- New analysis models include their assumptions and validation evidence.
- Security-sensitive platform features ship with explicit threat models and deployment guidance.
- Commercial layers may extend the platform without removing the rights granted for existing Apache-2.0 Community releases.
