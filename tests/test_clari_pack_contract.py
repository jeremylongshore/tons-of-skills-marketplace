"""Regression contract for the public Clari operator pack."""

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "clari-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "clari-ci-integration",
    "clari-common-errors",
    "clari-core-workflow-a",
    "clari-core-workflow-b",
    "clari-cost-tuning",
    "clari-debug-bundle",
    "clari-deploy-integration",
    "clari-hello-world",
    "clari-install-auth",
    "clari-local-dev-loop",
    "clari-performance-tuning",
    "clari-prod-checklist",
    "clari-rate-limits",
    "clari-reference-architecture",
    "clari-sdk-patterns",
    "clari-security-basics",
    "clari-upgrade-migration",
    "clari-webhooks-events",
}


def frontmatter(body: str) -> dict:
    return yaml.safe_load(body.split("---", 2)[1])


class ClariPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {item.parent.name for item in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_reviewable_structure(self) -> None:
        headings: set[str] = set()
        descriptions: set[str] = set()
        required_sections = (
            "## Overview",
            "## Prerequisites",
            "## Instructions",
            "## Authentication",
            "## Tool Discipline",
            "## Output",
            "## Examples",
            "## Error Handling",
            "## Resources",
        )
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                metadata = frontmatter(body)
                self.assertEqual("2.0.0", metadata["version"])
                self.assertIn("Use when", metadata["description"])
                self.assertIn("Trigger with", metadata["description"])
                for section in required_sections:
                    self.assertIn(section, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))
                descriptions.add(re.sub(r"\s+", " ", metadata["description"]))

                references = list((skill_file.parent / "references").glob("*.md"))
                self.assertEqual(["official-docs.md"], [item.name for item in references])
                evidence = references[0].read_text(encoding="utf-8")
                self.assertIn("Consulted on 2026-09-13", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 3)
                self.assertIn(
                    "3fa7e772eebc3b2461fa12561a82520d4069668c2c35220c6f54fd0dbda1b5e1",
                    evidence,
                )
                self.assertIn(
                    "e971686786068874001b8491189e233e634403e46bd3576a896cf02fb21774e6",
                    evidence,
                )

        self.assertEqual(18, len(headings))
        self.assertEqual(18, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(self.manifest["description"], self.package["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(
            item for item in marketplace["plugins"] if item["name"] == "clari-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertGreaterEqual(entry["verification"]["score"], 90)
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsupported_contracts_do_not_return(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for unsupported in (
            "Clari does not provide real-time webhooks",
            "Copilot webhook integration",
            "CLARI_ORG_ID",
            "your-api-key-here",
            "v3 (deprecated)",
            "Slack alerts for forecast movements",
            "raw debug bundle",
            "unlimited requests",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for current in (
            "apikey",
            "partnerkey",
            "X-Api-Key",
            "X-Api-Password",
            "/admin/limits",
            "SCHEDULED",
            "STARTED",
            "DONE",
            "ABORTED",
            "/export/forecast/{forecastId}",
            "/export/activity",
            "/audit/events",
            "rest-api.copilot.clari.com",
            "100,000 requests per week",
            "reconciliation",
            "checkpoint",
            "rollback",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
