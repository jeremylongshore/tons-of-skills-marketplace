"""The opt-in signing trial cannot publish or replace production signing."""

import itertools
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


class CosignTrialContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = yaml.safe_load((ROOT / ".github/workflows/emit-evidence.yml").read_text())
        cls.production = cls.workflow["jobs"]["emit"]
        cls.trial = cls.workflow["jobs"]["cosign-v3-trial"]
        cls.approval = cls.workflow["jobs"]["approve-cosign-v3-trial"]

    def test_trial_requires_explicit_main_dispatch_and_does_not_cancel_production(self):
        events = self.workflow.get("on", self.workflow.get(True))
        self.assertEqual(set(events), {"push", "workflow_dispatch"})
        option = events["workflow_dispatch"]["inputs"]["cosign_v3_trial"]
        self.assertEqual(option["type"], "boolean")
        self.assertIs(option["default"], False)
        # These expressions use the shared JS/GitHub boolean/string subset.
        # Exercise actual workflow expressions, including absent dispatch inputs.
        evaluate = r"""
const fs = require('node:fs');
const {expressions, cases} = JSON.parse(fs.readFileSync(0, 'utf8'));
const format = (pattern, value) => pattern.replace('{0}', value);
const functions = expressions.map(expression => new Function(
  'github', 'inputs', 'format',
  'return (' + expression.replace(/^\$\{\{\s*|\s*\}\}$/g, '') + ')'
));
process.stdout.write(JSON.stringify(cases.map(({github, inputs}) =>
  functions.map(fn => fn(github, inputs, format) ?? false))));
"""
        cases = []
        for ref, event, choice, run_id in itertools.product(
            ["refs/heads/main", "refs/heads/feature"],
            ["push", "workflow_dispatch", "pull_request"],
            [None, False, True],
            ["100", "101"],
        ):
            cases.append(
                {
                    "github": {"ref": ref, "event_name": event, "run_id": run_id},
                    "inputs": {} if choice is None else {"cosign_v3_trial": choice},
                }
            )
        result = subprocess.run(
            ["node", "-e", evaluate],
            input=json.dumps(
                {
                    "expressions": [self.production["if"], self.trial["if"], self.workflow["concurrency"]["group"]],
                    "cases": cases,
                }
            ),
            text=True,
            capture_output=True,
            check=True,
        )
        for case, (production, trial, group) in zip(cases, json.loads(result.stdout)):
            with self.subTest(case=case):
                context = case["github"]
                opted_in = context["event_name"] == "workflow_dispatch" and case["inputs"].get("cosign_v3_trial", False)
                main = context["ref"] == "refs/heads/main"
                self.assertEqual(bool(production), main and not opted_in)
                self.assertEqual(bool(trial), main and opted_in)
                self.assertFalse(production and trial)
                expected_group = "cosign-v3-trial-" + context["run_id"] if opted_in else "emit-evidence"
                self.assertEqual(group, expected_group)

    def test_trial_rejects_unapproved_or_advanced_source_before_any_action(self):
        self.assertEqual(self.trial["needs"], "approve-cosign-v3-trial")
        self.assertNotIn("environment", self.trial)  # Preserve branch-ref OIDC sub.
        self.assertEqual(self.approval["environment"], "cosign-v3-trial")
        self.assertNotIn("id-token", self.approval["permissions"])
        self.assertEqual(self.approval["if"], self.trial["if"])
        guard = self.approval["steps"][0]
        self.assertNotIn("uses", guard)
        self.assertIn("inputs.approved_source_sha", guard["env"]["APPROVED_SHA"])
        self.assertIn("github.sha", guard["env"]["SOURCE_SHA"])
        source = "a" * 40
        for approved, succeeds in [
            (source, True),
            ("", False),
            ("a" * 39, False),
            ("A" * 40, False),
            ("b" * 40, False),
            ("$(exit 0)", False),
        ]:
            with self.subTest(approved=approved):
                result = subprocess.run(
                    ["bash", "-c", guard["run"]],
                    env={**os.environ, "APPROVED_SHA": approved, "SOURCE_SHA": source},
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode == 0, succeeds, result.stderr)

    def test_trial_has_no_write_or_publish_step(self):
        self.assertEqual(
            self.trial["permissions"],
            {"checks": "read", "contents": "read", "id-token": "write"},
        )
        for step in self.trial["steps"]:
            self.assertNotIn("gh release", step.get("run", ""))
        uploads = [s for s in self.trial["steps"] if s.get("uses", "").startswith("actions/upload-artifact@")]
        self.assertEqual(len(uploads), 1)
        self.assertEqual(uploads[0]["with"]["if-no-files-found"], "error")
        receipt = next(s["run"] for s in self.trial["steps"] if s["name"].startswith("Record trial"))
        self.assertIn('consumer_verification:"not_run"', receipt)
        self.assertIn("published:false", receipt)

    def test_exact_producer_payload_sign_verify_and_assembly_steps_are_reused(self):
        names = [
            "Await completed protected-branch contexts for this SHA",
            "Emit gate-result/v1 EvidenceBundle(s)",
            "Sign each EvidenceBundle (cosign keyless -> production Rekor)",
            "Verify each EvidenceBundle signature (cosign verify-blob; fail-closed)",
            "Assemble report-manifest.json (fail-closed on shape mismatch)",
        ]
        production = {s["name"]: s for s in self.production["steps"]}
        trial = {s["name"]: s for s in self.trial["steps"]}
        for name in names:
            with self.subTest(step=name):
                self.assertEqual(trial[name], production[name])
        self.assertIn('--certificate-identity "$cert_identity"', trial[names[3]]["run"])
        self.assertNotIn("--insecure", trial[names[3]]["run"])

    def test_waiters_retry_inconsistent_pages_and_fail_after_the_bound(self):
        publication = yaml.safe_load((ROOT / ".github/workflows/emit-publication-evidence.yml").read_text())
        cases = [("production", self.production), ("publication", publication["jobs"]["emit"])]
        for kind, job in cases:
            steps = job["steps"]
            waiter = next(step for step in steps if step["name"].startswith("Await"))
            if kind == "publication":
                source = next(step for step in steps if step["name"] == "Check out the exact publication source")
                controls = next(step for step in steps if step["name"].startswith("Check out workflow controls"))
                self.assertEqual(source["with"]["ref"], "${{ inputs.source_sha }}")
                self.assertEqual(controls["with"]["ref"], "${{ github.sha }}")
                runtime = next(i for i, step in enumerate(steps) if step["name"] == "Setup Node.js")
                self.assertLess(runtime, steps.index(waiter))
            for mode in ["valid", "transient", "always_bad"]:
                with (
                    self.subTest(kind=kind, mode=mode),
                    tempfile.TemporaryDirectory(prefix="cosign-waiter-") as directory,
                ):
                    work = pathlib.Path(directory)
                    binary = work / "bin"
                    binary.mkdir()
                    helper = pathlib.Path("ci/emit-evidence/merge-check-pages.mjs")
                    if kind == "publication":
                        helper = pathlib.Path(controls["with"]["path"]) / controls["with"]["sparse-checkout"]
                        self.assertFalse((work / "ci/emit-evidence/merge-check-pages.mjs").exists())
                    (work / helper).parent.mkdir(parents=True)
                    (work / helper).write_text((ROOT / "ci/emit-evidence/merge-check-pages.mjs").read_text())
                    mock = r"""#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
root = Path(os.environ['CHECK_FIXTURE_DIR'])
count = root / 'count'
n = int(count.read_text()) + 1 if count.exists() else 1
count.write_text(str(n))
assert '--slurp' in sys.argv
assert os.environ['EXPECTED_ENDPOINT'] in sys.argv
checks = [{'name': name, 'status': 'completed', 'conclusion': 'success'} for name in ['ci-required', 'gitleaks', 'skill-conform']]
second_total = 4 if os.environ['CHECK_MODE'] == 'always_bad' or (os.environ['CHECK_MODE'] == 'transient' and n == 1) else 3
print(json.dumps([{'total_count': 3, 'check_runs': checks[:1]}, {'total_count': second_total, 'check_runs': checks[1:]}]))
"""
                    (binary / "gh").write_text(mock)
                    (binary / "gh").chmod(0o700)
                    (binary / "sleep").write_text(r"""#!/usr/bin/env python3
import os, sys
from pathlib import Path
assert sys.argv[1:] == ['20']
with (Path(os.environ['CHECK_FIXTURE_DIR']) / 'sleeps').open('a') as stream:
    stream.write('20\n')
""")
                    (binary / "sleep").chmod(0o700)
                    source_sha = "e" * 40 if kind == "publication" else "f" * 40
                    environment = {
                        "PATH": str(binary) + os.pathsep + os.environ["PATH"],
                        "GITHUB_REPOSITORY": "example/repo",
                        "GITHUB_SHA": "f" * 40,
                        "SOURCE_SHA": "e" * 40,
                        "CHECK_FIXTURE_DIR": str(work),
                        "CHECK_MODE": mode,
                        "EXPECTED_ENDPOINT": "repos/example/repo/commits/" + source_sha + "/check-runs?per_page=100",
                    }
                    output = work / "required-checks.json"
                    script = waiter["run"].replace("/tmp/required-checks.json", str(output))
                    result = subprocess.run(
                        ["bash", "-c", script], cwd=work, env=environment, text=True, capture_output=True, timeout=30
                    )
                    attempts = int((work / "count").read_text())
                    if mode == "always_bad":
                        self.assertNotEqual(result.returncode, 0)
                        self.assertEqual(attempts, 30)
                        self.assertNotIn("all three required contexts completed", result.stdout)
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual(attempts, 2 if mode == "transient" else 1)
                        report = json.loads(output.read_text())
                        self.assertEqual(len(report["check_runs"]), 3)
                        self.assertIn("all three required contexts completed", result.stdout)
                    sleep_file = work / "sleeps"
                    sleeps = len(sleep_file.read_text().splitlines()) if sleep_file.exists() else 0
                    self.assertEqual(sleeps, 30 if mode == "always_bad" else 1 if mode == "transient" else 0)

    def test_both_production_installers_remain_v2_and_trial_pins_v3(self):
        def pin(job):
            return next(
                s["with"]["cosign-release"]
                for s in job["steps"]
                if s.get("uses", "").startswith("sigstore/cosign-installer@")
            )

        publication = yaml.safe_load((ROOT / ".github/workflows/emit-publication-evidence.yml").read_text())
        self.assertEqual(pin(self.production), "v2.5.2")
        self.assertEqual(pin(publication["jobs"]["emit"]), "v2.5.2")
        self.assertEqual(pin(self.trial), "v3.0.6")


if __name__ == "__main__":
    unittest.main()
