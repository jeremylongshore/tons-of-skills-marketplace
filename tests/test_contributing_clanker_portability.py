"""Regression tests for the contributing-clanker community trust boundary."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import time
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/community/contributing-clanker"
SKILLS = PLUGIN / "skills"
CURATED_AUDIT = ROOT / "skills/.curated/contribute"


class ContributingClankerPortabilityTests(unittest.TestCase):
    def test_authority_is_split_into_three_skills(self) -> None:
        expected = {"contribute", "contribute-prepare", "contribute-publish"}
        actual = {path.parent.name for path in SKILLS.glob("*/SKILL.md")}
        self.assertEqual(actual, expected)

    def test_default_skill_is_read_only_and_has_no_load_time_shell(self) -> None:
        text = (SKILLS / "contribute/SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        for forbidden in ("  - Write", "  - Edit", "  - Task", "Bash(npm:*)", "Bash(pnpm:*)"):
            self.assertNotIn(forbidden, frontmatter)
        self.assertNotIn("```!", text)
        self.assertIn("Do not run prompt-load or activation-time shell commands", text)

    def test_no_automatic_persistence_hooks_exist(self) -> None:
        self.assertFalse((PLUGIN / "hooks").exists())

    def test_distribution_is_decoupled_from_personal_upstream(self) -> None:
        marketplace_repository = (
            "https://github.com/jeremylongshore/tons-of-skills-marketplace/"
            "tree/main/plugins/community/contributing-clanker"
        )
        personal_repository = "https://github.com/jeremylongshore/contributing-clanker"
        manifest = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        package = json.loads((PLUGIN / "package.json").read_text(encoding="utf-8"))
        readme = (PLUGIN / "README.md").read_text(encoding="utf-8")

        self.assertEqual(manifest["repository"], marketplace_repository)
        self.assertNotIn(personal_repository, json.dumps(manifest))
        self.assertNotIn("hooks", package["files"])
        self.assertIn("Do not mirror or bulk-copy a personal", readme)

        for path in PLUGIN.rglob("*"):
            self.assertFalse(path.is_symlink(), f"published plugin must not contain symlink: {path}")

    def test_curated_audit_is_an_exact_read_only_projection(self) -> None:
        source = SKILLS / "contribute"
        source_files = {path.relative_to(source) for path in source.rglob("*") if path.is_file()}
        curated_files = {path.relative_to(CURATED_AUDIT) for path in CURATED_AUDIT.rglob("*") if path.is_file()}
        self.assertEqual(curated_files, source_files)
        for relative in source_files:
            self.assertEqual(
                (CURATED_AUDIT / relative).read_bytes(),
                (source / relative).read_bytes(),
                str(relative),
            )

    def test_no_hidden_format_characters_or_personal_layouts(self) -> None:
        forbidden_codepoints = {0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF}
        forbidden_paths = (
            "~/000-projects/contributing-clanker",
            "$HOME/000-projects/contributing-clanker",
            "~/.contribute-system",
            "$HOME/.contribute-system",
            "~/.claude/",
            "${CLAUDE_SKILL_DIR}",
        )
        foreign_authority_markers = ("@scout", "@researcher", "CLAUDE.md")
        for path in PLUGIN.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            hidden = sorted({f"U+{ord(char):04X}" for char in text if ord(char) in forbidden_codepoints})
            self.assertFalse(hidden, f"{path}: hidden characters {hidden}")
            for forbidden in forbidden_paths:
                self.assertNotIn(forbidden, text, f"{path}: personal path {forbidden}")
            for marker in foreign_authority_markers:
                self.assertNotIn(marker, text, f"{path}: foreign authority marker {marker}")

    def test_versions_match_manifest(self) -> None:
        manifest = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        display_version = manifest["version"]
        # Display versions advance independently of package.json's npm patch.
        self.assertRegex(display_version, r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
        for skill in SKILLS.glob("*/SKILL.md"):
            frontmatter = skill.read_text(encoding="utf-8").split("---", 2)[1]
            versions = re.findall(r"^version: [\"']?([^\"'\s]+)[\"']?[ \t]*$", frontmatter, re.MULTILINE)
            self.assertEqual(versions, [display_version], str(skill))

    def test_setup_requires_explicit_safe_paths(self) -> None:
        setup = SKILLS / "contribute-prepare/scripts/setup.sh"
        missing = subprocess.run(["bash", str(setup)], text=True, capture_output=True, check=False)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("state-dir is required", missing.stderr)

        root = subprocess.run(
            ["bash", str(setup), "--state-dir", "/", "--workspace-dir", "/tmp/contribute-work"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(root.returncode, 0)
        self.assertIn("state-dir cannot be /", root.stderr)

        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "profile-state"
            workspace = Path(tmp) / "worktrees"
            created = subprocess.run(
                [
                    "bash",
                    str(setup),
                    "--state-dir",
                    str(state),
                    "--workspace-dir",
                    str(workspace),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertTrue((state / "candidates").is_dir())
            self.assertTrue((state / "research").is_dir())
            self.assertTrue((state / "user-gates").is_dir())
            self.assertTrue(workspace.is_dir())

    def test_runtime_refuses_implicit_state(self) -> None:
        runner = SKILLS / "contribute-prepare/scripts/gate-runner.sh"
        env = os.environ.copy()
        env.pop("CONTRIBUTE_STATE_DIR", None)
        env.pop("CONTRIBUTE_WORKSPACE_DIR", None)
        result = subprocess.run(
            ["bash", str(runner), "open→shortlist", "/does/not/exist"],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CONTRIBUTE_STATE_DIR must be explicitly set", result.stderr)

    def test_prepare_forbids_github_mutation_and_publish_requires_approval(self) -> None:
        prepare = (SKILLS / "contribute-prepare/SKILL.md").read_text(encoding="utf-8")
        publish = (SKILLS / "contribute-publish/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Never call GitHub mutation", prepare)
        self.assertIn("No external action has been taken", prepare)
        self.assertIn("fresh human approval", " ".join(publish.split()))
        self.assertIn("Earlier blanket permission", publish)

    def test_prepare_does_not_fetch_repository_supplied_urls(self) -> None:
        researcher = SKILLS / "contribute-prepare/scripts/researcher-build.sh"
        text = researcher.read_text(encoding="utf-8")
        self.assertNotIn("/usr/bin/curl", text)
        self.assertNotIn("wget", text)
        self.assertIn("were not retrieved", text)
        self.assertIn('status: "not-fetched"', text)

        env = os.environ.copy()
        env["CONTRIBUTE_STATE_DIR"] = "/tmp/contribute-portability-test"
        invalid = subprocess.run(
            ["bash", str(researcher), "owner/repo/extra", "--stdout"],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(invalid.returncode, 64)
        self.assertIn("usage:", invalid.stderr)


class HermeticContributingShellTests(unittest.TestCase):
    """Exercise audited mocked-gh callsites, not OS-wide network containment."""

    SUITES = (
        "test-known-traps.sh",
        "test-override-audit.sh",
        "test-plug-in.sh",
        "test-scout-refresh.sh",
        "test-stale-dossier-refresh.sh",
    )
    SCRIPTS = SKILLS / "contribute-prepare/scripts"

    def setUp(self) -> None:
        if not all(hasattr(os, name) for name in ("waitid", "WNOWAIT", "killpg")):
            self.fail("Linux/POSIX waitid(WNOWAIT) is required for owned subprocess cleanup")
        self.temp = tempfile.TemporaryDirectory(prefix="contribute shell fixtures ")
        self.root = Path(self.temp.name).resolve()
        self.marker = self.root / "owned-fixture"
        self.marker.write_text("contribute shell fixtures\n")
        self.addCleanup(self.cleanup_root)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.audit = self.root / "audit.jsonl"  # Outside nested script TMPDIR cleanup.
        self.audit.write_text("")
        for directory in ("tmp", "cwd", "config", "state", "workspace"):
            (self.root / directory).mkdir()
        self.env = {
            "PATH": f"{self.bin}:/usr/bin:/bin",
            "USER": "fixture",
            "LOGNAME": "fixture",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "TZ": "UTC",
            "TERM": "dumb",
            "PYTHONNOUSERSITE": "1",
            "TMPDIR": str(self.root / "tmp"),
            "GH_CONFIG_DIR": str(self.root / "config"),
            "XDG_CONFIG_HOME": str(self.root / "config"),
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "CONTRIBUTE_STATE_DIR": str(self.root / "state"),
            "CONTRIBUTE_WORKSPACE_DIR": str(self.root / "workspace"),
            "FIXTURE_GH_AUDIT": str(self.audit),
            "FIXTURE_GH_MODE": "normal",
        }
        if "HOME" in os.environ:
            self.env["HOME"] = os.environ["HOME"]  # Preserve value; never repurpose HOME.
        self.deadline = time.monotonic() + 300
        # transition.sh hardcodes this interpreter; toolcache Python is not sufficient.
        code, _, err = self.run_child(["/usr/bin/python3", "-c", "import yaml"])
        self.assertEqual(code, 0, "system Python requires PyYAML: " + err)
        for executable in ("bash", "jq", "date", "timeout", "git"):
            self.assertIsNotNone(shutil.which(executable, path="/usr/bin:/bin"), executable)
        self.install_gh_stub()

    def owned(self, path: Path) -> Path:
        resolved = path.resolve()
        if not resolved.is_relative_to(self.root) or not self.marker.is_file():
            raise ValueError("path is not inside the owned fixture root")
        return resolved

    def cleanup_root(self) -> None:
        if self.root.resolve() != self.root or not self.marker.is_file():
            raise RuntimeError("fixture ownership changed; refusing cleanup")
        self.temp.cleanup()  # rmtree removes contained symlinks, never their targets.

    def run_child(self, args, *, timeout=30, env=None):
        if not 0 < timeout <= 60:
            raise ValueError("fixture timeout must be positive and at most 60s")
        stop = min(time.monotonic() + timeout, self.deadline)
        if stop <= time.monotonic():
            raise TimeoutError("fixture suite exceeded its 300-second budget")
        process = subprocess.Popen(
            args,
            cwd=self.owned(self.root / "cwd"),
            env=env or self.env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        output = [bytearray(), bytearray()]
        try:
            with selectors.DefaultSelector() as poll:
                for index, stream in enumerate((process.stdout, process.stderr)):
                    os.set_blocking(stream.fileno(), False)
                    poll.register(stream, selectors.EVENT_READ, index)
                while poll.get_map():
                    if time.monotonic() >= stop:
                        raise TimeoutError("owned fixture command timed out")
                    for key, _ in poll.select(0.05):
                        chunk = os.read(key.fileobj.fileno(), 65536)
                        if not chunk:
                            poll.unregister(key.fileobj)
                        else:
                            output[key.data].extend(chunk)
                            if sum(map(len, output)) > 1024 * 1024:
                                raise RuntimeError("owned fixture output exceeded 1MiB")
                while os.waitid(os.P_PID, process.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT) is None:
                    if time.monotonic() >= stop:
                        raise TimeoutError("owned fixture command timed out")
                    time.sleep(0.01)
        finally:
            # The unreaped leader pins this owned PID/PGID until group cleanup.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
            if process.stdin:
                process.stdin.close()
        return process.returncode, *(bytes(value).decode(errors="replace") for value in output)

    def install_gh_stub(self):
        # Literal policy inventory, not a permissive /contents/* endpoint wildcard.
        builder = (self.SCRIPTS / "researcher-build.sh").read_text()
        policy_paths = [
            ".github/CODEOWNERS",
            ".github/CODE_OF_CONDUCT.md",
            ".github/CONTRIBUTING.md",
            ".github/ISSUE_TEMPLATE.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/SECURITY.md",
            ".github/issue_template.md",
            ".github/pull_request_template.md",
            "AI_POLICY.md",
            "CLA.md",
            "CLA.txt",
            "CODEOWNERS",
            "CODE_OF_CONDUCT.md",
            "CONTRIBUTING.md",
            "DCO.md",
            "DCO.txt",
            "DEVELOPMENT.md",
            "GOVERNANCE.md",
            "ISSUE_TEMPLATE.md",
            "PULL_REQUEST_TEMPLATE.md",
            "SECURITY.md",
            "SETUP.md",
            "docs/AI_POLICY.md",
            "docs/CLA.md",
            "docs/CODE_OF_CONDUCT.md",
            "docs/CONTRIBUTING.md",
            "docs/DCO.md",
            "docs/DEVELOPMENT.md",
            "docs/GOVERNANCE.md",
            "docs/PULL_REQUEST_TEMPLATE.md",
            "docs/SECURITY.md",
            "docs/SETUP.md",
        ]
        self.assertEqual(
            sorted(set(re.findall(r'"([^"\n]+):[A-Z_]+"', builder))),
            policy_paths,
            "builder policy inventory changed; review the frozen fixture endpoints",
        )
        stub = r"""#!/usr/bin/python3
