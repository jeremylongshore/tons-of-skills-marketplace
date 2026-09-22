"""Regression contract for the public QuickNode operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "quicknode-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "quicknode-ci-integration",
    "quicknode-common-errors",
    "quicknode-core-workflow-a",
    "quicknode-core-workflow-b",
    "quicknode-cost-tuning",
    "quicknode-debug-bundle",
    "quicknode-deploy-integration",
    "quicknode-hello-world",
    "quicknode-install-auth",
    "quicknode-local-dev-loop",
    "quicknode-performance-tuning",
    "quicknode-prod-checklist",
    "quicknode-rate-limits",
    "quicknode-reference-architecture",
    "quicknode-sdk-patterns",
    "quicknode-security-basics",
    "quicknode-upgrade-migration",
    "quicknode-webhooks-events",
}


class QuickNodePackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*" + "/SKILL.md"))
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
                    r"description: '(.+?)'\nallowed-tools:", body, re.DOTALL
                )
                self.assertIsNotNone(heading)
                self.assertIsNotNone(description)
                headings.add(heading.group(1))
                descriptions.add(re.sub(r"\s+", " ", description.group(1)))

                references = list((skill_file.parent / "references").glob("*.md"))
                self.assertEqual(["official-docs.md"], [path.name for path in references])
                evidence = references[0].read_text(encoding="utf-8")
                self.assertIn("Consulted: 2026-09-13", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 3)

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
            item for item in marketplace["plugins"] if item["name"] == "quicknode-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual(92, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "RPC endpoints for 77+ chains",
            "Auth via API key in endpoint URL",
            "/docs/quicknode-sdk/getting-started",
            "Streams (webhooks for on-chain events)",
            "Hardhat tests against QuickNode endpoints",
            "Typical savings",
            "unlimited requests",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "QuicknodeSdk",
            "QN_SDK__API_KEY",
            "x-api-key",
            "x-token",
            "-32007",
            "-32008",
            "-32011",
            "-32604",
            "-32611",
            "p95",
            "HMAC",
            "mTLS",
            "duplicates",
            "rollback",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
