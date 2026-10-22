# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Reproducible performance model validation against held-out, aggregate observations."""
from __future__ import annotations
import csv
import io
import math
import statistics
from .security import Workspace
from .simulation import Scenario, simulate


def validate_holdout(ws:Workspace,csv_path:str, replicas:int,
                     train_fraction:float=0.7,interval_seconds:float=60.,seed:int=42) -> dict:
    """Chronological train/test split; measured p95 evaluated against modelled p95.

    Required columns: request_count,mean_service_ms,error_count,observed_p95_ms.
    This is an intentionally low fidelity M/M/c proxy, not calibration of GPU latency.
    """
    if type(replicas) is not int or not 1<=replicas<=128:raise ValueError('Invalid replicas')
    if not 0.5<=train_fraction<=0.9 or not 1<=interval_seconds<=600:raise ValueError('Invalid split/interval')
    rows=list(csv.DictReader(io.StringIO(ws.text(csv_path))))
    if not 8<=len(rows)<=1000:raise ValueError('Expected 8-1000 chronological telemetry buckets')
    fields={'request_count','mean_service_ms','error_count','observed_p95_ms'}
    if not fields.issubset(rows[0]):raise ValueError('Expected request_count,mean_service_ms,error_count,observed_p95_ms headers')
    data=[]
    for row in rows:
        try:
            n=int(row['request_count']);errors=int(row['error_count'])
            ms=float(row['mean_service_ms']);p95=float(row['observed_p95_ms'])
        except (ValueError,TypeError) as exc:raise ValueError('Invalid telemetry numbers') from exc
        if n<0 or errors<0 or errors>n or not 0<ms<=1e7 or not 0<p95<=1e8 or not math.isfinite(ms) or not math.isfinite(p95):
            raise ValueError('Invalid telemetry measurement')
        data.append((n,ms,p95))
    n_train=int(len(data)*train_fraction)
    train,test=data[:n_train],data[n_train:]
    if sum(x[0] for x in train)==0:raise ValueError('Training window contains no requests')
    service_ms=sum(x[0]*x[1] for x in train)/sum(x[0] for x in train)
    mu=1000/service_ms
    predictions=[]
    for i,(count,ms,observed) in enumerate(test):
        if count==0:continue
        result=simulate(Scenario(arrival_rps=count/interval_seconds,
                                  service_rps_per_replica=mu,replicas=replicas,
                                  duration_seconds=max(1,round(interval_seconds)),
                                  seed=seed+i,queue_limit=10000))
        if result['p95_latency_ms'] is not None:
            predictions.append((result['p95_latency_ms'],observed))
    if not predictions:raise ValueError('No test buckets contain traffic')
    errors=[abs(p-o) for p,o in predictions]
    pct_errors=[abs(p-o)/o for p,o in predictions]
    bias=statistics.mean(p-o for p,o in predictions)
    return {'train_buckets':len(train),'test_buckets':len(test), 'compared_buckets':len(predictions),
            'trained_mean_service_ms':round(service_ms,3),'mae_p95_ms':round(statistics.mean(errors),3),
            'mean_absolute_percentage_error':round(statistics.mean(pct_errors),4),
            'bias_ms':round(bias,3),
            'model':'M/M/c proxy trained only on earlier aggregate buckets and evaluated on later p95 observations',
            'verdict':'MEASURED_NOT_CERTIFIED',
            'limits':'Small short-window Monte Carlo simulations have sampling variance; coarse aggregate mean service times do not identify tails, retries or correlated workloads. No proof of future accuracy.'}
