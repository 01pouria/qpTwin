# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Reproducible advisory report across architecture, contracts, tests, model fit and CIA.

No tool ever grants a production deployment or Git merge permission.
"""
from __future__ import annotations
from .security import Workspace
from .changes import inspect_patch
from .contracts import compare
from .quality import scan,junit
from .policy import check as check_policy
from .validation import validate_holdout


def review(ws:Workspace, patch_path:str, junit_path:str,
           old_contract_path:str | None=None,new_contract_path:str | None=None,
           holdout_path:str | None=None,replicas:int=1) -> dict:
    if (old_contract_path is None)!=(new_contract_path is None):
        raise ValueError('Supply both old and new OpenAPI contracts, or neither')
    change=inspect_patch(ws,patch_path)
    test=junit(ws,junit_path)
    risks=scan(ws)
    policy=check_policy(ws)
    contract=compare(ws,old_contract_path,new_contract_path) if old_contract_path else None
    fit=validate_holdout(ws,holdout_path,replicas) if holdout_path else None
    blockers=[]
    gaps=[]
    if not test['pass_gate']:blockers.append('JUnit failing or empty')
    highs=[x for x in risks['findings'] if x['severity']=='high']
    if highs:blockers.append(f'{len(highs)} high-risk static indicators require human investigation')
    if policy['status']=='VIOLATION':blockers.append('Architecture boundary policy violation')
    if contract and contract['breaking_candidates']:
        blockers.append(f"{contract['breaking_candidates']} possible breaking API contract changes")
    if policy['status']=='UNCONFIGURED':gaps.append('No architecture boundary policy configured')
    if not contract:gaps.append('No OpenAPI before/after compatibility evidence')
    if not fit:gaps.append('No measured simulation holdout accuracy evidence')
    else:gaps.append('Holdout error measured but acceptance threshold not defined; needs owner review')
    if change['new_or_unindexed_files']:gaps.append('New/unindexed files need independent review')
    status='BLOCKED_FOR_REVIEW' if blockers else 'EVIDENCE_INCOMPLETE' if gaps else 'READY_FOR_HUMAN_REVIEW'
    return {'status':status,'blockers':blockers,'evidence_gaps':gaps,
            'changed_files':change['changed_files'],
            'impact':change['impact'],
            'test_evidence':test,
            'static_findings':{'count':risks['count'],'high_count':len(highs)},
            'architecture_policy':{'status':policy['status'],'rule_count':policy.get('rules',0)},
            'contract_evidence':contract,
            'model_validation':fit,
            'authority':'ADVISORY_ONLY — cannot approve merge, deploy, tenant access, or any security certification.',
            'security_note':'All artifacts are supplied by user/CI and are not cryptographically attested to a commit; verify CI provenance independently.'}
