# qpTwin delivery and readiness roadmap — status at v0.4.0

## Phase 0: product scope and baseline
Concept articulated: architecture-aware, simulation-driven Vibe Coding assistance. B2B security requirements and success metrics proposed. No customer agreement or real pilot completed.

## Phase 1: static architecture twin — prototype delivered
Read-only source inventory, static Python/JS/TS imports and routes, change impact, local snapshots, explicit boundary policy. Automated tests. Limitations: best-effort parsing, incomplete framework coverage, no runtime architecture reconciliation.

## Phase 2: scenario and observable proxy — extended prototype delivered
Bounded single service M/M/c simulation and sequential multi-stage event simulation; Monte Carlo assumptions explicit. Offline aggregated CSV telemetry, OTLP JSON metric aggregation, time-split holdout p95 validation. Limitations: not a full general digital twin; cannot model all software behavior, concurrency semantics, DB contention or GPU inference.

## Phase 3: coding agent pipeline — preview delivered
23 locally callable MCP tools, local patch impact, conservative OpenAPI compatibility comparison and combined evidence review. Synthetic demos and automated stdio protocol tests are included. Twelve reviewable MCP client configuration profiles are generated, but execution inside every supported client UI has not been independently verified.

## Phase 4: production runtime twin — partially researched, not delivered
Live streaming telemetry ingestion; online parameter assimilation; uncertainty bounds; drift detection; calibrated service dependencies; retries and fanout; cloud fault model; production validation.

## Phase 5: enterprise and commercial release — not delivered
RBAC, authenticated Streamable HTTP, true tenant separation, quotas, audit, supported deployment and backup/restore, SLO/SLA, support process, finance/billing integration.

## Phase 6: field proof — not delivered
Independent QA and penetration testing, baseline comparison to other coding agents on actual PRs, real client interviews, B2B acceptance and economic analysis.

## Go/No-Go gates
- Local developer experiment: allowed with scoped non-sensitive code and full review.
- External demonstration: allowed only as **engineering preview**, with known limitations disclosed.
- Customer pilot: requires written permission, data handling agreement, threat model, pilot plan, suitable hosting.
- Production sale/claim of accuracy: **No-Go**, pending Phases 4–6 and independent evidence.
