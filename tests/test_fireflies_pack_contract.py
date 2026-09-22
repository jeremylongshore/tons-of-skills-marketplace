"""Regression contract for the public Fireflies operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "fireflies-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "fireflies-ci-integration",
    "fireflies-common-errors",
    "fireflies-core-workflow-a",
    "fireflies-core-workflow-b",
    "fireflies-cost-tuning",
    "fireflies-data-handling",
    "fireflies-debug-bundle",
    "fireflies-deploy-integration",
    "fireflies-enterprise-rbac",
    "fireflies-hello-world",
    "fireflies-incident-runbook",
    "fireflies-install-auth",
    "fireflies-local-dev-loop",
    "fireflies-migration-deep-dive",
    "fireflies-multi-env-setup",
    "fireflies-observability",
    "fireflies-performance-tuning",
    "fireflies-prod-checklist",
    "fireflies-rate-limits",
    "fireflies-reference-architecture",
    "fireflies-sdk-patterns",
    "fireflies-security-basics",
    "fireflies-upgrade-migration",
    "fireflies-webhooks-events",
}


class FirefliesPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())
        self.expected_version = self.manifest["version"]

    def test_release_alignment_and_reviewable_structure(self) -> None:
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
                    "## Validation",
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
                self.assertIn("Reviewed 2026-09-12", reference_body)
                self.assertIn("docs.fireflies.ai/llms.txt", reference_body)
                self.assertIn("graphql-api/webhooks-v2", reference_body)
                self.assertGreaterEqual(reference_body.count("https://"), 18)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.12.0", self.expected_version)
        self.assertEqual(self.expected_version, self.package["version"])
        self.assertEqual(24, len(self.skill_files))
        self.assertIn("Webhooks V2", self.manifest["description"])

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(item for item in marketplace["plugins"] if item["name"] == "fireflies-pack")
        self.assertEqual(self.expected_version, entry["version"])
        self.assertEqual(24, entry["components"]["skills"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "FirefliesApp",
            "transcripts(title:",
            "organizer_email: $",
            "participant_email: $",
            'eventType": "Transcription completed"',
            "if (!process.env.FIREFLIES_WEBHOOK_SECRET) return true",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_security_and_api_contracts_are_explicit(self) -> None:
        client = (SKILLS / "fireflies-sdk-patterns" / "SKILL.md").read_text()
        self.assertIn("documents a GraphQL API", client)
        self.assertIn("operation name", client)

        search = (SKILLS / "fireflies-core-workflow-b" / "SKILL.md").read_text()
        for term in ("keyword", "organizers", "participants", "limit up to 50"):
            self.assertIn(term, search)

        webhooks = (SKILLS / "fireflies-webhooks-events" / "SKILL.md").read_text()
        for term in (
            "meeting.transcribed",
            "meeting.summarized",
            "X-Hub-Signature",
            "raw body",
            "10 seconds",
        ):
            self.assertIn(term, webhooks)

        access = (SKILLS / "fireflies-enterprise-rbac" / "SKILL.md").read_text()
        self.assertIn("admin or user", access)
        self.assertIn("at least one admin", access)
        self.assertIn("all-or-nothing", access)

        limits = (SKILLS / "fireflies-rate-limits" / "SKILL.md").read_text()
        for term in ("50 requests/day", "60 requests/minute", "3 requests per 20 minutes"):
            self.assertIn(term, limits)


if __name__ == "__main__":
    unittest.main()
