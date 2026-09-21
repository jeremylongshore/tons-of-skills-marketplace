"""Regression contract for the public Adobe operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "adobe-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "adobe-advanced-troubleshooting",
    "adobe-architecture-variants",
    "adobe-ci-integration",
    "adobe-common-errors",
    "adobe-core-workflow-a",
    "adobe-core-workflow-b",
    "adobe-cost-tuning",
    "adobe-data-handling",
    "adobe-debug-bundle",
    "adobe-deploy-integration",
    "adobe-enterprise-rbac",
    "adobe-hello-world",
    "adobe-incident-runbook",
    "adobe-install-auth",
    "adobe-known-pitfalls",
    "adobe-load-scale",
    "adobe-local-dev-loop",
    "adobe-migration-deep-dive",
    "adobe-multi-env-setup",
    "adobe-observability",
    "adobe-performance-tuning",
    "adobe-policy-guardrails",
    "adobe-prod-checklist",
    "adobe-rate-limits",
    "adobe-reference-architecture",
    "adobe-reliability-patterns",
    "adobe-sdk-patterns",
    "adobe-security-basics",
    "adobe-upgrade-migration",
    "adobe-webhooks-events",
}


class AdobePackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_distinct_reviewable_structure(self) -> None:
        headings = set()
        descriptions = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 1.8.0", body)
                self.assertIn("allowed-tools: Read,Glob,Grep,Write,Edit", body)
                self.assertIn("Use ", normalized)
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
                self.assertGreaterEqual(evidence.count("https://developer.adobe.com/"), 3)

        self.assertEqual(30, len(headings))
        self.assertEqual(30, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("1.8.0", self.manifest["version"])
        self.assertEqual("1.8.0", self.package["version"])
        self.assertEqual(30, len(self.skill_files))
        self.assertIn("evidence-backed", self.manifest["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "adobe-pack")
        self.assertEqual("1.8.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(30, entry["components"]["skills"])
        self.assertEqual(98, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_obsolete_or_invented_implementation_does_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "https://image.adobe.io/sensei/cutout",
            "@adobe/lightroom-apis",
            "~20 req/min",
            "3,000 events/5sec",
            "Access token expired (24h TTL)",
            "Latencies Benchmarks (Real-World)",
            "Adobe OAuth secrets use `p8_` prefix",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "OAuth Server-to-Server",
            "User Authentication",
            "Service Account JWT is deprecated",
            "Photoshop v1 reached end of life on 2026-07-31",
            "Firefly Services Lightroom API also reached end of life",
            "statusUrl",
            "signed URLs",
            "at least once",
            "AIO CLI v11",
            "explicit approval",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
