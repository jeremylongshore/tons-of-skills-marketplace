"""Regression contract for the public Together AI operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "together-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "together-ci-integration",
    "together-common-errors",
    "together-core-workflow-a",
    "together-core-workflow-b",
    "together-cost-tuning",
    "together-deploy-integration",
    "together-hello-world",
    "together-install-auth",
    "together-local-dev-loop",
    "together-prod-checklist",
    "together-rate-limits",
    "together-reference-architecture",
    "together-sdk-patterns",
    "together-security-basics",
    "together-upgrade-migration",
    "together-webhooks-events",
}


class TogetherPackContractTest(unittest.TestCase):
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
                self.assertGreaterEqual(reference_body.count("https://"), 15)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_stale_or_invented_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "api.together.xyz",
            "x-together-signature",
            "Webhook Signature Verification",
            "$0.10-5.00 per 1M tokens",
            "TIER_CONFIG",
            "maxConcurrent: 20",
            "dump all environment variables",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

        self.assertNotRegex(markdown, re.compile(r"pip install together==0\."))

    def test_current_together_contracts_are_preserved(self) -> None:
        install = (SKILLS / "together-install-auth" / "SKILL.md").read_text()
        self.assertIn("`together>=2.0.0`", install)
        self.assertIn("project-scoped", install)
        self.assertIn("`client.models.list()`", install)

        limits = (SKILLS / "together-rate-limits" / "SKILL.md").read_text()
        self.assertIn("dynamic per organization and model", limits)
        self.assertIn("`x-ratelimit-*`", limits)
        self.assertIn("`x-tokenlimit-*`", limits)

        batch = (SKILLS / "together-core-workflow-b" / "SKILL.md").read_text()
        self.assertIn("`custom_id`", batch)
        self.assertIn('`purpose="batch-api"`', batch)
        self.assertIn("`error_file_id`", batch)

        deploy = (SKILLS / "together-deploy-integration" / "SKILL.md").read_text()
        self.assertIn("v2 endpoint/deployment model", deploy)
        self.assertIn("Legacy v1 endpoint creation is retired", deploy)

        events = (SKILLS / "together-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("no general signed webhook surface is documented", events)
        self.assertIn("your own signing scheme", events)


if __name__ == "__main__":
    unittest.main()
