"""Regression contract for the public OpenEvidence operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "openevidence-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "openevidence-ci-integration",
    "openevidence-common-errors",
    "openevidence-core-workflow-a",
    "openevidence-core-workflow-b",
    "openevidence-cost-tuning",
    "openevidence-data-handling",
    "openevidence-debug-bundle",
    "openevidence-deploy-integration",
    "openevidence-enterprise-rbac",
    "openevidence-hello-world",
    "openevidence-incident-runbook",
    "openevidence-install-auth",
    "openevidence-local-dev-loop",
    "openevidence-migration-deep-dive",
    "openevidence-multi-env-setup",
    "openevidence-observability",
    "openevidence-performance-tuning",
    "openevidence-prod-checklist",
    "openevidence-rate-limits",
    "openevidence-reference-architecture",
    "openevidence-sdk-patterns",
    "openevidence-security-basics",
    "openevidence-upgrade-migration",
    "openevidence-webhooks-events",
}


class OpenEvidencePackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.expected_version = manifest["version"]

    def test_all_skills_are_release_aligned_and_reviewable(self) -> None:
        headings = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn(
                    "allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit", body
                )
                for required in (
                    "Use when",
                    "Trigger with",
                    "argument-hint:",
                    "## Tool Discipline",
                    "## Current Contract",
                    "## Authentication",
                    "## Approval Boundaries",
                    "## Output",
                    "## Error Handling",
                    "## Examples",
                    "qualified",
                ):
                    self.assertIn(required, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("Evidence reviewed: 2026-09-11", reference_body)
                self.assertGreaterEqual(
                    reference_body.count("https://www.openevidence.com/"), 20
                )
                self.assertIn("https://trust.openevidence.com/", reference_body)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_fabricated_integration_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for fabricated in (
            "https://api.openevidence.com/v1",
            "https://api.dev.openevidence.com",
            "https://api.staging.openevidence.com",
            "OPENEVIDENCE_API_KEY",
            "pip install openevidence",
            "npm install @openevidence/sdk",
            "X-OpenEvidence-Signature",
            "100 requests per hour",
            "5x quota",
        ):
            with self.subTest(fabricated=fabricated):
                self.assertNotIn(fabricated, markdown)

    def test_guardrail_skills_reject_undocumented_interfaces(self) -> None:
        expected_phrases = {
            "openevidence-sdk-patterns": "do not publish an OpenEvidence SDK",
            "openevidence-webhooks-events": "No public OpenEvidence webhook endpoint",
            "openevidence-rate-limits": "No public numeric request limit",
            "openevidence-enterprise-rbac": "No public RBAC, SCIM",
            "openevidence-local-dev-loop": "does not publish a local runtime",
            "openevidence-migration-deep-dive": "replaced by OpenEvidence Snow",
        }
        for slug, phrase in expected_phrases.items():
            with self.subTest(skill=slug):
                body = (SKILLS / slug / "SKILL.md").read_text()
                self.assertIn(phrase, body)

    def test_clinical_and_data_boundaries_are_explicit(self) -> None:
        consult = (SKILLS / "openevidence-core-workflow-a" / "SKILL.md").read_text()
        self.assertIn("does not replace diagnosis or professional clinical judgment", consult)

        handling = (SKILLS / "openevidence-data-handling" / "SKILL.md").read_text()
        self.assertIn("applicable BAA or customer-specific agreement", handling)
        self.assertIn("recording notice and consent", handling)

        incident = (SKILLS / "openevidence-incident-runbook" / "SKILL.md").read_text()
        self.assertIn("clinical escalation or emergency procedure", incident)


if __name__ == "__main__":
    unittest.main()
