# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Strict JSON Schema conformance of legacy adapter to real supported arguments."""
from twindev_mcp.offline_stdio import definitions, invoke
from jsonschema import Draft202012Validator


def test_mcp_schema_real_dict_list_dict_inputs():
    tools={d['name']: d for d in definitions()}
    samples={
        'compare_capacity_scenarios': {'baseline':{'arrival_rps':5,'service_rps_per_replica':10,'replicas':1},
                                      'candidate':{'arrival_rps':5,'service_rps_per_replica':10,'replicas':2}},
        'simulate_microservice_chain': {'stages':[{'name':'api','replicas':1,'service_rps_per_replica':10}], 'arrival_rps':5},
    }
    for name,args in samples.items():
        spec=tools[name]['inputSchema']
        Draft202012Validator.check_schema(spec)
        assert not list(Draft202012Validator(spec).iter_errors(args))
        assert not invoke({'jsonrpc':'2.0','id':3,'method':'tools/call',
                           'params':{'name':name,'arguments':args}})['result']['isError']


def test_typed_parameters_reject_wrong_inputs():
    for key,value in [('replicas',1.5),('replicas',True),('duration_seconds',1.5)]:
        args={'arrival_rps':5,'service_rps_per_replica':10,'replicas':2, 'duration_seconds':10}
        args[key]=value
        r=invoke({'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'simulate_capacity','arguments':args}})
        assert r['result']['isError'] is True
