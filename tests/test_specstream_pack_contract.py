"""Regression contract and offline payload tests for plugins/saas-packs/specstream-pack."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import unittest
from unittest.mock import patch
import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "specstream-pack"
SKILLS = PACK / "skills"
VALIDATOR_SCRIPT = PACK / "scripts" / "validate_specstream_payload.py"

EXPECTED_SKILLS = {
    "specstream-search-and-dropins",
    "specstream-extract",
    "specstream-tables",
    "specstream-schedules",
    "specstream-mcp-setup",
}

REQUIRED_FRONTMATTER = {
    "name",
    "description",
    "allowed-tools",
    "version",
    "author",
    "license",
    "compatibility",
    "tags",
}

REQUIRED_SECTIONS = (
    "## Overview",
    "## Prerequisites",
    "## Instructions",
    "## Output",
    "## Error Handling",
    "## Examples",
    "## Resources",
)


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_specstream_payload", VALIDATOR_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SpecStreamPackContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertEqual(EXPECTED_SKILLS, {path.parent.name for path in self.skill_files})
        self.manifest = json.loads((PACK / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.validator = _load_validator_module()

    def test_required_docs_and_license_exist(self) -> None:
        for rel in ("LICENSE", "README.md", "docs/PRD.md", "docs/ADR.md", "docs/ONE-PAGER.md"):
            with self.subTest(path=rel):
                target = PACK / rel
                self.assertTrue(target.is_file(), f"Missing required file: {rel}")
                self.assertGreater(len(target.read_text(encoding="utf-8").strip()), 50)

    def test_skills_frontmatter_sections_and_references(self) -> None:
        headings = set()
        for skill_file in self.skill_files:
            skill_name = skill_file.parent.name
            with self.subTest(skill=skill_name):
                raw = skill_file.read_text(encoding="utf-8")
                match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.DOTALL)
                self.assertIsNotNone(match, f"Missing YAML frontmatter in {skill_file}")
                fm = yaml.safe_load(match.group(1))
                body = match.group(2)

                self.assertTrue(REQUIRED_FRONTMATTER.issubset(fm.keys()))
                self.assertEqual(skill_name, fm["name"])
                self.assertEqual(self.manifest["version"], fm["version"])
                self.assertEqual("Designed for Claude Code", fm["compatibility"])
                self.assertIn("Use when", fm["description"])
                self.assertIn("Trigger with", fm["description"])

                tools = [t.strip() for t in str(fm["allowed-tools"]).split(",")]
                self.assertNotIn("Bash", tools)
                self.assertNotIn("WebFetch", tools)
                self.assertNotIn("WebSearch", tools)

                for section in REQUIRED_SECTIONS:
                    self.assertIn(section, body)

                ref_doc = skill_file.parent / "references" / "api-contract.md"
                self.assertTrue(ref_doc.is_file(), f"Missing reference doc for {skill_name}")
                self.assertGreater(len(ref_doc.read_text(encoding="utf-8").strip()), 100)

                title = re.search(r"^# (.+)$", body, re.MULTILINE)
                self.assertIsNotNone(title)
                headings.add(title.group(1))

        self.assertEqual(len(EXPECTED_SKILLS), len(headings))

    def test_no_em_or_en_dashes_in_pack_markdown(self) -> None:
        for md_file in sorted(PACK.rglob("*.md")):
            with self.subTest(file=md_file.relative_to(PACK).as_posix()):
                text = md_file.read_text(encoding="utf-8")
                self.assertNotIn("\u2014", text)
                self.assertNotIn("\u2013", text)

    def test_manifest_package_and_catalog_consistency(self) -> None:
        self.assertEqual("specstream-pack", self.manifest["name"])
        package = json.loads((PACK / "package.json").read_text(encoding="utf-8"))
        self.assertEqual("@intentsolutionsio/specstream-pack", package["name"])
        self.assertEqual(self.manifest["version"], package["version"])
        self.assertEqual(self.manifest["description"], package["description"])
        self.assertEqual("plugins/saas-packs/specstream-pack", package["repository"]["directory"])

        extended = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.extended.json").read_text(encoding="utf-8")
        )
        ext_entry = next(p for p in extended["plugins"] if p.get("name") == "specstream-pack")
        self.assertEqual("./plugins/saas-packs/specstream-pack", ext_entry["source"])
        self.assertEqual("saas-packs", ext_entry["category"])
        self.assertEqual(self.manifest["version"], ext_entry["version"])
        self.assertEqual(len(EXPECTED_SKILLS), ext_entry["components"]["skills"])

        cli_catalog = json.loads(
            (ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        cli_entry = next(p for p in cli_catalog["plugins"] if p.get("name") == "specstream-pack")
        self.assertEqual("./plugins/saas-packs/specstream-pack", cli_entry["source"])
        self.assertEqual("saas-packs", cli_entry["category"])
        self.assertNotIn("components", cli_entry)

    def test_payload_validator_offline_without_api_key(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "SPECSTREAM_API_KEY"}
        with patch.dict(os.environ, env, clear=True):
            errs, warns = self.validator.validate_search(
                {"q": '"specstream" search api', "speed": "fast", "num": 10, "passages": True}
            )
            self.assertEqual([], errs)
            self.assertEqual([], warns)

            errs, _ = self.validator.validate_search({"q": "test", "images": True, "passages": True})
            self.assertTrue(errs)

            errs, _ = self.validator.validate_extract(
                {"urls": ["https://specstream.ai/agents.md"], "format": "markdown", "include": ["links"]}
            )
            self.assertEqual([], errs)

            errs, _ = self.validator.validate_extract({"urls": [f"https://example.com/{i}" for i in range(21)]})
            self.assertTrue(errs)

            errs, _ = self.validator.validate_table(
                {"request": "US clinical trials", "count": 50, "quote_id": "q_1", "confirm_max_cents": 500}
            )
            self.assertEqual([], errs)

            errs, _ = self.validator.validate_schedule(
                {
                    "name": "daily-funding",
                    "cadence": "daily",
                    "spend_cap_cents": 2000,
                    "delivery": [{"channel": "webhook", "url": "https://hooks.example.com/ss"}],
                }
            )
            self.assertEqual([], errs)

            errs, _ = self.validator.validate_schedule(
                {
                    "name": "bad-hook",
                    "cadence": "daily",
                    "spend_cap_cents": 2000,
                    "delivery": [{"channel": "webhook", "url": "http://hooks.example.com/ss"}],
                }
            )
            self.assertTrue(errs)

            errs, _ = self.validator.validate_mcp(
                {
                    "mcpServers": {
                        "specstream": {
                            "type": "http",
                            "url": "https://api.specstream.ai/mcp",
                            "headers": {"Authorization": "Bearer ${SPECSTREAM_API_KEY}"},
                        }
                    }
                }
            )
            self.assertEqual([], errs)

            errs, _ = self.validator.validate_mcp(
                {
                    "mcpServers": {
                        "specstream": {
                            "type": "http",
                            "url": "https://api.specstream.ai/mcp",
                            "headers": {"Authorization": "Bearer hardcoded_example_value"},
                        }
                    }
                }
            )
            self.assertTrue(errs)


if __name__ == "__main__":
    unittest.main()
