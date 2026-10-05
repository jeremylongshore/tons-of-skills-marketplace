"""Regression test for the podium-pack webhook server's log sanitization.

CodeQL py/log-injection (alert 2305, mirrored at alert 2875 in the generated
skills/.curated/ copy): `dispatch()` interpolates the attacker-controlled
`event.type` / `event.id` webhook payload fields directly into a log line.
A valid HMAC signature proves the payload came from the configured source,
not that its string fields are free of CR/LF — so a crafted field can forge
additional log lines. `safe_log_value()` must strip CR/LF and other control
characters before any payload value reaches the logger.

`webhook_server.py` imports fastapi at module scope, which is not a
repo-wide Python dependency, so this test stubs the handful of fastapi names
the module touches (decorators/signature-only usage, never invoked) rather
than requiring fastapi to be installed. Lives here, not in the skill, so the
test is not shipped to users with the skill.
"""

import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "plugins/saas-packs/podium-pack/skills/podium-webhook-reliability/scripts/webhook_server.py"
)


def _install_fastapi_stub() -> None:
    if "fastapi" in sys.modules:
        return

    class _FastAPI:
        def post(self, *_a, **_kw):
            def deco(fn):
                return fn

            return deco

        def get(self, *_a, **_kw):
            def deco(fn):
                return fn

            return deco

    class _Request:
        pass

    class _HTTPException(Exception):
        def __init__(self, status_code=500, detail=None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    def _Header(default=None, **_kw):
        return default

    stub = types.ModuleType("fastapi")
    stub.FastAPI = _FastAPI
    stub.Request = _Request
    stub.HTTPException = _HTTPException
    stub.Header = _Header
    sys.modules["fastapi"] = stub


def load_module():
    _install_fastapi_stub()
    spec = importlib.util.spec_from_file_location("podium_webhook_server", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SafeLogValue(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_plain_values_pass_through_unchanged(self):
        self.assertEqual(self.module.safe_log_value("call.completed"), "call.completed")
        self.assertEqual(self.module.safe_log_value("evt_123"), "evt_123")

    def test_crlf_is_stripped_so_a_forged_log_line_cannot_be_injected(self):
        hostile = 'evt_123\r\n{"ts": "fake", "lvl": "ERROR", "msg": "forged entry"}'
        cleaned = self.module.safe_log_value(hostile)
        self.assertNotIn("\r", cleaned)
        self.assertNotIn("\n", cleaned)
        self.assertEqual(
            cleaned,
            'evt_123{"ts": "fake", "lvl": "ERROR", "msg": "forged entry"}',
        )

    def test_other_control_characters_are_stripped(self):
        self.assertEqual(self.module.safe_log_value("a\x00b\x1bc\x7f"), "abc")

    def test_non_string_values_are_coerced_before_sanitizing(self):
        self.assertEqual(self.module.safe_log_value(None), "None")
        self.assertEqual(self.module.safe_log_value(42), "42")


if __name__ == "__main__":
    unittest.main()
