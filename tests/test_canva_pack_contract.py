"""Regression contract for the public Canva operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "canva-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "canva-advanced-troubleshooting",
    "canva-architecture-variants",
    "canva-ci-integration",
    "canva-common-errors",
    "canva-core-workflow-a",
    "canva-core-workflow-b",
    "canva-cost-tuning",
    "canva-data-handling",
    "canva-debug-bundle",
    "canva-deploy-integration",
    "canva-enterprise-rbac",
    "canva-hello-world",
    "canva-incident-runbook",
    "canva-install-auth",
    "canva-known-pitfalls",
    "canva-load-scale",
    "canva-local-dev-loop",
    "canva-migration-deep-dive",
    "canva-multi-env-setup",
    "canva-observability",
    "canva-performance-tuning",
    "canva-policy-guardrails",
    "canva-prod-checklist",
    "canva-rate-limits",
    "canva-reference-architecture",
    "canva-reliability-patterns",
    "canva-sdk-patterns",
    "canva-security-basics",
    "canva-upgrade-migration",
    "canva-webhooks-events",
}


class CanvaPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
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

        self.assertEqual(30, len(headings))
        self.assertEqual(30, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(self.manifest["description"], self.package["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(
            item for item in marketplace["plugins"] if item["name"] == "canva-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(30, entry["components"]["skills"])
        self.assertGreaterEqual(entry["verification"]["score"], 90)
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "5000/24hr",
            "5,000/day",
            "X-RateLimit-Remaining",
            ".canva-tokens.json",
            "Token refresh failed: $RESPONSE",
            "POST /v1/designs/{id}/comment_threads",
            "valid 24 hours",
            "auto-deleted after 7 days",
            "There is no official SDK",
            "Set min instances to 1",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "Authorization Code",
            "SHA-256 PKCE",
            "single-use refresh token",
            "/rest/v1/",
            "date-based",
            "epoch",
            "preview",
            "public integrations",
            "connect/keys",
            "Ed25519",
            "operation identity",
            "explicit",
            "reconcile",
            "rollback",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
