"""Execute documented collection and identity boundaries using inert fixtures."""

import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/saas-packs/supabase-pack/skills/supabase-debug-bundle/SKILL.md"


def executable(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/bash\n" + text)
    path.chmod(0o700)


@pytest.fixture
def collector(tmp_path):
    blocks = re.findall(r"```bash\n(.*?)\n```", SKILL.read_text(), re.S)
    script = next(block for block in blocks if "BUNDLE_DIR=" in block)
    temp = tmp_path / "scratch space"
    temp.mkdir()
    binary = tmp_path / "node_modules/.bin/supabase"
    executable(
        binary,
        'printf "%s\\n" "$*" >> called.txt\n'
        'if [[ "$1" == --version ]]; then printf "fixture-cli\\n"; exit 0; fi\n'
        'printf "PRIVATE_FIXTURE_VALUE\\n"\n'
        'if [[ "$3" == bloat ]]; then exit 7; fi\n',
    )
    executable(tmp_path / "bin/curl", 'printf \'{"status":{"indicator":"none"}}\\n\'\n')
    (tmp_path / ".env").write_text("DO_NOT_COLLECT=private-config-fixture\n")

    def run():
        result = subprocess.run(
            ["/bin/bash", "--noprofile", "--norc", "-c", "umask 000\n" + script],
            cwd=tmp_path,
            env={"PATH": f"{tmp_path / 'bin'}:/usr/bin:/bin", "TMPDIR": str(temp), "LC_ALL": "C"},
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result, temp

    return run


def test_candidate_is_private_and_retains_failed_observation(collector, tmp_path):
    result, temp = collector()
    assert result.returncode == 0, result.stderr
    directory = next(path for path in temp.iterdir() if path.is_dir())
    archive = next(temp.glob("*.tar.gz"))
    assert stat.S_IMODE(directory.stat().st_mode) == 0o700
    assert stat.S_IMODE(archive.stat().st_mode) == 0o600
    for path in directory.iterdir():
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert "bloat\t7\n" in (directory / "inspect-status.tsv").read_text()
    assert "table-sizes\t0\n" in (directory / "inspect-status.tsv").read_text()
    assert "PRIVATE_FIXTURE_VALUE" in (directory / "bloat.txt").read_text()
    assert "PRIVATE_FIXTURE_VALUE" not in result.stdout + result.stderr
    assert "UNREVIEWED" in (directory / "REVIEW-REQUIRED.txt").read_text()
    assert not (directory / "cli-status.txt").exists()
    with tarfile.open(archive) as bundle:
        names = bundle.getnames()
        assert all(not name.startswith("/") and ".." not in Path(name).parts for name in names)
        assert "./REVIEW-REQUIRED.txt" in names
        assert not any(".env" in name for name in names)
    assert "status" not in (tmp_path / "called.txt").read_text().splitlines()


def test_repeated_collection_does_not_reuse_evidence_directory(collector):
    first, temp = collector()
    assert first.returncode == 0
    before = set(temp.iterdir())
    second, _ = collector()
    assert second.returncode == 0
    assert len(set(temp.iterdir()) - before) == 2
    assert len(list(temp.glob("*.tar.gz"))) == 2


@pytest.mark.parametrize("approval", [None, "0", "1"])
def test_admin_key_requires_explicit_comparison_approval(tmp_path, approval):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the documented client-selection fixture")
    blocks = re.findall(r"```typescript\n(.*?)\n```", SKILL.read_text(), re.S)
    initialization = blocks[0].split("const diagnostics:")[0]
    initialization = re.sub(r"^import .*\n", "", initialization, flags=re.M)
    comparison = next(block for block in blocks if "// 2c" in block).split("// 2c", 1)[1]
    comparison = comparison.split("\n", 1)[1]
    script = (
        "const calls = []; globalThis.fetch = () => { throw Error('Network forbidden'); };\n"
        "function createClient(url, key) { calls.push(key); return {from: () => ({select: async () => "
        "({error: null, count: 0})})}; }\n"
        + initialization
        + "\nconst diagnostics = {}; const probeTable = 'fixture';\n"
        + comparison
        + "\nconsole.log(JSON.stringify({calls, result: diagnostics.rls_comparison}));\n"
    )
    env = {
        "PATH": os.defpath,
        "SUPABASE_URL": "https://fixture.invalid",
        "SUPABASE_ANON_KEY": "fixture-anon",
        "SUPABASE_SERVICE_ROLE_KEY": "fixture-admin",
    }
    if approval is not None:
        env["SUPABASE_DIAGNOSTIC_ADMIN_APPROVED"] = approval
    fixture = tmp_path / "identity-probe.mts"
    fixture.write_text(script)
    result = subprocess.run(
        [node, "--experimental-strip-types", str(fixture)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["calls"][0] == "fixture-anon"
    if approval == "1":
        assert report["calls"].count("fixture-admin") == 1
        assert report["result"]["status"] == "inconclusive"
    else:
        assert "fixture-admin" not in report["calls"]
        assert report["result"]["status"] == "not_run"
