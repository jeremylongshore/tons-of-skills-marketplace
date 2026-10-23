"""Offline contract and failure-path tests; upstream text is never executed."""

import importlib.util
import hashlib
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("forge_api_drift", ROOT / "scripts/forge-api-drift.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class FakeSource:
    def __init__(self, resources=None):
        self.calls = []
        self.resources = resources or {
            M.REGISTRY: b"RESOURCES = (cycle,)\n",
            "plane_mcp/tools/cycle.py": b'NAME = "cycle"\nLEGACY = {"list_cycles": "list"}\n',
        }

    def get(self, url):
        self.calls.append(url)
        if url.endswith("/commits/main"):
            return json.dumps({"sha": "a" * 40}).encode()
        path = url.split("/" + "a" * 40 + "/", 1)[1]
        return self.resources[path]


class DriftTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plugin = "plugins/productivity/plane"
        p = self.root / self.plugin / ".forge/research.md"
        p.parent.mkdir(parents=True)
        self.research = b"## Gate 3 \xe2\x80\x94 API surface research\n- `list_cycles` x\n## Gate 4\n"
        p.write_bytes(self.research)
        self.entry = {
            "plugin": self.plugin,
            "research_sha256": hashlib.sha256(self.research).hexdigest(),
            "captured_tools": ["list_cycles"],
            "probe": {
                "kind": "plane-python-catalogue",
                "repository": M.REPOSITORY,
                "branch": "main",
                "registry": M.REGISTRY,
            },
        }

    def inspect(self, source=None):
        return M.inspect(self.root, self.entry, source or FakeSource())

    def test_declared_alias_prevents_false_removal_and_all_sources_are_pinned(self):
        source = FakeSource()
        result = self.inspect(source)
        self.assertEqual(result["status"], "NO_NAME_DRIFT")
        self.assertEqual(result["declared_aliases"]["list_cycles"]["tool"], "cycle")
        self.assertEqual(len(result["source_sha256"]), 2)
        self.assertTrue(all("/" + "a" * 40 + "/" in url for url in source.calls[1:]))

    def test_actual_missing_name_is_not_hidden_by_an_unrelated_name(self):
        source = FakeSource()
        source.resources["plane_mcp/tools/cycle.py"] = b'NAME="cycle"\nLEGACY={"list_other":"list"}\n'
        result = self.inspect(source)
        self.assertEqual(result["status"], "NAME_DRIFT")
        self.assertEqual(result["missing_tools"], ["list_cycles"])

    def test_explicit_unmappable_name_is_drift(self):
        source = FakeSource()
        source.resources["plane_mcp/tools/cycle.py"] = (
            b'NAME="cycle"\nLEGACY={}\nLEGACY_UNMAPPED={"list_cycles":"use cycle"}\n'
        )
        result = self.inspect(source)
        self.assertEqual(result["status"], "NAME_DRIFT")
        self.assertEqual(result["explicitly_unmapped"], ["list_cycles"])

    def test_source_code_is_not_executed(self):
        source = FakeSource()
        marker = self.root / "must-not-exist"
        source.resources["plane_mcp/tools/cycle.py"] += f'\nopen({str(marker)!r},"w").write("bad")\n'.encode()
        self.assertEqual(self.inspect(source)["status"], "NO_NAME_DRIFT")
        self.assertFalse(marker.exists())

    def test_unregistered_file_does_not_rescue_a_removed_tool(self):
        source = FakeSource()
        source.resources["plane_mcp/tools/unregistered.py"] = source.resources["plane_mcp/tools/cycle.py"]
        source.resources["plane_mcp/tools/cycle.py"] = b'NAME="cycle"\nLEGACY={}\n'
        self.assertEqual(self.inspect(source)["status"], "NAME_DRIFT")

    def test_changed_research_or_names_refuses_before_network(self):
        for key, value in [("research_sha256", "0" * 64), ("captured_tools", ["other"])]:
            original = self.entry[key]
            self.entry[key] = value
            source = FakeSource()
            self.assertEqual(self.inspect(source)["status"], "UNVERIFIED")
            self.assertEqual(source.calls, [])
            self.entry[key] = original

    def test_unsupported_target_refuses_before_network(self):
        self.entry["probe"]["repository"] = "attacker/anything"
        source = FakeSource()
        self.assertEqual(self.inspect(source)["status"], "UNVERIFIED")
        self.assertEqual(source.calls, [])

    def test_fetch_or_parse_failure_cannot_be_no_drift(self):
        for body in [b"RESOURCES = discover()\n", b"not python !", b"RESOURCES=(cycle,cycle)"]:
            source = FakeSource()
            source.resources[M.REGISTRY] = body
            self.assertEqual(self.inspect(source)["status"], "UNVERIFIED")
        source = FakeSource()
        source.resources.pop("plane_mcp/tools/cycle.py")
        self.assertEqual(self.inspect(source)["status"], "UNVERIFIED")

    def test_nonliteral_alias_duplicate_assignment_and_collisions_refuse(self):
        for body in [
            b'NAME="cycle"\nLEGACY=load()\n',
            b'NAME="cycle"\nNAME="other"\nLEGACY={}\n',
            b'NAME="cycle"\nLEGACY={"cycle":"list"}\n',
        ]:
            source = FakeSource()
            source.resources["plane_mcp/tools/cycle.py"] = body
            self.assertEqual(self.inspect(source)["status"], "UNVERIFIED")

    def test_new_forge_capture_without_probe_is_visible_unknown(self):
        p = self.root / "plugins/testing/new/.forge/research.md"
        p.parent.mkdir(parents=True)
        p.write_text("new")
        report = M.run(self.root, {"schema_version": 1, "plugins": [self.entry]}, FakeSource())
        self.assertEqual(report["results"][1]["reason"], "NO_REVIEWED_PROBE")

    def test_http_body_and_global_byte_budgets_are_enforced(self):
        class Reply:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read1(self, size):
                count = min(size, self.remaining)
                self.remaining -= count
                return b"x" * count

        for initial in [0, 8 * 1024 * 1024]:
            source = M.PublicSource()
            source.total = initial
            source.opener = mock.Mock()
            reply = Reply()
            reply.remaining = M.MAX_BODY + 1 if initial == 0 else 1
            source.opener.open.return_value = reply
            with self.assertRaises(M.Unverified):
                source.get("https://api.github.com/repos/" + M.REPOSITORY + "/commits/main")
            if initial == 0:
                self.assertEqual(source.total, M.MAX_BODY + 1)
            else:
                source.opener.open.assert_not_called()

    def test_trickle_cannot_extend_the_global_deadline(self):
        clock = [0]

        class Reply:
            status = 200
            reads = 0

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read1(self, size):
                self.reads += 1
                clock[0] = 121
                return b"x"

        reply = Reply()
        with mock.patch.object(M.time, "monotonic", side_effect=lambda: clock[0]):
            source = M.PublicSource()
            source.opener = mock.Mock()
            source.opener.open.return_value = reply
            with self.assertRaisesRegex(M.Unverified, "DEADLINE"):
                source.get("https://api.github.com/repos/" + M.REPOSITORY + "/commits/main")
        self.assertEqual(reply.reads, 1)

    def test_exhausted_deadline_refuses_before_open(self):
        source = M.PublicSource()
        source.deadline = 0
        source.opener = mock.Mock()
        with self.assertRaisesRegex(M.Unverified, "DEADLINE"):
            source.get("https://api.github.com/repos/" + M.REPOSITORY + "/commits/main")
        source.opener.open.assert_not_called()

    def test_actual_research_capture_exactly_matches_registered_baseline(self):
        config = json.loads((ROOT / "scripts/forge-api-surfaces.json").read_text())
        for entry in config["plugins"]:
            data = (ROOT / entry["plugin"] / ".forge/research.md").read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["research_sha256"])
            self.assertEqual(M.captured_names(data.decode()), entry["captured_tools"])
        self.assertEqual(len(config["plugins"][0]["captured_tools"]), 13)

    def test_size_bound_and_redirect_refusal(self):
        with self.assertRaises(M.Unverified):
            M.assignments(b"x" * (M.MAX_BODY + 1))
        with self.assertRaises(M.Unverified):
            M.NoRedirect().redirect_request(None, None, 302, "", {}, "http://localhost/")
        with self.assertRaises(M.Unverified):
            M.PublicSource().get("http://localhost/")


if __name__ == "__main__":
    unittest.main()
