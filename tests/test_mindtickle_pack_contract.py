"""Regression contract for the public Mindtickle operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "mindtickle-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "mindtickle-ci-integration",
    "mindtickle-common-errors",
    "mindtickle-core-workflow-a",
    "mindtickle-core-workflow-b",
    "mindtickle-cost-tuning",
    "mindtickle-debug-bundle",
    "mindtickle-deploy-integration",
    "mindtickle-hello-world",
    "mindtickle-install-auth",
    "mindtickle-local-dev-loop",
    "mindtickle-performance-tuning",
    "mindtickle-prod-checklist",
    "mindtickle-rate-limits",
    "mindtickle-reference-architecture",
    "mindtickle-sdk-patterns",
    "mindtickle-security-basics",
    "mindtickle-upgrade-migration",
    "mindtickle-webhooks-events",
}


class MindticklePackContractTest(unittest.TestCase):
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

    def test_fabricated_mindtickle_contracts_do_not_return(self) -> None:
        corpus = "\n".join(path.read_text().lower() for path in self.skill_files)
        for invented in (
            "api.mindtickle.com",
            "developers.mindtickle.com",
            "company-id",
            "mindtickle_api_key",
            "mindtickle_webhook_secret",
            "x-mindtickle-signature",
            "/v2/webhooks",
            "30 req",
            "100 requests/min",
        ):
            with self.subTest(invented=invented):
                self.assertNotIn(invented, corpus)

    def test_contract_boundaries_are_explicit(self) -> None:
        corpus = "\n".join(path.read_text() for path in self.skill_files)
        lowered = corpus.lower()
        self.assertGreaterEqual(lowered.count("approval"), 18)
        self.assertGreaterEqual(lowered.count("tenant"), 90)
        self.assertGreaterEqual(lowered.count("synthetic"), 10)
        self.assertIn("Content, User, and Reporting APIs", corpus)
        self.assertIn("SCIM, SAML, and OpenID", corpus)
        self.assertIn("does not publish a universal webhook registration route", corpus)
        self.assertIn("does not publish universal endpoint quotas", corpus)

    def test_manifest_package_and_catalog_are_consistent(self) -> None:
        self.assertEqual("mindtickle-pack", self.manifest["name"])
        self.assertEqual(1, self.manifest["keywords"].count("mindtickle"))
        package = json.loads((PACK / "package.json").read_text())
        self.assertEqual(self.manifest["description"], package["description"])
        catalog = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(plugin for plugin in catalog["plugins"] if plugin["name"] == "mindtickle-pack")
        self.assertEqual(self.manifest["version"], entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual({"score": 94, "grade": "A", "badge": "gold"}, {
            key: entry["verification"][key] for key in ("score", "grade", "badge")
        })


if __name__ == "__main__":
    unittest.main()
