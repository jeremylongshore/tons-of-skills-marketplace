"""Regression contract for the public CAST AI operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "castai-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "castai-ci-integration",
    "castai-common-errors",
    "castai-core-workflow-a",
    "castai-core-workflow-b",
    "castai-cost-tuning",
    "castai-debug-bundle",
    "castai-deploy-integration",
    "castai-hello-world",
    "castai-install-auth",
    "castai-local-dev-loop",
    "castai-performance-tuning",
    "castai-prod-checklist",
    "castai-rate-limits",
    "castai-reference-architecture",
    "castai-sdk-patterns",
    "castai-security-basics",
    "castai-upgrade-migration",
    "castai-webhooks-events",
}


class CastAIPackContractTest(unittest.TestCase):
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
            item for item in marketplace["plugins"] if item["name"] == "castai-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual(92, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "terraform refresh",
            "Full Access key",
            "castai-helm/castai-agent",
            "/audit-log?limit=",
            "/clusters/${CASTAI_CLUSTER_ID}/savings",
            "cidr: 0.0.0.0/0",
            'version = "~> 7',
            "Typical savings: 50-70%",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

        bare_reuse = re.compile(r"(?<!reset-then-)--reuse-values")
        self.assertIsNone(bare_reuse.search(markdown))

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "castctl",
            "umbrella",
            "X-API-Key",
            "X-CastAI-Organization-Id",
            "Immediate",
            "Deferred",
            "autoscaling/v2",
            "Audit log",
            "Kvisor",
            "reset-then-reuse-values",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
