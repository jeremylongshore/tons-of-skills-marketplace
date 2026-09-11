"""Regression contract for the public SerpAPI operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "serpapi-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "serpapi-ci-integration",
    "serpapi-common-errors",
    "serpapi-core-workflow-a",
    "serpapi-core-workflow-b",
    "serpapi-cost-tuning",
    "serpapi-debug-bundle",
    "serpapi-deploy-integration",
    "serpapi-hello-world",
    "serpapi-install-auth",
    "serpapi-local-dev-loop",
    "serpapi-performance-tuning",
    "serpapi-prod-checklist",
    "serpapi-rate-limits",
    "serpapi-reference-architecture",
    "serpapi-sdk-patterns",
    "serpapi-security-basics",
    "serpapi-upgrade-migration",
    "serpapi-webhooks-events",
}


class SerpApiPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.expected_version = self.manifest["version"]

    def test_release_metadata_and_distinct_workflows(self) -> None:
        headings = set()
        descriptions = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("model: inherit", body)
                for section in (
                    "## Tool Discipline",
                    "## Current Contract",
                    "## Authentication",
                    "## Output",
                    "## Error Handling",
                    "## Example",
                ):
                    self.assertIn(section, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                description = re.search(r"^description: (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                self.assertIsNotNone(description)
                headings.add(heading.group(1))
                descriptions.add(description.group(1))

        self.assertEqual(len(self.skill_files), len(headings))
        self.assertEqual(len(self.skill_files), len(descriptions))

    def test_stale_or_fabricated_contracts_do_not_return(self) -> None:
        corpus = "\n".join(path.read_text() for path in self.skill_files)
        for stale in (
            "SERPAPI_API_KEY",
            "async_search",
            'client.search(engine="google", search_id=',
            "Result is already a dict",
            "Free (100/mo)",
            "Business ($200",
            "50K+/mo",
            "traditional webhooks",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, corpus)

    def test_current_contract_boundaries_are_explicit(self) -> None:
        corpus = "\n".join(path.read_text() for path in self.skill_files)
        lowered = corpus.lower()
        self.assertGreaterEqual(lowered.count("approval"), 18)
        self.assertGreaterEqual(corpus.count("SERPAPI_KEY"), 18)
        self.assertIn("`SerpResults` mapping", corpus)
        self.assertIn('"async": True', corpus)
        self.assertIn("client.search_archive(search_id=search_id)", corpus)
        self.assertIn("account_rate_limit_per_hour", corpus)
        self.assertIn("429 can mean", corpus)
        self.assertIn("expiring after 31 days", corpus)
        self.assertIn("does not define a generic callback webhook", corpus)

    def test_manifest_package_and_catalog_are_consistent(self) -> None:
        self.assertEqual("serpapi-pack", self.manifest["name"])
        self.assertEqual(1, self.manifest["keywords"].count("serpapi"))
        package = json.loads((PACK / "package.json").read_text())
        self.assertEqual(self.manifest["description"], package["description"])
        catalog = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(plugin for plugin in catalog["plugins"] if plugin["name"] == "serpapi-pack")
        self.assertEqual(self.manifest["version"], entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual({"score": 94, "grade": "A", "badge": "gold"}, {
            key: entry["verification"][key] for key in ("score", "grade", "badge")
        })


if __name__ == "__main__":
    unittest.main()
