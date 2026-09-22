"""Regression guard for owner-authorized external mirror retirement."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOMBSTONES = ROOT / "freshie/retired-external-mirrors.json"

EXPECTED = {
    "promptbook": ("promptbookgg/claude-code-plugin", "promptbookgg"),
    "executive-assistant-skills": ("mgonto/executive-assistant-skills", "mgonto"),
    "local-tts": ("vdk888/local-tts", "vdk888"),
    "boycott-filter": ("vdk888/boycott-filter", "vdk888"),
    "claude-reflect": ("bayramannakov/claude-reflect", "BayramAnnakov"),
    "hyperfocus": ("nextor2k/hyperfocus", "nextor2k"),
}

PLUGIN_PATHS = {
    "promptbook": "plugins/business-tools/promptbook",
    "executive-assistant-skills": "plugins/business-tools/executive-assistant-skills",
    "local-tts": "plugins/ai-ml/local-tts",
    "boycott-filter": "plugins/community/boycott-filter",
    "claude-reflect": "plugins/community/claude-reflect",
    "hyperfocus": "plugins/productivity/hyperfocus",
}

CURATED_NAMES = {
    "action-items-todoist",
    "boycott-filter",
    "claude-reflect",
    "doctor",
    "email-drafting",
    "executive-assistant-skills__meeting-prep",
    "executive-digest",
    "hyperfocus",
    "local-tts",
    "setup",
    "todoist-due-drafts",
}


class ExternalMirrorRetirementTests(unittest.TestCase):
    def test_tombstones_are_complete_and_attributed(self) -> None:
        data = json.loads(TOMBSTONES.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["authority"]["bead"], "claude-3zu7")
        self.assertEqual(data["authority"]["superseded_pr"], 1483)

        mirrors = {row["name"]: row for row in data["mirrors"]}
        self.assertEqual(set(mirrors), set(EXPECTED))
        for name, (repository, github) in EXPECTED.items():
            with self.subTest(name=name):
                row = mirrors[name]
                self.assertEqual(
                    row["upstream_repository"], f"https://github.com/{repository}"
                )
                self.assertEqual(row["attribution"]["github"], github)
                self.assertRegex(row["upstream_commit"], r"^[0-9a-f]{40}$")
                self.assertEqual(row["disposition"], "RETIRED")
                self.assertTrue(row["reason_codes"])
                self.assertTrue(row["relisting_requirement"])

        executive = mirrors["executive-assistant-skills"]
        self.assertEqual(executive["observed_license"], "NOASSERTION")
        self.assertEqual(executive["previous_catalog_license_claim"], "MIT")

    def test_plugin_and_curated_bytes_are_absent(self) -> None:
        for relative in PLUGIN_PATHS.values():
            with self.subTest(path=relative):
                path = ROOT / relative
                self.assertFalse(path.exists() or path.is_symlink())

        for name in CURATED_NAMES:
            with self.subTest(curated=name):
                path = ROOT / "skills/.curated" / name
                self.assertFalse(path.exists() or path.is_symlink())

    def test_canonical_registries_cannot_reintroduce_retired_mirrors(self) -> None:
        catalog = json.loads(
            (ROOT / ".claude-plugin/marketplace.extended.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(set(EXPECTED).isdisjoint(row["name"] for row in catalog["plugins"]))

        spotlights = json.loads(
            (ROOT / "marketplace/src/data/spotlights.json").read_text(encoding="utf-8")
        )
        spotlight_slugs = {spotlights["spotlight"]["pluginSlug"]}
        spotlight_slugs.update(row["pluginSlug"] for row in spotlights["hallOfFame"])
        self.assertTrue(set(EXPECTED).isdisjoint(spotlight_slugs))

        sources = (ROOT / "sources.yaml").read_text(encoding="utf-8")
        for name in EXPECTED:
            self.assertIsNone(
                re.search(rf"^\s{{2}}- name:\s*{re.escape(name)}\s*$", sources, re.MULTILINE)
            )

        lock = json.loads((ROOT / "sources.lock.json").read_text(encoding="utf-8"))
        self.assertTrue(set(EXPECTED).isdisjoint(lock["sources"]))

    def test_current_generated_and_public_surfaces_are_clean(self) -> None:
        current_surfaces = (
            ".claude-plugin/marketplace.json",
            "README.md",
            "freshie/disposition-ledger.json",
            "freshie/grades.csv",
            "marketplace/src/data/catalog.json",
            "marketplace/src/data/npm-stats.json",
            "marketplace/src/data/skills-catalog.json",
            "marketplace/src/data/skills-index.json",
            "marketplace/src/data/unified-search-index.json",
            "skills/.curated/MANIFEST.json",
        )
        for name, plugin_path in PLUGIN_PATHS.items():
            forbidden = (f'"name": "{name}"', f'"pluginSlug": "{name}"', plugin_path)
            for relative in current_surfaces:
                contents = (ROOT / relative).read_text(encoding="utf-8")
                for needle in forbidden:
                    with self.subTest(name=name, path=relative, needle=needle):
                        self.assertTrue(
                            needle not in contents,
                            f"retired mirror leaked into {relative}: {needle}",
                        )

            content_record = ROOT / "marketplace/src/content/plugins" / f"{name}.json"
            self.assertFalse(content_record.exists() or content_record.is_symlink())


if __name__ == "__main__":
    unittest.main()
