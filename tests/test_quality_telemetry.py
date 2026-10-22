# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

import pytest
from twindev_mcp.security import Workspace
from twindev_mcp.telemetry import calibrate
from twindev_mcp.quality import scan,junit,release_gate


def test_calibration(workspace):
    out=calibrate(Workspace(workspace),'metrics.csv',60)
    assert out['requests']==220
    assert out['estimated_arrival_rps']>1
    assert out['mean_service_ms']>40

def test_calibration_refuses_bad(workspace):
    (workspace/'bad.csv').write_text('request_count,mean_service_ms,error_count\n5,-9,0\n')
    with pytest.raises(ValueError):calibrate(Workspace(workspace),'bad.csv')

def test_junit_pass(workspace):
    x=junit(Workspace(workspace),'result.xml')
    assert x['pass_gate'] and x['passed']==4

def test_junit_fail(workspace):
    (workspace/'fail.xml').write_text('<testsuite tests="1" failures="1" errors="0"/>')
    assert not junit(Workspace(workspace),'fail.xml')['pass_gate']

def test_xml_entity_denied(workspace):
    (workspace/'entity.xml').write_text('<!DOCTYPE r [<!ENTITY xx SYSTEM "file:///etc/passwd">]><r>&xx;</r>')
    with pytest.raises(ValueError):junit(Workspace(workspace),'entity.xml')

def test_code_risks(workspace):
    (workspace/'service'/'unsafe.py').write_text('import subprocess\ndef x():\n    subprocess.run("echo hello",shell=True)\n')
    s=scan(Workspace(workspace))
    assert any(f['code']=='shell_true' for f in s['findings'])

def test_release_gate_missing_latency(workspace):
    x=release_gate(Workspace(workspace),'result.xml')
    assert x['status']=='REVIEW_REQUIRED'

def test_release_advisory_pass(workspace):
    x=release_gate(Workspace(workspace),'result.xml',100,1200)
    assert x['status']=='ADVISORY_PASS'
