#!/usr/bin/env python3
"""Fail closed when marketplace compliance debt exceeds the pinned policy envelope.

Blueprint 727 E6: compare the validator's triple-keyed marketplace findings,
monotone metrics and catalog-reconciled corpus with the pinned baseline.
Existing debt is tolerated; new debt and unexplained corpus shrink fail.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = ROOT / "scripts" / ".marketplace-compliance-baseline.json"
VALIDATOR = ROOT / "scripts" / "validate-skills-schema.py"
BASELINE_PATH = "scripts/.marketplace-compliance-baseline.json"
CAPTURE_BRANCH_PREFIX = "automation/compliance-baseline-"
CAPTURE_WORKFLOW_PATH = ".github/workflows/capture-marketplace-compliance-baseline.yml"
CAPTURE_JOB_NAME = "capture-baseline-artifact"
MONOTONE_TOTAL_FIELDS = {"errors", "grade_A_plus_B_pct"}


def entries(payload: dict[str, Any]) -> set[str]:
    values = payload.get("entries")
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError("baseline entries must be a list of triple-key strings")
    return set(values)


def compare(baseline: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """Return sorted live triples absent from the pinned baseline."""
    return sorted(entries(current) - entries(baseline))


def metadata_drift(baseline: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """Return baseline-contract changes that require a conscious re-baseline.

    Triple comparison alone cannot distinguish an intentional validator-rule
    change from legacy debt.  The emitted schema version and rule inventory are
    therefore part of the pinned contract: either changing them must fail the
    ratchet until the dedicated baseline-capture transaction has been reviewed.
    """
    errors: list[str] = []
    identity_versions = {}
    for label, payload in (("baseline", baseline), ("live", current)):
        version = payload.get("finding_identity_version", 1)
        if type(version) is not int or version not in (1, 2):
            errors.append(f"{label} has unsupported finding_identity_version")
            continue
        identity_versions[label] = version
        if version == 2 and any(
            len(parts := entry.split(" :: ", 2)) == 3
            and parts[1] == "E-MISSING-REQUIRED-SECTION"
            and parts[2].strip() in ("", "##")
            for entry in entries(payload)
        ):
            errors.append(f"{label} finding_identity_version=2 contains an unnamed required-section entry")
    if len(identity_versions) == 2 and identity_versions["baseline"] != identity_versions["live"]:
        errors.append(
            "finding_identity_version drift: "
            f"baseline={identity_versions['baseline']}, live={identity_versions['live']}"
        )
    baseline_schema = baseline.get("schema_version")
    current_schema = current.get("schema_version")
    if not isinstance(baseline_schema, str) or not isinstance(current_schema, str):
        errors.append("baseline and live payload must declare string schema_version values")
    elif baseline_schema != current_schema:
        errors.append(f"schema_version drift: baseline={baseline_schema}, live={current_schema}")

    baseline_rules = baseline.get("rule_inventory")
    current_rules = current.get("rule_inventory")
    if not isinstance(baseline_rules, list) or not all(isinstance(rule, str) for rule in baseline_rules):
        errors.append("baseline rule_inventory must be a list of rule ids")
    elif not isinstance(current_rules, list) or not all(isinstance(rule, str) for rule in current_rules):
        errors.append("live rule_inventory must be a list of rule ids")
    elif set(baseline_rules) != set(current_rules):
        added = sorted(set(current_rules) - set(baseline_rules))
        removed = sorted(set(baseline_rules) - set(current_rules))
        if added:
            errors.append(f"unknown live rule id(s): {', '.join(added)}")
        if removed:
            errors.append(f"baseline rule id(s) absent from live inventory: {', '.join(removed)}")
    return errors


def metric_drift(baseline: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """Return violations of the E6.7 monotone marketplace metrics.

    R2 prevents a fix from increasing the total number of validator errors.
    R4 prevents corpus dilution by requiring the A-plus-B share to hold or
    improve.  These checks deliberately compare the emitted totals rather than
    recomputing them here, keeping the canonical validator the sole owner of
    metric classification.
    """

    errors: list[str] = []
    baseline_totals = baseline.get("totals")
    current_totals = current.get("totals")
    if not isinstance(baseline_totals, dict) or not isinstance(current_totals, dict):
        return ["baseline and live payload must declare object totals"]

    for key in ("errors", "grade_A_plus_B_pct"):
        baseline_value = baseline_totals.get(key)
        current_value = current_totals.get(key)
        if isinstance(baseline_value, bool) or not isinstance(baseline_value, (int, float)):
            errors.append(f"baseline totals.{key} must be a finite number")
            continue
        if isinstance(current_value, bool) or not isinstance(current_value, (int, float)):
            errors.append(f"live totals.{key} must be a finite number")
            continue
        if not math.isfinite(baseline_value):
            errors.append(f"baseline totals.{key} must be a finite number")
            continue
        if not math.isfinite(current_value):
            errors.append(f"live totals.{key} must be a finite number")
            continue
        if baseline_value < 0 or current_value < 0:
            errors.append(f"totals.{key} must be non-negative")
            continue
        if key == "errors" and current_value > baseline_value:
            errors.append(f"totals.errors increased: baseline={baseline_value:g}, live={current_value:g}")
        elif key == "grade_A_plus_B_pct" and current_value < baseline_value:
            errors.append(f"totals.grade_A_plus_B_pct fell: baseline={baseline_value:g}, live={current_value:g}")
    return errors


def capture_required_reasons(base: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """Return baseline mutations that may relax or redefine the policy envelope.

    A strict removal from ``entries`` and monotone improvement of the two ratchet
    metrics do not broaden the baseline. Every other mutation changes either the
    accepted-debt set, its measurement contract, or a denominator/provenance
    field and therefore needs the exact owner-capture receipt.
    """

    reasons: list[str] = []
    added_entries = sorted(entries(current) - entries(base))
    if added_entries:
        reasons.append(f"entries added: {len(added_entries)}")

    base_totals = base.get("totals")
    current_totals = current.get("totals")
    if not isinstance(base_totals, dict) or not isinstance(current_totals, dict):
        if base_totals != current_totals:
            reasons.append("totals contract changed")
    else:
        for field, direction in (("errors", "increase"), ("grade_A_plus_B_pct", "decrease")):
            base_value = base_totals.get(field)
            current_value = current_totals.get(field)
            values_are_finite_numbers = all(
                not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
                for value in (base_value, current_value)
            )
            if not values_are_finite_numbers:
                if base_value != current_value:
                    reasons.append(f"totals.{field} contract changed")
            elif (direction == "increase" and current_value > base_value) or (
                direction == "decrease" and current_value < base_value
            ):
                reasons.append(f"totals.{field} became more permissive")

        base_other_totals = {key: value for key, value in base_totals.items() if key not in MONOTONE_TOTAL_FIELDS}
        current_other_totals = {key: value for key, value in current_totals.items() if key not in MONOTONE_TOTAL_FIELDS}
        if base_other_totals != current_other_totals:
            reasons.append("totals denominator contract changed")

    protected_fields = ("$comment", "schema_version", "rule_inventory", "corpus_definition", "corpus", "generated_from")
    for field in protected_fields:
        if base.get(field) != current.get(field):
            reasons.append(f"{field} contract changed")

    known_fields = {"entries", "totals", *protected_fields}
    base_extensions = {key: value for key, value in base.items() if key not in known_fields}
    current_extensions = {key: value for key, value in current.items() if key not in known_fields}
    if base_extensions != current_extensions:
        reasons.append("unknown policy-envelope fields changed")
    return reasons


def baseline_growth_error(
    base: dict[str, Any],
    current: dict[str, Any],
    changed_paths: set[str],
    head_ref: str,
    *,
    capture_authorized: bool = False,
) -> str | None:
    """Return an E6.6 violation for an unauthorized permissive envelope edit."""
    reasons = capture_required_reasons(base, current)
    if not reasons:
        return None
    if changed_paths != {BASELINE_PATH}:
        return "a permissive baseline policy-envelope change may only occur in a one-file baseline-only pull request"
    if capture_run_id(head_ref) is None:
        return (
            "a permissive baseline policy-envelope change may only occur on the dedicated CI capture branch "
            f"({CAPTURE_BRANCH_PREFIX}<run-id>): {', '.join(reasons)}"
        )
    if not capture_authorized:
        return "a permissive baseline policy-envelope change requires an owner-dispatched capture artifact verified by required CI"
    return None


def capture_run_id(head_ref: str) -> int | None:
    """Return the exact Actions run id encoded by a capture branch."""
    match = re.fullmatch(rf"{re.escape(CAPTURE_BRANCH_PREFIX)}([1-9][0-9]*)", head_ref)
    return int(match.group(1)) if match else None


def capture_provenance_errors(
    *,
    current: dict[str, Any],
    head_ref: str,
    repository: str,
    repository_owner: str,
    base_ref: str,
    pr_number: int,
    head_sha: str,
    head_parents: list[str],
    run: dict[str, Any],
    jobs: dict[str, Any],
    pull_requests: list[dict[str, Any]],
    artifact_bytes: bytes,
    baseline_bytes: bytes,
) -> list[str]:
    """Validate the owner/bot receipt for an E6.6 policy-envelope exception."""
    errors: list[str] = []
    run_id = capture_run_id(head_ref)
    if run_id is None:
        return [f"head branch must exactly match {CAPTURE_BRANCH_PREFIX}<run-id>"]

    if run.get("id") != run_id:
        errors.append("capture run id does not match the head branch")
    if run.get("event") != "workflow_dispatch":
        errors.append("capture run was not owner-dispatched")
    if run.get("path") != CAPTURE_WORKFLOW_PATH:
        errors.append("capture run used an unexpected workflow")
    if run.get("head_branch") != base_ref:
        errors.append("capture run did not execute from the protected base branch")
    if run.get("run_attempt") != 1:
        errors.append("capture run must be the first immutable attempt")

    head_repository = run.get("head_repository")
    if not isinstance(head_repository, dict) or head_repository.get("full_name") != repository:
        errors.append("capture run repository does not match this repository")
    for field in ("actor", "triggering_actor"):
        identity = run.get(field)
        if not isinstance(identity, dict) or identity.get("login") != repository_owner:
            errors.append(f"capture run {field} is not the repository owner")

    capture_jobs = jobs.get("jobs")
    if not isinstance(capture_jobs, list):
        errors.append("capture run jobs payload is malformed")
    elif not any(
        isinstance(job, dict)
        and job.get("name") == CAPTURE_JOB_NAME
        and job.get("status") == "completed"
        and job.get("conclusion") == "success"
        for job in capture_jobs
    ):
        errors.append(f"capture run has no successful {CAPTURE_JOB_NAME} job")

    if len(pull_requests) != 1:
        errors.append("capture branch must belong to exactly one pull request and cannot be replayed")
    else:
        pull_request = pull_requests[0]
        head = pull_request.get("head")
        base = pull_request.get("base")
        head_repository = head.get("repo") if isinstance(head, dict) else None
        if pull_request.get("number") != pr_number or pull_request.get("state") != "open":
            errors.append("capture receipt does not belong to the current open pull request")
        if not isinstance(head, dict) or head.get("ref") != head_ref or head.get("sha") != head_sha:
            errors.append("capture pull request head does not match the checked commit")
        if not isinstance(head_repository, dict) or head_repository.get("full_name") != repository:
            errors.append("capture pull request head is not in this repository")
        if not isinstance(base, dict) or base.get("ref") != base_ref:
            errors.append("capture pull request does not target the protected base branch")

    source_sha = run.get("head_sha")
    generated_from = current.get("generated_from")
    if not isinstance(source_sha, str) or not isinstance(generated_from, dict):
        errors.append("capture run or baseline source provenance is malformed")
    elif generated_from.get("sha") != source_sha:
        errors.append("baseline generated_from.sha does not match the capture source")

    if not head_sha or len(head_parents) != 1 or head_parents[0] != source_sha:
        errors.append("pull request head must be one capture commit directly atop the capture source")
    if artifact_bytes != baseline_bytes:
        errors.append("pull request baseline is not byte-identical to the immutable capture artifact")
    return errors


def baseline_at_ref(repo_root: Path, ref: str) -> dict[str, Any]:
    result = subprocess.run(
        ["git", "show", f"{ref}:{BASELINE_PATH}"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"could not read baseline at {ref}")
    return json.loads(result.stdout)


def changed_paths_since(repo_root: Path, base_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"could not diff against {base_ref}")
    return {path for path in result.stdout.splitlines() if path}


def commit_parents(repo_root: Path, sha: str) -> list[str]:
    result = subprocess.run(
        ["git", "rev-list", "--parents", "-n", "1", sha],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"could not inspect pull request head {sha}")
    parts = result.stdout.strip().split()
    if not parts or parts[0] != sha:
        raise RuntimeError(f"could not read exact pull request head {sha}")
    return parts[1:]


def emit_current(repo_root: Path, *, finding_identity_version: int = 1) -> dict[str, Any]:
    # Select the pinned contract, never infer it from live findings. Envelope
    # changes still pass the separate owner-capture provenance gate.
    if type(finding_identity_version) is not int or finding_identity_version not in (1, 2):
        raise ValueError("baseline has unsupported finding_identity_version")
    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--emit-baseline",
            "--baseline-identity-version",
            str(finding_identity_version),
            "--repo-root",
            str(repo_root),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "marketplace baseline emitter failed")
    return json.loads(result.stdout)


def corpus_shrink_evidence(
    baseline: dict[str, Any], current: dict[str, Any], repo_root: Path, checkout_sha: str = ""
) -> dict[str, Any]:
    """Bind R3 counts and catalog withdrawals to the canonical Git-tree census."""
    baseline_corpus = baseline.get("corpus")
    current_corpus = current.get("corpus")
    provenance = baseline.get("generated_from")
    if not all(isinstance(value, dict) for value in (baseline_corpus, current_corpus, provenance)):
        raise ValueError("R3 requires baseline/live corpus objects and baseline generated_from provenance")
    corpus_source_sha = provenance.get("sha")
    if "corpus_source_sha" in baseline:
        migration = baseline.get("identity_migration")
        original = migration.get("prior_generated_from") if isinstance(migration, dict) else None
        corpus_source_sha = baseline["corpus_source_sha"]
        if (
            type(baseline.get("finding_identity_version")) is not int
            or baseline["finding_identity_version"] != 2
            or not isinstance(migration, dict)
            or migration.get("kind") != "historical-required-sections-v1-to-v2"
            or not isinstance(original, dict)
            or not isinstance(corpus_source_sha, str)
            or not re.fullmatch(r"[0-9a-f]{40}", corpus_source_sha)
            or original.get("sha") != corpus_source_sha
        ):
            raise ValueError("R3 historical corpus source must match the version-2 section migration provenance")
    payload = {
        "baseline_count": baseline_corpus.get("skill_files"),
        "current_count": current_corpus.get("skill_files"),
        "baseline_sha": corpus_source_sha,
    }
    if checkout_sha:
        payload["checkout_sha"] = checkout_sha
    result = subprocess.run(
        ["node", str(ROOT / "scripts" / "check-corpus-shrink.mjs"), "--repo-root", str(repo_root)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "R3 Git-tree census failed")
    evidence = json.loads(result.stdout)
    if not isinstance(evidence, dict) or not isinstance(evidence.get("allowed"), bool):
        raise ValueError("R3 checker returned malformed evidence")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--current", type=Path, help="test-only emitted baseline JSON")
    parser.add_argument("--checkout-sha", default="", help="expected immutable checkout commit for the R3 census")
    parser.add_argument("--base", help="git base ref for the E6.6 PR policy-envelope check")
    parser.add_argument("--head-ref", default="", help="PR head branch for the E6.6 growth check")
    parser.add_argument("--head-sha", default="", help="exact PR head commit for capture provenance")
    parser.add_argument("--repository", default="", help="owner/name repository identity")
    parser.add_argument("--repository-owner", default="", help="owner allowed to dispatch a capture")
    parser.add_argument("--base-ref", default="", help="protected branch used as the capture source")
    parser.add_argument("--pr-number", type=int, help="current pull request number")
    parser.add_argument("--capture-run-metadata", type=Path, help="GitHub Actions run JSON")
    parser.add_argument("--capture-run-jobs", type=Path, help="GitHub Actions jobs JSON")
    parser.add_argument("--capture-pull-requests", type=Path, help="pull requests for the capture branch")
    parser.add_argument("--capture-artifact", type=Path, help="downloaded immutable baseline artifact")
    parser.add_argument(
        "--check-growth-only",
        action="store_true",
        help="check a PR diff for an unauthorized permissive baseline mutation without emitting the corpus",
    )
    args = parser.parse_args()

    try:
        repo_root = args.repo_root.resolve()
        if args.check_growth_only:
            if not args.base:
                raise ValueError("--check-growth-only requires --base")
            baseline = baseline_at_ref(repo_root, args.base)
            current = json.loads(args.baseline.read_text(encoding="utf-8"))
            requires_capture = bool(capture_required_reasons(baseline, current))
            capture_authorized = False
            provenance_errors: list[str] = []
            if requires_capture and capture_run_id(args.head_ref) is not None:
                required = {
                    "--head-sha": args.head_sha,
                    "--repository": args.repository,
                    "--repository-owner": args.repository_owner,
                    "--base-ref": args.base_ref,
                    "--pr-number": args.pr_number,
                    "--capture-run-metadata": args.capture_run_metadata,
                    "--capture-run-jobs": args.capture_run_jobs,
                    "--capture-pull-requests": args.capture_pull_requests,
                    "--capture-artifact": args.capture_artifact,
                }
                missing = [name for name, value in required.items() if not value]
                if missing:
                    provenance_errors.append(f"missing capture provenance argument(s): {', '.join(missing)}")
                else:
                    assert args.capture_run_metadata is not None
                    assert args.capture_run_jobs is not None
                    assert args.capture_pull_requests is not None
                    assert args.capture_artifact is not None
                    run = json.loads(args.capture_run_metadata.read_text(encoding="utf-8"))
                    jobs = json.loads(args.capture_run_jobs.read_text(encoding="utf-8"))
                    pull_requests = json.loads(args.capture_pull_requests.read_text(encoding="utf-8"))
                    if not isinstance(pull_requests, list):
                        raise ValueError("capture pull requests payload must be a list")
                    provenance_errors.extend(
                        capture_provenance_errors(
                            current=current,
                            head_ref=args.head_ref,
                            repository=args.repository,
                            repository_owner=args.repository_owner,
                            base_ref=args.base_ref,
                            pr_number=args.pr_number,
                            head_sha=args.head_sha,
                            head_parents=commit_parents(repo_root, args.head_sha),
                            run=run,
                            jobs=jobs,
                            pull_requests=pull_requests,
                            artifact_bytes=args.capture_artifact.read_bytes(),
                            baseline_bytes=args.baseline.read_bytes(),
                        )
                    )
                    capture_authorized = not provenance_errors
            violation = baseline_growth_error(
                baseline,
                current,
                changed_paths_since(repo_root, args.base),
                args.head_ref,
                capture_authorized=capture_authorized,
            )
            if violation:
                print(f"marketplace-compliance-ratchet: FAIL — {violation}", file=sys.stderr)
                for error in provenance_errors:
                    print(f"  {error}", file=sys.stderr)
                return 1
            print("marketplace-compliance-ratchet: OK (no unauthorized permissive baseline mutation)")
            return 0
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        current = (
            json.loads(args.current.read_text(encoding="utf-8"))
            if args.current
            else emit_current(repo_root, finding_identity_version=baseline.get("finding_identity_version", 1))
        )
        drift = metadata_drift(baseline, current)
        newcomers = compare(baseline, current)
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as error:
        print(f"marketplace-compliance-ratchet: ERROR: {error}", file=sys.stderr)
        return 2

    if drift:
        print("marketplace-compliance-ratchet: FAIL — baseline contract drift:", file=sys.stderr)
        for error in drift:
            print(f"  {error}", file=sys.stderr)
        return 1

    metric_failures = metric_drift(baseline, current)
    if metric_failures:
        print("marketplace-compliance-ratchet: FAIL — non-monotone marketplace metrics:", file=sys.stderr)
        for error in metric_failures:
            print(f"  {error}", file=sys.stderr)
        return 1

    if newcomers:
        print("marketplace-compliance-ratchet: FAIL — new marketplace debt:", file=sys.stderr)
        for entry in newcomers:
            print(f"  {entry}", file=sys.stderr)
        return 1

    try:
        corpus = corpus_shrink_evidence(baseline, current, repo_root, args.checkout_sha)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"marketplace-compliance-ratchet: ERROR: {error}", file=sys.stderr)
        return 2
    detail = (
        f"baseline={corpus['baseline_count']}, live={corpus['current_count']}, "
        f"matching withdrawals={corpus['withdrawn_count']}, "
        f"unmatched net loss={corpus['unmatched_net_loss']}"
    )
    if not corpus["allowed"]:
        print(f"marketplace-compliance-ratchet: FAIL — R3 corpus shrink exceeds 2% ({detail})", file=sys.stderr)
        return 1
    print(f"marketplace-compliance-ratchet: R3 OK ({detail})")
    print(f"marketplace-compliance-ratchet: OK ({len(entries(current))} live triples; no entries outside baseline)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
