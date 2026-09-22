"""Regression contract for the public Fly.io operator pack."""

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "flyio-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "flyio-ci-integration",
    "flyio-common-errors",
    "flyio-core-workflow-a",
    "flyio-core-workflow-b",
    "flyio-cost-tuning",
    "flyio-debug-bundle",
    "flyio-deploy-integration",
    "flyio-hello-world",
    "flyio-install-auth",
    "flyio-local-dev-loop",
    "flyio-performance-tuning",
    "flyio-prod-checklist",
    "flyio-rate-limits",
    "flyio-reference-architecture",
    "flyio-sdk-patterns",
    "flyio-security-basics",
    "flyio-upgrade-migration",
    "flyio-webhooks-events",
}


def frontmatter(body: str) -> dict:
    return yaml.safe_load(body.split("---", 2)[1])


class FlyioPackContractTest(unittest.TestCase):
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
            "## Resources",
        )
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                metadata = frontmatter(body)
                self.assertEqual("2.0.0", metadata["version"])
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
                self.assertGreaterEqual(evidence.count("https://"), 4)
                self.assertIn("f0f857b0b1e8b46f082b90f5038be0cf", evidence)
                self.assertIn("0de0a0159f6923ed88b322b9d43b6e2d", evidence)
                self.assertIn("c9dfbd78f7451f9f8249380e1c140d5", evidence)
                self.assertIn("e0a3c9545e45f2313e8d77a5d675c292b", evidence)

        self.assertEqual(18, len(headings))
        self.assertEqual(18, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(self.manifest["description"], self.package["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "flyio-pack")
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual(95, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsupported_contracts_do_not_return(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for unsupported in (
            "| Machine create/delete | 10 req |",
            "Apps v1 (Nomad) to v2 (Machines)",
            "Webhook Signature Verification",
            "Fly Postgres with read replicas",
            "https://fly.io/docs/reference/deploy-tokens/",
            "platform across 30+ regions",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for current in (
            "https://api.machines.dev",
            "FLY_API_TOKEN",
            "app deploy token",
            "read-only",
            "one request per second",
            "burst up to three",
            "five requests per second",
            "100 per minute",
            "Machine instance version",
            "Managed Postgres",
            "6PN",
            "attached Machine volumes",
            "checkpoint",
            "reconciliation",
            "rollback",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
