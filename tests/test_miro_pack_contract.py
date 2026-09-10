"""Regression contract for the public Miro operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "miro-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "miro-ci-integration",
    "miro-common-errors",
    "miro-core-workflow-a",
    "miro-core-workflow-b",
    "miro-cost-tuning",
    "miro-data-handling",
    "miro-debug-bundle",
    "miro-deploy-integration",
    "miro-enterprise-rbac",
    "miro-hello-world",
    "miro-incident-runbook",
    "miro-install-auth",
    "miro-local-dev-loop",
    "miro-migration-deep-dive",
    "miro-multi-env-setup",
    "miro-observability",
    "miro-performance-tuning",
    "miro-prod-checklist",
    "miro-rate-limits",
    "miro-reference-architecture",
    "miro-sdk-patterns",
    "miro-security-basics",
    "miro-upgrade-migration",
    "miro-webhooks-events",
}


class MiroPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.expected_version = manifest["version"]

    def test_all_skills_have_release_metadata_and_official_references(self) -> None:
        headings = set()
        reference_bodies = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn("allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit", body)
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("## Tool Discipline", body)
                self.assertIn("## Current Contract", body)
                self.assertIn("## Authentication", body)
                self.assertIn("## Approval Boundaries", body)
                self.assertIn("## Error Handling", body)
                self.assertIn("## Examples", body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("2026-09-10", reference_body)
                self.assertIn(skill_file.parent.name, reference_body.splitlines()[0])
                self.assertGreaterEqual(reference_body.count("https://"), 4)
                reference_bodies.add(reference_body)

        self.assertEqual(len(self.skill_files), len(headings))
        self.assertEqual(
            len(self.skill_files),
            len(reference_bodies),
            "each workflow must carry a distinct, skill-specific primary-source bundle",
        )

    def test_retired_or_invented_contracts_do_not_return(self) -> None:
        skills_markdown = "\n".join(path.read_text() for path in SKILLS.glob("*/SKILL.md"))
        for stale in (
            "x-miro-signature",
            "miro_webhook_secret",
            "webhook signing secret",
            "respond quickly (within 10 seconds)",
            "all board item types are supported except",
            "always store and use the refresh token",
            "dump all environment",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, skills_markdown.lower())

        endpoint = "/v2-experimental/webhooks/board_subscriptions"
        mentions = [path for path in self.skill_files if endpoint in path.read_text()]
        self.assertEqual(
            {SKILLS / "miro-webhooks-events" / "SKILL.md"},
            set(mentions),
            "the retired endpoint may appear only in the migration warning",
        )

    def test_current_miro_contracts_are_preserved(self) -> None:
        auth = (SKILLS / "miro-install-auth" / "SKILL.md").read_text()
        self.assertIn("https://miro.com/oauth/authorize", auth)
        self.assertIn("https://api.miro.com/v1/oauth/token", auth)
        self.assertIn("one-hour access token", auth)
        self.assertIn("sixty-day refresh token", auth)
        self.assertIn("cannot later be enabled, disabled, or changed", auth)

        limits = (SKILLS / "miro-rate-limits" / "SKILL.md").read_text()
        self.assertIn("100,000 credits per minute", limits)
        for value in ("50 credits", "100", "500", "2,000"):
            self.assertIn(value, limits)
        for header in ("X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"):
            self.assertIn(header, limits)

        events = (SKILLS / "miro-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("discontinued experimental REST webhooks", events)
        self.assertIn("no current production Miro REST callback/signature contract", events)
        self.assertIn("not durable server-to-server delivery", events)
        self.assertIn("does not fire for copy-paste or duplication", events)

        bulk = (SKILLS / "miro-core-workflow-a" / "SKILL.md").read_text()
        self.assertIn("at most twenty items", bulk)
        self.assertIn("transactional", bulk)
        self.assertIn("Level 2 credits per item", bulk)


if __name__ == "__main__":
    unittest.main()
