"""Regression contract for the public ClickUp operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "clickup-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "clickup-ci-integration",
    "clickup-common-errors",
    "clickup-core-workflow-a",
    "clickup-core-workflow-b",
    "clickup-cost-tuning",
    "clickup-data-handling",
    "clickup-debug-bundle",
    "clickup-deploy-integration",
    "clickup-enterprise-rbac",
    "clickup-hello-world",
    "clickup-incident-runbook",
    "clickup-install-auth",
    "clickup-local-dev-loop",
    "clickup-migration-deep-dive",
    "clickup-multi-env-setup",
    "clickup-observability",
    "clickup-performance-tuning",
    "clickup-prod-checklist",
    "clickup-rate-limits",
    "clickup-reference-architecture",
    "clickup-sdk-patterns",
    "clickup-security-basics",
    "clickup-upgrade-migration",
    "clickup-webhooks-events",
}


class ClickUpPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.expected_version = manifest["version"]

    def test_all_skills_have_release_metadata_and_official_references(self) -> None:
        headings = set()
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
                self.assertGreaterEqual(reference_body.count("https://developer.clickup.com"), 15)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_stale_or_invented_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text(encoding="utf-8") for path in PACK.rglob("*.md"))
        for stale in (
            "API v2-to-v3 migration",
            "Q1 2026",
            "X-ClickUp-Signature",
            "dump all environment",
            "dump the database",
            "universal batch endpoint",
            "fields selector",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

        self.assertNotRegex(markdown, re.compile(r"(?:print|log).{0,24}(?:CLICKUP_API_TOKEN|pk_[A-Za-z0-9])", re.IGNORECASE))

    def test_current_clickup_contracts_are_preserved(self) -> None:
        auth = (SKILLS / "clickup-install-auth" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("begin with `pk_`", auth)
        self.assertIn("https://app.clickup.com/api", auth)
        self.assertIn("https://api.clickup.com/api/v2/oauth/token", auth)
        self.assertIn("subject to change", auth)

        limits = (SKILLS / "clickup-rate-limits" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("100 requests/minute for Free Forever, Unlimited, and Business", limits)
        self.assertIn("1,000 for Business Plus", limits)
        self.assertIn("10,000 for Enterprise", limits)
        self.assertIn("`X-RateLimit-Limit`", limits)
        self.assertIn("`X-RateLimit-Remaining`", limits)
        self.assertIn("`X-RateLimit-Reset`", limits)

        webhooks = (SKILLS / "clickup-webhooks-events" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("raw-body HMAC-SHA256", webhooks)
        self.assertIn("hexadecimal `X-Signature`", webhooks)
        self.assertIn("up to five times", webhooks)
        self.assertIn("`fail_count=100`", webhooks)
        self.assertIn("401 suspends immediately", webhooks)

        tasks = (SKILLS / "clickup-core-workflow-a" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("100 tasks per zero-based page", tasks)
        self.assertIn("`include_timl`", tasks)
        comments = (SKILLS / "clickup-performance-tuning" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`start` plus `start_id` after the first 25 newest comments", comments)

        versions = (SKILLS / "clickup-upgrade-migration" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("no general v2-to-v3 cutover contract", versions)
        rbac = (SKILLS / "clickup-enterprise-rbac" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("User/guest management is Enterprise-only", rbac)
        self.assertIn("Enterprise-only and owner-only", rbac)


if __name__ == "__main__":
    unittest.main()
