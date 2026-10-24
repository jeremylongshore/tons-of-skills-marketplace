"""Report-sink tests; optional integration uses the real, unvendored C8 policy."""

import datetime as dt
import fcntl
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "plugins/productivity/000-jeremy-content-consistency-validator/skills/validate-consistency/scripts/persist-report.py"
)
SPEC = importlib.util.spec_from_file_location("consistency_report_sink", SCRIPT)
SINK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SINK)
AT = dt.datetime(2026, 10, 24, 3, 0, tzinfo=dt.timezone.utc)
REPORT = (
    "# Document Consistency Audit Report\n\n"
    "**Project:** fixture-widget\n**Registry:** sot-map.yaml, version-string owned by package-manifest\n\n"
    + SINK.PART_A
    + "\n\nVersion drift: README 1.0.0; package.json authority 1.1.0.\n\n"
    + SINK.PART_B
    + "\n\nNo advisory findings.\n"
)


def payload(report=REPORT, **kwargs):
    return json.dumps({"report": report, **kwargs}).encode()


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="consistency-sink-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.audited = self.root / "audited-project"
        self.audited.mkdir()
        (self.root / ".git").mkdir()
        (self.root / "000-docs").mkdir()
        self.index = self.root / "000-docs/000-INDEX.md"
        self.before = "# Existing index\n\nExisting unrelated edits stay byte-identical.\n"
        self.index.write_text(self.before)
        (self.root / "000-docs/041-AA-cluster").mkdir()
        (self.root / "000-docs/041-AA-cluster/092-AA-AUDR-prior.md").write_text("Prior record\n")

    def approved(self):
        # Unit tests isolate filesystem behavior; these are NOT privacy-policy tests.
        return patch.object(SINK, "screen", return_value={"sink": "evidence-ingest", "body_sha256": "a" * 64})

    def test_numbered_report_preserves_lanes_authority_repairs_and_index_prefix(self):
        data = payload(repairs=[{"summary": "Updated README version", "evidence": "reviewed commit fixture-proof"}])
        with self.approved():
            result = SINK.persist(self.root, data, AT, audited_root=self.audited)
        self.assertEqual(result["status"], "saved")
        self.assertTrue(result["path"].startswith("000-docs/093-AA-AUDR-consistency-"))
        written = (self.root / result["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(written).hexdigest(), result["sha256"])
        self.assertIn(REPORT.rstrip(), written.decode())
        self.assertIn("package.json authority 1.1.0", written.decode())
        self.assertIn("Updated README version", written.decode())
        self.assertIn("not perform repairs or independently adjudicate", written.decode())
        self.assertTrue(self.index.read_text().startswith(self.before))
        self.assertIn(Path(result["path"]).name, self.index.read_text())

    def test_identical_retry_never_overwrites_or_adds_an_index_entry(self):
        with self.approved():
            result = SINK.persist(self.root, payload(), AT, audited_root=self.audited)
            before = self.index.read_bytes()
            original = (self.root / result["path"]).read_bytes()
            with self.assertRaisesRegex(SINK.Held, "already-recorded"):
                SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(self.index.read_bytes(), before)
        self.assertEqual((self.root / result["path"]).read_bytes(), original)

    def test_moved_record_in_cluster_still_blocks_identical_retry(self):
        with self.approved():
            result = SINK.persist(self.root, payload(), AT, audited_root=self.audited)
            original = self.root / result["path"]
            original.rename(self.root / "000-docs/041-AA-cluster" / original.name)
            before = self.index.read_bytes()
            with self.assertRaisesRegex(SINK.Held, "already-recorded"):
                SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(self.index.read_bytes(), before)

    def test_destination_cannot_be_the_audited_tree(self):
        with self.approved() as screening:
            with self.assertRaisesRegex(SINK.Held, "destination-inside-audited-tree"):
                SINK.persist(self.root, payload(), AT, audited_root=self.root)
        screening.assert_not_called()
        self.assertEqual(self.index.read_text(), self.before)

    def test_symlink_file_or_directory_in_numbered_tree_is_held(self):
        for name, target in [("777-AA-linked.md", self.index), ("888-AA-linked", self.audited)]:
            with self.subTest(name=name), self.approved():
                link = self.root / "000-docs" / name
                link.symlink_to(target)
                try:
                    with self.assertRaisesRegex(SINK.Held, "symlink-in-document-tree"):
                        SINK.persist(self.root, payload(), AT, audited_root=self.audited)
                finally:
                    link.unlink()  # Owned scratch fixture only.
        self.assertEqual(self.index.read_text(), self.before)

    def test_missing_lanes_and_unsubstantiated_repair_shape_are_rejected(self):
        for data in [payload("one merged findings section"), payload(repairs=[{"summary": "fixed"}])]:
            with self.assertRaises(SINK.Held):
                SINK.persist(self.root, data, AT, audited_root=self.audited)
        self.assertEqual(self.index.read_text(), self.before)

    def test_policy_hold_writes_no_report_or_index_bytes(self):
        with patch.object(SINK, "screen", side_effect=SINK.Held("disclosure-held")):
            with self.assertRaisesRegex(SINK.Held, "disclosure-held"):
                SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(self.index.read_text(), self.before)
        self.assertFalse(list((self.root / "000-docs").glob("*-consistency-*.md")))

    def test_missing_policy_is_held_before_any_destination_write(self):
        with self.assertRaisesRegex(SINK.Held, "missing-required-file"):
            SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(self.index.read_text(), self.before)
        self.assertFalse(list((self.root / "000-docs").glob("*-consistency-*.md")))

    def test_index_symlink_is_rejected_without_following_it(self):
        other = self.root / "outside.md"
        other.write_text("do not modify")
        self.index.unlink()  # Owned scratch fixture only.
        self.index.symlink_to(other)
        with self.assertRaisesRegex(SINK.Held, "symlink-path"):
            SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(other.read_text(), "do not modify")

    def test_busy_index_is_held_without_creating_a_report(self):
        with self.index.open() as owner, self.approved():
            fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(SINK.Held, "index-busy"):
                SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(self.index.read_text(), self.before)
        self.assertFalse(list((self.root / "000-docs").glob("*-consistency-*.md")))

    def test_index_write_failure_preserves_report_and_reports_incomplete(self):
        with self.approved(), patch.object(SINK.os, "write", side_effect=OSError("fixture index failure")):
            with self.assertRaisesRegex(SINK.Held, "report-saved-index-incomplete"):
                SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(self.index.read_text(), self.before)
        self.assertEqual(len(list((self.root / "000-docs").glob("*-consistency-*.md"))), 1)

    def test_concurrent_index_replacement_is_preserved_and_reported_incomplete(self):
        original_write = os.write

        def replace_after_append(fd, data):
            count = original_write(fd, data)
            replacement = self.root / "new-index.md"
            replacement.write_text("Concurrent owner's replacement index\n")
            replacement.replace(self.index)  # Owned scratch fixture only.
            return count

        with self.approved(), patch.object(SINK.os, "write", side_effect=replace_after_append):
            with self.assertRaisesRegex(SINK.Held, "report-saved-index-incomplete"):
                SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(self.index.read_text(), "Concurrent owner's replacement index\n")
        self.assertEqual(len(list((self.root / "000-docs").glob("*-consistency-*.md"))), 1)


class PolicyTransportTests(unittest.TestCase):
    def test_temp_parent_inside_destination_or_audited_tree_is_held_before_adapter(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as audited:
            root = Path(folder)
            for relative in ["ops/disclosure-policy/policy.py", "ops/disclosure-policy/adapters/enforce.sh"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("transport fixture; not a privacy policy")
            for parent in [folder, audited]:
                with self.subTest(parent=parent), patch.object(SINK.tempfile, "gettempdir", return_value=parent):
                    with patch.object(SINK.subprocess, "run") as adapter:
                        with self.assertRaisesRegex(SINK.Held, "temporary-directory-inside-protected-tree"):
                            SINK.screen(root, REPORT, REPORT, AT.timestamp(), audited_root=Path(audited))
                        adapter.assert_not_called()

    def test_success_exit_with_dropped_payload_does_not_authorize_a_write(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for relative in ["ops/disclosure-policy/policy.py", "ops/disclosure-policy/adapters/enforce.sh"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("transport placeholder; not a privacy policy")

            def dropped(args, **kwargs):
                receipts = Path(args[args.index("--receipts") + 1])
                run = Path(args[args.index("--run-receipt") + 1])
                receipts.write_text("")
                run.write_text(json.dumps({"counts": {"pass": 0, "rejected": 2, "redacted": 0, "held": 0}}))
                return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

            with patch.object(SINK.subprocess, "run", side_effect=dropped):
                with self.assertRaisesRegex(SINK.Held, "disclosure-held"):
                    SINK.screen(root, REPORT, REPORT, AT.timestamp())

    def test_accepted_output_without_durable_receipts_is_held(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for relative in ["ops/disclosure-policy/policy.py", "ops/disclosure-policy/adapters/enforce.sh"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("transport placeholder; not a privacy policy")

            def missing_receipts(args, **kwargs):
                return subprocess.CompletedProcess(args, 0, stdout=kwargs["input"], stderr="")

            with patch.object(SINK.subprocess, "run", side_effect=missing_receipts):
                with self.assertRaisesRegex(SINK.Held, "disclosure-unavailable"):
                    SINK.screen(root, REPORT, REPORT, AT.timestamp())


@unittest.skipUnless(
    os.environ.get("INTENT_OS_DISCLOSURE_ROOT"), "real C8 policy is not vendored; set INTENT_OS_DISCLOSURE_ROOT"
)
class CanonicalPolicyIntegrationTests(unittest.TestCase):
    def setUp(self):
        PersistenceTests.setUp(self)
        canonical = Path(os.environ["INTENT_OS_DISCLOSURE_ROOT"])
        for relative in ["ops/disclosure-policy/policy.py", "ops/disclosure-policy/adapters/enforce.sh"]:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(canonical / relative, target)

    def test_real_filter_saves_only_approved_report(self):
        result = SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertTrue((self.root / result["path"]).is_file())
        self.assertEqual(result["disclosure"]["sink"], "evidence-ingest")

    def test_real_rejection_fault_bypass_and_missing_policy_do_not_leak(self):
        prohibited = "AK" + "IA" + "EXAMPLEFIXTUREKEY0"
        cases = [
            (payload(REPORT + "\n" + prohibited), {}),
            (payload(), {"C8_CLASSIFIER_FAULT": "1"}),
            (payload(), {"C8_BYPASS": "1"}),
        ]
        for data, env in cases:
            with self.subTest(env=env), patch.dict(os.environ, env):
                with self.assertRaises(SINK.Held):
                    SINK.persist(self.root, data, AT, audited_root=self.audited)
            self.assertEqual(self.index.read_text(), self.before)
            self.assertFalse(list((self.root / "000-docs").glob("*-consistency-*.md")))
        (self.root / "ops/disclosure-policy/policy.py").unlink()  # Scratch copy only.
        with self.assertRaises(SINK.Held):
            SINK.persist(self.root, payload(), AT, audited_root=self.audited)
        self.assertEqual(self.index.read_text(), self.before)

    def test_cli_failure_output_contains_no_rejected_content(self):
        prohibited = "AK" + "IA" + "EXAMPLEFIXTUREKEY0"
        result = subprocess.run(
            [
                os.sys.executable,
                str(SCRIPT),
                "--intent-os",
                str(self.root),
                "--audited-root",
                str(self.audited),
                "--at",
                "2026-10-24T03:00:00Z",
            ],
            input=payload(REPORT + "\n" + prohibited),
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(prohibited.encode(), result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "held")


if __name__ == "__main__":
    unittest.main()
