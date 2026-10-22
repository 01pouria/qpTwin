# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Single source of MCP tool functions; core engine is MCP-SDK independent."""
from __future__ import annotations
import os
from pathlib import Path
from .security import Workspace
from .discovery import discover, impact
from .quality import scan, junit, release_gate
from .simulation import Scenario, simulate, compare
from .telemetry import calibrate
from .snapshots import save, compare as compare_snapshots
from .policy import check as check_policy

_tool_registry: dict[str, callable] = {}

def register(func):
    _tool_registry[func.__name__]=func
    return func

def _workspace():
    path=os.environ.get('TWINDEV_WORKSPACE')
    if not path:
        raise RuntimeError('TWINDEV_WORKSPACE must be set to one absolute project directory')
    if not Path(path).is_absolute():
        raise RuntimeError('TWINDEV_WORKSPACE must be absolute')
    return Workspace(path)

@register
def workspace_overview() -> dict:
    """Describe the configured, filesystem-scoped software project without exposing source contents."""
    ws=_workspace()
    data=discover(ws)
    return {"workspace":ws.root.name,"scanned_files":data['scanned_files'],
            "source_files":len([x for x in data['components'] if x['kind']!='manifest']),
            "internal_import_edges":len(data['dependencies']), "api_routes":len(data['endpoints']),
            "read_only":True,"restrictions":"No arbitrary shell, no file writes except explicit metadata snapshots, no symlink traversal"}

@register
def discover_architecture() -> dict:
    """Build a best-effort architecture graph from Python/JS/TS imports and static API routes (read-only)."""
    return discover(_workspace())

@register
def analyze_change(changed_files: list[str], depth: int = 4) -> dict:
    """Trace reverse dependencies and API-route exposure of existing changed files; not a correctness proof."""
    if not 1 <= len(changed_files) <= 100: raise ValueError('Supply 1-100 changed files')
    if not 0 <= depth <= 12: raise ValueError('Depth must be 0-12')
    ws=_workspace()
    for file in changed_files:
        ws.resolve(file)
    return impact(discover(ws),changed_files,depth)

@register
def inspect_endpoints() -> dict:
    """List statically recognized Flask/FastAPI/Express routes and handlers to support contract review."""
    graph=discover(_workspace())
    return {"endpoints":graph['endpoints'],"count":len(graph['endpoints']),
            "warning":"Dynamic routing and framework decorators not recognized by parser are omitted."}

@register
def scan_code_risks() -> dict:
    """Non-executing static scan for selected security smells; results require human review."""
    return scan(_workspace())

@register
def simulate_capacity(arrival_rps: float, service_rps_per_replica: float, replicas: int,
                      duration_seconds: int=300, queue_limit: int=1000,
                      failed_replicas: int=0, seed: int=42, slo_p95_ms:float=1200) -> dict:
    """Bounded seeded discrete-event M/M/c capacity simulation with queue, failover and SLO metrics."""
    return simulate(Scenario(arrival_rps,service_rps_per_replica,replicas,duration_seconds,queue_limit,failed_replicas,seed,slo_p95_ms))

@register
def compare_capacity_scenarios(baseline: dict, candidate: dict) -> dict:
    """Compare two complete Scenario dictionaries using the same bounded simulation engine."""
    return compare(Scenario(**baseline),Scenario(**candidate))

@register
def calibrate_from_csv(csv_path: str, interval_seconds: float=60.0) -> dict:
    """Estimate arrival and mean service rates from aggregate CSV metrics; never expose raw rows."""
    return calibrate(_workspace(),csv_path,interval_seconds)

@register
def inspect_junit(report_path: str) -> dict:
    """Read existing JUnit XML results without running project code or tests."""
    return junit(_workspace(),report_path)

@register
def evaluate_release(report_path: str, observed_p95_ms: float | None=None, max_p95_ms:float=1200.0) -> dict:
    """Advisory release gate using JUnit evidence, static risk indicators and supplied measured p95 latency."""
    return release_gate(_workspace(),report_path,observed_p95_ms,max_p95_ms)

@register
def save_architecture_snapshot(name: str) -> dict:
    """Explicitly write a metadata-only architecture snapshot under workspace/.twindev/snapshots."""
    return save(_workspace(),name)

@register
def compare_architecture_snapshot(name: str) -> dict:
    """Compare current static architecture metadata against a previously saved snapshot."""
    return compare_snapshots(_workspace(),name)

@register
def propose_validation_plan(changed_files: list[str]) -> dict:
    """Suggest risk-focused checks and simulation tasks for an AI-generated pull request."""
    analysis=analyze_change(changed_files)
    checks=[{"kind":"required","action":"Run unit, integration and contract tests via a controlled CI pipeline"},
            {"kind":"required","action":"Review static indicators and inspect changed endpoints with a human reviewer"}]
    if analysis['impacted_endpoints']:
        checks += [{"kind":"recommended","action":"Run API contract/backward-compatibility tests"},
                   {"kind":"recommended","action":"Run scenario capacity simulation and compare with measured load tests"}]
    if any('auth' in x.lower() or 'security' in x.lower() for x in changed_files):
        checks.append({"kind":"required","action":"Threat-model authentication, authorization and tenant separation"})
    if any('database' in x.lower() or 'model' in x.lower() for x in changed_files):
        checks.append({"kind":"recommended","action":"Review transaction isolation, migration reversibility and data integrity"})
    return {"impact":analysis,"validation_plan":checks,
            "approval":"Do not merge or deploy solely based on this suggestion."}