import base64, datetime, json, os, pathlib, sys
args = sys.argv[1:]
audit = pathlib.Path(os.environ["FIXTURE_GH_AUDIT"])
mode = os.environ["FIXTURE_GH_MODE"]
allowed = {("PostHog/posthog", "55412"), ("Tracer-Cloud/opensre", "1129"),
           ("lingdojo/kana-dojo", "15441"), ("lingdojo/kana-dojo", "99999999"),
           ("example-org/example-repo", "1")}
paths = POLICY_PATHS
out, code, kind = "", 0, "expected"
def flag(name):
    if name in args:
        i=args.index(name)
        return args[i+1] if i+1<len(args) else None
    return next((x.split("=",1)[1] for x in args if x.startswith(name+"=")), None)
def unknown():
    global code,kind
    code,kind=97,"unexpected"
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
if args == ["auth", "status"]:
    pass
elif args[:1] == ["api"] and len(args)>=2:
    endpoint=args[1]
    if endpoint == "repos/lingdojo/kana-dojo" and args == ["api",endpoint]:
        out=json.dumps({"default_branch":"main","stargazers_count":1,"language":"TypeScript",
                        "description":"Synthetic fixture","license":{"spdx_id":"MIT"}})
    elif endpoint == "repos/lingdojo/kana-dojo/contents/.github/ISSUE_TEMPLATE" and args == ["api",endpoint]:
        out=json.dumps([{"type":"file","name":"bug.yml"}])
    elif endpoint.startswith("repos/lingdojo/kana-dojo/contents/"):
        path=endpoint.split("/contents/",1)[1]
        if path not in paths:
            unknown()
        elif path == "CONTRIBUTING.md" and args == ["api",endpoint]:
            out="{}"
        elif path == "CONTRIBUTING.md" and args == ["api",endpoint,"--jq",".content"]:
            out=base64.b64encode(b"## Testing\nRun tests.\n").decode()
        elif args == ["api",endpoint]:
            code,kind=1,"optional-missing"
        else:
            unknown()
    elif endpoint == "repos/lingdojo/kana-dojo/pulls?state=closed&sort=updated&direction=desc&per_page=100" and args == ["api",endpoint]:
        out="[]"
    else:
        unknown()
