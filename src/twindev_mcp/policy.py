# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Explicit architecture boundary policy; no implied approval from missing rules."""
from __future__ import annotations
import fnmatch
import json
from .security import Workspace
from .discovery import discover

POLICY_NAME='twindev-policy.json'

def check(ws: Workspace) -> dict:
    file = ws.root / POLICY_NAME
    if not file.exists():
        return {"status":"UNCONFIGURED","findings":[],
                "message":f"Optional {POLICY_NAME} not found; no explicit architecture boundaries checked."}
    data=json.loads(ws.text(POLICY_NAME))
    if not isinstance(data,dict):raise ValueError('Architecture policy must be an object')
    rules=data.get('forbidden_imports',[])
    if not isinstance(rules,list) or len(rules)>200:raise ValueError('Maximum 200 forbidden_imports rules')
    clean=[]
    for rule in rules:
        if not isinstance(rule,dict) or not isinstance(rule.get('from'),str) or not isinstance(rule.get('to'),str):
            raise ValueError('Each rule requires string from/to glob patterns')
        if len(rule['from'])>300 or len(rule['to'])>300:raise ValueError('Oversized glob patterns')
        clean.append(rule)
    violations=[]
    for edge in discover(ws)['dependencies']:
        for rule in clean:
            if fnmatch.fnmatchcase(edge['from'],rule['from']) and fnmatch.fnmatchcase(edge['to'],rule['to']):
                violations.append({"from":edge['from'],"to":edge['to'],"rule":rule})
    return {"status":"VIOLATION" if violations else "PASS", "rules":len(clean),
            "findings":violations,"scope":"Static internal imports only; does not validate runtime dependency injection or message queues."}
