"""Regression contract for the reviewed publishing-skills projection."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "productivity" / "publishing-skills"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "blog-editorial-calendar": "1.1.0",
    "blog-figure-svg": "1.2.0",
    "blog-topic-research": "1.2.0",
    "seo-blog-writer": "2.3.0",
}


class PublishingSkillsContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(set(EXPECTED_SKILLS), {path.parent.name for path in self.skill_files})

    def test_marketplace_contract_and_bounded_size(self) -> None:
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertLessEqual(len(body.splitlines()), 500)
                self.assertIn(f"version: {EXPECTED_SKILLS[skill_file.parent.name]}", body)
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                self.assertNotIn("\nemoji:", body)
                self.assertNotIn("\nhomepage:", body)
                self.assertNotRegex(body, r"^allowed-tools:.*(?:^|, )Bash(?:,|$)")
                for section in (
                    "## Overview",
                    "## Prerequisites",
                    "## Tool Discipline",
                    "## Instructions",
                    "## Approval Boundaries",
                    "## Output",
                    "## Error Handling",
                    "## Examples",
                    "## Verification",
                    "## Resources",
                ):
                    self.assertIn(section, body)

    def test_workflows_are_distinct_and_safety_bounded(self) -> None:
        headings = set()
        descriptions = set()
        corpus = ""
        for skill_file in self.skill_files:
            body = skill_file.read_text(encoding="utf-8")
            corpus += body
            heading = re.search(r"^# (.+)$", body, re.MULTILINE)
            description = re.search(r"^description: (.+)$", body, re.MULTILINE)
            self.assertIsNotNone(heading)
            self.assertIsNotNone(description)
            headings.add(heading.group(1))
            descriptions.add(description.group(1))

        self.assertEqual(4, len(headings))
        self.assertEqual(4, len(descriptions))
        for contract in (
            "owner approval",
            "never",
            "credentials",
            "current",
            "verification",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, corpus.lower())

    def test_product_specific_guardrails(self) -> None:
        calendar = (SKILLS / "blog-editorial-calendar" / "SKILL.md").read_text()
        figure = (SKILLS / "blog-figure-svg" / "SKILL.md").read_text()
        research = (SKILLS / "blog-topic-research" / "SKILL.md").read_text()
        writer = (SKILLS / "seo-blog-writer" / "SKILL.md").read_text()

        self.assertIn("Selection must be deterministic", calendar)
        self.assertIn("no scripts, event handlers, remote images", figure)
        self.assertIn("never search volume", research)
        self.assertIn("default is local draft output", writer)
        self.assertIn("Structured data must describe visible page content", writer)

    def test_manifest_package_and_catalog_are_consistent(self) -> None:
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        package = json.loads((PACK / "package.json").read_text())
        catalog = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(plugin for plugin in catalog["plugins"] if plugin["name"] == "publishing-skills")

        self.assertEqual("0.2.0", manifest["version"])
        self.assertEqual(manifest["version"], package["version"])
        self.assertEqual(manifest["version"], entry["version"])
        self.assertEqual(manifest["description"], package["description"])
        self.assertEqual(manifest["description"], entry["description"])
        self.assertEqual(
            {"score": 95, "grade": "A", "badge": "gold"},
            {key: entry["verification"][key] for key in ("score", "grade", "badge")},
        )


if __name__ == "__main__":
    unittest.main()
