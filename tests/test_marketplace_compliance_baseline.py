"""Focused tests for the E6.1 marketplace compliance baseline emitter."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-skills-schema.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skills_schema_baseline", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarketplaceComplianceBaselineTests(unittest.TestCase):
    def test_version_two_distinguishes_new_section_debt_from_real_body_diagnostics(self):
        validator = load_validator()
        path = "plugins/example/skills/example/SKILL.md"

        def section_errors(missing):
            body = "# Example\n\n" + "\n\n".join(
                section
                + "\n\nInspect the supplied input, record the observed result, and preserve unresolved evidence."
                for section in validator.RECOMMENDED_SECTIONS
                if section != "# " and section not in missing
            )
            errors, _, _ = validator.validate_body(Path(path), body, validator.TIER_MARKETPLACE)
            return [error for error in errors if "Required section missing:" in error]

        before = section_errors({"## Overview"})
        after = section_errors({"## Overview", "## Examples"})
        self.assertEqual((len(before), len(after)), (1, 2))
        # Reproduce the pinned legacy collision; do not silently change its policy.
        self.assertEqual(
            {validator.baseline_finding_triple(path, error) for error in before},
            {validator.baseline_finding_triple(path, error) for error in after},
        )
        old = {validator.baseline_finding_triple(path, error, identity_version=2) for error in before}
        new = {validator.baseline_finding_triple(path, error, identity_version=2) for error in after}
        self.assertEqual(new - old, {(path, "E-MISSING-REQUIRED-SECTION", "## Examples")})
        spec = importlib.util.spec_from_file_location(
            "section_identity_ratchet", ROOT / "scripts" / "check-marketplace-compliance-baseline.py"
        )
        ratchet = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ratchet)
        self.assertEqual(
            ratchet.compare(
                {"entries": [" :: ".join(triple) for triple in old]},
                {"entries": [" :: ".join(triple) for triple in new]},
            ),
            [f"{path} :: E-MISSING-REQUIRED-SECTION :: ## Examples"],
        )

    def test_version_two_preserves_multiword_sections_and_title_identity(self):
        validator = load_validator()
        for section in ("## Error Handling", "## Prerequisites", "# "):
            with self.subTest(section=section):
                self.assertEqual(
                    validator.baseline_finding_triple(
                        "example/SKILL.md", f"[body] Required section missing: '{section}'", identity_version=2
                    ),
                    ("example/SKILL.md", "E-MISSING-REQUIRED-SECTION", section.strip()),
                )
        for version in (True, 0, 3, "2"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                validator.baseline_finding_triple("example/SKILL.md", "error", identity_version=version)
        with self.assertRaises(ValueError):
            validator.baseline_finding_triple(
                "example/SKILL.md", "[body] Required section missing: ## Examples", identity_version=2
            )

    def test_version_two_payload_separates_occurrences_from_unique_identities(self):
        validator = load_validator()
        arguments = dict(
            findings=[("a/SKILL.md", "E-MISSING-REQUIRED-SECTION", "## Overview")] * 2
            + [("a/SKILL.md", "E-MISSING-REQUIRED-SECTION", "## Examples")],
            skill_files=1,
            command_files=0,
            plugin_dirs=1,
            agent_files=0,
            grade_a_plus_b=0,
            repo_root=ROOT,
        )
        legacy = validator.marketplace_baseline_payload(**arguments)
        self.assertNotIn("finding_identity_version", legacy)
        self.assertNotIn("raw_error_occurrences", legacy["totals"])
        payload = validator.marketplace_baseline_payload(**arguments, finding_identity_version=2)
        self.assertEqual(payload["finding_identity_version"], 2)
        self.assertEqual(payload["totals"]["errors"], 2)
        self.assertEqual(payload["totals"]["raw_error_occurrences"], 3)
        arguments["findings"] = [("a/SKILL.md", "E-MISSING-REQUIRED-SECTION", "##")]
        with self.assertRaises(ValueError):
            validator.marketplace_baseline_payload(**arguments, finding_identity_version=2)

    def test_common_finding_shapes_have_readable_stable_triples(self):
        validator = load_validator()
        path = "plugins/example/skills/example/SKILL.md"
        self.assertEqual(
            validator.baseline_finding_triple(path, "[frontmatter] Missing required field: 'tags' (marketplace)"),
            (path, "E-MISSING-REQUIRED-FIELD", "tags"),
        )
        self.assertEqual(
            validator.baseline_finding_triple(path, "[body] Required section missing: 'Overview' (marketplace tier)"),
            (path, "E-MISSING-REQUIRED-SECTION", "Overview"),
        )

    def test_payload_is_sorted_triple_keyed_and_carries_required_metadata(self):
        validator = load_validator()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".git").mkdir()
            payload = validator.marketplace_baseline_payload(
                findings=[
                    ("z/SKILL.md", "E-SECOND", "b"),
                    ("a/SKILL.md", "E-FIRST", "a"),
                    ("a/SKILL.md", "E-FIRST", "a"),
                ],
                skill_files=4,
                command_files=5,
                plugin_dirs=2,
                agent_files=3,
                grade_a_plus_b=3,
                repo_root=root,
            )
        self.assertEqual(payload["schema_version"], validator.SCHEMA_VERSION)
        self.assertEqual(payload["corpus_definition"], "resolveCorpus('graded')")
        self.assertEqual(
            payload["corpus"],
            {"skill_files": 4, "command_files": 5, "plugin_dirs": 2, "agent_files": 3},
        )
        self.assertEqual(payload["totals"]["errors"], 2)
        self.assertEqual(payload["totals"]["grade_A_plus_B_pct"], 75.0)
        self.assertEqual(
            payload["rule_inventory"],
            sorted(validator.DECLARED_MARKETPLACE_RULE_INVENTORY | {"E-FIRST", "E-SECOND"}),
        )
        self.assertEqual(
            payload["entries"],
            ["a/SKILL.md :: E-FIRST :: a", "z/SKILL.md :: E-SECOND :: b"],
        )
        self.assertIn("sha", payload["generated_from"])
        self.assertIn("captured_at", payload["generated_from"])

    def test_emit_baseline_refuses_partial_or_standard_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--emit-baseline", "--standard", "--repo-root", str(root)],
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires a full --marketplace corpus run", result.stderr)

    def test_identity_version_flag_requires_baseline_mode_and_known_contract(self):
        for arguments in (
            ["--baseline-identity-version", "2"],
            ["--emit-baseline", "--baseline-identity-version", "3"],
        ):
            with self.subTest(arguments=arguments):
                result = subprocess.run([sys.executable, str(SCRIPT), *arguments], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")

    def test_version_two_empty_emitter_declares_zero_occurrences(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plugins").mkdir()
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--emit-baseline",
                    "--baseline-identity-version",
                    "2",
                    "--repo-root",
                    str(root),
                ],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["finding_identity_version"], 2)
        self.assertEqual(payload["totals"]["raw_error_occurrences"], 0)
        self.assertEqual(payload["entries"], [])

    def test_emit_baseline_is_json_when_run_against_an_empty_marketplace_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plugins").mkdir()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--emit-baseline", "--repo-root", str(root)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["entries"], [])
        self.assertEqual(payload["totals"]["errors"], 0)
        self.assertTrue(payload["rule_inventory"])
        self.assertIn("E-FRONTMATTER-a84c0ab5ddff", payload["rule_inventory"])

    def test_emit_baseline_is_json_when_findings_are_present(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "plugins" / "example" / "skills" / "example" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(
                "---\n"
                "name: example\n"
                "description: A deliberately incomplete fixture for baseline output tests.\n"
                "---\n"
                "# Example\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--emit-baseline", "--repo-root", str(root)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreater(payload["totals"]["errors"], 0)
        self.assertTrue(payload["entries"])

    def test_emit_baseline_covers_commands_agents_and_manifests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / "plugins" / "example"
            (plugin / "commands").mkdir(parents=True)
            (plugin / "agents").mkdir()
            (plugin / ".claude-plugin").mkdir()
            (plugin / "commands" / "broken.md").write_text("not frontmatter\n", encoding="utf-8")
            (plugin / "agents" / "broken.md").write_text("not frontmatter\n", encoding="utf-8")
            (plugin / ".claude-plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--emit-baseline", "--repo-root", str(root)],
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        paths = {entry.split(" :: ", 1)[0] for entry in payload["entries"]}
        self.assertIn("plugins/example/commands/broken.md", paths)
        self.assertIn("plugins/example/agents/broken.md", paths)
        self.assertIn("plugins/example/.claude-plugin/plugin.json", paths)
        self.assertEqual(payload["corpus"]["command_files"], 1)


if __name__ == "__main__":
    unittest.main()
