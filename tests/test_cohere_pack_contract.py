"""Regression contract for the public Cohere v2 operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "cohere-pack"
SKILLS = PACK / "skills"

EXPECTED_SKILLS = {
    "cohere-ci-integration",
    "cohere-common-errors",
    "cohere-core-workflow-a",
    "cohere-core-workflow-b",
    "cohere-cost-tuning",
    "cohere-data-handling",
    "cohere-debug-bundle",
    "cohere-deploy-integration",
    "cohere-enterprise-rbac",
    "cohere-hello-world",
    "cohere-incident-runbook",
    "cohere-install-auth",
    "cohere-local-dev-loop",
    "cohere-migration-deep-dive",
    "cohere-multi-env-setup",
    "cohere-observability",
    "cohere-performance-tuning",
    "cohere-prod-checklist",
    "cohere-rate-limits",
    "cohere-reference-architecture",
    "cohere-sdk-patterns",
    "cohere-security-basics",
    "cohere-upgrade-migration",
    "cohere-webhooks-events",
}


class CoherePackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text())
        self.expected_version = manifest["version"]

    def test_all_skills_have_release_metadata_and_official_references(self) -> None:
        headings = set()
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn(
                    "allowed-tools: Read, Glob, Grep, WebFetch, Write, Edit", body
                )
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("## Tool Discipline", body)
                self.assertIn("## Current Contract", body)
                self.assertIn("## Authentication", body)
                self.assertIn("## Approval Boundaries", body)
                self.assertIn("## Error Handling", body)
                self.assertIn("## Examples", body)

                heading = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(heading)
                headings.add(heading.group(1))

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("2026-09-11", reference_body)
                self.assertGreaterEqual(reference_body.count("https://"), 20)

        self.assertEqual(len(self.skill_files), len(headings))

    def test_stale_or_invented_contracts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text() for path in PACK.rglob("*.md"))
        for stale in (
            "production: 1000 calls/min",
            "production: 1000 requests/min",
            "no built-in RBAC",
            "no built-in RBAC or SSO",
            "register data connectors for RAG",
            "rerank-english-v3.0",
            "command-r-plus-08-2024",
            "Command R7B or newer model (required for tool use)",
            "Latency Benchmarks (Typical)",
            "dump all environment variables",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

    def test_current_cohere_contracts_are_preserved(self) -> None:
        references = (
            SKILLS / "cohere-install-auth" / "references" / "official-docs.md"
        ).read_text()
        self.assertIn("`cohere-ai@8.1.0`", references)
        self.assertIn("`cohere==7.1.1`", references)
        self.assertIn("`command-a-plus-05-2026`", references)
        self.assertIn("`rerank-v4.0-pro`", references)

        rag = (SKILLS / "cohere-core-workflow-a" / "SKILL.md").read_text()
        self.assertIn("`input_type=search_document`", rag)
        self.assertIn("`input_type=search_query`", rag)
        self.assertIn("citation", rag.lower())

        tools = (SKILLS / "cohere-core-workflow-b" / "SKILL.md").read_text()
        self.assertIn("JSON Schema", tools)
        self.assertIn("`tool_call_id`", tools)
        self.assertIn("max-iterations=4", tools)

        events = (SKILLS / "cohere-webhooks-events" / "SKILL.md").read_text()
        self.assertIn("not an inbound signed webhook surface", events)
        self.assertIn("Managed v1 connectors are deprecated", events)

        rbac = (SKILLS / "cohere-enterprise-rbac" / "SKILL.md").read_text()
        self.assertIn("Owner and User roles", rbac)
        self.assertIn("provider roles alone are not application RBAC", rbac)


if __name__ == "__main__":
    unittest.main()
