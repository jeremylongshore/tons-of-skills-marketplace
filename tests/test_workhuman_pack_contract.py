"""Regression contract for the public Workhuman operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "workhuman-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "workhuman-ci-integration",
    "workhuman-common-errors",
    "workhuman-core-workflow-a",
    "workhuman-core-workflow-b",
    "workhuman-cost-tuning",
    "workhuman-debug-bundle",
    "workhuman-deploy-integration",
    "workhuman-hello-world",
    "workhuman-install-auth",
    "workhuman-local-dev-loop",
    "workhuman-performance-tuning",
    "workhuman-prod-checklist",
    "workhuman-rate-limits",
    "workhuman-reference-architecture",
    "workhuman-sdk-patterns",
    "workhuman-security-basics",
    "workhuman-upgrade-migration",
    "workhuman-webhooks-events",
}


class WorkhumanPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.expected_version = self.manifest["version"]

    def test_release_metadata_and_distinct_workflows(self) -> None:
        headings = set()
        descriptions = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn("allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit", body)
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                for section in (
                    "## Tool Discipline",
                    "## Current Contract",
                    "## Authentication",
                    "## Approval Boundaries",
                    "## Output",
                    "## Error Handling",
                    "## Example",
                ):
                    self.assertIn(section, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                description = re.search(r"^description: (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                self.assertIsNotNone(description)
                headings.add(heading.group(1))
                descriptions.add(description.group(1))

        self.assertEqual(len(self.skill_files), len(headings))
        self.assertEqual(len(self.skill_files), len(descriptions))

    def test_fabricated_public_contracts_do_not_return(self) -> None:
        corpus = "\n".join(path.read_text().lower() for path in self.skill_files)
        for invented in (
            "workhuman_base_url",
            "workhuman_client_secret",
            "/oauth/token",
            "/api/v1/recognitions",
            "/api/v1/rewards/redeem",
            "x-workhuman-signature",
            "bronze, silver, gold, platinum",
            "pending_approval -> approved -> delivered",
            "100 requests/min",
        ):
            with self.subTest(invented=invented):
                self.assertNotIn(invented, corpus)

    def test_contract_boundaries_are_explicit(self) -> None:
        corpus = "\n".join(path.read_text() for path in self.skill_files)
        lowered = corpus.lower()
        self.assertGreaterEqual(lowered.count("approval"), 18)
        self.assertGreaterEqual(lowered.count("customer"), 80)
        self.assertGreaterEqual(lowered.count("synthetic"), 12)
        self.assertIn("certified, prebuilt, bidirectional Workday integration", corpus)
        self.assertIn("does not publish a universal webhook registration route", corpus)
        self.assertIn("do not publish universal request-per-minute limits", corpus)
        self.assertIn("ISO 27001:2022 and ISO 27701:2019", corpus)

    def test_manifest_package_and_catalog_are_consistent(self) -> None:
        self.assertEqual("workhuman-pack", self.manifest["name"])
        self.assertEqual(1, self.manifest["keywords"].count("workhuman"))
        package = json.loads((PACK / "package.json").read_text())
        self.assertEqual(self.manifest["description"], package["description"])
        catalog = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(plugin for plugin in catalog["plugins"] if plugin["name"] == "workhuman-pack")
        self.assertEqual(self.manifest["version"], entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual({"score": 93, "grade": "A", "badge": "gold"}, {
            key: entry["verification"][key] for key in ("score", "grade", "badge")
        })


if __name__ == "__main__":
    unittest.main()
