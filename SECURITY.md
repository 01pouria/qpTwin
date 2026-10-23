# qpTwin security policy

## Supported versions

Security updates are provided for the current `0.4.x` Community release line.

## Reporting a vulnerability

Report vulnerabilities privately through GitHub's **Security Advisories** feature for this repository. Include the affected version, reproduction steps, impact, and any proposed mitigation. Do not place credentials, private source code, or exploit details in a public issue.

The maintainer will acknowledge a complete report, assess severity, coordinate a fix, and publish release information when remediation is available.

## Security model

qpTwin Community is a local MCP server that analyzes one explicitly configured workspace. Its primary controls include:

- canonical workspace-root enforcement;
- rejection of absolute paths and parent traversal;
- symlink rejection for analyzed files and snapshot locations;
- exclusion of common secret, dependency, VCS, and build paths;
- supported-extension and maximum-file-size checks;
- bounded repository scans and simulations;
- parsing without importing or executing project modules;
- no shell-command or application-source mutation tools;
- sanitized architecture snapshots written only by explicit tool invocation.

## Deployment guidance

- Run qpTwin with a dedicated least-privilege user where practical.
- Grant access only to repositories the operator and connected MCP client are authorized to inspect.
- Treat repository content as untrusted input, including comments and documentation that may contain prompt injection.
- Apply operating-system or container isolation for higher-sensitivity environments.
- Review what repository-derived information the MCP client may send to external model providers.
- Keep generated client configuration and `.twindev/` runtime state out of source control.
- Use authenticated gateways, tenant isolation, rate limiting, audit, and retention controls when building remote or shared deployments.

## Scope boundaries

Static discovery and simulation support engineering decisions but do not replace code review, dependency scanning, penetration testing, workload testing, or deployment controls. The local stdio transport is intended for a trusted client process on the same machine; public network exposure requires a separate secured transport layer.

See [docs/REDTEAM.md](docs/REDTEAM.md) for the threat model and control matrix.
