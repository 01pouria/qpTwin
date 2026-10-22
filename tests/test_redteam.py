# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

from twindev_mcp.tools import redteam_architecture_review

def test_redteam_sections(workspace):
    x=redteam_architecture_review()
    assert set(('confidentiality','integrity','availability'))<=set(x)
    assert x['verdict']=='NEEDS_HUMAN_REVIEW'
