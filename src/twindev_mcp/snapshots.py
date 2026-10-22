# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Explicit snapshots of sanitized metadata; no source content persisted."""
from __future__ import annotations
import json
import os
import re
import tempfile
from pathlib import Path
from .security import Workspace, WorkspaceError
from .discovery import discover

NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")

def _snapshot_path(ws: Workspace, name: str) -> Path:
    if not NAME_RE.fullmatch(name): raise ValueError("Invalid snapshot name")
    return ws.root / ".twindev" / "snapshots" / (name + ".json")


def _check_private_dir(ws:Workspace) -> Path:
    base = ws.root / '.twindev'
    folder = base / 'snapshots'
    if base.is_symlink() or folder.is_symlink(): raise WorkspaceError("Symlinked snapshot directory forbidden")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    return folder


def save(ws: Workspace,name:str) -> dict:
    path=_snapshot_path(ws,name)
    _check_private_dir(ws)
    if path.is_symlink(): raise WorkspaceError("Symlink snapshot file forbidden")
    graph=discover(ws)
    graph.pop("workspace",None)
    contents=json.dumps(graph,ensure_ascii=False,separators=(',',':'))
    if len(contents)>5_000_000: raise ValueError("Snapshot too large")
    tmp_fd,tmp_name=tempfile.mkstemp(prefix='.partial-',dir=path.parent)
    try:
        with os.fdopen(tmp_fd,'w',encoding='utf-8') as f:
            if hasattr(os, "fchmod"):
                os.fchmod(f.fileno(),0o600)
            f.write(contents)
        os.replace(tmp_name,path)
    finally:
        if os.path.exists(tmp_name): os.unlink(tmp_name)
    return {"snapshot":name,"path":f".twindev/snapshots/{name}.json","components":len(graph['components']),"contains_source_code":False}


def compare(ws:Workspace,name:str) -> dict:
    path=_snapshot_path(ws,name)
    _check_private_dir(ws)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 5_000_000:
        raise ValueError("Snapshot missing or unsafe")
    before=json.loads(path.read_text(encoding='utf-8'))
    after=discover(ws)
    def keys(graph,key):return {json.dumps(x,sort_keys=True) for x in graph[key]}
    result={}
    for key in ('components','dependencies','endpoints'):
        a,b=keys(before,key),keys(after,key)
        result[key]={"added":[json.loads(x) for x in sorted(b-a)], "removed":[json.loads(x) for x in sorted(a-b)]}
    return {"snapshot":name,"delta":result,"limitation":"Static metadata snapshot, not proof that executable behavior is unchanged"}
