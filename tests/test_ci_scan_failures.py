"""Execute the real CI scan steps with isolated input trees and offline tools."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/validate-plugins.yml"


def workflow_step(job, name):
    workflow = yaml.safe_load(WORKFLOW.read_text())
    return next(step["run"] for step in workflow["jobs"][job]["steps"] if step.get("name") == name)


class ScanFailureTests(unittest.TestCase):
    def run_step(self, job, name, files, *, failed_tool=None, pytest_status=0, warning_fault=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for filename, content in files.items():
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            tools = root / "offline-tools"
            tools.mkdir()
            pytest = tools / "pytest"
            pytest.write_text(
                '#!/usr/bin/env bash\nprintf "%s\\n" "$@" > "$SCAN_PYTEST_ARGS"\nexit "$SCAN_PYTEST_STATUS"\n'
            )
            pytest.chmod(0o755)
            if failed_tool == "find":
                # Emit real matching results, then fail a real filesystem traversal.
                tool = tools / "find"
                tool.write_text(
                    f'#!/usr/bin/env bash\n"{shutil.which("find")}" "$@"\n'
                    f'exec "{shutil.which("find")}" "$SCAN_MISSING_ROOT"\n'
                )
                tool.chmod(0o755)
            elif failed_tool == "grep-filter":
                tool = tools / "grep"
                tool.write_text(
                    '#!/usr/bin/env bash\nif [ "$1" = -v ]; then\n'
                    f'  exec "{shutil.which("grep")}" -v "["\nfi\n'
                    f'exec "{shutil.which("grep")}" "$@"\n'
                )
                tool.chmod(0o755)
            if warning_fault is not None:
                tool = tools / "grep"
                tool.write_text(
                    "#!" + sys.executable + "\n"
                    "import json, os, subprocess, sys\n"
                    "args = sys.argv[1:]\n"
                    "fault = json.loads(os.environ['SCAN_WARNING_FAULT'])\n"
                    "pattern = args[2] if args[:2] == ['-r', '-E'] else args[-1]\n"
                    "if pattern == fault['pattern']:\n"
                    "    if fault.get('filter'):\n        args = ['-v', '[']\n"
                    "    else:\n"
                    "        if fault.get('partial'):\n"
                    "            subprocess.run([os.environ['SCAN_REAL_GREP'], *args])\n"
                    "        args[-1] = os.environ['SCAN_MISSING_ROOT']\n"
                    "sys.exit(subprocess.run([os.environ['SCAN_REAL_GREP'], *args]).returncode)\n"
                )
                tool.chmod(0o755)
            args_file = root / "pytest-arguments"
            env = {
                **os.environ,
                "PATH": f"{tools}{os.pathsep}{os.environ['PATH']}",
                "SCAN_WARNING_FAULT": json.dumps(warning_fault),
                "SCAN_REAL_GREP": shutil.which("grep"),
                "SCAN_PYTEST_ARGS": str(args_file),
                "SCAN_PYTEST_STATUS": str(pytest_status),
                "SCAN_MISSING_ROOT": str(root / "missing-scan-root"),
            }
            result = subprocess.run(
                ["bash", "-e", "-c", workflow_step(job, name)],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result, args_file.read_text().splitlines() if args_file.exists() else None

    def dangerous(self, files, **kwargs):
        return self.run_step("validate", "Security scan - Dangerous patterns", files, **kwargs)

    def discovery(self, files, **kwargs):
        return self.run_step("test", "Run Python tests", files, **kwargs)

    def test_dangerous_match_still_fails(self):
        result, _ = self.dangerous({"plugins/example.txt": "rm -rf /\n"})
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Dangerous 'rm -rf /' pattern detected", result.stdout)

    def test_dangerous_no_match_still_passes(self):
        result, _ = self.dangerous({"plugins/example.txt": "rm -rf /var/application\n"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No dangerous patterns detected", result.stdout)

    def test_all_original_dangerous_path_exclusions_still_apply(self):
        files = {f"plugins/{name}/example.txt": "rm -rf /\n" for name in ("var", "tmp", "prometheus")}
        result, _ = self.dangerous(files)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dangerous_scan_io_error_does_not_report_clean(self):
        result, _ = self.dangerous({})
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("plugins/", result.stderr)
        self.assertNotIn("No dangerous patterns detected", result.stdout)

    def test_dangerous_filter_error_does_not_report_clean(self):
        result, _ = self.dangerous({"plugins/example.txt": "rm -rf /\n"}, failed_tool="grep-filter")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertTrue(result.stderr)
        self.assertNotIn("No dangerous patterns detected", result.stdout)

    def test_discovery_preserves_names_exclusions_and_pytest_arguments(self):
        result, args = self.discovery(
            {
                "test_alpha.py": "",
                "nested/alpha_test.py": "",
                "__pycache__/test_ignored.py": "",
                "backups/test_ignored.py": "",
            }
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("./test_alpha.py", result.stdout)
        self.assertIn("./nested/alpha_test.py", result.stdout)
        self.assertNotIn("test_ignored", result.stdout)
        self.assertEqual(args, ["-v", "--cov=.", "--cov-report=term-missing", "--cov-report=xml"])

    def test_discovery_no_match_still_skips_pytest(self):
        result, args = self.discovery({"README.md": "No tests here.\n"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No Python test files found", result.stdout)
        self.assertIsNone(args)

    def test_discovery_all_excluded_still_skips_pytest(self):
        result, args = self.discovery({"backups/test_ignored.py": "", "__pycache__/test_ignored.py": ""})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(args)

    def test_discovery_find_error_with_partial_matches_fails_before_pytest(self):
        result, args = self.discovery({"test_alpha.py": ""}, failed_tool="find")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing-scan-root", result.stderr)
        self.assertNotIn("No Python test files found", result.stdout)
        self.assertIsNone(args)

    def test_discovery_filter_error_is_not_a_no_tests_result(self):
        result, args = self.discovery({"test_alpha.py": ""}, failed_tool="grep-filter")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertTrue(result.stderr)
        self.assertNotIn("No Python test files found", result.stdout)
        self.assertIsNone(args)

    def test_pytest_failure_still_fails_the_step(self):
        result, args = self.discovery({"test_alpha.py": ""}, pytest_status=7)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIsNotNone(args)
        self.assertNotIn("Python tests passed", result.stdout)

    def test_warning_scan_operational_errors_are_not_clean(self):
        cases = [
            (
                "eval-producer",
                "Security scan - Dangerous patterns",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "eval\\s*\\("},
            ),
            (
                "eval-readme-filter",
                "Security scan - Dangerous patterns",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "README.md", "filter": True},
            ),
            (
                "eval-redis-filter",
                "Security scan - Dangerous patterns",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "this.redis.eval", "filter": True},
            ),
            (
                "numeric-http",
                "Security scan - Dangerous patterns",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "curl.*http://[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+"},
            ),
            (
                "base64",
                "Security scan - Dangerous patterns",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "base64\\s+-d"},
            ),
            (
                "insecure-producer",
                "Security scan - Suspicious URLs",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "http://[^l]"},
            ),
            (
                "insecure-localhost-filter",
                "Security scan - Suspicious URLs",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "localhost", "filter": True},
            ),
            (
                "insecure-loopback-filter",
                "Security scan - Suspicious URLs",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "127.0.0.1", "filter": True},
            ),
            (
                "shortener",
                "Security scan - Suspicious URLs",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                {"pattern": "(bit\\.ly|tinyurl\\.com|goo\\.gl)"},
            ),
            (
                "insecure-partial-output",
                "Security scan - Suspicious URLs",
                {"plugins/example.txt": "http://example.invalid\n"},
                {"pattern": "http://[^l]", "partial": True},
            ),
            (
                "eval-partial-output",
                "Security scan - Dangerous patterns",
                {"plugins/example.js": "eval(value)\n"},
                {"pattern": "eval\\s*\\(", "partial": True},
            ),
        ]
        for label, name, files, fault in cases:
            with self.subTest(case=label):
                result, args = self.run_step("validate", name, files, warning_fault=fault)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertTrue(result.stderr)
                self.assertNotIn("No dangerous patterns detected", result.stdout)
                self.assertNotIn("URL scan complete", result.stdout)
                self.assertIsNone(args)

    def test_warning_scan_controls_preserve_exact_output(self):
        cases = [
            (
                "dangerous-no-match",
                "Security scan - Dangerous patterns",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                "Scanning for dangerous command patterns...\n✅ No dangerous patterns detected\n",
            ),
            (
                "urls-no-match",
                "Security scan - Suspicious URLs",
                {"plugins/fixture.txt": "inert benign fixture\n"},
                "Scanning for suspicious URLs...\n✅ URL scan complete\n",
            ),
            (
                "warning-eval",
                "Security scan - Dangerous patterns",
                {"plugins/example.js": "eval(value)\n"},
                "Scanning for dangerous command patterns...\n⚠️  WARNING: 'eval()' detected - potential command injection risk\nplugins/example.js:eval(value)\n✅ No dangerous patterns detected\n",
            ),
            (
                "eval-exclusions",
                "Security scan - Dangerous patterns",
                {"plugins/README.md": "eval(value)\n", "plugins/redis.js": "this.redis.eval(value)\n"},
                "Scanning for dangerous command patterns...\n✅ No dangerous patterns detected\n",
            ),
            (
                "warning-numeric",
                "Security scan - Dangerous patterns",
                {"plugins/example.txt": "curl http://203.0.113.5\n"},
                "Scanning for dangerous command patterns...\nplugins/example.txt:curl http://203.0.113.5\n⚠️  WARNING: curl to IP address detected - potential data exfiltration\n✅ No dangerous patterns detected\n",
            ),
            (
                "warning-base64",
                "Security scan - Dangerous patterns",
                {"plugins/example.txt": "base64 -d inert\n"},
                "Scanning for dangerous command patterns...\nplugins/example.txt:base64 -d inert\n⚠️  WARNING: base64 decoding detected - potential obfuscation\n✅ No dangerous patterns detected\n",
            ),
            (
                "warning-http",
                "Security scan - Suspicious URLs",
                {"plugins/example.txt": "http://example.invalid\n"},
                "Scanning for suspicious URLs...\nplugins/example.txt:http://example.invalid\n⚠️  WARNING: Non-HTTPS URLs detected (security risk)\n✅ URL scan complete\n",
            ),
            (
                "url-exclusions",
                "Security scan - Suspicious URLs",
                {"plugins/example.txt": "http://localhost\nhttp://127.0.0.1\n"},
                "Scanning for suspicious URLs...\n✅ URL scan complete\n",
            ),
            (
                "warning-shortener",
                "Security scan - Suspicious URLs",
                {"plugins/example.txt": "https://bit.ly/inert\n"},
                "Scanning for suspicious URLs...\nplugins/example.txt:https://bit.ly/inert\n⚠️  WARNING: URL shorteners detected (potential phishing)\n✅ URL scan complete\n",
            ),
        ]
        for label, name, files, expected in cases:
            with self.subTest(case=label):
                result, args = self.run_step("validate", name, files)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, "")
                self.assertIsNone(args)


class PackageDiscoveryTests(unittest.TestCase):
    """Real workflow loop with actual grep errors and inert package-manager peers."""

    def run_packages(self, files, *, failed_pattern="", failed_plugin=""):
        with tempfile.TemporaryDirectory(prefix="package-discovery-") as temporary:
            root = Path(temporary)
            for filename, content in files.items():
                target = root / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)
            tools = root / "offline-tools"
            tools.mkdir()
            home = root / "home"
            home.mkdir()
            trace = root / "calls.jsonl"
            grep = tools / "grep"
            grep.write_text(
                "#!" + sys.executable + "\n"
                "import json, os, subprocess, sys\n"
                "args = sys.argv[1:]\n"
                "if args[1] == os.environ['FAILED_PATTERN']:\n"
                "    args[-1] = os.environ['MISSING_FIXTURE']\n"
                "result = subprocess.run([os.environ['REAL_GREP'], *args])\n"
                "with open(os.environ['CALL_TRACE'], 'a') as out:\n"
                "    out.write(json.dumps({'grep': sys.argv[1:], 'status': result.returncode}) + '\\n')\n"
                "sys.exit(result.returncode)\n"
            )
            grep.chmod(0o755)
            for command in ("pnpm", "npm"):
                stub = tools / command
                stub.write_text(
                    "#!" + sys.executable + "\n"
                    "import json, os, sys\nfrom pathlib import Path\n"
                    f"command = {command!r}\n"
                    "with open(os.environ['CALL_TRACE'], 'a') as out:\n"
                    "    out.write(json.dumps({'command': command, 'args': sys.argv[1:], "
                    "'plugin': Path.cwd().name}) + '\\n')\n"
                    "if command != 'pnpm' or sys.argv[1:] not in "
                    "[['test:ci'], ['test', '--', '--run']]:\n    sys.exit(88)\n"
                    "sys.exit(7 if Path.cwd().name == os.environ['FAILED_PLUGIN'] else 0)\n"
                )
                stub.chmod(0o755)
            env = {
                "PATH": f"{tools}{os.pathsep}{os.defpath}",
                "HOME": str(home),
                "REAL_GREP": shutil.which("grep"),
                "FAILED_PATTERN": failed_pattern,
                "FAILED_PLUGIN": failed_plugin,
                "MISSING_FIXTURE": str(root / "missing-package-fixture"),
                "CALL_TRACE": str(trace),
            }
            result = subprocess.run(
                [
                    "/bin/bash",
                    "-e",
                    "-c",
                    workflow_step("test", "Run plugin tests (widened loop — every package.json with a test script)"),
                ],
                cwd=root,
                env=env,
                text=True,
                capture_output=True,
                timeout=15,
            )
            events = [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
            return result, events

    @staticmethod
    def package(scripts):
        return json.dumps({"scripts": scripts})

    def test_all_four_grep_read_errors_fail_before_package_commands(self):
        cases = [
            ({"test": "inert"}, '"test":'),
            ({"other": "inert"}, '"test:ci":'),
            ({"test": "inert"}, "pytest"),
            ({"test": "inert", "test:ci": "inert"}, '"test:ci":'),
        ]
        for scripts, pattern in cases:
            with self.subTest(scripts=scripts, pattern=pattern):
                result, events = self.run_packages(
                    {"plugins/mcp/fixture/package.json": self.package(scripts)}, failed_pattern=pattern
                )
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("grep status 2", result.stderr)
                self.assertTrue(any(event.get("status") == 2 for event in events))
                self.assertFalse(any("command" in event for event in events))
                self.assertNotIn("All passing.", result.stdout)

    def test_no_test_script_skips(self):
        result, events = self.run_packages({"plugins/mcp/fixture/package.json": self.package({"other": "inert"})})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Tested: 0 plugins", result.stdout)
        self.assertFalse(any("command" in event for event in events))

    def test_python_plugin_skips(self):
        result, events = self.run_packages({"plugins/mcp/fixture/package.json": self.package({"test": "pytest"})})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Python plugin, tested separately", result.stdout)
        self.assertFalse(any("command" in event for event in events))

    def test_saas_pack_skips_before_grep_or_package_commands(self):
        result, events = self.run_packages(
            {"plugins/saas-packs/fixture-pack/package.json": self.package({"test": "inert"})},
            failed_pattern='"test":',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(events, [])

    def test_exact_script_token_recognition_is_preserved(self):
        result, events = self.run_packages({"plugins/mcp/fixture/package.json": '{"scripts": {"test" : "inert"}}'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(any("command" in event for event in events))

    def test_test_ci_preference_and_exact_arguments(self):
        for scripts, expected in [
            ({"test": "inert"}, ["test", "--", "--run"]),
            ({"test:ci": "inert"}, ["test:ci"]),
            ({"test": "inert", "test:ci": "inert"}, ["test:ci"]),
        ]:
            with self.subTest(scripts=scripts):
                result, events = self.run_packages({"plugins/mcp/fixture/package.json": self.package(scripts)})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    [e for e in events if "command" in e], [{"command": "pnpm", "args": expected, "plugin": "fixture"}]
                )

    def test_failure_accumulates_and_later_plugins_still_run(self):
        result, events = self.run_packages(
            {
                "plugins/mcp/a-fail/package.json": self.package({"test": "inert"}),
                "plugins/mcp/b-pass/package.json": self.package({"test:ci": "inert"}),
            },
            failed_plugin="a-fail",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual([e["plugin"] for e in events if "command" in e], ["a-fail", "b-pass"])
        self.assertIn("Tested: 2 plugins", result.stdout)
        self.assertIn("Failed: 1", result.stdout)
        self.assertIn("mcp/a-fail", result.stdout)
        self.assertNotIn("All passing.", result.stdout)


if __name__ == "__main__":
    unittest.main()
