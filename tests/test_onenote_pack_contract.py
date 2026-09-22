"""Regression contract for the public OneNote operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "onenote-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "onenote-ci-integration",
    "onenote-common-errors",
    "onenote-core-workflow-a",
    "onenote-core-workflow-b",
    "onenote-cost-tuning",
    "onenote-debug-bundle",
    "onenote-deploy-integration",
    "onenote-hello-world",
    "onenote-install-auth",
    "onenote-local-dev-loop",
    "onenote-performance-tuning",
    "onenote-prod-checklist",
    "onenote-rate-limits",
    "onenote-reference-architecture",
    "onenote-sdk-patterns",
    "onenote-security-basics",
    "onenote-upgrade-migration",
    "onenote-webhooks-events",
}


class OneNotePackContractTest(unittest.TestCase):
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
                self.assertIn("version: 1.7.0", body)
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

        self.assertEqual(18, len(headings))
        self.assertEqual(18, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.7.0", self.manifest["version"])
        self.assertEqual("1.7.0", self.package["version"])
        self.assertEqual(18, len(self.skill_files))
        self.assertIn("Operator-grade OneNote", self.manifest["description"])

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "onenote-pack")
        self.assertEqual("1.7.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual(98, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_unsupported_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "/onenote/pages/delta",
            "600 requests per 60 seconds",
            "10,000 per 10 minutes",
            "Every integration must now",
            "must now use delegated",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "app-only authentication is unsupported",
            "delegated",
            "@odata.nextLink",
            "change notifications",
            "delta query",
            "Retry-After",
            "input HTML",
            "explicit approval",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
