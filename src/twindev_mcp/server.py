# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Official MCP Python SDK v2 adapter. Install with `pip install -e '.[mcp]'`."""
from __future__ import annotations
import logging
from .tools import _tool_registry

logging.basicConfig(level=logging.INFO,format='%(levelname)s %(name)s: %(message)s')


def create_server():
    try:
        from mcp.server.mcpserver import MCPServer
    except ImportError as exc:
        raise RuntimeError("Official MCP SDK v2 unavailable. Install: pip install -e '.[mcp]' or use twindev-offline legacy stdio.") from exc
    server=MCPServer("qpTwin MCP")
    for fn in _tool_registry.values():
        server.tool()(fn)

    @server.resource("twindev://instructions")
    def instructions() -> str:
        return "Analyze architecture and impact first, simulate explicit hypotheses, run real CI tests outside MCP, and seek human review. No tool constitutes production approval."

    @server.prompt()
    def evaluate_change_request(request: str) -> str:
        return ("Act as a security-conscious system architect. Given this request: " + request +
                "\nCall discover_architecture, analyze_change for existing changed files, scan_code_risks and propose_validation_plan. "
                "Only simulate workloads whose parameters are grounded in evidence. Do not claim tests ran unless CI artifacts exist. "
                "Summarize architectural constraints, risk, uncertainty, and necessary human approvals.")
    return server


def main():
    create_server().run(transport="stdio")

if __name__=='__main__':main()
