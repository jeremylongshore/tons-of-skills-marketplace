"""Regression contract for the public RemoFirst operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "remofirst-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "remofirst-common-errors",
    "remofirst-core-workflow-a",
    "remofirst-core-workflow-b",
    "remofirst-debug-bundle",
    "remofirst-hello-world",
    "remofirst-install-auth",
    "remofirst-local-dev-loop",
    "remofirst-prod-checklist",
    "remofirst-rate-limits",
    "remofirst-sdk-patterns",
    "remofirst-security-basics",
    "remofirst-upgrade-migration",
}


class RemoFirstPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_distinct_reviewable_structure(self) -> None:
        headings = set()
        descriptions = set()
        required_sections = (
            "## Prerequisites",
            "## Current Contract",
            "## Instructions",
            "## Tool Discipline",
            "## Approval Boundaries",
            "## Output",
            "## Error Handling",
            "## Examples",
            "## Validation",
            "## Resources",
        )
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 2.0.0", body)
                self.assertIn("allowed-tools: Read,Glob,Grep,Write,Edit", body)
                self.assertIn("Use when", normalized)
                self.assertIn("Trigger with", normalized)
                for section in required_sections:
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
                self.assertGreaterEqual(evidence.count("https://"), 6)

        self.assertEqual(12, len(headings))
        self.assertEqual(12, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(self.manifest["description"], self.package["description"])
        self.assertIn("Evidence-backed", self.manifest["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "remofirst-pack")
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(12, entry["components"]["skills"])
        self.assertEqual(97, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_invented_api_contract_does_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "RemoFirstClient",
            "REMOFIRST_API_KEY",
            "api.remofirst.com/v1",
            'client.get("/employees"',
            'client.post("/payroll"',
            "401 Unauthorized",
            "429 Rate Limited",
            "API version upgrades",
            "Handle API rate limits",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "no public",
            "Workday",
            "ADP",
            "one-way inbound",
            "manually initiated",
            "Superuser",
            "two-factor authentication",
            "explicit human",
            "support",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
