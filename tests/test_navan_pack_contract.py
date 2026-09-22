"""Regression contract for the public Navan operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "navan-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "navan-ci-integration",
    "navan-common-errors",
    "navan-core-workflow-a",
    "navan-core-workflow-b",
    "navan-cost-tuning",
    "navan-data-handling",
    "navan-data-sync",
    "navan-debug-bundle",
    "navan-deploy-integration",
    "navan-enterprise-rbac",
    "navan-entity-management",
    "navan-hello-world",
    "navan-incident-runbook",
    "navan-install-auth",
    "navan-local-dev-loop",
    "navan-migration-deep-dive",
    "navan-multi-env-setup",
    "navan-observability",
    "navan-performance-tuning",
    "navan-prod-checklist",
    "navan-rate-limits",
    "navan-reference-architecture",
    "navan-sdk-patterns",
    "navan-security-basics",
    "navan-upgrade-migration",
    "navan-webhooks-events",
}


class NavanPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_reviewable_structure(self) -> None:
        headings = set()
        descriptions = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 1.9.0", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("Use when", normalized)
                self.assertIn("Trigger with", normalized)
                for section in (
                    "## Prerequisites",
                    "## Current Contract",
                    "## Authentication",
                    "## Instructions",
                    "## Tool Discipline",
                    "## Approval Boundaries",
                    "## Error Handling",
                    "## Output",
                    "## Examples",
                    "## Validation",
                    "## Resources",
                ):
                    self.assertIn(section, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                description = re.search(
                    r"description: >-\n\s+(.+?)(?=\nallowed-tools:)",
                    body,
                    re.DOTALL,
                )
                self.assertIsNotNone(heading)
                self.assertIsNotNone(description)
                headings.add(heading.group(1))
                descriptions.add(re.sub(r"\s+", " ", description.group(1)))

                reference_dir = skill_file.parent / "references"
                self.assertFalse((reference_dir / "one-pager.md").exists())
                evidence = (reference_dir / "official-docs.md").read_text(encoding="utf-8")
                self.assertIn("Reviewed: 2026-09-12", evidence)
                self.assertEqual(5, evidence.count("https://"))
                self.assertNotIn("wiki.internal", evidence)

        self.assertEqual(26, len(headings))
        self.assertEqual(26, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.9.0", self.manifest["version"])
        self.assertEqual("1.9.0", self.package["version"])
        self.assertEqual(26, len(self.skill_files))
        self.assertIn("Operator-grade Navan", self.manifest["description"])

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "navan-pack")
        self.assertEqual("1.9.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(26, entry["components"]["skills"])
        self.assertEqual(97, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_unsupported_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "api.navan.com",
            "/ta-auth/oauth/token",
            "/v1/bookings",
            "/v1/expenses",
            "x-navan-signature",
            "weekly full-refresh",
            "TRANSACTION is incremental and append-only",
            "Airbyte",
            "wiki.internal",
            "no public SDK",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "Booking API",
            "Expense API",
            "SFTP",
            "SCIM",
            "SAML",
            "OpenID Connect",
            "tenant-specific",
            "traveler",
            "payment",
            "MCP",
            "explicit approval",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
