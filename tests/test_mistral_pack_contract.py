"""Regression contract for the public Mistral operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "mistral-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "mistral-ci-integration",
    "mistral-common-errors",
    "mistral-core-workflow-a",
    "mistral-core-workflow-b",
    "mistral-cost-tuning",
    "mistral-data-handling",
    "mistral-debug-bundle",
    "mistral-deploy-integration",
    "mistral-enterprise-rbac",
    "mistral-hello-world",
    "mistral-incident-runbook",
    "mistral-install-auth",
    "mistral-local-dev-loop",
    "mistral-migration-deep-dive",
    "mistral-multi-env-setup",
    "mistral-observability",
    "mistral-performance-tuning",
    "mistral-prod-checklist",
    "mistral-rate-limits",
    "mistral-reference-architecture",
    "mistral-sdk-patterns",
    "mistral-security-basics",
    "mistral-upgrade-migration",
    "mistral-webhooks-events",
}


class MistralPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_reviewable_structure(self) -> None:
        headings = set()
        descriptions = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 1.14.0", body)
                self.assertIn("argument-hint:", body)
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
                    r"description: >-\n\s+(.+?)(?=\nallowed-tools:)",
                    body,
                    re.DOTALL,
                )
                self.assertIsNotNone(heading)
                self.assertIsNotNone(description)
                headings.add(heading.group(1))
                descriptions.add(re.sub(r"\s+", " ", description.group(1)))

                evidence = (
                    skill_file.parent / "references" / "official-docs.md"
                ).read_text(encoding="utf-8")
                self.assertIn("Reviewed: 2026-09-12", evidence)
                self.assertGreaterEqual(evidence.count("https://docs.mistral.ai/"), 5)

        self.assertEqual(24, len(headings))
        self.assertEqual(24, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.14.0", self.manifest["version"])
        self.assertEqual("1.14.0", self.package["version"])
        self.assertEqual(24, len(self.skill_files))
        self.assertIn("Operator-grade Mistral", self.manifest["description"])

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(
            item for item in marketplace["plugins"] if item["name"] == "mistral-pack"
        )
        self.assertEqual("1.14.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(24, entry["components"]["skills"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_and_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "Q1 2025",
            "as of 2025",
            "50% off",
            "1024 dimensions",
            "256k",
            "Input $/M",
            "Output $/M",
            "generic webhook callback endpoint",
            "no free tier",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_contracts_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "https://api.mistral.ai",
            "Authorization: Bearer",
            "POST /v1/chat/completions",
            "POST /v1/embeddings",
            "GET /v1/workflows/events/stream",
            "Public Preview",
            "Zero Data Retention",
            "workspace",
            "stateful",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
