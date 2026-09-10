"""Regression tests for scripts/validate-skills-schema.py frontmatter checks.

Covers review findings f-ccp-validator-1 and f-ccp-validator-2 (2026-06-11):

  * f-ccp-validator-1 — validate_tool_permission always returned True and the
    caller dropped its diagnostic messages, so malformed or misspelled
    allowed-tools entries passed without any output.
  * f-ccp-validator-2 — a SKILL.md missing `name` at standard tier produced
    zero field-presence diagnostics despite STANDARD_REQUIRED = {name,
    description}.

Unknown but structurally valid tool names remain advisory. Structurally
malformed `allowed-tools` entries are ERROR-level under ratified blueprint 727
E1.11 and the owner's written approval. The marketplace-tier guard tests at
the bottom pin NON-NEGOTIABLES #1-#2 (missing ALWAYS_REQUIRED fields stay
ERRORS at marketplace tier).
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate-skills-schema.py"
_spec = importlib.util.spec_from_file_location("validate_skills_schema", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)

# A description long enough (>20 chars) and bland enough to avoid unrelated
# length / voice / discoverability diagnostics muddying assertions.
GOOD_DESC = "Validate skill frontmatter fields against the published schema registry."

SKILL_PATH = Path("plugins/testing/my-skill/skills/my-skill/SKILL.md")


def _frontmatter(fm: dict, tier: str):
    return validator.validate_frontmatter(SKILL_PATH, fm, tier=tier)


def test_schema_version_records_current_agent_contract():
    # 4.1.0: E4.3/E4.4 added the --safety-metrics ratchet feed (bare-Bash /
    # tier-2 tool-safety / shell-substitution sets, mirrors excluded).
    # 4.0.2: E4.12 corrected the compliance-rate denominator to include the
    # plugin-manifest lane (impossible 224.1% rates); 4.0.1 added the portable
    # ${SKILL_DIR}/${PLUGIN_ROOT} spellings. The fail-closed allowed-tools
    # semantics this test pins are unchanged from 4.0.0.
    assert validator.SCHEMA_VERSION == "4.1.0"


def test_current_skill_model_and_background_fields_are_accepted():
    for model in ("fable", "claude-opus-5"):
        fm = {
            "name": "my-skill",
            "description": GOOD_DESC,
            "model": model,
            "background": False,
        }
        errors, warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
        assert not any("model" in item or "background" in item for item in errors), (model, errors)
        assert not any("model" in item or "background" in item for item in warnings), (model, warnings)


def test_skill_background_must_be_boolean():
    fm = {"name": "my-skill", "description": GOOD_DESC, "background": "false"}
    errors, _warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert any("background" in error and "boolean" in error for error in errors), errors


# =========================================================================
# f-ccp-validator-1 — validate_tool_permission unit behavior
# =========================================================================


def test_known_bare_tools_are_valid_with_no_message():
    for tool in ("Read", "Write", "Edit", "Bash", "Grep", "Glob", "Skill"):
        valid, msg = validator.validate_tool_permission(tool)
        assert valid is True, tool
        assert msg == "", (tool, msg)


def test_valid_tools_is_the_canonical_43_from_tools_reference():
    # code.claude.com/docs/en/tools-reference (captured 2026-07-23).
    assert len(validator.VALID_TOOLS) == 43
    assert "Agent" in validator.VALID_TOOLS
    assert "Task" not in validator.VALID_TOOLS  # retired alias, see LEGACY_TOOL_ALIASES
    assert "Workflow" in validator.VALID_TOOLS
    assert "ExitPlanMode" in validator.VALID_TOOLS


def test_agent_is_a_first_class_tool_not_unknown():
    # Pre-3.16.0: Agent produced "Unknown tool 'Agent'" — the gate was wrong.
    valid, msg = validator.validate_tool_permission("Agent")
    assert valid is True
    assert msg == "", msg


def test_task_is_legacy_alias_of_agent_with_warning():
    valid, msg = validator.validate_tool_permission("Task")
    assert valid is True  # still accepted (SDK still emits Task in places)
    assert "Legacy" in msg
    assert "Agent" in msg
    assert validator.LEGACY_TOOL_ALIASES["Task"] == "Agent"


def test_scoped_colon_form_is_valid():
    valid, msg = validator.validate_tool_permission("Bash(git:*)")
    assert valid is True
    assert msg == ""


def test_scoped_space_form_is_valid_per_anthropic_canonical_example():
    # code.claude.com/docs/en/skills canonical example: Bash(git add *)
    valid, msg = validator.validate_tool_permission("Bash(git add *)")
    assert valid is True
    assert msg == "", msg


def test_mcp_tool_reference_is_valid():
    valid, msg = validator.validate_tool_permission("mcp__database-explorer__query_database")
    assert valid is True
    assert msg == "", msg


def test_misspelled_tool_name_yields_advisory_with_suggestion():
    valid, msg = validator.validate_tool_permission("Reads")
    assert valid is True  # well-formed, just unknown — advisory, not malformed
    assert "Reads" in msg
    assert "Read" in msg  # did-you-mean suggestion


def test_unclosed_paren_is_malformed():
    valid, msg = validator.validate_tool_permission("Bash(git add *")
    assert valid is False
    assert "parenthes" in msg.lower()


def test_stray_close_paren_is_malformed():
    valid, msg = validator.validate_tool_permission("wc:*)")
    assert valid is False
    assert msg


def test_empty_scope_is_malformed():
    valid, msg = validator.validate_tool_permission("Bash()")
    assert valid is False
    assert "scope" in msg.lower()


def test_empty_entry_is_malformed():
    valid, msg = validator.validate_tool_permission("   ")
    assert valid is False
    assert msg


# =========================================================================
# f-ccp-validator-1 — caller routing inside validate_frontmatter
# =========================================================================


def test_misspelled_allowed_tool_surfaces_warning_not_error():
    for tier in (validator.TIER_STANDARD, validator.TIER_MARKETPLACE):
        fm = {"name": "my-skill", "description": GOOD_DESC, "allowed-tools": "Reads, Write"}
        errors, warnings, _infos = _frontmatter(fm, tier)
        assert any("allowed-tools" in w and "Reads" in w for w in warnings), (tier, warnings)
        assert not any("allowed-tools" in e for e in errors), (tier, errors)


def test_malformed_allowed_tool_surfaces_error_at_every_tier():
    # YAML-list form so the comma-free truncated entry survives parsing intact.
    malformed_entries = ("Bash(git add *", "Bash()", "123invalid")
    for tier in (validator.TIER_STANDARD, validator.TIER_MARKETPLACE, validator.TIER_ENTERPRISE):
        for entry in malformed_entries:
            fm = {"name": "my-skill", "description": GOOD_DESC, "allowed-tools": [entry, "Read"]}
            errors, warnings, _infos = _frontmatter(fm, tier)
            valid, message = validator.validate_tool_permission(entry)
            assert valid is False
            assert any("allowed-tools" in e and message in e for e in errors), (tier, entry, errors)
            assert not any("allowed-tools" in w and message in w for w in warnings), (
                tier,
                entry,
                warnings,
            )


def test_structurally_empty_or_non_string_allowlist_entries_fail_closed():
    malformed_values = (
        [None],
        [True],
        ["Read", ""],
        ["Read", "   "],
        "Read,,Write",
        ",Read",
        "Read,",
    )
    for tier in (validator.TIER_STANDARD, validator.TIER_MARKETPLACE, validator.TIER_ENTERPRISE):
        for allowed_tools in malformed_values:
            fm = {"name": "my-skill", "description": GOOD_DESC, "allowed-tools": allowed_tools}
            errors, _warnings, _infos = _frontmatter(fm, tier)
            assert any("allowed-tools" in error for error in errors), (tier, allowed_tools, errors)


def test_clean_allowed_tools_produce_no_tool_diagnostics():
    supported_forms = (
        "Read, Write, Bash(git:*)",
        "Read Write Bash(git add *)",
        ["Read", "Write", "Bash(git:*)"],
    )
    for tier in (validator.TIER_STANDARD, validator.TIER_MARKETPLACE):
        for allowed_tools in supported_forms:
            fm = {"name": "my-skill", "description": GOOD_DESC, "allowed-tools": allowed_tools}
            errors, warnings, _infos = _frontmatter(fm, tier)
            assert not any("Unknown tool" in w or "Malformed" in w for w in warnings), (
                tier,
                allowed_tools,
                warnings,
            )
            assert not any("allowed-tools" in e for e in errors), (tier, allowed_tools, errors)


def test_folded_scalar_allowed_tools_parse_cleanly():
    frontmatter, _body = validator.parse_frontmatter(
        """---
