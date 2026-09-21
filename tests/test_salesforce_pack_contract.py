"""Regression contract for the public Salesforce operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "salesforce-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "salesforce-advanced-troubleshooting",
    "salesforce-architecture-variants",
    "salesforce-ci-integration",
    "salesforce-common-errors",
    "salesforce-core-workflow-a",
    "salesforce-core-workflow-b",
    "salesforce-cost-tuning",
    "salesforce-data-handling",
    "salesforce-debug-bundle",
    "salesforce-deploy-integration",
    "salesforce-enterprise-rbac",
    "salesforce-hello-world",
    "salesforce-incident-runbook",
    "salesforce-install-auth",
    "salesforce-known-pitfalls",
    "salesforce-load-scale",
    "salesforce-local-dev-loop",
    "salesforce-migration-deep-dive",
    "salesforce-multi-env-setup",
    "salesforce-observability",
    "salesforce-performance-tuning",
    "salesforce-policy-guardrails",
    "salesforce-prod-checklist",
    "salesforce-rate-limits",
    "salesforce-reference-architecture",
    "salesforce-reliability-patterns",
    "salesforce-sdk-patterns",
    "salesforce-security-basics",
    "salesforce-upgrade-migration",
    "salesforce-webhooks-events",
}


class SalesforcePackContractTest(unittest.TestCase):
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

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        corpus = "\n".join(path.read_text() for path in self.skill_files)
        lowered = corpus.lower()
        for stale in (
            "/services/data/v59.0",
            "username-password flow",
            "sf_jwt_key",
            "all use the cometd",
            "v55.0 to v59.0",
            "api limit headroom > 20%",
            "api limit warning | > 80%",
            "new connected app configured",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, lowered)

    def test_current_contract_boundaries_are_explicit(self) -> None:
        corpus = "\n".join(path.read_text() for path in self.skill_files)
        lowered = corpus.lower()
        self.assertGreaterEqual(lowered.count("approval"), 30)
        self.assertGreaterEqual(lowered.count("reconcile"), 30)
        self.assertGreaterEqual(lowered.count("synthetic"), 25)
        self.assertIn("Creating Connected Apps is restricted as of Spring '26", corpus)
        self.assertIn("Pub/Sub API uses gRPC over HTTP/2 and Avro", corpus)
        self.assertIn("can lag consumption by up to five minutes", corpus)
        self.assertIn("query explain is Beta", corpus)
        self.assertIn("versions 21.0 through 30.0 are unavailable", corpus)

    def test_manifest_package_and_catalog_are_consistent(self) -> None:
        self.assertEqual("salesforce-pack", self.manifest["name"])
        self.assertEqual(1, self.manifest["keywords"].count("salesforce"))
        package = json.loads((PACK / "package.json").read_text())
        self.assertEqual(self.manifest["description"], package["description"])
        catalog = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(plugin for plugin in catalog["plugins"] if plugin["name"] == "salesforce-pack")
        self.assertEqual(self.manifest["version"], entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(
            {"score": 94, "grade": "A", "badge": "gold"},
            {key: entry["verification"][key] for key in ("score", "grade", "badge")},
        )


if __name__ == "__main__":
    unittest.main()
