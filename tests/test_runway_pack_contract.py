"""Regression contract for the public Runway operator pack."""

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "runway-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "runway-ci-integration",
    "runway-common-errors",
    "runway-core-workflow-a",
    "runway-core-workflow-b",
    "runway-cost-tuning",
    "runway-debug-bundle",
    "runway-deploy-integration",
    "runway-hello-world",
    "runway-install-auth",
    "runway-local-dev-loop",
    "runway-performance-tuning",
    "runway-prod-checklist",
    "runway-rate-limits",
    "runway-reference-architecture",
    "runway-sdk-patterns",
    "runway-security-basics",
    "runway-upgrade-migration",
    "runway-webhooks-events",
}


def frontmatter(body: str) -> dict:
    return yaml.safe_load(body.split("---", 2)[1])


class RunwayPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {item.parent.name for item in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_reviewable_structure(self) -> None:
        headings: set[str] = set()
        descriptions: set[str] = set()
        required_sections = (
            "## Overview",
            "## Prerequisites",
            "## Instructions",
            "## Authentication",
            "## Tool Discipline",
            "## Output",
            "## Examples",
            "## Error Handling",
            "## Validation",
            "## Resources",
        )
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                metadata = frontmatter(body)
                self.assertEqual("2.0.0", metadata["version"])
                self.assertEqual("inherit", metadata["model"])
                self.assertEqual("high", metadata["effort"])
                self.assertIn("Use when", metadata["description"])
                self.assertIn("Trigger with", metadata["description"])
                for section in required_sections:
                    self.assertIn(section, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))
                descriptions.add(re.sub(r"\s+", " ", metadata["description"]))

                references = list((skill_file.parent / "references").glob("*.md"))
                self.assertEqual(["official-docs.md"], [item.name for item in references])
                evidence = references[0].read_text(encoding="utf-8")
                self.assertIn("Consulted on 2026-09-13", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 16)
                for fingerprint_half in (
                    "9212210e1dec664ca50aa2545fca475e",
                    "813087dca3654bbcb24d3baef1c3c32f",
                    "20f3a2274ca6a530f7f1ac1f7977d117",
                    "c85020a51236865c6638d115161b0103",
                    "bb0e42a8f3f788edfd9006bb4f8b1284",
                    "8f9c6cc48ad1a5ea20922e843a7681c3",
                    "58f386bf2cd8f96eef42ea43f29817fb",
                    "1973a0a8ad5dc31c1be659853ad9e9b9",
                ):
                    self.assertIn(fingerprint_half, evidence)

        self.assertEqual(18, len(headings))
        self.assertEqual(18, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(self.manifest["description"], self.package["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "runway-pack")
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertGreaterEqual(entry["verification"]["score"], 90)
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for unsupported in (
            "https://api.runwayml.com",
            "model='gen3a_turbo'",
            'model="gen3a_turbo"',
            "gen4_turbo    — Latest model, highest quality",
            "File exceeds limit | Resize to under 16MB",
            "Runway sends a generation webhook",
            "retry every error",
            "fixed requests per minute",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for current in (
            "https://api.dev.runwayml.com",
            "X-Runway-Version",
            "2024-11-06",
            "RUNWAYML_API_SECRET",
            "PENDING",
            "THROTTLED",
            "RUNNING",
            "SUCCEEDED",
            "FAILED",
            "CANCELLED",
            "five seconds",
            "24-48 hours",
            "rolling 24-hour",
            "30-day",
            "50 percent",
            "429",
            "502",
            "503",
            "504",
            "512-byte",
            "200-MB",
            "Model Router",
            "dryRun",
            "no native completion-webhook endpoint",
            "transactional outbox",
            "owned storage",
            "rollback",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