name: my-skill
description: Validate folded scalar permission syntax without changing its semantics.
allowed-tools: >-
  Read Write Bash(git status *)
---

Validate the repository.
"""
    )
    errors, warnings, _infos = _frontmatter(frontmatter, validator.TIER_STANDARD)
    assert not any("allowed-tools" in error for error in errors), errors
    assert not any("allowed-tools" in warning for warning in warnings), warnings


def _tracked_skill_paths() -> list[Path]:
    repo_root = VALIDATOR_PATH.parent.parent
    result = subprocess.run(
        ["git", "ls-files", "plugins/**/SKILL.md"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = [repo_root / line for line in result.stdout.splitlines() if line]
    assert paths, "no tracked plugins/**/SKILL.md files found; corpus regression is vacuous"
    return paths


def _source_ancestor(path: Path) -> Path | None:
    repo_root = VALIDATOR_PATH.parent.parent
    for parent in (path.parent, *path.parents):
        if (parent / ".source.json").is_file():
            return parent
        if parent == repo_root:
            break
    return None


def test_tracked_corpus_has_zero_malformed_allowed_tools_by_provenance():
    repo_root = VALIDATOR_PATH.parent.parent
    malformed: dict[str, list[str]] = {"first-party": [], "mirror": []}
    declarations = {"first-party": 0, "mirror": 0}
    for path in _tracked_skill_paths():
        cohort = "mirror" if _source_ancestor(path) is not None else "first-party"
        frontmatter, _body = validator.parse_frontmatter(path.read_text(encoding="utf-8"))
        if "allowed-tools" not in frontmatter:
            continue
        declarations[cohort] += 1
        raw_tools = frontmatter["allowed-tools"]
        if not isinstance(raw_tools, (str, list)):
            malformed[cohort].append(
                f"{path.relative_to(repo_root)}: wrong type {type(raw_tools).__name__}"
            )
            continue
        if isinstance(raw_tools, list):
            invalid_items = [
                index
                for index, item in enumerate(raw_tools, start=1)
                if not isinstance(item, str) or not item.strip()
            ]
            if invalid_items:
                malformed[cohort].append(
                    f"{path.relative_to(repo_root)}: invalid YAML-list item(s) {invalid_items}"
                )
                continue
        if isinstance(raw_tools, str) and "," in raw_tools:
            empty_items = [
                index
                for index, item in enumerate(raw_tools.split(","), start=1)
                if not item.strip()
            ]
            if empty_items:
                malformed[cohort].append(
                    f"{path.relative_to(repo_root)}: empty CSV item(s) {empty_items}"
                )
                continue
        tools = validator.parse_allowed_tools(raw_tools)
        if not tools:
            malformed[cohort].append(f"{path.relative_to(repo_root)}: empty allowed-tools")
            continue
        for tool in tools:
            valid, message = validator.validate_tool_permission(tool)
            if not valid:
                malformed[cohort].append(f"{path.relative_to(repo_root)}: {message}")

    assert all(count > 0 for count in declarations.values()), declarations
    assert malformed == {"first-party": [], "mirror": []}


def test_mirror_owned_folded_scalars_are_parseable_and_byte_identical():
    folded_paths = []
    mirror_roots: set[Path] = set()
    for path in _tracked_skill_paths():
        frontmatter_text = path.read_text(encoding="utf-8")
        if "allowed-tools: >-" not in frontmatter_text:
            continue
        mirror_root = _source_ancestor(path)
        assert mirror_root is not None, f"folded scalar is not provenance-marked: {path}"
        folded_paths.append(path)
        mirror_roots.add(mirror_root)
        frontmatter, _body = validator.parse_frontmatter(frontmatter_text)
        tools = validator.parse_allowed_tools(frontmatter["allowed-tools"])
        assert tools
        assert all(validator.validate_tool_permission(tool)[0] for tool in tools)

    # E3.6 deleted the byte-identical .codex fork (blueprint 727 section 6:
    # a fork is not an adapter), so the folded-scalar census is the five
    # canonical kobiton skills only, and no .codex copy may reappear — the
    # adapter-thinness gate owns that invariant going forward.
    assert len(folded_paths) == 5
    assert len(mirror_roots) == 1
    mirror_root = mirror_roots.pop()
    assert all(".codex" not in path.parts for path in folded_paths)
    assert not (mirror_root / ".codex").exists()


# =========================================================================
# f-ccp-validator-2 — standard tier missing-name diagnostic
# =========================================================================


def test_standard_tier_missing_name_emits_warning():
    fm = {"description": GOOD_DESC}
    errors, warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert any("'name'" in w and "Missing" in w for w in warnings), (
        f"standard tier must diagnose a missing 'name' field; got warnings={warnings}"
    )
    # Warning-level only — promoting to error is gated by NON-NEGOTIABLE #7.
    assert not any("'name'" in e and "Missing" in e for e in errors), errors


def test_standard_tier_missing_description_still_warns():
    fm = {"name": "my-skill"}
    _errors, warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert any("'description'" in w and "Missing" in w for w in warnings), warnings


def test_standard_tier_complete_minimal_frontmatter_has_no_presence_warnings():
    fm = {"name": "my-skill", "description": GOOD_DESC}
    errors, warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert not errors, errors
    assert not any("Missing required field" in w or "Missing recommended field" in w for w in warnings), warnings


# =========================================================================
# NON-NEGOTIABLES #1-#2 guard — marketplace tier still ERRORS on the 8-field set
# =========================================================================


def test_marketplace_tier_missing_always_required_fields_are_errors():
    fm = {"name": "my-skill", "description": GOOD_DESC}
    errors, _warnings, _infos = _frontmatter(fm, validator.TIER_MARKETPLACE)
    for field in ("allowed-tools", "version", "author", "license", "compatibility", "tags"):
        assert any(f"'{field}'" in e and "Missing required field" in e for e in errors), (
            f"marketplace tier must ERROR on missing '{field}' (NON-NEGOTIABLE #2); got errors={errors}"
        )


def test_always_required_is_the_is_enterprise_8_field_set():
    # NON-NEGOTIABLE #1 — pin the canonical set so accidental reduction fails loudly.
    assert validator.ALWAYS_REQUIRED == {
        "name",
        "description",
        "allowed-tools",
        "version",
        "author",
        "license",
        "compatibility",
        "tags",
    }


# =========================================================================
# Issue #843 — agent body-vs-allowlist consistency checks.
# The `tools` frontmatter is a runtime allowlist; a body that invokes an MCP
# tool it never declares runtime-blocks every call. CHECK 1/3 = errors,
# CHECK 2 + over-declared = warnings.
# =========================================================================


def _body_check(tools, body):
    return validator.check_agent_body_vs_allowlist({"tools": tools}, body)


def test_843_check1_fq_mcp_not_in_allowlist_is_error():
    # Some MCP declared, but the body invokes a different (undeclared) one.
    errors, _ = _body_check(
        ["Read", "mcp__kobiton__getSession"],
        "First call `mcp__kobiton__listDevices` to enumerate, then inspect.",
    )
    assert any("CHECK 1" in e and "mcp__kobiton__listDevices" in e for e in errors), errors


def test_843_check3_zero_mcp_declared_with_body_ref_is_error():
    # The highest-confidence defect: no mcp__* declared at all, body uses one.
    errors, _ = _body_check(
        ["Read", "Bash(node:*)"],
        "Use `mcp__kobiton__getSession` to fetch the live session.",
    )
    assert any("CHECK 3" in e for e in errors), errors
    # CHECK 1 must NOT double-fire in the zero-declared case.
    assert not any("CHECK 1" in e for e in errors), errors


def test_843_clean_allowlist_matches_body_no_errors():
    errors, warnings = _body_check(
        ["Read", "mcp__kobiton__listDevices"],
        "Call `mcp__kobiton__listDevices` to enumerate devices.",
    )
    assert errors == [], errors
    # Declared tool IS referenced -> no over-declared warning either.
    assert not any("over-declared" in w for w in warnings), warnings


def test_843_no_mcp_anywhere_is_silent():
    # The common in-repo agent: no MCP tools, prose has no FQ mcp refs.
    errors, warnings = _body_check(
        ["Read", "Grep", "Glob"],
        "Analyze the repository structure and report findings. Read the configs.",
    )
    assert errors == []
    assert warnings == []


def test_843_fenced_code_examples_do_not_trigger_errors():
    # FQ refs inside ``` fences are documentation, not invocations.
    body = 'Here is the config shape:\n\n```json\n{"tool": "mcp__foo__bar"}\n```\n'
    errors, _ = _body_check(["Read"], body)
    assert errors == [], errors


def test_843_overdeclared_mcp_tool_warns():
    errors, warnings = _body_check(
        ["Read", "mcp__kobiton__terminateSession"],
        "Inspect the session state and summarize. No teardown here.",
    )
    assert errors == []
    assert any("over-declared" in w for w in warnings), warnings


def test_843_check2_shortname_mention_warns_not_errors():
    # CHECK 2 only fires for MCP-oriented agents (declares an mcp tool here),
    # so a backtick short name it never declared is flagged as a heuristic warn.
    errors, warnings = _body_check(
        ["Read", "mcp__kobiton__getSession"],
        "First `getSession`, then if the device is busy call `reserveDevice` and retry.",
    )
    assert not any("CHECK 1" in e or "CHECK 3" in e for e in errors), errors
    assert any("CHECK 2" in w and "reserveDevice" in w for w in warnings), warnings


def test_843_kebab_server_name_declared_and_used_is_clean():
    # Regression (schema 3.15.1): server segment with hyphens was invisible to
    # _RE_MCP_FQ, so a declared-and-used tool falsely warned as over-declared.
    errors, warnings = _body_check(
        ["Read", "mcp__semantic-scholar__paper_search"],
        "Call `mcp__semantic-scholar__paper_search` to find candidate papers.",
    )
    assert errors == [], errors
    assert not any("over-declared" in w for w in warnings), warnings


def test_843_snake_server_name_declared_and_used_is_clean():
    # Regression (schema 3.15.1): underscores in the server segment collided
    # with the `__` separator and the ref was never matched at all.
    errors, warnings = _body_check(
        ["Read", "mcp__plugin_automate_kobiton__getApp"],
        "Fetch metadata with `mcp__plugin_automate_kobiton__getApp` first.",
    )
    assert errors == [], errors
    assert not any("over-declared" in w for w in warnings), warnings


def test_843_kebab_server_undeclared_body_ref_still_errors():
    # True positive must survive the regex widening: an undeclared kebab-server
    # FQ ref in the body is still a CHECK 1 error.
    errors, _ = _body_check(
        ["Read", "mcp__semantic-scholar__paper_search"],
        "Then call `mcp__semantic-scholar__author_search` for the author list.",
    )
    assert any("CHECK 1" in e and "mcp__semantic-scholar__author_search" in e for e in errors), errors


def test_843_overdeclared_kebab_server_tool_still_warns():
    # True positive must survive: a declared kebab-server tool the body never
    # references is still flagged as over-declared privilege.
    errors, warnings = _body_check(
        ["Read", "mcp__semantic-scholar__paper_search"],
        "Summarize the papers already collected in the notes file.",
    )
    assert errors == []
    assert any("over-declared" in w and "mcp__semantic-scholar__paper_search" in w for w in warnings), warnings


def test_843_server_segment_cannot_swallow_separator():
    # Separator-ambiguity guard: in mcp__a_b__c the server segment must stop
    # at `a_b` (single-underscore joiner) and leave `__` as the separator, so
    # the exact declared string matches and no over-declared warning fires.
    errors, warnings = _body_check(
        ["Read", "mcp__a_b__c"],
        "Invoke `mcp__a_b__c` to run the check.",
    )
    assert errors == [], errors
    assert not any("over-declared" in w for w in warnings), warnings


def test_843_check2_suppressed_for_non_mcp_agent():
    # A code-focused agent with no MCP involvement: backtick `getStaticProps`
    # is prose, not a tool call — must not warn (the known-FP guard).
    errors, warnings = _body_check(
        ["Read", "Grep"],
        "Flag components using `getStaticProps` that should migrate to app router.",
    )
    assert errors == []
    assert not any("CHECK 2" in w for w in warnings), warnings


def test_843_end_to_end_validate_agent_surfaces_check3(tmp_path):
    # Full plugin-agent fixture (all required fields present) so the only
    # error is the #843 body-vs-allowlist one.
    agent = tmp_path / "plugins" / "x" / "agents" / "defective.md"
    agent.parent.mkdir(parents=True)
    (tmp_path / "plugins" / "x" / ".claude-plugin").mkdir(parents=True)
    (tmp_path / "plugins" / "x" / ".claude-plugin" / "plugin.json").write_text('{"name":"x"}')
    agent.write_text(
        "---\n"
        "name: defective\n"
        "description: Drives a Kobiton device session for automated UI testing flows end to end.\n"
        "tools:\n  - Read\n  - Bash\n"
        "model: sonnet\ncolor: blue\nversion: 1.0.0\n"
        "author: T <t@example.com>\n"
        "tags:\n  - testing\n  - mobile\n"
        "disallowedTools: []\nskills: []\nbackground: false\n"
        "---\n\n"
        "Call `mcp__kobiton__getSession` then `mcp__kobiton__getSessionArtifacts`.\n"
    )
    result = validator.validate_agent(agent)
    assert any("CHECK 3" in e for e in result["errors"]), result["errors"]


def _write_current_standalone_agent(tmp_path: Path, optional: str) -> Path:
    agent = tmp_path / ".claude" / "agents" / "current.md"
    agent.parent.mkdir(parents=True)
    agent.write_text(
        "---\n"
        "name: current\n"
        "description: Use when verifying the current Anthropic subagent contract.\n"
        "tools: [Read]\n"
        "model: claude-opus-5\n"
        "color: blue\n"
        "version: 1.0.0\n"
        "author: T <t@example.com>\n"
        "tags: [validation]\n"
        "disallowedTools: []\n"
        "skills: []\n"
        "background: false\n"
        "hooks: {}\n"
        "mcpServers: [github]\n"
        "permissionMode: manual\n"
        f"{optional}"
        "---\n\n"
        "Read the requested files and report contract drift.\n"
    )
    return agent


def test_agent_accepts_full_model_id_manual_mode_and_experimental_cache_ttl(tmp_path):
    agent = _write_current_standalone_agent(
        tmp_path,
        "experimental:\n  cacheTtl: 1h\n",
    )
    result = validator.validate_agent(agent)
    assert result["errors"] == [], result
    assert result["warnings"] == [], result


def test_agent_rejects_invalid_experimental_cache_ttl(tmp_path):
    agent = _write_current_standalone_agent(
        tmp_path,
        "experimental:\n  cacheTtl: forever\n",
    )
    result = validator.validate_agent(agent)
    assert any("experimental.cacheTtl" in error for error in result["errors"]), result


def test_agent_warns_when_experimental_key_will_be_ignored(tmp_path):
    agent = _write_current_standalone_agent(
        tmp_path,
        "experimental:\n  cacheTtl: 5m\n  futureFlag: true\n",
    )
    result = validator.validate_agent(agent)
    assert result["errors"] == [], result
    assert any("futureFlag" in warning for warning in result["warnings"]), result


# =========================================================================
# schema 3.7.0 / 3.15.2 — disallowed-tools cross-field enforcement
#   (claude-41c2.2): shape guard + allowed-tools ∩ disallowed-tools overlap
#   is an ERROR at every tier, mirroring the 3.5.0 requires_*/fallback_for_*
#   overlap rule. Both lists normalize through parse_allowed_tools().
# =========================================================================


def test_allowed_disallowed_tool_overlap_is_error():
    fm = {
        "name": "my-skill",
        "description": GOOD_DESC,
        "allowed-tools": "Read, Bash(rm:*)",
        "disallowed-tools": "Bash(rm:*)",
    }
    errors, _warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert any("contradictory tool declaration" in e and "Bash(rm:*)" in e for e in errors), errors


def test_overlap_is_error_at_marketplace_tier_too():
    fm = {
        "name": "my-skill",
        "description": GOOD_DESC,
        "allowed-tools": ["Read", "Write"],
        "disallowed-tools": ["Write"],
    }
    errors, _warnings, _infos = _frontmatter(fm, validator.TIER_MARKETPLACE)
    assert any("contradictory tool declaration" in e and "Write" in e for e in errors), errors


def test_disjoint_allowed_disallowed_is_clean():
    # Defense-in-depth: disallow a tool NOT in allowed-tools (the intended use).
    fm = {
        "name": "my-skill",
        "description": GOOD_DESC,
        "allowed-tools": "Read, Write",
        "disallowed-tools": "Bash(rm:*), Bash(curl:*)",
    }
    errors, _warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert not any("contradictory tool declaration" in e for e in errors), errors


def test_overlap_detection_uses_shared_normalization():
    # Space-separated allowed-tools vs the same token in disallowed-tools must
    # still overlap — both go through parse_allowed_tools().
    fm = {
        "name": "my-skill",
        "description": GOOD_DESC,
        "allowed-tools": "Read Bash(rm:*)",
        "disallowed-tools": ["Bash(rm:*)"],
    }
    errors, _warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert any("contradictory tool declaration" in e for e in errors), errors


def test_disallowed_tools_without_allowed_tools_is_clean():
    # The overlap check is guarded on allowed-tools also being present.
    fm = {"name": "my-skill", "description": GOOD_DESC, "disallowed-tools": "Bash(rm:*)"}
    errors, _warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert not any("contradictory tool declaration" in e for e in errors), errors


def test_disallowed_tools_bad_shape_is_error():
    fm = {
        "name": "my-skill",
        "description": GOOD_DESC,
        "allowed-tools": "Read",
        "disallowed-tools": 123,
    }
    errors, _warnings, _infos = _frontmatter(fm, validator.TIER_STANDARD)
    assert any("'disallowed-tools' must be" in e for e in errors), errors


# =========================================================================
# schema 3.16.1 — security lane (load-time shell + disallowed-tools entries)
# Residual of closed PR #1113; re-cut cleanly on main after VALID_TOOLS 3.16.0.
# =========================================================================

SHELL_SKILL = """---
name: my-skill
description: Validate skill frontmatter fields against the published schema registry.
---

