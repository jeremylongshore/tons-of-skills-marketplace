"""Pack distribution must not silently accept missing or escaping local references."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cw_pack_gate", ROOT / "scripts/validate-coreweave-pack.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def test_installed_reference_must_exist(tmp_path):
    (tmp_path / "SKILL.md").write_text("[procedure](references/missing.md)")
    assert gate.links(tmp_path) == ["SKILL.md: references/missing.md"]


def test_reference_cannot_escape_via_symlink(tmp_path):
    root = tmp_path / "skill"
    root.mkdir()
    outside = tmp_path / "private.md"
    outside.write_text("private")
    (root / "leak.md").symlink_to(outside)
    (root / "SKILL.md").write_text("[procedure](leak.md)")
    assert gate.links(root) == ["SKILL.md: leak.md"]


def test_valid_local_anchor_and_external_reference(tmp_path):
    (tmp_path / "notes.md").write_text("# Notes\n")
    (tmp_path / "SKILL.md").write_text("[notes](notes.md#notes) [reference](https://example.invalid/reference)")
    assert gate.links(tmp_path) == []
