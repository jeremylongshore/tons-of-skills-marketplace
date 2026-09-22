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
