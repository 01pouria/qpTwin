# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import pytest

@pytest.fixture
def workspace(tmp_path,monkeypatch):
    (tmp_path/'service').mkdir()
    (tmp_path/'service'/'__init__.py').write_text('',encoding='utf8')
    (tmp_path/'service'/'billing.py').write_text('def total(x,y):\n    return x*y\n',encoding='utf8')
    (tmp_path/'service'/'api.py').write_text('from flask import Flask\nfrom service.billing import total\napp=Flask(__name__)\n@app.post("/charge")\ndef charge(): return total(2,3)\n',encoding='utf8')
    (tmp_path/'service'/'invoice.py').write_text('from service.api import charge\n',encoding='utf8')
    (tmp_path/'metrics.csv').write_text('request_count,mean_service_ms,error_count\n100,50,1\n120,40,0\n',encoding='utf8')
    (tmp_path/'result.xml').write_text('<testsuite tests="5" failures="0" errors="0" skipped="1"/>',encoding='utf8')
    monkeypatch.setenv('TWINDEV_WORKSPACE',str(tmp_path))
    return tmp_path
