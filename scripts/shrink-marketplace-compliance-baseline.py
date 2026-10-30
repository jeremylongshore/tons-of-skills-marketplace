#!/usr/bin/env python3
"""Prepare a selective, evidence-bound baseline shrink; never modify the checkout."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "scripts/.marketplace-compliance-baseline.json"
WORKFLOW = ".github/workflows/validate-plugins.yml"


def load_ratchet():
    spec = importlib.util.spec_from_file_location("ratchet", ROOT / "scripts/check-marketplace-compliance-baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RATCHET = load_ratchet()


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "--no-replace-objects", *args],
        cwd=root,
        text=True,
        env={**os.environ, "GIT_NO_REPLACE_OBJECTS": "1"},
        stderr=subprocess.PIPE,
    ).strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def clean_source(root: Path, source_sha: str) -> None:
    require(bool(re.fullmatch(r"[0-9a-f]{40}", source_sha)), "source must be an exact commit SHA")
    require(git(root, "cat-file", "-t", source_sha) == "commit", "source must be a commit")
    require(git(root, "rev-parse", "HEAD") == source_sha, "checkout does not match source")
    require(git(root, "rev-parse", "refs/remotes/origin/main") == source_sha, "default branch moved")
    require(not git(root, "status", "--porcelain=v1", "--untracked-files=no"), "tracked checkout must be clean")
    require(git(root, "ls-tree", source_sha, "--", BASELINE).startswith("100644 blob "), "baseline must be regular")


def required_job_names(workflow: dict) -> set[str]:
    """Expand the trusted workflow's required jobs, refusing unsupported matrices."""
    jobs = workflow["jobs"]
    needed = jobs["ci-required"]["needs"]
    require(isinstance(needed, list) and "marketplace-compliance-ratchet" in needed, "missing required ratchet")
    names = set()
    for key in [*needed, "ci-required"]:
        job = jobs[key]
        name = job.get("name", key)
        require(isinstance(name, str) and "${{" not in name, "dynamic job names are unsupported")
        matrix = job.get("strategy", {}).get("matrix")
        if matrix is None:
            expanded = [name]
        else:
            require(isinstance(matrix, dict) and bool(matrix), "invalid required matrix")
            require(not ({"include", "exclude"} & matrix.keys()), "matrix include/exclude needs explicit support")
            require(
                all(isinstance(v, list) and v and all(isinstance(x, str) for x in v) for v in matrix.values()),
                "required matrices must contain static string lists",
            )
            expanded = [f"{name} ({', '.join(values)})" for values in itertools.product(*matrix.values())]
        require(not names.intersection(expanded) and len(expanded) == len(set(expanded)), "duplicate required job name")
        names.update(expanded)
    return names


def validate_run(run: dict, job_pages: list, *, run_id: int, source_sha: str, repository: str, workflow: dict) -> None:
    require(type(run_id) is int and run_id > 0, "invalid validation run ID")
    require(bool(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)), "invalid repository")
    expected = {
        "id": run_id,
        "name": "Validate Plugins",
        "path": WORKFLOW,
        "event": "push",
        "head_branch": "main",
        "head_sha": source_sha,
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
    }
    require(
        all(type(run.get(k)) is type(v) and run[k] == v for k, v in expected.items()),
        "validation run is not a successful first-attempt main push at source",
    )
    for key in ("repository", "head_repository"):
        require(run.get(key, {}).get("full_name") == repository, "validation repository mismatch")
    require(isinstance(job_pages, list) and bool(job_pages), "missing validation job pages")
    jobs = []
    for page in job_pages:
        require(isinstance(page, dict) and isinstance(page.get("jobs"), list), "malformed validation job page")
        jobs.extend(page["jobs"])
    require(
        all(type(p.get("total_count")) is int and p["total_count"] == len(jobs) for p in job_pages),
        "incomplete validation jobs",
    )
    names = [job.get("name") for job in jobs]
    require(
        all(isinstance(n, str) for n in names) and len(names) == len(set(names)), "duplicate or invalid validation jobs"
    )
    require(required_job_names(workflow).issubset(names), "missing required validation jobs")
    # Pushes use the full lane. A green run with a skipped/failed job is not proof.
    require(
        all(
            job.get("status") == "completed"
            and job.get("conclusion") == "success"
            and type(job.get("run_id")) is int
            and job["run_id"] == run_id
            and job.get("head_sha") == source_sha
            and type(job.get("run_attempt")) is int
            and job["run_attempt"] == 1
            for job in jobs
        ),
        "validation jobs must all succeed at the first exact-source attempt",
    )


