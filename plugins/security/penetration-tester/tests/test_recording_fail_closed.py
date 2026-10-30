"""Actual recording CLI behavior using local dummy evidence; no GPG or targets."""

import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def recorder():
    script = Path(__file__).resolve().parents[1] / "skills/recording-pentest-engagement/scripts/record_engagement.py"
    spec = importlib.util.spec_from_file_location("recording_fail_closed", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def engagement(tmp_path):
    root = tmp_path / "engagement"
    root.mkdir()
    (root / "evidence.txt").write_text("original fixture\n")
    return root


@pytest.mark.parametrize("change", ["modified", "added", "missing"])
@pytest.mark.parametrize("severity", ["info", "critical"])
def test_integrity_failure_preserves_prior_artifacts(recorder, engagement, tmp_path, monkeypatch, change, severity):
    assert recorder.main([str(engagement)]) == 0
    manifest = engagement / "manifest.sha256"
    original = manifest.read_bytes()
    signature = engagement / "manifest.sha256.asc"
    signature.write_bytes(b"prior signature fixture")
    archive = tmp_path / "prior.tar.gz"
    archive.write_bytes(b"prior archive fixture")
    if change == "modified":
        (engagement / "evidence.txt").write_text("changed fixture\n")
    elif change == "added":
        (engagement / "new.txt").write_text("new fixture\n")
    else:
        (engagement / "evidence.txt").unlink()
    monkeypatch.setattr(recorder, "sign_manifest", lambda *args: pytest.fail("must not sign failed evidence"))
    monkeypatch.setattr(recorder, "create_tar", lambda *args: pytest.fail("must not package failed evidence"))
    assert recorder.main([str(engagement), "--sign", "--tar", str(archive), "--min-severity", severity]) != 0
    assert manifest.read_bytes() == original
    assert signature.read_bytes() == b"prior signature fixture"
    assert archive.read_bytes() == b"prior archive fixture"
    assert recorder.main([str(engagement)]) != 0


@pytest.mark.parametrize(
    "contents",
    ["invalid\n", "0" * 64 + "  ../outside\n", "0" * 64 + "  /outside\n", ("0" * 64 + "  evidence.txt\n") * 2],
)
def test_malformed_manifest_is_preserved(recorder, engagement, contents):
    manifest = engagement / "manifest.sha256"
    manifest.write_text(contents)
    assert recorder.main([str(engagement), "--min-severity", "critical"]) != 0
    assert manifest.read_text() == contents


def test_dangling_manifest_is_preserved(recorder, engagement, tmp_path):
    manifest = engagement / "manifest.sha256"
    target = tmp_path / "missing"
    manifest.symlink_to(target)
    assert recorder.main([str(engagement)]) != 0
    assert manifest.is_symlink()
    assert not target.exists()


def test_clean_existing_manifest_not_rewritten(recorder, engagement):
    assert recorder.main([str(engagement)]) == 0
    manifest = engagement / "manifest.sha256"
    before = (manifest.read_bytes(), manifest.stat().st_mtime_ns)
    assert recorder.main([str(engagement)]) == 0
    assert (manifest.read_bytes(), manifest.stat().st_mtime_ns) == before


@pytest.mark.parametrize("suffix", ["json", "jsonl"])
def test_external_sibling_prefix_reference_is_reported(recorder, engagement, suffix):
    findings = engagement / "findings"
    findings.mkdir()
    record = {"evidence": {"file": str(engagement) + "-outside/proof.txt"}}
    (findings / f"f.{suffix}").write_text(json.dumps([record] if suffix == "json" else record))
    issues = recorder.scan_findings_for_external_refs(engagement)
    assert any("out-of-tree" in f.title for f in issues)


@pytest.mark.parametrize("data", ["not-json", "[3]", '{"findings": "invalid"}', '[{"evidence": []}]'])
def test_unsupported_findings_block_packaging(recorder, engagement, data):
    findings = engagement / "findings"
    findings.mkdir()
    (findings / "f.json").write_text(data)
    assert recorder.main([str(engagement), "--min-severity", "critical"]) != 0
    assert not (engagement / "manifest.sha256").exists()


@pytest.mark.parametrize("output", ["manifest.sha256", "manifest.sha256.asc", "evidence.txt"])
def test_report_cannot_replace_evidence_or_integrity_artifacts(recorder, engagement, output):
    assert recorder.main([str(engagement)]) == 0
    manifest = engagement / "manifest.sha256"
    before = manifest.read_bytes()
    assert recorder.main([str(engagement), "--output", str(engagement / output)]) != 0
    assert manifest.read_bytes() == before
    assert (engagement / "evidence.txt").read_text() == "original fixture\n"


def test_custom_snapshot_and_operational_report_do_not_include_themselves(recorder, engagement):
    manifest = engagement / "snapshot[1].sha256"
    output = engagement / "report[1].json"
    args = [str(engagement), "--manifest", str(manifest), "--output", str(output), "--format", "json"]
    assert recorder.main(args) == 0
    assert recorder.main(args) == 0
    assert len(recorder.load_existing_manifest(manifest)) == 1


def test_existing_signature_is_not_replaced(recorder, engagement, monkeypatch):
    assert recorder.main([str(engagement)]) == 0
    signature = engagement / "manifest.sha256.asc"
    signature.write_bytes(b"prior fixture")
    monkeypatch.setattr(recorder, "sign_manifest", lambda *args: pytest.fail("must preserve signature"))
    assert recorder.main([str(engagement), "--sign", "--min-severity", "critical"]) != 0
    assert signature.read_bytes() == b"prior fixture"


def test_clean_archive_path_remains_supported(recorder, engagement, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(recorder, "create_tar", lambda *args: (calls.append(args) is None, ""))
    archive = tmp_path / "archive.tar.gz"
    assert recorder.main([str(engagement), "--tar", str(archive)]) == 0
    assert calls == [(engagement, archive)]


@pytest.mark.parametrize("flag", ["--output", "--tar"])
def test_output_hardlink_cannot_replace_evidence(recorder, engagement, tmp_path, flag):
    destination = tmp_path / "alias"
    destination.hardlink_to(engagement / "evidence.txt")
    assert recorder.main([str(engagement), flag, str(destination)]) != 0
    assert (engagement / "evidence.txt").read_text() == "original fixture\n"
    assert not (engagement / "manifest.sha256").exists()


@pytest.mark.parametrize("flags", [[], ["--sign"]])
def test_orphan_signature_does_not_get_a_new_manifest(recorder, engagement, monkeypatch, flags):
    signature = engagement / "manifest.sha256.asc"
    signature.write_bytes(b"prior fixture")
    monkeypatch.setattr(recorder, "sign_manifest", lambda *args: pytest.fail("must preserve signature"))
    assert recorder.main([str(engagement), *flags]) != 0
    assert signature.read_bytes() == b"prior fixture"
    assert not (engagement / "manifest.sha256").exists()
