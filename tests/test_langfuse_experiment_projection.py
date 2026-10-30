"""Run the provider-free Node adapter suite in the repository's Python CI lane."""

import os
import subprocess
import sys
import unittest
from pathlib import Path


class ExperimentProjectionTests(unittest.TestCase):
    def test_sdk_result_projection_and_actual_comparator_boundary(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["node", "--test", "tests/fixtures/langfuse/experiment-projection.test.mjs"],
            cwd=root,
            env={**os.environ, "LANGFUSE_GUARDIAN_TEST_PYTHON": sys.executable},
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
