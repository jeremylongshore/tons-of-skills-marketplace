"""Regression contract for the public StackBlitz operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "stackblitz-pack"
SKILLS = PACK / "skills"


class StackBlitzPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(10, len(self.skill_files))
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.expected_version = manifest["version"]

    def test_release_metadata_and_official_references(self) -> None:
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("## Tool Discipline", body)
                self.assertIn("## Current Contract", body)
                self.assertIn("## Authentication", body)
                self.assertIn("## Approval Boundaries", body)
                self.assertIn("## Examples", body)

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("Checked on 2026-09-10", reference_body)
                self.assertGreaterEqual(reference_body.count("https://"), 3)

    def test_stale_or_unsafe_claims_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text(encoding="utf-8") for path in PACK.rglob("*.md"))
        for stale in (
            "Memory | ~2GB",
            "Modern browser (Chrome 90+",
            "WebContainers require no auth",
            "No risk of bad actors",
            "npm install --prefer-offline",
            "retrying...",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

        self.assertNotRegex(markdown, re.compile(r"npm install .*@(?:latest|next)"))

    def test_current_operator_boundaries_are_preserved(self) -> None:
        install = (SKILLS / "stackblitz-install-auth" / "SKILL.md").read_text()
        for expected in ("configureAPIKey", "auth.init", "before `WebContainer.boot()`"):
            self.assertIn(expected, install)

        embed = (SKILLS / "stackblitz-core-workflow-b" / "SKILL.md").read_text()
        self.assertIn("unless a user forks", embed)
        self.assertIn("deprecated `forceEmbedLayout`", embed)

        capacity = (SKILLS / "stackblitz-rate-limits" / "SKILL.md").read_text()
        self.assertIn("unsupported universal quota", capacity)
        self.assertIn("measured application budget", capacity)

        security = (SKILLS / "stackblitz-security-basics" / "SKILL.md").read_text()
        self.assertIn("does not make user code trustworthy", security)
        self.assertIn("preview messages", security)


if __name__ == "__main__":
    unittest.main()
