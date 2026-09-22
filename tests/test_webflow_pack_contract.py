"""Regression contract for the public Webflow operator pack."""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "webflow-pack"
SKILLS = PACK / "skills"


class WebflowPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(24, len(self.skill_files))
        manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.expected_version = manifest["version"]

    def test_all_skills_have_release_metadata_and_official_references(self) -> None:
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn(f"version: {self.expected_version}", body)
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("## Authentication", body)
                self.assertIn("## Approval Boundaries", body)
                self.assertIn("## Examples", body)

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("Checked on 2026-09-10", reference_body)
                self.assertGreaterEqual(reference_body.count("https://developers.webflow.com"), 3)

    def test_stale_and_unsafe_shortcuts_do_not_return(self) -> None:
        markdown = "\n".join(path.read_text(encoding="utf-8") for path in PACK.rglob("*.md"))
        for stale in (
            "SDK v1-to-v3",
            "Current version: 3.x",
            "Free and Unlimited",
            "publish-on-merge",
            "WEBFLOW_WEBHOOK_SECRET",
            "prod-token-here",
            "up to 100 items",
            "all 11 trigger types",
        ):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, markdown)

        self.assertNotRegex(markdown, re.compile(r"npm install .*@(?:latest|next)"))

    def test_current_operator_boundaries_are_preserved(self) -> None:
        rate_limits = (SKILLS / "webflow-rate-limits" / "SKILL.md").read_text()
        for expected in (
            "60 requests/minute",
            "120 for CMS, Ecommerce, and Business",
            "one successful publish per minute",
            "`MISS` or `BYPASS`",
        ):
            self.assertIn(expected, rate_limits)

        webhooks = (SKILLS / "webflow-webhooks-events" / "SKILL.md").read_text()
        for expected in (
            "dashboard-created webhooks lack",
            "five-minute window",
            "up to three additional times",
        ):
            self.assertIn(expected, webhooks)

        deployment = (SKILLS / "webflow-deploy-integration" / "SKILL.md").read_text()
        self.assertIn("site-attached apps", deployment)
        self.assertIn("terminal deployment status", deployment)
        self.assertIn("GitHub-linked deployment", deployment)

        security = (SKILLS / "webflow-security-basics" / "SKILL.md").read_text()
        self.assertIn("365 inactive days", security)
        self.assertIn("SDK verifier", security)


if __name__ == "__main__":
    unittest.main()
