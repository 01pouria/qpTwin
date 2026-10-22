# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

import pytest
from twindev_mcp.simulation import Scenario,simulate,compare


def test_repeatability():
    s=Scenario(2,3,2,100,10,0,99)
    assert simulate(s)==simulate(s)

def test_fails_under_load():
    x=simulate(Scenario(90,1,1,10,0))
    assert x['rejected'] > 0

def test_high_capacity_improves_latency():
    slow=simulate(Scenario(7,3,2,300,1000,0,10))
    fast=simulate(Scenario(7,3,5,300,1000,0,10))
    assert fast['p95_latency_ms'] < slow['p95_latency_ms']

def test_failover_capacity():
    x=simulate(Scenario(6,3,4,200,200,1))
    assert x['effective_replicas']==3

def test_invalid_scenarios():
    bad=[{'arrival_rps':0,'service_rps_per_replica':1,'replicas':1},
         {'arrival_rps':1,'service_rps_per_replica':1,'replicas':1,'failed_replicas':1},
         {'arrival_rps':20000,'service_rps_per_replica':1,'replicas':1,'duration_seconds':3600}]
    for payload in bad:
        with pytest.raises(ValueError):Scenario(**payload)

def test_compare():
    a=Scenario(4,3,1,100)
    b=Scenario(4,3,3,100)
    x=compare(a,b)
    assert 'baseline' in x and 'candidate' in x and 'difference' in x

def test_stability_when_low_traffic():
    x=simulate(Scenario(.001,5,2,10))
    assert x['p95_latency_ms'] is None or x['p95_latency_ms']>=0
