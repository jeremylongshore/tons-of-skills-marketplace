"""Exercise real hook scripts with native event fixtures and no provider calls."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NativeHookEventsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="native-hook-events-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        self.workflow = self.project / ".github/workflows/probe.yml"
        self.workflow.parent.mkdir(parents=True)
        self.gcp = self.root / "gcp"
        self.formatter = self.root / "formatter"
        shutil.copytree(ROOT / "plugins/devops/jeremy-github-actions-gcp", self.gcp)
        shutil.copytree(ROOT / "plugins/examples/formatter", self.formatter)
        self.marker = self.root / "invocations.jsonl"
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        for name in ("prettier", "npx"):
            stub = bin_dir / name
            stub.write_text(
                "#!/usr/bin/env python3\nimport json,os,sys\n"
                "with open(os.environ['HOOK_TEST_MARKER'],'a') as f: "
                "f.write(json.dumps({'program':os.path.basename(sys.argv[0]),'args':sys.argv[1:]})+'\\n')\n"
                + ("sys.exit(99)\n" if name == "npx" else "sys.exit(0)\n")
            )
            stub.chmod(0o755)
        self.env = {
            **os.environ,
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "HOOK_TEST_MARKER": str(self.marker),
        }
        self.env.pop("CLAUDE_FILE_PATH", None)
        self.env.pop("FORMATTER_DEBUG", None)

    def event(self, tool="Write", event="PreToolUse", **data):
        return {
            "hook_event_name": event,
            "tool_name": tool,
            "cwd": str(self.project),
            "tool_input": {"file_path": str(self.workflow), **data},
        }

    def run_script(self, path, payload, *args):
        return subprocess.run(
            ["bash", str(path), *args],
            input=payload if isinstance(payload, str) else json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=self.project,
            env=self.env,
            timeout=10,
        )

    def gcp_result(self, payload):
        return self.run_script(self.gcp / "scripts/validate-workflow.sh", payload)

    def test_native_write_checks_proposed_content_without_creating_file(self):
        denied = self.gcp_result(self.event(content="credentials_json: synthetic-secret"))
        self.assertEqual(denied.returncode, 2, denied.stderr)
        self.assertNotIn("synthetic-secret", denied.stdout + denied.stderr)
        allowed = self.gcp_result(
            self.event(content="workload_identity_provider: fixture\npermissions:\n  id-token: write\n")
        )
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertFalse(self.workflow.exists())

    def test_edit_evaluates_result_and_preserves_disk(self):
        self.workflow.write_text("safe: true\n")
        result = self.gcp_result(
            self.event(tool="Edit", old_string="safe: true", new_string="credentials_json: fixture")
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.workflow.read_text(), "safe: true\n")
        self.workflow.write_text("credentials_json: fixture\n")
        result = self.gcp_result(self.event(tool="Edit", old_string="credentials_json", new_string="safe_key"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.workflow.read_text(), "credentials_json: fixture\n")

    def test_ambiguous_edit_requires_explicit_replace_all(self):
        original = "credentials_json: one\ncredentials_json: two\n"
        self.workflow.write_text(original)
        payload = self.event(tool="Edit", old_string="credentials_json", new_string="safe_key")
        self.assertEqual(self.gcp_result(payload).returncode, 2)
        payload["tool_input"]["replace_all"] = True
        self.assertEqual(self.gcp_result(payload).returncode, 0)
        self.assertEqual(self.workflow.read_text(), original)

    def test_existing_policy_rules_and_native_scope(self):
        for text in (
            "roles/owner",
            "roles/editor",
            "GCP_SA_KEY=fixture",
            "GOOGLE_APPLICATION_CREDENTIALS=fixture",
            "workload_identity_provider: fixture",
        ):
            with self.subTest(text=text):
                self.assertEqual(self.gcp_result(self.event(content=text)).returncode, 2)
        for payload in (
            self.event(tool="Read", content="credentials_json"),
            self.event(event="PostToolUse", content="credentials_json"),
            self.event(file_path=str(self.project / "notes.yml"), content="credentials_json"),
        ):
            self.assertEqual(self.gcp_result(payload).returncode, 0)
        for payload in (
            "",
            "{",
            "[]",
            self.event(content=None),
            self.event(tool="Edit", old_string="x", new_string="y"),
        ):
            self.assertEqual(self.gcp_result(payload).returncode, 2)

    def test_explicit_manual_file_retains_conventional_failure(self):
        self.workflow.write_text("credentials_json: fixture")
        result = self.run_script(self.gcp / "scripts/validate-workflow.sh", "", str(self.workflow))
        self.assertEqual(result.returncode, 1)

    def invocations(self):
        return [json.loads(line) for line in self.marker.read_text().splitlines()] if self.marker.exists() else []

    def set_enabled(self, event, enabled):
        path = self.formatter / "hooks/hooks.json"
        data = json.loads(path.read_text())
        data["hooks"][event][0]["enabled"] = enabled
        path.write_text(json.dumps(data))

    def formatting_event(self):
        target = self.project / "with space.js"
        target.write_text("const fixture = 1;\n")
        return target, self.event(event="PostToolUse", file_path=str(target), content="fixture")

    def test_formatter_uses_native_input_and_response_paths(self):
        target, payload = self.formatting_event()
        for from_response in (False, True):
            if from_response:
                payload["tool_input"].pop("file_path")
                payload["tool_response"] = {"filePath": str(target)}
            result = self.run_script(self.formatter / "scripts/format.sh", payload)
            self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.invocations()
        self.assertEqual(len(calls), 2)
        self.assertTrue(all(x["program"] == "prettier" and x["args"][-1] == str(target) for x in calls))
        self.assertEqual(target.read_text(), "const fixture = 1;\n")

    def test_formatter_enabled_switch_and_wrong_event_cannot_format(self):
        _, payload = self.formatting_event()
        for flag in (False, "true"):
            self.set_enabled("PostToolUse", flag)
            self.assertEqual(self.run_script(self.formatter / "scripts/format.sh", payload).returncode, 0)
        self.set_enabled("PostToolUse", True)
        payload["tool_name"] = "Read"
        self.assertEqual(self.run_script(self.formatter / "scripts/format.sh", payload).returncode, 0)
        self.assertEqual(self.invocations(), [])

    def test_manual_legacy_payload_still_formats(self):
        target, _ = self.formatting_event()
        result = self.run_script(self.formatter / "scripts/format.sh", {"toolOutput": {"file": str(target)}})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.invocations()), 1)

    def test_debug_log_does_not_include_native_write_content(self):
        target, _ = self.formatting_event()
        sentinel = "synthetic-content-must-not-appear-in-logs"
        payload = {
            "tool_input": {"content": sentinel, "file_path": str(target)},
            "hook_event_name": "PostToolUse",
            "tool_name": "Write",
        }
        self.env["FORMATTER_DEBUG"] = "true"
        result = self.run_script(self.formatter / "scripts/format.sh", payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        logs = "".join(p.read_text() for p in (self.formatter / "logs").glob("*.log"))
        self.assertNotIn(sentinel, result.stdout + result.stderr + logs)

    def test_npx_fallback_never_installs_packages(self):
        # Remove the global formatter and use a recording npx that refuses
        # installation; exercise both actual shell entry points offline.
        (self.root / "bin/prettier").unlink()
        npx = self.root / "bin/npx"
        npx.write_text(
            npx.read_text().replace(
                "sys.exit(99)", "sys.exit(0 if sys.argv[1:3] == ['--no-install', 'prettier'] else 99)"
            )
        )
        target, payload = self.formatting_event()
        result = self.run_script(self.formatter / "scripts/format.sh", payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.set_enabled("PreToolUse", True)
        result = self.run_script(
            self.formatter / "scripts/validate-format.sh",
            self.event(tool="Edit", file_path=str(target)),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.invocations()
        self.assertGreaterEqual(len(calls), 3)
        self.assertTrue(
            all(c["program"] == "npx" and c["args"][:2] == ["--no-install", "prettier"] for c in calls), calls
        )
        self.assertTrue(any("--check" in c["args"] for c in calls))
        self.assertTrue(any("--write" in c["args"] for c in calls))

    def test_optional_pre_hook_is_inert_until_its_switch_is_enabled(self):
        target, _ = self.formatting_event()
        payload = self.event(tool="Edit", file_path=str(target))
        script = self.formatter / "scripts/validate-format.sh"
        self.assertEqual(self.run_script(script, payload).returncode, 0)
        self.assertEqual(self.invocations(), [])
        self.set_enabled("PreToolUse", True)
        result = self.run_script(script, payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.invocations()
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], {"program": "prettier", "args": ["--check", str(target)]})


if __name__ == "__main__":
    unittest.main()
