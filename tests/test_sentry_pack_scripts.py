"""Regression contract for the sentry-pack v2 helper scripts.

The pack's skills are advisory: scripts read pasted input, print to stdout,
make no network calls and refuse write actions. These tests pin that contract.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "plugins" / "saas-packs" / "sentry-pack"
LIB = PACK / "scripts" / "lib"
SCRIPTS = sorted((PACK / "skills").glob("*/scripts/*.py"))

# (script relative to the pack, extra args) for every script with an --apply path.
REFUSAL_CASES = (
    ("skills/sentry-event-forensics/scripts/parse-resolved-with.py", []),
    ("skills/sentry-issue-triage/scripts/fingerprint-from-event.py", []),
    ("skills/sentry-issue-triage/scripts/issue-context.py", []),
    ("skills/sentry-quota-leak-hunter/scripts/parse-usage-stats.py", []),
    ("skills/sentry-pii-scrub-enforcer/scripts/settings-diff.py", []),
)


def run(script: Path, *args: str, stdin: str = "{}") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, script.name, *args],
        cwd=script.parent,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=60,
    )


class SentryPackScriptsContract(unittest.TestCase):
    def test_every_script_answers_help(self):
        self.assertGreaterEqual(len(SCRIPTS), 11)
        for script in SCRIPTS:
            with self.subTest(script=script.name):
                result = run(script, "--help")
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_apply_is_refused_cleanly_without_a_traceback(self):
        for rel, extra in REFUSAL_CASES:
            script = PACK / rel
            with self.subTest(script=script.name):
                result = run(script, "--apply", *extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("refuses write action", result.stdout + result.stderr)

    def test_no_script_imports_a_network_client(self):
        for script in [*SCRIPTS, LIB / "sentry_readonly.py"]:
            source = script.read_text(encoding="utf-8")
            with self.subTest(script=script.name):
                for banned in ("import requests", "urllib.request", "import httpx", "http.client", "subprocess"):
                    self.assertNotIn(banned, source)

    def test_redaction_removes_all_three_token_shapes(self):
        script = PACK / "skills/sentry-event-forensics/scripts/redact-support-bundle.py"
        bundle = (
            "dsn ok\n"
            "token sntrys_abcDEF123.xyz-789\n"
            "SENTRY_AUTH_TOKEN=supersecretvalue\n"
            "Authorization: Bearer anothersecret\n"
        )
        result = run(script, "--json", "-", stdin=bundle)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for secret in ("sntrys_abcDEF123", "supersecretvalue", "anothersecret"):
            self.assertNotIn(secret, result.stdout)

    def test_client_is_advisory_and_honest_about_live_fetch(self):
        sys.path.insert(0, str(LIB))
        try:
            from sentry_readonly import SentryReadOnlyClient, SentryReadOnlyError
        finally:
            sys.path.remove(str(LIB))
        client = SentryReadOnlyClient(token=None)
        self.assertEqual(client.fetch_event_json("abc", pasted=json.dumps({"id": "abc"})), {"id": "abc"})
        with self.assertRaises(SentryReadOnlyError):
            client.fetch_event_json("abc", pasted="not json")
        with self.assertRaises(SentryReadOnlyError):
            client.refuse_write("anything")
        source = (LIB / "sentry_readonly.py").read_text(encoding="utf-8")
        self.assertNotIn("TODO", source)


if __name__ == "__main__":
    unittest.main()
