"""Full-history jobs in validate-plugins.yml must never re-shallow themselves.

Diff-scoped jobs check out with `fetch-depth: 0` and then compare the PR against
`origin/<base>` with a three-dot range, which needs a merge base. A
`git fetch --depth=1 origin <base>` in such a job turns a newly fetched base tip
into a parentless shallow root. If main advanced after the pull-request event,
the merge base is gone and the comparison dies (seen on #1612 as
"changed-plugin-deps: STRUCTURAL - cannot resolve changed files").

Jobs that deliberately check out shallow (`fetch-depth: 1`) and fetch one exact
SHA keep `--depth=1`; that is correct there and out of scope.
"""

import re
import unittest
from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "validate-plugins.yml"
DEPTH_FETCH = re.compile(r"\bgit\s+fetch\b[^\n]*--depth\b")


def full_history_jobs():
    jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
    for name, job in jobs.items():
        steps = job.get("steps", [])
        checkout = next((s for s in steps if str(s.get("uses", "")).startswith("actions/checkout")), None)
        if checkout and str((checkout.get("with") or {}).get("fetch-depth")) == "0":
            yield name, steps


class NoShallowRefetch(unittest.TestCase):
    def test_full_history_jobs_exist(self):
        self.assertGreaterEqual(len(list(full_history_jobs())), 4)

    def test_full_history_jobs_never_fetch_with_depth(self):
        for name, steps in full_history_jobs():
            for step in steps:
                with self.subTest(job=name, step=step.get("name")):
                    self.assertIsNone(
                        DEPTH_FETCH.search(str(step.get("run", ""))),
                        "a depth-limited fetch re-shallows this fetch-depth: 0 checkout",
                    )


if __name__ == "__main__":
    unittest.main()
