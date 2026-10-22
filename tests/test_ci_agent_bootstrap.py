"""Exercise the actual advisory agent step without installing or running Python tools."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/validate-plugins.yml"


class AgentBootstrapTests(unittest.TestCase):
    def run_step(self, *, import_status=0, install_status=0, validator_status=0):
        workflow = yaml.safe_load(WORKFLOW.read_text())
        step = next(
            item
            for item in workflow["jobs"]["validate"]["steps"]
            if item.get("name") == "Validate agent frontmatter (report-only)"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            calls = root / "calls"
            python = root / "python3"
            python.write_text(
                '#!/usr/bin/env bash\nprintf "%s\\n" "$*" >> "$BOOTSTRAP_CALLS"\n'
                'if [ "$#" -eq 2 ] && [ "$1" = -c ] && [ "$2" = "import yaml" ]; then\n'
                '  exit "$BOOTSTRAP_IMPORT_STATUS"\n'
                'elif [ "$*" = "-m pip install --quiet pyyaml" ]; then\n'
                '  exit "$BOOTSTRAP_INSTALL_STATUS"\n'
                'elif [ "$*" = "scripts/validate-skills-schema.py --agents-only" ]; then\n'
                '  exit "$BOOTSTRAP_VALIDATOR_STATUS"\n'
                "fi\nexit 99\n"
            )
            python.chmod(0o755)
            result = subprocess.run(
                ["bash", "-e", "-c", step["run"]],
                cwd=root,
                env={
                    **os.environ,
                    "PATH": f"{root}{os.pathsep}{os.environ['PATH']}",
                    "BOOTSTRAP_CALLS": str(calls),
                    "BOOTSTRAP_IMPORT_STATUS": str(import_status),
                    "BOOTSTRAP_INSTALL_STATUS": str(install_status),
                    "BOOTSTRAP_VALIDATOR_STATUS": str(validator_status),
                },
                text=True,
                capture_output=True,
                timeout=10,
            )
            return result, calls.read_text().splitlines()

    def test_available_dependency_skips_install(self):
        result, calls = self.run_step(install_status=4)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, ["-c import yaml", "scripts/validate-skills-schema.py --agents-only"])

    def test_missing_dependency_installs_before_validator(self):
        result, calls = self.run_step(import_status=1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            calls,
            ["-c import yaml", "-m pip install --quiet pyyaml", "scripts/validate-skills-schema.py --agents-only"],
        )

    def test_failed_install_stops_before_validator(self):
        result, calls = self.run_step(import_status=1, install_status=4)
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        self.assertEqual(calls, ["-c import yaml", "-m pip install --quiet pyyaml"])

    def test_existing_validator_errors_remain_advisory(self):
        result, calls = self.run_step(validator_status=9)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[-1], "scripts/validate-skills-schema.py --agents-only")

    def test_validator_errors_after_install_remain_advisory(self):
        result, calls = self.run_step(import_status=1, validator_status=9)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls[-1], "scripts/validate-skills-schema.py --agents-only")


if __name__ == "__main__":
    unittest.main()
