# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Safe bounded open-loop discrete-event simulation of a sequential microservice chain.

Each admitted request traverses each service stage in order; intermediate
service times are exponential and independent. There is no branching or retries.
"""
from __future__ import annotations
from collections import deque
import heapq
import math
import random
from .simulation import _percentile


def simulate_chain(stages: list[dict], arrival_rps: float, duration_seconds: int=120,
                   seed: int=42, slo_p95_ms: float=1500) -> dict:
    if isinstance(arrival_rps,bool) or not isinstance(arrival_rps,(int,float)) or not math.isfinite(arrival_rps) or not 0<arrival_rps<=2000:
        raise ValueError('arrival_rps must be finite and in (0,2000]')
    if not 1<=duration_seconds<=3600 or arrival_rps*duration_seconds>50000:
        raise ValueError('Simulation duration/arrivals out of range')
    if not 0<slo_p95_ms<=600000 or not 1<=len(stages)<=12:
        raise ValueError('Invalid SLO or stage count')
    normalized=[]
    seen=set()
    for s in stages:
        if not isinstance(s,dict): raise ValueError('Each stage must be an object')
        if set(s)-{'name','replicas','service_rps_per_replica','queue_limit','failed_replicas'}:
            raise ValueError('Unknown stage fields')
        name=s.get('name')
        replicas=s.get('replicas')
        failed=s.get('failed_replicas',0)
        rate=s.get('service_rps_per_replica')
        limit=s.get('queue_limit',1000)
        if not isinstance(name,str) or not 1<=len(name)<=64 or name in seen:raise ValueError('Stage names must be unique, nonempty, <=64 chars')
        if type(replicas) is not int or not 1<=replicas<=128:raise ValueError('Stage replicas out of range')
        if type(failed) is not int or not 0<=failed<replicas:raise ValueError('Stage failures out of range')
        if type(limit) is not int or not 0<=limit<=50000:raise ValueError('Stage queue_limit out of range')
        if type(rate) not in (int,float) or not math.isfinite(rate) or not 0<rate<=20000:
            raise ValueError('Stage service rate out of range')
        seen.add(name)
        normalized.append({'name':name,'replicas':replicas,'failed_replicas':failed,
                           'service_rps_per_replica':rate,'queue_limit':limit})
    rng=random.Random(seed)
    states=[]
    for s in normalized:
        states.append({'avail':[0.0]*(s['replicas']-s['failed_replicas']),
                       'waiting':[], 'wait_ms':[],'rejected':0,'served':0,'busy_time':0.0,'max_queue':0})
    for state in states:heapq.heapify(state['avail'])
    # Each stage-arrival is a distinct event. Processing in chronological order
    # is essential: downstream stage arrivals can overtake upstream requests.
    events=[]
    next_event=0
    arrival=0.
    arrivals=0
    while True:
        arrival+=rng.expovariate(arrival_rps)
        if arrival>=duration_seconds:break
        heapq.heappush(events,(arrival,next_event,0,arrival))
        next_event+=1
        arrivals+=1
    latencies=[]
    finished=[]
    accepted=0
    total_rejected=0
    while events:
        now,_,stage_id,started_at=heapq.heappop(events)
        conf=normalized[stage_id]
        state=states[stage_id]
        waiting=state['waiting']
        while waiting and waiting[0]<=now:
            heapq.heappop(waiting)
        earliest=heapq.heappop(state['avail'])
        begin=max(now,earliest)
        if begin>now and len(waiting)>=conf['queue_limit']:
            heapq.heappush(state['avail'],earliest)
            state['rejected']+=1
            total_rejected+=1
            continue
        if begin>now:heapq.heappush(waiting,begin)
        end=begin+rng.expovariate(conf['service_rps_per_replica'])
        heapq.heappush(state['avail'],end)
        state['wait_ms'].append((begin-now)*1000)
        state['served']+=1
        state['max_queue']=max(state['max_queue'],len(waiting))
        state['busy_time']+=max(0.,min(end,duration_seconds)-min(begin,duration_seconds))
        if stage_id==len(states)-1:
            accepted+=1
            latencies.append((end-started_at)*1000)
            finished.append(end)
        else:
            heapq.heappush(events,(end,next_event,stage_id+1,started_at))
            next_event+=1
    stage_metrics=[]
    for conf,state in zip(normalized,states):
        capacity=conf['replicas']-conf['failed_replicas']
        stage_metrics.append({'name':conf['name'],'served':state['served'],'rejected':state['rejected'],
                              'max_queue':state['max_queue'],'p95_queue_wait_ms':_percentile(state['wait_ms'],.95),
                              'estimated_utilization':round(min(1.,state['busy_time']/(duration_seconds*capacity)),4)})
    p95=_percentile(latencies,.95)
    return {'assumptions':'Poisson arrivals; sequential independent exponential service stages; static stage failure; bounded FIFO admission; no retry or branching',
            'arrivals':arrivals,'accepted':accepted,'rejected':arrivals-accepted,
            'rejection_rate':round((arrivals-accepted)/arrivals,5) if arrivals else 0,
            'p50_end_to_end_ms':_percentile(latencies,.5),'p95_end_to_end_ms':p95,
            'throughput_rps':round(sum(end<=duration_seconds for end in finished)/duration_seconds,4),
            'slo_met':bool(p95 is not None and p95<=slo_p95_ms),
            'stages':stage_metrics,
            'caution':'Synthetic sequential-chain model only; validate distributional assumptions using actual traces.'}
