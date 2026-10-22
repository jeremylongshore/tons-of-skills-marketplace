"""Exercise the funding validator CLI against actual manifests and file types."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ci/validate_funding.py"


class FundingSchemaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.manifest = self.directory / "FUNDING.yml"

    def run_cli(self, path=None, cwd=None):
        args = [sys.executable, str(SCRIPT)]
        if path is not None:
            args.append(str(path))
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=10, check=False)

    def assert_manifest(self, text, valid):
        self.manifest.write_text(text, encoding="utf-8")
        result = self.run_cli(self.manifest)
        self.assertEqual(result.returncode, 0 if valid else 1, result.stdout + result.stderr)
        self.assertIn("funding schema: OK" if valid else "funding schema: FAIL", result.stdout + result.stderr)

    def test_current_repository_manifest_and_default_path(self):
        result = self.run_cli(cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "funding schema: OK\n")

    def test_each_platform_and_valid_github_list(self):
        for text in (
            "github: [someone]\n",
            "github: ['a', 'A-b', 'c9', 'four']\n",
            "github: ['" + "a" * 39 + "']\n",
            "buy_me_a_coffee: Someone9\n",
            "ko_fi: Someone9\n",
            "# Payment options\ngithub:\n  - someone\nko_fi: 'other'\n",
        ):
            with self.subTest(text=text):
                self.assert_manifest(text, True)

    def test_nonempty_mapping_and_supported_platforms_only(self):
        for text in (
            "",
            "# comment\n",
            "{}",
            "[]",
            "someone",
            "null",
            "custom: https://example.com",
            "patreon: someone",
        ):
            with self.subTest(text=text):
                self.assert_manifest(text, False)

    def test_duplicate_keys_cannot_overwrite_a_bad_value(self):
        for text in (
            "github: https://invalid.example\ngithub: [someone]\n",
            "github: [someone]\n'github': [another]\n",
            "ko_fi: one\nko_fi: two\n",
        ):
            with self.subTest(text=text):
                self.assert_manifest(text, False)

    def test_github_requires_one_to_four_distinct_string_handles(self):
        for value in (
            "someone",
            "[]",
            "[a,b,c,d,e]",
            "[someone, Someone]",
            "[true]",
            "[123]",
            "[null]",
            "[[someone]]",
            "{}",
        ):
            with self.subTest(value=value):
                self.assert_manifest(f"github: {value}\n", False)

    def test_github_handle_boundaries(self):
        for value in (
            "",
            "-someone",
            "someone-",
            "some--one",
            "some_one",
            "some.one",
            "a" * 40,
            "éclair",
            "https://github.com/person",
            "@person",
            "some one",
        ):
            with self.subTest(value=value):
                self.assert_manifest(f"github: ['{value}']\n", False)

    def test_support_platforms_require_scalar_handles_not_urls(self):
        for platform in ("buy_me_a_coffee", "ko_fi"):
            for value in (
                "[]",
                "{}",
                "null",
                "true",
                "123",
                "''",
                "'a-b'",
                "'a_b'",
                "'a.b'",
                "'a b'",
                "'éclair'",
                "'https://example.com/person'",
                "'" + "a" * 40 + "'",
            ):
                with self.subTest(platform=platform, value=value):
                    self.assert_manifest(f"{platform}: {value}\n", False)

    def test_anchors_aliases_merges_tags_and_multiple_documents_rejected(self):
        for text in (
            "github: &handles [someone]\n",
            "github: *handles\n",
            "github: [someone]\nko_fi: &name someone\nbuy_me_a_coffee: *name\n",
            "<<: {github: [someone]}\n",
            "github: !!seq [someone]\n",
            "ko_fi: !!str someone\n",
            "%YAML 1.1\n---\ngithub: [someone]\n",
            "github: [someone]\n---\nko_fi: someone\n",
            "github: [someone\n",
            "[github]: [someone]\n",
            "true: someone\n",
        ):
            with self.subTest(text=text):
                self.assert_manifest(text, False)

    def test_executable_yaml_is_not_executed(self):
        marker = self.directory / "executed"
        self.assert_manifest(f"!!python/object/apply:os.system ['touch {marker}']\n", False)
        self.assertFalse(marker.exists())

    def test_missing_directory_symlink_and_fifo_fail_without_hanging(self):
        target = self.directory / "target.yml"
        target.write_text("github: [someone]\n", encoding="utf-8")
        self.manifest.symlink_to(target)
        fifo = self.directory / "fifo"
        os.mkfifo(fifo)
        for path in (self.directory / "missing", self.directory, self.manifest, fifo):
            with self.subTest(path=path):
                result = self.run_cli(path)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_size_and_encoding_are_bounded(self):
        for raw in (b"#" + b"a" * (16 * 1024), b"github: [\xff]\n"):
            with self.subTest(raw_length=len(raw)):
                self.manifest.write_bytes(raw)
                result = self.run_cli(self.manifest)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_parse_errors_do_not_echo_manifest_contents(self):
        # This public canary is deliberately not a credential.
        canary = "public-parser-diagnostic-canary"
        self.manifest.write_text(f"github: [{canary}\n", encoding="utf-8")
        result = self.run_cli(self.manifest)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(canary, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
