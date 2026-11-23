"""Run the documented replacement sequence with an inert local CLI fixture."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/saas-packs/supabase-pack/skills/supabase-upgrade-migration/SKILL.md"


def run_example(tmp_path, output, exit_code=0, target_kind="file"):
    blocks = re.findall(r"```bash\n(.*?)\n```", SKILL.read_text(), re.S)
    script = next(block for block in blocks if "# Preserve existing types" in block)
    (tmp_path / "lib").mkdir()
    target = tmp_path / "lib/database.types.ts"
    original = b"export type Existing = string;\n"
    victim = tmp_path / "original.ts"
    if target_kind == "symlink":
        victim.write_bytes(original)
        target.symlink_to(victim)
    elif target_kind == "directory":
        target.mkdir()
    elif target_kind == "file":
        target.write_bytes(original)
    binary = tmp_path / "node_modules/.bin/supabase"
    binary.parent.mkdir(parents=True)
    binary.write_text(
        f"#!/bin/bash\nprintf '%s\\n' \"$@\" > called-args.txt\ncat fixture-output.txt\nexit {exit_code}\n"
    )
    binary.chmod(0o700)
    (tmp_path / "fixture-output.txt").write_bytes(output)
    result = subprocess.run(
        ["/bin/bash", "--noprofile", "--norc", "-c", script],
        cwd=tmp_path,
        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"},
        capture_output=True,
        timeout=10,
    )
    assert not list((tmp_path / "lib").glob(".database.types.*"))
    return result, target, original, victim


@pytest.mark.parametrize("output,exit_code", [(b"partial types", 7), (b"", 0)])
def test_failed_or_empty_generation_preserves_existing_file(tmp_path, output, exit_code):
    result, target, original, _ = run_example(tmp_path, output, exit_code)
    assert result.returncode != 0
    assert target.read_bytes() == original
    assert not result.stdout


@pytest.mark.parametrize("target_kind", ["file", "absent"])
def test_success_publishes_complete_candidate(tmp_path, target_kind):
    generated = b"export type Database = { public: { Tables: {} } };\n"
    result, target, _, _ = run_example(tmp_path, generated, target_kind=target_kind)
    assert result.returncode == 0, result.stderr.decode()
    assert target.read_bytes() == generated
    assert not result.stdout
    assert (tmp_path / "called-args.txt").read_text().splitlines() == [
        "gen",
        "types",
        "--lang",
        "typescript",
        "--schema",
        "public",
    ]


@pytest.mark.parametrize("target_kind", ["symlink", "directory"])
def test_unsafe_target_refused_before_cli_execution(tmp_path, target_kind):
    result, target, original, victim = run_example(tmp_path, b"new", target_kind=target_kind)
    assert result.returncode != 0
    assert not (tmp_path / "called-args.txt").exists()
    if target_kind == "symlink":
        assert target.is_symlink()
        assert victim.read_bytes() == original
    else:
        assert target.is_dir()
