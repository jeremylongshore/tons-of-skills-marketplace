"""Historical identity migration must preserve debt rather than recapture it."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/migrate-marketplace-section-identities.py"
SPEC = importlib.util.spec_from_file_location("section_identity_migration", SCRIPT)
migration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(migration)


class SectionIdentityMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.com")
        validator = self.root / migration.VALIDATOR_PATH
        validator.parent.mkdir()
        validator.write_bytes((ROOT / migration.VALIDATOR_PATH).read_bytes())
        self.skill_path = "plugins/example/skills/example/SKILL.md"
        self.skill = self.root / self.skill_path
        self.skill.parent.mkdir(parents=True)
        catalog = self.root / ".claude-plugin/marketplace.extended.json"
        catalog.parent.mkdir()
        catalog.write_text(json.dumps({"plugins": [{"name": "example", "source": "./plugins/example/skills"}]}))
        self.skill.write_text(
            "---\nname: example\ndescription: A historical fixture.\n---\n## Examples\n", encoding="utf-8"
        )
        self.git("add", ".")
        self.git("commit", "-qm", "historical capture source")
        self.source_sha = self.git("rev-parse", "HEAD").strip()
        self.baseline = {
            "$comment": "Existing baseline policy",
            "schema_version": "4.1.0",
            "generated_from": {"sha": self.source_sha, "run_id": "123", "captured_at": "2026-08-27T00:00:00Z"},
            "corpus_definition": "resolveCorpus('graded')",
            "corpus": {"skill_files": 1, "agent_files": 0, "command_files": 0, "plugin_dirs": 1},
            "rule_inventory": [migration.SECTION_RULE, "E-MISSING-REQUIRED-FIELD"],
            "entries": [
                f"{self.skill_path} :: {migration.SECTION_RULE} :: #",
                f"{self.skill_path} :: {migration.SECTION_RULE} :: ##",
                f"{self.skill_path} :: E-MISSING-REQUIRED-FIELD :: author",
            ],
            "totals": {"errors": 18, "grade_A_plus_B": 0, "grade_A_plus_B_pct": 0.0},
        }

    def git(self, *arguments):
        return subprocess.check_output(["git", *arguments], cwd=self.root, text=True)

    def migrate(self, baseline=None):
        return migration.migrate(self.root, json.dumps(baseline or self.baseline).encode(), run_id="456")

    def run_capture_step(self, mode, baseline):
        baseline_file = self.root / migration.BASELINE_PATH
        baseline_file.write_text(json.dumps(baseline), encoding="utf-8")
        (self.root / "scripts/migrate-marketplace-section-identities.py").write_bytes(SCRIPT.read_bytes())
        for name in ("corpus-resolver.mjs", "plugin-provenance.mjs", "publication-policy.cjs"):
            (self.root / "scripts" / name).write_bytes((ROOT / "scripts" / name).read_bytes())
        workflow = yaml.safe_load((ROOT / ".github/workflows/capture-marketplace-compliance-baseline.yml").read_text())
        step = next(
            step
            for step in workflow["jobs"]["capture"]["steps"]
            if step.get("name") == "Emit the triple-keyed marketplace baseline"
        )
        result = subprocess.run(
            ["bash", "-c", step["run"]],
            cwd=self.root,
            env={**os.environ, "CAPTURE_MODE": mode, "RUNNER_TEMP": str(self.root), "GITHUB_RUN_ID": "456"},
            capture_output=True,
            text=True,
        )
        return result, json.loads(baseline_file.read_text())

    def test_original_debt_expands_without_grandfathering_current_missing_section(self):
        # Examples existed at capture but is now missing. Live debt must not be
        # used as the source of the migrated accepted-debt set.
        self.skill.write_text("---\nname: example\ndescription: Current fixture.\n---\n# Example\n", encoding="utf-8")
        result = self.migrate()
        sections = {entry.rsplit(" :: ", 1)[1] for entry in result["entries"] if migration.SECTION_RULE in entry}
        self.assertEqual(
            sections,
            {
                "#",
                "## Overview",
                "## Prerequisites",
                "## Instructions",
                "## Output",
                "## Error Handling",
                "## Resources",
            },
        )
        self.assertNotIn("## Examples", sections)
        self.assertEqual(result["finding_identity_version"], 2)
        self.assertEqual(result["generated_from"]["run_id"], "456")
        self.assertEqual(result["generated_from"]["sha"], self.source_sha)
        self.assertEqual(result["identity_migration"]["prior_generated_from"], self.baseline["generated_from"])
        self.assertEqual(result["corpus_source_sha"], self.source_sha)
        self.assertEqual(result["totals"]["errors"] - len(result["entries"]), 15)
        self.assertIsNone(result["identity_migration"]["historical_raw_error_occurrences"])
        self.assertNotIn("raw_error_occurrences", result["totals"])
        for key in ("$comment", "schema_version", "corpus_definition", "corpus", "rule_inventory"):
            self.assertEqual(result[key], self.baseline[key])
        self.assertEqual(result["totals"]["grade_A_plus_B_pct"], self.baseline["totals"]["grade_A_plus_B_pct"])
        self.assertEqual(
            {entry for entry in result["entries"] if migration.SECTION_RULE not in entry},
            {entry for entry in self.baseline["entries"] if migration.SECTION_RULE not in entry},
        )
        with self.assertRaisesRegex(ValueError, "unmigrated"):
            self.migrate(result)

    def test_previously_removed_historical_title_key_is_not_resurrected(self):
        baseline = copy.deepcopy(self.baseline)
        baseline["entries"] = [entry for entry in baseline["entries"] if not entry.endswith(" :: #")]
        result = self.migrate(baseline)
        self.assertNotIn(f"{self.skill_path} :: {migration.SECTION_RULE} :: #", result["entries"])
        self.assertEqual(result["identity_migration"]["prior_section_identities"], 1)

    def test_missing_historical_blob_refuses_instead_of_using_live_source(self):
        baseline = copy.deepcopy(self.baseline)
        baseline["entries"][0] = "plugins/missing/skills/missing/SKILL.md :: E-MISSING-REQUIRED-SECTION :: #"
        with self.assertRaisesRegex(ValueError, "regular tracked file"):
            self.migrate(baseline)

    def test_historical_symlink_is_not_treated_as_skill_content(self):
        self.skill.unlink()
        self.skill.symlink_to("other.md")
        self.git("add", ".")
        self.git("commit", "-qm", "historical symlink")
        baseline = copy.deepcopy(self.baseline)
        baseline["generated_from"]["sha"] = self.git("rev-parse", "HEAD").strip()
        with self.assertRaisesRegex(ValueError, "regular tracked file"):
            self.migrate(baseline)

    def test_historical_module_is_parsed_without_executing_its_top_level_code(self):
        validator = self.root / migration.VALIDATOR_PATH
        source = validator.read_text()
        validator.write_text(source + '\nPath(__file__).with_name("historical-executed").write_text("unsafe")\n')
        self.git("add", ".")
        self.git("commit", "-qm", "historical executable sentinel")
        baseline = copy.deepcopy(self.baseline)
        baseline["generated_from"]["sha"] = self.git("rev-parse", "HEAD").strip()
        validator.write_text(source)
        self.git("add", ".")
        self.git("commit", "-qm", "current validator has no sentinel")
        candidate = self.migrate(baseline)
        self.assertEqual(candidate["finding_identity_version"], 2)
        self.assertFalse(validator.with_name("historical-executed").exists())

    def test_repo_root_cannot_supply_unreviewed_executable_validator_code(self):
        validator = self.root / migration.VALIDATOR_PATH
        validator.write_text(
            validator.read_text() + '\nPath(__file__).with_name("current-executed").write_text("unsafe")\n'
        )
        with self.assertRaisesRegex(ValueError, "reviewed migration tool"):
            self.migrate()
        self.assertFalse(validator.with_name("current-executed").exists())

    def test_pinned_section_not_missing_at_capture_refuses(self):
        self.skill.write_text("---\nname: example\ndescription: Fixture.\n---\n# Present title\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "title present")
        baseline = copy.deepcopy(self.baseline)
        baseline["generated_from"]["sha"] = self.git("rev-parse", "HEAD").strip()
        with self.assertRaisesRegex(ValueError, "not reproduced"):
            self.migrate(baseline)

    def test_semantic_drift_refuses_without_executing_historical_source(self):
        validator = self.root / migration.VALIDATOR_PATH
        source = validator.read_text()
        for old, new in (
            ('"## Resources",', '"## Changed Resources",'),
            ("target = heading.strip().lower()", "target = heading.strip().upper()"),
            ("data = yaml.safe_load(front_str) or {}", 'data = yaml.safe_load(front_str) or {"changed": True}'),
        ):
            with self.subTest(old=old):
                self.assertIn(old, source)
                validator.write_text(source.replace(old, new, 1))
                with self.assertRaisesRegex(ValueError, "semantics differ"):
                    self.migrate()
        validator.write_text(source)

    def test_malformed_version_paths_counts_or_duplicate_entries_refuse(self):
        candidates = []
        for version in (True, "1", 2, 3):
            candidates.append({**self.baseline, "finding_identity_version": version})
        candidates.append({**self.baseline, "entries": self.baseline["entries"] * 2})
        candidates.append({**self.baseline, "totals": {"errors": True}})
        candidates.append({**self.baseline, "totals": {"errors": 0}})
        candidates.append({**self.baseline, "totals": {"errors": 18, "raw_error_occurrences": 18}})
        for path in ("/tmp/SKILL.md", "plugins/../SKILL.md", "plugins/x/skills/x/other.md"):
            candidates.append({**self.baseline, "entries": [f"{path} :: {migration.SECTION_RULE} :: ##"]})
        for baseline in candidates:
            with self.subTest(baseline=baseline), self.assertRaises(ValueError):
                self.migrate(baseline)

    def test_actual_capture_step_migrates_historical_debt_without_capturing_live_debt(self):
        self.skill.write_text("---\nname: example\ndescription: Current fixture.\n---\n# Example\n", encoding="utf-8")
        result, candidate = self.run_capture_step("historical-section-identities-v2", self.baseline)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(candidate["finding_identity_version"], 2)
        self.assertEqual(candidate["generated_from"]["run_id"], "456")
        self.assertNotIn(f"{self.skill_path} :: {migration.SECTION_RULE} :: ## Examples", candidate["entries"])
        self.assertEqual(candidate["totals"]["errors"] - len(candidate["entries"]), 15)

    def test_failed_capture_step_never_truncates_or_replaces_pinned_baseline(self):
        for mode, baseline in (
            ("unknown", self.baseline),
            ("capture", {**self.baseline, "finding_identity_version": True}),
            ("historical-section-identities-v2", {**self.baseline, "finding_identity_version": 2}),
        ):
            with self.subTest(mode=mode):
                result, after = self.run_capture_step(mode, baseline)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(after, baseline)

    def test_full_capture_preserves_pinned_identity_version_after_migration(self):
        baseline = self.migrate()
        result, candidate = self.run_capture_step("capture", baseline)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(candidate["finding_identity_version"], 2)
        self.assertIn(f"{self.skill_path} :: {migration.SECTION_RULE} :: ## Overview", candidate["entries"])
        self.assertNotIn(f"{self.skill_path} :: {migration.SECTION_RULE} :: ##", candidate["entries"])
        self.assertIsInstance(candidate["totals"]["raw_error_occurrences"], int)

    def test_r3_uses_original_corpus_source_after_new_owner_transaction(self):
        new_skill = self.skill.parent.parent / "new/SKILL.md"
        new_skill.parent.mkdir()
        new_skill.write_text("---\nname: new\ndescription: A later fixture.\n---\n# New\n")
        self.git("add", ".")
        self.git("commit", "-qm", "new protected source with two skills")
        candidate = self.migrate()
        self.assertNotEqual(candidate["generated_from"]["sha"], self.source_sha)
        spec = importlib.util.spec_from_file_location(
            "section_migration_ratchet", ROOT / "scripts/check-marketplace-compliance-baseline.py"
        )
        ratchet = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ratchet)
        current = {"corpus": {"skill_files": 2}}
        evidence = ratchet.corpus_shrink_evidence(candidate, current, self.root)
        self.assertTrue(evidence["allowed"])
        self.assertEqual(evidence["baseline_sha"], self.source_sha)
        self.assertEqual(evidence["baseline_count"], 1)
        for forged in (
            {**candidate, "corpus_source_sha": candidate["generated_from"]["sha"]},
            {**candidate, "finding_identity_version": True},
            {**candidate, "identity_migration": {}},
        ):
            with self.subTest(forged=forged), self.assertRaisesRegex(ValueError, "historical corpus source"):
                ratchet.corpus_shrink_evidence(forged, current, self.root)

        self.assertIn(
            "unknown policy-envelope fields changed", ratchet.capture_required_reasons(self.baseline, candidate)
        )
        self.assertIn(
            "owner-dispatched capture artifact",
            ratchet.baseline_growth_error(
                self.baseline,
                candidate,
                {migration.BASELINE_PATH},
                "automation/compliance-baseline-456",
            ),
        )
        self.assertIn(
            "one-file baseline-only",
            ratchet.baseline_growth_error(
                self.baseline,
                candidate,
                {migration.BASELINE_PATH, migration.VALIDATOR_PATH},
                "automation/compliance-baseline-456",
                capture_authorized=True,
            ),
        )


if __name__ == "__main__":
    unittest.main()
