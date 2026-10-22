# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Conservative OpenAPI JSON contract analysis. Does not dereference URLs or $refs.

Compatibility here concerns documented route/method/required-input shape;
not behavioral or semantic backward compatibility.
"""
from __future__ import annotations
import json
from .security import Workspace

MAX_OPENAPI_ENDPOINTS = 3000


def _load(ws: Workspace, filename: str) -> dict:
    if not filename.endswith('.json'):
        raise ValueError('Only OpenAPI JSON is supported; no remote refs or YAML parsing')
    obj = json.loads(ws.text(filename))
    if not isinstance(obj,dict) or not isinstance(obj.get('paths'),dict):
        raise ValueError('Expected OpenAPI JSON with paths object')
    if len(obj['paths']) > MAX_OPENAPI_ENDPOINTS:
        raise ValueError('OpenAPI document exceeds path limit')
    return obj


def inventory(ws: Workspace, filename: str) -> dict:
    document=_load(ws,filename)
    routes={}
    for path,methods in document['paths'].items():
        if not isinstance(path,str) or not path.startswith('/') or not isinstance(methods,dict):
            continue
        for method,op in methods.items():
            if method.lower() not in {'get','post','put','patch','delete','head','options','trace'} or not isinstance(op,dict):
                continue
            required=[]
            for param in (methods.get('parameters',[]),op.get('parameters',[])):
                if isinstance(param,list):
                    for item in param:
                        if isinstance(item,dict) and item.get('required') is True:
                            required.append((str(item.get('in','')),str(item.get('name',''))))
            bodies=op.get('requestBody',{})
            request_required=isinstance(bodies,dict) and bodies.get('required') is True
            responses=op.get('responses',{})
            keys=sorted(k for k in responses if isinstance(k,str)) if isinstance(responses,dict) else []
            routes[f'{method.upper()} {path}']={
                'required_parameters':sorted(set(required)),
                'required_request_body':request_required,
                'response_codes':keys,
                'deprecated':op.get('deprecated') is True,
            }
            if len(routes)>MAX_OPENAPI_ENDPOINTS*8: raise ValueError('Too many endpoints')
    return {'file':filename,'operation_count':len(routes),'operations':routes,
            'limitations':'Only local OpenAPI JSON operation keys, required parameter flags, required requestBody and response-code presence are examined; schema/$ref details, behavior and auth not verified.'}


def compare(ws: Workspace, old_file: str, new_file: str) -> dict:
    old=inventory(ws,old_file)['operations']
    new=inventory(ws,new_file)['operations']
    issues=[]
    for key in sorted(old.keys()-new.keys()):
        issues.append({'operation':key,'kind':'removed_operation','severity':'breaking_candidate'})
    for key in sorted(old.keys()&new.keys()):
        o,n=old[key],new[key]
        added=set(map(tuple,n['required_parameters']))-set(map(tuple,o['required_parameters']))
        if added:
            issues.append({'operation':key,'kind':'new_required_parameters','parameters':sorted(added),'severity':'breaking_candidate'})
        if n['required_request_body'] and not o['required_request_body']:
            issues.append({'operation':key,'kind':'new_required_body','severity':'breaking_candidate'})
        removed=set(o['response_codes'])-set(n['response_codes'])
        if removed:
            issues.append({'operation':key,'kind':'removed_declared_responses','codes':sorted(removed),'severity':'review'})
    return {'old':old_file,'new':new_file,'added_operations':sorted(new.keys()-old.keys()),
            'findings':issues,'breaking_candidates':sum(x['severity']=='breaking_candidate' for x in issues),
            'status':'REVIEW_REQUIRED' if issues else 'NO_STRUCTURAL_BREAK_FOUND',
            'caution':'Best-effort OpenAPI contract diff, not proof of backward compatibility; schema, security and runtime validation still required.'}
