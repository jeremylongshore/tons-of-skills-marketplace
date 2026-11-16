"""Pure-module packaging and trusted-source loading, without changing rule policy."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "agent_body_tools.py"
SPEC = importlib.util.spec_from_file_location("packaged_agent_tools", MODULE)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


@pytest.mark.parametrize("frontmatter", [{}, {"tools": []}, {"tools": ""}])
def test_missing_and_explicit_empty_keep_existing_findings_not_runtime_proof(frontmatter):
    errors, warnings = CHECKER.check_agent_body_vs_allowlist(
        frontmatter, "Use `mcp__fixture__read` to inspect the fixture."
    )
    assert errors == [
        "[agent] body references MCP tools (mcp__fixture__read) but the `tools` allowlist "
        "declares no mcp__* tools — every call would be runtime-blocked (#843 CHECK 3)"
    ]
    assert warnings == []


def test_pure_module_imports_without_site_packages(tmp_path):
    copied = tmp_path / "agent_body_tools.py"
    shutil.copyfile(MODULE, copied)
    result = subprocess.run(
        [sys.executable, "-I", "-S", "-c", "import runpy, sys; "
         "m=runpy.run_path(sys.argv[1]); "
         "assert m['check_agent_body_vs_allowlist']({'tools':['Read']}, 'Read files.') == ([], [])",
         str(copied)],
        capture_output=True, text=True, check=False, timeout=15,
    )
    assert result.returncode == 0, result.stderr


def test_validator_loaded_by_path_ignores_cwd_pythonpath_and_module_cache(tmp_path):
    shadow = tmp_path / "agent_body_tools.py"
    shadow.write_text("raise RuntimeError('untrusted helper executed')\n")
    code = """
import importlib.util, json, sys, types
poison = types.ModuleType('_marketplace_agent_body_tools')
poison.check_agent_body_vs_allowlist = lambda *_: (['untrusted helper executed'], [])
sys.modules['_marketplace_agent_body_tools'] = poison
spec = importlib.util.spec_from_file_location('validator', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(json.dumps(module.check_agent_body_vs_allowlist({'tools':['Read']}, 'Read files.')))
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(ROOT / "scripts/validate-skills-schema.py")],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True, text=True, check=False, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == [[], []]


def test_direct_validator_cli_works_outside_checkout(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate-skills-schema.py"), "--help"],
        cwd=tmp_path, capture_output=True, text=True, check=False, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "--repo-root" in result.stdout