elif args[:2] == ["issue","view"] and len(args)==9:
    issue=args[2]; repo=flag("--repo"); fields=flag("--json"); query=flag("--jq")
    queries={
      "assignees": '[.assignees[].login] | join(",")',
      "body,comments": '.body + " " + (.comments | map(.body) | join(" "))',
      "createdAt,updatedAt,comments": '{createdAt, updatedAt, last_comment_at: (.comments | sort_by(.createdAt) | .[-1].createdAt // null)}',
      "state,stateReason,closedAt": '{state, stateReason: (.stateReason // ""), closedAt: (.closedAt // "")}',
    }
    if (repo,issue) not in allowed or fields not in queries or query!=queries[fields] or args[3:4]!=["--repo"] or args[5:6]!=["--json"] or args[7:8]!=["--jq"]:
        unknown()
    elif fields=="assignees":
        out="synthetic-assignee" if (repo,issue)==("Tracer-Cloud/opensre","1129") or mode=="assigned" else ""
    elif fields=="body,comments":
        out="Synthetic neutral issue body"
    elif fields=="createdAt,updatedAt,comments":
        out=json.dumps({"createdAt":now,"updatedAt":now,"last_comment_at":None})
    else:
        closed=(repo,issue)==("lingdojo/kana-dojo","15441") or mode=="closed"
        out=json.dumps({"state":"CLOSED" if closed else "OPEN","stateReason":"NOT_PLANNED" if closed else "","closedAt":now if closed else ""})
