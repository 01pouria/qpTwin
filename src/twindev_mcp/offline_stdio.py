# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Minimal standalone legacy MCP stdio adapter for air-gapped demonstrations.

Implements only core initialize/tools/list/tools/call/ping, protocol 2025-11-25.
For a full maintained MCP implementation use official SDK v2 `server.py`.
"""
from __future__ import annotations
import inspect
import json
import sys
import types
from typing import get_origin,get_args,get_type_hints,Union
from .tools import _tool_registry

PROTOCOL='2025-11-25'

def _schema(t):
    if t is type(None):return {'type':'null'}
    origin=get_origin(t)
    if origin is list:return {'type':'array','items':_schema(get_args(t)[0])}
    if origin is dict or t is dict:
        args=get_args(t)
        return {'type':'object','additionalProperties':_schema(args[1]) if len(args)==2 else True}
    if origin in (Union,types.UnionType):
        return {'anyOf':[_schema(x) for x in get_args(t)]}
    if t is int:return {'type':'integer'}
    if t is float:return {'type':'number'}
    if t is bool:return {'type':'boolean'}
    if t is str:return {'type':'string'}
    return {'type':'string'}

def definitions():
    out=[]
    for name,func in _tool_registry.items():
        spec=inspect.signature(func)
        hints=get_type_hints(func)
        properties={}
        required=[]
        for arg,param in spec.parameters.items():
            t=_schema(hints.get(arg,str))
            if param.default is inspect.Parameter.empty:required.append(arg)
            else:t['default']=param.default
            properties[arg]=t
        out.append({'name':name,'description':inspect.getdoc(func) or '',
                    'inputSchema':{'type':'object','properties':properties,'required':required,'additionalProperties':False},
                    'annotations':{'readOnlyHint':name!='save_architecture_snapshot','openWorldHint':False}})
    return out

def invoke(req: dict) -> dict | None:
    if not isinstance(req,dict) or req.get('jsonrpc') != '2.0':
        return {'jsonrpc':'2.0','id':req.get('id') if isinstance(req,dict) else None,'error':{'code':-32600,'message':'Invalid request'}}
    method=req.get('method')
    if method in ('notifications/initialized','notifications/cancelled') or 'id' not in req:
        return None
    rid=req['id']
    if method == 'initialize':
        init_params=req.get('params') or {}
        if not isinstance(init_params,dict):return {'jsonrpc':'2.0','id':rid,'error':{'code':-32602,'message':'Expected params object'}}
        wanted=init_params.get('protocolVersion',PROTOCOL)
        negotiated=wanted if wanted in ('2025-11-25','2025-06-18','2025-03-26') else PROTOCOL
        result={'protocolVersion':negotiated,'capabilities':{'tools':{'listChanged':False}},
                'serverInfo':{'name':'qpTwin-local-adapter','version':'0.4.0'},
                'instructions':'Read-only project analysis; explicit snapshot writes only; no project-code execution.'}
    elif method == 'ping': result={}
    elif method == 'tools/list':result={'tools':definitions()}
    elif method == 'tools/call':
        params=req.get('params') or {}
        if not isinstance(params,dict):return {'jsonrpc':'2.0','id':rid,'error':{'code':-32602,'message':'Expected params object'}}
        name=params.get('name')
        func=_tool_registry.get(name)
        if not func:
            return {'jsonrpc':'2.0','id':rid,'error':{'code':-32602,'message':'Unknown tool'}}
        args=params.get('arguments') or {}
        if not isinstance(args,dict):return {'jsonrpc':'2.0','id':rid,'error':{'code':-32602,'message':'Expected object arguments'}}
        try:
            spec=inspect.signature(func)
            bound=spec.bind(**args)
            # Do not trust agent input types; avoid coercion surprises.
            hints=get_type_hints(func)
            for key,value in bound.arguments.items():
                typ=hints.get(key)
                if typ is int and type(value) is not int:
                    raise TypeError(f'{key} must be an integer')
                if typ is float and type(value) not in (int,float):
                    raise TypeError(f'{key} must be numeric')
                if typ is str and not isinstance(value,str):raise TypeError(f'{key} must be a string')
                if typ is bool and type(value) is not bool:
                    raise TypeError(f'{key} must be a boolean')
                if (get_origin(typ) is dict or typ is dict) and not isinstance(value,dict):
                    raise TypeError(f'{key} must be an object')
                if get_origin(typ) is list:
                    itemtype=get_args(typ)[0]
                    if not isinstance(value,list) or (itemtype is str and not all(isinstance(v,str) for v in value)) or (get_origin(itemtype) is dict and not all(isinstance(v,dict) for v in value)):
                        raise TypeError(f'{key} has invalid list contents')
            output=func(*bound.args,**bound.kwargs)
            result={'content':[{'type':'text','text':json.dumps(output,ensure_ascii=False)}],
                    'structuredContent':output, 'isError':False}
        except (ValueError,TypeError,RuntimeError,PermissionError,OSError) as e:
            result={'content':[{'type':'text','text':str(e)}], 'isError':True}
        except Exception:
            # Never leak a traceback or environment secrets to an agent.
            result={'content':[{'type':'text','text':'Internal error. Review server stderr in a secured environment.'}], 'isError':True}
    else:
        return {'jsonrpc':'2.0','id':rid,'error':{'code':-32601,'message':'Method not found'}}
    return {'jsonrpc':'2.0','id':rid,'result':result}

def main():
    for line in sys.stdin:
        if len(line) > 1_000_000:
            print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32600,'message':'Message too large'}}),flush=True)
            continue
        try:
            req=json.loads(line)
            response=invoke(req)
            if response is not None:
                print(json.dumps(response,ensure_ascii=False,allow_nan=False,separators=(',',':')),flush=True)
        except (ValueError,TypeError):
            print(json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Parse error'}}),flush=True)
if __name__=='__main__':main()
