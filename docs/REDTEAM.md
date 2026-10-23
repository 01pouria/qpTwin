# qpTwin security architecture and threat model

This document summarizes the primary trust boundaries, controls, and residual risks for qpTwin Community v0.4.0.

## Trust boundaries

1. **Workspace:** repository files are untrusted input and may contain malicious syntax, oversized data, symlinks, or prompt-injection content.
2. **qpTwin process:** runs with the permissions of its operating-system identity and must be deployed with least privilege.
3. **MCP client:** receives architecture-derived results and controls which tools are invoked.
4. **Model provider:** may receive MCP results according to the connected client's data-handling configuration.
5. **Runtime state:** architecture snapshots under `.twindev/` are local metadata and require the same access protection as the workspace.

## Control matrix

| Area | Threat | Implemented control | Deployment responsibility |
|---|---|---|---|
| Confidentiality | Reading outside the configured workspace | Canonical root checks; absolute path, traversal, and symlink rejection | Restrict OS permissions and client access |
| Confidentiality | Accidental secret collection | Common private filenames and directories excluded; supported file types and sizes enforced | Maintain repository hygiene and provider data policies |
| Integrity | Executing malicious project code | Static parsing; no import, shell, or project command execution | Isolate the process for sensitive repositories |
| Integrity | Unauthorized source modification | No application-source write tools | Control other tools available to the coding agent |
| Integrity | Unsafe snapshot writes | Explicit invocation, validated name, protected location, atomic replacement | Protect `.twindev/` and workspace ownership |
| Integrity | Incorrect analysis interpreted as fact | Structured caveats, model assumptions, evidence gaps, and advisory statuses | Require CI, review, and domain validation |
| Availability | Resource exhaustion | File-count, file-size, duration, arrival, and stage limits | Add process quotas and timeouts in shared deployments |
| Protocol | Malformed MCP input | Argument validation and bounded error responses | Keep client and server versions maintained |
| Supply chain | Untrusted artifacts or dependencies | Minimal runtime dependency surface and CI coverage | Pin, scan, and attest deployment dependencies |
| AI safety | Prompt injection in repository content | Repository content is treated as data; qpTwin does not execute embedded instructions | Configure the connected agent to preserve tool/data boundaries |

## Verification coverage

Automated tests cover:

- path traversal and private-file rejection;
- symlink escape and nested symlink handling;
- bounded scans and oversized files;
- XML entity rejection;
- numeric and schema validation;
- deterministic simulation behavior and capacity limits;
- JSON-RPC initialization, tool discovery, invocation, and error handling;
- snapshot path validation;
- removal of sensitive OTLP attributes from aggregated results.

## Secure deployment profile

For high-sensitivity repositories:

- run qpTwin in an isolated process or container;
- mount a read-only workspace where snapshot persistence is not required;
- disable outbound network access for the qpTwin process;
- authenticate and authorize any bridge that exposes MCP remotely;
- apply per-request timeouts, quotas, logging, and retention rules;
- validate CI and telemetry artifacts before supplying them to review tools;
- monitor dependency and container vulnerabilities continuously.

## Platform-layer controls

Remote multi-user deployments require controls outside the Community stdio server: authenticated transport, authorization, tenant isolation, rate limiting, encrypted storage, audit, incident response, backup and restore, and data-retention governance. These controls are part of the deployment or enterprise platform architecture.
