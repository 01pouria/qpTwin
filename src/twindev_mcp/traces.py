# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Aggregate service timings from a local bounded OTLP JSON trace export.

We use only timestamps, span kind, service.name and a numeric status code.
Attributes such as HTTP paths, prompts, headers or user identities are never returned.
"""
from __future__ import annotations
import json
import math
from collections import defaultdict
from .simulation import _percentile
from .security import Workspace

MAX_SPANS=12000

def aggregate_traces(ws:Workspace,filename:str)->dict:
    if not filename.endswith('.json'):raise ValueError('Expected local OTLP trace .json export')
    obj=json.loads(ws.text(filename))
    if not isinstance(obj,dict) or not isinstance(obj.get('resourceSpans'),list):
        raise ValueError('Expected OTLP JSON resourceSpans')
    out=defaultdict(list);errors=defaultdict(int)
    earliest=None;latest=None;seen=0;skipped=0
    if len(obj['resourceSpans'])>1000:raise ValueError('Too many resource spans')
    for resource in obj['resourceSpans']:
        if not isinstance(resource,dict):continue
        raw_name='unknown'
        for attr in resource.get('resource',{}).get('attributes',[]):
            if isinstance(attr,dict) and attr.get('key')=='service.name':
                name=attr.get('value',{}).get('stringValue','unknown')
                if isinstance(name,str) and 0<len(name)<=100:raw_name=name
        for scope in resource.get('scopeSpans',[]):
            for span in scope.get('spans',[]):
                seen+=1
                if seen>MAX_SPANS:raise ValueError('Exceeded 12000 trace spans')
                if not isinstance(span,dict) or span.get('kind') not in (None,2,'SPAN_KIND_SERVER'):
                    skipped+=1;continue
                try:
                    a=int(span['startTimeUnixNano']);b=int(span['endTimeUnixNano'])
                except (KeyError,TypeError,ValueError):skipped+=1;continue
                if a<=0 or b<a or b-a>10**12:skipped+=1;continue
                latency=(b-a)/1e6
                out[raw_name].append(latency)
                if span.get('status',{}).get('code') in (2,'STATUS_CODE_ERROR'):
                    errors[raw_name]+=1
                earliest=a if earliest is None else min(earliest,a)
                latest=b if latest is None else max(latest,b)
    if not out:raise ValueError('No usable server spans found')
    duration=(latest-earliest)/1e9 if earliest is not None else None
    series=[]
    for service,times in sorted(out.items()):
        series.append({'service':service,'observed_span_count':len(times),
                       'mean_latency_ms':round(sum(times)/len(times),3),
                       'p95_latency_ms':round(_percentile(times,.95),3),
                       'observed_error_fraction':round(errors[service]/len(times),4)})
    return {'services':series,'total_server_spans':sum(len(x) for x in out.values()),
            'skipped_spans':skipped,'export_observation_seconds':round(duration,3) if duration is not None else None,
            'privacy':'No span names, trace IDs, http paths, request attributes or original payload are emitted.',
            'caution':'A trace sample may be biased or incomplete; count is not reliable throughput without sampling rate and coverage. Parallel spans cannot be summed as end-to-end latency.'}
