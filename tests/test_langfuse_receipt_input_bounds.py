"""Unrepresentable JSON integers must hold reviews without tracebacks or payloads."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "plugins/saas-packs/langfuse-pack/skills"
RAW = '{"private":' + "9" * 5000 + "}"


class ReceiptInputBoundsTests(unittest.TestCase):
    def test_all_stdin_receipt_analyzers_hold_unrepresentable_json_integers(self):
        for skill, script in (
            ("langfuse-experiment-guardian", "compare.py"),
            ("langfuse-cost-forensics", "inspect-costs.py"),
            ("langfuse-trace-ingestion-medic", "inspect-ingestion.py"),
            ("langfuse-prompt-release-guardian", "inspect-release.py"),
        ):
            with self.subTest(skill=skill):
                result = subprocess.run(
                    [sys.executable, str(ROOT / skill / "scripts" / script)], input=RAW, text=True, capture_output=True
                )
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertEqual(json.loads(result.stderr)["status"], "held")
                self.assertNotIn("private", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_webhook_local_replay_receipt_parser_holds_large_integer_without_traceback(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / "body.json").write_text("{}")
            (folder / "header.txt").write_text("unused")
            (folder / "seen.json").write_text(RAW)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "langfuse-prompt-release-guardian/scripts/verify-webhook.py"),
                    str(folder / "body.json"),
                    "--header-file",
                    str(folder / "header.txt"),
                    "--secret-env",
                    "SYNTHETIC_UNUSED_ENV",
                    "--project-id",
                    "synthetic-project",
                    "--seen-receipt",
                    str(folder / "seen.json"),
                ],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stderr)["status"], "held")
            self.assertNotIn("private", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
