"""Regression contract for the public Procore operator pack."""

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "procore-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "procore-ci-integration",
    "procore-common-errors",
    "procore-core-workflow-a",
    "procore-core-workflow-b",
    "procore-cost-tuning",
    "procore-data-handling",
    "procore-debug-bundle",
    "procore-deploy-integration",
    "procore-enterprise-rbac",
    "procore-hello-world",
    "procore-incident-runbook",
    "procore-install-auth",
    "procore-local-dev-loop",
    "procore-migration-deep-dive",
    "procore-multi-env-setup",
    "procore-observability",
    "procore-performance-tuning",
    "procore-prod-checklist",
    "procore-rate-limits",
    "procore-reference-architecture",
    "procore-sdk-patterns",
    "procore-security-basics",
    "procore-upgrade-migration",
    "procore-webhooks-events",
}


def frontmatter(body: str) -> dict:
    return yaml.safe_load(body.split("---", 2)[1])


class ProcorePackContractTest(unittest.TestCase):
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
                self.assertIn("Consulted: 2026-09-13", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 3)
                self.assertIn(
                    "fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318", evidence
                )

        self.assertEqual(24, len(headings))
        self.assertEqual(24, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(self.manifest["description"], self.package["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text()
        )
        entry = next(
            item for item in marketplace["plugins"] if item["name"] == "procore-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(24, entry["components"]["skills"])
        self.assertEqual(94, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for unsupported in (
            "OAuth2 client credentials flow",
            "For sandbox: https://sandbox.procore.com",
            "v1.0 to v1.1",
            "3600/hour",
            "raw debug bundle",
            "requests.post(\"https://login.procore.com/oauth/token\"",
            "status\": \"closed\"",
            "data.records",
            "unlimited requests",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for current in (
            "Authorization Code",
            "Client Credentials",
            "Developer Managed Service Account",
            "Procore-Company-Id",
            "Developer Sandbox",
            "On-Demand Sandbox",
            "Monthly Sandbox",
            "X-Rate-Limit-Remaining",
            "Retry-After",
            "best-effort",
            "reconciliation",
            "Integration Health",
            "API Call Activity Report",
            "Link",
            "origin_id",
            "rollback",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
