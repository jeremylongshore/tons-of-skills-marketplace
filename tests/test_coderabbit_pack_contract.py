"""Regression contract for the public CodeRabbit operator pack."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "coderabbit-pack"
SKILLS = PACK / "skills"
EXPECTED = {
    "coderabbit-ci-integration",
    "coderabbit-common-errors",
    "coderabbit-core-workflow-a",
    "coderabbit-core-workflow-b",
    "coderabbit-cost-tuning",
    "coderabbit-data-handling",
    "coderabbit-debug-bundle",
    "coderabbit-deploy-integration",
    "coderabbit-enterprise-rbac",
    "coderabbit-hello-world",
    "coderabbit-incident-runbook",
    "coderabbit-install-auth",
    "coderabbit-local-dev-loop",
    "coderabbit-migration-deep-dive",
    "coderabbit-multi-env-setup",
    "coderabbit-observability",
    "coderabbit-performance-tuning",
    "coderabbit-prod-checklist",
    "coderabbit-rate-limits",
    "coderabbit-reference-architecture",
    "coderabbit-sdk-patterns",
    "coderabbit-security-basics",
    "coderabbit-upgrade-migration",
    "coderabbit-webhooks-events",
}


class CodeRabbitPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.package = json.loads((PACK / "package.json").read_text())

    def test_release_alignment_and_reviewable_structure(self) -> None:
        headings: set[str] = set()
        descriptions: set[str] = set()
        required_sections = (
            "## Prerequisites",
            "## Current Contract",
            "## Authentication",
            "## Instructions",
            "## Tool Discipline",
            "## Approval Boundaries",
            "## Output",
            "## Error Handling",
            "## Examples",
            "## Validation",
            "## Resources",
        )
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                normalized = re.sub(r"\s+", " ", body)
                self.assertIn("version: 2.0.0", body)
                self.assertIn("allowed-tools: Read,Glob,Grep,Write,Edit", body)
                self.assertIn("Use when", normalized)
                self.assertIn("Trigger with", normalized)
                for section in required_sections:
                    self.assertIn(section, body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                description = re.search(r"description: >-\n\s+(.+?)(?=\nallowed-tools:)", body, re.DOTALL)
                self.assertIsNotNone(heading)
                self.assertIsNotNone(description)
                headings.add(heading.group(1))
                descriptions.add(re.sub(r"\s+", " ", description.group(1)))

                references = list((skill_file.parent / "references").glob("*.md"))
                self.assertEqual(["official-docs.md"], [path.name for path in references])
                evidence = references[0].read_text(encoding="utf-8")
                self.assertIn("Reviewed: 2026-09-12", evidence)
                self.assertGreaterEqual(evidence.count("https://"), 6)

        self.assertEqual(24, len(headings))
        self.assertEqual(24, len(descriptions))

    def test_pack_metadata_is_aligned(self) -> None:
        self.assertEqual("2.0.0", self.manifest["version"])
        self.assertEqual("2.0.0", self.package["version"])
        self.assertEqual(self.manifest["description"], self.package["description"])
        self.assertEqual(len(self.manifest["keywords"]), len(set(self.manifest["keywords"])))

        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.extended.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == "coderabbit-pack")
        self.assertEqual("2.0.0", entry["version"])
        self.assertEqual(self.manifest["description"], entry["description"])
        self.assertEqual(24, entry["components"]["skills"])
        self.assertEqual(98, entry["verification"]["score"])
        self.assertEqual("A", entry["verification"]["grade"])

    def test_stale_or_invented_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for unsupported in (
            "CodeRabbit posts a GitHub Check on each PR",
            "Free: 1, Pro: 5, Enterprise: custom",
            "$15/seat/month",
            "Reviews take 2-15 min",
            "CodeRabbit reads config from the PR's base branch",
            "CodeRabbit reads from base branch",
            "Config not on the base branch",
            "cli.coderabbit.ai/install.sh",
            "X-Hub-Signature-256",
            "Concurrent reviews per org",
        ):
            with self.subTest(unsupported=unsupported):
                self.assertNotIn(unsupported, markdown)

    def test_current_public_boundaries_are_explicit(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for current in (
            "feature branch",
            "base_branches",
            "request_changes_workflow",
            "x-coderabbitai-api-key",
            "Admin, Member, and Billing Admin",
            "usage-based add-on",
            "Git provider",
            "explicit human approval",
            "independent CI",
        ):
            with self.subTest(current=current):
                self.assertIn(current, markdown)


if __name__ == "__main__":
    unittest.main()
