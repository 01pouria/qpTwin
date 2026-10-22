# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Conservative static indicators and source-derived quality reporting."""
from __future__ import annotations
import ast
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from .security import Workspace
from .discovery import discover

_JS_PATTERNS = [
    (re.compile(r"\beval\s*\("), "dynamic_eval", "high"),
    (re.compile(r"\binnerHTML\s*="), "html_injection_sink", "medium"),
    (re.compile(r"\b(?:exec|execSync)\s*\("), "process_execution", "high"),
]
_SECRET_NAMES = re.compile(r"(?:api[_-]?key|private[_-]?key|secret|password|token)$", re.I)


def _findings_py(path: str, text: str) -> list[dict]:
    out = []
    try: tree = ast.parse(text)
    except SyntaxError: return [{"file":path,"line":0,"code":"syntax_error","severity":"high"}]
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
            if name in {"eval", "exec"}:
                out.append({"file":path,"line":node.lineno,"code":"dynamic_execution","severity":"high"})
            if name in {"run", "Popen", "call", "check_call", "check_output"}:
                if any(kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True for kw in node.keywords):
                    out.append({"file":path,"line":node.lineno,"code":"shell_true","severity":"high"})
            if name == "load" and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "yaml":
                if not any(kw.arg == "Loader" for kw in node.keywords):
                    out.append({"file":path,"line":node.lineno,"code":"potential_unsafe_yaml_load","severity":"medium"})
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node,ast.Assign) else [node.target]
            val = node.value
            if isinstance(val, ast.Constant) and isinstance(val.value, str) and len(val.value) >= 8:
                for target in targets:
                    if isinstance(target,ast.Name) and _SECRET_NAMES.search(target.id):
                        out.append({"file":path,"line":node.lineno,"code":"possible_hardcoded_secret","severity":"high"})
    return out


def scan(ws: Workspace) -> dict:
    findings = []
    paths = ws.source_files()
    for path in paths:
        if path.endswith(".py"):
            findings += _findings_py(path,ws.text(path))
        elif path.endswith((".js", ".jsx", ".ts", ".tsx")):
            text = ws.text(path)
            for regex, kind, severity in _JS_PATTERNS:
                for m in list(regex.finditer(text))[:30]:
                    findings.append({"file":path,"line":text.count("\n",0,m.start())+1,"code":kind,"severity":severity})
    graph = discover(ws)
    grouped = defaultdict(list)
    for endpoint in graph["endpoints"]:
        grouped[(endpoint["method"],endpoint["path"])].append(endpoint["file"])
    for (method,route), files in grouped.items():
        if len(files)>1:
            findings.append({"file":", ".join(files[:3]),"line":0,"code":"possible_duplicate_route", "severity":"medium", "method":method,"route":route})
    return {"findings":findings[:300],"count":len(findings),"files_scanned":len(paths),
            "assessment":"Heuristic indicators only; absence of findings is NOT a security clearance. Dynamic routes and app configuration may be missed."}


def junit(ws: Workspace, report_path: str) -> dict:
    text = ws.text(report_path)
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper(): raise ValueError("XML DTD/entities not allowed")
    root = ET.fromstring(text)
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    if not suites: raise ValueError("Expected JUnit testsuite XML")
    totals = {key:0 for key in ("tests","failures","errors","skipped")}
    for s in suites:
        for k in totals: totals[k]+=int(s.attrib.get(k,0))
    return {**totals,"passed":totals["tests"]-totals["failures"]-totals["errors"]-totals["skipped"],
            "pass_gate":totals["tests"]>0 and totals["failures"]==0 and totals["errors"]==0,
            "source":"Externally-generated JUnit artifact; tests are NOT executed by this MCP tool."}


def release_gate(ws: Workspace, report_path: str, p95_ms: float | None = None, max_p95_ms: float = 1200.0) -> dict:
    quality=scan(ws)
    tests=junit(ws,report_path)
    high=[x for x in quality["findings"] if x["severity"] == "high"]
    reasons=[]
    if not tests["pass_gate"]: reasons.append("JUnit suite is failing or has no tests")
    if high: reasons.append("Unreviewed high-severity static indicators exist")
    if p95_ms is None: reasons.append("No measured latency evidence supplied")
    elif not (0<=p95_ms<=max_p95_ms): reasons.append("Observed p95 exceeds limit or invalid")
    return {"status":"REVIEW_REQUIRED" if reasons else "ADVISORY_PASS", "reasons":reasons,
            "junit":tests,"high_severity_indicators":high[:30],
            "notice":"Advisory only. Production release requires human approval and independent security/performance checks."}
