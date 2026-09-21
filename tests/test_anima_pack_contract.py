"""Regression contract for the public Anima operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "anima-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "anima-ci-integration",
    "anima-common-errors",
    "anima-core-workflow-a",
    "anima-core-workflow-b",
    "anima-cost-tuning",
    "anima-debug-bundle",
    "anima-deploy-integration",
    "anima-hello-world",
    "anima-install-auth",
    "anima-local-dev-loop",
    "anima-performance-tuning",
    "anima-prod-checklist",
    "anima-rate-limits",
    "anima-reference-architecture",
    "anima-sdk-patterns",
    "anima-security-basics",
    "anima-upgrade-migration",
    "anima-webhooks-events",
}


class AnimaPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_reviewable_structure(self) -> None:
        headings: set[str] = set()
        descriptions: set[str] = set()
        required_sections = (
            "## Overview",
            "## Prerequisites",
            "## Tool Discipline",
            "## Output",
            "## Examples",
            "## Error Handling",
            "## Resources",
        )
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 2.0.0", body)
                self.assertIn("Use when", normalized)
                self.assertIn("Trigger with", normalized)
                for section in required_sections:
                    self.assertIn(section, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                description = re.search(
                    r"description: '(.+?)'\nallowed-tools:",
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
                self.assertIn("Checked 2026-09-12", evidence)
                self.assertIn("95b66d7e56514908d2017b6d9da03699e6ee0e00", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 4)

        self.assertEqual(18, len(headings))
        self.assertEqual(18, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(self.manifest["description"], self.package["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(
            item for item in marketplace["plugins"] if item["name"] == "anima-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual(95, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "api.animaapp.com",
            "ANIMA_API_KEY",
            "10 generations/minute",
            "React/Vue/HTML",
            "files.length",
            "for (const file of files)",
            "scope=files:read",
            '"team_id":',
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "@animaapp/anima-sdk",
            "generateCodeFromWebsite",
            "generateCodeFromPrompt",
            "FigmaRestApi",
            "figmaRateLimitMaxWait",
            "file_content:read",
            "context_id",
            "plain_css",
            "custom_design_system",
            "Record<string",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
