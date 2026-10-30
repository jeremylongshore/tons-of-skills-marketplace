#!/usr/bin/env python3
"""Expand pinned section debt from its original capture, never from live debt.

Print a candidate baseline; do not write files, commit, push or dispatch CI.
Publication still requires the existing owner-dispatched capture transaction.
Historical source is parsed as data, never imported or executed.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = "scripts/validate-skills-schema.py"
BASELINE_PATH = "scripts/.marketplace-compliance-baseline.json"
SECTION_RULE = "E-MISSING-REQUIRED-SECTION"
SECTION_HELPERS = {"iter_non_code_lines", "has_markdown_h1", "has_heading_line", "resolve_present_heading"}


def git_text(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        env={**os.environ, "GIT_NO_REPLACE_OBJECTS": "1"},
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def historical_file(root: Path, source_sha: str, path: str) -> str:
    records = git_text(root, "ls-tree", "-z", source_sha, "--", path).split("\0")
    if len(records) != 2 or records[1] or "\t" not in records[0]:
        raise ValueError(f"historical source must contain a regular tracked file: {path}")
    metadata, actual_path = records[0].split("\t", 1)
    blob = re.fullmatch(r"100(?:644|755) blob ([0-9a-f]{40})", metadata)
    if blob is None or actual_path != path:
        raise ValueError(f"historical source must contain a regular tracked file: {path}")
    return git_text(root, "cat-file", "blob", blob.group(1))


def one_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    matches = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one canonical {name} function")
    return matches[0]


def section_contract(tree: ast.Module) -> list[str]:
    """Fingerprint only the historical parser and section-check dependencies."""
    body = one_function(tree, "validate_body")
    helpers = [node for node in body.body if isinstance(node, ast.FunctionDef) and node.name in SECTION_HELPERS]
    if {node.name for node in helpers} != SECTION_HELPERS or len(helpers) != len(SECTION_HELPERS):
        raise ValueError("canonical required-section helpers are missing or duplicated")
    loops = [
        node
        for node in body.body
        if isinstance(node, ast.If)
        and ast.unparse(node.test) == "tier == TIER_ENTERPRISE"
        and any(
            isinstance(child, ast.For) and isinstance(child.iter, ast.Name) and child.iter.id == "RECOMMENDED_SECTIONS"
            for child in node.body
        )
    ]
    if len(loops) != 1:
        raise ValueError("canonical required-section loop is missing or duplicated")
    section_nodes = [*helpers, loops[0]]
    covered = {id(child) for node in section_nodes for child in ast.walk(node)}
    if any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and "Required section missing:" in node.value
        and id(node) not in covered
        for node in ast.walk(body)
    ):
        raise ValueError("required-section diagnostics exist outside the verified historical section check")
    dependencies = []
    for name in (
        "RECOMMENDED_SECTIONS",
        "SECTION_SYNONYMS",
        "CODE_FENCE_PATTERN",
        "RE_FRONTMATTER",
        "TIER_MARKETPLACE",
        "TIER_ENTERPRISE",
    ):
        matches = [
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
        ]
        if len(matches) != 1:
            raise ValueError(f"canonical dependency {name} is missing or duplicated")
        dependencies.append(matches[0])
    return [
        ast.dump(node, include_attributes=False)
        for node in [one_function(tree, "parse_frontmatter"), *dependencies, *section_nodes]
    ]


def parse_entry(entry: str) -> tuple[str, str, str]:
    parts = entry.split(" :: ")
    if len(parts) != 3 or not all(parts):
        raise ValueError("baseline contains a malformed finding identity")
    return tuple(parts)


def section_path(path: str) -> None:
    parsed = PurePosixPath(path)
    if (
        parsed.is_absolute()
        or parsed.as_posix() != path
        or ".." in parsed.parts
        or "\\" in path
        or any(ord(character) < 32 or ord(character) == 127 for character in path)
        or not path.startswith("plugins/")
        or parsed.name != "SKILL.md"
    ):
        raise ValueError(f"section debt is not a canonical repository-relative skill path: {path}")


def migrate(root: Path, baseline_bytes: bytes, *, run_id: str | None = None) -> dict[str, Any]:
    baseline = json.loads(baseline_bytes)
    if not isinstance(baseline, dict) or type(baseline.get("finding_identity_version", 1)) is not int:
        raise ValueError("baseline must declare the legacy version-1 identity contract")
    if (
        baseline.get("finding_identity_version", 1) != 1
        or "identity_migration" in baseline
        or "corpus_source_sha" in baseline
    ):
        raise ValueError("section migration accepts only an unmigrated version-1 baseline")
    provenance = baseline.get("generated_from")
    source_sha = provenance.get("sha") if isinstance(provenance, dict) else None
    if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", source_sha):
        raise ValueError("baseline requires an immutable original capture source SHA")
    if git_text(root, "cat-file", "-t", source_sha).strip() != "commit":
        raise ValueError("original capture source must identify a commit")
    entries = baseline.get("entries")
    if not isinstance(entries, list) or not all(isinstance(entry, str) for entry in entries):
        raise ValueError("baseline entries must be an array of finding identities")
    if len(entries) != len(set(entries)):
        raise ValueError("baseline contains duplicate finding identities")
    totals = baseline.get("totals")
    ceiling = totals.get("errors") if isinstance(totals, dict) else None
    if type(ceiling) is not int or ceiling < len(entries):
        raise ValueError("legacy error ceiling must be an integer no smaller than its unique findings")
    if "raw_error_occurrences" in totals:
        raise ValueError("legacy raw occurrence contract needs explicit review before identity migration")

    historical_source = historical_file(root, source_sha, VALIDATOR_PATH)
    current_source = (root / VALIDATOR_PATH).read_text(encoding="utf-8")
    if section_contract(ast.parse(historical_source)) != section_contract(ast.parse(current_source)):
        raise ValueError("historical parser or required-section semantics differ from the current validator")
    trusted_validator = ROOT / VALIDATOR_PATH
    if current_source != trusted_validator.read_text(encoding="utf-8"):
        raise ValueError("repository validator must match the reviewed migration tool's canonical validator")
    # --repo-root supplies data, not executable Python. Import only this tool's
    # companion validator, after proving that the inspected source matches it.
    spec = importlib.util.spec_from_file_location("section_migration_validator", trusted_validator)
    if spec is None or spec.loader is None:
        raise ValueError("could not load the current canonical validator")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    if baseline.get("schema_version") != validator.SCHEMA_VERSION:
        raise ValueError("section migration must not change the validator schema contract")

    pinned_sections: dict[str, set[str]] = {}
    retained = set()
    for entry in entries:
        path, rule, field = parse_entry(entry)
        if rule != SECTION_RULE:
            retained.add(entry)
            continue
        section_path(path)
        if field not in ("#", "##"):
            raise ValueError("legacy section entry is already precise or malformed")
        pinned_sections.setdefault(path, set()).add(field)
    if not pinned_sections:
        raise ValueError("baseline has no legacy section identities to migrate")

    expanded = set()
    for path, fields in sorted(pinned_sections.items()):
        content = historical_file(root, source_sha, path)
        fm, body = validator.parse_frontmatter(content)
        diagnostics, _, _ = validator.validate_body(Path(path), body, validator.TIER_MARKETPLACE, fm)
        sections: dict[str, set[str]] = {}
        for diagnostic in diagnostics:
            if "Required section missing:" not in diagnostic:
                continue
            legacy = validator.baseline_finding_triple(path, diagnostic, identity_version=1)
            precise = validator.baseline_finding_triple(path, diagnostic, identity_version=2)
            if legacy[1] != SECTION_RULE or precise[1] != SECTION_RULE:
                raise ValueError("canonical classifier did not preserve the section rule")
            sections.setdefault(legacy[2], set()).add(" :: ".join(precise))
        if not fields.issubset(sections):
            raise ValueError(f"pinned section debt is not reproduced by its original capture source: {path}")
        # Only surviving pinned keys may expand. Historical keys already removed
        # by a shrink must never be resurrected by reading the original source.
        for field in fields:
            expanded.update(sections[field])

    old_section_count = sum(len(fields) for fields in pinned_sections.values())
    delta = len(expanded) - old_section_count
    if delta < 0:
        raise ValueError("identity expansion unexpectedly removed a pinned section key")
    migrated = copy.deepcopy(baseline)
    migrated["entries"] = sorted(retained | expanded)
    migrated["totals"]["errors"] = ceiling + delta
    migrated["finding_identity_version"] = 2
    # generated_from identifies this new owner transaction. R3 must retain the
    # original source of the unchanged historical corpus denominator.
    migrated["corpus_source_sha"] = source_sha
    migrated["identity_migration"] = {
        "kind": "historical-required-sections-v1-to-v2",
        "prior_baseline_sha256": hashlib.sha256(baseline_bytes).hexdigest(),
        "prior_generated_from": provenance,
        "historical_validator_sha256": hashlib.sha256(historical_source.encode()).hexdigest(),
        "section_paths": len(pinned_sections),
        "prior_section_identities": old_section_count,
        "precise_section_identities": len(expanded),
        "preserved_error_ceiling_offset": ceiling - len(entries),
        "historical_raw_error_occurrences": None,
    }
    migrated["generated_from"] = {
        "sha": git_text(root, "rev-parse", "HEAD").strip(),
        "run_id": run_id,
        "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return migrated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    try:
        candidate = migrate(root, (root / BASELINE_PATH).read_bytes(), run_id=os.environ.get("GITHUB_RUN_ID"))
    except (OSError, ValueError, SyntaxError, subprocess.CalledProcessError) as error:
        print(f"section-identity-migration: ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(candidate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
