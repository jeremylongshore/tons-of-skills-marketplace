"""Synthetic webhook verification tests; no signing service or provider calls."""

import copy
import hashlib
import hmac
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "plugins/saas-packs/langfuse-pack/skills/langfuse-prompt-release-guardian/scripts/verify-webhook.py"
)
SPEC = importlib.util.spec_from_file_location("langfuse_prompt_webhook", SCRIPT)
ENGINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENGINE)
SECRET = b"synthetic-test-only-signing-material"
NOW = 1790856000
PROJECT = "private-project"


def event():
    return {
        "id": "private-event",
        "timestamp": "2026-10-01T12:00:00Z",
        "type": "prompt-version",
        "apiVersion": "v1",
        "action": "updated",
        "prompt": {
            "id": "private-prompt-id",
            "name": "private-prompt-name",
            "projectId": PROJECT,
            "version": 3,
            "labels": ["private-label"],
            "type": "text",
            "prompt": "private prompt {{private_variable}}",
            "config": {"private": "content"},
        },
    }


def signed(payload=None, signed_at=NOW):
    raw = json.dumps(event() if payload is None else payload, ensure_ascii=False).encode()
    header = (
        "t="
        + str(signed_at)
        + ",v1="
        + hmac.new(SECRET, str(signed_at).encode() + b"." + raw, hashlib.sha256).hexdigest()
    )
    return raw, header


def history():
    return {"schema_version": 1, "project_sha256": ENGINE.digest(PROJECT), "processed_event_sha256": []}


