"""Regression contract for the public Attio operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "attio-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "attio-ci-integration",
    "attio-common-errors",
    "attio-core-workflow-a",
    "attio-core-workflow-b",
    "attio-cost-tuning",
    "attio-debug-bundle",
    "attio-deploy-integration",
    "attio-hello-world",
    "attio-install-auth",
    "attio-local-dev-loop",
    "attio-performance-tuning",
    "attio-prod-checklist",
    "attio-rate-limits",
    "attio-reference-architecture",
    "attio-sdk-patterns",
    "attio-security-basics",
    "attio-upgrade-migration",
    "attio-webhooks-events",
}


class AttioPackContractTest(unittest.TestCase):
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
                self.assertGreaterEqual(reference_body.count("https://docs.attio.com"), 8)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_stale_or_unsafe_claims_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text(encoding="utf-8") for path in PACK.rglob("*.md"))
        for stale in (
            "Attio uses cursor-based pagination",
            "V1-to-V2 migration",
            "All event types",
            "sk_prod_xyz",
            "/v2/records/search",
            "timestamp + body",
            "timestamp.concat(body)",
            "dump all environment",
            "dump the database",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

        self.assertNotRegex(markdown, re.compile(r"npm install .*@(?:latest|next)"))

    def test_current_attio_operator_contracts_are_preserved(self) -> None:
        rate_limits = (SKILLS / "attio-rate-limits" / "SKILL.md").read_text()
        self.assertIn("100 read requests per second", rate_limits)
        self.assertIn("25 write requests per second", rate_limits)
        self.assertIn("HTTP date", rate_limits)
        self.assertIn("score budget over a 10-second window", rate_limits)

        security = (SKILLS / "attio-security-basics" / "SKILL.md").read_text()
        self.assertIn("exact raw UTF-8 request body", security)
        self.assertIn("signature input is the raw body only", security)
        self.assertIn("equal-length", security)

        webhooks = (SKILLS / "attio-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("`Attio-Signature`", webhooks)
        self.assertIn("`Idempotency-Key`", webhooks)
        self.assertIn("at least once", webhooks)
        self.assertIn("5-second timeout", webhooks)

        sdk = (SKILLS / "attio-sdk-patterns" / "SKILL.md").read_text()
        self.assertIn("offset and cursor iterators", sdk)
        self.assertIn("Attio App SDK package `attio`", sdk)


if __name__ == "__main__":
    unittest.main()
