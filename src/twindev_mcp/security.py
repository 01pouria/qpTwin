# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

"""Tight read-only boundaries for untrusted repositories.

The MCP client runs this code with the user's OS permissions. Therefore all
client-supplied paths are resolved against one explicit workspace root.
"""
from __future__ import annotations

import os
from pathlib import Path, PurePosixPath, PureWindowsPath

MAX_BYTES = 1024 * 512
SKIP_DIRS = {".git", ".hg", "node_modules", ".venv", "venv", "dist", "build", "target", "coverage", "__pycache__", ".next", ".idea", ".twindev"}
PRIVATE_NAMES = {".env", ".npmrc", ".pypirc", "id_rsa", "id_ed25519", "credentials.json", "secrets.json", "service-account.json"}
SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx"}
MANIFESTS = {"pyproject.toml", "package.json", "requirements.txt"}

class WorkspaceError(ValueError):
    pass

class Workspace:
    def __init__(self, root: str | Path):
        p = Path(root).expanduser().resolve(strict=True)
        if not p.is_dir():
            raise WorkspaceError("Workspace must be an existing directory")
        self.root = p

    def resolve(self, relative: str, *, must_exist: bool = True) -> Path:
        if not isinstance(relative, str) or not relative or "\x00" in relative:
            raise WorkspaceError("Invalid relative path")
        p = Path(relative)
        portable_parts = set(PurePosixPath(relative).parts) | set(PureWindowsPath(relative).parts)
        if (p.is_absolute() or PurePosixPath(relative).is_absolute()
                or PureWindowsPath(relative).is_absolute() or ".." in portable_parts
                or any(x in SKIP_DIRS or x in PRIVATE_NAMES or x.startswith(".env") for x in portable_parts)):
            raise WorkspaceError("Absolute paths, parent traversal and private directories are forbidden")
        try:
            candidate = (self.root / p).resolve(strict=must_exist)
        except OSError as exc:
            raise WorkspaceError("Path does not exist or cannot be resolved") from exc
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise WorkspaceError("Path escapes workspace") from exc
        if must_exist and (not candidate.is_file() or candidate.is_symlink()):
            raise WorkspaceError("Expected regular file")
        # Reject a symlink anywhere on the input path, even when it resolves inside the workspace.
        node = self.root
        for part in p.parts:
            node = node / part
            if node.is_symlink():
                raise WorkspaceError("Symlinks are not permitted")
        return candidate

    def source_files(self, limit: int = 2000) -> list[str]:
        found: list[str] = []
        for directory, dirs, filenames in os.walk(self.root, followlinks=False):
            d = Path(directory)
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not (d / x).is_symlink())
            for name in sorted(filenames):
                p = d / name
                if p.is_symlink() or name in PRIVATE_NAMES or name.startswith(".env"):
                    continue
                if p.suffix not in SOURCE_SUFFIXES and name not in MANIFESTS:
                    continue
                try:
                    if p.stat().st_size > MAX_BYTES:
                        continue
                except OSError:
                    continue
                found.append(p.relative_to(self.root).as_posix())
                if len(found) >= limit:
                    return found
        return found

    def text(self, path: str) -> str:
        target = self.resolve(path)
        if target.stat().st_size > MAX_BYTES:
            raise WorkspaceError("File exceeds safe size limit")
        if target.name in PRIVATE_NAMES or target.name.startswith(".env"):
            raise WorkspaceError("Private configuration files are excluded")
        if target.suffix not in SOURCE_SUFFIXES | {".json", ".yaml", ".yml", ".csv", ".xml", ".toml", ".txt", ".patch", ".diff"}:
            raise WorkspaceError("Unsupported file type")
        return target.read_text(encoding="utf-8", errors="replace")
