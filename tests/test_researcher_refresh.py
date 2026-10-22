"""Offline dossier refresh regressions; gh never reaches the network."""

import importlib.util
import os
import re
import resource
from pathlib import Path
import subprocess
import tempfile
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins/community/contributing-clanker/skills/contribute-prepare/scripts"
BUILDER = SCRIPTS / "researcher-build.sh"
HEADINGS = ("Pet peeves & known triggers", "Failure log", "Notes")

SPEC = importlib.util.spec_from_file_location("researcher_refresh", SCRIPTS / "researcher-refresh.py")
REFRESH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REFRESH)


def dossier(auto=b"automatic", bodies=None):
    bodies = bodies or [b"\nManual note.\n"] * 3
    return auto + b"\n" + b"".join(b"## " + heading.encode() + b"\n" + body for heading, body in zip(HEADINGS, bodies))


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / "dossier.md"
        self.original = dossier(b"old automatic")
        self.target.write_bytes(self.original)
        self.generated = dossier(b"new automatic", [b"\nStub.\n"] * 3)

    def test_exact_bodies_fences_subheadings_and_crlf(self):
        bodies = [
            b"\r\n### Subheading\r\nKeep trailing spaces.  \r\n",
            b"\n````markdown\n## Notes\n```\n````\n",
            b"\n~~~markdown\n## Failure log\n~~~\n\n",
        ]
        existing = dossier(b"old", bodies)
        expected = dossier(b"new automatic", bodies)
        result = REFRESH.merge(self.generated, existing)
        self.assertEqual(result, expected)
        self.assertEqual(REFRESH.merge(self.generated, result), result)

    def test_empty_manual_bodies(self):
        self.assertEqual(
            REFRESH.merge(self.generated, dossier(b"old", [b""] * 3)), dossier(b"new automatic", [b""] * 3)
        )

    def test_ambiguous_existing_or_generated_refused(self):
        invalid = [
            self.original.replace(b"## Notes", b"## Other"),
            self.original + b"## Notes\nDuplicate\n",
            self.original + b"```\nunclosed\n",
            self.original + b"~~~\nunclosed\n",
            self.original + b"```bad`info\n",
            self.original + b"\xff",
        ]
        for content in invalid:
            for existing in (True, False):
                with self.subTest(content=content, existing=existing):
                    self.target.write_bytes(content if existing else self.original)
                    before = self.target.read_bytes()
                    with self.assertRaises(ValueError):
                        REFRESH.refresh(self.generated if existing else content, self.target)
                    self.assertEqual(self.target.read_bytes(), before)

    def test_success_retains_mode_and_leaves_no_stage(self):
        self.target.chmod(0o640)
        REFRESH.refresh(self.generated, self.target)
        self.assertEqual(self.target.read_bytes(), dossier(b"new automatic"))
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o640)
        self.assertEqual(list(self.target.parent.glob(".researcher-*")), [])

    def test_io_failures_preserve_existing(self):
        for operation in ("tempfile.mkstemp", "os.fchmod", "os.fsync", "os.replace", "snapshot"):
            owner, _, attribute = operation.rpartition(".")
            target = getattr(REFRESH, owner) if owner else REFRESH
            with self.subTest(operation=operation):
                with mock.patch.object(target, attribute, side_effect=OSError("injected I/O failure")):
                    with self.assertRaises(OSError):
                        REFRESH.refresh(self.generated, self.target)
                self.assertEqual(self.target.read_bytes(), self.original)
                self.assertEqual(list(self.target.parent.glob(".researcher-*")), [])

    def test_concurrent_change_refused(self):
        read = REFRESH.snapshot
        calls = 0
        edited = dossier(b"concurrent editor")

        def changing_snapshot(path):
            nonlocal calls
            calls += 1
            if calls == 2:
                path.write_bytes(edited)
            return read(path)

        with mock.patch.object(REFRESH, "snapshot", side_effect=changing_snapshot):
            with self.assertRaisesRegex(ValueError, "changed during refresh"):
                REFRESH.refresh(self.generated, self.target)
        self.assertEqual(self.target.read_bytes(), edited)

    def test_new_file_race_does_not_overwrite(self):
        self.target.unlink()
        link = REFRESH.os.link

        def create_before_link(source, destination):
            destination.write_bytes(b"another writer")
            return link(source, destination)

        with mock.patch.object(REFRESH.os, "link", side_effect=create_before_link):
            with self.assertRaises(FileExistsError):
                REFRESH.refresh(self.generated, self.target)
        self.assertEqual(self.target.read_bytes(), b"another writer")

    def test_symlink_and_directory_refused(self):
        other = self.target.with_name("other.md")
        other.write_bytes(self.original)
        self.target.unlink()
        self.target.symlink_to(other)
        with self.assertRaises(ValueError):
            REFRESH.refresh(self.generated, self.target)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(other.read_bytes(), self.original)
        self.target.unlink()
        self.target.mkdir()
        with self.assertRaises(ValueError):
            REFRESH.refresh(self.generated, self.target)

    def test_new_dossier_creates_stubs_and_parent(self):
        target = self.target.parent / "new" / "dossier.md"
        REFRESH.refresh(self.generated, target)
        self.assertEqual(target.read_bytes(), self.generated)
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)


class ResearcherRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text("""#!/usr/bin/env python3
import base64, json, os, sys
args = sys.argv[1:]
if args == ["auth", "status"]:
    sys.exit(0)
if args[:1] != ["api"]:
    sys.exit(98)
endpoint = args[1]
if endpoint == "repos/fixture/project":
    if os.environ.get("FIXTURE_FAIL"):
        sys.exit(1)
    print(json.dumps({"stargazers_count": int(os.environ.get("FIXTURE_STARS", "1")),
                      "default_branch": "main", "description": "Offline fixture"}))
elif endpoint == "repos/fixture/project/contents/CONTRIBUTING.md":
    if "--jq" in args:
        print(base64.b64encode(b"## Testing\\nRun tests.\\n").decode())
    else:
        print("{}")
elif "/pulls?" in endpoint:
    if os.environ.get("FIXTURE_OPTIONAL_FAIL"):
        sys.exit(1)
    print("[]")
else:
    sys.exit(1)
""")
        gh.chmod(0o755)
        self.env = dict(
            os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", CONTRIBUTE_STATE_DIR=str(self.root / "state")
        )
        self.env.pop("CONTRIBUTE_RESEARCH_DIR", None)
        self.target = self.root / "state/research/fixture__project.md"

    def build(self, *args, preexec_fn=None):
        return subprocess.run(
            ["bash", str(BUILDER), "fixture/project", *args],
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
            preexec_fn=preexec_fn,
        )

    def test_refresh_preserves_manual_bodies_and_updates_metadata(self):
        self.assertEqual(self.build().returncode, 0)
        original = self.target.read_text()
        bodies = [f"\nPersonal observation {i}.\n### Detail\n```markdown\n## Notes\n```\n\n" for i in range(3)]
        start = original.index("## " + HEADINGS[0])
        self.target.write_text(
            original[:start] + "".join(f"## {heading}\n{body}" for heading, body in zip(HEADINGS, bodies))
        )
        self.env["FIXTURE_STARS"] = "42"
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        refreshed = self.target.read_text()
        self.assertIn("stars: 42\n", refreshed)
        for body in bodies:
            self.assertIn(body, refreshed)
        again = self.build()
        self.assertEqual(again.returncode, 0, again.stderr)
        # Freshness timestamps intentionally change; all other bytes are stable.
        timestamp = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
        self.assertEqual(re.sub(timestamp, "TIME", self.target.read_text()), re.sub(timestamp, "TIME", refreshed))

    def test_stdout_is_merged_preview_and_does_not_write(self):
        self.target.parent.mkdir(parents=True)
        original = dossier()
        self.target.write_bytes(original)
        self.env["FIXTURE_STARS"] = "42"
        result = self.build("--stdout")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("stars: 42", result.stdout)
        self.assertIn("Manual note.", result.stdout)
        self.assertEqual(self.target.read_bytes(), original)
        self.assertNotIn("wrote dossier", result.stderr)

    def test_failed_required_read_preserves_existing(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_bytes(dossier())
        before = self.target.read_bytes()
        self.env["FIXTURE_FAIL"] = "1"
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.target.read_bytes(), before)
        self.assertNotIn("wrote dossier", result.stderr)

    def test_render_write_failure_preserves_existing(self):
        self.target.parent.mkdir(parents=True)
        before = dossier()
        self.target.write_bytes(before)

        def limit_file_size():
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024, 1024))

        result = self.build(preexec_fn=limit_file_size)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dossier rendering failed", result.stderr)
        self.assertEqual(self.target.read_bytes(), before)
        self.assertNotIn("wrote dossier", result.stderr)

    def test_optional_read_failure_still_builds(self):
        self.env["FIXTURE_OPTIONAL_FAIL"] = "1"
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("external_merge_rate_90d: 0", self.target.read_text())

    def test_malformed_existing_refused_with_nonzero_cli(self):
        self.target.parent.mkdir(parents=True)
        before = b"## Notes\nOnly one section\n"
        self.target.write_bytes(before)
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refused refresh", result.stderr)
        self.assertEqual(self.target.read_bytes(), before)
        self.assertNotIn("wrote dossier", result.stderr)


if __name__ == "__main__":
    unittest.main()
