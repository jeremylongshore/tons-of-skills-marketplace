"""Regression contract for the public Ideogram operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "ideogram-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "ideogram-ci-integration",
    "ideogram-common-errors",
    "ideogram-core-workflow-a",
    "ideogram-core-workflow-b",
    "ideogram-cost-tuning",
    "ideogram-data-handling",
    "ideogram-debug-bundle",
    "ideogram-deploy-integration",
    "ideogram-enterprise-rbac",
    "ideogram-hello-world",
    "ideogram-incident-runbook",
    "ideogram-install-auth",
    "ideogram-local-dev-loop",
    "ideogram-migration-deep-dive",
    "ideogram-multi-env-setup",
    "ideogram-observability",
    "ideogram-performance-tuning",
    "ideogram-prod-checklist",
    "ideogram-rate-limits",
    "ideogram-reference-architecture",
    "ideogram-sdk-patterns",
    "ideogram-security-basics",
    "ideogram-upgrade-migration",
    "ideogram-webhooks-events",
}


class IdeogramPackContractTest(unittest.TestCase):
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
                self.assertIn("version: 1.11.0", body)
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
                self.assertIn("openapi.json", evidence)
                self.assertIn("ideogram-api/webhooks.md", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 18)

        self.assertEqual(24, len(headings))
        self.assertEqual(24, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.11.0", self.manifest["version"])
        self.assertEqual("1.11.0", self.package["version"])
        self.assertEqual(24, len(self.skill_files))
        self.assertIn("Operator-grade Ideogram", self.manifest["description"])
        self.assertEqual(
            len(self.manifest["keywords"]), len(set(self.manifest["keywords"]))
        )

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(
            item for item in marketplace["plugins"] if item["name"] == "ideogram-pack"
        )
        self.assertEqual("1.11.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(24, entry["components"]["skills"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_and_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "all six API endpoints",
            "API is synchronous",
            "https://api.ideogram.ai/generate",
            "model or V_2",
            "Expire after ~1 hour",
            "V3 Rendering Speeds",
            "Authorization: Bearer",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_contracts_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "/v1/ideogram-v4/generate",
            "/v1/ideogram-v4/async/generate",
            "GET /v1/generations/",
            "Api-Key",
            "is_image_safe",
            "Ed25519",
            "v1/.well-known/jwks.json",
            "Owner, Admin, and Member",
            "10 in-flight requests",
            "10–100 images",
            "[y_min,x_min,y_max,x_max]",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
