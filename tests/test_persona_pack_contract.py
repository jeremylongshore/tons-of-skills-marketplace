"""Regression contract for the public Persona operator pack."""

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "persona-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "persona-ci-integration",
    "persona-common-errors",
    "persona-core-workflow-a",
    "persona-core-workflow-b",
    "persona-cost-tuning",
    "persona-debug-bundle",
    "persona-deploy-integration",
    "persona-hello-world",
    "persona-install-auth",
    "persona-local-dev-loop",
    "persona-performance-tuning",
    "persona-prod-checklist",
    "persona-rate-limits",
    "persona-reference-architecture",
    "persona-sdk-patterns",
    "persona-security-basics",
    "persona-upgrade-migration",
    "persona-webhooks-events",
}


def frontmatter(body: str) -> dict:
    return yaml.safe_load(body.split("---", 2)[1])


class PersonaPackContractTest(unittest.TestCase):
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
                self.assertGreaterEqual(evidence.count("https://"), 12)
                for fingerprint_half in (
                    "63e5f1079542954e91f4f597ba40a72d",
                    "4841c339021bcda28aa6acf716551d5f",
                    "9af3d9ba3b179ef6d5d5b85dbf924988",
                    "5a242599ef09e55130c9652e5ce8c9d5",
                    "a674a82497f5c4e275be680324fc84d04",
                    "ae672214c1ee78a32cf774434ec65db",
                    "166d3e485847ca3273a88fe6667ae4ea",
                    "6d7d7924b2c57f6d5cf141b96dd5cf32",
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
        entry = next(item for item in marketplace["plugins"] if item["name"] == "persona-pack")
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual(95, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for unsupported in (
            "https://withpersona.com/api/v1",
            "PERSONA_API_VERSION=2023-01-05",
            "| sed 's/",
            "HMAC-SHA256(rawBody",
            "reference-id` to associate",
            "QuotaLimit-Remaining",
            "parallel verification polling",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for current in (
            "https://api.withpersona.com/api/v1",
            "2025-12-08",
            "Persona-Version",
            "Idempotency-Key",
            "auto-create-account-reference-id",
            "meta.session-token",
            "25",
            "timestamp + '.' + rawBody",
            "multiple `v1`",
            "constant time",
            "created-at",
            "300 requests per minute",
            "RateLimit-Remaining",
            "Quota-Remaining",
            "15 percent",
            "5, 10, 20, and 40",
            "unknown",
            "irreversible",
            "reconciliation",
            "rollback",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
