"""Source-owned production heuristics preserve findings, not runtime guarantees."""

import ast
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load(ROOT / "scripts/validate-skills-schema.py", "canonical_tier2_test")
helper = load(ROOT / "scripts/skill_production_gate.py", "standalone_tier2_test")


@pytest.mark.parametrize(
    "raw,expected",
    [
        (None, []),
        (False, []),
        ("", []),
        (["Read", " Bash(git add *) "], ["Read", "Bash(git add *)"]),
        ("Read Bash(git add *)", ["Read", "Bash(git add *)"]),
        ("Read, Bash(git add *)", ["Read", "Bash(git add *)"]),
        ("Read Write,Bash(git:*)", ["Read Write", "Bash(git:*)"]),
    ],
)
def test_exact_skill_parser_legacy_controls(raw, expected):
    assert helper.parse_allowed_tools(raw) == expected
    assert validator.parse_allowed_tools(raw) == expected


def test_descriptor_matches_actual_implicit_flags_and_canonical_ast():
    descriptor = json.loads((ROOT / "scripts/skill_production_policy.json").read_text())
    assert descriptor["code_fence"] == {
        "pattern": validator.CODE_FENCE_PATTERN.pattern,
        "flags": validator.CODE_FENCE_PATTERN.flags,
    }
    assert validator.CODE_FENCE_PATTERN.flags == re.UNICODE
    tree = ast.parse((ROOT / "scripts/validate-skills-schema.py").read_text())
    matches = [
        n
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "CODE_FENCE_PATTERN" for t in n.targets)
    ]
    expected = ast.parse('CODE_FENCE_PATTERN = re.compile(r"^\\s*(```|~~~)")').body[0]
    assert len(matches) == 1
    assert ast.dump(matches[0], include_attributes=False) == ast.dump(expected, include_attributes=False)


@pytest.mark.parametrize(
    "body,fm",
    [
        ("Plain instructions.", {}),
        ("Read", {"allowed-tools": ["Write", "Read", "Bash"]}),
        ("curl endpoint", {}),
        ("curl endpoint; authentication is documented", {}),
        ("if false\nif false\nif false\nif false", {}),
        ("Write output", {"allowed-tools": "Bash Write"}),
        ("Safety Justification: bounded inputs", {"allowed-tools": "Bash Write"}),
        ("Write output", {"allowed-tools": "Bash(git add *) Write"}),
        ("delegate to /other", {}),
        ("```\ndelegate to /other\n```", {}),
        ("~~~\ndelegate to /other\n~~~", {}),
        ("never delegate to /other\n> delegate to /other\n| delegate to /other |", {}),
    ],
)
def test_public_legacy_wrapper_matches_pure_explicit_dependency(body, fm):
    assert validator.validate_tier2_production_gate(Path("unused"), body, fm) == helper.validate_tier2_production_gate(
        Path("unused"), body, fm, fence_pattern=validator.CODE_FENCE_PATTERN
    )


def test_exact_warning_order_and_error_messages():
    body = "curl endpoint\nif false\nspawn another skill"
    errors, warnings, infos = helper.validate_tier2_production_gate(
        Path("unused"),
        body,
        {"allowed-tools": ["Write", "Bash", "Read"]},
        fence_pattern=validator.CODE_FENCE_PATTERN,
    )
    assert errors == [
        "[tier2:tool-safety] Unscoped Bash + Write/WebFetch declared without a Safety Justification section — high-risk combo. Add `## Safety Justification` explaining why.",
        "[tier2:orchestration-bounds] Body contains orchestration smell 'spawn another skill' — cross-skill orchestration is plugin-layer concern, not skill-layer",
    ]
    assert warnings == [
        "[tier2:allowed-tools-accuracy] Tool 'Read' is declared in allowed-tools but never referenced in the skill body — over-permissive or stale declaration",
        "[tier2:allowed-tools-accuracy] Tool 'Write' is declared in allowed-tools but never referenced in the skill body — over-permissive or stale declaration",
        "[tier2:auth-documented] External API surface referenced (curl/fetch/MCP/OAuth/etc.) but no authentication method documented — add an Auth section or reference auth.md",
        "[tier2:dead-code] Literal-false branch found at line ~2: 'if false'",
    ]
    assert infos == [
        "[tier2] Production gate ran 5 checks: allowed-tools accuracy, auth documented, dead code, tool safety, orchestration bounds"
    ]


