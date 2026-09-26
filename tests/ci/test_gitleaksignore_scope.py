"""Pin the scope of .gitleaksignore.

Every suppression must be an exact, commit-bound Gitleaks fingerprint
(<40-hex commit>:<path>:<rule>:<line>), so no path, rule or value blanket
can slip in. The historical administrator-credential finding is a real
incident: it must stay visible to full-history scans until it is rotated
and adjudicated, so its commit may never appear in the ignore file.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IGNORE = ROOT / ".gitleaksignore"
FINGERPRINT = re.compile(r"^[0-9a-f]{40}:[^:*?\s]+:[a-z0-9-]+:[0-9]+$")
# Real credential incident (claude-vggd.1.2); must never be suppressed.
INCIDENT_COMMIT = "6efe20ade03978bc6dbde430738f294841b630cf"


def entries():
    for raw in IGNORE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            yield line


class GitleaksIgnoreScope(unittest.TestCase):
    def test_every_entry_is_an_exact_commit_bound_fingerprint(self):
        bad = [line for line in entries() if not FINGERPRINT.match(line)]
        self.assertEqual(bad, [], f"non-fingerprint suppressions: {bad}")

    def test_entries_are_unique(self):
        lines = list(entries())
        self.assertEqual(len(lines), len(set(lines)), "duplicate suppressions")

    def test_real_credential_incident_is_never_suppressed(self):
        text = IGNORE.read_text(encoding="utf-8")
        self.assertNotIn(INCIDENT_COMMIT[:10], text)

    def test_every_entry_has_a_reason_comment_above_its_block(self):
        lines = IGNORE.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith("#"):
                block_start = i
                while block_start > 0 and lines[block_start - 1].strip() and not lines[block_start - 1].startswith("#"):
                    block_start -= 1
                header = lines[max(0, block_start - 3) : block_start]
                self.assertTrue(
                    any(h.startswith("# reason:") for h in header),
                    f"entry on line {i + 1} has no '# reason:' header",
                )


if __name__ == "__main__":
    unittest.main()