elif args[:2] == ["search","prs"] and len(args)==11:
    repo=flag("--repo"); search=args[3]; issue=search.split(" #")[-1]
    if (repo,issue) not in allowed or search not in [k+" #"+issue for k in ("closes","fixes","resolves")] or args[4:]!=["--merged","--limit","1","--json","url","--jq",".[0].url // empty"]:
        unknown()
    elif ((repo,issue)==("PostHog/posthog","55412") or mode=="shipped") and search.startswith("closes #"):
        out="https://github.com/PostHog/posthog/pull/57145"
else:
    unknown()
if mode=="force-unknown": unknown()
record=json.dumps({"args":args,"kind":kind},separators=(",",":"))
if len(record)>4096 or not audit.is_file() or audit.stat().st_size+len(record)+1>262144:
    audit.write_text("AUDIT_OVERFLOW_OR_MISSING\n")
    sys.exit(98)
with audit.open("a") as f: f.write(record+"\n")
if out: print(out)
sys.exit(code)
""".replace("POLICY_PATHS", repr(policy_paths))
        gh = self.bin / "gh"
        gh.write_text(stub)
        gh.chmod(0o700)

    def audit_rows(self):
        if not self.audit.is_file() or self.audit.stat().st_size > 262144:
            raise AssertionError("missing or overflowed gh audit")
        try:
            rows = [json.loads(line) for line in self.audit.read_text().splitlines()]
        except (ValueError, UnicodeError) as exc:
            raise AssertionError("malformed gh audit") from exc
        if len(rows) > 512 or any(
            not isinstance(row, dict)
            or set(row) != {"args", "kind"}
            or not isinstance(row["args"], list)
            or any(not isinstance(arg, str) for arg in row["args"])
            or row["kind"] not in ("expected", "optional-missing")
            for row in rows
        ):
            raise AssertionError("unexpected gh request or malformed audit row")
        return rows

    def test_five_bundled_suites_with_audited_gh_fixtures(self):
        for suite in self.SUITES:
            with self.subTest(suite=suite):
                self.audit.write_text("")
                code, out, err = self.run_child(["/bin/bash", str(self.SCRIPTS / suite)])
                rows = self.audit_rows()  # Fail swallowed unknown calls even with exit0.
                self.assertEqual(code, 0, out + err)
                requests = [row["args"] for row in rows]
                assignees = [a for a in requests if "assignees" in a]
                if suite == "test-plug-in.sh":
                    self.assertGreaterEqual(
                        len(assignees), 2
                    )  # Two calls in the bundled add/remove suite; not phase-labelled.
                elif suite == "test-known-traps.sh":
                    self.assertTrue(any("closes #55412" in a for a in requests))
                    self.assertTrue(any("1129" in a and "assignees" in a for a in requests))
                    self.assertTrue(any("15441" in a and "state,stateReason,closedAt" in a for a in requests))
                elif suite == "test-override-audit.sh":
                    self.assertGreaterEqual(sum("state,stateReason,closedAt" in a for a in requests), 2)
                elif suite == "test-stale-dossier-refresh.sh":
                    self.assertIn(["auth", "status"], requests)
                    self.assertIn(["api", "repos/lingdojo/kana-dojo"], requests)
                    self.assertTrue(any(row["kind"] == "optional-missing" for row in rows))
                else:
                    self.assertEqual(requests, [])  # This suite is an awk simulation.

    def candidate(self):
        target = self.root / "candidate.md"
        body = "\n# Synthetic issue\n\nManual body bytes.  \n"
        target.write_text("---\nrepo: example-org/example-repo\nissue_number: 1\nstatus: open\n---\n" + body)
        return target, body

    def direct_gate(self, filename, mode):
        target, _ = self.candidate()
        payload = json.dumps(
            {
                "candidate": str(target),
                "dossier": "",
                "action": "shortlist→claimed",
                "env": {"repo": "example-org/example-repo", "branch": ""},
            }
        )
        input_file = self.root / "input.json"
        input_file.write_text(payload)
        env = dict(self.env, FIXTURE_GH_MODE=mode)
        code, out, err = self.run_child(
            ["/bin/bash", "-c", 'exec "$1" < "$2"', "fixture", str(self.SCRIPTS / "gates" / filename), str(input_file)],
            env=env,
        )
        self.assertEqual(code, 0, err)
        return json.loads(out)

    def test_real_gate_positive_negative_pairs(self):
        for gate, blocked_mode in (
            ("a01-already-assigned.sh", "assigned"),
            ("a02-already-shipped.sh", "shipped"),
            ("a05-issue-still-open.sh", "closed"),
        ):
            with self.subTest(gate=gate):
                for mode, severity in (("normal", "PASS"), (blocked_mode, "BLOCK")):
                    self.audit.write_text("")
                    self.assertEqual(self.direct_gate(gate, mode)["severity"], severity)
                    requests = [row["args"] for row in self.audit_rows()]
                    if gate == "a02-already-shipped.sh":
                        keywords = ("closes", "fixes", "resolves") if mode == "normal" else ("closes",)
                        expected = [
                            [
                                "search",
                                "prs",
                                "--repo=example-org/example-repo",
                                keyword + " #1",
                                "--merged",
                                "--limit",
                                "1",
                                "--json",
                                "url",
                                "--jq",
                                ".[0].url // empty",
                            ]
                            for keyword in keywords
                        ]
                    else:
                        fields, query = (
                            ("assignees", '[.assignees[].login] | join(",")')
                            if gate == "a01-already-assigned.sh"
                            else (
                                "state,stateReason,closedAt",
                                '{state, stateReason: (.stateReason // ""), closedAt: (.closedAt // "")}',
                            )
                        )
                        expected = [
                            [
                                "issue",
                                "view",
                                "1",
                                "--repo",
                                "example-org/example-repo",
                                "--json",
                                fields,
                                "--jq",
                                query,
                            ]
                        ]
                    self.assertEqual(requests, expected, (gate, mode))

    def test_real_transition_preserves_candidate_and_prior_log(self):
        target, body = self.candidate()
        state = self.root / "state"
        (state / "user-gates").mkdir()
        log = state / "log.jsonl"
        prefix = b'{"event":"synthetic_prior","details":{"repo":"example-org/example-repo"}}\n'
        log.write_bytes(prefix)
        before = target.read_bytes()
        command = [
            "/bin/bash",
            str(self.SCRIPTS / "transition.sh"),
            "shortlist→claimed",
            str(target),
            "--override-gate",
            "A05",
            "synthetic controlled override",
        ]
        env = dict(self.env, FIXTURE_GH_MODE="closed")
        code, _, err = self.run_child(command + ["--dry-run"], env=env)
        # Dry-run does not persist the override; the closed issue must still block.
        self.assertEqual(code, 1, err)
        self.assertIn("[transition] BLOCKED", err)
        self.assertEqual(target.read_bytes(), before)
        self.assertTrue(log.read_bytes().startswith(prefix))
        # Gate-run records from dry-run are allowed; prior bytes must stay exact.
        before_real = log.read_bytes()
        code, out, err = self.run_child(command, env=env)
        self.assertEqual(code, 0, err)
        self.assertIn("1 BLOCK (0 after overrides)", out + err)
        after = target.read_bytes()
        self.assertEqual(after.split(b"---", 2)[2], before.split(b"---", 2)[2])
        self.assertTrue(log.read_bytes().startswith(before_real))
        appended = [json.loads(line) for line in log.read_bytes()[len(before_real) :].splitlines()]
        override = [row for row in appended if row.get("event") == "gate_override"]
        self.assertEqual(len(override), 1)
        self.assertEqual(override[0]["details"].get("gate"), "A05")
        self.assertEqual(override[0]["details"].get("reason"), "synthetic controlled override")
        self.assertTrue(self.audit_rows())

    def test_unknown_calls_and_invalid_audits_cannot_be_green(self):
        # An actual gate swallows the stub's failure and can still PASS; outer audit refuses.
        self.direct_gate("a01-already-assigned.sh", "force-unknown")
        with self.assertRaises(AssertionError):
            self.audit_rows()
        for value in ("not json\n", "x" * 262145):
            self.audit.write_text(value)
            with self.assertRaises(AssertionError):
                self.audit_rows()
        self.audit.unlink()
        with self.assertRaises(AssertionError):
            self.audit_rows()

    def test_cleanup_does_not_follow_sibling_symlink(self):
        disposable = self.root / "cleanup-owned"
        disposable.mkdir()
        sentinel = self.root / "sibling-sentinel"
        sentinel.write_bytes(b"preserve synthetic sibling")
        (disposable / "link").symlink_to(sentinel)
        shutil.rmtree(self.owned(disposable))
        self.assertEqual(sentinel.read_bytes(), b"preserve synthetic sibling")

    def test_owned_process_timeout_and_output_cleanup(self):
        for mode in ("timeout", "output"):
            with self.subTest(mode=mode):
                marker = self.root / (mode + "-child.json")
                child = (
                    "import os,json,pathlib,time; "
                    "fields=pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split(); "
                    f"pathlib.Path({str(marker)!r}).write_text(json.dumps({{'pid':os.getpid(),'start':fields[19]}})); "
                    "time.sleep(60)"
                )
                helper = self.root / (mode + "-helper.py")
                helper.write_text(
                    "import subprocess,sys,time,pathlib\n"
                    + f"subprocess.Popen([sys.executable,'-c',{child!r}])\n"
                    + f"while not pathlib.Path({str(marker)!r}).exists(): time.sleep(0.01)\n"
                    + ("print('x'*1100000,flush=True)\n" if mode == "output" else "")
                    + "time.sleep(60)\n"
                )
                with self.assertRaises(TimeoutError if mode == "timeout" else RuntimeError):
                    self.run_child(["/usr/bin/python3", str(helper)], timeout=2)
                self.assertTrue(marker.is_file(), "descendant must actually start")
                identity = json.loads(marker.read_text())
                stat = Path(f"/proc/{identity['pid']}/stat")
                stop = time.monotonic() + 3
                while stat.exists():
                    try:
                        fields = stat.read_text().rsplit(")", 1)[1].split()
                    except FileNotFoundError:
                        break
                    if fields[19] != identity["start"] or fields[0] in ("Z", "X"):
                        break  # Nonlive orphan zombie is not claimed to be reaped here.
                    if time.monotonic() >= stop:
                        self.fail("owned helper descendant remains live")
                    time.sleep(0.01)


if __name__ == "__main__":
    unittest.main()
