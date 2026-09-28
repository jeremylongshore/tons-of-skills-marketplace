"""Regression test for the podium-pack webchat partial-state path guard.

CodeQL py/path-injection: phone_e164 and location_uid come from the inbound
webhook payload. _partial_state_path must never produce a path outside the
partial-state directory, whatever those values contain. Lives here, not in
the skill, so the test is not shipped to users with the skill.
"""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/saas-packs/podium-pack/skills/podium-webchat-handler/scripts/webchat_ingest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("podium_webchat_ingest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve types through sys.modules
    spec.loader.exec_module(module)
    return module


class WebchatPathGuard(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.state_dir = Path(tempfile.mkdtemp())
        self.module.PARTIAL_STATE_DIR = self.state_dir

    def test_normal_values_keep_a_readable_name_inside_the_state_dir(self):
        path = self.module._partial_state_path("+15551234567", "loc_ABC-123")
        self.assertEqual(path.parent, self.state_dir)
        self.assertEqual(path.name, "p15551234567__loc_ABC-123.json")

    def test_traversal_values_never_leave_the_state_dir(self):
        hostile = [
            ("+15551234567", "../../etc/passwd"),
            ("../../x", "loc"),
            ("+1555", "a/../../b"),
            ("+1555", ".."),
            ("+1555", "/absolute/path"),
            ("+1555", "..\\..\\windows"),
        ]
        for phone, location in hostile:
            with self.subTest(phone=phone, location=location):
                path = self.module._partial_state_path(phone, location)
                self.assertEqual(path.parent, self.state_dir)
                self.assertNotIn("/", path.name)
                self.assertNotIn("..", path.name.replace("__", "_"))


if __name__ == "__main__":
    unittest.main()
