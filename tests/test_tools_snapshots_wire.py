# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

import os
import pytest
from twindev_mcp.tools import (_tool_registry,workspace_overview,analyze_change,simulate_capacity,propose_validation_plan,save_architecture_snapshot,compare_architecture_snapshot,calibrate_from_csv,evaluate_release)
from twindev_mcp.offline_stdio import invoke,definitions


def test_registered_tools():
    assert len(_tool_registry)>=12
    assert 'simulate_capacity' in _tool_registry

def test_tool_outputs(workspace):
    assert workspace_overview()['api_routes']>=1
    assert 'service/api.py' in analyze_change(['service/billing.py'])['impacted_files']
    assert simulate_capacity(3,4,2,30)['effective_replicas']==2
    assert calibrate_from_csv('metrics.csv')['requests']==220
    assert propose_validation_plan(['service/billing.py'])['validation_plan']
    assert evaluate_release('result.xml',100)['status']=='ADVISORY_PASS'

def test_explicit_snapshot(workspace):
    out=save_architecture_snapshot('baseline')
    assert out['contains_source_code'] is False
    (workspace/'service'/'new.py').write_text('def x():return 1')
    x=compare_architecture_snapshot('baseline')
    assert any(y['path']=='service/new.py' for y in x['delta']['components']['added'])

def test_snapshot_traversal(workspace):
    with pytest.raises(ValueError):save_architecture_snapshot('../outside')

def test_snapshot_directory_symlink_denied(workspace,tmp_path):
    try:
        (workspace/'.twindev').symlink_to(tmp_path,target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
    with pytest.raises(ValueError):save_architecture_snapshot('bad')

def test_mcp_initialize():
    msg=invoke({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1'}}})
    assert msg['result']['capabilities']['tools'] is not None

def test_mcp_list_and_call(workspace):
    lst=invoke({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']
    assert any(x['name']=='discover_architecture' for x in lst)
    result=invoke({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'workspace_overview','arguments':{}}})
    assert result['result']['structuredContent']['api_routes']>=1

def test_mcp_errors_bounded(workspace):
    result=invoke({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'analyze_change','arguments':{'changed_files':['../other']}}})
    assert result['result']['isError']
    assert invoke({'jsonrpc':'2.0','id':4,'method':'missing'})['error']['code']==-32601
    assert invoke({'jsonrpc':'2.0','method':'notifications/initialized'}) is None

def test_mcp_bad_arg_type(workspace):
    x=invoke({'jsonrpc':'2.0','id':5,'method':'tools/call','params':{'name':'simulate_capacity','arguments':{'arrival_rps':'7','service_rps_per_replica':5,'replicas':2}}})
    assert x['result']['isError']