def test_dead_code_limit_and_explicit_fence_dependency():
    errors, warnings = helper.tier2_check_dead_code("if false\n" * 4)
    assert errors == []
    assert len(warnings) == 3
    assert "line ~3" in warnings[-1]
    assert helper.tier2_check_orchestration_bounds(
        "CUSTOM\nspawn another skill\nCUSTOM", fence_pattern=re.compile("^CUSTOM$")
    ) == ([], [])


def test_standard_demotes_only_tier2_errors(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "---\nname: fixture\ndescription: A complete fixture for static policy tests.\nallowed-tools: Bash Write\n---\nPlain instructions.\n"
    )
    standard = validator.validate_skill(skill, tier=validator.TIER_STANDARD)
    marketplace = validator.validate_skill(skill, tier=validator.TIER_MARKETPLACE)
    assert not any("[tier2:" in e for e in standard["errors"])
    assert any("[tier2:tool-safety]" in e for e in standard["warnings"])
    assert any("[tier2:tool-safety]" in e for e in marketplace["errors"])


def test_loader_ignores_hostile_cwd_pythonpath_and_cache(tmp_path):
    (tmp_path / "skill_production_gate.py").write_text('raise RuntimeError("hostile")\n')
    script = f"""import importlib.util,sys,types
sys.modules['_canonical_skill_production_gate']=types.SimpleNamespace(parse_allowed_tools=lambda _: ['hostile'])
spec=importlib.util.spec_from_file_location('v',{str(ROOT / "scripts/validate-skills-schema.py")!r})
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
assert v.parse_allowed_tools('Read Bash(git add *)') == ['Read','Bash(git add *)']
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(tmp_path)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_retained_original_boundary_oracle():
    import hashlib

    fixtures = ROOT / "tests/fixtures/skill-production"
    inputs = (fixtures / "inputs.json").read_bytes()
    original = json.loads((fixtures / "expected.json").read_text())
    assert original["source_commit"] == "ed4778951a4007d1ca56781a468233212e371502"
    assert (
        original["source_hashes"]["validate-skills-schema.py"]
        == "fb202d6362f8e33c55654ff8b278dbe5bccd122b297bccb3ca15a6aac3358595"
    )
    assert original["inputs_sha256"] == hashlib.sha256(inputs).hexdigest()
    cases = json.loads(inputs)
    assert [c["id"] for c in cases] == [c["id"] for c in original["cases"]]
    for case, expected in zip(cases, original["cases"], strict=True):
        actual = helper.validate_tier2_production_gate(
            Path("unused"), case["body"], case["frontmatter"], fence_pattern=validator.CODE_FENCE_PATTERN
        )
        assert actual == (expected["errors"], expected["warnings"], expected["infos"]), case["id"]


def test_standalone_stdlib_only_import(tmp_path):
    import shutil

    copied = tmp_path / "skill_production_gate.py"
    shutil.copyfile(ROOT / "scripts/skill_production_gate.py", copied)
    script = f"""import importlib.util,re
s=importlib.util.spec_from_file_location('isolated',{str(copied)!r});m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert m.parse_allowed_tools('Read Bash(git add *)') == ['Read','Bash(git add *)']
assert m.validate_tier2_production_gate(None,'Plain instructions',{{}},fence_pattern=re.compile(r'^\\s*(```|~~~)'))[0:2] == ([],[])
"""
    result = subprocess.run([sys.executable, "-I", "-S", "-c", script], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_enterprise_alias_actual_cli_normalization(tmp_path):
    skill = tmp_path / "SKILL.md"
    skill.write_text(
        "---\nname: fixture\ndescription: A meaningful fixture for the static production boundary.\nallowed-tools: Bash Write\n---\nPlain instructions.\n"
    )
    rows = {}
    for flag in ["--standard", "--marketplace", "--enterprise"]:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate-skills-schema.py"), flag, "--json", str(skill)],
            env={**os.environ, "CI": "true"},
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)[0]
        rows[flag] = {name: [v for v in payload[name] if v.startswith("[tier2:")] for name in ["errors", "warnings"]}
    assert rows["--marketplace"] == rows["--enterprise"]
    assert rows["--marketplace"]["errors"]
    assert rows["--standard"]["errors"] == []
    assert rows["--marketplace"]["errors"][0] in rows["--standard"]["warnings"]
