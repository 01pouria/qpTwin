# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

import json
import math
import pytest
from twindev_mcp.changes import inspect_patch
from twindev_mcp.contracts import compare,inventory
from twindev_mcp.chain import simulate_chain
from twindev_mcp.security import Workspace
from twindev_mcp.simulation import Scenario
from twindev_mcp.tools import analyze_patch,inspect_openapi_contract,compare_openapi_contracts,simulate_microservice_chain,validate_capacity_holdout
from twindev_mcp.validation import validate_holdout
from twindev_mcp.offline_stdio import invoke,definitions


def test_openapi_detects_breaking(workspace):
    old={'openapi':'3.1.0','paths':{'/items':{'get':{'responses':{'200':{'description':'ok'}}}},'/health':{'get':{'responses':{'200':{'description':'ok'}}}}}}
    newer={'openapi':'3.1.0','paths':{'/items':{'get':{'parameters':[{'name':'tenant_id','in':'query','required':True}],'responses':{'201':{'description':'ok'}}}}}}
    (workspace/'old.json').write_text(json.dumps(old))
    (workspace/'new.json').write_text(json.dumps(newer))
    assert inspect_openapi_contract('old.json')['operation_count']==2
    c=compare_openapi_contracts('old.json','new.json')
    assert c['breaking_candidates']==2
    assert c['status']=='REVIEW_REQUIRED'
    assert any(x['kind']=='removed_declared_responses' for x in c['findings'])


def test_openapi_no_network_refs(workspace):
    (workspace/'api.json').write_text(json.dumps({'paths':{'/x':{'get':{'parameters':[{'$ref':'https://bad.invalid/secret'}]}}}}))
    assert inventory(Workspace(workspace),'api.json')['operation_count']==1


def test_chain_deterministic_and_faults():
    stages=[{'name':'api','replicas':3,'service_rps_per_replica':35},
            {'name':'db','replicas':2,'service_rps_per_replica':22}]
    base=simulate_chain(stages,20,30,seed=5)
    assert base==simulate_chain(stages,20,30,seed=5)
    assert base['arrivals']==base['accepted']+base['rejected']
    worse=simulate_chain([{**stages[0],'failed_replicas':2},stages[1]],20,30,seed=5)
    assert worse['rejected']>=0
    assert [s['name'] for s in worse['stages']]==['api','db']


def test_chain_queue_limit_zero_drops():
    stages=[{'name':'api','replicas':1,'service_rps_per_replica':1,'queue_limit':0}]
    r=simulate_chain(stages,40,10)
    assert r['rejected']>0


@pytest.mark.parametrize('bad',[
    [{'name':'dup','replicas':1,'service_rps_per_replica':1},{'name':'dup','replicas':1,'service_rps_per_replica':1}],
    [{'name':'bad','replicas':1,'service_rps_per_replica':math.nan}],
    [{'name':'bad','replicas':True,'service_rps_per_replica':1}],
    [{'name':'bad','replicas':1,'service_rps_per_replica':1,'oops':2}],
])
def test_chain_rejects_bad(bad):
    with pytest.raises(ValueError):simulate_chain(bad,5,10)


def test_holdout_time_series(workspace):
    raw='request_count,mean_service_ms,error_count,observed_p95_ms\n'
    raw+='\n'.join(f'{30+i},55,0,{200+i*2}' for i in range(12))+'\n'
    (workspace/'holdout.csv').write_text(raw)
    r=validate_holdout(Workspace(workspace),'holdout.csv',3,.7,30)
    assert r['test_buckets']>=3
    assert r['mae_p95_ms']>=0
    assert r['verdict']=='MEASURED_NOT_CERTIFIED'
    assert validate_capacity_holdout('holdout.csv',3)['compared_buckets']>=3


def test_patch_analysis(workspace):
    (workspace/'change.patch').write_text('diff --git a/service/billing.py b/service/billing.py\n--- a/service/billing.py\n+++ b/service/billing.py\n@@ -1 +1 @@\n-return x\n+return x*2\n')
    r=analyze_patch('change.patch')
    assert 'service/api.py' in r['impact']['impacted_files']
    assert r['added_lines']==1
    (workspace/'evil.patch').write_text('diff --git a/../top.py b/../top.py\n')
    with pytest.raises(ValueError):analyze_patch('evil.patch')


