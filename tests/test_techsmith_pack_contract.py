"""Regression contract for the public TechSmith operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "techsmith-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "techsmith-ci-integration",
    "techsmith-common-errors",
    "techsmith-core-workflow-a",
    "techsmith-core-workflow-b",
    "techsmith-cost-tuning",
    "techsmith-debug-bundle",
    "techsmith-deploy-integration",
    "techsmith-hello-world",
    "techsmith-install-auth",
    "techsmith-local-dev-loop",
    "techsmith-performance-tuning",
    "techsmith-prod-checklist",
    "techsmith-rate-limits",
    "techsmith-reference-architecture",
    "techsmith-sdk-patterns",
    "techsmith-security-basics",
    "techsmith-upgrade-migration",
    "techsmith-webhooks-events",
}


class TechSmithPackContractTest(unittest.TestCase):
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
                self.assertIn("## Licensing and Authentication", body)
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
            "CamtasiaProducer.exe /i",
            "CamtasiaProducer.exe /batch",
            "Region (2)",
            "Window (4)",
            "Clipboard (1)",
            "HTTP 429",
            "TechSmith webhook signature",
            "dump all environment",
            "disable antivirus",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

        self.assertNotRegex(markdown, re.compile(r"npm install .*@(?:latest|next)"))

    def test_current_techsmith_contracts_are_preserved(self) -> None:
        capture = (SKILLS / "techsmith-core-workflow-a" / "SKILL.md").read_text()
        self.assertIn("`Snagit.ImageCapture.1`", capture)
        self.assertIn("window `1`, region `4`", capture)
        self.assertIn("file `2`, clipboard `4`", capture)
        self.assertIn("`IsCaptureDone`", capture)
        self.assertIn("`LastCaptureSucceeded`", capture)
        self.assertIn("`LastFileWritten`", capture)

        export = (SKILLS / "techsmith-core-workflow-b" / "SKILL.md").read_text()
        self.assertIn("legacy exporter was removed in 2024.1.3", export)
        self.assertIn("local non-synced drive", export)
        self.assertIn("not backward-compatible", export)

        install = (SKILLS / "techsmith-install-auth" / "SKILL.md").read_text()
        self.assertIn("Individual subscriptions require", install)
        self.assertIn("Business subscriptions use software keys", install)
        self.assertIn("SnagitCapture.exe /register", install)

        events = (SKILLS / "techsmith-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("not authenticated vendor webhooks", events)
        self.assertIn("Filesystem watcher notifications are hints", events)


if __name__ == "__main__":
    unittest.main()
