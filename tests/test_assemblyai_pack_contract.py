"""Regression contract for the public AssemblyAI operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "assemblyai-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "assemblyai-ci-integration",
    "assemblyai-common-errors",
    "assemblyai-core-workflow-a",
    "assemblyai-core-workflow-b",
    "assemblyai-cost-tuning",
    "assemblyai-debug-bundle",
    "assemblyai-deploy-integration",
    "assemblyai-hello-world",
    "assemblyai-install-auth",
    "assemblyai-local-dev-loop",
    "assemblyai-performance-tuning",
    "assemblyai-prod-checklist",
    "assemblyai-rate-limits",
    "assemblyai-reference-architecture",
    "assemblyai-sdk-patterns",
    "assemblyai-security-basics",
    "assemblyai-upgrade-migration",
    "assemblyai-webhooks-events",
}


class AssemblyAIPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_structure(self) -> None:
        headings = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 1.12.0", body)
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
                    "## Failure Modes",
                    "## Output",
                    "## Example",
                    "## Validation",
                    "## References",
                ):
                    self.assertIn(required, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                evidence = reference.read_text(encoding="utf-8")
                self.assertIn("Reviewed: 2026-09-12", evidence)
                self.assertIn("docs/llms-full.txt", evidence)
                self.assertIn("migration-from-lemur", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 12)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.12.0", self.manifest["version"])
        self.assertEqual("1.12.0", self.package["version"])
        self.assertEqual(18, len(self.skill_files))
        self.assertIn("AssemblyAI", self.manifest["description"])

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(item for item in marketplace["plugins"] if item["name"] == "assemblyai-pack")
        self.assertEqual("1.12.0", entry["version"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_retired_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "client.lemur.",
            "createService({ speech_model: 'nova-3'",
            "wss://api.assemblyai.com/v2/realtime/ws",
            "@assemblyai/sdk",
            "Best vs Nano",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_contracts_are_explicit(self) -> None:
        all_text = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for required in (
            "speech_models",
            "streaming.assemblyai.com/v3/ws",
            "LLM Gateway",
            "March 31, 2026",
            "20,000 API requests per five minutes",
            "10-second acknowledgment window",
            "raw project key",
            "single-use",
            "Termination",
        ):
            with self.subTest(required=required):
                self.assertIn(required, all_text)


if __name__ == "__main__":
    unittest.main()
