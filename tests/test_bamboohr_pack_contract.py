"""Regression contract for the public BambooHR operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "bamboohr-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "bamboohr-ci-integration",
    "bamboohr-common-errors",
    "bamboohr-core-workflow-a",
    "bamboohr-core-workflow-b",
    "bamboohr-cost-tuning",
    "bamboohr-debug-bundle",
    "bamboohr-deploy-integration",
    "bamboohr-hello-world",
    "bamboohr-install-auth",
    "bamboohr-local-dev-loop",
    "bamboohr-performance-tuning",
    "bamboohr-prod-checklist",
    "bamboohr-rate-limits",
    "bamboohr-reference-architecture",
    "bamboohr-sdk-patterns",
    "bamboohr-security-basics",
    "bamboohr-upgrade-migration",
    "bamboohr-webhooks-events",
}


class BambooHRPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())
        self.expected_version = self.manifest["version"]

    def test_all_skills_are_release_aligned_and_reviewable(self) -> None:
        headings = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("Use when", normalized)
                self.assertIn("Trigger with", normalized)
                for required in (
                    "## Prerequisites",
                    "## Current Contract",
                    "## Authentication",
                    "## Instructions",
                    "## Tool Discipline",
                    "## Approval Boundaries",
                    "## Output",
                    "## Error Handling",
                    "## Examples",
                    "## Resources",
                ):
                    self.assertIn(required, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("Evidence reviewed: 2026-09-11", reference_body)
                self.assertIn("BambooHR/bhr-api-python", reference_body)
                self.assertIn("BambooHR/bhr-api-php", reference_body)
                self.assertIn("public PyPI returned no matching distribution", reference_body)
                self.assertGreaterEqual(reference_body.count("https://"), 13)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_pack_metadata_is_version_and_scope_aligned(self) -> None:
        self.assertEqual("1.5.0", self.expected_version)
        self.assertEqual(self.expected_version, self.package["version"])
        self.assertEqual(18, len(self.skill_files))
        self.assertIn("Operator-grade", self.manifest["description"])
        self.assertIn("governed HR integrations", self.package["description"])

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(item for item in marketplace["plugins"] if item["name"] == "bamboohr-pack")
        self.assertEqual(self.expected_version, entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])

    def test_stale_or_fabricated_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "api.bamboohr.com/api/gateway.php",
            "npm install @bamboohr/sdk",
            "BAMBOOHR_WEBHOOK_SECRET",
            "X-BambooHR-Signature",
            "500 requests per hour",
            "API call volume does not directly affect your bill",
            "directory-response.json",
            "send the .tar.gz to support",
            "Deploy to Vercel, Fly.io, and Cloud Run",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_contract_and_safety_boundaries_are_explicit(self) -> None:
        auth = (SKILLS / "bamboohr-install-auth" / "SKILL.md").read_text()
        self.assertIn("OAuth 2.0", auth)
        self.assertIn("SDK does not persist refreshed tokens", auth)

        sdk = (SKILLS / "bamboohr-sdk-patterns" / "SKILL.md").read_text()
        self.assertIn("public PyPI did not", sdk)
        self.assertIn("bamboohr/api", sdk)
        self.assertIn("No official npm", sdk)

        data = (SKILLS / "bamboohr-core-workflow-a" / "SKILL.md").read_text()
        self.assertIn("POST /api/v2/datasets/{datasetName}/data", data)
        self.assertIn("Dataset v1 data calls are deprecated", data)

        retries = (SKILLS / "bamboohr-rate-limits" / "SKILL.md").read_text()
        self.assertIn("408, 429, 504, and 598", retries)
        self.assertIn("does not publish one universal numeric quota", retries)

        webhooks = (SKILLS / "bamboohr-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("only once", webhooks)
        self.assertIn("HMAC-SHA256", webhooks)
        self.assertIn("signature carrier/header", webhooks)

        diagnostics = (SKILLS / "bamboohr-debug-bundle" / "SKILL.md").read_text()
        self.assertIn("Do not create a broad tarball", diagnostics)
        self.assertIn("Do not retain the response body", diagnostics)


if __name__ == "__main__":
    unittest.main()
