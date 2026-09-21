"""Regression contract for the public Notion operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "notion-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "notion-advanced-troubleshooting",
    "notion-architecture-variants",
    "notion-ci-integration",
    "notion-common-errors",
    "notion-content-management",
    "notion-core-workflow-a",
    "notion-core-workflow-b",
    "notion-cost-tuning",
    "notion-data-handling",
    "notion-debug-bundle",
    "notion-deploy-integration",
    "notion-enterprise-rbac",
    "notion-hello-world",
    "notion-incident-runbook",
    "notion-install-auth",
    "notion-known-pitfalls",
    "notion-load-scale",
    "notion-local-dev-loop",
    "notion-migration-deep-dive",
    "notion-multi-env-setup",
    "notion-observability",
    "notion-performance-tuning",
    "notion-policy-guardrails",
    "notion-prod-checklist",
    "notion-rate-limits",
    "notion-reference-architecture",
    "notion-reliability-patterns",
    "notion-sdk-patterns",
    "notion-search-retrieve",
    "notion-security-basics",
    "notion-upgrade-migration",
    "notion-webhooks-events",
}


class NotionPackContractTest(unittest.TestCase):
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
                self.assertIn("version: 1.40.0", body)
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

                references = list((skill_file.parent / "references").glob("*.md"))
                self.assertEqual(["official-docs.md"], [path.name for path in references])
                evidence = references[0].read_text(encoding="utf-8")
                self.assertIn("Reviewed: 2026-09-12", evidence)
                self.assertEqual(5, evidence.count("https://"))
                self.assertIn("2026-03-11", evidence)

        self.assertEqual(32, len(headings))
        self.assertEqual(32, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.40.0", self.manifest["version"])
        self.assertEqual("1.40.0", self.package["version"])
        self.assertEqual(32, len(self.skill_files))
        self.assertIn("Operator-grade Notion", self.manifest["description"])

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "notion-pack")
        self.assertEqual("1.40.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(32, entry["components"]["skills"])
        self.assertEqual(98, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_obsolete_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for obsolete in (
            "2022-06-28",
            "notion.databases.query",
            "hard limit of 3 requests",
            "all pricing tiers",
            "current stable API version",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "2026-03-11",
            "data-source ID",
            "in_trash",
            "meeting_notes",
            "Retry-After",
            "X-Notion-Signature",
            "HMAC-SHA256",
            "explicit approval",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
