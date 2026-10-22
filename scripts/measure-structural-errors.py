#!/usr/bin/env python3
"""Measure Blueprint 727 row 7 from existing validator JSON, without revalidation.

The adjacent canonical validator owns rule classification. This adapter preserves
diagnostic multiplicity; it does not emit or modify a compliance baseline.
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


RULE_IDS = ("E-MISSING-REQUIRED-FIELD", "E-MISSING-REQUIRED-SECTION")


def relative_skill_path(value, root):
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise ValueError("invalid skill path")
    path = Path(value)
    if ".." in path.parts:
        raise ValueError(f"skill path traversal: {value}")
    if path.is_absolute():
        path = path.relative_to(root)
    if path.name != "SKILL.md" or path.as_posix() in ("SKILL.md", "."):
        raise ValueError(f"invalid skill path: {value}")
    # Do not allow an alias through a symlink to count as another artifact.
    probe = root
    for part in path.parts:
        probe /= part
        if probe.is_symlink():
            raise ValueError(f"symlink skill path: {value}")
    if not probe.is_file():
        raise ValueError(f"missing skill file: {value}")
    return path.as_posix()


def measure(payload, root, validator):
    if not isinstance(payload, dict) or set(payload) != {"rows", "expected_paths"}:
        raise ValueError("expected rows and canonical resolver paths")
    expected = payload["expected_paths"]
    if not isinstance(expected, list) or not expected:
        raise ValueError("canonical graded inventory must be nonempty")
    expected = [relative_skill_path(path, root) for path in expected]
    if len(set(expected)) != len(expected):
        raise ValueError("duplicate canonical resolver path")
    rows = payload["rows"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("validator rows must be nonempty")
    if not set(RULE_IDS).issubset(validator.DECLARED_MARKETPLACE_RULE_INVENTORY):
        raise ValueError("canonical validator no longer declares both structural rule IDs")
    if not isinstance(validator.SCHEMA_VERSION, str) or not validator.SCHEMA_VERSION:
        raise ValueError("missing canonical validator schema version")

    seen = set()
    affected = set()
    counts = dict.fromkeys(RULE_IDS, 0)
    unique = {rule: set() for rule in RULE_IDS}
    all_errors = 0
    for row in rows:
        if not isinstance(row, dict) or "fatal" in row:
            raise ValueError("fatal or malformed skill row prevents a complete measurement")
        path = relative_skill_path(row.get("path"), root)
        if path in seen:
            raise ValueError(f"duplicate validator path: {path}")
        seen.add(path)
        errors = row.get("errors")
        details = row.get("error_details")
        if (
            type(errors) is not int
            or errors < 0
            or not isinstance(details, list)
            or not all(isinstance(item, str) and item for item in details)
            or len(details) != errors
        ):
            raise ValueError(f"diagnostic count/type mismatch: {path}")
        all_errors += errors
        for error in details:
            triple = validator.baseline_finding_triple(path, error)
            if (
                not isinstance(triple, tuple)
                or len(triple) != 3
                or not all(isinstance(part, str) and part for part in triple)
                or triple[0] != path
            ):
                raise ValueError(f"malformed canonical classifier result: {path}")
            rule = triple[1]
            if rule in counts:
                counts[rule] += 1
                unique[rule].add(triple)
                affected.add(path)
    if seen != set(expected):
        missing = sorted(set(expected) - seen)
        extra = sorted(seen - set(expected))
        raise ValueError(f"graded path coverage mismatch: missing={missing[:5]}, extra={extra[:5]}")

    total = sum(counts.values())
    return {
        "measurement_schema_version": 1,
        "validator_schema_version": validator.SCHEMA_VERSION,
        "skill_rows": len(seen),
        "missing_required_field_occurrences": counts[RULE_IDS[0]],
        "missing_required_section_occurrences": counts[RULE_IDS[1]],
        "structural_occurrences": total,
        "all_skill_error_occurrences": all_errors,
        "other_skill_error_occurrences": all_errors - total,
        "affected_skills": len(affected),
        "unique_structural_triples": sum(len(members) for members in unique.values()),
        "unique_triples_by_rule": {rule: len(unique[rule]) for rule in RULE_IDS},
        "structural_share_of_skill_errors_pct": round(100 * total / all_errors, 4) if all_errors else None,
    }


def main():
    root = Path.cwd().resolve()
    source = root / "scripts" / "validate-skills-schema.py"
    if source.is_symlink() or source.parent.is_symlink():
        raise ValueError("canonical classifier must not be a symlink")
    spec = importlib.util.spec_from_file_location("canonical_structural_classifier", source)
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    result = measure(json.load(sys.stdin), root, validator)
    result["validator_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, AttributeError, OSError) as error:
        print(f"structural-measurement: {error}", file=sys.stderr)
        sys.exit(1)
