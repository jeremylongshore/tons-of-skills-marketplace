"""Exercise the real Git hook with isolated commands and temporary commits."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


HOOK = Path(__file__).resolve().parents[1] / ".husky" / "pre-commit"
GIT = shutil.which("git")


class PreCommitHookTests(unittest.TestCase):
    def attempt_commit(self, *, lint=0, audit=0, credential=0):
        with tempfile.TemporaryDirectory(prefix="pre-commit-hook-") as directory:
            root = Path(directory)
            commands = root / "commands"
            commands.mkdir()
            log = root / "commands.log"
            scripts = {
                "git": "#!/bin/sh\nexit 0\n",
                "pnpm": (
                    '#!/bin/sh\nprintf "pnpm:%s\\n" "$*" >> "$HOOK_TEST_LOG"\n'
                    'case "$*" in\n'
                    '  "exec lint-staged") exit "$HOOK_TEST_LINT_EXIT" ;;\n'
                    '  "exec audit-harness verify") exit "$HOOK_TEST_AUDIT_EXIT" ;;\n'
                    "  *) exit 99 ;;\nesac\n"
                ),
                "node": (
                    '#!/bin/sh\nprintf "node:%s\\n" "$*" >> "$HOOK_TEST_LOG"\nexit "$HOOK_TEST_CREDENTIAL_EXIT"\n'
                ),
            }
            for name, script in scripts.items():
                path = commands / name
                path.write_text(script)
                path.chmod(0o755)
            env = {
                **{key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
                "PATH": f"{commands}{os.pathsep}{os.environ['PATH']}",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "HOOK_TEST_LOG": str(log),
                "HOOK_TEST_LINT_EXIT": str(lint),
                "HOOK_TEST_AUDIT_EXIT": str(audit),
                "HOOK_TEST_CREDENTIAL_EXIT": str(credential),
            }

            def git(*args, check=True):
                return subprocess.run([GIT, *args], cwd=root, env=env, check=check, capture_output=True, text=True)

            git("init", "--quiet")
            installed_hook = root / ".git" / "hooks" / "pre-commit"
            installed_hook.write_bytes(HOOK.read_bytes())
            installed_hook.chmod(0o755)
            (root / "candidate.txt").write_text("isolated hook fixture\n")
            git("add", "candidate.txt")
            result = git(
                "-c",
                "core.hooksPath=.git/hooks",
                "-c",
                "commit.gpgSign=false",
                "-c",
                "user.name=Hook Test",
                "-c",
                "user.email=hook-test@example.invalid",
                "commit",
                "--quiet",
                "-m",
                "test: exercise pre-commit hook",
                check=False,
            )
            has_commit = git("rev-parse", "--verify", "HEAD", check=False).returncode == 0
            return result, has_commit, log.read_text().splitlines()

    def test_lint_failure_refuses_commit_before_later_checks(self):
        result, committed, calls = self.attempt_commit(lint=7)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(committed)
        self.assertEqual(calls, ["pnpm:exec lint-staged"])

    def test_audit_failure_refuses_commit_before_credential_check(self):
        result, committed, calls = self.attempt_commit(audit=8)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(committed)
        self.assertEqual(calls, ["pnpm:exec lint-staged", "pnpm:exec audit-harness verify"])

    def test_success_runs_all_checks_and_creates_commit(self):
        result, committed, calls = self.attempt_commit()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(committed)
        self.assertEqual(
            calls,
            [
                "pnpm:exec lint-staged",
                "pnpm:exec audit-harness verify",
                "node:scripts/check-mcp-plaintext-creds.mjs --all-local",
            ],
        )

    def test_credential_failure_still_refuses_commit(self):
        result, committed, calls = self.attempt_commit(credential=9)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(committed)
        self.assertEqual(len(calls), 3)


if __name__ == "__main__":
    unittest.main()
