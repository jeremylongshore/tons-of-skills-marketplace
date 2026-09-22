"""Regression contract for the public Algolia operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "algolia-pack"
SKILLS = PACK / "skills"


class AlgoliaPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(24, len(self.skill_files))
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.expected_version = manifest["version"]

    def test_all_skills_have_release_metadata_and_official_references(self) -> None:
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("## Tool Discipline", body)
                self.assertIn("## Current Contract", body)
                self.assertIn("## Authentication", body)
                self.assertIn("## Approval Boundaries", body)
                self.assertIn("## Examples", body)

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("Checked on 2026-09-10", reference_body)
                self.assertGreaterEqual(reference_body.count("https://www.algolia.com"), 3)

    def test_stale_or_unsafe_claims_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text(encoding="utf-8") for path in PACK.rglob("*.md"))
        for stale in (
            "Pricing Structure (2025)",
            "indexing operations are free",
            "typically delivers search in < 50ms globally",
            "true Algolia outages are rare",
            "Insights API is built into the algoliasearch client",
            "Every Algolia account has three default keys",
            "Use Admin key",
            "built-in retry handles",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

        self.assertNotRegex(markdown, re.compile(r"npm install .*@(?:latest|next)"))

    def test_current_operator_boundaries_are_preserved(self) -> None:
        upgrade = (SKILLS / "algolia-upgrade-migration" / "SKILL.md").read_text()
        self.assertIn("Version 5 removes `initIndex`", upgrade)
        self.assertIn("wait helpers", upgrade)

        events = (SKILLS / "algolia-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("dedicated `search-insights` client", events)
        self.assertIn("source-to-index updates", events)

        cost = (SKILLS / "algolia-cost-tuning" / "SKILL.md").read_text()
        self.assertIn("avoids embedding plan names, prices", cost)
        self.assertIn("current invoice", cost)

        performance = (SKILLS / "algolia-performance-tuning" / "SKILL.md").read_text()
        self.assertIn("application's SLO", performance)
        self.assertIn("same harness", performance)


if __name__ == "__main__":
    unittest.main()

