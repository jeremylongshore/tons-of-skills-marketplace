"""Regression contract for the public Firecrawl v2 operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "firecrawl-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "firecrawl-advanced-troubleshooting",
    "firecrawl-architecture-variants",
    "firecrawl-ci-integration",
    "firecrawl-common-errors",
    "firecrawl-core-workflow-a",
    "firecrawl-core-workflow-b",
    "firecrawl-cost-tuning",
    "firecrawl-data-handling",
    "firecrawl-debug-bundle",
    "firecrawl-deploy-integration",
    "firecrawl-enterprise-rbac",
    "firecrawl-hello-world",
    "firecrawl-incident-runbook",
    "firecrawl-install-auth",
    "firecrawl-known-pitfalls",
    "firecrawl-load-scale",
    "firecrawl-local-dev-loop",
    "firecrawl-migration-deep-dive",
    "firecrawl-multi-env-setup",
    "firecrawl-observability",
    "firecrawl-performance-tuning",
    "firecrawl-policy-guardrails",
    "firecrawl-prod-checklist",
    "firecrawl-rate-limits",
    "firecrawl-reference-architecture",
    "firecrawl-reliability-patterns",
    "firecrawl-sdk-patterns",
    "firecrawl-security-basics",
    "firecrawl-upgrade-migration",
    "firecrawl-webhooks-events",
}


class FirecrawlPackContractTest(unittest.TestCase):
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
                self.assertIn("firecrawl/firecrawl-docs/tree/8bd51cb", reference_body)
                self.assertIn("github.com/firecrawl/firecrawl", reference_body)
                self.assertGreaterEqual(reference_body.count("https://"), 20)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_pack_metadata_is_version_and_scope_aligned(self) -> None:
        self.assertEqual("1.12.0", self.expected_version)
        self.assertEqual(self.expected_version, self.package["version"])
        self.assertEqual(30, len(self.skill_files))
        self.assertIn("Operator-grade Firecrawl v2", self.manifest["description"])

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(item for item in marketplace["plugins"] if item["name"] == "firecrawl-pack")
        self.assertEqual(self.expected_version, entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(30, entry["components"]["skills"])

    def test_legacy_and_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "@mendable/firecrawl-js",
            "https://api.firecrawl.dev/v1/",
            "if (!process.env.FIRECRAWL_WEBHOOK_SECRET) return true",
            "events: [\"completed\", \"page\"]",
            "crawl.failed |",
            "batch_scrape.failed |",
            "1 credit = 1 page scraped",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_v2_and_security_contracts_are_explicit(self) -> None:
        install = (SKILLS / "firecrawl-install-auth" / "SKILL.md").read_text()
        self.assertIn("Node package as firecrawl", install)
        self.assertIn("feature-frozen v1", install)

        core = (SKILLS / "firecrawl-core-workflow-a" / "SKILL.md").read_text()
        for method in ("scrape", "crawl", "startCrawl", "getCrawlStatus", "cancelCrawl"):
            self.assertIn(method, core)

        extraction = (SKILLS / "firecrawl-core-workflow-b" / "SKILL.md").read_text()
        self.assertIn("startBatchScrape", extraction)
        self.assertIn("getBatchScrapeStatus", extraction)
        self.assertIn("json format object", extraction)

        webhooks = (SKILLS / "firecrawl-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("X-Firecrawl-Signature", webhooks)
        self.assertIn("sha256=hex", webhooks)
        self.assertIn("raw body", webhooks)
        self.assertIn("webhookId", webhooks)
        self.assertIn("10 seconds", webhooks)

        access = (SKILLS / "firecrawl-enterprise-rbac" / "SKILL.md").read_text()
        self.assertIn("Admin and Member", access)
        self.assertIn("Empty restriction lists mean unrestricted", access)


if __name__ == "__main__":
    unittest.main()