# Body

!`git status`
"""


def test_load_time_shell_substitution_is_reported():
    hits = validator._load_time_shell_hits("a\n!`git status`\nb")
    assert len(hits) == 1, hits
    assert "git status" in hits[0]


def test_shell_hits_are_reported_in_file_line_numbers():
    """A security finding pointing at the wrong line is worse than none."""
    body = "x\n!`whoami`\n"
    assert validator._load_time_shell_hits(body)[0].startswith("L2:")
    assert validator._load_time_shell_hits(body, line_offset=10)[0].startswith("L12:")


def test_shell_syntax_inside_an_ordinary_fence_is_not_a_finding():
    """Skills that DOCUMENT the syntax must not be flagged as executing it."""
    body = "```\n!`git status`\n```\n"
    assert validator._load_time_shell_hits(body) == []


def test_shell_fence_form_is_always_counted():
    hits = validator._load_time_shell_hits("```!\necho hi\n```\n")
    assert any("```! block" in h for h in hits), hits


def test_body_check_surfaces_shell_execution_as_a_warning_not_an_error():
    errors, warnings, _ = validator.validate_body(
        SKILL_PATH, SHELL_SKILL.split("---", 2)[2], validator.TIER_MARKETPLACE, {"name": "my-skill"}
    )
    assert any("LOAD time" in w for w in warnings), warnings
    assert not any("LOAD time" in e for e in errors), errors


def test_disallowed_tools_entries_are_validated():
    """A deny rule naming a non-existent tool denies nothing."""
    fm = {"name": "my-skill", "description": GOOD_DESC, "disallowed-tools": "Wibble"}
    _, warnings, _ = _frontmatter(fm, validator.TIER_MARKETPLACE)
    assert any("disallowed-tools" in w and "Wibble" in w for w in warnings), warnings


def test_disallowed_tools_flags_the_legacy_name():
    fm = {"name": "my-skill", "description": GOOD_DESC, "disallowed-tools": "Task"}
    _, warnings, _ = _frontmatter(fm, validator.TIER_MARKETPLACE)
    assert any("disallowed-tools" in w and ("Legacy" in w or "Task" in w) for w in warnings), warnings


def test_disallowed_tools_overlap_error_still_fires():
    """Regression guard: entry validation must not displace the overlap rule."""
    fm = {
        "name": "my-skill",
        "description": GOOD_DESC,
        "allowed-tools": "Read",
        "disallowed-tools": "Read",
    }
    errors, _, _ = _frontmatter(fm, validator.TIER_MARKETPLACE)
    assert any("contradictory" in e for e in errors), errors


def test_clean_disallowed_tools_is_quiet():
    fm = {"name": "my-skill", "description": GOOD_DESC, "disallowed-tools": "Bash(rm:*), Agent"}
    _, warnings, _ = _frontmatter(fm, validator.TIER_MARKETPLACE)
    assert not any("disallowed-tools" in w for w in warnings), warnings


# =========================================================================
# 4.0.2 — compliance-rate invariants (blueprint 727 bead 4.12)
# =========================================================================


def test_compliance_rate_invariants():
    assert validator.compute_compliance_rate(0, 0) == 0.0
    assert validator.compute_compliance_rate(0, 10) == 0.0
    assert validator.compute_compliance_rate(10, 10) == 100.0
    assert 0.0 <= validator.compute_compliance_rate(3, 7) <= 100.0
    import pytest

    with pytest.raises(ValueError):
        validator.compute_compliance_rate(11, 10)  # the 224.1% class
    with pytest.raises(ValueError):
        validator.compute_compliance_rate(-1, 10)
