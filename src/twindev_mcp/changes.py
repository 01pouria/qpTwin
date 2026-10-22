# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Parse a *supplied* unified diff to connect agent-generated changes to architecture.

Does not execute git or apply patches; paths are validated within one workspace.
"""
from __future__ import annotations
import re
from .discovery import discover,impact
from .security import Workspace, WorkspaceError

_DIFF=re.compile(r'^diff --git a/(\S+) b/(\S+)$')

def inspect_patch(ws:Workspace,patch_file:str)->dict:
    if not patch_file.endswith(('.patch','.diff','.txt')):
        raise ValueError('Supply a local .patch/.diff/.txt file, not shell commands')
    text=ws.text(patch_file)
    changed=[];additions=deletions=0
    for line in text.splitlines():
        if line.startswith('diff --git '):
            match=_DIFF.fullmatch(line)
            if not match:raise ValueError('Unsupported or malformed diff file header')
            before,after=match.groups()
            if before!=after:raise ValueError('Renames not supported in patch analyzer')
            # Workspace.resolve when possible, and explicitly reject new-file traversal.
            try:ws.resolve(after,must_exist=False)
            except WorkspaceError as exc:raise ValueError('Unsafe path found in diff') from exc
            if after not in changed:changed.append(after)
            if len(changed)>100:raise ValueError('Too many changed files')
        elif line.startswith('+') and not line.startswith('+++'):
            additions+=1
        elif line.startswith('-') and not line.startswith('---'):
            deletions+=1
    if not changed:raise ValueError('No diff --git file header found')
    graph=discover(ws)
    existing={x['path'] for x in graph['components']}
    known=[p for p in changed if p in existing]
    unknown=[p for p in changed if p not in existing]
    analyzed=impact(graph,known) if known else {'changed_files':[],'impacted_files':[],'impacted_endpoints':[]}
    return {'changed_files':changed,'existing_files':known,'new_or_unindexed_files':unknown,
            'added_lines':additions,'removed_lines':deletions,
            'impact':analyzed,
            'risk_hints':(['Endpoint contract verification recommended'] if analyzed.get('impacted_endpoints') else []) +
                         (['New/unindexed files require manual review'] if unknown else []),
            'limitations':'Diff is untrusted input; parsing only, not patch application, semantic code review or proof of safe changes.'}