def checked_entries(payload: dict) -> list[str]:
    values = payload.get("entries")
    require(isinstance(values, list) and all(isinstance(v, str) for v in values), "invalid baseline entries")
    require(len(values) == len(set(values)), "duplicate baseline entries")
    require(all(len(v.split(" :: ")) == 3 and all(v.split(" :: ")) for v in values), "malformed finding triple")
    return values


def selective_candidate(baseline: dict, current: dict, rule_id: str, expected_count: int) -> tuple[dict, list[str]]:
    require(bool(re.fullmatch(r"E-[A-Za-z0-9-]+", rule_id)), "invalid rule ID")
    require(type(expected_count) is int and expected_count > 0, "expected count must be a positive integer")
    require(
        rule_id in baseline.get("rule_inventory", []) and rule_id in current.get("rule_inventory", []),
        "rule is not in the exact inventory",
    )
    old = checked_entries(baseline)
    live = checked_entries(current)
    removed = [entry for entry in old if entry.split(" :: ")[1] == rule_id]
    require(len(removed) == expected_count, "selected baseline count does not match expectation")
    require(not any(entry.split(" :: ")[1] == rule_id for entry in live), "selected rule still has live findings")
    errors = baseline.get("totals", {}).get("errors")
    require(type(errors) is int and errors >= expected_count, "invalid baseline error total")
    candidate = copy.deepcopy(baseline)
    candidate["entries"] = [entry for entry in old if entry not in set(removed)]
    candidate["totals"]["errors"] -= expected_count
    failures = [
        *RATCHET.metadata_drift(candidate, current),
        *RATCHET.compare(candidate, current),
        *RATCHET.metric_drift(candidate, current),
    ]
    require(not failures, "live R1/R2/R4 refusal: " + "; ".join(failures))
    require(not RATCHET.capture_required_reasons(baseline, candidate), "candidate broadens the baseline envelope")
    return candidate, removed


def prepare(
    root: Path,
    *,
    source_sha: str,
    repository: str,
    run_id: int,
    run: dict,
    job_pages: list,
    rule_id: str,
    expected_count: int,
) -> tuple[dict, dict]:
    clean_source(root, source_sha)
    workflow = yaml.safe_load((root / WORKFLOW).read_text())
    validate_run(run, job_pages, run_id=run_id, source_sha=source_sha, repository=repository, workflow=workflow)
    baseline_bytes = (root / BASELINE).read_bytes()
    baseline = json.loads(baseline_bytes)
    current = RATCHET.emit_current(root, finding_identity_version=baseline.get("finding_identity_version", 1))
    require(current.get("generated_from", {}).get("sha") == source_sha, "live emitter source mismatch")
    candidate, removed = selective_candidate(baseline, current, rule_id, expected_count)
    corpus = RATCHET.corpus_shrink_evidence(candidate, current, root, source_sha)
    require(corpus["allowed"], "live R3 corpus shrink refused")
    clean_source(root, source_sha)
    require((root / BASELINE).read_bytes() == baseline_bytes, "baseline changed during validation")
    return candidate, {
        "source_sha": source_sha,
        "validation_run_id": run_id,
        "validation_run_url": f"https://github.com/{repository}/actions/runs/{run_id}",
        "rule_id": rule_id,
        "removed_count": len(removed),
        "removed_entries": removed,
        "baseline_sha256": hashlib.sha256(baseline_bytes).hexdigest(),
        "baseline_entries_before": len(baseline["entries"]),
        "baseline_entries_after": len(candidate["entries"]),
        "errors_before": baseline["totals"]["errors"],
        "errors_after": candidate["totals"]["errors"],
        "live_errors": current["totals"]["errors"],
        "corpus": corpus,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--validation-run-id", type=int, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--jobs", type=Path, required=True)
    parser.add_argument("--rule-id", required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = args.repo_root.resolve()
        output = args.output_dir.resolve()
        require(not output.is_relative_to(root), "output must be outside the checkout")
        require(not output.exists(), "output directory already exists")
        candidate, receipt = prepare(
            root,
            source_sha=args.source_sha,
            repository=args.repository,
            run_id=args.validation_run_id,
            run=json.loads(args.run.read_text()),
            job_pages=json.loads(args.jobs.read_text()),
            rule_id=args.rule_id,
            expected_count=args.expected_count,
        )
        data = (json.dumps(candidate, indent=2, ensure_ascii=False) + "\n").encode()
        receipt["candidate_sha256"] = hashlib.sha256(data).hexdigest()
        output.mkdir()
        (output / "baseline.json").write_bytes(data)
        (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt))
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        print(f"selective-baseline-shrink: REFUSED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
