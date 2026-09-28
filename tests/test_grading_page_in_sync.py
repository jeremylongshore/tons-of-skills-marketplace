"""Drift detection between the public /grading page and the rubric source.

The grading page at marketplace/src/pages/grading.astro is the public-facing
translation of the 100-point rubric inside scripts/validate-skills-schema.py.
If the validator's category maxes / grade bands change without the Astro page
being updated, this test fails — and vice versa. CI gate.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate-skills-schema.py"
GRADING_PAGE = REPO_ROOT / "marketplace" / "src" / "pages" / "grading.astro"

EXPECTED_CATEGORY_MAXES = {
    "Progressive Disclosure Architecture": 30,
    "Ease of Use": 25,
    "Utility": 20,
    "Spec Compliance": 15,
    "Writing Style": 10,
}

EXPECTED_GRADE_BANDS = [
    ("A", 90, 100),
    ("B", 80, 89),
    ("C", 70, 79),
    ("D", 60, 69),
    ("F", 0, 59),
]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def test_validator_exists() -> None:
    assert VALIDATOR.exists(), f"validator not found at {VALIDATOR}"


def test_grading_page_exists() -> None:
    assert GRADING_PAGE.exists(), f"grading page not found at {GRADING_PAGE}"


def test_category_maxes_total_100() -> None:
    """Sum of category maxes must equal 100. Hardcoded contract."""
    assert sum(EXPECTED_CATEGORY_MAXES.values()) == 100


def test_validator_category_maxes_match_expected() -> None:
    """Each score_* function must return its expected max.

    Pulls every `return {"score": total, "max": N, ...}` literal from the
    validator and asserts the canonical category names map to the
    expected maxes.
    """
    text = _read(VALIDATOR)

    # Map function name → declared max from the source
    pattern = re.compile(
        # One lazy [\s\S]*? instead of the nested (?:.*?\n)*?, which could
        # backtrack exponentially; with DOTALL both match the same text.
        r"def\s+(score_[a-z_]+)\s*\([^)]*\)[^{]*?:\s*\n[\s\S]*?\s*return\s*\{[^}]*\"max\"\s*:\s*(\d+)",
        re.DOTALL,
    )
    func_to_max = {m.group(1): int(m.group(2)) for m in pattern.finditer(text)}

    expected = {
        "score_progressive_disclosure": 30,
        "score_ease_of_use": 25,
        "score_utility": 20,
        "score_spec_compliance": 15,
        "score_writing_style": 10,
    }

    for func, exp_max in expected.items():
        assert func in func_to_max, f"validator missing {func}"
        assert func_to_max[func] == exp_max, (
            f"{func} max drifted: validator says {func_to_max[func]}, "
            f"grading page expects {exp_max}"
        )


def test_grading_page_lists_every_category_with_correct_max() -> None:
    """Each EXPECTED_CATEGORY_MAXES entry appears in the Astro page with its max."""
    text = _read(GRADING_PAGE)
    for name, expected_max in EXPECTED_CATEGORY_MAXES.items():
        assert name in text, f"grading page missing category name: {name!r}"
        block_pattern = re.compile(
            re.escape(name) + r".*?max\s*:\s*(\d+)",
            re.DOTALL,
        )
        m = block_pattern.search(text)
        assert m is not None, f"could not locate max for {name!r} in grading.astro"
        page_max = int(m.group(1))
        assert page_max == expected_max, (
            f"category {name!r} max drift: grading page says {page_max}, "
            f"expected {expected_max}"
        )


def test_validator_grade_bands_match_expected() -> None:
    """calculate_grade() thresholds must match EXPECTED_GRADE_BANDS."""
    text = _read(VALIDATOR)
    # Locate the function block by string search rather than a brittle
    # multi-line regex — Python source formatting is stable enough here.
    start = text.find("def calculate_grade(")
    assert start != -1, "calculate_grade() not found in validator"
    # End of function = next top-level def/class after start
    rest = text[start:]
    end_match = re.search(r"\n(?:def|class) ", rest[1:])
    body = rest[: end_match.start() + 1] if end_match else rest

    found: dict[str, int] = {}
    for sm in re.finditer(r">=\s*(\d+):\s*\n\s+return\s+\"([A-F])\"", body):
        found[sm.group(2)] = int(sm.group(1))
    else_m = re.search(r"else:\s*\n\s+return\s+\"([A-F])\"", body)
    assert else_m is not None, "calculate_grade has no else branch"
    found[else_m.group(1)] = 0

    expected_thresholds = {"A": 90, "B": 80, "C": 70, "D": 60, "F": 0}
    assert found == expected_thresholds, (
        f"grade-band thresholds drifted: validator has {found}, "
        f"grading page expects {expected_thresholds}"
    )


def test_grading_page_lists_every_grade_band() -> None:
    """Each grade band appears in the Astro page with its range string."""
    text = _read(GRADING_PAGE)
    for grade, low, high in EXPECTED_GRADE_BANDS:
        if grade == "F":
            expected_range = "<60"
        else:
            expected_range = f"{low}–{high}"
        assert expected_range in text, (
            f"grading page missing range {expected_range!r} for grade {grade}"
        )


def test_no_top_level_anthropic_urls_on_grading_page() -> None:
    """Per the README/wiki Anthropic-deep-link convention, the grading page
    must NOT cite top-level docs.anthropic.com or www.anthropic.com URLs —
    use code.claude.com deep references instead.
    """
    text = _read(GRADING_PAGE)
    forbidden_patterns = [
        r"https?://(?:www\.)?anthropic\.com[/\"]",
        r"https?://docs\.anthropic\.com[/\"]",
        r"https?://claude\.ai[/\"]",
    ]
    for pat in forbidden_patterns:
        m = re.search(pat, text)
        assert m is None, (
            f"grading page has forbidden top-level Anthropic URL "
            f"matching {pat!r}: {m.group(0) if m else ''!r}. "
            "Use code.claude.com deep references."
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
