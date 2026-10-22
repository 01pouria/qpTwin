# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

from flask import Flask
from backend.billing import charge
app = Flask(__name__)

@app.get('/health')
def health():
    return {'ok':True}

@app.post('/invoices')
def create_invoice():
    return {'status':'created'}
