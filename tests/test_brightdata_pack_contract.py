"""Regression contract for the public Bright Data operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "brightdata-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "brightdata-ci-integration",
    "brightdata-common-errors",
    "brightdata-core-workflow-a",
    "brightdata-core-workflow-b",
    "brightdata-cost-tuning",
    "brightdata-debug-bundle",
    "brightdata-deploy-integration",
    "brightdata-hello-world",
    "brightdata-install-auth",
    "brightdata-local-dev-loop",
    "brightdata-performance-tuning",
    "brightdata-prod-checklist",
    "brightdata-rate-limits",
    "brightdata-reference-architecture",
    "brightdata-sdk-patterns",
    "brightdata-security-basics",
    "brightdata-upgrade-migration",
    "brightdata-webhooks-events",
}


class BrightDataPackContractTest(unittest.TestCase):
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
                self.assertIn("Checked 2026-09-13", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 4)

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
            item for item in marketplace["plugins"] if item["name"] == "brightdata-pack"
        )
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(18, entry["components"]["skills"])
        self.assertEqual(93, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_unsafe_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "api/v2/status.json",
            "get_active_zones",
            "retries on non-2xx",
            "limit: '50mb'",
            "known IPs",
            "Rotate quarterly",
            "No SDK",
            "Web Unlocker v1",
            "Datasets v2",
            "target_site_blocked",
            "X-Luminati",
            "headers?.['x-luminati",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "Proxy-Status",
            "x-brd-err-code",
            "Browser API",
            "BrightDataClient",
            "/datasets/v3/trigger",
            "/datasets/v3/progress/SNAPSHOT_ID",
            "/datasets/v3/snapshot/SNAPSHOT_ID",
            "/datasets/v3/deliver/SNAPSHOT_ID",
            "geo.brdtest.com",
            "Acceptable use",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)

        legacy_mentions = [
            str(path.relative_to(PACK))
            for path in PACK.rglob("*.md")
            if "x-luminati" in path.read_text().lower()
        ]
        self.assertEqual(
            [
                "skills/brightdata-common-errors/SKILL.md",
                "skills/brightdata-common-errors/references/official-docs.md",
                "skills/brightdata-hello-world/references/official-docs.md",
                "skills/brightdata-upgrade-migration/SKILL.md",
                "skills/brightdata-upgrade-migration/references/official-docs.md",
            ],
            sorted(legacy_mentions),
        )


if __name__ == "__main__":
    unittest.main()
