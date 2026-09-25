"""Regression contract for the public Flexport operator pack."""

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "flexport-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "flexport-ci-integration",
    "flexport-common-errors",
    "flexport-core-workflow-a",
    "flexport-core-workflow-b",
    "flexport-cost-tuning",
    "flexport-data-handling",
    "flexport-debug-bundle",
    "flexport-deploy-integration",
    "flexport-enterprise-rbac",
    "flexport-hello-world",
    "flexport-incident-runbook",
    "flexport-install-auth",
    "flexport-local-dev-loop",
    "flexport-migration-deep-dive",
    "flexport-multi-env-setup",
    "flexport-observability",
    "flexport-performance-tuning",
    "flexport-prod-checklist",
    "flexport-rate-limits",
    "flexport-reference-architecture",
    "flexport-sdk-patterns",
    "flexport-security-basics",
    "flexport-upgrade-migration",
    "flexport-webhooks-events",
}


def frontmatter(body: str) -> dict:
    return yaml.safe_load(body.split("---", 2)[1])


class FlexportPackContractTest(unittest.TestCase):
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
            item for item in marketplace["plugins"] if item["name"] == "flexport-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(24, entry["components"]["skills"])
        self.assertGreaterEqual(entry["verification"]["score"], 90)
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for unsupported in (
            "Flexport-Version: 2",
            "/v2/shipments",
            "/freight_invoices",
            "data.records",
            "shipment.milestone",
            "X-RateLimit-Remaining",
            "5 requests per second",
            "fp_dev_",
            "dual-write",
            "right to erasure",
            "X-Hub-Signature header",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for current in (
            "https://api.flexport.com",
            "Flexport-Version",
            "client credentials",
            "24 hours",
            "10 per day",
            "https://mcp.flexport.com/mcp",
            "JSON-RPC",
            "X-Hub-Signature-256",
            "/shipment#created",
            "/invoices",
            "operation key",
            "reconcile",
            "rollback",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
