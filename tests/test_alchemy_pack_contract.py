"""Regression contract for the public Alchemy operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "alchemy-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "alchemy-ci-integration",
    "alchemy-common-errors",
    "alchemy-core-workflow-a",
    "alchemy-core-workflow-b",
    "alchemy-cost-tuning",
    "alchemy-debug-bundle",
    "alchemy-deploy-integration",
    "alchemy-hello-world",
    "alchemy-install-auth",
    "alchemy-local-dev-loop",
    "alchemy-performance-tuning",
    "alchemy-prod-checklist",
    "alchemy-rate-limits",
    "alchemy-reference-architecture",
    "alchemy-sdk-patterns",
    "alchemy-security-basics",
    "alchemy-upgrade-migration",
    "alchemy-webhooks-events",
}


class AlchemyPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_distinct_reviewable_structure(self) -> None:
        headings = set()
        descriptions = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 2.0.0", body)
                self.assertIn("allowed-tools: Read,Glob,Grep,Write,Edit", body)
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
                    r"description: >-\n\s+(.+?)(?=\nallowed-tools:)", body, re.DOTALL
                )
                self.assertIsNotNone(heading)
                self.assertIsNotNone(description)
                headings.add(heading.group(1))
                descriptions.add(re.sub(r"\s+", " ", description.group(1)))

                references = list((skill_file.parent / "references").glob("*.md"))
                self.assertEqual(["official-docs.md"], [path.name for path in references])
                evidence = references[0].read_text(encoding="utf-8")
                self.assertIn("Reviewed: 2026-09-12", evidence)
                self.assertGreaterEqual(evidence.count("https://www.alchemy.com/"), 6)

        self.assertEqual(18, len(headings))
        self.assertEqual(18, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(18, len(self.skill_files))
        self.assertIn("Evidence-backed", self.manifest["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "alchemy-pack")
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual(98, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_obsolete_content_does_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "npm install alchemy-sdk",
            "pip install alchemy-sdk",
            "Network.MATIC_MUMBAI",
            "Mumbai (testnet)",
            "330 CU/s",
            "dashboard.alchemy.com/api/stats",
            "migrate to `alchemy-sdk`",
            "SDK works with ethers v5 and v6",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "archived and deprecated",
            "`viem`",
            "`@alchemy/wallet-apis`",
            "Admin access key",
            "rolling ten-second token-bucket",
            "`error.partialErrors`",
            "fresh, bounded retry",
            "HMAC-SHA256",
            "`X-Alchemy-Signature`",
            "short-lived JWTs",
            "explicit approval",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
