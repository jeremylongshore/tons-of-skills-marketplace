"""The no-Docker scanner keeps the PR range, result classes and fail-closed flags."""

from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ci/scan-reviewed-pr-secrets.sh"


class ReviewedSecretScanTests(unittest.TestCase):
    def test_scanner_contract_and_checksum_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binaries = root / "bin"
            binaries.mkdir()
            mocks = {
                "curl": '#!/bin/bash\nprintf download >> "$PROBE_LOG"\n',
                "sha256sum": '#!/bin/bash\ncat >/dev/null\nexit "${CHECKSUM_STATUS:-0}"\n',
                "tar": """#!/bin/bash
while [[ $# -gt 0 ]]; do
 if [[ $1 == -C ]]; then shift; dest=$1; fi
 shift
done
cat > "$dest/trufflehog" <<'TOOL'
#!/bin/bash
printf '%s\\n' "$@" > "$ARGS_LOG"
exit "${SCANNER_STATUS:-0}"
TOOL
chmod +x "$dest/trufflehog"
""",
            }
            for name, content in mocks.items():
                path = binaries / name
                path.write_text(content)
                path.chmod(0o755)
            args_file = root / "args"
            env = {
                "PATH": str(binaries) + ":/usr/bin:/bin",
                "RUNNER_TEMP": directory,
                "PR_BASE_SHA": "a" * 40,
                "PR_HEAD_SHA": "b" * 40,
                "PROBE_LOG": str(root / "probe"),
                "ARGS_LOG": str(args_file),
            }
            result = subprocess.run(["bash", str(SCRIPT)], env=env, cwd=root, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                args_file.read_text().splitlines(),
                [
                    "git",
                    f"file://{root}/",
                    "--since-commit",
                    "a" * 40,
                    "--branch",
                    "b" * 40,
                    "--fail",
                    "--no-update",
                    "--github-actions",
                    "--results=verified,unknown",
                ],
            )
            args_file.unlink()
            result = subprocess.run(["bash", str(SCRIPT)], env={**env, "CHECKSUM_STATUS": "1"}, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(args_file.exists(), "Failed checksum must never execute downloaded code")
            result = subprocess.run(["bash", str(SCRIPT)], env={**env, "SCANNER_STATUS": "183"}, capture_output=True)
            self.assertEqual(result.returncode, 183, "Findings must remain blocking")
            (root / "probe").unlink()
            result = subprocess.run(["bash", str(SCRIPT)], env={**env, "PR_HEAD_SHA": "malformed"}, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "probe").exists(), "Invalid range must fail before downloading")


if __name__ == "__main__":
    unittest.main()
