#!/usr/bin/env python3
"""Generate self-contained copies of shared policy and helper; --check is read-only."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BILLABLE = (
    "hello-world",
    "core-workflow-a",
    "core-workflow-b",
    "ci-integration",
    "deploy-integration",
    "upgrade-migration",
    "multi-env-setup",
    "performance-tuning",
    "cks-provisioning",
    "caios-stage-model",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failed = []
    for name in BILLABLE:
        skill = ROOT / "skills" / ("coreweave-" + name)
        for source, dest in [
            ("cost-gate.md", "references/cost-gate.md"),
            ("review-cost-plan.py", "scripts/review-cost-plan.py"),
        ]:
            expected = (ROOT / "shared" / source).read_bytes()
            target = skill / dest
            if args.check:
                if not target.is_file() or target.read_bytes() != expected:
                    failed.append(str(target.relative_to(ROOT)))
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(expected)
    for path in failed:
        print("DRIFT:", path)
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
