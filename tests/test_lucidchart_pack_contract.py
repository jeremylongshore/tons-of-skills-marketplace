"""Regression contract for the public Lucid integration operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "lucidchart-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "lucidchart-ci-integration",
    "lucidchart-common-errors",
    "lucidchart-core-workflow-a",
    "lucidchart-core-workflow-b",
    "lucidchart-cost-tuning",
    "lucidchart-debug-bundle",
    "lucidchart-deploy-integration",
    "lucidchart-hello-world",
    "lucidchart-install-auth",
    "lucidchart-local-dev-loop",
    "lucidchart-performance-tuning",
    "lucidchart-prod-checklist",
    "lucidchart-rate-limits",
    "lucidchart-reference-architecture",
    "lucidchart-sdk-patterns",
    "lucidchart-security-basics",
    "lucidchart-upgrade-migration",
    "lucidchart-webhooks-events",
}


class LucidchartPackContractTest(unittest.TestCase):
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
                for section in (
                    "## Tool Discipline",
                    "## Current Contract",
                    "## Authentication",
                    "## Approval Boundaries",
                    "## Error Handling",
                    "## Example",
                ):
                    self.assertIn(section, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("2026-09-11", reference_body)
                self.assertGreaterEqual(reference_body.count("https://"), 4)
                reference_bodies.add(reference_body)

        self.assertEqual(len(self.skill_files), len(headings))
        self.assertEqual(len(self.skill_files), len(reference_bodies))

    def test_fabricated_lucid_contracts_do_not_return(self) -> None:
        corpus = "\n".join(path.read_text().lower() for path in self.skill_files)
        for invented in (
            "lucid-api-key:",
            "x-lucid-signature",
            "document.updated",
            "shape.created",
            "collaborator.joined",
            "100 requests/min",
            "100 requests per minute",
            "cost per export",
            "document lock endpoint",
        ):
            with self.subTest(invented=invented):
                self.assertNotIn(invented, corpus)

    def test_contract_boundaries_are_explicit(self) -> None:
        corpus = "\n".join(path.read_text() for path in self.skill_files)
        self.assertGreaterEqual(corpus.lower().count("approval"), 18)
        self.assertGreaterEqual(corpus.lower().count("bearer"), 3)
        self.assertGreaterEqual(corpus.lower().count("synthetic"), 8)
        self.assertIn("API keys, OAuth user tokens, and OAuth account tokens", corpus)
        self.assertIn("There is no justified pack-wide fixed requests-per-minute value", corpus)
        self.assertIn("Do not claim generic Lucid document", corpus)

    def test_manifest_and_catalog_are_consistent(self) -> None:
        self.assertEqual("lucidchart-pack", self.manifest["name"])
        self.assertEqual(1, self.manifest["keywords"].count("lucidchart"))
        package = json.loads((PACK / "package.json").read_text())
        self.assertEqual(self.manifest["description"], package["description"])
        catalog = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(plugin for plugin in catalog["plugins"] if plugin["name"] == "lucidchart-pack")
        self.assertEqual(self.manifest["version"], entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])


if __name__ == "__main__":
    unittest.main()