class PromptWebhookTests(unittest.TestCase):
    def test_native_envelope_authenticates_without_echoing_content(self):
        raw, header = signed()
        result = ENGINE.verify(raw, header, SECRET, PROJECT, NOW, history())
        self.assertEqual(result["status"], "authenticated-supplied-event")
        self.assertFalse(result["replay_in_supplied_history"])
        self.assertEqual(result["version"], 3)
        for private in ("private", SECRET.decode(), header):
            self.assertNotIn(private, json.dumps(result))

    def test_reformatted_bytes_do_not_inherit_a_valid_signature(self):
        raw, header = signed()
        for changed in (
            raw + b"\n",
            json.dumps(event(), separators=(",", ":")).encode(),
            raw.replace(b'version": 3', b'version": 4'),
        ):
            with self.subTest(changed=changed):
                with self.assertRaisesRegex(ENGINE.InvalidReceipt, "signature-mismatch"):
                    ENGINE.verify(changed, header, SECRET, PROJECT, NOW, history())

    def test_old_bare_body_hmac_format_is_rejected(self):
        raw, _ = signed()
        bare = hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "invalid-signature-header"):
            ENGINE.verify(raw, bare, SECRET, PROJECT, NOW, history())
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "signature-mismatch"):
            ENGINE.verify(raw, "t=" + str(NOW) + ",v1=" + bare, SECRET, PROJECT, NOW, history())

    def test_duplicate_malformed_and_ambiguous_headers_are_rejected(self):
        raw, header = signed()
        for altered in (
            header + ",v1=" + "0" * 64,
            header.replace("t=", "x="),
            header.replace("v1=", "v2="),
            header + ",t=" + str(NOW),
            header[:-1],
            "t=-1,v1=" + "0" * 64,
        ):
            with self.assertRaisesRegex(ENGINE.InvalidReceipt, "invalid-signature-header"):
                ENGINE.verify(raw, altered, SECRET, PROJECT, NOW, history())

    def test_exact_review_window_and_future_replays(self):
        for age in (-301, 301):
            raw, header = signed(signed_at=NOW + age)
            with self.assertRaisesRegex(ENGINE.InvalidReceipt, "review-window"):
                ENGINE.verify(raw, header, SECRET, PROJECT, NOW, history())
        for age in (-300, 300):
            raw, header = signed(signed_at=NOW + age)
            self.assertEqual(
                ENGINE.verify(raw, header, SECRET, PROJECT, NOW, history())["status"], "authenticated-supplied-event"
            )

    def test_wrong_key_or_project_cannot_authenticate_for_requested_project(self):
        raw, header = signed()
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "signature-mismatch"):
            ENGINE.verify(raw, header, b"wrong-synthetic-material", PROJECT, NOW, history())
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "event-project-mismatch"):
            ENGINE.verify(raw, header, SECRET, "different-project", NOW, history())

    def test_no_history_does_not_claim_replay_protection(self):
        raw, header = signed()
        result = ENGINE.verify(raw, header, SECRET, PROJECT, NOW, None)
        self.assertEqual(result["status"], "signature-valid-replay-unchecked")
        self.assertIsNone(result["replay_in_supplied_history"])

    def test_repeated_event_id_stays_duplicate_when_signed_again_with_different_body(self):
        raw, header = signed()
        seen = history()
        first = ENGINE.verify(raw, header, SECRET, PROJECT, NOW, seen)
        seen["processed_event_sha256"].append(first["event_sha256"])
        changed = event()
        changed["prompt"]["labels"] = []
        raw, header = signed(changed, NOW + 1)
        before = copy.deepcopy(seen)
        result = ENGINE.verify(raw, header, SECRET, PROJECT, NOW + 1, seen)
        self.assertEqual(result["status"], "duplicate-supplied-event")
        self.assertEqual(seen, before)

    def test_history_is_project_bound_and_rejects_invalid_or_duplicate_hashes(self):
        raw, header = signed()
        for update in (
            {"project_sha256": "0" * 64},
            {"processed_event_sha256": ["bad"]},
            {"processed_event_sha256": ["0" * 64, "0" * 64]},
            {"schema_version": True},
        ):
            seen = history()
            seen.update(update)
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.verify(raw, header, SECRET, PROJECT, NOW, seen)

    def test_authentication_precedes_json_parsing(self):
        raw, header = signed()
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "signature-mismatch"):
            ENGINE.verify(b"not-json-private", header, SECRET, PROJECT, NOW, history())
        malformed = b'{"id":"private","id":"private"}'
        digest = hmac.new(SECRET, str(NOW).encode() + b"." + malformed, hashlib.sha256).hexdigest()
        with self.assertRaisesRegex(ENGINE.InvalidReceipt, "duplicate-json-field"):
            ENGINE.verify(malformed, "t=" + str(NOW) + ",v1=" + digest, SECRET, PROJECT, NOW, history())

    def test_native_action_contract_is_not_legacy_event_data(self):
        for key, value in (("type", "prompt.updated"), ("apiVersion", "v2"), ("action", "promote")):
            payload = event()
            payload[key] = value
            raw, header = signed(payload)
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.verify(raw, header, SECRET, PROJECT, NOW, history())

    def test_invalid_version_label_and_content_shape_are_held(self):
        for key, value in (
            ("version", True),
            ("version", 0),
            ("labels", ["duplicate", "duplicate"]),
            ("labels", "production"),
            ("prompt", {}),
            ("type", "unknown"),
        ):
            payload = event()
            payload["prompt"][key] = value
            raw, header = signed(payload)
            with self.assertRaises(ENGINE.InvalidReceipt):
                ENGINE.verify(raw, header, SECRET, PROJECT, NOW, history())

    def test_utf8_chat_and_deleted_envelopes_can_authenticate_without_release_approval(self):
        payload = event()
        payload["action"] = "deleted"
        payload["prompt"].update(type="chat", prompt=[{"role": "user", "content": "synthetic caf\u00e9"}])
        raw, header = signed(payload)
        result = ENGINE.verify(raw, header, SECRET, PROJECT, NOW, history())
        self.assertEqual(result["status"], "authenticated-supplied-event")
        self.assertTrue(any("does not authorize deployment" in item for item in result["limits"]))

    def test_stale_payload_time_is_not_treated_as_current_label_state(self):
        payload = event()
        payload["timestamp"] = "2024-01-01T00:00:00Z"
        raw, header = signed(payload)
        result = ENGINE.verify(raw, header, SECRET, PROJECT, NOW, history())
        self.assertEqual(result["status"], "authenticated-supplied-event")
        self.assertTrue(any("current deployed version require fresh" in item for item in result["limits"]))

    def test_cli_secret_is_env_only_and_exit_codes_are_honest(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            raw, header = signed()
            (temp / "body.json").write_bytes(raw)
            (temp / "header.txt").write_text(header + "\n")
            (temp / "seen.json").write_text(json.dumps(history()))
            command = [
                sys.executable,
                str(SCRIPT),
                str(temp / "body.json"),
                "--header-file",
                str(temp / "header.txt"),
                "--secret-env",
                "SYNTHETIC_TEST_ONLY",
                "--project-id",
                PROJECT,
                "--now",
                str(NOW),
            ]
            environment = {**os.environ, "SYNTHETIC_TEST_ONLY": SECRET.decode()}
            result = subprocess.run(command, env=environment, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1)
            result = subprocess.run(
                command + ["--seen-receipt", str(temp / "seen.json")], env=environment, text=True, capture_output=True
            )
            self.assertEqual(result.returncode, 0)
            environment.pop("SYNTHETIC_TEST_ONLY")
            result = subprocess.run(command, env=environment, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("private", result.stdout + result.stderr)
            self.assertNotIn(SECRET.decode(), result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
