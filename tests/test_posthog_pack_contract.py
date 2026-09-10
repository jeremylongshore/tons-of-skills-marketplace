"""Regression contract for the public PostHog operator pack."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "posthog-pack"
SKILLS = PACK / "skills"


class PostHogPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(24, len(self.skill_files))

    def test_all_skills_have_release_metadata_and_official_references(self) -> None:
        for skill_file in self.skill_files:
            with self.subTest(skill=skill_file.parent.name):
                body = skill_file.read_text(encoding="utf-8")
                self.assertIn("version: 1.13.0", body)
                self.assertIn("Use when", body)
                self.assertIn("Trigger with", body)
                self.assertIn("argument-hint:", body)
                self.assertIn("## Examples", body)
                self.assertNotRegex(body, r"(?m)^!`")

                reference = skill_file.parent / "references" / "official-docs.md"
                self.assertTrue(reference.is_file())
                reference_body = reference.read_text(encoding="utf-8")
                self.assertIn("Checked on 2026-09-09", reference_body)
                self.assertGreaterEqual(reference_body.count("https://posthog.com"), 2)

    def test_removed_stale_hosts_endpoints_and_local_eval_credentials(self) -> None:
        markdown = "\n".join(
            path.read_text(encoding="utf-8") for path in PACK.rglob("*.md")
        )
        self.assertNotIn("app.posthog.com/api", markdown)
        self.assertNotRegex(markdown, r"/(?:capture|decide)/")
        self.assertNotRegex(
            markdown,
            r"personalApiKey:\s*process\.env\.POSTHOG_PERSONAL_API_KEY",
        )
        self.assertNotRegex(
            markdown,
            r"personal_api_key\s*=\s*os\.getenv\(['\"]POSTHOG_PERSONAL_API_KEY",
        )

    def test_current_operator_boundaries_are_preserved(self) -> None:
        rate_limits = (SKILLS / "posthog-rate-limits" / "SKILL.md").read_text()
        for expected in (
            "240/min, 1200/hour",
            "60/min, 300/hour",
            "2400/hour",
            "600/min",
            "480/min, 4800/hour",
            "whole PostHog team",
        ):
            self.assertIn(expected, rate_limits)

        migration = (SKILLS / "posthog-migration-deep-dive" / "SKILL.md").read_text()
        self.assertIn("historicalMigration: true", migration)
        self.assertIn('"historical_migration": true', migration)

        cost = (SKILLS / "posthog-cost-tuning" / "SKILL.md").read_text()
        self.assertNotIn("Free Tiers (2025)", cost)
        self.assertNotIn("Cost Reduction Estimates", cost)

        deploy = (SKILLS / "posthog-deploy-integration" / "SKILL.md").read_text()
        self.assertNotIn("docker-compose.hobby", deploy)
        self.assertIn("hobbyist, single-machine option", deploy)

        upgrade = (SKILLS / "posthog-upgrade-migration" / "SKILL.md").read_text()
        self.assertNotIn("posthog-node@latest", upgrade)
        self.assertNotIn("posthog-js@latest", upgrade)
        self.assertIn("POSTHOG_NODE_PREVIOUS", upgrade)
        self.assertIn("POSTHOG_JS_PREVIOUS", upgrade)


if __name__ == "__main__":
    unittest.main()
