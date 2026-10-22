# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

from flask import Flask
from . import billing
app=Flask(__name__)

@app.get('/health')
def health():return {'ok':True}

@app.post('/charge')
def charge():return {'invoice':billing.total(2,3)}
