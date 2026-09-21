"""Regression contract for the public Instantly API v2 operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "instantly-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "instantly-ci-integration",
    "instantly-common-errors",
    "instantly-core-workflow-a",
    "instantly-core-workflow-b",
    "instantly-cost-tuning",
    "instantly-data-handling",
    "instantly-debug-bundle",
    "instantly-deploy-integration",
    "instantly-enterprise-rbac",
    "instantly-hello-world",
    "instantly-incident-runbook",
    "instantly-install-auth",
    "instantly-local-dev-loop",
    "instantly-migration-deep-dive",
    "instantly-multi-env-setup",
    "instantly-observability",
    "instantly-performance-tuning",
    "instantly-prod-checklist",
    "instantly-rate-limits",
    "instantly-reference-architecture",
    "instantly-sdk-patterns",
    "instantly-security-basics",
    "instantly-upgrade-migration",
    "instantly-webhooks-events",
}


class InstantlyPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.expected_version = manifest["version"]

    def test_all_skills_have_release_metadata_and_official_references(self) -> None:
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
                    "## Error Handling",
                    "## Examples",
                ):
                    self.assertIn(required, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("2026-09-11", reference_body)
                self.assertGreaterEqual(reference_body.count("https://"), 13)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_stale_or_invented_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "developer.instantly.ai/_mock/api/v2",
            "$97.95",
            "3 retries in 30s",
            "INSTANTLY_WEBHOOK_SECRET",
            "X-Webhook-Secret",
            "Bash(npm:",
            "developer.instantly.ai/api/v2/schemas",
            "varies by plan",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_instantly_contracts_are_preserved(self) -> None:
        references = (
            SKILLS / "instantly-install-auth" / "references" / "official-docs.md"
        ).read_text()
        self.assertIn("100 requests/second", references)
        self.assertIn("6,000 requests/minute", references)
        self.assertIn("`@instantlyai/sdk`", references)
        self.assertIn("`1.0.0-beta.1`", references)
        self.assertIn("`@instantlyai/cli`", references)
        self.assertIn("`0.2.7`", references)

        migration = (SKILLS / "instantly-migration-deep-dive" / "SKILL.md").read_text()
        self.assertIn("deprecated on January 19, 2026", migration)
        self.assertIn("not compatible with v1 keys", migration)

        rate_limits = (SKILLS / "instantly-rate-limits" / "SKILL.md").read_text()
        self.assertIn("100 requests per second", rate_limits)
        self.assertIn("6,000 per minute", rate_limits)
        self.assertIn("20 requests per minute", rate_limits)

        webhooks = (SKILLS / "instantly-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("without assuming an unpublished signature", webhooks)
        self.assertIn("Custom labels may arrive as event_type values", webhooks)

        access = (SKILLS / "instantly-enterprise-rbac" / "SKILL.md").read_text()
        self.assertIn("x-as-workspace", access)
        self.assertIn("Only owners/admins", access)


if __name__ == "__main__":
    unittest.main()
