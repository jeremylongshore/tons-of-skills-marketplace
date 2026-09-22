"""Regression contract for the public Exa operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "exa-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "exa-advanced-troubleshooting",
    "exa-architecture-variants",
    "exa-ci-integration",
    "exa-common-errors",
    "exa-core-workflow-a",
    "exa-core-workflow-b",
    "exa-cost-tuning",
    "exa-data-handling",
    "exa-debug-bundle",
    "exa-deploy-integration",
    "exa-enterprise-rbac",
    "exa-hello-world",
    "exa-incident-runbook",
    "exa-install-auth",
    "exa-known-pitfalls",
    "exa-load-scale",
    "exa-local-dev-loop",
    "exa-migration-deep-dive",
    "exa-multi-env-setup",
    "exa-observability",
    "exa-performance-tuning",
    "exa-policy-guardrails",
    "exa-prod-checklist",
    "exa-rate-limits",
    "exa-reference-architecture",
    "exa-reliability-patterns",
    "exa-sdk-patterns",
    "exa-security-basics",
    "exa-upgrade-migration",
    "exa-webhooks-events",
}


class ExaPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_structure(self) -> None:
        headings = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 1.12.0", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("Use when", normalized)
                self.assertIn("Trigger with", normalized)
                self.assertNotIn("!`", body)
                for required in (
                    "## Prerequisites",
                    "## Current Contract",
                    "## Authentication",
                    "## Instructions",
                    "## Tool Discipline",
                    "## Approval Boundaries",
                    "## Failure Modes",
                    "## Output",
                    "## Example",
                    "## Validation",
                    "## References",
                ):
                    self.assertIn(required, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                evidence = reference.read_text(encoding="utf-8")
                self.assertIn("Reviewed: 2026-09-12", evidence)
                self.assertIn("docs/llms-full.txt", evidence)
                self.assertIn("monitors-api-guide-for-coding-agents", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 18)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.12.0", self.manifest["version"])
        self.assertEqual("1.12.0", self.package["version"])
        self.assertEqual(30, len(self.skill_files))
        self.assertIn("Exa", self.manifest["description"])

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(item for item in marketplace["plugins"] if item["name"] == "exa-pack")
        self.assertEqual("1.12.0", entry["version"])
        self.assertEqual(30, entry["components"]["skills"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            '!`npm list exa-js',
            '!`node --version',
            '-H "x-api-key:',
            'type: "neural"',
            "10 QPS default",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_contracts_are_explicit(self) -> None:
        all_text = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for required in (
            "Authorization: Bearer",
            "auto, fast, instant, deep-lite, deep, and deep-reasoning",
            "per-URL statuses",
            "webhookSecret",
            "Exa-Signature",
            "SOC 2 Type II",
            "cache-only",
            "10 QPS",
            "100 QPS",
            "402",
            "503 SERVICE_OVERLOADED",
            "costDollars",
        ):
            with self.subTest(required=required):
                self.assertIn(required, all_text)


if __name__ == "__main__":
    unittest.main()
