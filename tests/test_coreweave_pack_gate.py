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


def make_archive(tmp_path, name="package/README.md", payload=b"original", kind=None):
    import io
    import tarfile

    source = tmp_path / "source"
    source.mkdir()
    for filename in ("README.md", "package.json", "QUALITY.md", "offline-results.json"):
        (source / filename).write_bytes(b"original")
    archive = tmp_path / "test.tgz"
    with tarfile.open(archive, "w:gz") as bundle:
        for filename in ("README.md", "package.json", "QUALITY.md", "offline-results.json"):
            member = tarfile.TarInfo(name if filename == "README.md" else "package/" + filename)
            member.size = len(payload)
            if kind is not None and filename == "README.md":
                member.type = kind
                member.linkname = "../../outside"
                member.size = 0
            bundle.addfile(member, io.BytesIO(payload))
    return archive, source


def test_archive_replays_identical_distribution(tmp_path):
    archive, source = make_archive(tmp_path)
    installed = tmp_path / "installed"
    assert gate.unpack_package(archive, installed, source) == 4
    assert (installed / "README.md").read_bytes() == b"original"


def test_archive_rejects_traversal(tmp_path):
    import pytest

    archive, source = make_archive(tmp_path, name="package/../../outside")
    with pytest.raises(ValueError, match="Unsafe package path"):
        gate.unpack_package(archive, tmp_path / "installed", source)
    assert not (tmp_path.parent / "outside").exists()


def test_archive_rejects_links(tmp_path):
    import tarfile
    import pytest

    for index, kind in enumerate((tarfile.SYMTYPE, tarfile.LNKTYPE)):
        case = tmp_path / str(index)
        case.mkdir()
        archive, source = make_archive(case, kind=kind)
        with pytest.raises(ValueError, match="links and special files"):
            gate.unpack_package(archive, case / "installed", source)


def test_archive_rejects_changed_bytes(tmp_path):
    import pytest

    archive, source = make_archive(tmp_path, payload=b"modified")
    with pytest.raises(ValueError, match="bytes differ"):
        gate.unpack_package(archive, tmp_path / "installed", source)


def test_archive_rejects_missing_skill(tmp_path):
    import pytest

    archive, source = make_archive(tmp_path)
    skill = source / "skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Required skill")
    with pytest.raises(ValueError, match="omits required files"):
        gate.unpack_package(archive, tmp_path / "installed", source)
