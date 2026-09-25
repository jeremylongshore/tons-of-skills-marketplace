"""Tests must not pin a plugin's exact recorded verification score.

The verify job fails CI when a plugin's recorded score, grade, or badge drifts
from the validator, and the auto-bump workflow refreshes those values on plugin
pull requests. An exact score pinned in a test would then go red whenever the
validator or the pack legitimately moves the score by a point, including on
the bot's own refresh commit. Assert the grade floor instead:

    self.assertGreaterEqual(entry["verification"]["score"], 90)
    self.assertEqual("A", entry["verification"]["grade"])
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXACT_SCORE_PIN = re.compile(
    r"assertEqual\(\s*\d+\s*,\s*[^)]*\[\s*[\"']verification[\"']\s*\]\s*\[\s*[\"']score[\"']\s*\]"
    r"|assertEqual\(\s*[^)]*\[\s*[\"']verification[\"']\s*\]\s*\[\s*[\"']score[\"']\s*\]\s*,\s*\d+\s*\)"
)


class NoExactVerificationScorePinsTest(unittest.TestCase):
    def test_no_test_pins_an_exact_verification_score(self) -> None:
        offenders = []
        for path in sorted((ROOT / "tests").rglob("test_*.py")):
            if path.name == Path(__file__).name:
                continue
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                if EXACT_SCORE_PIN.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
        self.assertEqual([], offenders, "\n".join(offenders))

    def test_the_pattern_catches_both_argument_orders(self) -> None:
        self.assertIsNotNone(EXACT_SCORE_PIN.search('self.assertEqual(98, entry["verification"]["score"])'))
        self.assertIsNotNone(EXACT_SCORE_PIN.search('self.assertEqual(entry["verification"]["score"], 98)'))
        self.assertIsNone(
            EXACT_SCORE_PIN.search('self.assertGreaterEqual(entry["verification"]["score"], 90)')
        )


if __name__ == "__main__":
    unittest.main()
