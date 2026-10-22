# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Static structure discovery. Never imports or executes project code."""
from __future__ import annotations
import ast
import re
from collections import defaultdict
from pathlib import PurePosixPath
from .security import Workspace

_JS_IMPORT = re.compile(r'''(?:import\s+(?:[^;]+?\s+from\s+)?|require\(\s*|import\(\s*)[\"']([^\"']+)[\"']''')
_JS_ROUTE = re.compile(r'''\b(?:app|router)\.(get|post|put|patch|delete)\s*\(\s*[\"'`]([^\"'`]+)[\"'`]''')


def _py_endpoint(call: ast.Call) -> tuple[str, str] | None:
    if isinstance(call.func, ast.Attribute) and call.func.attr in {"route", "get", "post", "put", "patch", "delete", "api_route"}:
        if call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str):
            method = call.func.attr.upper()
            if method in {"ROUTE", "API_ROUTE"}:
                methods = next((kw.value for kw in call.keywords if kw.arg == "methods"), None)
                if isinstance(methods, (ast.List, ast.Tuple)):
                    names = [x.value for x in methods.elts if isinstance(x, ast.Constant) and isinstance(x.value, str)]
                    method = ",".join(names) or "ANY"
                else:
                    method = "ANY"
            return method, call.args[0].value
    return None


def _module_path(module: str, by_path: set[str]) -> str | None:
    base = module.replace(".", "/")
    for option in (base + ".py", base + "/__init__.py"):
        if option in by_path:
            return option
    return None


def discover(ws: Workspace) -> dict:
    paths = ws.source_files()
    python_modules = {p.removesuffix(".py").replace("/", "."): p for p in paths if p.endswith(".py")}
    by_path = set(paths)
    components = []
    dependencies = []
    endpoints = []
    errors = []
    for path in paths:
        if path not in by_path or PurePosixPath(path).name in {"requirements.txt"}:
            continue
        if path.endswith(('.json', '.toml')):
            components.append({"path": path, "kind": "manifest"})
            continue
        if not path.endswith(('.py','.js','.jsx','.ts','.tsx')):
            continue
        code = ws.text(path)
        kind = "python" if path.endswith(".py") else "javascript"
        components.append({"path": path, "kind": kind})
        if kind == "python":
            try:
                tree = ast.parse(code, filename=path)
            except SyntaxError as e:
                errors.append({"path": path, "error": f"syntax error at line {e.lineno}"})
                continue
            for node in ast.walk(tree):
                imports = []
                if isinstance(node, ast.Import):
                    imports = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.level == 0:
                        imports = [node.module] if node.module else []
                        if node.module:
                            imports += [node.module + "." + alias.name for alias in node.names]
                    else:
                        current = PurePosixPath(path).parent.parts
                        ancestry = current[:max(0, len(current) - (node.level - 1))]
                        base = ".".join((*ancestry, *(node.module or "").split("."))).strip(".")
                        imports = [base, *((base + "." if base else "") + alias.name for alias in node.names)]
                for imp in imports:
                    target = python_modules.get(imp) or _module_path(imp, by_path)
                    if target and target != path:
                        dependencies.append({"from": path, "to": target, "kind": "import"})
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            ep = _py_endpoint(decorator)
                            if ep:
                                endpoints.append({"file": path, "method": ep[0], "path": ep[1], "handler": node.name})
        else:
            for imp in _JS_IMPORT.findall(code):
                if not imp.startswith("."):
                    continue
                stem = (PurePosixPath(path).parent / imp).as_posix()
                # Reject traversal to a normalized path outside repo (never read it).
                parts = []
                for part in stem.split("/"):
                    if part == "..":
                        if parts: parts.pop()
                    elif part not in ("", "."): parts.append(part)
                candidate = "/".join(parts)
                for to in (candidate, *(candidate + e for e in (".js", ".jsx", ".ts", ".tsx", "/index.ts", "/index.js"))):
                    if to in by_path and to != path:
                        dependencies.append({"from": path, "to": to, "kind": "import"})
                        break
            endpoints += [{"file": path, "method": m.upper(), "path": url, "handler": "unresolved"}
                          for m, url in _JS_ROUTE.findall(code)]
    dedup = {(d["from"], d["to"], d["kind"]): d for d in dependencies}
    return {"workspace": ws.root.name, "components": components, "dependencies": list(dedup.values()),
            "endpoints": endpoints, "warnings": errors, "scanned_files": len(paths),
            "limitations": "Static best-effort graph; dynamic imports, runtime routing and DB operations require explicit adapters."}


def impact(graph: dict, changed: list[str], depth: int = 4) -> dict:
    paths = {c["path"] for c in graph["components"]}
    reverse: dict[str,set[str]] = defaultdict(set)
    for d in graph["dependencies"]:
        reverse[d["to"]].add(d["from"])
    changed = list(dict.fromkeys(changed))
    for path in changed:
        if path not in paths:
            raise ValueError(f"File not found in architecture graph: {path}")
    seen = set(changed)
    frontier = set(changed)
    hops: dict[str,int] = {x: 0 for x in changed}
    for step in range(1, depth + 1):
        frontier = set().union(*(reverse.get(x,set()) for x in frontier)) - seen
        for x in frontier: hops[x] = step
        seen |= frontier
        if not frontier: break
    endpoint_hits = [e for e in graph["endpoints"] if e["file"] in seen]
    return {"changed_files": changed, "impacted_files": sorted(seen - set(changed)),
            "impacted_endpoints": endpoint_hits, "hop_distance": hops,
            "risk_indicators": {"fanout_count": len(seen)-len(changed), "api_routes_affected": len(endpoint_hits)},
            "caveat": "Dependency-based impact only. Does not prove behavioral compatibility or absence of vulnerabilities."}
