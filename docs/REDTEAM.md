# Security / Redteam assessment (CIA)

| Area | Risk | Control in this release | Residual gap |
|---|---|---|---|
| Confidentiality | Traversal/symlinks expose user files | Explicit workspace root, file-extension checks, symlink denial | Same OS process identity; not OS sandboxed |
| Confidentiality | Leaking secrets via metadata scan | Skip common secret filenames, no raw source/tool outputs, aggregate telemetry only | Risky code or paths may still encode sensitive info |
| Integrity | Agent executes arbitrary commands | No execute/shell/write-source tools | External coding agents still require separate authorization |
| Integrity | Malicious repository tricks parsing | AST parse without import, file size limits, no project execution | Inputs are still untrusted and parsers may have bugs |
| Integrity | Incorrect architectural claims | Explicit best-effort labels; advisory release gate; require CI | Route and dependency coverage incomplete |
| Availability | Unbounded scans/DoS | 2000 file cap, 512KiB max/file, 100k arrival simulation bound | No CPU process isolation or per-call timeout |
| Availability | AI code disrupts production | Simulation + integration tests recommended, human release approval | No HA/failover controls implemented in this package |
| Business security | Agent gives false certainty | No deployment approval; visible uncertainty text | Must train and audit operators |

**Security posture:** read-only development helper, not trusted decision authority.

## Threat modeling before enterprise deployment

Review prompt injection from repository comments and READMEs; symlink/race conditions; secrets in paths; stdio bridge privilege escalations; malicious IDE extensions; inherited environment credentials; data retention; multiple customer environments; tenant isolation; denial of service and rate limits; PR branch and CI provenance; role based approvals. Deploy in an OS-isolated, no-network worker with a read-only copy of one repository when possible.

## Verification done

- Path traversal, symlink escape, private file exclusions and scan caps covered by automated tests.
- XML entity injection denied via DTD/entity guard before parsing.
- Deterministic bounded capacity simulation and failover scenarios covered by automated tests.
- Offline stdio JSON-RPC handshake, tools/list and tools/call exercised in a subprocess.

## Deployment blocking items

No production incident drill, vendor security audit, host privilege isolation, authorization system, tamper-evident audit, comprehensive dynamic SAST/DAST or live cluster integration is present. Do not market the current release as an enterprise-certified security gate.
