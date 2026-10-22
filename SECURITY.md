# Security policy

qpTwin v0.4.0 is a **local engineering preview**, not a remote multi-tenant service. Report suspected vulnerabilities privately to the maintainer via a private channel specified by the project maintainer Pouriya Khalilian; avoid posting vulnerabilities, secrets, or internal repository information in public issues.

Supported version for coordinated testing: v0.4.x only. Do not publish or run arbitrary repositories with elevated privileges. The snapshot tool is deliberately write-capable; all other tools should remain read-only. Review access to MCP tools, trust boundaries and returned source-derived data before using with AI agents.

Known limitations: read-only static analysis cannot establish system security; simulation is synthetic until calibrated; local stdio transport cannot provide remote tenant isolation.
