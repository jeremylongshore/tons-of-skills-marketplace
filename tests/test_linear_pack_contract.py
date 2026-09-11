"""Regression contract for the public Linear operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "linear-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "linear-ci-integration",
    "linear-common-errors",
    "linear-core-workflow-a",
    "linear-core-workflow-b",
    "linear-cost-tuning",
    "linear-data-handling",
    "linear-debug-bundle",
    "linear-deploy-integration",
    "linear-enterprise-rbac",
    "linear-hello-world",
    "linear-incident-runbook",
    "linear-install-auth",
    "linear-local-dev-loop",
    "linear-migration-deep-dive",
    "linear-multi-env-setup",
    "linear-observability",
    "linear-performance-tuning",
    "linear-prod-checklist",
    "linear-rate-limits",
    "linear-reference-architecture",
    "linear-sdk-patterns",
    "linear-security-basics",
    "linear-upgrade-migration",
    "linear-webhooks-events",
}


class LinearPackContractTest(unittest.TestCase):
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
                    "## Output",
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
                self.assertGreaterEqual(reference_body.count("https://linear.app/"), 19)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "250,000 complexity",
            "5,000 req/hr + 250,000",
            "Rate Limiting (HTTP 429)",
            "https://api.linear.app/scim/v2",
            "gh secret set LINEAR_API_KEY --body",
            "git revert HEAD && npm run deploy",
            "[INCIDENT-DIAG] Safe to delete",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_linear_contracts_are_preserved(self) -> None:
        references = (
            SKILLS / "linear-install-auth" / "references" / "official-docs.md"
        ).read_text()
        self.assertIn("2,500 requests", references)
        self.assertIn("3,000,000 complexity", references)
        self.assertIn("5,000 requests", references)
        self.assertIn("2,000,000 points", references)
        self.assertIn("HTTP 400", references)
        self.assertIn("2026-04-01", references)
        self.assertIn("`@linear/sdk` 95.0.0", references)

        hello = (SKILLS / "linear-hello-world" / "SKILL.md").read_text()
        self.assertIn("Authorization: <API_KEY>", hello)
        self.assertIn("Authorization: Bearer <ACCESS_TOKEN>", hello)

        limits = (SKILLS / "linear-rate-limits" / "SKILL.md").read_text()
        self.assertIn("10,000 points", limits)
        self.assertIn("extensions.code: RATELIMITED", limits)

        webhooks = (SKILLS / "linear-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("within five seconds", webhooks)
        self.assertIn("one minute, one hour, and six hours", webhooks)
        self.assertIn("Linear-Delivery", webhooks)

        enterprise = (SKILLS / "linear-enterprise-rbac" / "SKILL.md").read_text()
        self.assertIn("SCIM 2.0", enterprise)
        self.assertIn("90 days", enterprise)
        self.assertIn("do not hard-code a guessed endpoint", enterprise)


if __name__ == "__main__":
    unittest.main()
