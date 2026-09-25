"""Regression contract for the public Vast.ai operator pack."""

import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "vastai-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "vastai-ci-integration",
    "vastai-common-errors",
    "vastai-core-workflow-a",
    "vastai-core-workflow-b",
    "vastai-cost-tuning",
    "vastai-data-handling",
    "vastai-debug-bundle",
    "vastai-deploy-integration",
    "vastai-enterprise-rbac",
    "vastai-hello-world",
    "vastai-incident-runbook",
    "vastai-install-auth",
    "vastai-local-dev-loop",
    "vastai-migration-deep-dive",
    "vastai-multi-env-setup",
    "vastai-observability",
    "vastai-performance-tuning",
    "vastai-prod-checklist",
    "vastai-rate-limits",
    "vastai-reference-architecture",
    "vastai-sdk-patterns",
    "vastai-security-basics",
    "vastai-upgrade-migration",
    "vastai-webhooks-events",
}


def frontmatter(body: str) -> dict:
    return yaml.safe_load(body.split("---", 2)[1])


class VastaiPackContractTest(unittest.TestCase):
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
                self.assertIn("Consulted on 2026-09-13", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 3)
                self.assertIn(
                    "175a318c27750ea64da94f043dda39ec5cb26259", evidence
                )
                self.assertIn(
                    "1c6f8b61d3929a7ae423f89a3a0a53e4e9be02bc", evidence
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
            item for item in marketplace["plugins"] if item["name"] == "vastai-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(24, entry["components"]["skills"])
        self.assertGreaterEqual(entry["verification"]["score"], 90)
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for unsupported in (
            "StrictHostKeyChecking=no",
            "separate Vast.ai accounts per team",
            "application-level controls",
            "if Vast.ai introduces v1",
            "v1 — if",
            "YOUR_KEY_FROM_CLOUD_VAST_AI",
            "interruptible (spot) instances are 30-60% cheaper",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(item.read_text() for item in PACK.rglob("*.md"))
        for current in (
            "~/.config/vastai/vast_api_key",
            "VAST_API_KEY",
            "misc",
            "instance_read",
            "new_contract",
            "actual_status",
            "dlperf_usd",
            "storage charges",
            "bid search alone",
            "X-Vast-Signature-256",
            "X-Vast-Event-Id",
            "300 seconds",
            "at-least-once",
            "inactivity_timeout",
            "target_queue_time",
            "rolling update",
            "vastai_sdk",
            "checkpoint",
            "destroy",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
