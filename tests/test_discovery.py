# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

import pytest
from twindev_mcp.security import Workspace
from twindev_mcp.discovery import discover,impact


def test_routes_and_imports(workspace):
    g=discover(Workspace(workspace))
    assert any(e['path']=='/charge' and e['method']=='POST' for e in g['endpoints'])
    assert any(e['from']=='service/api.py' and e['to']=='service/billing.py' for e in g['dependencies'])

def test_reverse_impact(workspace):
    g=discover(Workspace(workspace))
    r=impact(g,['service/billing.py'])
    assert 'service/api.py' in r['impacted_files']
    assert any(e['path']=='/charge' for e in r['impacted_endpoints'])

def test_impact_invalid(workspace):
    with pytest.raises(ValueError):impact(discover(Workspace(workspace)),['nonexistent.py'])

def test_js_typescript_routes(workspace):
    (workspace/'app.ts').write_text("import { add } from './math';\nrouter.get('/v1/items', handler);",encoding='utf8')
    (workspace/'math.ts').write_text('export const add = (a,b)=>a+b;',encoding='utf8')
    g=discover(Workspace(workspace))
    assert any(x['path']=='/v1/items' for x in g['endpoints'])
    assert {'from':'app.ts','to':'math.ts','kind':'import'} in g['dependencies']

def test_syntax_warning_not_crash(workspace):
    (workspace/'bad.py').write_text('def x(:')
    assert any(w['path']=='bad.py' for w in discover(Workspace(workspace))['warnings'])

def test_root_relative_import(workspace):
    (workspace/'root_a.py').write_text('from . import root_b\n')
    (workspace/'root_b.py').write_text('VALUE = 1\n')
    g=discover(Workspace(workspace))
    assert any(d['from']=='root_a.py' and d['to']=='root_b.py' for d in g['dependencies'])
