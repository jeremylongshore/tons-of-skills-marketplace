"""Exercise shipped helper fixtures through their actual CLIs, without account access."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "plugins/saas-packs/coreweave-pack/skills"
HELPERS = {
    "core-workflow-a": "review-inference.py",
    "core-workflow-b": "review-training.py",
    "enterprise-rbac": "review-access.py",
    "ci-integration": "review-workflow.py",
    "incident-runbook": "review-incident.py",
    "workload-health": "check-health.py",
    "cks-provisioning": "review-plan.py",
    "caios-stage-model": "review-transfer.py",
}
CASES = [
    (slug, filename, case)
    for slug, filename in HELPERS.items()
    for case in json.loads((SKILLS / ("coreweave-" + slug) / "tests/fixtures/cases.json").read_text())
]


@pytest.mark.parametrize("slug,filename,case", CASES, ids=[s + "-" + c["id"] for s, _, c in CASES])
def test_shipped_evidence_contract(slug, filename, case, tmp_path):
    data = tmp_path / "input.json"
    data.write_text(json.dumps(case["input"]))
    # sitecustomize intercepts network and subprocess operations before helper imports.
    (tmp_path / "sitecustomize.py").write_text(
        'import sys\ndef guard(event,args):\n if event in ("socket.connect","socket.getaddrinfo","subprocess.Popen","os.system"):\n  raise RuntimeError("offline operation attempted")\nsys.addaudithook(guard)\n'
    )
    env = {"PATH": os.defpath, "PYTHONPATH": str(tmp_path), "PYTHONDONTWRITEBYTECODE": "1"}
    script = SKILLS / ("coreweave-" + slug) / "scripts" / filename
    proc = subprocess.run(
        [sys.executable, str(script), "--input", str(data), "--as-of", "2026-11-05T12:01:00Z"],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    result = json.loads(proc.stdout)
    assert result["status"] == case["expected_status"], result
    assert set(case["expected_codes"]) <= {f["code"] for f in result["findings"]}
    assert proc.returncode == {"reviewed": 0, "blocked": 2, "incomplete": 3}[result["status"]]
    assert "SECRET_CANARY" not in proc.stdout + proc.stderr
    assert not proc.stderr


@pytest.mark.parametrize("slug,filename", HELPERS.items())
def test_malformed_evidence_is_not_a_success(slug, filename, tmp_path):
    data = tmp_path / "bad.json"
    data.write_text('{"schema":"secret-canary","schema":null}')
    p = subprocess.run(
        [sys.executable, str(SKILLS / ("coreweave-" + slug) / "scripts" / filename), "--input", str(data)],
        capture_output=True,
        text=True,
    )
    assert p.returncode == 2 and "secret-canary" not in p.stdout + p.stderr


@pytest.mark.parametrize("workflow_index", [0, 1])
def test_documented_ci_workflows_match_review_contract(workflow_index, tmp_path):
    import re
    import yaml

    skill = SKILLS / "coreweave-ci-integration"
    source = (skill / "SKILL.md").read_text()
    workflow = yaml.load(re.findall(r"```yaml\n(.*?)```", source, re.S)[workflow_index], Loader=yaml.BaseLoader)
    evidence = json.loads((skill / "tests/fixtures/example.json").read_text())
    evidence["workflow"] = workflow
    evidence["protected_environments"] = ["coreweave-staging"]
    data = tmp_path / "documented-workflow.json"
    data.write_text(json.dumps(evidence))
    result = subprocess.run(
        [
            sys.executable,
            str(skill / "scripts/review-workflow.py"),
            "--input",
            str(data),
            "--as-of",
            "2026-11-05T12:01:00Z",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["status"] == "reviewed"


@pytest.mark.parametrize(
    "endpoint", ["https://cwobject.com:8443", "https://user@cwobject.com", "https://cwobject.com/models"]
)
def test_staging_endpoint_is_exact_public_tls_endpoint(endpoint, tmp_path):
    skill = SKILLS / "coreweave-caios-stage-model"
    evidence = json.loads((skill / "tests/fixtures/example.json").read_text())
    evidence["endpoint"] = endpoint
    data = tmp_path / "endpoint.json"
    data.write_text(json.dumps(evidence))
    result = subprocess.run(
        [
            sys.executable,
            str(skill / "scripts/review-transfer.py"),
            "--input",
            str(data),
            "--as-of",
            "2026-11-05T12:01:00Z",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "storage-endpoint" in {finding["code"] for finding in json.loads(result.stdout)["findings"]}


def test_inference_rejects_nonhex_artifact_digest(tmp_path):
    skill = SKILLS / "coreweave-core-workflow-a"
    evidence = json.loads((skill / "tests/fixtures/example.json").read_text())
    evidence["model_provenance"]["sha256"] = "z" * 64
    data = tmp_path / "digest.json"
    data.write_text(json.dumps(evidence))
    result = subprocess.run(
        [
            sys.executable,
            str(skill / "scripts/review-inference.py"),
            "--input",
            str(data),
            "--as-of",
            "2026-11-05T12:01:00Z",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "model-provenance" in {finding["code"] for finding in json.loads(result.stdout)["findings"]}


@pytest.mark.parametrize(
    "crds",
    [
        "inferenceservices.serving.kserve.io",
        "prefix-inferenceservices.serving.kserve.io-suffix",
        ["inferenceservices.serving.kserve.io.attacker.invalid"],
        {"inferenceservices.serving.kserve.io": True},
        None,
    ],
)
def test_inference_requires_exact_crd_name_in_list(crds, tmp_path):
    skill = SKILLS / "coreweave-core-workflow-a"
    evidence = json.loads((skill / "tests/fixtures/example.json").read_text())
    evidence["crds"] = crds
    data = tmp_path / "crds.json"
    data.write_text(json.dumps(evidence))
    result = subprocess.run(
        [
            sys.executable,
            str(skill / "scripts/review-inference.py"),
            "--input",
            str(data),
            "--as-of",
            "2026-11-05T12:01:00Z",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "kserve-crd" in {finding["code"] for finding in json.loads(result.stdout)["findings"]}
