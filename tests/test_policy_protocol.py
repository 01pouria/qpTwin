# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

import json
import subprocess
import sys
import os
from twindev_mcp.policy import check
from twindev_mcp.security import Workspace
from twindev_mcp.offline_stdio import invoke


def test_architecture_policy(workspace):
    rules={'forbidden_imports':[{'from':'service/api.py','to':'service/billing.py'}]}
    (workspace/'twindev-policy.json').write_text(json.dumps(rules))
    out=check(Workspace(workspace))
    assert out['status']=='VIOLATION'
    assert len(out['findings'])==1

def test_no_architecture_policy(workspace):
    assert check(Workspace(workspace))['status']=='UNCONFIGURED'

def test_legacy_negotiation():
    r=invoke({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18'}})
    assert r['result']['protocolVersion']=='2025-06-18'

def test_real_stdio_roundtrip(workspace):
    env={**os.environ,'PYTHONPATH':os.path.join(os.path.dirname(__file__),'..','src')}
    requests=[
        {'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1.0'}}},
        {'jsonrpc':'2.0','method':'notifications/initialized'},
        {'jsonrpc':'2.0','id':2,'method':'tools/list'},
        {'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'discover_architecture','arguments':{}}},
    ]
    completed=subprocess.run([sys.executable,'-m','twindev_mcp.offline_stdio'],input='\n'.join(json.dumps(v) for v in requests)+'\n',
                             text=True,capture_output=True,env=env,timeout=10)
    assert completed.returncode==0
    replies=[json.loads(line) for line in completed.stdout.splitlines()]
    assert len(replies)==3
    assert replies[2]['result']['structuredContent']['endpoints']
    assert any(t['name']=='simulate_capacity' for t in replies[1]['result']['tools'])
