"""Regression coverage for Blueprint 727 E6.3's R1 comparator."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-marketplace-compliance-baseline.py"
CAPTURE_WORKFLOW = ROOT / ".github" / "workflows" / "capture-marketplace-compliance-baseline.yml"
VALIDATE_WORKFLOW = ROOT / ".github" / "workflows" / "validate-plugins.yml"


def load_module():
    spec = importlib.util.spec_from_file_location("marketplace_compliance_ratchet", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load ratchet")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarketplaceComplianceRatchetTests(unittest.TestCase):
    def setUp(self):
        self.ratchet = load_module()

    def test_existing_baselined_debt_passes_r1(self):
        baseline = {"entries": ["a/SKILL.md :: E-ONE :: name"]}
        current = {"entries": ["a/SKILL.md :: E-ONE :: name"]}
        self.assertEqual(self.ratchet.compare(baseline, current), [])

    def test_planted_new_triple_fails_r1(self):
        baseline = {"entries": ["a/SKILL.md :: E-ONE :: name"]}
        current = {
            "entries": [
                "a/SKILL.md :: E-ONE :: name",
                "b/SKILL.md :: E-MISSING-REQUIRED-FIELD :: author",
            ]
        }
        self.assertEqual(
            self.ratchet.compare(baseline, current),
            ["b/SKILL.md :: E-MISSING-REQUIRED-FIELD :: author"],
        )

    def test_real_emitter_and_ratchet_cli_detect_a_different_missing_section(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "plugins/example/skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            sections = (
                "## Overview",
                "## Prerequisites",
                "## Instructions",
                "## Output",
                "## Error Handling",
                "## Examples",
                "## Resources",
            )

            def write_skill(missing):
                skill.write_text(
                    "---\nname: example\ndescription: An isolated section identity fixture.\n---\n# Example\n\n"
                    + "\n\n".join(
                        section + "\n\nInspect the supplied input and record the observed result."
                        for section in sections
                        if section not in missing
                    ),
                    encoding="utf-8",
                )

            write_skill({"## Overview", "## Resources"})
            legacy_before = self.ratchet.emit_current(root)
            before = self.ratchet.emit_current(root, finding_identity_version=2)
            self.assertEqual(before["finding_identity_version"], 2)
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps(before), encoding="utf-8")

            # Keep Overview missing and the number of missing sections constant.
            # R1 must still detect Examples rather than aliasing it to Overview.
            write_skill({"## Overview", "## Examples"})
            legacy_after = self.ratchet.emit_current(root)
            after = self.ratchet.emit_current(root, finding_identity_version=2)
            self.assertEqual(self.ratchet.compare(legacy_before, legacy_after), [])
            self.assertEqual(before["totals"]["errors"], after["totals"]["errors"])
            expected = "plugins/example/skills/example/SKILL.md :: E-MISSING-REQUIRED-SECTION :: ## Examples"
            self.assertEqual(self.ratchet.compare(before, after), [expected])

            # The actual CLI must select v2 from pinned metadata, without a
            # caller override, a supplied --current payload, or a mocked emitter.
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--baseline", str(baseline), "--repo-root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn("new marketplace debt", result.stderr)
            self.assertIn(expected, result.stderr)
            self.assertNotIn("contract drift", result.stderr)

    def test_emitter_refuses_unknown_pinned_identity_versions(self):
        for version in (True, 0, 3, "2"):
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "unsupported"):
                self.ratchet.emit_current(ROOT, finding_identity_version=version)

    def test_malformed_entries_fail_closed(self):
        with self.assertRaises(ValueError):
            self.ratchet.compare({"entries": "not-a-list"}, {"entries": []})

    def test_unknown_rule_id_requires_conscious_rebaseline(self):
        baseline = {"schema_version": "4.1.0", "rule_inventory": ["E-ONE"]}
        current = {"schema_version": "4.1.0", "rule_inventory": ["E-ONE", "E-NEW"]}
        self.assertEqual(
            self.ratchet.metadata_drift(baseline, current),
            ["unknown live rule id(s): E-NEW"],
        )

    def test_schema_version_drift_requires_conscious_rebaseline(self):
        baseline = {"schema_version": "4.1.0", "rule_inventory": ["E-ONE"]}
        current = {"schema_version": "4.2.0", "rule_inventory": ["E-ONE"]}
        self.assertEqual(
            self.ratchet.metadata_drift(baseline, current),
            ["schema_version drift: baseline=4.1.0, live=4.2.0"],
        )

    def test_finding_identity_version_cannot_silently_change(self):
        baseline = {"schema_version": "4.1.0", "rule_inventory": ["E-ONE"], "entries": []}
        current = {**baseline, "finding_identity_version": 2}
        self.assertEqual(
            self.ratchet.metadata_drift(baseline, current),
            ["finding_identity_version drift: baseline=1, live=2"],
        )
        self.assertTrue(self.ratchet.capture_required_reasons(baseline, current))
        self.assertIn(
            "owner-dispatched capture artifact",
            self.ratchet.baseline_growth_error(
                baseline,
                current,
                {self.ratchet.BASELINE_PATH},
                "automation/compliance-baseline-123",
            ),
        )

    def test_version_two_rejects_collapsed_or_unknown_identity_contracts(self):
        baseline = {"schema_version": "4.1.0", "rule_inventory": ["E-ONE"], "entries": []}
        for version in (True, 0, 3, "2"):
            with self.subTest(version=version):
                self.assertIn(
                    "live has unsupported finding_identity_version",
                    self.ratchet.metadata_drift(baseline, {**baseline, "finding_identity_version": version}),
                )
        collapsed = {
            **baseline,
            "finding_identity_version": 2,
            "entries": ["a/SKILL.md :: E-MISSING-REQUIRED-SECTION :: ##"],
        }
        self.assertIn(
            "live finding_identity_version=2 contains an unnamed required-section entry",
            self.ratchet.metadata_drift(collapsed, collapsed),
        )

    def test_monotone_metrics_allow_equal_or_improved_values(self):
        baseline = {
            "totals": {"errors": 10, "grade_A_plus_B_pct": 75.0},
        }
        current = {
            "totals": {"errors": 9, "grade_A_plus_B_pct": 80.0},
        }
        self.assertEqual(self.ratchet.metric_drift(baseline, current), [])

    def test_error_total_growth_fails_r2(self):
        baseline = {"totals": {"errors": 10, "grade_A_plus_B_pct": 75.0}}
        current = {"totals": {"errors": 11, "grade_A_plus_B_pct": 75.0}}
        self.assertEqual(
            self.ratchet.metric_drift(baseline, current),
            ["totals.errors increased: baseline=10, live=11"],
        )

    def test_a_plus_b_share_dilution_fails_r4(self):
        baseline = {"totals": {"errors": 10, "grade_A_plus_B_pct": 75.0}}
        current = {"totals": {"errors": 10, "grade_A_plus_B_pct": 74.5}}
        self.assertEqual(
            self.ratchet.metric_drift(baseline, current),
            ["totals.grade_A_plus_B_pct fell: baseline=75, live=74.5"],
        )

    def test_monotone_metrics_fail_closed_when_totals_are_missing(self):
        self.assertEqual(
            self.ratchet.metric_drift({}, {"totals": {}}),
            ["baseline and live payload must declare object totals"],
        )

    def test_monotone_metrics_fail_closed_on_non_numeric_values(self):
        baseline = {"totals": {"errors": 10, "grade_A_plus_B_pct": 75.0}}
        current = {"totals": {"errors": "10", "grade_A_plus_B_pct": 75.0}}
        self.assertEqual(
            self.ratchet.metric_drift(baseline, current),
            ["live totals.errors must be a finite number"],
        )

    def test_baseline_growth_is_refused_on_a_regular_pull_request(self):
        baseline = {"entries": ["a/SKILL.md :: E-ONE :: name"]}
        current = {"entries": ["a/SKILL.md :: E-ONE :: name", "b/SKILL.md :: E-TWO :: tags"]}
        self.assertEqual(
            self.ratchet.baseline_growth_error(
                baseline,
                current,
                {"scripts/.marketplace-compliance-baseline.json", "plugins/example/SKILL.md"},
                "feature/ordinary-change",
            ),
            "a permissive baseline policy-envelope change may only occur in a one-file baseline-only pull request",
        )

    def test_capture_branch_name_alone_cannot_authorize_growth(self):
        baseline = {"entries": ["a/SKILL.md :: E-ONE :: name"]}
        current = {"entries": ["a/SKILL.md :: E-ONE :: name", "b/SKILL.md :: E-TWO :: tags"]}
        self.assertEqual(
            self.ratchet.baseline_growth_error(
                baseline,
                current,
                {"scripts/.marketplace-compliance-baseline.json"},
                "automation/compliance-baseline-123",
            ),
            "a permissive baseline policy-envelope change requires an owner-dispatched capture artifact verified by required CI",
        )

    def test_strict_entry_and_metric_improvements_do_not_need_capture(self):
        baseline = {
            "entries": ["a/SKILL.md :: E-ONE :: name", "b/SKILL.md :: E-TWO :: tags"],
            "totals": {"errors": 2, "grade_A_plus_B_pct": 50.0},
        }
        current = {
            "entries": ["a/SKILL.md :: E-ONE :: name"],
            "totals": {"errors": 1, "grade_A_plus_B_pct": 75.0},
        }
        self.assertEqual(self.ratchet.capture_required_reasons(baseline, current), [])

    def run_ordinary_baseline_mutation(self, mutate):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            baseline_path = repo / "scripts" / ".marketplace-compliance-baseline.json"
            baseline_path.parent.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            baseline = {
                "$comment": "shrink only",
                "schema_version": "4.1.0",
                "rule_inventory": ["E-ONE"],
                "corpus_definition": "resolveCorpus('graded')",
                "corpus": {"skill_files": 3628, "command_files": 373},
                "entries": ["a/SKILL.md :: E-ONE :: name"],
                "generated_from": {"sha": "a" * 40},
                "totals": {"errors": 2132, "grade_A_plus_B": 2979, "grade_A_plus_B_pct": 82.1114},
            }
            baseline_path.write_text(json.dumps(baseline, sort_keys=True) + "\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
            source_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

            current = copy.deepcopy(baseline)
            mutate(current)
            baseline_path.write_text(json.dumps(current, sort_keys=True) + "\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "mutate"], cwd=repo, check=True)
            return subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--check-growth-only",
                    "--repo-root",
                    str(repo),
                    "--baseline",
                    str(baseline_path),
                    "--base",
                    source_sha,
                    "--head-ref",
                    "feature/ordinary-change",
                ],
                capture_output=True,
                text=True,
            )

    def test_cli_regular_branch_refuses_permissive_metric_mutations(self):
        mutations = {
            "errors-increase": lambda payload: payload["totals"].__setitem__("errors", 3132),
            "grade-share-decrease": lambda payload: payload["totals"].__setitem__("grade_A_plus_B_pct", 0),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                result = self.run_ordinary_baseline_mutation(mutate)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("permissive baseline policy-envelope change", result.stderr)

    def test_cli_regular_branch_refuses_other_envelope_mutations(self):
        mutations = {
            "schema-version": lambda payload: payload.__setitem__("schema_version", "99.0.0"),
            "rule-inventory": lambda payload: payload["rule_inventory"].append("E-NEW"),
            "corpus-definition": lambda payload: payload.__setitem__("corpus_definition", "partial"),
            "corpus-denominator": lambda payload: payload["corpus"].__setitem__("skill_files", 1),
            "grade-count-denominator": lambda payload: payload["totals"].__setitem__("grade_A_plus_B", 1),
            "generated-provenance": lambda payload: payload["generated_from"].__setitem__("sha", "b" * 40),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                result = self.run_ordinary_baseline_mutation(mutate)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("permissive baseline policy-envelope change", result.stderr)

    def capture_provenance(self):
        source_sha = "a" * 40
        head_sha = "b" * 40
        baseline_bytes = b'{"entries": []}\n'
        return {
            "current": {"generated_from": {"sha": source_sha}},
            "head_ref": "automation/compliance-baseline-123",
            "repository": "jeremylongshore/tons-of-skills-marketplace",
            "repository_owner": "jeremylongshore",
            "base_ref": "main",
            "pr_number": 456,
            "head_sha": head_sha,
            "head_parents": [source_sha],
            "run": {
                "id": 123,
                "event": "workflow_dispatch",
                "path": ".github/workflows/capture-marketplace-compliance-baseline.yml",
                "head_branch": "main",
                "head_sha": source_sha,
                "run_attempt": 1,
                "head_repository": {"full_name": "jeremylongshore/tons-of-skills-marketplace"},
                "actor": {"login": "jeremylongshore"},
                "triggering_actor": {"login": "jeremylongshore"},
            },
            "jobs": {
                "jobs": [
                    {
                        "name": "capture-baseline-artifact",
                        "status": "completed",
                        "conclusion": "success",
                    }
                ]
            },
            "pull_requests": [
                {
                    "number": 456,
                    "state": "open",
                    "head": {
                        "ref": "automation/compliance-baseline-123",
                        "sha": head_sha,
                        "repo": {"full_name": "jeremylongshore/tons-of-skills-marketplace"},
                    },
                    "base": {"ref": "main"},
                }
            ],
            "artifact_bytes": baseline_bytes,
            "baseline_bytes": baseline_bytes,
        }

    def test_owner_capture_artifact_authorizes_one_file_growth(self):
        provenance = self.capture_provenance()
        self.assertEqual(self.ratchet.capture_provenance_errors(**provenance), [])
        baseline = {"entries": ["a/SKILL.md :: E-ONE :: name"]}
        current = {"entries": ["a/SKILL.md :: E-ONE :: name", "b/SKILL.md :: E-TWO :: tags"]}
        self.assertIsNone(
            self.ratchet.baseline_growth_error(
                baseline,
                current,
                {"scripts/.marketplace-compliance-baseline.json"},
                "automation/compliance-baseline-123",
                capture_authorized=True,
            )
        )

    def test_non_owner_dispatch_is_refused(self):
        provenance = self.capture_provenance()
        provenance["run"]["triggering_actor"] = {"login": "contributor"}
        self.assertIn(
            "capture run triggering_actor is not the repository owner",
            self.ratchet.capture_provenance_errors(**provenance),
        )

    def test_wrong_workflow_is_refused(self):
        provenance = self.capture_provenance()
        provenance["run"]["path"] = ".github/workflows/untrusted.yml"
        self.assertIn(
            "capture run used an unexpected workflow",
            self.ratchet.capture_provenance_errors(**provenance),
        )

    def test_failed_capture_job_is_refused(self):
        provenance = self.capture_provenance()
        provenance["jobs"]["jobs"][0]["conclusion"] = "failure"
        self.assertIn(
            "capture run has no successful capture-baseline-artifact job",
            self.ratchet.capture_provenance_errors(**provenance),
        )

    def test_artifact_mismatch_is_refused(self):
        provenance = self.capture_provenance()
        provenance["artifact_bytes"] = b'{"entries": ["smuggled"]}\n'
        self.assertIn(
            "pull request baseline is not byte-identical to the immutable capture artifact",
            self.ratchet.capture_provenance_errors(**provenance),
        )

    def test_replayed_capture_branch_is_refused(self):
        provenance = self.capture_provenance()
        provenance["pull_requests"].append(
            {
                "number": 123,
                "state": "closed",
                "head": provenance["pull_requests"][0]["head"],
                "base": {"ref": "main"},
            }
        )
        self.assertIn(
            "capture branch must belong to exactly one pull request and cannot be replayed",
            self.ratchet.capture_provenance_errors(**provenance),
        )

    def test_fork_capture_branch_is_refused(self):
        provenance = self.capture_provenance()
        provenance["pull_requests"][0]["head"]["repo"] = {"full_name": "attacker/fork"}
        self.assertIn(
            "capture pull request head is not in this repository",
            self.ratchet.capture_provenance_errors(**provenance),
        )

    def test_extra_or_reparented_commit_is_refused(self):
        provenance = self.capture_provenance()
        provenance["head_parents"] = ["c" * 40]
        self.assertIn(
            "pull request head must be one capture commit directly atop the capture source",
            self.ratchet.capture_provenance_errors(**provenance),
        )

    def test_capture_branch_requires_exact_run_id_shape(self):
        self.assertEqual(self.ratchet.capture_run_id("automation/compliance-baseline-123"), 123)
        self.assertIsNone(self.ratchet.capture_run_id("automation/compliance-baseline-123-extra"))
        self.assertIsNone(self.ratchet.capture_run_id("automation/compliance-baseline-0"))

    def test_required_ci_wires_the_owner_capture_receipt(self):
        capture = CAPTURE_WORKFLOW.read_text(encoding="utf-8")
        validation = VALIDATE_WORKFLOW.read_text(encoding="utf-8")

        for required_capture_fragment in (
            'test "$ACTOR" = "$REPOSITORY_OWNER"',
            'test "$TRIGGERING_ACTOR" = "$REPOSITORY_OWNER"',
            "name: marketplace-compliance-baseline-${{ github.run_id }}",
            "include-hidden-files: true",
            "GH_TOKEN: ${{ secrets.BOT_PR_TOKEN }}",
        ):
            self.assertIn(required_capture_fragment, capture)
        self.assertNotIn("secrets.GITHUB_TOKEN", capture)

        for required_validation_fragment in (
            "marketplace-compliance-ratchet:",
            '--capture-run-metadata "$evidence_dir/run.json"',
            '--capture-run-jobs "$evidence_dir/jobs.json"',
            '--capture-pull-requests "$evidence_dir/pulls.json"',
            '--capture-artifact "${artifact_files[0]}"',
            "- marketplace-compliance-ratchet",
        ):
            self.assertIn(required_validation_fragment, validation)

    def test_growth_cli_requires_and_accepts_exact_capture_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir)
            baseline_path = repo / "scripts" / ".marketplace-compliance-baseline.json"
            baseline_path.parent.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
            baseline_path.write_text('{"entries": []}\n', encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
            source_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

            payload = {"entries": ["a/SKILL.md :: E-ONE :: name"], "generated_from": {"sha": source_sha}}
            baseline_bytes = (json.dumps(payload, sort_keys=True) + "\n").encode()
            baseline_path.write_bytes(baseline_bytes)
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "capture"], cwd=repo, check=True)
            head_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

            run_path = repo / "run.json"
            jobs_path = repo / "jobs.json"
            pulls_path = repo / "pulls.json"
            artifact_path = repo / "artifact.json"
            provenance = self.capture_provenance()
            provenance["current"] = payload
            provenance["head_sha"] = head_sha
            provenance["head_parents"] = [source_sha]
            provenance["run"]["head_sha"] = source_sha
            provenance["pull_requests"][0]["head"]["sha"] = head_sha
            run_path.write_text(json.dumps(provenance["run"]), encoding="utf-8")
            jobs_path.write_text(json.dumps(provenance["jobs"]), encoding="utf-8")
            pulls_path.write_text(json.dumps(provenance["pull_requests"]), encoding="utf-8")
            artifact_path.write_bytes(baseline_bytes)

            common = [
                sys.executable,
                str(SCRIPT),
                "--check-growth-only",
                "--repo-root",
                str(repo),
                "--baseline",
                str(baseline_path),
                "--base",
                source_sha,
                "--head-ref",
                "automation/compliance-baseline-123",
            ]
            missing_receipt = subprocess.run(common, capture_output=True, text=True)
            self.assertEqual(missing_receipt.returncode, 1)
            self.assertIn("requires an owner-dispatched capture artifact", missing_receipt.stderr)

            accepted = subprocess.run(
                common
                + [
                    "--head-sha",
                    head_sha,
                    "--repository",
                    "jeremylongshore/tons-of-skills-marketplace",
                    "--repository-owner",
                    "jeremylongshore",
                    "--base-ref",
                    "main",
                    "--pr-number",
                    "456",
                    "--capture-run-metadata",
                    str(run_path),
                    "--capture-run-jobs",
                    str(jobs_path),
                    "--capture-pull-requests",
                    str(pulls_path),
                    "--capture-artifact",
                    str(artifact_path),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            self.assertIn("OK (no unauthorized permissive baseline mutation)", accepted.stdout)


class CorpusShrinkCliTests(unittest.TestCase):
    """Exercise the public Python gate against committed Git corpus/catalog fixtures."""

    def run_fixture(
        self, *, remove=0, withdraw=False, alias=False, reported_count=None, checkout_sha=None, dirty=False
    ):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

            git("init", "-q")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.com")
            catalog_path = repo / ".claude-plugin" / "marketplace.extended.json"
            catalog_path.parent.mkdir()
            catalog = {"plugins": [{"name": "fixture", "source": "./plugins/test/fixture"}]}
            if alias:
                catalog["plugins"].append({"name": "alias", "source": "./plugins/test/fixture"})
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            skills = []
            for index in range(50):
                skill = repo / f"plugins/test/fixture/skills/skill-{index}/SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text("# Test skill\n", encoding="utf-8")
                skills.append(skill)
            git("add", ".")
            git("commit", "-qm", "source corpus")
            source_sha = git("rev-parse", "HEAD")
            for skill in skills[:remove]:
                skill.unlink()
            if withdraw:
                catalog["plugins"] = [entry for entry in catalog["plugins"] if entry["name"] != "fixture"]
                catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            git("add", "-A")
            git("commit", "--allow-empty", "-qm", "candidate corpus")
            head = git("rev-parse", "HEAD")
            if dirty:
                skills[-1].write_text("# Uncommitted edit\n", encoding="utf-8")
            payload = {
                "schema_version": "4.1.0",
                "rule_inventory": ["E-ONE"],
                "entries": [],
                "totals": {"errors": 0, "grade_A_plus_B_pct": 100},
                "corpus": {"skill_files": 50},
                "generated_from": {"sha": source_sha},
            }
            baseline = root / "baseline.json"
            baseline.write_text(json.dumps(payload), encoding="utf-8")
            payload["corpus"]["skill_files"] = 50 - remove if reported_count is None else reported_count
            payload["generated_from"]["sha"] = head
            current = root / "current.json"
            current.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--baseline",
                    str(baseline),
                    "--current",
                    str(current),
                    "--checkout-sha",
                    checkout_sha or head,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

    def test_exact_two_percent_loss_is_allowed(self):
        result = self.run_fixture(remove=1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("R3 OK", result.stdout)
        self.assertIn("matching withdrawals=0", result.stdout)

    def test_unmatched_loss_over_two_percent_fails_the_public_gate(self):
        result = self.run_fixture(remove=2)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("R3 corpus shrink exceeds 2%", result.stderr)

    def test_matching_catalog_withdrawal_credits_only_removed_paths(self):
        result = self.run_fixture(remove=5, withdraw=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("matching withdrawals=5", result.stdout)

    def test_retained_published_alias_does_not_authorize_shrink(self):
        result = self.run_fixture(remove=5, withdraw=True, alias=True)
        self.assertEqual(result.returncode, 1, result.stderr)

    def test_forged_current_count_cannot_hide_actual_git_deletions(self):
        result = self.run_fixture(remove=2, reported_count=50)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("ERROR", result.stderr)

    def test_wrong_checkout_identity_and_dirty_tree_fail_closed(self):
        for kwargs in ({"checkout_sha": "f" * 40}, {"dirty": True}):
            with self.subTest(**kwargs):
                result = self.run_fixture(**kwargs)
                self.assertEqual(result.returncode, 2, result.stderr)

    def test_required_workflow_binds_census_to_immutable_checkout(self):
        import yaml

        job = yaml.safe_load(VALIDATE_WORKFLOW.read_text(encoding="utf-8"))["jobs"]["marketplace-compliance-ratchet"]
        steps = job["steps"]
        enforcement = next(
            step for step in steps if step.get("name") == "Enforce R1/R2/R3/R4 marketplace compliance ratchet"
        )
        self.assertEqual(enforcement["env"]["CHECKOUT_SHA"], "${{ github.sha }}")
        self.assertIn('--checkout-sha "$CHECKOUT_SHA"', enforcement["run"])
        self.assertNotIn("if", enforcement)
        self.assertNotIn("continue-on-error", enforcement)
        regression = next(step for step in steps if step.get("name") == "Exercise corpus withdrawal invariants")
        self.assertEqual(regression["run"], "node --test scripts/check-corpus-shrink.test.mjs")
        self.assertNotIn("if", regression)
        self.assertNotIn("continue-on-error", regression)
        checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["fetch-depth"], 0)


if __name__ == "__main__":
    unittest.main()
