"""CLI regressions for the E6.12 deadline boundary, using isolated policy trees."""

import datetime as dt
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check-ci-deadlines.py"


class DeadlineTests(unittest.TestCase):
    def run_tree(self, files, *args):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".github/workflows").mkdir(parents=True)
            for name, content in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=root, text=True, capture_output=True)

    def test_expired_directives_across_policy_surfaces(self):
        cases = {
            ".github/workflows/nested/gate.yml": "# REPORT-ONLY-UNTIL: 2000-01-01\n",
            ".github/workflows/gate.yaml": "# REPORT-ONLY-UNTIL: 2000-01-01\n",
            "scripts/nested/gate.py": "# REPORT-ONLY-UNTIL: 2000-01-01\n",
            "scripts/gate.mjs": "// REPORT-ONLY-UNTIL: 2000-01-01\n",
            "scripts/gate.sh": "# REPORT-ONLY-UNTIL: 2000-01-01\n",
            "scripts/sops-env": "#!/usr/bin/env bash\n# REPORT-ONLY-UNTIL: 2000-01-01\n",
            "scripts/.baseline.json": '{"policy": [{"REPORT-ONLY-UNTIL": "2000-01-01"}]}',
            ".policy-baseline.json": '{"REPORT-ONLY-UNTIL": "2000-01-01"}',
            "config/nested/policy-baseline.json": '{"REPORT-ONLY-UNTIL": "2000-01-01"}',
            "scripts/scan-allowlist.txt": "plugins/foo.py:outbound-network  Reviewer Jane; expires 2000-01-01; offline only\n",
        }
        for name, content in cases.items():
            with self.subTest(path=name):
                result = self.run_tree({name: content})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(name, result.stdout)

    def test_malformed_directives_fail_closed(self):
        for value in ["", "tomorrow", "YYYY-MM-DD", "2026-2-03", "2026-02-30", "20261031", "2026-10-31junk"]:
            for path, content in [
                ("scripts/gate.py", f"# REPORT-ONLY-UNTIL: {value}\n"),
                (".policy-baseline.json", '{"REPORT-ONLY-UNTIL": "' + value + '"}'),
                (
                    "scripts/scan-allowlist.txt",
                    f"plugins/foo.py:outbound-network  Reviewer Jane; expires {value}; reason\n",
                ),
            ]:
                with self.subTest(path=path, value=value):
                    result = self.run_tree({path: content})
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_non_string_json_deadline_is_invalid(self):
        for value in ["null", "123", "[]", "{}", "true"]:
            with self.subTest(value=value):
                result = self.run_tree({"scripts/.baseline.json": '{"REPORT-ONLY-UNTIL": ' + value + "}"})
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_examples_and_non_policy_data_are_not_directives(self):
        files = {
            "scripts/gate.py": '"""Example:\n# REPORT-ONLY-UNTIL: YYYY-MM-DD\n"""\ntext = "# REPORT-ONLY-UNTIL: 2000-01-01"\n',
            "scripts/gate.mjs": 'const a = "// REPORT-ONLY-UNTIL: 2000-01-01";\nconst b = `example\n// REPORT-ONLY-UNTIL: 2000-01-01\n`;\n/** Example: REPORT-ONLY-UNTIL: YYYY-MM-DD */\n',
            "scripts/gate.sh": 'printf "%s" "# REPORT-ONLY-UNTIL: 2000-01-01"\nprintf "%s" \'example\n# REPORT-ONLY-UNTIL: 2000-01-01\n\'\ncat <<\'EOF\'\n# REPORT-ONLY-UNTIL: 2000-01-01\nEOF\n',
            "scripts/.baseline.json": '{"description": "REPORT-ONLY-UNTIL: 2000-01-01"}',
            "scripts/scan-allowlist.txt": "# Example: expires 2000-01-01\nplugins/foo.py:outbound-network  reviewed offline\n",
            ".github/workflows/gate.yml": "# `# REPORT-ONLY-UNTIL: YYYY-MM-DD` is the documented syntax\n",
            "scripts/fixtures/gate.py": "# REPORT-ONLY-UNTIL: 2000-01-01\n",
            "plugins/example/scripts/gate.py": "# REPORT-ONLY-UNTIL: 2000-01-01\n",
            "000-docs/historical-baseline.json": '{"REPORT-ONLY-UNTIL": "2000-01-01"}',
        }
        result = self.run_tree(files)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("No REPORT-ONLY-UNTIL markers", result.stdout)

    def test_real_comments_after_examples_still_enforce(self):
        for path, example, directive in [
            ("scripts/gate.py", '"""# REPORT-ONLY-UNTIL: YYYY-MM-DD"""\n', "#"),
            ("scripts/gate.mjs", "const example = `// REPORT-ONLY-UNTIL: YYYY-MM-DD`;\n", "//"),
            ("scripts/gate.sh", "cat <<EOF\n# REPORT-ONLY-UNTIL: YYYY-MM-DD\nEOF\n", "#"),
        ]:
            with self.subTest(path=path):
                result = self.run_tree({path: example + f"{directive} REPORT-ONLY-UNTIL: 2000-01-01\n"})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_today_is_allowed_and_yesterday_expires(self):
        today = dt.date.today()
        for date, expected in [(today, 0), (today - dt.timedelta(days=1), 1), (today + dt.timedelta(days=8), 0)]:
            with self.subTest(date=date):
                result = self.run_tree({".github/workflows/gate.yml": f"# REPORT-ONLY-UNTIL: {date.isoformat()}\n"})
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)

    def test_allowlist_report_marker_and_existing_expiry_syntax(self):
        for reason in [
            "REPORT-ONLY-UNTIL: 2000-01-01 (reviewed)",
            "Reviewer Jeremy Longshore; expires 2000-01-01; offline only",
        ]:
            with self.subTest(reason=reason):
                result = self.run_tree({"scripts/scan-allowlist.txt": "plugins/foo.py:outbound-network  " + reason})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_allowlist_directive_comment_is_active_but_prose_is_not(self):
        result = self.run_tree({"scripts/scan-allowlist.txt": "# REPORT-ONLY-UNTIL: 2000-01-01\n"})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_duplicate_and_escaped_json_keys_cannot_hide_expired_policy(self):
        for body in [
            '{"REPORT-ONLY-UNTIL": "2000-01-01", "REPORT-ONLY-UNTIL": "2999-01-01"}',
            '{"REPORT-ONLY-UNTIL": "2999-01-01", "nested": {"REPORT-ONLY-UNTIL": "2000-01-01"}}',
            '{"REPORT-ONLY-UNTIL": "2000-01-01"}'.replace("R", r"\u0052"),
        ]:
            with self.subTest(body=body):
                result = self.run_tree({"scripts/.baseline.json": body})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_yaml_plain_apostrophe_does_not_hide_real_comment(self):
        source = "name: Don't hide the deadline\n# REPORT-ONLY-UNTIL: 2000-01-01\njobs: {}\n# a later apostrophe '\n"
        result = self.run_tree({".github/workflows/gate.yaml": source})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_yaml_scalars_are_data_except_run_code(self):
        source = (
            'name: "# REPORT-ONLY-UNTIL: 2000-01-01"\n'
            "description: |\n  # REPORT-ONLY-UNTIL: 2000-01-01\n"
            "jobs:\n  validate:\n    steps:\n      - run: |\n"
            '          printf "%s" "# REPORT-ONLY-UNTIL: 2000-01-01"\n'
        )
        result = self.run_tree({".github/workflows/gate.yaml": source})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        source += "          # REPORT-ONLY-UNTIL: 2000-01-01\n"
        result = self.run_tree({".github/workflows/gate.yaml": source})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("gate.yaml:9", result.stdout)

    def test_yaml_block_header_comment_is_real_policy(self):
        result = self.run_tree(
            {".github/workflows/gate.yaml": "description: | # REPORT-ONLY-UNTIL: 2000-01-01\n  documentation\n"}
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_yaml_env_run_is_data_not_step_code(self):
        result = self.run_tree(
            {".github/workflows/gate.yaml": 'env:\n  run: "# REPORT-ONLY-UNTIL: 2000-01-01"\njobs: {}\n'}
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shell_hash_must_start_an_actual_comment(self):
        source = "printf '%s\\n' example#REPORT-ONLY-UNTIL: 2000-01-01\n"
        source += r"printf '%s' \#REPORT-ONLY-UNTIL: 2000-01-01" + "\n"
        result = self.run_tree({"scripts/gate.sh": source})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for prefix in ["echo done #", "echo done;#", "#"]:
            with self.subTest(prefix=prefix):
                result = self.run_tree({"scripts/gate.sh": source + prefix + " REPORT-ONLY-UNTIL: 2000-01-01\n"})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_missing_workflow_directory_still_fails(self):
        result = self.run_tree({}, "--workflows", "missing")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
