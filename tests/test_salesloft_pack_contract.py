"""Regression contract for the public Salesloft operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "salesloft-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "salesloft-ci-integration",
    "salesloft-common-errors",
    "salesloft-core-workflow-a",
    "salesloft-core-workflow-b",
    "salesloft-cost-tuning",
    "salesloft-debug-bundle",
    "salesloft-deploy-integration",
    "salesloft-hello-world",
    "salesloft-install-auth",
    "salesloft-local-dev-loop",
    "salesloft-performance-tuning",
    "salesloft-prod-checklist",
    "salesloft-rate-limits",
    "salesloft-reference-architecture",
    "salesloft-sdk-patterns",
    "salesloft-security-basics",
    "salesloft-upgrade-migration",
    "salesloft-webhooks-events",
}


class SalesloftPackContractTest(unittest.TestCase):
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
                self.assertGreaterEqual(
                    reference_body.count("https://developers.salesloft.com"), 15
                )

        self.assertEqual(len(self.skill_files), len(headings))

    def test_stale_or_unsafe_claims_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "x-ratelimit-limit-per-minute",
            "x-ratelimit-remaining-per-minute",
            "x-salesloft-timestamp",
            "HMAC-SHA256",
            "API key deprecation",
            "dump all environment",
            "dump the database",
            "no batch endpoints",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

        self.assertNotRegex(markdown, re.compile(r"/v2/[A-Za-z0-9_/-]+\.json"))
        self.assertNotRegex(markdown, re.compile(r"npm install .*@(?:latest|next)"))

    def test_current_salesloft_operator_contracts_are_preserved(self) -> None:
        auth = (SKILLS / "salesloft-install-auth" / "SKILL.md").read_text()
        self.assertIn("Partners use OAuth", auth)
        self.assertIn("expire after 7,200 seconds", auth)
        self.assertIn("have no refresh token", auth)
        self.assertIn("revokes the old one", auth)

        rate = (SKILLS / "salesloft-rate-limits" / "SKILL.md").read_text()
        self.assertIn("600 cost per minute", rate)
        self.assertIn("Page 101-150 costs 3", rate)
        self.assertIn("x-ratelimit-endpoint-cost", rate)
        self.assertIn("x-ratelimit-remaining-minute", rate)

        webhook = (SKILLS / "salesloft-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("hexadecimal SHA-1 HMAC", webhook)
        self.assertIn("exact raw body", webhook)
        self.assertIn("three additional times, 15 seconds apart", webhook)
        self.assertIn("callback token", webhook)

        sync = (SKILLS / "salesloft-core-workflow-b" / "SKILL.md").read_text()
        self.assertIn("membership is mutable", sync)
        self.assertIn("microsecond-precision", sync)


if __name__ == "__main__":
    unittest.main()
