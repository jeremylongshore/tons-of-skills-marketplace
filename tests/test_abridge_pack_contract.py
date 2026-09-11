"""Regression contract for the public Abridge operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "abridge-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "abridge-ci-integration",
    "abridge-common-errors",
    "abridge-core-workflow-a",
    "abridge-core-workflow-b",
    "abridge-cost-tuning",
    "abridge-debug-bundle",
    "abridge-deploy-integration",
    "abridge-hello-world",
    "abridge-install-auth",
    "abridge-local-dev-loop",
    "abridge-performance-tuning",
    "abridge-prod-checklist",
    "abridge-rate-limits",
    "abridge-reference-architecture",
    "abridge-sdk-patterns",
    "abridge-security-basics",
    "abridge-upgrade-migration",
    "abridge-webhooks-events",
}


class AbridgePackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.expected_version = self.manifest["version"]

    def test_release_metadata_and_distinct_reference_maps(self) -> None:
        headings = set()
        reference_bodies = set()
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
                self.assertIn("## Example", body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("2026-09-10", reference_body)
                self.assertGreaterEqual(reference_body.count("https://"), 4)
                reference_bodies.add(reference_body)

        self.assertEqual(len(self.skill_files), len(headings))
        self.assertEqual(len(self.skill_files), len(reference_bodies))

    def test_invented_public_abridge_contracts_do_not_return(self) -> None:
        corpus = "\n".join(path.read_text().lower() for path in self.skill_files)
        for invented in (
            "sandbox.api.abridge.com",
            "api.abridge.com/v1",
            "x-org-id",
            "abridge_client_secret",
            "x-abridge-signature",
            "note.completed",
            "patient.summary.ready",
            "provider.enrolled",
            "retry-after header",
            "documentreference post",
            "tls 1.3 enforcement",
        ):
            with self.subTest(invented=invented):
                self.assertNotIn(invented, corpus)

    def test_private_contract_and_clinician_review_boundaries_are_explicit(self) -> None:
        corpus = "\n".join(path.read_text() for path in self.skill_files)
        self.assertGreaterEqual(corpus.count("tenant-specific"), 18)
        self.assertGreaterEqual(corpus.lower().count("synthetic"), 18)
        self.assertGreaterEqual(corpus.lower().count("approval"), 18)
        self.assertIn("clinician reviews and edits the generated draft", corpus)
        self.assertIn("does not claim a public Abridge SDK", (PACK / "README.md").read_text())

    def test_manifest_is_qualified_and_consistent(self) -> None:
        self.assertEqual("abridge-pack", self.manifest["name"])
        self.assertEqual(1, self.manifest["keywords"].count("abridge"))
        self.assertIn("live actions remain approval-gated", self.manifest["description"])
        package = json.loads((PACK / "package.json").read_text())
        self.assertEqual(self.manifest["description"], package["description"])


if __name__ == "__main__":
    unittest.main()
