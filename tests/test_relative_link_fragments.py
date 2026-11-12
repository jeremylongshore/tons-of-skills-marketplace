"""Filesystem link checks ignore fragments without pretending to validate headings."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


VALIDATOR = Path(__file__).resolve().parents[1] / "scripts" / "validate-skills-schema.py"
SPEC = importlib.util.spec_from_file_location("relative_link_validator", VALIDATOR)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class RelativeLinkFragments(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skill"
        self.refs = self.skill / "references"
        self.refs.mkdir(parents=True)
        self.path = self.skill / "SKILL.md"
        self.path.write_text("# Skill\n")
        (self.refs / "guide.md").write_text("# Availability\nExisting supporting content.\n")
        self.fm = {"description": "Use when reviewing local supporting documentation."}

    def check_link(self, target):
        return validator.validate_relative_links(self.path, f"[Guide]({target})")

    def modifiers(self, target):
        return validator.calculate_modifiers(self.path, f"[Guide]({target})", self.fm)

    def test_existing_file_fragment_has_no_missing_file_warning(self):
        for fragment in ("availability", "heading-not-validated", ""):
            with self.subTest(fragment=fragment):
                self.assertEqual(self.check_link(f"references/guide.md#{fragment}"), ([], []))

    def test_existing_file_fragment_has_same_score_as_plain_link(self):
        self.assertEqual(
            self.modifiers("references/guide.md#availability"),
            self.modifiers("references/guide.md"),
        )

    def test_missing_file_fragment_retains_warning_and_orphan_penalty(self):
        target = "references/missing.md#availability"
        errors, warnings = self.check_link(target)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn(target, warnings[0])
        penalty, reason = self.modifiers(target)["items"]["anti_pattern_penalty"]
        self.assertLess(penalty, 0)
        self.assertIn("orphan references", reason)
        self.assertIn(target, reason)

    def test_parent_traversal_with_fragment_still_errors(self):
        (self.root / "outside.md").write_text("# Outside\n")
        target = "../outside.md#heading"
        errors, warnings = self.check_link(target)
        self.assertEqual(len(errors), 1)
        self.assertIn("escapes skill directory", errors[0])
        self.assertIn(target, errors[0])
        self.assertEqual(warnings, [])

    def test_symlink_escape_with_fragment_still_errors(self):
        outside = self.root / "outside.md"
        outside.write_text("# Outside\n")
        (self.refs / "linked.md").symlink_to(outside)
        errors, warnings = self.check_link("references/linked.md#heading")
        self.assertEqual(len(errors), 1)
        self.assertIn("escapes skill directory", errors[0])
        self.assertEqual(warnings, [])

    def test_anchor_only_and_examples_are_not_file_checks(self):
        body = "[Local](#heading)\n`[Example](missing.md#heading)`\n```md\n[Example](missing.md#heading)\n```"
        self.assertEqual(validator.validate_relative_links(self.path, body), ([], []))

    def test_percent_sequences_remain_literal_filesystem_names(self):
        # Existing parser does not URL-decode paths; this fix does not add that scope.
        (self.refs / "encoded%23name.md").write_text("# Guide\n")
        self.assertEqual(self.check_link("references/encoded%23name.md#heading"), ([], []))


if __name__ == "__main__":
    unittest.main()