def test_mcp_v02_tools_available_and_call(workspace):
    names={tool['name'] for tool in definitions()}
    assert {'inspect_openapi_contract','compare_openapi_contracts','simulate_microservice_chain','validate_capacity_holdout','analyze_patch'}<=names
    result=invoke({'jsonrpc':'2.0','id':12,'method':'tools/call','params':{'name':'simulate_microservice_chain','arguments':{'stages':[{'name':'web','replicas':2,'service_rps_per_replica':10}],'arrival_rps':3,'duration_seconds':10}}})
    assert result['result']['isError'] is False
    assert result['result']['structuredContent']['arrivals']>0


def test_nonfinite_rejected():
    with pytest.raises(ValueError):Scenario(math.nan,1,2)
    with pytest.raises(ValueError):Scenario(5,math.inf,2)
    with pytest.raises(ValueError):Scenario(5,5,True)


def test_otlp_aggregation_no_personal_metadata(workspace):
    from twindev_mcp.tools import aggregate_otlp_traces
    export={'resourceSpans':[{'resource':{'attributes':[{'key':'service.name','value':{'stringValue':'api'}}]},'scopeSpans':[{'spans':[
        {'kind':2,'startTimeUnixNano':'1000000000','endTimeUnixNano':'1020000000','name':'/private?token=SECRET','attributes':[{'key':'http.request.header.authorization','value':{'stringValue':'SECRET'}}],'status':{'code':1}},
        {'kind':2,'startTimeUnixNano':'1050000000','endTimeUnixNano':'1080000000','status':{'code':2}}
    ]}]}]}
    (workspace/'trace.json').write_text(json.dumps(export))
    result=aggregate_otlp_traces('trace.json')
    assert result['services'][0]['mean_latency_ms']==25
    assert result['services'][0]['observed_error_fraction']==.5
    assert 'SECRET' not in json.dumps(result)


def test_otlp_bounded_and_empty(workspace):
    from twindev_mcp.tools import aggregate_otlp_traces
    (workspace/'trace.json').write_text('{"resourceSpans":[]}')
    with pytest.raises(ValueError):aggregate_otlp_traces('trace.json')


def test_evidence_review_requires_human_and_reports_gaps(workspace):
    from twindev_mcp.tools import review_change_evidence
    (workspace/'change.patch').write_text('diff --git a/service/billing.py b/service/billing.py\n')
    r=review_change_evidence('change.patch','result.xml')
    assert r['status']=='EVIDENCE_INCOMPLETE'
    assert r['test_evidence']['pass_gate'] is True
    assert 'ADVISORY_ONLY' in r['authority']
    assert 'No architecture boundary policy configured' in r['evidence_gaps']


def test_evidence_review_detects_contract_break(workspace):
    from twindev_mcp.tools import review_change_evidence
    (workspace/'change.patch').write_text('diff --git a/service/api.py b/service/api.py\n')
    old={'paths':{'/old':{'get':{}}}}
    new={'paths':{}}
    (workspace/'old.json').write_text(json.dumps(old))
    (workspace/'new.json').write_text(json.dumps(new))
    r=review_change_evidence('change.patch','result.xml','old.json','new.json')
    assert r['status']=='BLOCKED_FOR_REVIEW'
    assert any('API contract' in b for b in r['blockers'])


def test_bad_protocol_params_do_not_crash():
    assert invoke({'jsonrpc':'2.0','id':1,'method':'tools/call','params':['nonsense']})['error']['code']==-32602
    assert invoke({'jsonrpc':'2.0','id':2,'method':'initialize','params':['nonsense']})['error']['code']==-32602


def test_hidden_env_directory_forbidden(workspace):
    from twindev_mcp.security import WorkspaceError
    (workspace/'.env').mkdir()
    (workspace/'.env'/'bad.py').write_text('print(1)')
    with pytest.raises(WorkspaceError):Workspace(workspace).text('.env/bad.py')


def test_simulation_capacity_comparison_expected_direction():
    stages=[{'name':'web','replicas':1,'service_rps_per_replica':2,'queue_limit':5}]
    small=simulate_chain(stages,12,30,seed=55)
    doubled=simulate_chain([{**stages[0],'replicas':4}],12,30,seed=55)
    assert doubled['rejected'] < small['rejected']


def test_malformed_trace_is_rejected(workspace):
    from twindev_mcp.tools import aggregate_otlp_traces
    (workspace/'trace.json').write_text(json.dumps({'resourceSpans':[{'scopeSpans':[{'spans':[{'kind':2,'startTimeUnixNano':'1','endTimeUnixNano':'0'}]}]}]}))
    with pytest.raises(ValueError):aggregate_otlp_traces('trace.json')