@register
def twindev_help(topic: str='workflow') -> dict:
    """Provide agent guidance for responsible twin-assisted software changes."""
    topics = {
        'workflow': ["Discover architecture", "Analyze changed file impact", "Review API/risks", "Simulate only measurable scenarios", "Write code via coding agent", "Execute tests in sandbox/CI", "Compare observations to prediction", "Human approval"],
        'limits':["Only static best-effort graph", "No executing or changing user code", "Queueing model is M/M/c, not real GPU inference", "No live production telemetry connector", "No autonomous merge or deployment"],
        'security':["Use least-privilege workspace", "Treat source and external results as untrusted", "Avoid secrets in CSV", "Keep backups and human review", "Run CI tests separately in sandbox"]
    }
    if topic not in topics: raise ValueError('Choose workflow, limits or security')
    return {"topic":topic,"guidance":topics[topic]}

@register
def check_architecture_policy() -> dict:
    """Enforce optional twindev-policy.json forbidden-import boundaries in the current workspace."""
    return check_policy(_workspace())

@register
def redteam_architecture_review() -> dict:
    """CIA-oriented /redteam checklist grounded in static evidence; advisory, never a security certification."""
    ws=_workspace()
    graph=discover(ws)
    risks=scan(ws)
    policy=check_policy(ws)
    high=[x for x in risks['findings'] if x['severity']=='high']
    return {
      'confidentiality':{
        'observed_signals': [x for x in risks['findings'] if x['code'] in ('possible_hardcoded_secret','html_injection_sink')],
        'manual_checks':['Tenant isolation across APIs and databases','Secret storage and rotation','Sensitive data retention policies','Threat-model prompt injection and untrusted repository content']},
      'integrity':{
        'observed_signals': policy['findings'],
        'manual_checks':['API schema compatibility','Migration reversibility','Authentication and authorization bypass tests','Supply-chain pinning and build provenance']},
      'availability':{
        'observed_signals':{'api_routes':len(graph['endpoints']),'components':len(graph['components'])},
        'manual_checks':['Capacity simulation calibrated with load testing','Circuit breaker/retry storms','Failover and restore drills','Rate limiting and backpressure per tenant']},
      'static_high_count':len(high),'architecture_policy_status':policy['status'],
      'verdict':'NEEDS_HUMAN_REVIEW',
      'limits':'Static evidence cannot validate access controls, runtime failure modes or business continuity.'}

@register
def inspect_openapi_contract(json_path: str) -> dict:
    """Inventory local OpenAPI JSON methods, routes and required inputs without loading network refs."""
    from .contracts import inventory
    return inventory(_workspace(), json_path)

@register
def compare_openapi_contracts(old_json_path: str, new_json_path: str) -> dict:
    """Flag candidate backward-incompatible API contract changes, never silently approve them."""
    from .contracts import compare
    return compare(_workspace(),old_json_path,new_json_path)

@register
def simulate_microservice_chain(stages: list[dict], arrival_rps: float,
                                duration_seconds:int=120, seed:int=42, slo_p95_ms:float=1500) -> dict:
    """Simulate 1-12 sequential microservice stages with independent queues, capacity and failures."""
    from .chain import simulate_chain
    return simulate_chain(stages,arrival_rps,duration_seconds,seed,slo_p95_ms)

@register
def validate_capacity_holdout(csv_path: str, replicas:int,train_fraction:float=.7,
                              interval_seconds:float=60.,seed:int=42) -> dict:
    """Measure M/M/c p95 prediction error on chronological held-out aggregate telemetry buckets."""
    from .validation import validate_holdout
    return validate_holdout(_workspace(),csv_path,replicas,train_fraction,interval_seconds,seed)

@register
def analyze_patch(patch_path: str) -> dict:
    """Read a local unified .patch/.diff and locate changed files plus reverse dependency impact."""
    from .changes import inspect_patch
    return inspect_patch(_workspace(),patch_path)

@register
def aggregate_otlp_traces(json_path: str) -> dict:
    """Read local OTLP JSON and compute per-service aggregate latency/error metrics without returning payloads."""
    from .traces import aggregate_traces
    return aggregate_traces(_workspace(),json_path)

@register
def review_change_evidence(patch_path:str,junit_path:str,
                           old_contract_path:str|None=None,new_contract_path:str|None=None,
                           holdout_path:str|None=None,replicas:int=1) -> dict:
    """Combine patch impact, tests, security, architecture, API compatibility and model fit in an advisory release review."""
    from .review import review
    return review(_workspace(),patch_path,junit_path,old_contract_path,new_contract_path,holdout_path,replicas)
