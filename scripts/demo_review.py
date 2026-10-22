# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Print an entirely local demonstration review, without changing source or running project code."""
from __future__ import annotations
import json
import os
from pathlib import Path
from twindev_mcp.security import Workspace
from twindev_mcp.review import review

folder=Path(__file__).resolve().parent.parent/'examples'/'demo_repository'
report=review(Workspace(folder),'pr.diff','test-result.xml',
              'openapi-before.json','openapi-after.json','holdout.csv',2)
print(json.dumps(report,indent=2,ensure_ascii=False))
