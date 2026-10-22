# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

import pytest
from twindev_mcp.security import Workspace,WorkspaceError


def test_traversal_denied(workspace):
    ws=Workspace(workspace)
    for p in ('../outside','/etc/passwd','service/../service/api.py','.git/config','.twindev/x'):
        with pytest.raises(WorkspaceError): ws.resolve(p)

def test_symlink_escape_denied(workspace,tmp_path):
    link=workspace/'escape.py'
    try:
        link.symlink_to('/etc/passwd')
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
    with pytest.raises(WorkspaceError): Workspace(workspace).resolve('escape.py')

def test_symlink_internal_denied(workspace):
    try:
        (workspace/'inside.py').symlink_to(workspace/'service'/'api.py')
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
    with pytest.raises(WorkspaceError): Workspace(workspace).resolve('inside.py')

def test_private_excluded(workspace):
    (workspace/'.env').write_text('API_KEY=SECRET')
    (workspace/'node_modules').mkdir()
    (workspace/'node_modules'/'hack.py').write_text('print("x")')
    ws=Workspace(workspace)
    assert '.env' not in ws.source_files()
    assert 'node_modules/hack.py' not in ws.source_files()
    with pytest.raises(WorkspaceError):ws.text('.env')

def test_bounded_file_size(workspace):
    (workspace/'massive.py').write_text('x' * (512*1024+1))
    assert 'massive.py' not in Workspace(workspace).source_files()

def test_nested_symlink_denied(workspace):
    try:
        (workspace/'alias').symlink_to(workspace/'service',target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
    with pytest.raises(WorkspaceError):Workspace(workspace).resolve('alias/api.py')
