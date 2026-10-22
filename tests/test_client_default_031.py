# Copyright 2026 Pouriya Khalilian
# SPDX-License-Identifier: Apache-2.0

import json
import subprocess
import sys
from pathlib import Path


def test_config_generator_defaults_to_locally_tested_legacy(tmp_path):
    root = Path(__file__).resolve().parents[1]
    destination = tmp_path / "client-output"
    p = subprocess.run(
        [sys.executable, str(root / "scripts/generate_client_configs.py"), "--workspace", str(tmp_path), "--output", str(destination)],
        capture_output=True, text=True, timeout=10,
    )
    assert p.returncode == 0, p.stderr
    cfg = json.loads((destination / ".mcp.json").read_text())
    assert cfg["mcpServers"]["qptwin"]["args"] == ["-m", "twindev_mcp.offline_stdio"]
