#!/usr/bin/env python3
"""
Claude Code Plugin Validator v7.0 (Anthropic-Aligned Two-Tier Schema)

Unified validator for all Claude Code plugin content:
- SKILL.md files (Agent Skills)
- commands/*.md files (Slash Commands)
- agents/*.md files (Custom Agents)

Two-tier validation system (aligned with Anthropic published spec):
- Standard (DEFAULT): Mirrors Anthropic spec exactly. Required: name + description only.
  All other fields optional. Type/value validation when fields are present.
- Marketplace (--marketplace): IS enterprise standard. All 8 ALWAYS_REQUIRED fields
  (name, description, allowed-tools, version, author, license, compatibility, tags)
  must be present — missing any of them is an ERROR (schema 3.3.0+; see
  000-docs/SCHEMA_CHANGELOG.md NON-NEGOTIABLES #1-#2). 100-point rubric.
- Deep (--deep): Intent Solutions Deep Evaluation Engine. 10 weighted dimensions.
- Auto-detect: if CI=true or GITHUB_ACTIONS=true → marketplace by default.

The legacy --enterprise flag is a deprecated alias for --marketplace.

Schema registry sources (all 7 verified 2026-04-28):
- platform.claude.com/docs/en/agents-and-tools/agent-skills/overview      (name+description required)
- platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (name+description required)
- code.claude.com/docs/en/skills                                          (description recommended)
- code.claude.com/docs/en/plugins-reference                               (no extra SKILL.md fields)
- anthropic.com/engineering/equipping-agents-for-the-real-world-...       (name+description required)
- agentskills.io/specification                                            (compatibility, metadata are optional)
- github.com/anthropics/skills                                            (reference impl)

Usage:
    python scripts/validate-skills-schema.py [--verbose|-v]              # Standard tier (default)
    python scripts/validate-skills-schema.py --marketplace [--verbose]   # Marketplace tier
    python scripts/validate-skills-schema.py --enterprise                # Deprecated alias for --marketplace
    python scripts/validate-skills-schema.py --standard [--verbose]      # Explicit standard
    python scripts/validate-skills-schema.py --deep [--verbose]          # Deep Evaluation Engine
    python scripts/validate-skills-schema.py --skills-only
    python scripts/validate-skills-schema.py --commands-only
    python scripts/validate-skills-schema.py --agents-only
    python scripts/validate-skills-schema.py path/to/SKILL.md            # Single-file mode

Author: Jeremy Longshore <jeremy@intentsolutions.io>
Version: 7.0.0
Schema:  3.8.0  (see 000-docs/SCHEMA_CHANGELOG.md)
"""

import argparse
import difflib
import hashlib
import json as json_module
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml required. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# === CONSTANTS ===

# Schema version (independent of validator script version).
# 3.0.0 (2026-04-28) — attempted realignment to Anthropic spec; reduced
#                       required fields to {name, description}. REVERTED in 3.3.0.
# 3.1.0 (2026-04-28) — added when_to_use, arguments, paths, shell to SKILL_FIELDS;
#                       effort valid values include xhigh. (These technical
#                       additions are kept in 3.3.0.)
# 3.2.0 (2026-04-28) — reframed tier model around tracking metadata. REVERTED in 3.3.0.
# 3.3.0 (2026-04-28) — restored 8-field enterprise standard (name, description,
#                       allowed-tools, version, author, license, compatibility, tags).
#                       compatible-with → compatibility migration is the only kept
#                       change from the 3.0–3.2 experiments. when_to_use, arguments,
#                       paths, shell, effort:xhigh additions are also kept.
# 3.3.1 (2026-04-28) — Claude Code extension audit: fixed `allowed-tools` to accept
#                       YAML lists AND space-separated strings per Anthropic spec
#                       (was rejecting YAML lists, was only splitting on commas);
#                       relaxed CONDITIONAL_FIELDS for `agent` (defaults to
#                       general-purpose per spec — not a missing-field warning);
#                       fixed `argument-hint` conditional (disable-model-invocation
#                       doesn't affect /-menu visibility); added ${CLAUDE_EFFORT} to
#                       YAML_VALUE_ALLOWED_VARS.
# 3.7.0 (2026-05-28) — Claude Code v2.1.152 (released 2026-05-27) added
#                       `disallowed-tools` to SKILL.md frontmatter. Recognized as
#                       Anthropic-source optional field with same string|array shape
#                       as `allowed-tools`. Per SAK plan 031 § 14.10 binding, lands
#                       at IS marketplace tier (NOT spec-floor recognition).
#                       Snapshot anchor: intent-eval-platform/intent-eval-lab/research/
#                       claude-docs-spec-tree-2026-05-27.md.
# 3.8.0 (2026-06-11) — allowed-tools entry validation made real (was
#                       always-True with diagnostics silently dropped):
#                       malformed entries (unbalanced parens, empty scope,
#                       illegal tool-name characters) and unknown tool names
#                       now surface as WARNINGS at all tiers; standard tier
#                       now emits a missing-'name' warning (was silent);
#                       stale "marketplace = warnings-only" docstrings
#                       corrected. No change to ALWAYS_REQUIRED or
#                       error-vs-warning semantics.
# 3.10.0 (2026-06-17) — AGENT gate flipped to KERNEL-STRICT + ENTERPRISE-FLESHED
#                       (Jeremy sign-off on the required-field-set change). Agents
#                       are NOT tier-gated like skills. Two layers, both ERRORS at
#                       every tier:
#                         (a) Kernel floor (8): name, description, tools, model,
#                             color, version, author, tags. Source of truth:
#                             @intentsolutions/core schemas/authoring/v1/
#                             agent-definition (upstream-base ∪ is-overlay),
#                             consumed via load_kernel_agent_required() with an
#                             inline AGENT_ALWAYS_REQUIRED fallback.
#                         (b) Enterprise "flesh out the entire spec" live set on
#                             top of the floor: + disallowedTools, skills,
#                             background for ALL agents (=> 11 on a plugin agent),
#                             + hooks, mcpServers, permissionMode for STANDALONE
#                             agents (=> 14; those three are plugin-level and
#                             runtime-ignored on a plugin agent). Six optional
#                             tuning fields (effort, maxTurns, memory, isolation,
#                             initialPrompt, experimental) are carried as a
#                             commented "upgrade levers" body block, not
#                             parser-required.
#                       `fable` added to the agent model enum. Banned agent fields
#                       (capabilities, expertise_level, activation_priority,
#                       activation_triggers, type, category + kernel
#                       deprecationRegistry compatible-with/when_to_use) promoted
#                       WARN → ERROR. tools accepts string|array (tolerant — no
#                       forced re-typing). description over-length warning realigned
#                       200 → 1536 (kernel disclosureMarkers cap). No change to the
#                       SKILL ALWAYS_REQUIRED set or skill tier semantics.
# 3.12.0 (2026-06-28) — plugin.json manifest brought up to the current Anthropic
#                       GA spec (code.claude.com/docs/en/plugins-reference). Added
#                       7 GA fields + 1 experimental object to PLUGIN_JSON_FIELDS:
#                       displayName, defaultEnabled (boolean), dependencies,
#                       userConfig, channels, $schema, experimental. Without these
#                       the validator hard-rejected valid current plugins as
#                       "Unknown field … not in Anthropic spec." TYPE_MAP gained
#                       `boolean` (for defaultEnabled). Spec-compliance fix
#                       (NON-NEGOTIABLE #6: adding missing documented fields).
#                       Unknown-field error-vs-warning semantics UNCHANGED in
#                       3.12.0 — that flip is NON-NEGOTIABLE #7 (needs sign-off),
#                       landed in 3.13.0. No change to any required-fields set/tier.
# 3.13.0 (2026-06-28) — plugin.json UNRECOGNIZED fields: ERROR -> WARNING by
#                       default; new --strict flag promotes them back to errors
#                       (mirrors `claude plugin validate --strict`). Wrong-type
#                       fields + missing required 'name' stay errors. Now
#                       consistent with the SKILL.md + agent validators, which
#                       already warn (never error) on unknown fields. Adds a
#                       difflib "did you mean" near-miss hint. NON-NEGOTIABLE #7
#                       error-vs-warning change — APPROVED by Jeremy Longshore
#                       2026-06-28 (sign-off recorded in the PR thread). No change
#                       to any required-fields set or tier semantics.
# 3.14.0 (2026-06-28) — L2 consumer-cutover (692-AA-AACR § 0.5): PLUGIN_JSON_FIELDS
#                       is now drift-gated against the kernel's CURRENT (authoring/v2)
#                       plugin-manifest field surface via load_kernel_plugin_fields()
#                       + a `plugin_manifest` block in kernel_shadow_report() — so the
#                       next upstream plugin-manifest field the kernel captures is
#                       CAUGHT in the kernel-shadow CI lane instead of needing a
#                       hand-patch (the failure mode that produced 3.12.0). The shadow
#                       immediately surfaced one drift — the kernel sanctions a
#                       `metadata` plugin.json field (authoring/v2 is-overlay) CCPI
#                       lacked — now adopted into PLUGIN_JSON_FIELDS (fields match).
#                       Advisory (PLUGIN_JSON_FIELDS stays authoritative until the
#                       DR-049 flip). Reads authoring/V2 (v1 plugin-manifest is stale);
#                       needs @intentsolutions/core>=0.9.0.
# 3.15.0 (2026-07-01) — iel-62j validator FAIRNESS: the enterprise (marketplace)
#                       body-section checks now credit equivalent, well-understood
#                       heading names (e.g. `## Usage`≈`## Instructions`,
#                       `## Summary`/`## Capabilities`≈`## Overview`,
#                       `## Returns`≈`## Output`, `## Troubleshooting`≈`## Error
#                       Handling`, `## References`≈`## Resources`) so an external
#                       contributor is not failed for standard-but-non-IS section
#                       wording. RECOMMENDED_SECTIONS was never a published standard
#                       (see the note there); requiring the EXACT IS wording was
#                       off-spec. Presence + non-empty-content + step-by-step checks
#                       all resolve synonyms via SECTION_SYNONYMS /
#                       resolve_present_heading(). NOT a semantics change: an error
#                       still fires when NEITHER the canonical section NOR any
#                       synonym is present; tiers, ALWAYS_REQUIRED, and the
#                       frontmatter `capabilities` BAN (NON-NEGOTIABLE) are all
#                       unchanged — only `## Capabilities` as a *heading* is credited
#                       as an Overview synonym.
# 3.15.2 (2026-07-12) — disallowed-tools (schema 3.7.0) cross-field enforcement
#                       made real. The field was recognized since 3.7.0 but its
#                       two rules were never checked: (1) shape — must be a
#                       string or YAML list (same as allowed-tools); (2) a tool
#                       pattern MUST NOT appear in both allowed-tools and
#                       disallowed-tools (contradictory permit+deny), an ERROR at
#                       every tier, mirroring the 3.5.0 requires_*/fallback_for_*
#                       overlap rule. Reuses parse_allowed_tools() so both lists
#                       normalize identically. Spec-compliance implementation of
#                       already-documented behavior (repo CLAUDE.md + 000-docs/681);
#                       not an architectural change — ALWAYS_REQUIRED, tiers, and
#                       error-vs-warning semantics are unchanged. Closes claude-41c2.2.
# 3.16.0 (2026-07-23) — VALID_TOOLS expanded from 13 names to the full 43-tool
#                       set from code.claude.com/docs/en/tools-reference. Adds
#                       Agent (was missing — gate treated it as unknown) and
#                       demotes Task to LEGACY_TOOL_ALIASES with a warn (renamed
#                       to Agent in v2.1.63; SDK still emits Task in places).
#                       Spec-compliance bug fix (NON-NEGOTIABLE #6) — advisory
#                       severity only; ALWAYS_REQUIRED / tiers / error-vs-warning
#                       unchanged. Source: IEP plan golden-imagining-planet Phase A.
# 3.16.1 (2026-07-23) — security lane (advisory only): load-time shell
#                       substitution (!`cmd` / ```!) + disallowed-tools entry
#                       validation (mirrors allowed-tools). Residual of closed #1113.
# 4.0.0 (2026-08-16)  — malformed allowed-tools entries fail closed as ERRORS
#                       at every tier; unknown but well-formed names remain
#                       advisory. Approved by ratified blueprint 727 E1.11 and
#                       the owner's written execution directive.
# 4.1.0 (2026-09-09 amendment) — current Anthropic subagent contract: recognize the
#                       optional experimental object and validate cacheTtl as
#                       5m|1h; accept permissionMode: manual and documented full
#                       Claude model IDs. Required fields and tier semantics are
#                       unchanged. Source: code.claude.com/docs/en/sub-agents.
# See 000-docs/SCHEMA_CHANGELOG.md.
SCHEMA_VERSION = "4.1.0"

# Rule IDs are part of the compliance-baseline contract, not a census of the
# errors that happen to exist today. Keep the declared inventory stable when
# the last finding for a rule is fixed or its artifact is retired; otherwise a
# strict debt reduction is indistinguishable from disabling a validator rule.
# Newly observed catch-all hashes are still added below and therefore fail the
# ratchet until they receive the normal owner-reviewed baseline treatment.
DECLARED_MARKETPLACE_RULE_INVENTORY = frozenset(
    {
        "E-AGENT-8355989ea80e",
        "E-AGENT-ad4126251028",
        "E-AGENT-e7ed4704ab0d",
        "E-BODY-a8e5f61fa69b",
        "E-FATAL-9a99b10dfdaf",
        "E-FRONTMATTER-9c196f479e69",
        "E-FRONTMATTER-a84c0ab5ddff",
        "E-FRONTMATTER-e9c3798ae38e",
        "E-FRONTMATTER-f666eb7a814d",
        "E-INVALID-FIELD",
        "E-MISSING-REQUIRED-FIELD",
        "E-MISSING-REQUIRED-SECTION",
        "E-REFERENCE-ESCAPES-SKILL-DIRECTORY",
        "E-TIER2-ORCHESTRATION-BOUNDS-31b9cdf7bcb8",
        "E-TIER2-TOOL-SAFETY-5d322e66e4de",
        "E-VALIDATOR-696637dc3a0f",
        "E-VALIDATOR-c457e10de492",
        "E-VALIDATOR-fed1b0ce3bfe",
        "E-YAML-SHELL-SUBSTITUTION",
    }
)


def compute_compliance_rate(compliant_count: int, total_count: int) -> float:
    """Compliance rate with the 4.12 invariants: 0 <= rate <= 100 and
    compliant <= total by construction. An impossible pair (numerator larger
    than its population) raises instead of printing nonsense — the 224.1%
    class fails loudly if a lane is ever miscounted again."""
    if total_count == 0:
        return 0.0
    if compliant_count < 0 or total_count < 0 or compliant_count > total_count:
        raise ValueError(
            f"impossible compliance pair: {compliant_count}/{total_count} — a validation lane is counted in the numerator but not the denominator"
        )
    return compliant_count / total_count * 100


# Validation tiers
TIER_STANDARD = "standard"
TIER_MARKETPLACE = "marketplace"
# Backward-compat alias; --enterprise still resolves to TIER_MARKETPLACE
TIER_ENTERPRISE = TIER_MARKETPLACE

# Canonical built-in tool names from code.claude.com/docs/en/tools-reference
# (captured 2026-07-23). These are the exact strings used in permission rules,
# subagent tool lists, and hook matchers. Count = 43.
# Previously this set had 13 names and omitted `Agent` while listing the
# retired alias `Task` — which made the marketplace gate reject correct
# declarations and silently bless the legacy name (IEP plan golden-imagining-planet,
# Phase A).
VALID_TOOLS = {
    "Agent",
    "Artifact",
    "AskUserQuestion",
    "Bash",
    "CronCreate",
    "CronDelete",
    "CronList",
    "Edit",
    "EndConversation",
    "EnterPlanMode",
    "EnterWorktree",
    "ExitPlanMode",
    "ExitWorktree",
    "Glob",
    "Grep",
    "ListMcpResourcesTool",
    "LSP",
    "Monitor",
    "NotebookEdit",
    "PowerShell",
    "PushNotification",
    "Read",
    "ReadMcpResourceTool",
    "RemoteTrigger",
    "ReportFindings",
    "ScheduleWakeup",
    "SendMessage",
    "SendUserFile",
    "ShareOnboardingGuide",
    "Skill",
    "TaskCreate",
    "TaskGet",
    "TaskList",
    "TaskOutput",
    "TaskStop",
    "TaskUpdate",
    "TodoWrite",
    "ToolSearch",
    "WaitForMcpServers",
    "WebFetch",
    "WebSearch",
    "Workflow",
    "Write",
}

# Retired names that still appear in the wild. Accept with a warning; prefer
# the canonical name. SDK system:init still emits "Task" in some tool lists
# even though tool_use events use "Agent" (v2.1.63+ rename).
LEGACY_TOOL_ALIASES = {
    "Task": "Agent",
}

# === Two-tier field definitions (Anthropic spec alignment, 2026-04-28) ===
#
# Hard requirements (BOTH tiers):
#   name, description
# Sources: platform.claude.com/...overview, platform.claude.com/...best-practices,
#          anthropic.com/engineering/equipping-agents..., agentskills.io/specification
#
# Standard tier: nothing else required. All other fields optional, validated
# only if present. Mirrors Anthropic published spec verbatim.
#
# Marketplace tier: the full IS enterprise 8-field set (ALWAYS_REQUIRED) must
# be present — missing any of them is an ERROR (restored in schema 3.3.0; see
# 000-docs/SCHEMA_CHANGELOG.md NON-NEGOTIABLES #1-#2). The rubric additionally
# rewards inclusion of optional polish fields.
STANDARD_REQUIRED = {"name", "description"}
STANDARD_RECOMMENDED = set()  # description is now in REQUIRED at standard tier

MARKETPLACE_REQUIRED = {"name", "description"}
# Tracking + governance fields that marketplace listings benefit from.
# These are not "polish" — they are how a serious marketplace operates:
#   - author    : who maintains it, who to contact
#   - version   : downstream consumers can pin; upgrades are visible
#   - license   : legal clarity for installers
#   - allowed-tools : security best practice (Anthropic doc itself promotes this)
#   - tags      : discovery filtering
#   - compatibility : runtime / environment requirements (free-text, AgentSkills.io)
# All six are members of ALWAYS_REQUIRED: missing any of them at marketplace
# tier is an ERROR (SCHEMA_CHANGELOG NON-NEGOTIABLE #2). The 100-point rubric
# additionally rewards their inclusion.
MARKETPLACE_TRACKING_FIELDS = {"allowed-tools", "version", "author", "license", "compatibility", "tags"}
# Back-compat alias — old name, same set.
MARKETPLACE_RECOMMENDED = MARKETPLACE_TRACKING_FIELDS

# Backward-compat aliases (used by grading functions and external callers).
# Do not use for new code — reference STANDARD_/MARKETPLACE_ explicitly.
ENTERPRISE_RECOMMENDED = MARKETPLACE_TRACKING_FIELDS
ANTHROPIC_REQUIRED = STANDARD_REQUIRED
ENTERPRISE_REQUIRED = MARKETPLACE_REQUIRED
REQUIRED_FIELDS = STANDARD_REQUIRED

# Deprecated fields (warn but don't error).
#
# Note: `when_to_use` was previously misclassified here. Anthropic's Claude Code
# skills doc (code.claude.com/docs/en/skills, "Frontmatter reference") documents
# `when_to_use` as a valid optional field — *"Additional context for when Claude
# should invoke the skill, such as trigger phrases or example requests. Appended
# to `description` in the skill listing and counts toward the 1,536-character
# cap."* It has been moved to SKILL_FIELDS as a documented optional field.
#
# `compatible-with` is deprecated because the IS rubric originally required it
# as a closed CSV platform list with allow-list values. That field is not in any
# Anthropic or AgentSkills.io published spec. Replaced by free-text `compatibility`
# (agentskills.io/specification, max 500 chars).
#
# `mode` was an old IS-only field; replaced by `disable-model-invocation`.
DEPRECATED_FIELDS = {
    "mode": "Use `disable-model-invocation: true` instead. Not in any published spec.",
    "compatible-with": (
        "Use `compatibility` (free-text per agentskills.io/specification) instead. "
        "Example: `compatibility: Designed for Claude Code` or "
        "`compatibility: Requires Python 3.10+ and uv`. The old CSV-platform-list "
        "form was an Intent Solutions invention and is not part of any published spec."
    ),
}

# Recommended sections (best practices, not mandated by any published standard)
RECOMMENDED_SECTIONS = [
    "# ",  # title line
    "## Overview",
    "## Prerequisites",
    "## Instructions",
    "## Output",
    "## Error Handling",
    "## Examples",
    "## Resources",
]

# Backward compat aliases
ENTERPRISE_SECTIONS = RECOMMENDED_SECTIONS
REQUIRED_SECTIONS = RECOMMENDED_SECTIONS

# iel-62j — validator fairness. The RECOMMENDED_SECTIONS names above are Intent
# Solutions conventions, NOT a published standard (see the note there). External
# contributors routinely use equivalent, well-understood headings; failing them
# for the exact IS wording is unfair and off-spec. The enterprise (marketplace)
# section checks credit any of these synonyms as satisfying the corresponding
# canonical section. This credits `## Capabilities` as a *heading* only — the
# frontmatter `capabilities` field stays banned per SCHEMA_CHANGELOG
# NON-NEGOTIABLES.
SECTION_SYNONYMS = {
    "## Overview": [
        "## Summary",
        "## About",
        "## Description",
        "## What it does",
        "## Introduction",
        "## Capabilities",
        "## Purpose",
    ],
    "## Prerequisites": [
        "## Requirements",
        "## Setup",
        "## Dependencies",
        "## Before you begin",
        "## Installation",
    ],
    "## Instructions": [
        "## Usage",
        "## How to use",
        "## How it works",
        "## Steps",
        "## Workflow",
        "## Guide",
        "## Getting started",
    ],
    "## Output": [
        "## Outputs",
        "## Returns",
        "## Results",
        "## Output format",
        "## Response",
    ],
    "## Error Handling": [
        "## Errors",
        "## Troubleshooting",
        "## Failure modes",
        "## Edge cases",
        "## Limitations",
    ],
    "## Examples": [
        "## Example",
        "## Sample",
        "## Samples",
        "## Usage examples",
        "## Example usage",
    ],
    "## Resources": [
        "## References",
        "## See also",
        "## Links",
        "## Further reading",
        "## Related",
        "## Additional resources",
    ],
}

# Regex patterns
RE_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
# Shell-substitution / backtick injection in YAML scalar values.
# NLPM audit (2026-04) caught `description: $(echo "$description" | cut ...)` in
# plugins/devops/backup-strategy-implementor/commands/backup-strategy.md — these
# never evaluate, break strict YAML parsers, and trip downstream security tooling.
RE_YAML_SHELL_SUBST = re.compile(r"(?:\$\(|`)")
# Allow-listed template/substitution variables that are legitimate in NL artifacts.
# All Claude Code documented substitutions per code.claude.com/docs/en/skills
# "Available string substitutions" table.
YAML_VALUE_ALLOWED_VARS = {
    "${CLAUDE_SKILL_DIR}",
    "${CLAUDE_PLUGIN_ROOT}",
    # Portable canonical-layer spellings (blueprint 727 E3.9): canonical
    # bodies write ${SKILL_DIR}/${PLUGIN_ROOT}; the claude-code adapter emits
    # the CLAUDE_-branded forms. The anti-absolute-path posture is unchanged —
    # these are the same variables in their harness-free spelling.
    "${SKILL_DIR}",
    "${PLUGIN_ROOT}",
    "${CLAUDE_PLUGIN_DATA}",
    "${CLAUDE_SESSION_ID}",
    "${CLAUDE_EFFORT}",
    "$ARGUMENTS",
    "$0",
    "$1",
    "$2",
    "$3",
    "$4",
    "$5",
    "$6",
    "$7",
    "$8",
    "$9",
}
RE_DESCRIPTION_USE_WHEN = re.compile(r"\bUse when\b", re.IGNORECASE)
RE_DESCRIPTION_TRIGGER_WITH = re.compile(r"\bTrigger with\b", re.IGNORECASE)
RE_SKILLDIR_SCRIPTS = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/scripts/([\w\-./]+)")
RE_SKILLDIR_REFERENCES = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/references/([\w\-./]+)")
RE_SKILLDIR_ASSETS = re.compile(r"\$\{CLAUDE_SKILL_DIR\}/assets/([\w\-./]+)")
RE_RELATIVE_MD_LINK = re.compile(r"\[([^\]]*)\]\(((?!https?://|#)[^)]+)\)")
RE_FIRST_PERSON = re.compile(r"\b(I can|I will|I'm going to|I help)\b", re.IGNORECASE)
RE_SECOND_PERSON = re.compile(r"\b(You can|You should|You will)\b", re.IGNORECASE)
FORBIDDEN_WORDS = ("anthropic", "claude")
CODE_FENCE_PATTERN = re.compile(r"^\s*(```|~~~)")
HEADING_PATTERN = re.compile(r"^\s*#{1,6}\s+")
ABSOLUTE_PATH_PATTERNS = [
    (re.compile(r"/home/\w+/"), "/home/..."),
    (re.compile(r"/Users/\w+/"), "/Users/..."),
    (re.compile(r"[A-Za-z]:\\\\Users\\\\", re.IGNORECASE), "C:\\\\Users\\\\..."),
]
RE_XML_TAG = re.compile(r"[<>]")
RE_TIME_SENSITIVE = [
    re.compile(r"\b(20\d{2}[-/]\d{2}[-/]\d{2})\b"),
    re.compile(r"\b(v\d+\.\d+\.\d+)\b", re.IGNORECASE),
    re.compile(
        r"\b(as of|since|after|before) (January|February|March|April|May|June|July|August|September|October|November|December)\b",
        re.IGNORECASE,
    ),
]

# === SCHEMA REGISTRY (Single Source of Truth) ===
# Derived from Anthropic docs (code.claude.com/docs/en/skills), synced 2026-03-21

SKILL_FIELDS = {
    # === Anthropic published spec — code.claude.com/docs/en/skills "Frontmatter reference" ===
    # All fields below are documented at code.claude.com/docs/en/skills as of 2026-09-09.
    # `name` and `description` are required at every tier. The remaining Anthropic
    # fields are accepted as valid optional and validated for type/format only.
    "name": {"type": "string", "source": "anthropic", "tier": "standard"},
    "description": {"type": "string", "source": "anthropic", "tier": "standard"},
    "when_to_use": {"type": "string", "source": "anthropic", "tier": "standard"},
    "argument-hint": {"type": "string", "source": "anthropic", "tier": "standard"},
    "arguments": {"type": "string|array", "source": "anthropic", "tier": "standard"},
    "disable-model-invocation": {"type": "boolean", "source": "anthropic", "tier": "standard", "default": False},
    "user-invocable": {"type": "boolean", "source": "anthropic", "tier": "standard", "default": True},
    "allowed-tools": {"type": "string|array", "source": "anthropic", "tier": "standard"},
    # disallowed-tools added in Claude Code v2.1.152 (2026-05-27 changelog).
    # Removes tools from the model while the skill is active (security gate).
    # Same shape as allowed-tools: string (space-separated) OR YAML list.
    # Per SAK plan 031 § 14.10: recognized at IS marketplace tier; not added to
    # MARKETPLACE_TRACKING_FIELDS (it's optional security polish, not required).
    # D4 hand-authored entry preserved as audit trail; kernel shadow compares at runtime [11hl]
    "disallowed-tools": {"type": "string|array", "source": "anthropic", "tier": "standard"},
    "model": {
        "type": "string",
        "source": "anthropic",
        "tier": "standard",
        "valid": ["sonnet", "haiku", "opus", "fable", "inherit"],
    },
    "effort": {
        "type": "string",
        "source": "anthropic",
        "tier": "standard",
        "valid": ["low", "medium", "high", "xhigh", "max"],
    },
    "context": {"type": "string", "source": "anthropic", "tier": "standard", "valid": ["fork"]},
    "agent": {"type": "string", "source": "anthropic", "tier": "standard"},
    "background": {"type": "boolean", "source": "anthropic", "tier": "standard", "default": True},
    "hooks": {"type": "object", "source": "anthropic", "tier": "standard"},
    "paths": {"type": "string|array", "source": "anthropic", "tier": "standard"},
    "shell": {"type": "string", "source": "anthropic", "tier": "standard", "valid": ["bash", "powershell"]},
    # === AgentSkills.io open standard (agentskills.io/specification) ===
    # Claude Code skills follow the AgentSkills.io standard per code.claude.com.
    # Free-text, max 500 chars. Replaces the IS-invented `compatible-with` CSV list.
    "compatibility": {"type": "string", "source": "agentskills.io", "tier": "standard", "max_length": 500},
    # Arbitrary key-value mapping (e.g. metadata.version, metadata.author)
    "metadata": {"type": "object", "source": "agentskills.io", "tier": "standard"},
    "license": {"type": "string", "source": "agentskills.io", "tier": "standard"},
    # === Intent Solutions enterprise extensions (required at marketplace tier) ===
    # Top-level tracking + governance metadata. Required at marketplace tier
    # via ALWAYS_REQUIRED; missing any of these = ERROR.
    "version": {"type": "string", "source": "enterprise", "tier": "enterprise"},
    "author": {"type": "string", "source": "enterprise", "tier": "enterprise"},
    "tags": {"type": "array", "source": "enterprise", "tier": "enterprise"},
    # === Visibility fields (IS extension, schema 3.5.0) ===
    # Conditional visibility — let a skill self-declare its env / tool deps
    # so consumers (the marketplace UI, the Claude Code skill loader) can
    # hide it when prereqs are absent, and surface fallbacks when a primary
    # tool isn't available. All optional, all default to empty list, no
    # behavior change for existing skills.
    "requires_env": {"type": "array", "source": "enterprise", "tier": "standard"},
    "requires_tools": {"type": "array", "source": "enterprise", "tier": "standard"},
    "fallback_for_env": {"type": "array", "source": "enterprise", "tier": "standard"},
    "fallback_for_tools": {"type": "array", "source": "enterprise", "tier": "standard"},
    # === Self-declared config surface (IS extension, schema 3.6.0) ===
    # Skills self-describe the secrets and config keys they consume so the
    # installer / helper can prompt the user on first run instead of letting
    # them hit a runtime error. Each entry is an object — shape validated in
    # the frontmatter checks. The companion config keys live nested under
    # `metadata.intent-solutions.config` (no separate top-level field).
    "required_environment_variables": {"type": "array", "source": "enterprise", "tier": "standard"},
    # === Deprecated alias (kept for backward compat) ===
    # Was an IS-invented field with VALID_PLATFORMS allow-list. Not in any spec.
    # Validator emits deprecation warning + migration suggestion. Still parsed so
    # existing 3,385 public-repo SKILL.md files keep passing.
    "compatible-with": {"type": "string", "source": "deprecated-is-extension", "tier": "standard"},
}

AGENT_FIELDS = {
    "name": {"type": "string", "source": "anthropic"},
    "description": {"type": "string", "source": "anthropic"},
    # model — documented aliases sonnet/opus/haiku/fable plus `inherit`, or a full
    # Claude model ID. `fable` added 2026-06-17 to match the kernel agent-definition enum
    # (@intentsolutions/core schemas/authoring/v1/upstream-base/agent-definition.v1.json)
    # and code.claude.com/docs/en/sub-agents § "Choose a model".
    "model": {"type": "string", "source": "anthropic"},
    "effort": {"type": "string", "source": "anthropic", "valid": ["low", "medium", "high", "xhigh", "max"]},
    "maxTurns": {"type": "integer", "source": "anthropic"},
    # tools — the kernel narrows the wire form to a YAML array of tool identifiers,
    # but code.claude.com/docs/en/sub-agents documents a comma-separated string and
    # the existing public corpus uses both. Accept string|array (tolerant) so the
    # required-presence gate does not also force a mechanical re-typing of every
    # agent; an agent that pre-approves zero tools may declare an empty array.
    "tools": {"type": "string|array", "source": "anthropic"},
    "disallowedTools": {"type": "array", "source": "anthropic"},
    "skills": {"type": "array", "source": "anthropic"},
    # Current upstream form is a list whose entries are string references or
    # one-key inline server definitions. Accept an object too for compatibility
    # with existing IS standalone-agent templates that used an empty map.
    "mcpServers": {"type": "object|array", "source": "anthropic"},
    "hooks": {"type": "object", "source": "anthropic"},
    "memory": {"type": "string", "source": "anthropic", "valid": ["user", "project", "local"]},
    "background": {"type": "boolean", "source": "anthropic"},
    "isolation": {"type": "string", "source": "anthropic", "valid": ["worktree"]},
    "permissionMode": {
        "type": "string",
        "source": "anthropic",
        "valid": ["default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan", "manual"],
    },
    # Spec fields confirmed against code.claude.com/docs/en/sub-agents (snapshot at
    # ~/.claude/skills/agent-creator/references/anthropic-sub-agents-spec.md, captured
    # 2026-05-08). Both `color` and `initialPrompt` are documented Anthropic optional
    # fields; previously misclassified as DEPRECATED_AGENT_FIELDS / unknown.
    "color": {
        "type": "string",
        "source": "anthropic",
        "valid": ["red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"],
    },
    "initialPrompt": {"type": "string", "source": "anthropic"},
    # Added in Claude Code v2.1.248. Only cacheTtl is currently interpreted;
    # other keys are ignored by Claude Code and therefore surfaced as warnings.
    "experimental": {"type": "object", "source": "anthropic"},
    # === Intent Solutions enterprise tracking fields (required at every tier for agents) ===
    # Net-new IS-required tracking trio mirrored from the kernel agent-definition
    # is-overlay (@intentsolutions/core schemas/authoring/v1/is-overlay/agent-
    # definition.v1.json). Registered here so they type-check and do not trip the
    # unknown-field warning; their required-presence is enforced via
    # AGENT_ALWAYS_REQUIRED below.
    "version": {"type": "string", "source": "enterprise"},
    "author": {"type": "string", "source": "enterprise"},
    "tags": {"type": "array", "source": "enterprise"},
}

# === Kernel floor: the agent-definition required set (8 fields) ==================
# Source of truth: @intentsolutions/core schemas/authoring/v1/
# agent-definition.schema.json — the union of the upstream-base floor
# [name, description] and the is-overlay required delta
# [tools, model, color, version, author, tags]. When the kernel package is
# installed the validator derives this floor at runtime (load_kernel_agent_required);
# this inline mirror is the fallback for clones without the kernel vendored.
# TODO(kernel-cutover): consume the kernel agent schema as the sole source once the
# DR-049 consumer-cutover bead lands (epic bd_000-projects-9k5h).
AGENT_ALWAYS_REQUIRED = {"name", "description", "tools", "model", "color", "version", "author", "tags"}

# === Enterprise "flesh out the entire spec" required set (Jeremy 2026-06-17) ======
# The IS standard requires every authored agent to carry the full SUPPORTED live
# field surface — "empties and all" — so the upgrade levers are always visible on
# the file. This is the IS-marketplace-strict layer sitting ON TOP of the kernel
# floor (the same pattern skills use). Enforced as ERRORS at every tier (agents are
# NOT tier-gated).
#
# Two spec realities shape the set:
#   1. Optional tuning fields (effort, maxTurns, memory, isolation,
#      initialPrompt, experimental) are carried as a commented "upgrade levers"
#      block in the body template — visible, not parser-required. See
#      AGENT_UPGRADE_LEVERS.
#   2. hooks / mcpServers / permissionMode are configured at the PLUGIN level and
#      ignored on a plugin agent, so they are required only on STANDALONE agents.
#
# Live-required for ALL agents (kernel floor ∪ these): adds the no-op-empty fields
# disallowedTools ([]), skills ([]), background (false). => 11 fields on a plugin agent.
AGENT_ENTERPRISE_LIVE_COMMON = {"disallowedTools", "skills", "background"}
# Live-required for STANDALONE agents only (plugin agents don't support these):
# hooks ({}), mcpServers ([]), permissionMode (default). => 14 live-required
# fields total on a standalone agent.
AGENT_STANDALONE_ONLY_REQUIRED = {"hooks", "mcpServers", "permissionMode"}
# The "upgrade levers" carried as a commented block in every authored agent's
# body — present so they're a standing menu of how to tune the agent, but not
# parser-required because defaults should remain authoritative until selected.
AGENT_UPGRADE_LEVERS = ("effort", "maxTurns", "memory", "isolation", "initialPrompt", "experimental")

# Fields NOT supported in plugin agents (silently ignored by runtime)
AGENT_PLUGIN_RESTRICTED = {"hooks", "mcpServers", "permissionMode"}

# Fields that are NOT in any canonical spec — ERROR if found.
# Promoted from DEPRECATED_AGENT_FIELDS (warn) to ERROR on 2026-06-17 as part of the
# kernel-strict flip: the IS-invented activation/classification fields were never in
# the Anthropic sub-agents spec nor the kernel agent-definition contract, and
# `compatible-with` / `when_to_use` are banned by the kernel deprecationRegistry
# universal fold (@intentsolutions/core marketplace-tier.schema.json $defs/
# deprecationRegistry). A serious marketplace gate rejects them, not warns.
INVALID_AGENT_FIELDS = {
    "capabilities": "Non-standard field. Not in the Anthropic sub-agents spec nor the kernel agent-definition contract. Remove it.",
    "expertise_level": "Non-standard field. Not in the Anthropic sub-agents spec nor the kernel agent-definition contract. Remove it.",
    "activation_priority": "Non-standard field. Not in the Anthropic sub-agents spec nor the kernel agent-definition contract. Remove it.",
    "activation_triggers": "Non-standard field. Not in the Anthropic sub-agents spec nor the kernel agent-definition contract. Encode triggers in `description` instead.",
    "type": "Non-standard field. Not in the Anthropic sub-agents spec nor the kernel agent-definition contract. Remove it.",
    "category": "Non-standard field. Not in the Anthropic sub-agents spec nor the kernel agent-definition contract. Remove it.",
    "compatible-with": "Deprecated (kernel deprecationRegistry). Not a sub-agents field; remove it.",
    "when_to_use": "Deprecated (kernel deprecationRegistry). For agents, fold the trigger phrasing into `description` instead.",
}

# Kept for backward compatibility (external callers / the compliance-DB rollup).
# Empty now that every former entry is a hard error in INVALID_AGENT_FIELDS.
DEPRECATED_AGENT_FIELDS = {}

# Truly-invalid fields are now empty: `compatibility` and `metadata` are documented
# optional fields per agentskills.io/specification. `when_to_use` and `mode` moved
# to DEPRECATED_FIELDS (warn + migration message rather than hard error). This
# keeps 3,385 existing public-repo SKILL.md files passing while we migrate at
# our own pace via batch-remediate.py --migrate-compatible-with.
INVALID_SKILL_FIELDS = {}

# plugin.json (.claude-plugin/plugin.json) — the Anthropic plugin manifest.
# Source of truth: https://code.claude.com/docs/en/plugins-reference
#   § "Plugin manifest schema". `name` is the only required field; everything
# else is optional. Kept in sync with upstream GA fields — see SCHEMA_CHANGELOG
# 3.12.0 (the manifest gained displayName/defaultEnabled/dependencies/userConfig/
# channels/$schema/experimental as GA; this allowlist had only the pre-GA 15).
PLUGIN_JSON_FIELDS = {
    # — Metadata —
    "name": {"type": "string", "required": True},
    "displayName": {"type": "string"},  # GA (Claude Code v2.1.143+) — human-readable picker name
    "version": {"type": "string"},
    "description": {"type": "string"},
    "author": {"type": "object"},
    "homepage": {"type": "string"},
    "repository": {"type": "string"},
    "license": {"type": "string"},
    "keywords": {"type": "array"},
    "$schema": {"type": "string"},  # GA — JSON Schema URL for editor autocomplete (ignored at load)
    "metadata": {
        "type": "object"
    },  # IS-overlay extension (kernel authoring/v2 plugin-manifest is-overlay) — adopted via the L2 kernel shadow (692-AA-AACR)
    # — Component paths —
    "commands": {"type": "string|array"},
    "agents": {"type": "string|array"},
    "skills": {"type": "string|array"},
    "hooks": {"type": "string|array|object"},
    "mcpServers": {"type": "string|array|object"},
    "outputStyles": {"type": "string|array"},
    "lspServers": {"type": "string|array|object"},
    # — Behavior / config (GA) —
    "defaultEnabled": {"type": "boolean"},  # GA (v2.1.154+) — enabled by default absent a user preference
    "userConfig": {"type": "object"},  # GA — user-configurable values prompted at enable time
    "channels": {"type": "array"},  # GA — message-channel declarations bound to MCP servers
    "dependencies": {"type": "array"},  # GA — required plugins w/ optional semver constraints
    # — Experimental (schema may change between releases): experimental.{themes,monitors} —
    "experimental": {"type": "object"},
}

# Intent Solutions enterprise / marketplace standard: 8 required fields.
# Missing any of these = ERROR at marketplace tier (TIER_MARKETPLACE).
# Standard tier is more permissive — see field-presence logic in validate_frontmatter.
#
# This is the canonical IS standard, restored 2026-04-28. The brief experiment with
# reducing this to {name, description} (schema 3.0–3.1) is reverted; the only kept
# change is `compatible-with` → `compatibility` (free-text per agentskills.io).
# D4 hand-authored entry preserved as audit trail; kernel shadow compares at runtime [11hl]
ALWAYS_REQUIRED = {"name", "description", "allowed-tools", "version", "author", "license", "compatibility", "tags"}

# Conditional fields: relevant when other fields are set.
# Triggers a "missing conditional field" warning at marketplace tier when the
# condition is True but the field is absent. Never errors.
#
# Rules calibrated to Anthropic's documented defaults at
# code.claude.com/docs/en/skills:
#   - `agent` defaults to `general-purpose` when `context: fork` is set
#     ("If omitted, uses general-purpose"). NOT required — recommended only
#     when the engineer wants a non-default agent type.
#   - `context` is only meaningful when `agent` is intentionally set;
#     setting `agent` without `context: fork` makes the agent field a no-op.
#   - `argument-hint` is shown in the `/` autocomplete menu, which only
#     applies when `user-invocable: true` (the default). `disable-model-
#     invocation: true` doesn't affect the / menu — only Claude's auto-load,
#     so it should NOT be in this conditional.
CONDITIONAL_FIELDS = {
    "context": lambda fm: fm.get("agent") is not None,
    "argument-hint": lambda fm: fm.get("user-invocable", True),
}

# Facelift opportunities: optional fields that could improve the skill
FACELIFT_FIELDS = {
    "model": "Setting an explicit model prevents unexpected behavior when session model changes",
    "effort": "Setting effort level optimizes reasoning for this skill's complexity",
}


# === KERNEL SHADOW (DR-049 — advisory, never gating) ====================
# The Spec Authority Kernel (@intentsolutions/core, pinned exactly in
# package.json) publishes the machine-spec skill-frontmatter contract at
# schemas/authoring/v1/. The effective required set is the union of the
# upstream-base layer's `required` (agentskills.io standardFloor) and the
# is-overlay layer's `required` (the IS marketplace promotions/inventions).
# At runtime the validator can COMPARE that derived set against the
# hand-authored ALWAYS_REQUIRED above (which stays AUTHORITATIVE — this is
# a shadow, not a cutover; the flip is gated on the DR-049 soak). [11hl]

_KERNEL_SCHEMA_DIR = (
    Path(__file__).resolve().parents[1] / "node_modules" / "@intentsolutions" / "core" / "schemas" / "authoring" / "v1"
)


def load_kernel_required() -> Dict[str, Any]:
    """Existence-guarded load of the kernel's skill-frontmatter contract.

    Reads the composed schema's two authored layers (upstream-base +
    is-overlay) and derives the effective required set + the combined
    property surface. Returns a dict:
      {"available": False, "reason": str}                       when the kernel
                                                                 is not installed
      {"available": True, "required": set, "properties": set,
       "schema_dir": str}                                        on success
    Never raises — a missing/corrupt kernel degrades to available=False.
    """
    composition = _KERNEL_SCHEMA_DIR / "skill-frontmatter.schema.json"
    base = _KERNEL_SCHEMA_DIR / "upstream-base" / "skill-frontmatter.v1.json"
    overlay = _KERNEL_SCHEMA_DIR / "is-overlay" / "skill-frontmatter.v1.json"
    if not (composition.exists() and base.exists() and overlay.exists()):
        return {
            "available": False,
            "reason": (
                "kernel schemas not found under node_modules/@intentsolutions/core/"
                "schemas/authoring/v1 (run pnpm install)"
            ),
        }
    try:
        base_doc = json_module.loads(base.read_text(encoding="utf-8"))
        overlay_doc = json_module.loads(overlay.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"available": False, "reason": f"kernel schema load failed: {e}"}
    required = set(base_doc.get("required", []) or []) | set(overlay_doc.get("required", []) or [])
    properties = set(base_doc.get("properties", {}) or {}) | set(overlay_doc.get("properties", {}) or {})
    return {
        "available": True,
        "required": required,
        "properties": properties,
        "schema_dir": "node_modules/@intentsolutions/core/schemas/authoring/v1",
    }


def load_kernel_agent_required() -> Optional[set]:
    """Derive the effective required set for the agent-definition contract.

    Reads the kernel agent-definition schema's two authored layers
    (upstream-base + is-overlay) and returns the union of their `required`
    arrays — the canonical 8-field agent required set. Returns None (degrade to
    the inline AGENT_ALWAYS_REQUIRED mirror) when the kernel is not installed or
    is unreadable. Never raises.

    Authority: @intentsolutions/core schemas/authoring/v1/agent-definition.schema.json
    (composition of upstream-base/agent-definition.v1.json + is-overlay/
    agent-definition.v1.json). Kept aligned with the skill-frontmatter shadow
    machinery above; agents are NOT tier-gated — this set errors at every tier.
    """
    base = _KERNEL_SCHEMA_DIR / "upstream-base" / "agent-definition.v1.json"
    overlay = _KERNEL_SCHEMA_DIR / "is-overlay" / "agent-definition.v1.json"
    if not (base.exists() and overlay.exists()):
        return None
    try:
        base_doc = json_module.loads(base.read_text(encoding="utf-8"))
        overlay_doc = json_module.loads(overlay.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    required = set(base_doc.get("required", []) or []) | set(overlay_doc.get("required", []) or [])
    return required or None


# L2 consumer-cutover (692-AA-AACR § 0.5). The plugin-manifest contract is read
# from authoring/V2, not v1: the v1 fold is an early minimal capture (~10 metadata
# fields), while v2 is the current deep-capture carrying the full GA surface
# (displayName/defaultEnabled/dependencies/userConfig/channels/$schema/experimental
# + all component-path fields). Pinning the plugin shadow to v2 is the
# "promote authoring/v2 canonical" path; needs @intentsolutions/core>=0.9.0.
_KERNEL_SCHEMA_DIR_V2 = (
    Path(__file__).resolve().parents[1] / "node_modules" / "@intentsolutions" / "core" / "schemas" / "authoring" / "v2"
)


def load_kernel_plugin_fields() -> Dict[str, Any]:
    """Existence-guarded load of the kernel's CURRENT (v2) plugin-manifest field
    surface — the upstream-base ∪ is-overlay property sets. Returns:
      {"available": False, "reason": str}                       kernel/v2 absent
      {"available": True, "properties": set, "required": set, "schema_dir": str}
    Never raises — a missing/corrupt kernel degrades to available=False.
    """
    base = _KERNEL_SCHEMA_DIR_V2 / "upstream-base" / "plugin-manifest.v2.json"
    overlay = _KERNEL_SCHEMA_DIR_V2 / "is-overlay" / "plugin-manifest.v2.json"
    if not base.exists():
        return {
            "available": False,
            "reason": (
                "kernel plugin-manifest v2 schema not found under node_modules/"
                "@intentsolutions/core/schemas/authoring/v2 — run pnpm install "
                "(needs @intentsolutions/core>=0.9.0; the v1 plugin-manifest fold is stale)"
            ),
        }
    try:
        base_doc = json_module.loads(base.read_text(encoding="utf-8"))
        overlay_doc = json_module.loads(overlay.read_text(encoding="utf-8")) if overlay.exists() else {}
    except (OSError, ValueError) as e:
        return {"available": False, "reason": f"kernel plugin-manifest schema load failed: {e}"}
    properties = set(base_doc.get("properties", {}) or {}) | set(overlay_doc.get("properties", {}) or {})
    required = set(base_doc.get("required", []) or []) | set(overlay_doc.get("required", []) or [])
    return {
        "available": True,
        "properties": properties,
        "required": required,
        "schema_dir": "node_modules/@intentsolutions/core/schemas/authoring/v2",
    }


def kernel_shadow_report() -> Dict[str, Any]:
    """Build the kernel-shadow comparison block (machine-readable).

    Compares the kernel-derived effective required set against the
    hand-authored ALWAYS_REQUIRED, and the kernel property surface against
    the hand-authored `disallowed-tools` registry entry. ALWAYS_REQUIRED
    stays authoritative; this block only surfaces drift.
    """
    kernel = load_kernel_required()
    report: Dict[str, Any] = {
        "mode": "shadow-advisory",
        "kernel_package": "@intentsolutions/core",
        "schema": "authoring/v1/skill-frontmatter (upstream-base + is-overlay)",
        "available": kernel["available"],
    }
    if not kernel["available"]:
        report["note"] = kernel["reason"]
        return report
    hand = set(ALWAYS_REQUIRED)
    kreq = kernel["required"]
    report["hand_authored_always_required"] = sorted(hand)
    report["kernel_effective_required"] = sorted(kreq)
    report["required_match"] = hand == kreq
    report["required_only_in_hand_authored"] = sorted(hand - kreq)
    report["required_only_in_kernel"] = sorted(kreq - hand)
    # disallowed-tools shadow: the hand-authored SKILL_FIELDS entry is
    # D4-preserved; report whether the kernel property surface carries it yet.
    report["disallowed_tools"] = {
        "in_hand_authored_registry": "disallowed-tools" in SKILL_FIELDS,
        "in_kernel_properties": "disallowed-tools" in kernel["properties"],
        "match": ("disallowed-tools" in SKILL_FIELDS) == ("disallowed-tools" in kernel["properties"]),
    }
    # L2 consumer-cutover (692-AA-AACR § 0.5): shadow the hand-maintained
    # PLUGIN_JSON_FIELDS against the kernel's CURRENT (v2) plugin-manifest field
    # surface, so the next upstream plugin-manifest field the kernel captures is
    # CAUGHT here instead of needing a hand-patch (the exact failure mode that
    # produced schema 3.12.0). Advisory — PLUGIN_JSON_FIELDS stays authoritative
    # until the DR-049 flip; this only surfaces drift. `stale_missing_from_hand_authored`
    # is the load-bearing signal: a kernel field we lack means we've gone stale.
    pj_kernel = load_kernel_plugin_fields()
    plugin_block: Dict[str, Any] = {
        "schema": "authoring/v2/plugin-manifest (upstream-base + is-overlay)",
        "available": pj_kernel["available"],
    }
    if pj_kernel["available"]:
        hand_pj = set(PLUGIN_JSON_FIELDS.keys())
        kpj = pj_kernel["properties"]
        plugin_block["hand_authored_fields"] = sorted(hand_pj)
        plugin_block["kernel_fields"] = sorted(kpj)
        plugin_block["fields_match"] = hand_pj == kpj
        plugin_block["stale_missing_from_hand_authored"] = sorted(kpj - hand_pj)
        plugin_block["only_in_hand_authored"] = sorted(hand_pj - kpj)
    else:
        plugin_block["note"] = pj_kernel["reason"]
    report["plugin_manifest"] = plugin_block
    return report


def print_kernel_shadow(report: Dict[str, Any]) -> None:
    """Human-readable startup print for --kernel-shadow (advisory only)."""
    prefix = "[kernel-shadow]"
    if not report["available"]:
        print(f"{prefix} NOTE: {report['note']} — shadow comparison skipped", file=sys.stderr)
        return
    if report["required_match"]:
        print(
            f"{prefix} NOTE: hand-authored ALWAYS_REQUIRED matches the kernel effective "
            f"required set ({len(report['kernel_effective_required'])} fields)",
            file=sys.stderr,
        )
    else:
        print(
            f"{prefix} WARNING: hand-authored ALWAYS_REQUIRED differs from the kernel "
            f"effective required set — only-in-hand-authored: "
            f"{report['required_only_in_hand_authored'] or 'none'}; only-in-kernel: "
            f"{report['required_only_in_kernel'] or 'none'} "
            f"(hand-authored set stays authoritative; surface this delta per DR-049)",
            file=sys.stderr,
        )
    dt = report["disallowed_tools"]
    if dt["match"]:
        print(f"{prefix} NOTE: 'disallowed-tools' presence agrees between registry and kernel", file=sys.stderr)
    else:
        print(
            f"{prefix} INFO: 'disallowed-tools' is in the hand-authored registry but not in the "
            f"kernel base+overlay property surface (expected until the kernel vendors the "
            f"2026-05-27 Claude Code field; hand-authored entry stays authoritative)"
            if dt["in_hand_authored_registry"] and not dt["in_kernel_properties"]
            else f"{prefix} WARNING: 'disallowed-tools' is in the kernel property surface but missing "
            f"from the hand-authored registry — add it to SKILL_FIELDS",
            file=sys.stderr,
        )
    # L2 plugin-manifest shadow (692-AA-AACR § 0.5).
    pj = report.get("plugin_manifest", {})
    if not pj.get("available"):
        print(
            f"{prefix} NOTE: plugin-manifest shadow skipped — {pj.get('note', 'kernel v2 unavailable')}",
            file=sys.stderr,
        )
    elif pj.get("fields_match"):
        print(
            f"{prefix} NOTE: PLUGIN_JSON_FIELDS matches the kernel v2 plugin-manifest "
            f"surface ({len(pj.get('kernel_fields', []))} fields) — plugin.json validator is current",
            file=sys.stderr,
        )
    else:
        stale = pj.get("stale_missing_from_hand_authored") or []
        extra = pj.get("only_in_hand_authored") or []
        if stale:
            print(
                f"{prefix} WARNING: PLUGIN_JSON_FIELDS is STALE vs the kernel v2 plugin-manifest "
                f"surface — missing {stale}. The kernel captured these upstream fields; add them "
                f"to PLUGIN_JSON_FIELDS (this is the drift that used to require a hand-patch).",
                file=sys.stderr,
            )
        if extra:
            print(
                f"{prefix} INFO: PLUGIN_JSON_FIELDS carries fields not in the kernel v2 surface: "
                f"{extra} (IS extensions or ahead-of-kernel — expected for e.g. 'metadata')",
                file=sys.stderr,
            )


def detect_component(path: Path) -> tuple:
    """Auto-detect component type AND context.
    Returns: (component_type, context)
    - component_type: 'skill', 'agent', 'command', 'plugin', 'unknown'
    - context: 'plugin', 'standalone', 'unknown'
    """
    component = "unknown"

    def find_plugin_root(p: Path):
        for parent in [p] + list(p.parents):
            if (parent / ".claude-plugin" / "plugin.json").exists():
                return parent
        return None

    plugin_root = find_plugin_root(path)
    context = "plugin" if plugin_root else "standalone"

    if path.is_dir():
        if (path / ".claude-plugin" / "plugin.json").exists():
            component = "plugin"
        elif (path / "SKILL.md").exists():
            component = "skill"
    elif path.name == "SKILL.md":
        component = "skill"
    elif path.parent.name == "agents":
        component = "agent"
    elif path.parent.name == "commands":
        component = "command"

    return (component, context)


# OPTIONAL_FIELDS: all fields recognized by the validator (from schema registry + deprecated)
# Used for unknown-field detection. Defined here after SKILL_FIELDS is available.
OPTIONAL_FIELDS = set(SKILL_FIELDS.keys()) | set(INVALID_SKILL_FIELDS.keys()) | set(DEPRECATED_FIELDS.keys())

# Defaults
DEFAULT_AUTHOR = "Jeremy Longshore <jeremy@intentsolutions.io>"
DEFAULT_LICENSE = "MIT"

# Skill list token budget (Lee Han Chung deep dive): total descriptions are aggregated.
# NOTE: This repo hosts many skills; the "installed set" varies by user/workflow.
# This check is optional via --check-description-budget.
TOTAL_DESCRIPTION_BUDGET_WARN = 12_000
TOTAL_DESCRIPTION_BUDGET_ERROR = 15_000


# === INTENT SOLUTIONS 100-POINT GRADING RUBRIC ===
#
# Based on:
# - Anthropic Official Best Practices (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
# - Lee Han Chung Deep Dive (leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
# - Intent Solutions production grading at scale
#
# Grade Scale:
#   A (90-100): Production-ready
#   B (80-89):  Good, minor improvements needed
#   C (70-79):  Adequate, has gaps
#   D (60-69):  Needs significant work
#   F (<60):    Major revision required


def calculate_grade(score: int) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def score_progressive_disclosure(path: Path, body: str, fm: dict) -> dict:
    """
    Progressive Disclosure Architecture (30 pts max)
    - Token Economy (10): SKILL.md line count
    - Layered Structure (10): Has references/ directory with content
    - Reference Depth (5): References are one level deep only
    - Navigation Signals (5): Well-structured sections for navigability
    """
    breakdown = {}
    lines = len(body.splitlines())
    skill_dir = path.parent

    # Token Economy (10 pts) - Per Anthropic: SKILL.md should be concise
    # ≤150=10, 151-300=7, 301-500=4, >500=0
    if lines <= 150:
        breakdown["token_economy"] = (10, "Excellent: ≤150 lines")
    elif lines <= 300:
        breakdown["token_economy"] = (7, f"Good: {lines} lines (target ≤150)")
    elif lines <= 500:
        breakdown["token_economy"] = (4, f"Acceptable: {lines} lines (target ≤150)")
    else:
        breakdown["token_economy"] = (0, f"Too long: {lines} lines (target ≤150)")

    # Layered Structure (10 pts) - Has references/ or resources/ with markdown files
    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        refs_dir = skill_dir / "resources"  # Accept resources/ as alternative
    if refs_dir.exists():
        ref_files = list(refs_dir.glob("*.md"))
        if ref_files:
            breakdown["layered_structure"] = (10, f"Has references/ with {len(ref_files)} files")
        else:
            breakdown["layered_structure"] = (3, "references/ exists but empty")
    else:
        # Penalty scales with file length - short files don't need references
        if lines <= 100:
            breakdown["layered_structure"] = (8, "No references/ (acceptable for short skill)")
        elif lines <= 200:
            breakdown["layered_structure"] = (4, "No references/ (should extract content)")
        else:
            breakdown["layered_structure"] = (0, "No references/ (long skill needs extraction)")

    # Info note: dynamic injection + references/ = sophisticated progressive disclosure
    has_dynamic_injection = bool(re.search(r"(?m)^!\`[^`]+\`\s*$", body))
    if has_dynamic_injection and refs_dir.exists() and refs_dir.glob("*.md"):
        score, msg = breakdown["layered_structure"]
        breakdown["layered_structure"] = (score, msg + " + dynamic injection")

    # Reference Depth (5 pts) - One level deep only (no nested subdirs in references/)
    if refs_dir.exists():
        nested_dirs = [d for d in refs_dir.iterdir() if d.is_dir()]
        if not nested_dirs:
            breakdown["reference_depth"] = (5, "References are flat (good)")
        else:
            breakdown["reference_depth"] = (2, f"Nested dirs in references/: {len(nested_dirs)}")
    else:
        breakdown["reference_depth"] = (5, "N/A - no references/")

    # Navigation Signals (5 pts) - Well-structured sections for navigability
    # Note: No published standard mandates specific sections. Scoring is softened
    # to reflect that these are best practices, not requirements.
    sections = len(re.findall(r"(?m)^##\s+", body))
    if lines <= 100:
        breakdown["navigation_signals"] = (5, "Short file, navigation implicit")
    elif sections >= 7:
        breakdown["navigation_signals"] = (5, f"Well-structured: {sections} section headers")
    elif sections >= 4:
        breakdown["navigation_signals"] = (4, f"Adequate structure: {sections} sections (7+ ideal)")
    elif sections >= 2:
        breakdown["navigation_signals"] = (2, f"Minimal structure: {sections} sections (4+ recommended)")
    else:
        breakdown["navigation_signals"] = (0, f"Poor structure: only {sections} sections")

    total = sum(v[0] for v in breakdown.values())
    return {"score": total, "max": 30, "breakdown": breakdown}


def score_ease_of_use(path: Path, body: str, fm: dict) -> dict:
    """
    Ease of Use (25 pts max)
    - Metadata Quality (10): Complete, well-formed frontmatter
    - Discoverability (6): Has trigger phrases, "Use when"
    - Terminology Consistency (4): Consistent naming
    - Workflow Clarity (5): Clear step-by-step instructions
    """
    breakdown = {}
    desc = str(fm.get("description", "")).lower()

    # Metadata Quality (10 pts)
    meta_score = 0
    meta_notes = []
    if fm.get("name"):
        meta_score += 2
    else:
        meta_notes.append("missing name")
    if fm.get("description") and len(str(fm.get("description", ""))) >= 50:
        meta_score += 3
    else:
        meta_notes.append("description too short")
    if fm.get("version"):
        meta_score += 2
    else:
        meta_notes.append("missing version")
    if fm.get("allowed-tools"):
        meta_score += 2
    else:
        meta_notes.append("missing allowed-tools")
    if fm.get("author") and "@" in str(fm.get("author", "")):
        meta_score += 1
    if fm.get("tags") and isinstance(fm.get("tags"), list) and len(fm["tags"]) > 0:
        meta_score += 1
    else:
        meta_notes.append("missing tags")
    # Accept either `compatibility` (current spec) or legacy `compatible-with`
    # (deprecated alias) for credit, but don't reward both stacked.
    if fm.get("compatibility") or fm.get("compatible-with"):
        meta_score += 1
    else:
        meta_notes.append("missing compatibility")
    meta_score = min(meta_score, 10)
    breakdown["metadata_quality"] = (meta_score, ", ".join(meta_notes) if meta_notes else "Complete metadata")

    # Discoverability (6 pts) — trigger quality assessment
    disc_score = 0
    disc_notes = []
    if "use when" in desc:
        disc_score += 2
        disc_notes.append("has 'Use when'")
    if "trigger with" in desc or "trigger phrase" in desc:
        disc_score += 2
        disc_notes.append("has trigger phrases")
    # Bonus: description contains action verbs that help model match intent
    trigger_verbs = [
        "analyze",
        "audit",
        "build",
        "check",
        "create",
        "debug",
        "deploy",
        "detect",
        "fix",
        "generate",
        "implement",
        "manage",
        "monitor",
        "optimize",
        "review",
        "scan",
        "test",
        "validate",
    ]
    verb_matches = [v for v in trigger_verbs if v in desc]
    if len(verb_matches) >= 2:
        disc_score += 1
        disc_notes.append(f"action verbs: {', '.join(verb_matches[:3])}")
    # Bonus: description length in sweet spot for matching (50-300 chars)
    desc_len = len(str(fm.get("description", "")))
    if 50 <= desc_len <= 300:
        disc_score += 1
        disc_notes.append("description length in trigger sweet spot")
    disc_score = min(disc_score, 6)
    if not disc_notes:
        disc_notes.append("missing discovery cues")
    breakdown["discoverability"] = (disc_score, ", ".join(disc_notes))

    # Terminology Consistency (4 pts)
    # Check for consistent naming patterns in the skill
    name = str(fm.get("name", ""))
    folder = path.parent.name
    term_score = 4  # Start with full score
    term_notes = []
    if name and name != folder:
        term_score -= 2
        term_notes.append("name differs from folder")
    # Check for mixed case in description
    if any(w.isupper() and len(w) > 3 for w in str(fm.get("description", "")).split()):
        term_score -= 1
        term_notes.append("inconsistent casing")
    breakdown["terminology"] = (max(0, term_score), ", ".join(term_notes) if term_notes else "Consistent terminology")

    # Workflow Clarity (5 pts)
    workflow_score = 0
    workflow_notes = []
    # Check for numbered steps
    if re.search(r"(?m)^\s*1\.\s+", body):
        workflow_score += 3
        workflow_notes.append("has numbered steps")
    # Check for clear section headers
    section_count = len(re.findall(r"(?m)^##\s+", body))
    if section_count >= 5:
        workflow_score += 2
        workflow_notes.append(f"{section_count} sections")
    elif section_count >= 3:
        workflow_score += 1
        workflow_notes.append(f"{section_count} sections (add more)")
    if not workflow_notes:
        workflow_notes.append("unclear workflow")
    breakdown["workflow_clarity"] = (workflow_score, ", ".join(workflow_notes))

    total = sum(v[0] for v in breakdown.values())
    return {"score": total, "max": 25, "breakdown": breakdown}


def score_utility(path: Path, body: str, fm: dict) -> dict:
    """
    Utility (20 pts max)
    - Problem Solving Power (8): Clear use cases, practical value
    - Degrees of Freedom (2): Flexible, configurable
    - Feedback Loops (4): Error handling, validation
    - Examples & Templates (3): Has working examples
    - Content Density (3): Word count in body (150+ words for substance)
    """
    breakdown = {}
    body_lower = body.lower()

    # Problem Solving Power (8 pts)
    problem_score = 0
    problem_notes = []
    # Check for Overview section with substance
    if "## overview" in body_lower:
        overview_match = re.search(r"## overview\s*\n(.*?)(?=\n##|\Z)", body, re.IGNORECASE | re.DOTALL)
        if overview_match and len(overview_match.group(1).strip()) > 50:
            problem_score += 4
            problem_notes.append("has overview")
    # Check for Prerequisites (shows understanding of requirements)
    if "## prerequisites" in body_lower:
        problem_score += 2
        problem_notes.append("has prerequisites")
    # Check for Output section
    if "## output" in body_lower:
        problem_score += 2
        problem_notes.append("has output spec")
    if not problem_notes:
        problem_notes.append("unclear problem/solution")
    breakdown["problem_solving"] = (problem_score, ", ".join(problem_notes))

    # Degrees of Freedom (2 pts) — reduced from 5 to make room for content_density
    freedom_score = 0
    freedom_notes = []
    # Check for configuration options
    if re.search(r"(?i)(optional|configur|parameter|argument|flag|option)", body):
        freedom_score += 1
        freedom_notes.append("has options")
    # Check for multiple approaches or extensibility
    if re.search(r"(?i)(alternatively|or use|another approach|you can also|extend|customize|modify|adapt)", body):
        freedom_score += 1
        freedom_notes.append("shows alternatives/extensibility")
    if not freedom_notes:
        freedom_notes.append("rigid implementation")
    breakdown["degrees_of_freedom"] = (freedom_score, ", ".join(freedom_notes))

    # Feedback Loops (4 pts)
    feedback_score = 0
    feedback_notes = []
    if "## error handling" in body_lower:
        feedback_score += 2
        feedback_notes.append("has error handling")
    if re.search(r"(?i)(validate|verify|check|test|confirm)", body):
        feedback_score += 1
        feedback_notes.append("has validation")
    if re.search(r"(?i)(troubleshoot|debug|diagnose|fix)", body):
        feedback_score += 1
        feedback_notes.append("has troubleshooting")
    if not feedback_notes:
        feedback_notes.append("no feedback mechanisms")
    breakdown["feedback_loops"] = (feedback_score, ", ".join(feedback_notes))

    # Examples & Templates (3 pts)
    examples_score = 0
    examples_notes = []
    if "## examples" in body_lower or "**example" in body_lower:
        examples_score += 2
        examples_notes.append("has examples")
    if "```" in body:
        code_blocks = len(re.findall(r"```", body)) // 2
        if code_blocks >= 2:
            examples_score += 1
            examples_notes.append(f"{code_blocks} code blocks")
    if not examples_notes:
        examples_notes.append("no examples")
    breakdown["examples"] = (examples_score, ", ".join(examples_notes))

    # Content Density (3 pts) — based on word count in body
    body_word_count = len(body.split())
    if body_word_count < 150:
        density_score = 0
        density_note = f"thin content ({body_word_count} words, minimum 150)"
    elif body_word_count < 300:
        density_score = 1
        density_note = f"minimal content ({body_word_count} words, target 300+)"
    elif body_word_count < 500:
        density_score = 2
        density_note = f"adequate content ({body_word_count} words)"
    else:
        density_score = 3
        density_note = f"substantial content ({body_word_count} words)"
    breakdown["content_density"] = (density_score, density_note)

    total = sum(v[0] for v in breakdown.values())
    return {"score": total, "max": 20, "breakdown": breakdown}


def score_spec_compliance(path: Path, body: str, fm: dict) -> dict:
    """
    Spec Compliance (15 pts max)
    - Frontmatter Validity (5): Valid YAML, no parse errors
    - Name Conventions (4): Kebab-case, proper length
    - Description Quality (4): Proper length, no forbidden words
    - Optional Fields (2): Proper use of optional fields
    """
    breakdown = {}
    name = str(fm.get("name", ""))
    desc = str(fm.get("description", ""))

    # Frontmatter Validity (5 pts)
    fm_score = 5  # Start with full score
    fm_notes = []
    required = ALWAYS_REQUIRED
    missing = required - set(fm.keys())
    if missing:
        fm_score -= min(len(missing), 4)
        fm_notes.append(f"missing: {', '.join(missing)}")
    if not fm_notes:
        fm_notes.append("valid frontmatter")
    breakdown["frontmatter_validity"] = (max(0, fm_score), ", ".join(fm_notes))

    # Name Conventions (4 pts)
    name_score = 4
    name_notes = []
    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", name) and len(name) > 1:
        name_score -= 2
        name_notes.append("not kebab-case")
    if len(name) > 64:
        name_score -= 1
        name_notes.append("name too long")
    if name != path.parent.name:
        name_score -= 1
        name_notes.append("name/folder mismatch")
    if not name_notes:
        name_notes.append("proper naming")
    breakdown["name_conventions"] = (max(0, name_score), ", ".join(name_notes))

    # Description Quality (4 pts)
    desc_score = 4
    desc_notes = []
    if len(desc) < 50:
        desc_score -= 2
        desc_notes.append("too short")
    if len(desc) > 1024:
        desc_score -= 2
        desc_notes.append("too long")
    desc_lower = desc.lower()
    if "i can" in desc_lower or "i will" in desc_lower:
        desc_score -= 1
        desc_notes.append("uses first person")
    if "you can" in desc_lower or "you should" in desc_lower:
        desc_score -= 1
        desc_notes.append("uses second person")
    if not desc_notes:
        desc_notes.append("good description")
    breakdown["description_quality"] = (max(0, desc_score), ", ".join(desc_notes))

    # Optional Fields (2 pts)
    opt_score = 2
    opt_notes = []
    if "model" in fm:
        model = fm["model"]
        if model not in ["inherit", "sonnet", "haiku", "opus", "fable"] and not re.fullmatch(
            r"claude-[a-z0-9][a-z0-9.-]*", str(model)
        ):
            opt_score -= 1
            opt_notes.append("invalid model value")
    if not opt_notes:
        opt_notes.append("optional fields ok")
    breakdown["optional_fields"] = (opt_score, ", ".join(opt_notes))

    # Field Coverage (3 pts) — percentage of applicable fields present
    all_applicable = set(SKILL_FIELDS.keys())
    present_fields = set(fm.keys()) & all_applicable
    coverage_pct = len(present_fields) / len(all_applicable) * 100 if all_applicable else 0
    if coverage_pct >= 80:
        breakdown["field_coverage"] = (
            3,
            f"Excellent: {len(present_fields)}/{len(all_applicable)} fields ({coverage_pct:.0f}%)",
        )
    elif coverage_pct >= 60:
        breakdown["field_coverage"] = (
            2,
            f"Good: {len(present_fields)}/{len(all_applicable)} fields ({coverage_pct:.0f}%)",
        )
    elif coverage_pct >= 40:
        breakdown["field_coverage"] = (
            1,
            f"Fair: {len(present_fields)}/{len(all_applicable)} fields ({coverage_pct:.0f}%)",
        )
    else:
        breakdown["field_coverage"] = (
            0,
            f"Low: {len(present_fields)}/{len(all_applicable)} fields ({coverage_pct:.0f}%)",
        )

    total = min(sum(v[0] for v in breakdown.values()), 15)
    return {"score": total, "max": 15, "breakdown": breakdown}


def score_writing_style(path: Path, body: str, fm: dict) -> dict:
    """
    Writing Style (10 pts max)
    - Voice & Tense (4): Imperative voice, present tense
    - Objectivity (3): No first/second person in body
    - Conciseness (3): Not overly verbose
    """
    breakdown = {}

    # Voice & Tense (4 pts)
    voice_score = 4
    voice_notes = []
    # Check for imperative language (good)
    imperative_verbs = ["create", "use", "run", "execute", "configure", "set", "add", "remove", "check", "verify"]
    has_imperative = any(re.search(rf"(?m)^\s*\d+\.\s*{v}", body, re.IGNORECASE) for v in imperative_verbs)
    if not has_imperative:
        voice_score -= 2
        voice_notes.append("use imperative voice")
    if not voice_notes:
        voice_notes.append("good voice")
    breakdown["voice_tense"] = (voice_score, ", ".join(voice_notes))

    # Objectivity (3 pts)
    obj_score = 3
    obj_notes = []
    body_lower = body.lower()
    if "you should" in body_lower or "you can" in body_lower or "you will" in body_lower:
        obj_score -= 1
        obj_notes.append("has second person")
    if " i " in body_lower or "i can" in body_lower or "i'll" in body_lower:
        obj_score -= 1
        obj_notes.append("has first person")
    if not obj_notes:
        obj_notes.append("objective")
    breakdown["objectivity"] = (max(0, obj_score), ", ".join(obj_notes))

    # Conciseness (3 pts)
    conc_score = 3
    conc_notes = []
    word_count = len(body.split())
    lines = len(body.splitlines())
    if word_count > 3000:
        conc_score -= 2
        conc_notes.append(f"verbose ({word_count} words)")
    elif word_count > 2000:
        conc_score -= 1
        conc_notes.append(f"lengthy ({word_count} words)")
    if lines > 400:
        conc_score -= 1
        conc_notes.append(f"many lines ({lines})")
    if not conc_notes:
        conc_notes.append("concise")
    breakdown["conciseness"] = (max(0, conc_score), ", ".join(conc_notes))

    total = sum(v[0] for v in breakdown.values())
    return {"score": total, "max": 10, "breakdown": breakdown}


def calculate_modifiers(path: Path, body: str, fm: dict) -> dict:
    """
    Modifiers (±15 pts)
    Bonuses: gerund name, grep-friendly, exemplary examples
    Penalties: first/second person description, unnecessary TOC
    """
    modifiers = {}
    name = str(fm.get("name", ""))
    desc = str(fm.get("description", ""))

    # Bonuses (up to +5)
    # Gerund-style name (verb-ing pattern) +1
    if any(name.endswith(f"-{s}") or name.endswith(s) for s in ["ing"]):
        modifiers["gerund_name"] = (+1, "gerund-style name")

    # Grep-friendly structure (clear section markers) +1
    sections = len(re.findall(r"(?m)^##\s+", body))
    if sections >= 7:
        modifiers["grep_friendly"] = (+1, "grep-friendly structure")

    # Exemplary examples (multiple labeled examples) +2
    example_count = len(re.findall(r"(?i)\*\*example[:\s]", body))
    if example_count >= 3:
        modifiers["exemplary_examples"] = (+2, f"{example_count} labeled examples")

    # Resources section with external links +1
    if "## resources" in body.lower():
        external_links = len(re.findall(r"\[.*?\]\(https?://", body))
        if external_links >= 2:
            modifiers["external_resources"] = (+1, f"{external_links} external links")

    # Penalties (up to -5)
    # First/second person in description -2
    desc_lower = desc.lower()
    if "i can" in desc_lower or "i will" in desc_lower or "you can" in desc_lower or "you should" in desc_lower:
        modifiers["person_in_desc"] = (-2, "first/second person in description")

    # TOC wastes tokens — Anthropic spec doesn't require it, progressive disclosure does
    has_toc = bool(re.search(r"(?mi)^##?\s*(table of contents|contents|toc)\b", body))
    if has_toc:
        modifiers["unnecessary_toc"] = (-1, "TOC wastes tokens — use clear section headers instead")

    # Dynamic context injection (Anthropic spec feature) +1
    has_dynamic_injection = bool(re.search(r"(?m)^!\`[^`]+\`\s*$", body))
    if has_dynamic_injection:
        injection_count = len(re.findall(r"(?m)^!\`[^`]+\`\s*$", body))
        modifiers["dynamic_injection"] = (+1, f"Uses preprocessing injection ({injection_count} directives)")

    # XML tags in body (anti-pattern) -1
    if "<" in body and ">" in body and re.search(r"<[a-z]+>", body):
        modifiers["xml_tags"] = (-1, "XML-like tags in body")

    # === ANTI-PATTERN DETECTION (graduated penalty system) ===
    # Each detected anti-pattern reduces score by 1pt, floor at -5
    skill_dir = path.parent
    anti_patterns_found = []

    # AP1: Over-constrained — excessive MUST/NEVER/ALWAYS keywords
    constraint_words = len(re.findall(r"\b(MUST|NEVER|ALWAYS|SHALL NOT|REQUIRED)\b", body))
    if constraint_words > 15:
        anti_patterns_found.append(f"over-constrained ({constraint_words} MUST/NEVER/ALWAYS — reduces flexibility)")
    elif constraint_words > 10:
        anti_patterns_found.append(f"moderately constrained ({constraint_words} MUST/NEVER/ALWAYS)")

    # AP2: Missing trigger phrase — description lacks activation cues
    desc_lower_ap = desc.lower()
    has_trigger_cue = any(
        phrase in desc_lower_ap
        for phrase in [
            "use when",
            "use this",
            "trigger",
            "use proactively",
            "activate",
            "use for",
            "invoke when",
        ]
    )
    if not has_trigger_cue and len(desc) > 20:
        anti_patterns_found.append("missing trigger phrase in description — autonomous activation impossible")

    refs_dir = skill_dir / "references"

    # AP3: Orphan references — markdown links to files that don't exist
    if refs_dir.exists():
        orphan_refs = []
        for match in re.finditer(r"\[([^\]]*)\]\((references/[^)]+)\)", body):
            ref_target = skill_dir / match.group(2)
            if not ref_target.exists():
                orphan_refs.append(match.group(2))
        if orphan_refs:
            anti_patterns_found.append(f"orphan references: {', '.join(orphan_refs[:3])}")

    # Stub classification belongs exclusively to deterministic_stub_flags(),
    # which evaluates the complete run.  Do not reintroduce thin-content,
    # placeholder-density, or link-count guesses here: those are local
    # heuristics and disagree with the persisted Freshie is_stub verdict.

    # AP6: Ecosystem coherence — bonus for cross-referencing siblings
    has_cross_ref = bool(re.search(r"(?i)(see also|related skill|sibling|cross-reference|companion)", body))
    has_see_also_links = bool(re.search(r"\[.*?\]\(\.\./.*?/SKILL\.md\)", body))
    if has_cross_ref or has_see_also_links:
        modifiers["ecosystem_coherence"] = (+1, "cross-references sibling skills")

    # Apply graduated anti-pattern penalty: -1 per pattern, max -5
    if anti_patterns_found:
        penalty = min(len(anti_patterns_found), 5)
        modifiers["anti_pattern_penalty"] = (
            -penalty,
            f"{len(anti_patterns_found)} anti-pattern(s): {'; '.join(anti_patterns_found)}",
        )

    # Supporting files bonus: has references/ with real content +1
    if refs_dir.exists():
        ref_files = [f for f in refs_dir.glob("*.md") if f.stat().st_size > 100]
        if ref_files:
            modifiers["supporting_files"] = (+1, f"Has references/ with {len(ref_files)} substantial files")

    total = sum(v[0] for v in modifiers.values())
    # Cap modifiers at ±15
    total = max(-15, min(15, total))
    return {"score": total, "max_bonus": 8, "max_penalty": -10, "items": modifiers}


def grade_skill(path: Path, body: str, fm: dict) -> dict:
    """
    Calculate Intent Solutions 100-point grade for a skill.

    Returns dict with:
    - score: total points (0-100)
    - grade: letter grade (A-F)
    - breakdown: per-pillar scores
    """
    pda = score_progressive_disclosure(path, body, fm)
    ease = score_ease_of_use(path, body, fm)
    utility = score_utility(path, body, fm)
    spec = score_spec_compliance(path, body, fm)
    style = score_writing_style(path, body, fm)
    mods = calculate_modifiers(path, body, fm)

    base_score = pda["score"] + ease["score"] + utility["score"] + spec["score"] + style["score"]
    total_score = base_score + mods["score"]

    # Clamp to 0-100
    total_score = max(0, min(100, total_score))

    return {
        "score": total_score,
        "grade": calculate_grade(total_score),
        "breakdown": {
            "progressive_disclosure": pda,
            "ease_of_use": ease,
            "utility": utility,
            "spec_compliance": spec,
            "writing_style": style,
            "modifiers": mods,
        },
    }


# === COMMAND VALIDATION ===

# Valid categories for commands
VALID_CMD_CATEGORIES = [
    "git",
    "deployment",
    "security",
    "testing",
    "documentation",
    "database",
    "api",
    "frontend",
    "backend",
    "devops",
    "forecasting",
    "analytics",
    "migration",
    "monitoring",
    "other",
]

VALID_DIFFICULTIES = ["beginner", "intermediate", "advanced", "expert"]


def check_yaml_shell_substitution(fm: Dict[str, Any]) -> List[str]:
    """Flag shell substitutions ($(...), backticks, unguarded ${VAR}) in YAML string values.

    YAML frontmatter values are data, not Markdown: backticks do not provide
    code formatting there. They are intentionally refused as command-
    substitution-shaped text. Put commands and code-formatted paths in the
    Markdown body; keep frontmatter descriptions plain prose.

    Known-safe template vars (CLAUDE_SKILL_DIR, $ARGUMENTS, positional params)
    are allow-listed. Anything else is treated as a likely unevaluated template
    left in frontmatter by mistake — the class of bug NLPM surfaced in 2026-04.
    """
    issues: List[str] = []

    def _walk(value: Any, path: str) -> None:
        if isinstance(value, str):
            if not (RE_YAML_SHELL_SUBST.search(value) or "${" in value):
                return
            # Remove allow-listed tokens before re-checking.
            residue = value
            for tok in YAML_VALUE_ALLOWED_VARS:
                residue = residue.replace(tok, "")
            if RE_YAML_SHELL_SUBST.search(residue) or "${" in residue:
                issues.append(
                    f"[security] YAML field '{path}' contains shell substitution "
                    f"(e.g. $(...), backticks, or ${{VAR}}) that will not evaluate: "
                    f"{value!r}"
                )
        elif isinstance(value, dict):
            for k, v in value.items():
                _walk(v, f"{path}.{k}" if path else str(k))
        elif isinstance(value, list):
            for i, v in enumerate(value):
                _walk(v, f"{path}[{i}]")

    _walk(fm, "")
    return issues


def find_command_files(root: Path) -> List[Path]:
    """Find all command markdown files in plugins/."""
    results = []
    plugins_dir = root / "plugins"
    if plugins_dir.exists():
        for cmd_file in plugins_dir.rglob("commands/*.md"):
            if cmd_file.is_file():
                results.append(cmd_file)
    return results


def validate_command(path: Path) -> Dict[str, Any]:
    """Validate a command markdown file."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"fatal": f"Cannot read file: {e}"}

    # Extract frontmatter
    m = RE_FRONTMATTER.match(content)
    if not m:
        return {"fatal": "No frontmatter found"}

    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"fatal": f"Invalid YAML: {e}"}

    errors: List[str] = []
    warnings: List[str] = []

    # Surface unevaluated shell substitutions in YAML values.
    errors.extend(check_yaml_shell_substitution(fm))

    # Required: name
    if "name" not in fm:
        errors.append("[command] Missing required field: name")
    else:
        name = str(fm["name"])
        if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$", name) and len(name) > 1:
            warnings.append("[command] 'name' should be kebab-case")
        if name != path.stem:
            warnings.append(f"[command] 'name' '{name}' should match filename '{path.stem}.md'")

    # Required: description
    if "description" not in fm:
        errors.append("[command] Missing required field: description")
    else:
        desc = str(fm["description"])
        if len(desc) < 10:
            errors.append("[command] 'description' must be at least 10 characters")
        if len(desc) > 80:
            warnings.append("[command] 'description' should be 80 characters or less")

    # Optional: shortcut
    if "shortcut" in fm:
        shortcut = str(fm["shortcut"])
        if len(shortcut) < 1 or len(shortcut) > 4:
            warnings.append("[command] 'shortcut' should be 1-4 characters")
        elif not shortcut.islower():
            warnings.append("[command] 'shortcut' should be lowercase")
        elif not shortcut.isalpha():
            warnings.append("[command] 'shortcut' should contain only letters")

    # Optional: category
    if "category" in fm:
        if fm["category"] not in VALID_CMD_CATEGORIES:
            warnings.append(f"[command] Unknown category: {fm['category']}")

    # Optional: difficulty
    if "difficulty" in fm:
        if fm["difficulty"] not in VALID_DIFFICULTIES:
            warnings.append(f"[command] Unknown difficulty: {fm['difficulty']}")

    return {"errors": errors, "warnings": warnings, "type": "command"}


# === AGENT VALIDATION ===

# Mirror of AGENT_FIELDS["effort"]["valid"] (the live check). Kept in sync with the
# Anthropic effort enum — `xhigh` was added (code.claude.com/docs/en/sub-agents).
VALID_EFFORT_LEVELS = ["low", "medium", "high", "xhigh", "max"]


def find_agent_files(root: Path) -> List[Path]:
    """Find agent markdown files across all known agent surfaces.

    Scans: plugins/**/agents/, .claude/agents/, and workspace/**/agents/.
    Expansion rationale: external audit (NLPM, 2026-04) caught missing
    frontmatter in .claude/agents/ and workspace/lab/ that this validator
    previously ignored because it only scanned plugins/.
    """
    excluded_dirs = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
    results: List[Path] = []
    seen: set = set()

    def _add_agents_from(base: Path, pattern: str) -> None:
        if not base.exists():
            return
        for agent_file in base.rglob(pattern):
            if not agent_file.is_file():
                continue
            try:
                rel_parts = agent_file.relative_to(root).parts
            except ValueError:
                rel_parts = agent_file.parts
            if any(part in excluded_dirs for part in rel_parts):
                continue
            resolved = agent_file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            results.append(agent_file)

    _add_agents_from(root / "plugins", "agents/*.md")
    _add_agents_from(root / ".claude" / "agents", "*.md")
    _add_agents_from(root / "workspace", "agents/*.md")
    return results


def find_plugin_json_files(root: Path) -> List[Path]:
    """Find all plugin.json files in plugins/."""
    results = []
    plugins_dir = root / "plugins"
    if plugins_dir.exists():
        for pj_file in plugins_dir.rglob(".claude-plugin/plugin.json"):
            if pj_file.is_file():
                results.append(pj_file)
    return results


def validate_plugin_json(path: Path, strict: bool = False) -> Dict[str, Any]:
    """Validate a single plugin.json file (standalone, for batch mode).

    Unrecognized top-level fields are reported as WARNINGS by default and only
    become errors under ``strict=True`` (the ``--strict`` flag). This mirrors
    Anthropic's own ``claude plugin validate``, which "reports unrecognized
    fields as warnings, not errors … a plugin with only unrecognized-field
    warnings still passes validation and loads at runtime" (plugins-reference
    § "Unrecognized fields"), and is consistent with how this validator already
    treats unknown SKILL.md and agent fields (warn, never error). A wrong-TYPE
    field and a missing required ``name`` stay hard errors at every level —
    Anthropic fails those too.

    NON-NEGOTIABLE #7 error-vs-warning change, approved by Jeremy Longshore
    2026-06-28 (see SCHEMA_CHANGELOG 3.13.0 + the sign-off in the PR thread).
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        pj = json_module.loads(path.read_text(encoding="utf-8"))
    except json_module.JSONDecodeError as e:
        return {"errors": [f"Invalid JSON: {e}"], "warnings": []}

    if not isinstance(pj, dict):
        return {"errors": ["Must be a JSON object"], "warnings": []}

    if "name" not in pj:
        errors.append("Missing required field: 'name'")

    valid_fields = set(PLUGIN_JSON_FIELDS.keys())
    for key in pj:
        if key not in valid_fields:
            # Anthropic suggests the likely intended name when a field is a
            # near-miss of a recognized one; mirror that.
            near = difflib.get_close_matches(key, valid_fields, n=1, cutoff=0.8)
            hint = f" (did you mean '{near[0]}'?)" if near else ""
            msg = f"Unrecognized field: '{key}' — not in the Anthropic plugin manifest spec; ignored at load{hint}"
            (errors if strict else warnings).append(msg)

    TYPE_MAP = {"string": str, "object": dict, "array": list, "boolean": bool}
    for key, value in pj.items():
        if key in PLUGIN_JSON_FIELDS:
            expected = PLUGIN_JSON_FIELDS[key].get("type", "")
            allowed = tuple(TYPE_MAP[t] for t in expected.split("|") if t in TYPE_MAP)
            if allowed and not isinstance(value, allowed):
                errors.append(f"Field '{key}' must be {expected}, got {type(value).__name__}")

    if isinstance(pj.get("author"), dict) and "name" not in pj["author"]:
        errors.append("author object must have 'name' field")

    return {"errors": errors, "warnings": warnings}


_MCP_VERB_PREFIXES = (
    "list",
    "get",
    "create",
    "delete",
    "update",
    "reserve",
    "terminate",
    "confirm",
    "upload",
    "fetch",
    "cancel",
    "start",
    "stop",
)
# Fully-qualified MCP tool reference: mcp__<server>__<tool>.
# The server segment accepts kebab/snake names (mcp__semantic-scholar__paper_search,
# mcp__plugin_automate_kobiton__getApp): alnum runs joined by a SINGLE `-`/`_`.
# Each joiner must be followed by an alnum char, so the segment can never swallow
# the `__` separator (whose second char is `_`, not alnum) — deliberate
# disambiguation. Charset mirrors RE_MCP_TOOL_REF, minus its ^…$ anchors.
_RE_MCP_FQ = re.compile(r"mcp__[a-zA-Z0-9]+(?:[-_][a-zA-Z0-9]+)*__[a-zA-Z0-9_]+")
# Backtick-quoted verbCamelCase short names commonly tool-call-shaped.
_RE_BACKTICK_VERB = re.compile(r"`([a-z][a-zA-Z0-9_]*)`")


def _agent_declared_tools(fm: Dict[str, Any]) -> List[str]:
    """Normalize the agent `tools` field (string|array) to a list of names."""
    val = fm.get("tools")
    if isinstance(val, list):
        return [str(t).strip() for t in val if str(t).strip()]
    if isinstance(val, str):
        return [t.strip() for t in re.split(r"[,\s]+", val) if t.strip()]
    return []


def check_agent_body_vs_allowlist(fm: Dict[str, Any], body: str) -> Tuple[List[str], List[str]]:
    """Cross-check the agent body against its `tools` allowlist (issue #843).

    The `tools` frontmatter is a runtime allowlist — tools not listed are
    blocked. An agent whose body invokes an MCP tool it never declares will
    runtime-block every call (caught downstream, not by the old validator).

    CHECK 1 (ERROR): body contains a fully-qualified mcp__server__tool that is
                     not in the declared allowlist (and some MCP tools ARE
                     declared — the partial-coverage case).
    CHECK 3 (ERROR): the allowlist declares ZERO mcp__* tools but the body
                     contains fully-qualified mcp__ references — the highest-
                     confidence form of the defect; every call would block.
    CHECK 2 (WARN):  body backtick-mentions a verbCamelCase short name
                     (listDevices, getSession, …) with no matching declared
                     mcp__*__<name>. Heuristic — short names are ambiguous.
    WARN (over-declared): a declared mcp__*__<tool> whose suffix never appears
                     in the body (FQ or short) — privilege drift.
    """
    errors: List[str] = []
    warnings: List[str] = []

    declared = _agent_declared_tools(fm)
    declared_mcp = [t for t in declared if t.startswith("mcp__")]
    declared_set = set(declared)
    declared_suffixes = {t.rsplit("__", 1)[-1] for t in declared_mcp if "__" in t}

    # Strip fenced code blocks from the body so syntax/examples inside ``` … ```
    # don't trip the FQ-reference checks (they document, not invoke).
    body_no_fences = re.sub(r"```.*?```", "", body, flags=re.DOTALL)

    fq_refs = sorted(set(_RE_MCP_FQ.findall(body_no_fences)))

    if fq_refs and not declared_mcp:
        # CHECK 3 — zero MCP tools declared, body references MCP tools.
        errors.append(
            "[agent] body references MCP tools "
            f"({', '.join(fq_refs[:5])}{'…' if len(fq_refs) > 5 else ''}) "
            "but the `tools` allowlist declares no mcp__* tools — every call would be runtime-blocked (#843 CHECK 3)"
        )
    else:
        # CHECK 1 — specific FQ ref present in body but not in allowlist.
        for ref in fq_refs:
            if ref not in declared_set:
                errors.append(
                    f"[agent] body invokes '{ref}' but it is not in the `tools` allowlist — "
                    "this call would be runtime-blocked (#843 CHECK 1)"
                )

    # CHECK 2 — heuristic short-name mentions with no matching declared MCP tool.
    # Only meaningful when the agent is demonstrably MCP-oriented (declares an
    # mcp tool or the body already has a fully-qualified ref); otherwise a
    # backtick `getStaticProps` / `getServerSideProps` in a code-focused agent
    # is plain prose, not a tool call. Gating here cuts the false positives the
    # short-name heuristic is known to produce (#843 acknowledges the ambiguity).
    short_mentions = (
        {
            w
            for w in _RE_BACKTICK_VERB.findall(body_no_fences)
            if w.startswith(_MCP_VERB_PREFIXES) and any(c.isupper() for c in w)
        }
        if (declared_mcp or fq_refs)
        else set()
    )
    for name in sorted(short_mentions):
        if name not in declared_suffixes:
            warnings.append(
                f"[agent] body mentions `{name}` (tool-call-shaped) but no declared "
                "mcp__*__"
                f"{name} matches — verify it isn't a runtime-blocked call (#843 CHECK 2)"
            )

    # WARN — over-declared MCP tool never referenced in the body.
    for t in declared_mcp:
        suffix = t.rsplit("__", 1)[-1]
        if t not in fq_refs and suffix not in short_mentions:
            warnings.append(
                f"[agent] declares MCP tool '{t}' but the body never references it — "
                "over-declared privilege / spec drift (#843)"
            )

    return errors, warnings


def validate_agent(path: Path) -> Dict[str, Any]:
    """Validate an agent markdown file against Anthropic 2026 spec."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"fatal": f"Cannot read file: {e}"}

    m = RE_FRONTMATTER.match(content)
    if not m:
        return {"fatal": "No frontmatter found"}

    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"fatal": f"Invalid YAML: {e}"}

    errors: List[str] = []
    warnings: List[str] = []

    # Surface unevaluated shell substitutions in YAML values.
    errors.extend(check_yaml_shell_substitution(fm))

    # Detect context (plugin vs standalone)
    _, context = detect_component(path)
    is_plugin_agent = context == "plugin"

    # Required fields — kernel-strict + enterprise "flesh out the entire spec"
    # (errors at every tier; agents are NOT tier-gated like skills). The kernel
    # floor (prefer kernel-derived, else inline mirror) plus the enterprise live
    # set: disallowedTools/skills/background for all agents, plus
    # hooks/mcpServers/permissionMode for STANDALONE agents (those three are
    # plugin-level and runtime-ignored on a plugin agent). The six optional
    # upgrade levers (AGENT_UPGRADE_LEVERS) live as a commented body block and
    # are not parser-required.
    required_set = set(load_kernel_agent_required() or AGENT_ALWAYS_REQUIRED) | AGENT_ENTERPRISE_LIVE_COMMON
    if not is_plugin_agent:
        required_set |= AGENT_STANDALONE_ONLY_REQUIRED
    for field_name in sorted(required_set):
        if field_name not in fm:
            errors.append(f"[agent] Missing required field: {field_name}")

    # Validate present fields against schema
    for field_name, value in fm.items():
        if field_name in AGENT_FIELDS:
            field_def = AGENT_FIELDS[field_name]

            # Type checking
            expected_type = field_def.get("type")
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"[agent] '{field_name}' must be a string, got: {type(value).__name__}")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"[agent] '{field_name}' must be an integer, got: {type(value).__name__}")
            elif expected_type == "boolean" and not isinstance(value, bool):
                errors.append(f"[agent] '{field_name}' must be a boolean, got: {type(value).__name__}")
            elif expected_type == "array" and not isinstance(value, list):
                errors.append(f"[agent] '{field_name}' must be an array, got: {type(value).__name__}")
            elif expected_type == "object" and not isinstance(value, dict):
                errors.append(f"[agent] '{field_name}' must be an object, got: {type(value).__name__}")
            elif expected_type and "|" in expected_type:
                # Union type (e.g. tools: string|array). Accept any listed type.
                _tmap = {"string": str, "array": list, "integer": int, "boolean": bool, "object": dict}
                _allowed = tuple(_tmap[t] for t in expected_type.split("|") if t in _tmap)
                if _allowed and not isinstance(value, _allowed):
                    errors.append(f"[agent] '{field_name}' must be {expected_type}, got: {type(value).__name__}")

            # Value validation
            if "valid" in field_def and isinstance(value, str):
                if value not in field_def["valid"]:
                    errors.append(
                        f"[agent] '{field_name}' value '{value}' not valid. Must be one of: {', '.join(field_def['valid'])}"
                    )

            # Plugin-restricted fields
            if is_plugin_agent and field_name in AGENT_PLUGIN_RESTRICTED:
                warnings.append(f"[agent] '{field_name}' is not supported in plugin agents (ignored by runtime)")

        elif field_name in INVALID_AGENT_FIELDS:
            errors.append(f"[agent] Invalid field '{field_name}': {INVALID_AGENT_FIELDS[field_name]}")
        elif field_name in DEPRECATED_AGENT_FIELDS:
            warnings.append(f"[agent] Deprecated field '{field_name}': {DEPRECATED_AGENT_FIELDS[field_name]}")
        else:
            warnings.append(f"[agent] Unknown field: '{field_name}'")

    # Additional validation for specific fields
    if "name" in fm:
        name = str(fm["name"]).strip()
        if not name:
            errors.append("[agent] 'name' must be non-empty")
        elif not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name):
            warnings.append(f"[agent] 'name' should be kebab-case: {name}")

    if "description" in fm:
        desc = str(fm["description"]).strip()
        if len(desc) < 20:
            errors.append("[agent] 'description' must be at least 20 characters")
        # The A-grade bar wants a real "Use when…/Trigger with…" trigger, which
        # makes good descriptions long. The operative cap is the kernel
        # disclosureMarkers fold (1536); warn only above it rather than at 200.
        if len(desc) > 1536:
            warnings.append("[agent] 'description' should be 1536 characters or less (kernel disclosureMarkers cap)")

    if "model" in fm and isinstance(fm["model"], str):
        model = fm["model"].strip()
        aliases = {"sonnet", "haiku", "opus", "fable", "inherit"}
        if model not in aliases and not re.fullmatch(r"claude-[a-z0-9][a-z0-9.-]*", model):
            errors.append(
                "[agent] 'model' must be sonnet, haiku, opus, fable, inherit, "
                "or a full Claude model ID such as claude-opus-5"
            )

    if "maxTurns" in fm and isinstance(fm["maxTurns"], int):
        if fm["maxTurns"] < 1:
            errors.append("[agent] 'maxTurns' must be a positive integer")

    if "disallowedTools" in fm and isinstance(fm["disallowedTools"], list):
        for i, tool in enumerate(fm["disallowedTools"]):
            if not isinstance(tool, str):
                errors.append(f"[agent] 'disallowedTools[{i}]' must be a string")

    if "skills" in fm and isinstance(fm["skills"], list):
        for i, skill in enumerate(fm["skills"]):
            if not isinstance(skill, str):
                errors.append(f"[agent] 'skills[{i}]' must be a string")

    if "mcpServers" in fm and isinstance(fm["mcpServers"], list):
        for i, server in enumerate(fm["mcpServers"]):
            if isinstance(server, str):
                continue
            if not isinstance(server, dict) or len(server) != 1:
                errors.append(
                    f"[agent] 'mcpServers[{i}]' must be a server-name string or a one-key inline server definition"
                )

    if "experimental" in fm and isinstance(fm["experimental"], dict):
        experimental = fm["experimental"]
        if "cacheTtl" in experimental and experimental["cacheTtl"] not in {"5m", "1h"}:
            errors.append("[agent] 'experimental.cacheTtl' must be one of: 5m, 1h")
        for key in sorted(set(experimental) - {"cacheTtl"}):
            warnings.append(f"[agent] Unknown experimental field: '{key}' (Claude Code currently ignores it)")

    # tags — required array; every entry must be a string (kernel is-overlay
    # agent-definition: tags = array of strings).
    if "tags" in fm and isinstance(fm["tags"], list):
        for i, tag in enumerate(fm["tags"]):
            if not isinstance(tag, str):
                errors.append(f"[agent] 'tags[{i}]' must be a string")

    # Body-vs-allowlist consistency (issue #843). The allowlist is a runtime
    # gate: tools not declared are blocked. So the body and `tools` must agree.
    # RE_FRONTMATTER group(2) is the post-frontmatter body.
    body = m.group(2) or ""
    be, bw = check_agent_body_vs_allowlist(fm, body)
    errors.extend(be)
    warnings.extend(bw)

    return {"errors": errors, "warnings": warnings, "type": "agent"}


# === UTILITY FUNCTIONS ===


def find_skill_files(root: Path) -> List[Path]:
    """Return the canonical graded cohort; requires repository Node 20+ on PATH."""
    resolver = Path(__file__).resolve().parent / "corpus-resolver.mjs"
    try:
        result = subprocess.run(
            ["node", str(resolver), "--cohort", "graded", "--root", str(root), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("corpus resolver requires Node 20+ on PATH") from exc
    if result.returncode != 0:
        raise RuntimeError(f"corpus resolver failed: {result.stderr.strip()}")
    try:
        payload = json_module.loads(result.stdout)
        files = payload["files"]
    except (json_module.JSONDecodeError, KeyError, TypeError) as exc:
        raise RuntimeError(f"corpus resolver returned invalid JSON: {exc}") from exc
    if not isinstance(files, list) or not all(isinstance(value, str) for value in files):
        raise RuntimeError("corpus resolver returned an invalid file list")
    return [root / value for value in files]


def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """Parse YAML frontmatter from SKILL.md content."""
    m = RE_FRONTMATTER.match(content)
    if not m:
        raise ValueError("Invalid or absent YAML frontmatter block at top of SKILL.md")
    front_str, body = m.groups()
    try:
        data = yaml.safe_load(front_str) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parse error: {e}")
    if not isinstance(data, dict):
        raise ValueError("Frontmatter is not a YAML mapping")
    return data, body


def parse_allowed_tools(tools_value: Any) -> List[str]:
    """Parse allowed-tools per Anthropic spec.

    Anthropic doc (code.claude.com/docs/en/skills, Frontmatter reference):
      "Tools Claude can use without asking permission when this skill is active.
       Accepts a space-separated string or a YAML list."

    The doc's canonical example uses space-separated form:
      allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)

    This parser accepts:
      - YAML list: [Read, Write, "Bash(git:*)"]
      - Space-separated string: "Read Write Bash(git add *)"
      - Comma-separated string: "Read, Write, Bash(git:*)" (IS convention)
      - Mixed: "Read Write,Bash(git:*)" (graceful)

    Quoted-arg regions like Bash(git add *) keep their internal spaces.
    """
    if isinstance(tools_value, list):
        return [str(t).strip() for t in tools_value if str(t).strip()]
    if not isinstance(tools_value, str):
        return []
    s = tools_value.strip()
    if not s:
        return []
    # If commas present, split on commas (preserves spaces inside parens).
    if "," in s:
        return [t.strip() for t in s.split(",") if t.strip()]
    # Otherwise space-separated. Walk the string respecting paren depth so
    # `Bash(git add *)` stays as one token.
    tokens: List[str] = []
    buf: List[str] = []
    depth = 0
    for ch in s:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch.isspace() and depth == 0:
            if buf:
                tokens.append("".join(buf).strip())
                buf = []
        else:
            buf.append(ch)
    if buf:
        tokens.append("".join(buf).strip())
    return [t for t in tokens if t]


# Well-formed base tool / server identifier (letters, digits, underscore, hyphen).
RE_TOOL_BASE_IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
# MCP tool reference: mcp__<server> or mcp__<server>__<tool> (Claude Code
# permission-rule form; appears in the corpus, e.g. mcp__database-explorer__query_database).
RE_MCP_TOOL_REF = re.compile(r"^mcp__[A-Za-z0-9_-]+(?:__[A-Za-z0-9_-]+)?$")


def validate_tool_permission(tool: str) -> Tuple[bool, str]:
    """Validate a single allowed-tools entry.

    Entry shapes observed across the plugin corpus (surveyed 2026-06-11):
      - Bare known tool:             Read, Write, Bash, Grep, ...
      - Scoped, colon form:          Bash(git:*), Bash(npm:*)        (IS convention)
      - Scoped, space form:          Bash(git add *)                 (Anthropic canonical example)
      - MCP tool, double-underscore: mcp__server__tool
      - Colon shorthand:             git:*, ServerName:tool_name

    Returns (valid, msg):
      - (True,  "")  — recognized and well-formed.
      - (True,  msg) — well-formed but the base tool name is not a built-in
                       Claude Code tool (e.g. a misspelling like 'Reads').
                       Caller surfaces msg as a WARNING.
      - (False, msg) — malformed entry (unbalanced parentheses, empty scope,
                       illegal characters in the tool name). Caller surfaces
                       msg as an ERROR at every tier under blueprint 727 E1.11
                       and the owner's written approval.

    Note: the old `cmd:*`-format advisory was dropped — Anthropic's canonical
    example is the space form `Bash(git add *)` (code.claude.com/docs/en/skills),
    so a no-colon scope is spec-compliant, not suspect.
    """
    entry = tool.strip()
    if not entry:
        return False, "empty allowed-tools entry"

    # Parenthesis structure: every "(" must be balanced and the scope must
    # close at the end of the entry (catches truncations like `Bash(git add *`
    # and stray fragments like `wc:*)` produced by splitting a parenthesized
    # list on commas).
    open_count = entry.count("(")
    close_count = entry.count(")")
    if open_count != close_count:
        return False, f"Malformed entry (unbalanced parentheses): {tool}"
    if open_count and not entry.endswith(")"):
        return False, f"Malformed entry (scope must close at end of entry): {tool}"

    base = entry.split("(", 1)[0].strip()
    if open_count and not base:
        return False, f"Malformed entry (missing tool name before scope): {tool}"

    # MCP tool references are valid allowed-tools entries; no advisory.
    if RE_MCP_TOOL_REF.match(entry):
        return True, ""

    # Colon shorthand like "git:*" or "ServerName:tool_name" — validate the
    # segment before the colon as the base name.
    base_tool = base.split(":")[0].strip()

    if not RE_TOOL_BASE_IDENT.match(base_tool):
        return False, f"Malformed entry (tool name must be alphanumeric/_/- ): {tool}"

    if open_count:
        inner = entry[entry.index("(") + 1 : -1].strip()
        if not inner:
            return False, f"Empty scope in allowed-tools entry: {tool}"

    if base_tool in LEGACY_TOOL_ALIASES:
        canonical = LEGACY_TOOL_ALIASES[base_tool]
        return True, (
            f"Legacy tool alias '{base_tool}' in entry '{tool}' — prefer '{canonical}' "
            f"(Task was renamed to Agent in Claude Code v2.1.63; both still accepted)"
        )

    if base_tool not in VALID_TOOLS:
        suggestion = difflib.get_close_matches(base_tool, sorted(VALID_TOOLS), n=1, cutoff=0.75)
        if suggestion:
            return True, f"Unknown tool '{base_tool}' in entry '{tool}' — did you mean '{suggestion[0]}'?"
        return True, (
            f"Unknown tool '{base_tool}' in entry '{tool}' (not a built-in Claude Code tool; "
            f"shell commands belong inside a Bash(...) scope)"
        )

    return True, ""


def estimate_word_count(content: str) -> int:
    """Estimate word count for content length check."""
    # Remove frontmatter
    content_body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL)
    return len(content_body.split())


# === VALIDATION FUNCTIONS ===


def validate_frontmatter(path: Path, fm: dict, tier: str = TIER_STANDARD) -> Tuple[List[str], List[str], List[str]]:
    """
    Validate SKILL.md frontmatter.
    Returns: (errors, warnings, infos)
    """
    errors: List[str] = []
    warnings: List[str] = []
    infos: List[str] = []

    # === FIELD PRESENCE CHECKS (tier-aware) ===
    # Standard tier: name + description (STANDARD_REQUIRED per Anthropic spec).
    # Marketplace tier: full IS enterprise standard — all 8 ALWAYS_REQUIRED fields
    # must be present. Missing any of them = ERROR.

    if tier == TIER_MARKETPLACE:
        for key in ALWAYS_REQUIRED:
            if key not in fm:
                errors.append(f"[frontmatter] Missing required field: '{key}' (marketplace)")
        # Conditional fields
        for key, condition in CONDITIONAL_FIELDS.items():
            if condition(fm) and key not in fm:
                warnings.append(
                    f"[frontmatter] Missing conditional field: '{key}' (relevant for this skill's configuration)"
                )
        # Facelift opportunities
        for key, reason in FACELIFT_FIELDS.items():
            if key not in fm:
                infos.append(f"[frontmatter] Consider adding '{key}': {reason}")
    else:
        # Standard tier: Anthropic spec requires name + description
        # (STANDARD_REQUIRED). Both surface as WARNINGS at this tier — errors
        # are reserved for the marketplace gate, and promoting these would be
        # an error-vs-warning semantics change (architectural per
        # SCHEMA_CHANGELOG NON-NEGOTIABLE #7, needs prior approval).
        if "name" not in fm:
            warnings.append("[frontmatter] Missing required field: 'name' (required by Anthropic spec)")
        if "description" not in fm:
            warnings.append("[frontmatter] Missing recommended field: 'description' (recommended by Anthropic spec)")

    # === FIELD-SPECIFIC VALIDATION ===

    # name field
    if "name" in fm:
        name = str(fm["name"]).strip()
        if not name:
            errors.append("[frontmatter] 'name' must be non-empty")
        else:
            # Kebab-case check (WARN for now - some skills use human-readable names)
            if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", name) and len(name) > 1:
                warnings.append(f"[frontmatter] 'name' should be kebab-case (lowercase + hyphens): {name}")

            # Length check
            if len(name) > 64:
                errors.append("[frontmatter] 'name' exceeds 64 characters")

            # Reserved words
            name_lower = name.lower()
            if "anthropic" in name_lower or "claude" in name_lower:
                errors.append(f"[frontmatter] 'name' contains reserved word: {name}")

            # Folder match check (best practice, not error)
            folder_name = path.parent.name
            if name != folder_name:
                warnings.append(
                    f"[frontmatter] 'name' '{name}' differs from folder '{folder_name}' (best practice: match them)"
                )

            if RE_XML_TAG.search(str(name)):
                errors.append("'name' must not contain XML tags (< or >)")

    # description field
    if "description" in fm:
        desc = str(fm["description"]).strip()

        if not desc:
            errors.append("[frontmatter] 'description' must be non-empty")
        else:
            # Length checks
            if len(desc) < 20:
                warnings.append("[frontmatter] 'description' too short (< 20 chars) - may not trigger well")
            if len(desc) > 1024:
                errors.append("[frontmatter] 'description' exceeds 1024 characters")

            # Discoverability checks (tier-aware)
            if not RE_DESCRIPTION_USE_WHEN.search(desc):
                if tier == TIER_ENTERPRISE:
                    warnings.append(
                        "[frontmatter] 'description' should include 'Use when ...' phrase for model discoverability (marketplace)"
                    )
                else:
                    infos.append(
                        "[frontmatter] Consider adding 'Use when ...' phrase to description for better discoverability"
                    )

            if not RE_DESCRIPTION_TRIGGER_WITH.search(desc):
                if tier == TIER_ENTERPRISE:
                    warnings.append(
                        "[frontmatter] 'description' should include 'Trigger with ...' phrase for user discoverability (marketplace)"
                    )
                else:
                    infos.append("[frontmatter] Consider adding 'Trigger with ...' phrase to description")

            # Voice checks (tier-aware)
            if RE_FIRST_PERSON.search(desc):
                if tier == TIER_ENTERPRISE:
                    warnings.append(
                        "[frontmatter] 'description' should NOT use first person (I can / I will / etc.) - use third person"
                    )
                else:
                    warnings.append("[frontmatter] 'description' uses first person - third person recommended")

            if RE_SECOND_PERSON.search(desc):
                if tier == TIER_ENTERPRISE:
                    warnings.append(
                        "[frontmatter] 'description' should NOT use second person (You can / You should) - use third person"
                    )
                else:
                    warnings.append("[frontmatter] 'description' uses second person - third person recommended")

            if RE_XML_TAG.search(str(desc)):
                errors.append("'description' must not contain XML tags (< or >)")

            # Reserved words (WARN - legitimate in AI/Claude product context)
            desc_lower = desc.lower()
            for bad in FORBIDDEN_WORDS:
                if bad in desc_lower:
                    warnings.append(
                        f"[frontmatter] 'description' contains reserved word: '{bad}' (ok for Claude/AI context)"
                    )

            # Imperative language check (best practice)
            imperative_starts = [
                "analyze",
                "audit",
                "build",
                "compare",
                "configure",
                "convert",
                "create",
                "debug",
                "deploy",
                "detect",
                "extract",
                "fix",
                "forecast",
                "generate",
                "implement",
                "log",
                "manage",
                "migrate",
                "monitor",
                "optimize",
                "process",
                "review",
                "route",
                "scan",
                "set up",
                "setup",
                "test",
                "track",
                "transform",
                "validate",
            ]
            has_imperative = any(v in desc_lower for v in imperative_starts)
            if not has_imperative:
                warnings.append("[frontmatter] Consider using action verbs (analyze, detect, forecast, etc.)")

    # allowed-tools field
    # Per code.claude.com/docs/en/skills (Frontmatter reference):
    #   "Accepts a space-separated string or a YAML list."
    # parse_allowed_tools() handles: YAML list, space-separated string,
    # comma-separated string, or mixed. Paren-depth aware so `Bash(git add *)`
    # stays one token in space-separated form.
    if "allowed-tools" in fm:
        raw_tools = fm["allowed-tools"]
        tools_type_error = False
        if isinstance(raw_tools, list):
            valid_list_items: List[str] = []
            for index, item in enumerate(raw_tools, start=1):
                if not isinstance(item, str):
                    errors.append(
                        f"[frontmatter] 'allowed-tools' YAML list item {index} must be a non-empty string, "
                        f"got: {type(item).__name__}"
                    )
                elif not item.strip():
                    errors.append(f"[frontmatter] 'allowed-tools' YAML list item {index} must be a non-empty string")
                else:
                    valid_list_items.append(item)
            tools = parse_allowed_tools(valid_list_items)
        elif isinstance(raw_tools, str):
            if "," in raw_tools:
                empty_positions = [
                    str(index) for index, item in enumerate(raw_tools.split(","), start=1) if not item.strip()
                ]
                if empty_positions:
                    errors.append(
                        "[frontmatter] 'allowed-tools' comma-separated form contains empty "
                        f"entry at position(s): {', '.join(empty_positions)}"
                    )
            tools = parse_allowed_tools(raw_tools)
        else:
            errors.append(
                f"[frontmatter] 'allowed-tools' must be a string or YAML list, got: {type(raw_tools).__name__}"
            )
            tools_type_error = True
            tools = []

        if not tools and not tools_type_error:
            errors.append("[frontmatter] 'allowed-tools' is empty - must list at least one tool")

        for tool in tools:
            valid, msg = validate_tool_permission(tool)
            if not valid:
                # Malformed entry (unbalanced parens, empty scope, illegal
                # characters in the tool name). Ratified blueprint 727 E1.11
                # and the owner's written approval make these fail closed at
                # every tier. Well-formed unknown names remain advisory below.
                errors.append(f"[frontmatter] allowed-tools: {msg}")
            elif msg:
                # Well-formed but unrecognized base tool name (e.g. a
                # misspelling like 'Reads') — advisory.
                warnings.append(f"[frontmatter] allowed-tools: {msg}")

        # Unscoped Bash check (tier-aware)
        if "Bash" in tools:
            if tier == TIER_ENTERPRISE:
                errors.append(
                    "[frontmatter] allowed-tools: unscoped 'Bash' is not allowed - use scoped Bash(git:*), Bash(npm:*), etc."
                )
            else:
                warnings.append(
                    "[frontmatter] allowed-tools: unscoped 'Bash' - consider scoping (Bash(git:*), Bash(npm:*), etc.)"
                )

        # Info about over-permissioning
        # Count unique base tools (Bash scopes like Bash(git:*) should not inflate the tool count).
        def _base_tool(tool: str) -> str:
            base = tool.split("(")[0].strip()
            if ":" in base:
                base = base.split(":")[0].strip()
            return base

        unique_tool_count = len({_base_tool(t) for t in tools})
        if unique_tool_count > 6:
            warnings.append(
                f"[frontmatter] Many tools permitted ({unique_tool_count}) - consider limiting for security"
            )

    # version field
    if "version" in fm:
        version = str(fm["version"])
        if not re.match(r"^\d+\.\d+\.\d+", version):
            errors.append(f"[frontmatter] 'version' should be semver format (X.Y.Z): {version}")

    # author field
    if "author" in fm:
        author = str(fm["author"]).strip()
        if not author:
            errors.append("[frontmatter] 'author' must be non-empty")
        # Recommend email format
        if "@" not in author:
            warnings.append("[frontmatter] 'author' best practice: include email (Name <email>)")

    # license field
    if "license" in fm:
        license_val = str(fm["license"]).strip()
        if not license_val:
            errors.append("[frontmatter] 'license' must be non-empty")

    # === OPTIONAL FIELDS ===

    # model field
    if "model" in fm:
        model = fm["model"]
        valid_models = ["inherit", "sonnet", "haiku", "opus", "fable"]
        if model not in valid_models and not re.fullmatch(r"claude-[a-z0-9][a-z0-9.-]*", str(model)):
            warnings.append(
                f"[frontmatter] 'model' value '{model}' not standard "
                "(use: inherit, sonnet, haiku, opus, fable, or a full Claude model ID)"
            )

    if "background" in fm and not isinstance(fm["background"], bool):
        errors.append(f"[frontmatter] 'background' must be boolean, got: {type(fm['background']).__name__}")

    # disable-model-invocation field
    if "disable-model-invocation" in fm:
        dmi = fm["disable-model-invocation"]
        if not isinstance(dmi, bool):
            errors.append(f"[frontmatter] 'disable-model-invocation' must be boolean, got: {type(dmi).__name__}")

    # tags field
    if "tags" in fm:
        tags = fm["tags"]
        if not isinstance(tags, list):
            errors.append(f"[frontmatter] 'tags' must be array of strings, got: {type(tags).__name__}")
        elif not all(isinstance(t, str) for t in tags):
            errors.append("[frontmatter] 'tags' must contain only strings")

    # === COMPATIBILITY FIELD (per agentskills.io/specification) ===
    # Free-text, max 500 chars. Indicates environment requirements.
    # Examples per the published spec:
    #   compatibility: "Designed for Claude Code"
    #   compatibility: "Requires Python 3.10+ with uv installed"
    #   compatibility: "Designed for Claude Code, also compatible with Codex and OpenClaw"
    if "compatibility" in fm:
        compat = fm["compatibility"]
        if not isinstance(compat, str):
            errors.append(
                f"[frontmatter] 'compatibility' must be a string (free-text per "
                f"agentskills.io/specification), got: {type(compat).__name__}"
            )
        else:
            compat_str = compat.strip()
            if not compat_str:
                errors.append("[frontmatter] 'compatibility' must be non-empty if specified")
            elif len(compat_str) > 500:
                errors.append(
                    f"[frontmatter] 'compatibility' exceeds 500 characters "
                    f"(agentskills.io/specification limit): {len(compat_str)} chars"
                )

    # === COMPATIBLE-WITH FIELD (deprecated alias) ===
    # Pre-v3.0.0 schema treated this as an enterprise-required CSV platform list
    # with an allow-list. That field was an Intent Solutions invention — it does
    # not appear in any of the 7 verified Anthropic / open-standard sources. Kept
    # parsing for backward compatibility; emits deprecation warning + migration
    # suggestion. Use `compatibility` (free-text) instead.
    if "compatible-with" in fm:
        compat = fm["compatible-with"]
        if isinstance(compat, str):
            sample = compat
        elif isinstance(compat, list):
            sample = ", ".join(str(p).strip() for p in compat)
        else:
            sample = str(compat)
        # Deprecation message. Validator continues to accept the value; do not
        # promote to error here — that would break 3,385 existing public-repo
        # SKILL.md files. Migration handled by batch-remediate.py.
        warnings.append(
            f"[frontmatter] Deprecated field 'compatible-with' — use `compatibility` "
            f"(free-text per agentskills.io/specification) instead. "
            f"Suggested migration: `compatibility: Designed for {sample or 'Claude Code'}`."
        )

    # === NEW CLAUDE CODE SPEC FIELDS ===

    # context field (fork for subagent execution)
    if "context" in fm:
        ctx = fm["context"]
        if ctx not in ("fork",):
            warnings.append(f"[frontmatter] 'context' value '{ctx}' not standard (use: fork)")

    # agent field (subagent type)
    if "agent" in fm:
        agent_val = str(fm["agent"]).strip()
        if not agent_val:
            errors.append("[frontmatter] 'agent' must be non-empty if specified")

    # user-invocable field (boolean)
    if "user-invocable" in fm:
        ui = fm["user-invocable"]
        if not isinstance(ui, bool):
            errors.append(f"[frontmatter] 'user-invocable' must be boolean, got: {type(ui).__name__}")

    # argument-hint field (string autocomplete hint)
    if "argument-hint" in fm:
        hint = str(fm["argument-hint"]).strip()
        if len(hint) > 200:
            warnings.append("[frontmatter] 'argument-hint' exceeds 200 chars - keep hints concise")

    # arguments field — named positional arguments per code.claude.com/docs/en/skills
    # "Accepts a space-separated string or a YAML list. Names map to argument
    # positions in order."
    if "arguments" in fm:
        args_val = fm["arguments"]
        if not isinstance(args_val, (str, list)):
            errors.append(
                f"[frontmatter] 'arguments' must be a space-separated string or YAML "
                f"list, got: {type(args_val).__name__}"
            )

    # paths field — glob patterns limiting when the skill auto-activates
    # (code.claude.com/docs/en/skills "Frontmatter reference"). Accepts CSV
    # string or YAML list.
    if "paths" in fm:
        paths_val = fm["paths"]
        if not isinstance(paths_val, (str, list)):
            errors.append(
                f"[frontmatter] 'paths' must be a comma-separated string or YAML list, got: {type(paths_val).__name__}"
            )

    # shell field — bash (default) or powershell (code.claude.com/docs/en/skills)
    if "shell" in fm:
        shell_val = fm["shell"]
        if shell_val not in ("bash", "powershell"):
            warnings.append(f"[frontmatter] 'shell' value '{shell_val}' not standard (use: bash or powershell)")

    # when_to_use field — documented optional per code.claude.com/docs/en/skills
    # "Additional context for when Claude should invoke the skill, such as trigger
    # phrases or example requests. Appended to `description` in the skill listing
    # and counts toward the 1,536-character cap."
    if "when_to_use" in fm:
        wtu = fm["when_to_use"]
        if not isinstance(wtu, str):
            errors.append(f"[frontmatter] 'when_to_use' must be a string, got: {type(wtu).__name__}")
        else:
            wtu_str = wtu.strip()
            # description+when_to_use combined cap is 1,536 chars per Anthropic doc.
            desc_len = len(str(fm.get("description", "")).strip())
            combined_len = desc_len + len(wtu_str)
            if combined_len > 1536:
                warnings.append(
                    f"[frontmatter] 'description' + 'when_to_use' combined "
                    f"({combined_len} chars) exceeds Anthropic's 1,536-char cap on "
                    f"the skill listing entry."
                )

    # hooks field (skill-scoped lifecycle hooks)
    if "hooks" in fm:
        hooks_val = fm["hooks"]
        if not isinstance(hooks_val, dict):
            errors.append(f"[frontmatter] 'hooks' must be a mapping, got: {type(hooks_val).__name__}")

    # ── Visibility fields (schema 3.5.0) ─────────────────────────────────
    # Shape: each must be a list of strings (or absent). Authors may write
    # block-list, inline-array `[a, b]`, or CSV form — discover-skills.mjs
    # normalizes those. The validator accepts any of the three at parse-time
    # and validates the *normalized* representation here.
    VISIBILITY_FIELDS = ("requires_env", "requires_tools", "fallback_for_env", "fallback_for_tools")

    def _normalize_visibility_list(val):
        """Accept array / `[a,b]` string / CSV string. Return list[str]."""
        if val is None:
            return []
        if isinstance(val, list):
            return [str(x).strip().strip("\"'") for x in val if str(x).strip()]
        if isinstance(val, str):
            s = val.strip()
            if s.startswith("[") and s.endswith("]"):
                s = s[1:-1]
            return [p.strip().strip("\"'") for p in s.split(",") if p.strip()]
        return []

    for field in VISIBILITY_FIELDS:
        if field not in fm:
            continue
        val = fm[field]
        if not isinstance(val, (list, str)):
            errors.append(
                f"[frontmatter] '{field}' must be a list of strings or a "
                f"comma-separated string, got: {type(val).__name__}"
            )

    # Cross-field rule: same identifier MUST NOT appear in both `requires_*`
    # and `fallback_for_*` for the same scope. A skill cannot simultaneously
    # be "required when X is set" AND "the fallback when X is absent" — that's
    # a contradiction. Validated per scope (env vs tools).
    for scope in ("env", "tools"):
        req = set(_normalize_visibility_list(fm.get(f"requires_{scope}")))
        fb = set(_normalize_visibility_list(fm.get(f"fallback_for_{scope}")))
        overlap = req & fb
        if overlap:
            errors.append(
                f"[frontmatter] contradictory visibility rule on "
                f"requires_{scope} + fallback_for_{scope}: "
                f"{sorted(overlap)} appears in both. A skill cannot "
                f"simultaneously require and be the fallback for the same "
                f"{scope[:-1] if scope.endswith('s') else scope} identifier."
            )

    # ── disallowed-tools cross-field rule (schema 3.7.0) ─────────────────
    # disallowed-tools (kebab-case denylist) removes tools from the model while
    # the skill is active — defense-in-depth parallel to allowed-tools, not a
    # replacement. Shape mirrors allowed-tools: a space/comma-separated string
    # OR a YAML list. Two rules, both enforced here:
    #   1. shape: must be a string or a list (same as allowed-tools);
    #   2. cross-field: a tool pattern MUST NOT appear in both allowed-tools and
    #      disallowed-tools — declaring the same tool permitted AND denied is
    #      contradictory and almost always a mis-scoped list. Error at every tier
    #      (the fields are optional, but if both are present they must agree).
    # Mirrors the visibility-gating overlap rule above.
    if "disallowed-tools" in fm:
        dt_val = fm["disallowed-tools"]
        if not isinstance(dt_val, (list, str)):
            errors.append(
                f"[frontmatter] 'disallowed-tools' must be a list of strings or a "
                f"space/comma-separated string, got: {type(dt_val).__name__}"
            )
        else:
            # Entry-level validation, mirroring allowed-tools (schema 3.16.1).
            # A misspelling or retired name in a deny list matched nothing silently.
            for tool in parse_allowed_tools(dt_val):
                valid, msg = validate_tool_permission(tool)
                if not valid:
                    warnings.append(f"[frontmatter] disallowed-tools: {msg}")
                elif msg:
                    warnings.append(f"[frontmatter] disallowed-tools: {msg}")

        if isinstance(dt_val, (list, str)) and "allowed-tools" in fm:
            allowed_set = set(parse_allowed_tools(fm.get("allowed-tools")))
            disallowed_set = set(parse_allowed_tools(dt_val))
            tool_overlap = allowed_set & disallowed_set
            if tool_overlap:
                errors.append(
                    f"[frontmatter] contradictory tool declaration: "
                    f"{sorted(tool_overlap)} appears in both allowed-tools and "
                    f"disallowed-tools. A tool cannot be simultaneously permitted "
                    f"and denied — remove it from one list."
                )

    # ── Self-declared config surface (schema 3.6.0) ──────────────────────
    # required_environment_variables — list of objects describing each env
    # var the skill consumes. Shape:
    #   - name: ENV_VAR_NAME    (required, string, UPPER_SNAKE_CASE)
    #     prompt: "..."          (required, string — shown to user on first run)
    #     help: "..."            (optional, string — extra context)
    #     required_for: "..."    (optional, string — what the var unlocks)
    rev = fm.get("required_environment_variables")
    rev_declared_names = set()
    if rev is not None:
        if not isinstance(rev, list):
            errors.append(
                f"[frontmatter] 'required_environment_variables' must be a list of objects, got: {type(rev).__name__}"
            )
        else:
            for i, entry in enumerate(rev):
                if not isinstance(entry, dict):
                    errors.append(
                        f"[frontmatter] required_environment_variables[{i}] "
                        f"must be a mapping with at least 'name' + 'prompt', "
                        f"got: {type(entry).__name__}"
                    )
                    continue
                if not entry.get("name"):
                    errors.append(f"[frontmatter] required_environment_variables[{i}] missing required key 'name'")
                else:
                    rev_declared_names.add(str(entry["name"]).strip())
                if not entry.get("prompt"):
                    errors.append(
                        f"[frontmatter] required_environment_variables[{i}] "
                        f"(name={entry.get('name', '?')}) missing required "
                        f"key 'prompt'"
                    )

    # Cross-field consistency with `requires_env` (schema 3.5.0). If a skill
    # declares it needs an env var for visibility, it should also describe
    # that var in `required_environment_variables` so the installer can
    # prompt the user. WARN (not error) — the visibility field alone is
    # still useful even without prompt metadata.
    req_env = set(_normalize_visibility_list(fm.get("requires_env")))
    missing_descriptions = req_env - rev_declared_names
    if missing_descriptions and rev is not None:
        warnings.append(
            f"[frontmatter] requires_env declares "
            f"{sorted(missing_descriptions)} but they have no matching entry "
            f"in required_environment_variables. Add a prompt/help entry so "
            f"the installer can guide the user on first run."
        )

    # metadata.intent-solutions.config — list of per-skill config keys.
    # Shape: each entry is { key, description, default, prompt? }.
    md = fm.get("metadata")
    if isinstance(md, dict):
        is_ns = md.get("intent-solutions") or md.get("intent_solutions")
        if isinstance(is_ns, dict):
            cfg = is_ns.get("config")
            if cfg is not None:
                if not isinstance(cfg, list):
                    errors.append(
                        f"[frontmatter] 'metadata.intent-solutions.config' "
                        f"must be a list of objects, got: "
                        f"{type(cfg).__name__}"
                    )
                else:
                    for i, entry in enumerate(cfg):
                        if not isinstance(entry, dict):
                            errors.append(
                                f"[frontmatter] metadata.intent-solutions."
                                f"config[{i}] must be a mapping, got: "
                                f"{type(entry).__name__}"
                            )
                            continue
                        for required in ("key", "description", "default"):
                            if required not in entry:
                                errors.append(
                                    f"[frontmatter] metadata.intent-"
                                    f"solutions.config[{i}] "
                                    f"(key={entry.get('key', '?')}) missing "
                                    f"required key '{required}'"
                                )

    # Invalid fields — ERROR. Currently empty (see INVALID_SKILL_FIELDS comment),
    # but kept as an extension point.
    for field, message in INVALID_SKILL_FIELDS.items():
        if field in fm:
            errors.append(f"[frontmatter] Invalid field '{field}': {message}")

    # === DEPRECATED FIELDS ===
    # `compatible-with` is handled above with a custom migration suggestion that
    # quotes the user's actual value. Skip here to avoid double-warning.
    deprecated_handled_inline = {"compatible-with"}
    for field, message in DEPRECATED_FIELDS.items():
        if field in fm and field not in deprecated_handled_inline:
            warnings.append(f"[frontmatter] Deprecated field '{field}': {message}")

    # === UNKNOWN FIELDS ===
    # Fields outside the schema registry. At marketplace tier we still warn
    # rather than error so that ad-hoc experimentation isn't blocked.
    known_fields = set(SKILL_FIELDS.keys()) | set(INVALID_SKILL_FIELDS.keys()) | set(DEPRECATED_FIELDS.keys())
    unknown_fields = set(fm.keys()) - known_fields
    for field in unknown_fields:
        warnings.append(
            f"[frontmatter] Unknown field: '{field}'. Not in Anthropic spec, "
            f"AgentSkills.io spec, or Intent Solutions marketplace extensions. "
            f"Will be ignored by the runtime."
        )

    return errors, warnings, infos


# Load-time shell substitution, the two documented forms:
#   !`command`   inline substitution
#   ```!         a fenced block whose body is executed
RE_INLINE_SHELL = re.compile(r"!`([^`\n]+)`")
RE_SHELL_FENCE = re.compile(r"^\s*```!")
RE_ANY_FENCE = re.compile(r"^\s*(```|~~~)")


def _load_time_shell_hits(body: str, line_offset: int = 0) -> List[str]:
    """Locations of load-time shell substitution, as 'L<line>: <snippet>'.

    Occurrences inside an ordinary code fence are excluded (skills that
    document the syntax). The ```! fence is itself the executable form, so
    it is always counted. `line_offset` shifts reported lines into file
    coordinates when frontmatter was already stripped.
    """
    hits: List[str] = []
    in_fence = False
    for i, line in enumerate(body.splitlines(), start=1 + line_offset):
        if RE_SHELL_FENCE.match(line):
            hits.append(f"L{i}: ```! block")
            in_fence = not in_fence
            continue
        if RE_ANY_FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in RE_INLINE_SHELL.finditer(line):
            cmd = m.group(1).strip()
            hits.append(f"L{i}: !`{cmd[:40]}{'…' if len(cmd) > 40 else ''}`")
    return hits


def validate_body(
    path: Path, body: str, tier: str = TIER_STANDARD, fm: dict = None, line_offset: int = 0
) -> Tuple[List[str], List[str], List[str]]:
    """
    Validate SKILL.md body content.
    Returns: (errors, warnings, infos)
    """
    errors: List[str] = []
    warnings: List[str] = []
    infos: List[str] = []
    if fm is None:
        fm = {}
    lines = body.splitlines()

    # === LOAD-TIME SHELL EXECUTION (schema 3.16.1) — advisory only ===
    # Preprocessing, not a tool call; allowed-tools does not gate it.
    shell_hits = _load_time_shell_hits(body, line_offset)
    if shell_hits:
        where = ", ".join(shell_hits[:3]) + (f" (+{len(shell_hits) - 3} more)" if len(shell_hits) > 3 else "")
        target = fm.get("shell")
        target_note = f"; `shell: {target}` selects the interpreter" if target else ""
        warnings.append(
            f"[security] SKILL.md runs {len(shell_hits)} shell substitution(s) at LOAD time, before Claude "
            f"reads the body: {where}. This is preprocessing — it is not a tool call, allowed-tools does not "
            f"gate it, and the output is not re-scanned{target_note}. Review it as executable code. The "
            f"documented kill switch is the `disableSkillShellExecution` setting."
        )

    # === LENGTH CHECKS ===

    # Line limit
    if len(lines) > 500:
        errors.append(
            f"[body] SKILL.md body has {len(lines)} lines — exceeds Anthropic 500-line limit. Extract to references/"
        )
    elif len(lines) > 300:
        warnings.append(
            f"[body] SKILL.md body has {len(lines)} lines (301-500 approaching limit). Consider extracting to references/"
        )

    # Word count check
    word_count = len(body.split())
    if word_count > 5000:
        warnings.append(f"[body] Content exceeds 5000 words ({word_count}) - may overwhelm context")
    elif word_count > 3500:
        warnings.append(f"[body] Content is lengthy ({word_count} words) - consider references/ directory")

    # === SECTION CHECKS (enterprise tier only) ===
    # IMPORTANT: Detect headings outside fenced code blocks to avoid false positives from examples.

    def iter_non_code_lines(text: str):
        in_code_block = False
        for raw in text.splitlines():
            if CODE_FENCE_PATTERN.match(raw):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            yield raw

    def has_markdown_h1(text: str) -> bool:
        for raw in iter_non_code_lines(text):
            if re.match(r"^#\s+\S", raw) and not raw.startswith("## "):
                return True
        return False

    def has_heading_line(text: str, heading: str) -> bool:
        target = heading.strip().lower()
        for raw in iter_non_code_lines(text):
            if raw.strip().lower() == target:
                return True
        return False

    def resolve_present_heading(canonical: str) -> Optional[str]:
        # iel-62j fairness: return whichever heading is actually present for a
        # canonical section — the canonical form OR any accepted synonym — so an
        # external contributor's equivalent wording (e.g. '## Usage' for
        # '## Instructions') satisfies presence + content checks. None if absent.
        for h in [canonical, *SECTION_SYNONYMS.get(canonical, [])]:
            if has_heading_line(body, h):
                return h
        return None

    if tier == TIER_ENTERPRISE:
        for sec in RECOMMENDED_SECTIONS:
            if sec == "# ":
                if not has_markdown_h1(body):
                    errors.append(f"[body] Required section missing: '{sec}' (marketplace tier)")
            elif resolve_present_heading(sec) is None:
                syns = ", ".join(SECTION_SYNONYMS.get(sec, []))
                hint = f" (or an equivalent heading: {syns})" if syns else ""
                errors.append(f"[body] Required section missing: '{sec}'{hint} (marketplace tier)")

    # === LEE HAN CHUNG: SECTION CONTENT MUST BE NON-EMPTY ===

    def _section_body(section_heading: str) -> str:
        """
        Grab content between this heading and the next heading of same or higher level.
        Headings inside code fences are ignored.
        """
        m_heading = re.match(r"^(#+)\s+", section_heading.strip())
        if not m_heading:
            return ""
        level = len(m_heading.group(1))
        target = section_heading.strip().lower()

        found = False
        collected: List[str] = []

        in_code = False
        for raw in body.splitlines():
            if CODE_FENCE_PATTERN.match(raw):
                in_code = not in_code
                continue
            if in_code:
                continue

            if not found:
                if raw.strip().lower() == target:
                    found = True
                continue

            m_next = re.match(r"^\s*(#{1,6})\s+", raw)
            if m_next:
                next_level = len(m_next.group(1))
                if next_level <= level:
                    break

            collected.append(raw)

        return "\n".join(collected).strip()

    if tier == TIER_ENTERPRISE:
        for section, min_chars, level in [
            ("## Instructions", 40, "WARN"),
            ("## Output", 20, "WARN"),
            ("## Error Handling", 20, "WARN"),
            ("## Examples", 20, "WARN"),
            ("## Resources", 20, "WARN"),
        ]:
            present_section = resolve_present_heading(section)
            content = _section_body(present_section) if present_section else ""
            # Ignore empty sections that only contain code fences/whitespace
            content_no_code = re.sub(r"```.*?```", "", content, flags=re.DOTALL).strip()
            if len(content_no_code) < min_chars:
                msg = f"[body] Section '{section}' looks empty/too short (marketplace quality standard)"
                if level == "ERROR":
                    errors.append(msg)
                else:
                    warnings.append(msg)

        # === LEE HAN CHUNG: INSTRUCTIONS MUST BE STEP-BY-STEP ===

        present_instr = resolve_present_heading("## Instructions")
        instructions = _section_body(present_instr) if present_instr else ""
        if instructions:
            has_numbered = bool(re.search(r"(?m)^\s*1\.\s+\S+", instructions))
            has_step_heading = bool(re.search(r"(?mi)^\s*#{2,6}\s*step\s*\d+", instructions))
            has_step_label = bool(re.search(r"(?mi)^\s*step\s*\d+[:\-]", instructions))
            if not (has_numbered or has_step_heading or has_step_label):
                warnings.append(
                    "[body] '## Instructions' should include step-by-step steps (numbered list or Step headings) (marketplace)"
                )

    # === LEE HAN CHUNG: PURPOSE STATEMENT (1-2 sentences near top) ===

    def _sentence_count(text: str) -> int:
        cleaned = re.sub(r"\s+", " ", text.strip())
        if not cleaned:
            return 0
        parts = re.split(r"(?<=[.!?])\s+", cleaned)
        return len([p for p in parts if p.strip()])

    def _extract_first_paragraph(after_line_idx: int) -> str:
        paragraph: List[str] = []
        in_code = False
        for raw in lines[after_line_idx:]:
            if CODE_FENCE_PATTERN.match(raw):
                in_code = not in_code
                continue
            if in_code:
                continue
            if HEADING_PATTERN.match(raw):
                break
            if not raw.strip():
                if paragraph:
                    break
                continue
            # Skip list items to avoid counting bullets as purpose text.
            if raw.lstrip().startswith(("-", "*", "+")):
                if paragraph:
                    break
                continue
            paragraph.append(raw.strip())
        return " ".join(paragraph).strip()

    # Find first H1 title line
    title_idx: Optional[int] = None
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title_idx = i
            break

    purpose_text = ""
    purpose_location: Optional[int] = None

    # Prefer explicit "## Purpose" section if present
    for i, line in enumerate(lines):
        if line.strip().lower() == "## purpose":
            purpose_text = _extract_first_paragraph(i + 1)
            purpose_location = i + 1
            break

    # Fallback: first paragraph after title
    if not purpose_text and title_idx is not None:
        purpose_text = _extract_first_paragraph(title_idx + 1)
        purpose_location = title_idx + 1
        if not purpose_text:
            # Common layout: title followed immediately by a section heading (e.g., ## Overview).
            for i, line in enumerate(lines):
                if line.strip().lower() == "## overview":
                    purpose_text = _extract_first_paragraph(i + 1)
                    purpose_location = i + 1
                    break

    if tier == TIER_ENTERPRISE:
        if not purpose_text:
            warnings.append("[body] Missing purpose statement near the top (marketplace quality standard)")
        else:
            sc = _sentence_count(purpose_text)
            if sc == 0:
                warnings.append("[body] Purpose statement is empty (marketplace quality standard)")
            elif sc > 2:
                warnings.append(f"[body] Purpose statement is {sc} sentences (recommended 1-2)")
            if len(purpose_text) > 400:
                warnings.append("[body] Purpose statement is long (>400 chars) - keep it crisp")
            if purpose_location is not None and purpose_location > 120:
                warnings.append("[body] Purpose statement appears late in the document - keep it near the top")

    # === LEE HAN CHUNG: AVOID HUGE EMBEDDED BLOCKS ===

    in_code_block = False
    code_block_lines = 0
    for raw in lines:
        if CODE_FENCE_PATTERN.match(raw):
            if in_code_block:
                if code_block_lines >= 200:
                    warnings.append(
                        f"[body] Large embedded code block ({code_block_lines} lines) - prefer scripts/ or references/ (Lee Han Chung)"
                    )
                code_block_lines = 0
            in_code_block = not in_code_block
            continue
        if in_code_block:
            code_block_lines += 1

    # === PATH CHECKS ===
    # Remove all code blocks and inline code BEFORE scanning
    # This eliminates false positives from code examples

    body_no_code = re.sub(r"```.*?```", "", body, flags=re.DOTALL)  # Remove fenced code blocks
    body_no_code = re.sub(r"`[^`]+`", "", body_no_code)  # Remove inline code

    # Now check for absolute paths in the cleaned content
    for i, line in enumerate(body_no_code.splitlines(), start=1):
        # Absolute paths forbidden
        for pattern, desc in ABSOLUTE_PATH_PATTERNS:
            if pattern.search(line):
                errors.append(
                    f"[body] Line {i}: contains absolute/OS-specific path ({desc}) - use '${{CLAUDE_SKILL_DIR}}/...'"
                )
                break

        # Backslashes forbidden
        if "\\scripts\\" in line or "\\\\" in line:
            errors.append(f"[body] Line {i}: uses backslashes in path - use forward slashes")

    # === TIME-SENSITIVE INFORMATION ===
    # Check for date-specific logic that will become stale
    time_patterns = [
        (r"\b(before|after|until|since)\s+20\d{2}\b", "date-specific logic"),
        (r"\bas of\s+20\d{2}\b", "date-specific reference"),
        (
            r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+20\d{2}\b",
            "specific date",
        ),
        (r"\bQ[1-4]\s+20\d{2}\b", "quarter reference"),
        (r"\bdeprecated\s+(in|since)\s+v?\d", "version deprecation note"),
    ]
    for pattern, desc in time_patterns:
        matches = list(re.finditer(pattern, body, re.IGNORECASE))
        for m in matches:
            warnings.append(f"[body] Time-sensitive information found: '{m.group()}' ({desc}) - may become stale")

    # Time-sensitive information (skip code blocks to avoid false positives)
    stripped = re.sub(r"```[\s\S]*?```", "", body)
    stripped = re.sub(r"`[^`]+`", "", stripped)
    for pat in RE_TIME_SENSITIVE:
        if pat.search(stripped):
            warnings.append("Body may contain time-sensitive information (dates, versions) that could go stale")
            break

    # === SCRIPT QUALITY CHECKS ===
    # Check embedded scripts for error handling
    code_blocks = re.findall(r"```(?:bash|sh|python|py)?\n(.*?)```", body, re.DOTALL | re.IGNORECASE)
    for i, block in enumerate(code_blocks):
        # Check for error handling in bash scripts (only for substantial scripts, not examples)
        if "set -e" not in block and "|| " not in block and "if [" not in block:
            if len(block.strip().splitlines()) > 15:  # Only warn for substantial scripts
                if re.search(r"\b(rm|mv|cp|curl|wget|pip|npm)\b", block):
                    warnings.append(f"[scripts] Code block {i + 1}: Consider adding error handling (set -e or || exit)")

        # Check for unexplained magic numbers (voodoo constants)
        # Whitelist well-known HTTP status codes and common port numbers
        KNOWN_NUMBERS = {
            "200",
            "201",
            "204",
            "301",
            "302",
            "304",
            "307",
            "308",
            "400",
            "401",
            "403",
            "404",
            "405",
            "408",
            "409",
            "422",
            "429",
            "500",
            "502",
            "503",
            "504",
            "3000",
            "5000",
            "8000",
            "8080",
            "8443",
            "9090",  # common ports
        }
        magic_numbers = re.findall(r"(?<![.\d])\b(?:(?:[2-9]\d{2,})|(?:1\d{3,}))\b(?![.\d])", block)
        for num in magic_numbers[:3]:  # Limit warnings
            if num in KNOWN_NUMBERS:
                continue
            if not re.search(rf"#.*{num}", block):  # No comment explaining it
                warnings.append(f"[scripts] Code block {i + 1}: Magic number '{num}' - add comment explaining why")

    # === STRING SUBSTITUTION CHECKS ===
    # Detect $ARGUMENTS / $ARGUMENTS[N] / $0-$9 usage and validate argument-hint presence
    has_arguments = bool(re.search(r"\$ARGUMENTS", body))
    has_positional = bool(re.search(r"\$[0-9]", body))
    if (has_arguments or has_positional) and "argument-hint" not in fm:
        infos.append(
            "[body] Uses $ARGUMENTS/$N but 'argument-hint' frontmatter is missing — "
            "add argument-hint for autocomplete support (per official docs)"
        )

    # === VOICE CHECKS ===

    if re.search(r"\byou should\b|\byou can\b|\byou will\b", body, re.IGNORECASE):
        warnings.append("[body] Consider imperative language instead of 'you should/can/will'")

    return errors, warnings, infos


def validate_scripts_exist(path: Path, body: str) -> Tuple[List[str], List[str]]:
    """
    Validate that all ${CLAUDE_SKILL_DIR}/scripts/... references point to real files.
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []
    skill_dir = path.parent.resolve()

    referenced = set(m.group(1) for m in RE_SKILLDIR_SCRIPTS.finditer(body))

    for rel in sorted(referenced):
        script_path = (skill_dir / "scripts" / rel).resolve()

        # Ensure path doesn't escape skill directory
        try:
            script_path.relative_to(skill_dir)
        except ValueError:
            errors.append(f"[scripts] Reference escapes skill directory: {rel}")
            continue

        if not script_path.exists():
            warnings.append(
                f"[scripts] Referenced script not found: '${{CLAUDE_SKILL_DIR}}/scripts/{rel}' "
                f"(expected at {skill_dir.name}/scripts/{rel})"
            )

    return errors, warnings


def validate_resource_files_exist(path: Path, body: str) -> Tuple[List[str], List[str]]:
    """
    Validate that all ${CLAUDE_SKILL_DIR}/references/... and ${CLAUDE_SKILL_DIR}/assets/... references point to real files.
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []
    skill_dir = path.parent.resolve()

    for rel in sorted(set(m.group(1) for m in RE_SKILLDIR_REFERENCES.finditer(body))):
        target = (skill_dir / "references" / rel).resolve()
        try:
            target.relative_to(skill_dir)
        except ValueError:
            errors.append(f"[resources] Reference escapes skill directory: references/{rel}")
            continue
        if not target.exists():
            warnings.append(
                f"[resources] Referenced file not found: '${{CLAUDE_SKILL_DIR}}/references/{rel}' "
                f"(expected at {skill_dir.name}/references/{rel})"
            )

    for rel in sorted(set(m.group(1) for m in RE_SKILLDIR_ASSETS.finditer(body))):
        target = (skill_dir / "assets" / rel).resolve()
        try:
            target.relative_to(skill_dir)
        except ValueError:
            errors.append(f"[resources] Reference escapes skill directory: assets/{rel}")
            continue
        if not target.exists():
            warnings.append(
                f"[resources] Referenced file not found: '${{CLAUDE_SKILL_DIR}}/assets/{rel}' "
                f"(expected at {skill_dir.name}/assets/{rel})"
            )

    return errors, warnings


def validate_relative_links(path: Path, body: str) -> Tuple[List[str], List[str]]:
    """
    Validate that relative markdown links in SKILL.md point to existing files.
    Per Anthropic docs, [text](relative-path) is the official pattern for supporting files.
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []
    skill_dir = path.parent.resolve()

    # Skip links inside code blocks and inline code
    in_code_block = False
    filtered_lines = []
    for line in body.splitlines():
        if CODE_FENCE_PATTERN.match(line):
            in_code_block = not in_code_block
        if not in_code_block:
            # Strip inline code spans to avoid matching example links
            filtered_lines.append(re.sub(r"`[^`]+`", "", line))
    filtered_body = "\n".join(filtered_lines)

    for match in RE_RELATIVE_MD_LINK.finditer(filtered_body):
        link_text = match.group(1)
        link_target = match.group(2)

        # Skip anchors, mailto, and template variables
        if link_target.startswith(("#", "mailto:", "${")):
            continue

        target_path = (skill_dir / link_target).resolve()

        # Ensure path doesn't escape skill directory
        try:
            target_path.relative_to(skill_dir)
        except ValueError:
            errors.append(f"[relative-link] Link escapes skill directory: [{link_text}]({link_target})")
            continue

        if not target_path.exists():
            warnings.append(
                f"[relative-link] Linked file not found: [{link_text}]({link_target}) "
                f"(expected at {skill_dir.name}/{link_target})"
            )

    return errors, warnings


# === CONTENT QUALITY VALIDATION (Phase 4: Hightower Feedback) ===
#
# These functions catch content quality issues that structural validation misses:
# - Files listed in README.md but don't exist
# - Python scripts that are stubs (only contain 'pass')
# - Placeholder text like REPLACE_ME, {variable}
# - Generic boilerplate descriptions

# Patterns for detecting stub scripts
STUB_SCRIPT_PATTERNS = [
    re.compile(r"def\s+\w+\([^)]*\):\s*\n\s*pass\s*$", re.MULTILINE),  # Function with only pass
    re.compile(r"Add processing logic here", re.IGNORECASE),
    re.compile(r"This is a template", re.IGNORECASE),
    re.compile(r"Customize based on", re.IGNORECASE),
    re.compile(r"#\s*TODO:\s*implement", re.IGNORECASE),
    re.compile(r"raise NotImplementedError"),
]

# Patterns for detecting placeholder text
PLACEHOLDER_PATTERNS = [
    re.compile(r"\{[a-z_]+\}"),  # {table_name}, {database}, etc.
    re.compile(r"REPLACE_ME", re.IGNORECASE),
    re.compile(r"\[YOUR_[A-Z_]+\]"),  # [YOUR_API_KEY], etc.
    re.compile(r"<insert\s+.+>", re.IGNORECASE),  # <insert description here>
    re.compile(r"\bTBD\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"to be determined", re.IGNORECASE),
    re.compile(r"\bplaceholder\b", re.IGNORECASE),
]

# Patterns for detecting generic boilerplate
BOILERPLATE_PATTERNS = [
    re.compile(r"This skill provides automated assistance for \[?\w*\]? tasks", re.IGNORECASE),
    re.compile(r"This skill enables Claude to", re.IGNORECASE),
    re.compile(r"Step \d+: Assess Current State\s*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"Step \d+: Design Solution\s*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"Step \d+: Implement Changes\s*$", re.MULTILINE | re.IGNORECASE),
    re.compile(r"This is a template that can be customized", re.IGNORECASE),
    re.compile(r"Customize based on your requirements", re.IGNORECASE),
]


def validate_references_readme(skill_path: Path) -> Tuple[List[str], List[str]]:
    """
    Parse references/README.md for checkbox file lists.
    Verify each listed file actually exists.
    Returns (errors, warnings).

    Catches issues like:
    - references/README.md lists "postgresql_best_practices.md" but file doesn't exist
    """
    errors: List[str] = []
    warnings: List[str] = []
    skill_dir = skill_path.parent.resolve()

    # Check references/README.md
    refs_readme = skill_dir / "references" / "README.md"
    if refs_readme.exists():
        try:
            content = refs_readme.read_text(encoding="utf-8")
            # Match checkbox patterns: - [x] filename.md or - [ ] filename.md
            checkbox_pattern = re.compile(r"-\s*\[[ xX]\]\s*([^\s:]+\.(?:md|yaml|json|py|sh))")
            matches = checkbox_pattern.findall(content)

            for filename in matches:
                file_path = skill_dir / "references" / filename
                if not file_path.exists():
                    warnings.append(f"[content-quality] references/README.md lists '{filename}' but file doesn't exist")
        except Exception as e:
            warnings.append(f"[content-quality] Could not parse references/README.md: {e}")

    # Check assets/README.md
    assets_readme = skill_dir / "assets" / "README.md"
    if assets_readme.exists():
        try:
            content = assets_readme.read_text(encoding="utf-8")
            checkbox_pattern = re.compile(r"-\s*\[[ xX]\]\s*([^\s:]+\.(?:md|yaml|json|py|sh|template))")
            matches = checkbox_pattern.findall(content)

            for filename in matches:
                file_path = skill_dir / "assets" / filename
                if not file_path.exists():
                    warnings.append(f"[content-quality] assets/README.md lists '{filename}' but file doesn't exist")
        except Exception as e:
            warnings.append(f"[content-quality] Could not parse assets/README.md: {e}")

    return errors, warnings


def detect_stub_scripts(skill_path: Path) -> Tuple[List[str], List[str]]:
    """
    Scan Python scripts for stub patterns:
    - Functions with only 'pass' in body
    - "Add processing logic here"
    - "This is a template"
    - TODO/FIXME without implementation
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []
    skill_dir = skill_path.parent.resolve()
    scripts_dir = skill_dir / "scripts"

    if not scripts_dir.exists():
        return errors, warnings

    for script in scripts_dir.glob("*.py"):
        try:
            content = script.read_text(encoding="utf-8")
            script_name = script.name

            # Check for stub patterns
            for pattern in STUB_SCRIPT_PATTERNS:
                if pattern.search(content):
                    warnings.append(
                        f"[content-quality] scripts/{script_name} appears to be a stub (contains placeholder code)"
                    )
                    break  # One warning per file is enough

            # Additional check: file is mostly empty or just imports
            lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
            non_import_lines = [l for l in lines if not l.startswith(("import ", "from "))]
            if len(non_import_lines) < 5 and len(lines) > 0:
                warnings.append(
                    f"[content-quality] scripts/{script_name} has minimal implementation ({len(non_import_lines)} non-import lines)"
                )

        except Exception as e:
            warnings.append(f"[content-quality] Could not read scripts/{script.name}: {e}")

    return errors, warnings


def detect_placeholder_text(skill_path: Path) -> Tuple[List[str], List[str]]:
    """
    Scan SKILL.md, templates, and config for placeholder patterns:
    - REPLACE_ME, {table_name}, {PLACEHOLDER}
    - TBD, TODO, FIXME in prose (not code comments)
    - "to be determined", "placeholder"
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []
    skill_dir = skill_path.parent.resolve()

    # Files to scan (exclude code files where placeholders might be intentional)
    files_to_scan = [
        skill_path,  # SKILL.md
    ]

    # Add templates and config files
    for pattern in ["assets/*.yaml", "assets/*.yml", "config/*.yaml", "config/*.yml"]:
        files_to_scan.extend(skill_dir.glob(pattern))

    for file_path in files_to_scan:
        if not file_path.exists():
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = file_path.relative_to(skill_dir)

            # Skip checking inside code blocks for SKILL.md
            if file_path.name == "SKILL.md":
                # Remove code blocks before checking
                content_no_code = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
            else:
                content_no_code = content

            for pattern in PLACEHOLDER_PATTERNS:
                matches = pattern.findall(content_no_code)
                if matches:
                    # Limit to first 3 unique matches per file
                    unique_matches = list(set(matches))[:3]
                    warnings.append(
                        f"[content-quality] {rel_path} contains placeholder text: {', '.join(unique_matches)}"
                    )
                    break  # One warning per file

        except Exception as e:
            warnings.append(f"[content-quality] Could not scan {file_path.name}: {e}")

    return errors, warnings


def check_line_character_length(body: str) -> Tuple[List[str], List[str]]:
    """
    Check for excessively long lines in SKILL.md body (outside code fences).
    - WARN if any line > 500 chars
    - ERROR if any line > 2000 chars
    Caps at 5 warnings to avoid spamming.
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []
    in_fence = False
    warning_count = 0

    for lineno, line in enumerate(body.splitlines(), start=1):
        if CODE_FENCE_PATTERN.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        length = len(line)
        if length > 2000:
            errors.append(f"[line-length] Line {lineno} is {length} chars (limit 2000): {line[:80]}...")
        elif length > 500 and warning_count < 5:
            warnings.append(f"[line-length] Line {lineno} is {length} chars (recommended limit 500)")
            warning_count += 1

    return errors, warnings


# ============================================================================
# Tier 2: Static Production Gate
# ============================================================================
# Five binary checks beyond the 100-point rubric, framed as production-readiness
# gates. Run alongside the standard tier checks; surface as errors at marketplace
# tier when they fail. See `~/.claude/skills/validate-skillmd/SKILL.md` § Tier 2
# for the consumer-side framing. The plan reference is "Use the Printing Press
# to Learn" Phase 2.
#
# Each check is intentionally conservative — false-negatives are preferred to
# false-positives so legitimate skills don't get blocked by an over-eager gate.

# Tools that, when declared without scoping AND combined with file-write or
# network-fetch, raise a tool-safety concern. Skills that legitimately need
# unscoped Bash + Write/WebFetch should justify with a "Safety Justification"
# section in the body (the heuristic checks for one).
TIER2_DANGEROUS_BASH_COMBOS = ("Write", "WebFetch")
TIER2_AUTH_INDICATORS = (
    "curl ",
    "fetch(",
    "API_KEY",
    "TOKEN",
    "OAuth",
    "Bearer ",
    "mcp__",
)
TIER2_AUTH_DOCS_MARKERS = (
    "authentication",
    "auth method",
    "api key",
    "bearer token",
    "oauth flow",
    "credentials",
    "x-api-key",
)
TIER2_ORCHESTRATION_SMELLS = (
    "spawn another skill",
    "delegate to /",
    "orchestrate across",
    "self-coordinate",
    "spawns multiple skills",
    "invokes other skills as primary",
)
TIER2_BASE_TOOL_PATTERN = re.compile(
    r"\b(Agent|Artifact|AskUserQuestion|Bash|CronCreate|CronDelete|CronList|Edit|EndConversation|EnterPlanMode|EnterWorktree|ExitPlanMode|ExitWorktree|Glob|Grep|ListMcpResourcesTool|LSP|Monitor|NotebookEdit|PowerShell|PushNotification|Read|ReadMcpResourceTool|RemoteTrigger|ReportFindings|ScheduleWakeup|SendMessage|SendUserFile|ShareOnboardingGuide|Skill|Task|TaskCreate|TaskGet|TaskList|TaskOutput|TaskStop|TaskUpdate|TodoWrite|ToolSearch|WaitForMcpServers|WebFetch|WebSearch|Workflow|Write)\b"
)
TIER2_LITERAL_FALSE_PATTERN = re.compile(r"^\s*(if false|if \[ false \]|elif false)\b", re.MULTILINE)


def _tier2_extract_declared_base_tools(fm: dict) -> set:
    """Return the set of base tool names declared in allowed-tools.

    Handles all three accepted forms (CSV string, space-separated string, YAML
    list) per schema 3.3.1. Strips Bash() scoping wrappers to get just the
    base tool name (`Bash(git:*)` → `Bash`).
    """
    tools_value = fm.get("allowed-tools") if fm else None
    if not tools_value:
        return set()
    parsed = parse_allowed_tools(tools_value)
    base_tools: set = set()
    for tool in parsed:
        m = TIER2_BASE_TOOL_PATTERN.match(tool)
        if m:
            base_tools.add(m.group(1))
    return base_tools


def tier2_check_allowed_tools_accuracy(body: str, fm: dict) -> Tuple[List[str], List[str]]:
    """Tier 2.1: every declared tool is actually referenced in the skill body.

    Over-permissive declarations are an attack-surface concern. Returns
    (errors, warnings) where any unused declared tool is a warning (not an
    error — refactors can briefly leave declarations dangling without breaking
    the skill).
    """
    errors: List[str] = []
    warnings: List[str] = []
    declared = _tier2_extract_declared_base_tools(fm)
    for tool in sorted(declared):
        # Each declared tool should appear somewhere in the body. We grep for
        # the bare token, allowing tool name to be referenced in code snippets,
        # prose, or examples. Bash is special-cased — virtually every skill
        # body mentions "bash" in code fences.
        if tool == "Bash":
            continue
        if tool not in body:
            warnings.append(
                f"[tier2:allowed-tools-accuracy] Tool '{tool}' is declared in allowed-tools "
                f"but never referenced in the skill body — over-permissive or stale declaration"
            )
    return errors, warnings


def tier2_check_auth_documented(body: str) -> Tuple[List[str], List[str]]:
    """Tier 2.2: if the skill mentions an external API, an auth method must be documented.

    Heuristic: presence of API indicators (curl, fetch, MCP server, OAuth,
    bearer tokens) requires at least one documentation marker
    (authentication / auth method / api key / etc.) somewhere in the body.
    """
    errors: List[str] = []
    warnings: List[str] = []
    body_lower = body.lower()
    has_api_indicator = any(ind.lower() in body_lower for ind in TIER2_AUTH_INDICATORS)
    if not has_api_indicator:
        return errors, warnings
    has_auth_doc = any(marker in body_lower for marker in TIER2_AUTH_DOCS_MARKERS)
    if not has_auth_doc:
        warnings.append(
            "[tier2:auth-documented] External API surface referenced (curl/fetch/MCP/OAuth/etc.) "
            "but no authentication method documented — add an Auth section or reference auth.md"
        )
    return errors, warnings


def tier2_check_dead_code(body: str) -> Tuple[List[str], List[str]]:
    """Tier 2.3: detect literal-false branches and unreachable conditionals.

    Conservative — only flags syntactically-obvious dead code. Real
    unreachable-branch analysis would require parsing the bash AST, which
    is out of scope for a deterministic gate.
    """
    errors: List[str] = []
    warnings: List[str] = []
    matches = list(TIER2_LITERAL_FALSE_PATTERN.finditer(body))
    for m in matches[:3]:  # Cap surfacing to 3
        line_no = body[: m.start()].count("\n") + 1
        warnings.append(f"[tier2:dead-code] Literal-false branch found at line ~{line_no}: '{m.group(0).strip()}'")
    return errors, warnings


def tier2_check_tool_safety(body: str, fm: dict) -> Tuple[List[str], List[str]]:
    """Tier 2.4: dangerous tool combos require a Safety Justification.

    Unscoped Bash + Write/WebFetch is the canonical curl-pipe-shell exploit
    surface. Skills that need this combo legitimately should explain why
    in a body section so reviewers can audit.
    """
    errors: List[str] = []
    warnings: List[str] = []
    tools_value = fm.get("allowed-tools") if fm else None
    if not tools_value:
        return errors, warnings
    parsed = parse_allowed_tools(tools_value)

    # Detect unscoped Bash (presence of "Bash" without paren-scoping)
    has_unscoped_bash = any(t.strip() == "Bash" for t in parsed)
    if not has_unscoped_bash:
        return errors, warnings

    # Check companion dangerous tools
    has_dangerous_companion = any(
        any(t.strip().startswith(combo) for combo in TIER2_DANGEROUS_BASH_COMBOS) for t in parsed
    )
    if not has_dangerous_companion:
        return errors, warnings

    # Look for safety justification in body
    body_lower = body.lower()
    has_justification = (
        "safety justification" in body_lower or "why unscoped bash" in body_lower or "why bash + " in body_lower
    )
    if not has_justification:
        errors.append(
            "[tier2:tool-safety] Unscoped Bash + Write/WebFetch declared without a Safety "
            "Justification section — high-risk combo. Add `## Safety Justification` explaining why."
        )
    return errors, warnings


def tier2_check_orchestration_bounds(body: str) -> Tuple[List[str], List[str]]:
    """Tier 2.5: skills should not orchestrate other skills as primary control flow.

    Skills do one job. Cross-skill orchestration is plugin-layer concern.
    This check flags claims of multi-skill orchestration — multi-agent
    synthesis WITHIN one skill invocation (calling subagents to specialize)
    is fine and expected.

    False-positive avoidance:
    - Skip lines inside code fences (descriptive examples, not actual claims)
    - Skip lines with negation markers ('not', 'never', 'avoid', "don't",
      'must not', 'should not', 'NOT', 'forbidden', 'disallow') — these are
      documenting the anti-pattern, not committing it
    - Skip lines starting with '>' (block quotes — typically didactic)
    """
    errors: List[str] = []
    warnings: List[str] = []
    negation_markers = (
        " not ",
        "never",
        "avoid",
        "don't",
        "do not",
        "must not",
        "should not",
        "forbidden",
        "disallow",
        "anti-pattern",
        "antipattern",
        "wrong:",
        "bad:",
    )
    in_fence = False
    for line in body.splitlines():
        if CODE_FENCE_PATTERN.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if stripped.startswith(">") or stripped.startswith("|"):
            # Block quotes and table cells often discuss anti-patterns descriptively
            continue
        line_lower = line.lower()
        # Skip negated lines
        if any(neg in line_lower for neg in negation_markers):
            continue
        for smell in TIER2_ORCHESTRATION_SMELLS:
            if smell in line_lower:
                errors.append(
                    f"[tier2:orchestration-bounds] Body contains orchestration smell '{smell}' — "
                    f"cross-skill orchestration is plugin-layer concern, not skill-layer"
                )
                return errors, warnings  # one is enough
    return errors, warnings


def validate_tier2_production_gate(path: Path, body: str, fm: dict) -> Tuple[List[str], List[str], List[str]]:
    """Run all 5 Tier 2 production-gate checks and aggregate results.

    Returns (errors, warnings, infos). Infos report which checks ran (always
    5) for transparency in the validator output.
    """
    errors: List[str] = []
    warnings: List[str] = []
    infos: List[str] = [
        "[tier2] Production gate ran 5 checks: allowed-tools accuracy, auth documented, dead code, tool safety, orchestration bounds"
    ]

    e1, w1 = tier2_check_allowed_tools_accuracy(body, fm)
    e2, w2 = tier2_check_auth_documented(body)
    e3, w3 = tier2_check_dead_code(body)
    e4, w4 = tier2_check_tool_safety(body, fm)
    e5, w5 = tier2_check_orchestration_bounds(body)

    errors.extend(e1 + e2 + e3 + e4 + e5)
    warnings.extend(w1 + w2 + w3 + w4 + w5)
    return errors, warnings, infos


def detect_stub_sections(body: str) -> Tuple[List[str], List[str]]:
    """
    Detect stub or empty sections in SKILL.md body.
    Splits on '## ' headings and checks each section for:
    - Content < 3 words (essentially empty)
    - TODO, TBD, WIP, or "Coming soon" markers
    - Content < 15 words and only 1 sentence (stub section)
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Split body into sections on level-2 headings
    section_pattern = re.compile(r"^## .+", re.MULTILINE)
    positions = [m.start() for m in section_pattern.finditer(body)]

    if not positions:
        return errors, warnings

    sections: List[Tuple[str, str]] = []
    for i, start in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(body)
        chunk = body[start:end]
        header_end = chunk.index("\n") if "\n" in chunk else len(chunk)
        header = chunk[:header_end].strip()
        content = chunk[header_end:].strip()
        sections.append((header, content))

    stub_markers = re.compile(r"\b(TODO|TBD|WIP|Coming soon)\b", re.IGNORECASE)

    for header, content in sections:
        words = content.split()
        word_count = len(words)

        if word_count < 3:
            warnings.append(f"[stub-section] Section '{header}' has no meaningful content ({word_count} words)")
            continue

        if stub_markers.search(content):
            warnings.append(f"[stub-section] Section '{header}' contains stub marker (TODO/TBD/WIP/Coming soon)")

        # Count sentences (rough: split on sentence-ending punctuation)
        sentence_count = len(re.findall(r"[.!?]+", content))
        if word_count < 15 and sentence_count <= 1:
            warnings.append(
                f"[stub-section] Section '{header}' appears to be a stub ({word_count} words, {sentence_count} sentence)"
            )

    return errors, warnings


def validate_reference_file_quality(path: Path) -> Tuple[List[str], List[str]]:
    """
    Check quality of files in the references/ directory adjacent to SKILL.md.
    Strips YAML frontmatter before evaluating content length.
    - WARN if file has < 5 lines or < 100 chars after stripping frontmatter
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []
    refs_dir = path.parent / "references"

    if not refs_dir.is_dir():
        return errors, warnings

    for ref_file in sorted(refs_dir.glob("*.md")):
        try:
            raw = ref_file.read_text(encoding="utf-8")
            # Strip YAML frontmatter if present
            fm_match = RE_FRONTMATTER.match(raw)
            content = fm_match.group(2) if fm_match else raw

            lines = [ln for ln in content.splitlines() if ln.strip()]
            char_count = len(content.strip())

            if len(lines) < 5 or char_count < 100:
                warnings.append(
                    f"[reference-quality] references/{ref_file.name} is too thin "
                    f"({len(lines)} non-blank lines, {char_count} chars after frontmatter)"
                )

        except Exception as e:
            warnings.append(f"[reference-quality] Could not read references/{ref_file.name}: {e}")

    return errors, warnings


def validate_dci_fallbacks(body: str) -> Tuple[List[str], List[str]]:
    """
    Check that DCI directives (!`cmd`) outside code fences include fallback patterns.
    Fallback indicators: || echo, 2>/dev/null, || true, [ -f, command -v, which , type
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []
    in_fence = False
    dci_pattern = re.compile(r"^!`([^`]+)`\s*$")
    fallback_patterns = (
        r"\|\| echo",
        r"2>/dev/null",
        r"\|\| true",
        r"\[ -f",
        r"command -v",
        r"which ",
        r"\btype ",
    )
    fallback_re = re.compile("|".join(fallback_patterns))

    for line in body.splitlines():
        if CODE_FENCE_PATTERN.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        m = dci_pattern.match(line.rstrip())
        if m:
            cmd = m.group(1)
            if not fallback_re.search(cmd):
                warnings.append(
                    f"[dci-fallback] DCI directive lacks fallback: `{cmd}` "
                    f"— consider adding `|| echo 'not installed'` or `2>/dev/null`"
                )

    return errors, warnings


def detect_boilerplate(skill_path: Path) -> Tuple[List[str], List[str]]:
    """
    Detect generic boilerplate phrases in SKILL.md:
    - "This skill provides automated assistance for"
    - "This skill enables Claude to"
    - Generic step descriptions without specifics
    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []

    try:
        content = skill_path.read_text(encoding="utf-8")

        for pattern in BOILERPLATE_PATTERNS:
            if pattern.search(content):
                match = pattern.search(content)
                if match:
                    # Truncate long matches
                    matched_text = match.group()[:60] + ("..." if len(match.group()) > 60 else "")
                    warnings.append(f"[content-quality] SKILL.md contains generic boilerplate: '{matched_text}'")

    except Exception as e:
        warnings.append(f"[content-quality] Could not scan SKILL.md for boilerplate: {e}")

    return errors, warnings


# === STRUCTURAL ADVISORS (suggest architecture improvements) ===

RE_OPERATION_HEADER = re.compile(r"^##\s+[\w-]+(?:\s*\(.*\))?\s*$", re.MULTILINE)


def advise_split_to_commands(path: Path, body: str) -> List[str]:
    """
    Detect multiple distinct operation sections that would be better as
    individual commands/*.md files. Looks for 3+ ## headers that follow
    step/operation naming patterns (## verb-noun, ## Step N: name, ## N. name).
    Returns info-level suggestions.
    """
    infos: List[str] = []
    skill_dir = path.parent.resolve()

    # Walk up to find the plugin root (directory containing .claude-plugin/)
    plugin_dir = None
    for parent in skill_dir.parents:
        if (parent / ".claude-plugin").exists():
            plugin_dir = parent
            break

    # Find ## headers that look like distinct user-invocable operations
    # Only matches kebab-case names (## verb-noun) — the clearest signal
    operation_pattern = re.compile(r"^##\s+(?:\d+\.\s+)?([\w]+-[\w]+(?:-[\w]+)*)\s*$", re.MULTILINE)
    operations = operation_pattern.findall(body)

    if len(operations) >= 3:
        # Check if plugin already has commands/ directory
        has_commands = plugin_dir and (plugin_dir / "commands").exists()

        if not has_commands:
            op_list = ", ".join(operations[:5])
            infos.append(
                f"[advisor] Found {len(operations)} operation sections ({op_list}). "
                f"Consider splitting into individual commands/*.md files for independent invocation."
            )

    return infos


def advise_offload_to_references(path: Path, body: str) -> List[str]:
    """
    Identify body sections >20 lines that could be offloaded to references/.
    Returns info-level suggestions.
    """
    infos: List[str] = []
    skill_dir = path.parent.resolve()
    refs_dir = skill_dir / "references"

    # Split body by ## headers
    sections: List[Tuple[str, int]] = []
    current_header = ""
    current_lines = 0

    for line in body.splitlines():
        if line.startswith("## "):
            if current_header and current_lines > 0:
                sections.append((current_header, current_lines))
            current_header = line.strip("# ").strip()
            current_lines = 0
        else:
            current_lines += 1

    if current_header and current_lines > 0:
        sections.append((current_header, current_lines))

    # Flag sections >20 lines that are good candidates for references
    offload_candidates = [
        "Output",
        "Error Handling",
        "Examples",
        "Resources",
        "Reference",
        "API",
        "Configuration",
        "Schema",
    ]
    for header, line_count in sections:
        if line_count > 20:
            is_candidate = any(kw.lower() in header.lower() for kw in offload_candidates)
            if is_candidate and not refs_dir.exists():
                infos.append(
                    f"[advisor] Section '## {header}' is {line_count} lines. "
                    f"Consider offloading to references/{header.lower().replace(' ', '-')}.md "
                    f"with a relative link: [details](references/{header.lower().replace(' ', '-')}.md)"
                )

    return infos


def advise_dci_opportunities(path: Path, body: str) -> List[str]:
    """
    Detect patterns where DCI (dynamic context injection) would save tool calls.
    Returns info-level suggestions.
    """
    infos: List[str] = []

    # Already has DCI? Skip.
    has_dci = bool(re.search(r"(?m)^!\`[^`]+\`\s*$", body))
    if has_dci:
        return infos

    # Patterns that suggest DCI would help
    dci_triggers = [
        (r"(?i)check if .+ exists", "file existence check", '!`[ -f FILE ] && echo "exists" || echo "not found"`'),
        (r"(?i)read .+\.md", "file reading at start", '!`[ -f FILE ] && head -5 FILE || echo "not found"`'),
        (
            r"(?i)git status|git log|git branch",
            "git state discovery",
            '!`git status --short 2>/dev/null || echo "not a git repo"`',
        ),
        (
            r"(?i)check (?:which |if )?(?:node|python|docker|terraform|npm|pnpm)",
            "tool version check",
            '!`command -v TOOL 2>/dev/null && TOOL --version 2>/dev/null || echo "not installed"`',
        ),
    ]

    for pattern, desc, example in dci_triggers:
        if re.search(pattern, body):
            infos.append(f"[advisor] Skill performs {desc} — consider DCI to auto-detect at activation: `{example}`")
            break  # One suggestion is enough

    return infos


def validate_supporting_files(path: Path) -> Tuple[List[str], List[str]]:
    """Check supporting file requirements for a skill.
    - references/ directory must exist (enterprise)
    - references/ must have content (not empty files)
    - scripts/ must exist if SKILL.md uses ${CLAUDE_SKILL_DIR}/scripts/
    """
    errors: List[str] = []
    warnings: List[str] = []
    skill_dir = path.parent

    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        warnings.append("[supporting] Missing references/ directory — create it for progressive disclosure")
    elif refs_dir.exists():
        ref_files = list(refs_dir.glob("*.md"))
        if not ref_files:
            warnings.append("[supporting] references/ directory is empty — add reference documents")
        else:
            for ref_file in ref_files:
                if ref_file.stat().st_size == 0:
                    warnings.append(f"[supporting] references/{ref_file.name} is empty (0 bytes)")

    # Check for singular reference.md (anti-pattern)
    if (skill_dir / "reference.md").exists():
        errors.append(
            "[supporting] Found 'reference.md' (singular) — rename to references/ directory with .md files inside"
        )

    return errors, warnings


def detect_stub_skill(path: Path, body: str, fm: dict) -> Tuple[List[str], List[str]]:
    """Detect if a SKILL.md is a stub (insufficient content).
    A skill is a stub if ANY of:
    - Body < 30 lines
    - Zero code blocks AND zero markdown links to supporting files
    - Description matches generic patterns
    - No ## Instructions section
    """
    errors: List[str] = []
    warnings: List[str] = []
    lines = body.strip().splitlines()

    # Skip stub detection for fork skills (they're intentionally minimal)
    if fm.get("context") == "fork":
        return errors, warnings

    stub_reasons = []

    if len(lines) < 30:
        stub_reasons.append(f"body is only {len(lines)} lines (minimum 30)")

    code_blocks = len(re.findall(r"```", body)) // 2
    md_links = len(re.findall(r"\[.*?\]\((?!https?://)[^)]+\)", body))
    if code_blocks == 0 and md_links == 0:
        stub_reasons.append("no code blocks and no relative links to supporting files")

    desc = str(fm.get("description", "")).lower()
    generic_patterns = ["a helpful tool", "this skill provides", "enables claude to"]
    if any(p in desc for p in generic_patterns) and "use when" not in desc:
        stub_reasons.append("description is generic with no 'use when' phrase")

    has_instructions = bool(re.search(r"(?mi)^##\s+instructions", body))
    if not has_instructions:
        stub_reasons.append("missing ## Instructions section")

    if len(stub_reasons) >= 2:
        warnings.append(f"[stub] Skill appears to be a stub: {'; '.join(stub_reasons)}")

    return errors, warnings


def validate_skill(path: Path, tier: str = TIER_STANDARD) -> Dict[str, Any]:
    """
    Validate a single SKILL.md file.
    Returns dict with errors, warnings, infos, and metadata.
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"fatal": f"Cannot read file: {e}"}

    try:
        fm, body = parse_frontmatter(content)
    except Exception as e:
        return {"fatal": str(e)}

    errors: List[str] = []
    warnings: List[str] = []
    infos: List[str] = []

    # Frontmatter size budget (local, per-file)
    m = RE_FRONTMATTER.match(content)
    if m:
        front_str, _body = m.groups()
        front_len = len(front_str)
        if front_len > 15_000:
            errors.append(f"[frontmatter] Frontmatter is {front_len} chars (max 15000)")
        elif front_len >= 12_000:
            warnings.append(f"[frontmatter] Frontmatter is {front_len} chars (warn at 12000)")

    # Validate frontmatter
    fm_errors, fm_warnings, fm_infos = validate_frontmatter(path, fm, tier)
    errors.extend(fm_errors)
    warnings.extend(fm_warnings)
    infos.extend(fm_infos)

    # Surface unevaluated shell substitutions in YAML values.
    errors.extend(check_yaml_shell_substitution(fm))

    # Validate body
    body_errors, body_warnings, body_infos = validate_body(path, body, tier, fm)
    errors.extend(body_errors)
    warnings.extend(body_warnings)
    infos.extend(body_infos)

    # Tier 2 — static production gate (5 binary checks).
    # At marketplace tier these contribute errors/warnings; at standard tier
    # they're info-only (visibility without blocking). Plan reference:
    # "Use the Printing Press to Learn" Phase 2.
    t2_errors, t2_warnings, t2_infos = validate_tier2_production_gate(path, body, fm)
    if tier in (TIER_MARKETPLACE,):
        errors.extend(t2_errors)
        warnings.extend(t2_warnings)
    else:
        # Standard tier: surface as warnings instead of errors so the spec
        # floor stays permissive per Anthropic.
        warnings.extend(t2_errors)
        warnings.extend(t2_warnings)
    infos.extend(t2_infos)

    # Validate scripts
    script_errors, script_warnings = validate_scripts_exist(path, body)
    errors.extend(script_errors)
    warnings.extend(script_warnings)

    # Validate referenced resources/templates
    resource_errors, resource_warnings = validate_resource_files_exist(path, body)
    errors.extend(resource_errors)
    warnings.extend(resource_warnings)

    # Validate relative markdown links (Anthropic-recommended pattern)
    link_errors, link_warnings = validate_relative_links(path, body)
    errors.extend(link_errors)
    warnings.extend(link_warnings)

    # === CONTENT QUALITY VALIDATION (Hightower feedback) ===
    # Validate files listed in references/README.md and assets/README.md actually exist
    readme_errors, readme_warnings = validate_references_readme(path)
    errors.extend(readme_errors)
    warnings.extend(readme_warnings)

    # Detect stub Python scripts
    stub_errors, stub_warnings = detect_stub_scripts(path)
    errors.extend(stub_errors)
    warnings.extend(stub_warnings)

    # Detect placeholder text (REPLACE_ME, {variable}, etc.)
    placeholder_errors, placeholder_warnings = detect_placeholder_text(path)
    errors.extend(placeholder_errors)
    warnings.extend(placeholder_warnings)

    # Detect generic boilerplate
    boilerplate_errors, boilerplate_warnings = detect_boilerplate(path)
    errors.extend(boilerplate_errors)
    warnings.extend(boilerplate_warnings)

    # Supporting files check (marketplace tier)
    if tier == TIER_ENTERPRISE:
        sf_errors, sf_warnings = validate_supporting_files(path)
        errors.extend(sf_errors)
        warnings.extend(sf_warnings)

    # Stub detection
    stub_skill_errors, stub_skill_warnings = detect_stub_skill(path, body, fm)
    errors.extend(stub_skill_errors)
    warnings.extend(stub_skill_warnings)

    # Placeholder density check
    _body_no_code = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
    _body_no_code = re.sub(r"`[^`]+`", "", _body_no_code)
    _body_word_count = len(_body_no_code.split())
    _placeholder_tokens = ["TODO", "FIXME", "REPLACE_ME", "TBD", "[YOUR_", "<insert"]
    _placeholder_count = sum(
        len(re.findall(re.escape(tok), _body_no_code, re.IGNORECASE)) for tok in _placeholder_tokens
    ) + len(re.findall(r"\{[a-z_]+\}", _body_no_code))
    if _body_word_count > 0:
        _placeholder_density = _placeholder_count / _body_word_count
        if _placeholder_density > 0.10:
            errors.append(
                f"[content-quality] Excessive placeholders — likely stub content "
                f"({_placeholder_density:.1%} of words are placeholders)"
            )
        elif _placeholder_density > 0.05:
            warnings.append(f"[content-quality] High placeholder density ({_placeholder_density:.1%})")

    # Enterprise-tier quality checks (warnings only)
    if tier == TIER_ENTERPRISE:
        line_len_errors, line_len_warnings = check_line_character_length(body)
        errors.extend(line_len_errors)
        warnings.extend(line_len_warnings)

        stub_errors, stub_warnings = detect_stub_sections(body)
        errors.extend(stub_errors)
        warnings.extend(stub_warnings)

        ref_quality_errors, ref_quality_warnings = validate_reference_file_quality(path)
        errors.extend(ref_quality_errors)
        warnings.extend(ref_quality_warnings)

        dci_errors, dci_warnings = validate_dci_fallbacks(body)
        errors.extend(dci_errors)
        warnings.extend(dci_warnings)

    # === STRUCTURAL ADVISORS (enterprise tier only) ===
    if tier == TIER_ENTERPRISE:
        infos.extend(advise_split_to_commands(path, body))
        infos.extend(advise_offload_to_references(path, body))
        infos.extend(advise_dci_opportunities(path, body))

    description = str(fm.get("description") or "")

    # Calculate Intent Solutions grade
    grade_result = grade_skill(path, body, fm)

    return {
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
        "word_count": estimate_word_count(content),
        "line_count": len(body.splitlines()),
        "description_length": len(description),
        "grade": grade_result,
    }


# === MARKETPLACE COMPLIANCE BASELINE =========================================


def baseline_finding_triple(artifact_path: str, error: str) -> Tuple[str, str, str]:
    """Return a stable ``(path, rule_id, field)`` identity for one validator
    error.

    The ratchet must preserve the validator's actual finding surface. It must
    not scrape terminal output or collapse a file's findings into a count: a
    new field error at an existing path is still new debt. Common rule shapes
    receive readable IDs; every other shape gets a deterministic ID based on
    the normalized validator message, so an unrecognized new error can never
    silently alias an old one.
    """
    scoped = re.match(r"^\[([^\]]+)\]\s*(.*)$", error)
    scope = scoped.group(1) if scoped else "validator"
    detail = scoped.group(2) if scoped else error
    field_match = re.search(
        r"(?:field|section|Reference|Link|resource|script)\s*(?:missing|escapes|does not exist|must be|invalid)?[: ]*'?([^' :]+)'?",
        detail,
        re.IGNORECASE,
    )
    quoted_match = re.search(r"'([^']+)'", detail)
    field = field_match.group(1) if field_match else (quoted_match.group(1) if quoted_match else "_")
    if "Missing required field:" in detail:
        rule_id = "E-MISSING-REQUIRED-FIELD"
    elif "Required section missing:" in detail:
        rule_id = "E-MISSING-REQUIRED-SECTION"
    elif "Invalid field" in detail:
        rule_id = "E-INVALID-FIELD"
    elif "shell substitution" in detail.lower():
        rule_id = "E-YAML-SHELL-SUBSTITUTION"
    elif "Link escapes skill directory" in detail or "Reference escapes skill directory" in detail:
        rule_id = "E-REFERENCE-ESCAPES-SKILL-DIRECTORY"
    else:
        normalized = re.sub(r"\d+", "#", detail.lower())
        normalized = re.sub(r"\s+", " ", normalized).strip()
        category = re.sub(r"[^A-Z0-9]+", "-", scope.upper()).strip("-") or "VALIDATOR"
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
        rule_id = f"E-{category}-{digest}"
    return artifact_path, rule_id, field


def marketplace_baseline_payload(
    findings: List[Tuple[str, str, str]],
    skill_files: int,
    command_files: int,
    plugin_dirs: int,
    agent_files: int,
    grade_a_plus_b: int,
    repo_root: Path,
) -> Dict[str, Any]:
    """Build the shrink-only baseline schema from a full validator run."""
    triples = sorted(set(findings))
    entries = [f"{path} :: {rule_id} :: {field}" for path, rule_id, field in triples]
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, text=True, check=True)
        sha = proc.stdout.strip()
    except Exception:
        sha = "unknown"
    run_id = os.environ.get("GITHUB_RUN_ID")
    return {
        "$comment": (
            "Shrink-only. Entries may ONLY be REMOVED. Regenerate ONLY via --emit-baseline "
            "in the owner-dispatched CI capture whose immutable artifact is verified by required CI."
        ),
        "schema_version": SCHEMA_VERSION,
        "generated_from": {
            "sha": sha,
            "run_id": run_id if run_id else None,
            "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        "corpus_definition": "resolveCorpus('graded')",
        "corpus": {
            "skill_files": skill_files,
            "command_files": command_files,
            "plugin_dirs": plugin_dirs,
            "agent_files": agent_files,
        },
        "totals": {
            "errors": len(entries),
            "grade_A_plus_B": grade_a_plus_b,
            "grade_A_plus_B_pct": round((grade_a_plus_b / skill_files * 100) if skill_files else 0.0, 4),
        },
        "rule_inventory": sorted(DECLARED_MARKETPLACE_RULE_INVENTORY | {rule_id for _path, rule_id, _field in triples}),
        "entries": entries,
    }


def validate_plugin(plugin_dir: Path, tier: str = TIER_STANDARD, strict: bool = False) -> Dict[str, Any]:
    """Validate a plugin as a complete unit.
    Walks all components and rolls up scores.

    `strict` promotes plugin.json unrecognized-field warnings to errors
    (the `--strict` flag); see validate_plugin_json.
    """
    errors: List[str] = []
    warnings: List[str] = []
    infos: List[str] = []

    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"

    # 1. Validate plugin.json — delegate to validate_plugin_json to avoid duplicating logic
    if plugin_json_path.exists():
        pj_result = validate_plugin_json(plugin_json_path, strict=strict)
        for err in pj_result["errors"]:
            errors.append(f"[plugin.json] {err}")
        for warn in pj_result["warnings"]:
            warnings.append(f"[plugin.json] {warn}")
    else:
        warnings.append("[plugin.json] No .claude-plugin/plugin.json found")

    # 2. Validate skills
    # Two supported layouts:
    #   (a) plugin_dir/skills/<name>/SKILL.md   (legacy nested)
    #   (b) plugin_dir/SKILL.md                 (Anthropic-spec / Wondelai-style — SKILL.md at plugin root)
    skill_results = []
    seen_skills: set = set()
    skills_dir = plugin_dir / "skills"
    if skills_dir.exists():
        for skill_md in skills_dir.rglob("SKILL.md"):
            abs_p = skill_md.resolve()
            if abs_p in seen_skills:
                continue
            seen_skills.add(abs_p)
            result = validate_skill(skill_md, tier)
            skill_results.append((skill_md, result))
    root_skill_md = plugin_dir / "SKILL.md"
    if root_skill_md.is_file():
        abs_p = root_skill_md.resolve()
        if abs_p not in seen_skills:
            seen_skills.add(abs_p)
            result = validate_skill(root_skill_md, tier)
            skill_results.append((root_skill_md, result))

    # 3. Validate agents
    agent_results = []
    agents_dir = plugin_dir / "agents"
    if agents_dir.exists():
        for agent_md in agents_dir.glob("*.md"):
            result = validate_agent(agent_md)
            agent_results.append((agent_md, result))

    # 4. Validate commands (legacy — warn to migrate)
    commands_dir = plugin_dir / "commands"
    if commands_dir.exists():
        cmd_files = list(commands_dir.glob("*.md"))
        if cmd_files:
            infos.append(f"[plugin] commands/ directory has {len(cmd_files)} files — consider migrating to skills/")
        for cmd_md in cmd_files:
            result = validate_command(cmd_md)
            if result.get("errors"):
                errors.extend(result["errors"])
            if result.get("warnings"):
                warnings.extend(result["warnings"])

    # 5. Check optional config files
    if (plugin_dir / "hooks" / "hooks.json").exists():
        try:
            json_module.loads((plugin_dir / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        except (json_module.JSONDecodeError, Exception) as e:
            errors.append(f"[plugin] hooks/hooks.json is invalid: {e}")

    if (plugin_dir / ".mcp.json").exists():
        try:
            json_module.loads((plugin_dir / ".mcp.json").read_text(encoding="utf-8"))
        except (json_module.JSONDecodeError, Exception) as e:
            errors.append(f"[plugin] .mcp.json is invalid: {e}")

    # Roll up results
    skill_scores = []
    for skill_path, result in skill_results:
        rel = skill_path.relative_to(plugin_dir)
        if result.get("fatal"):
            errors.append(f"[skill] {rel}: FATAL - {result['fatal']}")
        else:
            errors.extend(result.get("errors", []))
            warnings.extend(result.get("warnings", []))
            grade = result.get("grade", {})
            if grade.get("score"):
                skill_scores.append(grade["score"])

    for agent_path, result in agent_results:
        rel = agent_path.relative_to(plugin_dir)
        if result.get("fatal"):
            errors.append(f"[agent] {rel}: FATAL - {result['fatal']}")
        else:
            errors.extend(result.get("errors", []))
            warnings.extend(result.get("warnings", []))

    avg_score = sum(skill_scores) / len(skill_scores) if skill_scores else 0

    return {
        "errors": errors,
        "warnings": warnings,
        "infos": infos,
        "skill_count": len(skill_results),
        "agent_count": len(agent_results),
        "avg_skill_score": avg_score,
        "type": "plugin",
    }


# === COMPLIANCE DATABASE ===


def deterministic_stub_flags(records: list) -> dict:
    """Return run-scoped stub findings without heuristic thin-content guesses.

    A finding is limited to repeated normalized content within one plugin pack
    (three or more skills) or a relative in-plugin link to a missing path.
    Templates are intentionally excluded and A/B graded skills are protected.
    """
    hashes: Dict[Tuple[str, str], list] = {}
    flags: Dict[str, list] = {}
    for record in records:
        path = record["path"]
        if "templates" in path.parts:
            continue
        normalized = re.sub(r"\s+", " ", record["body"].strip()).lower()
        if normalized:
            digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            hashes.setdefault((str(record["pack"]), digest), []).append(record)
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", record["body"]):
            target = target.strip().split("#", 1)[0]
            if not target or re.match(r"(?:https?:|mailto:|/)", target):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(record["pack"].resolve())
            except ValueError:
                continue
            if not resolved.exists():
                flags.setdefault(str(path), []).append(f"missing in-plugin reference: {target}")
    for (_pack, _digest), members in hashes.items():
        if len(members) >= 3:
            for record in members:
                flags.setdefault(str(record["path"]), []).append(
                    f"normalized body hash shared by {len(members)} skills in pack"
                )
    return {
        path: reasons
        for path, reasons in flags.items()
        if next(record for record in records if str(record["path"]) == path)["grade"] not in {"A", "B"}
    }


def populate_compliance_db(
    db_path: str, skill_results: list, agent_results: list = None, validator_version: str = "5.0.0"
):
    """Write validation results to SQLite compliance tables.

    Writes are tagged with the latest discovery_runs.id so freshie queries
    can filter by run. Paths are stored in repo-relative directory form to
    match the shape used by `skills.path` / `plugins.path` — enabling direct
    joins without path-normalization workarounds.
    """
    import sqlite3
    from datetime import datetime, timezone

    # 60s busy timeout (default is 5s): the populate holds SQLite's single
    # writer slot for the whole loop, and a concurrent writer on the same file
    # (e.g. `j-rig eval --db freshie/inventory.sqlite`) previously turned into
    # a "database is locked" failure that was silently swallowed downstream.
    conn = sqlite3.connect(db_path, timeout=60.0)
    c = conn.cursor()

    # Resolve the current discovery run. Rows from older runs keep their
    # original run_id; fresh writes stamp the latest run so consumers can
    # filter WHERE run_id = (SELECT MAX(id) FROM discovery_runs).
    current_run_id: Optional[int] = None
    try:
        row = c.execute("SELECT MAX(id) FROM discovery_runs").fetchone()
        if row and row[0] is not None:
            current_run_id = int(row[0])
    except sqlite3.Error:
        pass  # discovery_runs may not exist on a fresh DB

    # A discovery run's totals are NULL until rebuild-inventory.py's final
    # UPDATE — NULL totals on the newest run mean a crashed half-run. Stamping
    # compliance rows onto a phantom run poisons the append-only Dolt export,
    # so warn loudly (rebuild-inventory.py purges it on its next default run).
    if current_run_id is not None:
        try:
            trow = c.execute(
                "SELECT total_skills, total_files FROM discovery_runs WHERE id = ?",
                (current_run_id,),
            ).fetchone()
            if trow is not None and trow[0] is None and trow[1] is None:
                print(
                    f"[populate-db] WARN: discovery run_id={current_run_id} has NULL "
                    f"totals — it looks like a crashed/incomplete rebuild-inventory "
                    f"run. Compliance rows will be stamped onto it anyway; re-run "
                    f"freshie/scripts/rebuild-inventory.py first if that is not "
                    f"intended.",
                    file=sys.stderr,
                )
        except sqlite3.Error:
            pass

    repo_root_for_paths = Path(__file__).resolve().parents[1]

    # Issue #660 item 4: pre-2026-05-17 DBs created the *_compliance tables
    # with `<entity>_path TEXT UNIQUE`, which means INSERT OR REPLACE silently
    # overwrites prior runs. Fix: rebuild each table with the composite UNIQUE
    # (path, run_id). Idempotent — only acts when the old constraint is
    # detected. Run before the CREATE TABLE IF NOT EXISTS so the rebuilt
    # tables match the new schema below.
    def _migrate_compliance_unique_to_composite() -> None:
        """Rebuild compliance tables when the legacy single-col UNIQUE is found."""
        for table, key_col in (
            ("skill_compliance", "skill_path"),
            ("agent_compliance", "agent_path"),
            ("plugin_compliance", "plugin_path"),
        ):
            try:
                # Index-list inspects all UNIQUEs (named + auto). The legacy
                # schema's UNIQUE constraint surfaces as a single-column
                # autoindex on `<key_col>`. The new schema's composite
                # constraint surfaces as a two-column autoindex on
                # (<key_col>, run_id). The presence of the single-column
                # autoindex (without a corresponding composite) is the
                # smoking gun for the legacy schema.
                idx_rows = c.execute(f"PRAGMA index_list({table})").fetchall()
            except sqlite3.OperationalError:
                # Table doesn't exist yet — nothing to migrate. The CREATE
                # TABLE IF NOT EXISTS below will create it with the right
                # schema directly.
                continue
            has_legacy_unique = False
            has_composite_unique = False
            for idx_row in idx_rows:
                idx_name = idx_row[1]
                is_unique = bool(idx_row[2])
                if not is_unique:
                    continue
                info = c.execute(f"PRAGMA index_info({idx_name})").fetchall()
                cols = [r[2] for r in info]
                if cols == [key_col]:
                    has_legacy_unique = True
                elif cols == [key_col, "run_id"]:
                    has_composite_unique = True
            if has_composite_unique:
                continue  # already on new schema
            if not has_legacy_unique:
                continue  # neither — table is custom, leave alone
            # Rebuild. We carry data forward verbatim. Old DBs only have one
            # row per skill_path (that's the bug); after migration those same
            # rows live under their original run_id, future writes start
            # snapshotting per-run.
            old_cols = [r[1] for r in c.execute(f"PRAGMA table_info({table})").fetchall()]
            tmp_name = f"{table}__migrate_tmp"
            c.execute(f"DROP TABLE IF EXISTS {tmp_name}")
            c.execute(f"ALTER TABLE {table} RENAME TO {tmp_name}")
            # The CREATE TABLE IF NOT EXISTS below will create the new
            # `<table>` with the composite UNIQUE. Copy data over after.
            # Defer copy to a second pass — done at the bottom of the
            # migration block.
            _migration_queue.append((table, tmp_name, old_cols))

    _migration_queue: list = []
    _migrate_compliance_unique_to_composite()

    def _normalize_skill_path(raw: str) -> str:
        """Convert any skill path form to repo-relative dir (no /SKILL.md)."""
        if not raw:
            return raw
        p = Path(raw)
        if p.is_absolute():
            try:
                p = p.relative_to(repo_root_for_paths)
            except ValueError:
                pass  # outside repo root — keep as-is
        if p.name == "SKILL.md":
            p = p.parent
        return str(p)

    def _normalize_generic_path(raw: str) -> str:
        """Convert any path form to repo-relative; preserves file suffix."""
        if not raw:
            return raw
        p = Path(raw)
        if p.is_absolute():
            try:
                p = p.relative_to(repo_root_for_paths)
            except ValueError:
                pass
        return str(p)

    # skill_compliance: one row per (skill_path, run_id). Composite-key UNIQUE
    # so multiple validation passes against the same discovery run preserve
    # before/after history (issue #660 item 4). Pre-2026-05-17 schema had
    # `skill_path TEXT UNIQUE` which caused INSERT OR REPLACE to silently
    # overwrite prior runs, losing the very thing the run_id column was meant
    # to enable. _migrate_compliance_unique_to_composite() below repairs older
    # DBs at startup. New deployments get the correct schema directly.
    c.execute("""CREATE TABLE IF NOT EXISTS skill_compliance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_path TEXT,
        total_fields INTEGER,
        anthropic_fields INTEGER,
        enterprise_fields INTEGER,
        missing_fields TEXT,
        has_references_dir INTEGER,
        has_examples INTEGER,
        has_scripts_dir INTEGER,
        is_stub INTEGER,
        stub_reasons TEXT,
        score INTEGER,
        grade TEXT,
        error_count INTEGER,
        warning_count INTEGER,
        validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        source_modified_at TIMESTAMP,
        validator_version TEXT,
        run_id INTEGER,
        has_prd INTEGER DEFAULT 0,
        has_ard INTEGER DEFAULT 0,
        has_errors_md INTEGER DEFAULT 0,
        has_examples_md INTEGER DEFAULT 0,
        has_implementation_md INTEGER DEFAULT 0,
        reference_file_count INTEGER DEFAULT 0,
        has_config_dir INTEGER DEFAULT 0,
        gold_standard_pct INTEGER DEFAULT 0,
        jrig_passed INTEGER DEFAULT NULL,
        jrig_tier_blocked INTEGER DEFAULT NULL,
        jrig_baseline_delta REAL DEFAULT NULL,
        UNIQUE(skill_path, run_id)
    )""")

    # Idempotent migration: add JRig integration columns to pre-existing tables
    # that were created before these columns were part of the schema. Phase 5
    # of "Use the Printing Press to Learn" plan — JRig behavioral-eval results
    # join into skill_compliance so reports unify spec rubric + behavioral
    # verdict in one query.
    c.execute("PRAGMA table_info(skill_compliance)")
    existing_cols = {row[1] for row in c.fetchall()}
    for col_name, col_def in (
        ("jrig_passed", "INTEGER DEFAULT NULL"),
        ("jrig_tier_blocked", "INTEGER DEFAULT NULL"),
        ("jrig_baseline_delta", "REAL DEFAULT NULL"),
    ):
        if col_name not in existing_cols:
            c.execute(f"ALTER TABLE skill_compliance ADD COLUMN {col_name} {col_def}")

    # Same per-run-snapshot rule as skill_compliance: composite UNIQUE on
    # (agent_path, run_id) so re-validating the same discovery run preserves
    # history rather than overwriting it.
    c.execute("""CREATE TABLE IF NOT EXISTS agent_compliance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_path TEXT,
        total_fields INTEGER,
        anthropic_fields INTEGER,
        missing_fields TEXT,
        has_invalid_fields INTEGER,
        invalid_fields TEXT,
        is_plugin_agent INTEGER,
        error_count INTEGER,
        warning_count INTEGER,
        validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        validator_version TEXT,
        run_id INTEGER,
        UNIQUE(agent_path, run_id)
    )""")

    # Same per-run-snapshot rule as skill_compliance: composite UNIQUE on
    # (plugin_path, run_id).
    c.execute("""CREATE TABLE IF NOT EXISTS plugin_compliance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plugin_path TEXT,
        plugin_json_valid INTEGER,
        plugin_json_fields INTEGER,
        skill_count INTEGER,
        skill_avg_score REAL,
        agent_count INTEGER,
        has_hooks_json INTEGER,
        has_mcp_json INTEGER,
        has_license INTEGER,
        has_changelog INTEGER,
        overall_score REAL,
        error_count INTEGER,
        warning_count INTEGER,
        validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        validator_version TEXT,
        run_id INTEGER,
        UNIQUE(plugin_path, run_id)
    )""")

    # Forge proofs table — Phase 4A of the "Use the Printing Press to Learn"
    # plan. Stores per-plugin verification evidence produced during the
    # /skill-creator --forge generation pipeline (Tier 1+2+3 results) and
    # joined into the marketplace build at render time so the JRig-Verified
    # badge surfaces real evidence on plugin detail pages.
    forge_columns = [r[1] for r in c.execute("PRAGMA table_info(forge_proofs)").fetchall()]
    if "run_id" in forge_columns and "jrig_run_id" not in forge_columns:
        c.execute("ALTER TABLE forge_proofs RENAME COLUMN run_id TO jrig_run_id")
    c.execute("""CREATE TABLE IF NOT EXISTS forge_proofs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plugin_name TEXT NOT NULL,
        jrig_run_id INTEGER,
        discovery_run_id INTEGER REFERENCES discovery_runs(id),
        verification_type TEXT NOT NULL,
        passed INTEGER NOT NULL,
        evidence TEXT,
        evidence_class TEXT NOT NULL DEFAULT 'E0' CHECK(evidence_class IN ('E0', 'E1', 'E2', 'E3')),
        artifact_sha256 TEXT,
        artifact_uri TEXT,
        spec_sha256 TEXT,
        tool_version TEXT,
        kernel_version TEXT,
        provider TEXT,
        model TEXT,
        recorded_by_identity TEXT,
        producing_identity TEXT,
        layers_passed INTEGER DEFAULT NULL,
        total_layers INTEGER DEFAULT 7,
        baseline_delta REAL DEFAULT NULL,
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(plugin_name, verification_type, jrig_run_id)
    )""")

    # Evidence v2 migration. SQLite permits an ADD COLUMN foreign-key
    # reference with the required NULL default, so old ledger rows stay E0
    # while all future non-null discovery references are checked.
    forge_columns = {r[1] for r in c.execute("PRAGMA table_info(forge_proofs)").fetchall()}
    for col_name, col_def in (
        ("discovery_run_id", "INTEGER REFERENCES discovery_runs(id)"),
        ("evidence_class", "TEXT NOT NULL DEFAULT 'E0' CHECK(evidence_class IN ('E0', 'E1', 'E2', 'E3'))"),
        ("artifact_sha256", "TEXT"),
        ("artifact_uri", "TEXT"),
        ("spec_sha256", "TEXT"),
        ("tool_version", "TEXT"),
        ("kernel_version", "TEXT"),
        ("provider", "TEXT"),
        ("model", "TEXT"),
        ("recorded_by_identity", "TEXT"),
        ("producing_identity", "TEXT"),
    ):
        if col_name not in forge_columns:
            c.execute(f"ALTER TABLE forge_proofs ADD COLUMN {col_name} {col_def}")

    # Complete the legacy-UNIQUE migration started above: copy rows from the
    # renamed `*__migrate_tmp` tables into the freshly created tables (which
    # now carry the composite UNIQUE), then drop the temporaries. Carried at
    # this point because the new CREATE TABLE IF NOT EXISTS statements above
    # have just run.
    for table, tmp_name, old_cols in _migration_queue:
        new_cols = [r[1] for r in c.execute(f"PRAGMA table_info({table})").fetchall()]
        # Copy only columns that exist in BOTH (defensive — if the migration
        # ever lags behind a schema change, we still carry what we can rather
        # than crash). `id` is excluded so the new table renumbers cleanly.
        common = [col for col in old_cols if col in new_cols and col != "id"]
        if not common:
            c.execute(f"DROP TABLE {tmp_name}")
            continue
        col_list = ", ".join(common)
        c.execute(f"INSERT INTO {table} ({col_list}) SELECT {col_list} FROM {tmp_name}")
        c.execute(f"DROP TABLE {tmp_name}")

    # Helpful index for run-scoped queries.
    c.execute("CREATE INDEX IF NOT EXISTS idx_skill_compliance_run_id ON skill_compliance(run_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_agent_compliance_run_id ON agent_compliance(run_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_plugin_compliance_run_id ON plugin_compliance(run_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_forge_proofs_plugin ON forge_proofs(plugin_name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_forge_proofs_passed ON forge_proofs(passed)")

    # Purge legacy rows that pre-date run_id tagging. These rows have NULL
    # run_id and absolute /SKILL.md paths, and cannot be joined against
    # skills / plugins / agents without string gymnastics. They are safe to
    # delete because the current populate will regenerate any still-valid
    # rows using the new relative-path scheme.
    if current_run_id is not None:
        for tbl in ("skill_compliance", "agent_compliance", "plugin_compliance"):
            c.execute(f"DELETE FROM {tbl} WHERE run_id IS NULL")

    now = datetime.now(timezone.utc).isoformat()

    # Build the complete run snapshot before writing rows: duplicate stamping
    # cannot be established safely while visiting one skill at a time.
    stub_records = []
    for result in skill_results:
        raw = result.get("path", "")
        skill_file = Path(raw)
        if not skill_file.is_absolute():
            skill_file = repo_root_for_paths / skill_file
        if skill_file.is_dir():
            skill_file = skill_file / "SKILL.md"
        try:
            _fm, body = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        except Exception:
            body = ""
        parts = skill_file.parts
        try:
            pack = Path(*parts[: parts.index("skills")])
        except ValueError:
            pack = skill_file.parent
        stub_records.append({"path": skill_file, "pack": pack, "body": body, "grade": result.get("grade", "F")})
    deterministic_stubs = deterministic_stub_flags(stub_records)

    for result in skill_results:
        raw_skill_path = result.get("path", "")
        # Read the file via the raw (possibly absolute) path before normalizing
        # for storage — keeps file-system lookups working regardless of form.
        skill_path = _normalize_skill_path(raw_skill_path)
        score = result.get("score", 0)
        grade = result.get("grade", "F")
        errors = result.get("errors", 0)
        warnings = result.get("warnings", 0)

        # Locate the SKILL.md on disk regardless of which form was passed in.
        # skill_path is already normalized to a repo-relative directory
        # (e.g. plugins/foo/skills/bar). The file itself is <dir>/SKILL.md.
        skill_file = Path(raw_skill_path) if raw_skill_path else Path(skill_path) / "SKILL.md"
        if not skill_file.is_absolute():
            skill_file = repo_root_for_paths / skill_file
        if skill_file.is_dir():
            skill_file = skill_file / "SKILL.md"

        # Parse frontmatter and body from the file to count fields and detect stubs
        fm = {}
        body_for_stub = ""
        try:
            if skill_file.exists():
                content = skill_file.read_text(encoding="utf-8")
                fm_data, body_for_stub = parse_frontmatter(content)
                fm = fm_data
        except Exception:
            pass  # Frontmatter parse failure — field counts default to 0
        anthropic_fields = len([k for k in fm if k in SKILL_FIELDS and SKILL_FIELDS[k].get("source") == "anthropic"])
        enterprise_fields = len([k for k in fm if k in SKILL_FIELDS and SKILL_FIELDS[k].get("source") == "enterprise"])
        total_fields = anthropic_fields + enterprise_fields
        missing = [k for k in ALWAYS_REQUIRED if k not in fm]

        _db_stub_reasons = deterministic_stubs.get(str(skill_file), [])
        is_stub_val = 1 if _db_stub_reasons else 0

        try:
            mtime = (
                datetime.fromtimestamp(skill_file.stat().st_mtime, tz=timezone.utc).isoformat()
                if skill_file.exists()
                else None
            )
        except Exception:
            mtime = None

        skill_dir = skill_file.parent if skill_file else Path(".")
        has_refs = 1 if (skill_dir / "references").exists() else 0
        has_examples_dir = 1 if (skill_dir / "examples").exists() else 0
        has_scripts = 1 if (skill_dir / "scripts").exists() else 0

        # Gold standard doc tracking (crypto pack = reference)
        has_prd = 1 if (skill_dir / "PRD.md").exists() else 0
        has_ard = 1 if (skill_dir / "ARD.md").exists() else 0
        has_errors_md = 1 if (skill_dir / "references" / "errors.md").exists() else 0
        has_examples_md = 1 if (skill_dir / "references" / "examples.md").exists() else 0
        has_impl_md = (
            1
            if (skill_dir / "references" / "implementation.md").exists()
            or (skill_dir / "references" / "implementation-guide.md").exists()
            else 0
        )
        has_config = 1 if (skill_dir / "config").exists() else 0
        ref_file_count = len(list((skill_dir / "references").glob("*"))) if (skill_dir / "references").exists() else 0

        # Gold standard: 8 components (SKILL.md + PRD + ARD + refs/ + errors + examples + implementation + config)
        gold_components = sum([1, has_prd, has_ard, has_refs, has_errors_md, has_examples_md, has_impl_md, has_config])
        gold_pct = int(100 * gold_components / 8)

        # Upsert instead of INSERT OR REPLACE: REPLACE is delete-then-insert, so
        # re-validating the same discovery run silently reset every column NOT in
        # this statement's list to its default — including the j-rig-owned
        # jrig_passed / jrig_tier_blocked / jrig_baseline_delta columns, NULLing
        # paid behavioral-eval results (2026-07-14 ops review). DO UPDATE only
        # touches the validator-owned columns; j-rig columns survive.
        c.execute(
            """INSERT INTO skill_compliance
            (skill_path, total_fields, anthropic_fields, enterprise_fields, missing_fields,
             has_references_dir, has_examples, has_scripts_dir, is_stub, stub_reasons,
             score, grade, error_count, warning_count, validated_at, source_modified_at, validator_version,
             has_prd, has_ard, has_errors_md, has_examples_md, has_implementation_md,
             reference_file_count, has_config_dir, gold_standard_pct, run_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(skill_path, run_id) DO UPDATE SET
             total_fields=excluded.total_fields,
             anthropic_fields=excluded.anthropic_fields,
             enterprise_fields=excluded.enterprise_fields,
             missing_fields=excluded.missing_fields,
             has_references_dir=excluded.has_references_dir,
             has_examples=excluded.has_examples,
             has_scripts_dir=excluded.has_scripts_dir,
             is_stub=excluded.is_stub,
             stub_reasons=excluded.stub_reasons,
             score=excluded.score,
             grade=excluded.grade,
             error_count=excluded.error_count,
             warning_count=excluded.warning_count,
             validated_at=excluded.validated_at,
             source_modified_at=excluded.source_modified_at,
             validator_version=excluded.validator_version,
             has_prd=excluded.has_prd,
             has_ard=excluded.has_ard,
             has_errors_md=excluded.has_errors_md,
             has_examples_md=excluded.has_examples_md,
             has_implementation_md=excluded.has_implementation_md,
             reference_file_count=excluded.reference_file_count,
             has_config_dir=excluded.has_config_dir,
             gold_standard_pct=excluded.gold_standard_pct""",
            (
                skill_path,
                total_fields,
                anthropic_fields,
                enterprise_fields,
                json_module.dumps(missing),
                has_refs,
                has_examples_dir,
                has_scripts,
                is_stub_val,
                json_module.dumps(_db_stub_reasons),
                score,
                grade,
                errors,
                warnings,
                now,
                mtime,
                validator_version,
                has_prd,
                has_ard,
                has_errors_md,
                has_examples_md,
                has_impl_md,
                ref_file_count,
                has_config,
                gold_pct,
                current_run_id,
            ),
        )

    if agent_results:
        for result in agent_results:
            raw_agent_path = result.get("path", "")
            agent_path = _normalize_generic_path(raw_agent_path)
            errors = result.get("errors", 0)
            warnings = result.get("warnings", 0)

            # Resolve an absolute file path for reading, independent of the stored form.
            agent_file = Path(raw_agent_path) if raw_agent_path else Path(agent_path)
            if not agent_file.is_absolute():
                agent_file = repo_root_for_paths / agent_file

            # Parse agent frontmatter for field analysis
            agent_fm = {}
            try:
                if agent_file.exists():
                    content = agent_file.read_text(encoding="utf-8")
                    agent_fm, _ = parse_frontmatter(content)
            except Exception:
                pass

            anthropic_agent_fields = {
                "name",
                "description",
                "model",
                "effort",
                "maxTurns",
                "tools",
                "disallowedTools",
                "skills",
                "mcpServers",
                "hooks",
                "memory",
                "background",
                "isolation",
                "permissionMode",
            }
            invalid_agent_set = set(DEPRECATED_AGENT_FIELDS.keys()) | set(INVALID_AGENT_FIELDS.keys())

            a_total = len(agent_fm)
            a_anthropic = len([k for k in agent_fm if k in anthropic_agent_fields])
            a_missing = [k for k in ("name", "description") if k not in agent_fm]
            a_invalid = [k for k in agent_fm if k in invalid_agent_set]
            a_has_invalid = 1 if a_invalid else 0

            # Detect if plugin agent (has .claude-plugin/plugin.json ancestor)
            is_plugin = 0
            try:
                for parent in agent_file.parents:
                    if (parent / ".claude-plugin" / "plugin.json").exists():
                        is_plugin = 1
                        break
            except Exception:
                pass

            # Same upsert posture as skill_compliance: never delete-then-insert a
            # row another tool may later own columns on; update in place.
            c.execute(
                """INSERT INTO agent_compliance
                (agent_path, total_fields, anthropic_fields, missing_fields,
                 has_invalid_fields, invalid_fields, is_plugin_agent,
                 error_count, warning_count, validated_at, validator_version, run_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(agent_path, run_id) DO UPDATE SET
                 total_fields=excluded.total_fields,
                 anthropic_fields=excluded.anthropic_fields,
                 missing_fields=excluded.missing_fields,
                 has_invalid_fields=excluded.has_invalid_fields,
                 invalid_fields=excluded.invalid_fields,
                 is_plugin_agent=excluded.is_plugin_agent,
                 error_count=excluded.error_count,
                 warning_count=excluded.warning_count,
                 validated_at=excluded.validated_at,
                 validator_version=excluded.validator_version""",
                (
                    agent_path,
                    a_total,
                    a_anthropic,
                    json_module.dumps(a_missing),
                    a_has_invalid,
                    json_module.dumps(a_invalid),
                    is_plugin,
                    errors,
                    warnings,
                    now,
                    validator_version,
                    current_run_id,
                ),
            )

    # Populate plugin_compliance by rolling up skill scores per plugin
    if skill_results:
        plugin_skills: Dict[str, list] = {}  # absolute plugin root dir -> list of skill results
        for result in skill_results:
            raw_path = result.get("path", "")
            # Walk up the real filesystem path to find the plugin root; stored
            # paths are repo-relative so we resolve against repo_root_for_paths.
            try:
                fs_path = Path(raw_path)
                if not fs_path.is_absolute():
                    fs_path = repo_root_for_paths / fs_path
                if fs_path.name == "SKILL.md":
                    fs_path = fs_path.parent
                for parent in fs_path.parents:
                    if (parent / ".claude-plugin" / "plugin.json").exists():
                        plugin_path_key = str(parent)
                        if plugin_path_key not in plugin_skills:
                            plugin_skills[plugin_path_key] = []
                        plugin_skills[plugin_path_key].append(result)
                        break
            except Exception:
                pass

        for plugin_abs_path, skills_list in plugin_skills.items():
            p = Path(plugin_abs_path)
            # Store plugin_path in the same relative form used by the plugins table.
            plugin_path = _normalize_generic_path(plugin_abs_path)
            # Validate plugin.json
            pj_valid = 0
            pj_fields = 0
            try:
                pj = p / ".claude-plugin" / "plugin.json"
                if pj.exists():
                    data = json_module.loads(pj.read_text(encoding="utf-8"))
                    pj_valid = 1
                    pj_fields = len(data)
            except Exception:
                pass

            s_count = len(skills_list)
            s_scores = [s.get("score", 0) for s in skills_list if s.get("score")]
            s_avg = sum(s_scores) / len(s_scores) if s_scores else 0.0

            # Count agents
            agents_dir = p / "agents"
            a_count = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0

            # Check optional files
            has_hooks = 1 if (p / "hooks" / "hooks.json").exists() else 0
            has_mcp = 1 if (p / ".mcp.json").exists() else 0
            has_license = 1 if (p / "LICENSE").exists() or (p / "LICENSE.md").exists() else 0
            has_changelog = 1 if (p / "CHANGELOG.md").exists() else 0

            total_errors = sum(s.get("errors", 0) for s in skills_list)
            total_warnings = sum(s.get("warnings", 0) for s in skills_list)

            # Same upsert posture as skill_compliance (see comment there).
            c.execute(
                """INSERT INTO plugin_compliance
                (plugin_path, plugin_json_valid, plugin_json_fields, skill_count,
                 skill_avg_score, agent_count, has_hooks_json, has_mcp_json,
                 has_license, has_changelog, overall_score,
                 error_count, warning_count, validated_at, validator_version, run_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(plugin_path, run_id) DO UPDATE SET
                 plugin_json_valid=excluded.plugin_json_valid,
                 plugin_json_fields=excluded.plugin_json_fields,
                 skill_count=excluded.skill_count,
                 skill_avg_score=excluded.skill_avg_score,
                 agent_count=excluded.agent_count,
                 has_hooks_json=excluded.has_hooks_json,
                 has_mcp_json=excluded.has_mcp_json,
                 has_license=excluded.has_license,
                 has_changelog=excluded.has_changelog,
                 overall_score=excluded.overall_score,
                 error_count=excluded.error_count,
                 warning_count=excluded.warning_count,
                 validated_at=excluded.validated_at,
                 validator_version=excluded.validator_version""",
                (
                    plugin_path,
                    pj_valid,
                    pj_fields,
                    s_count,
                    s_avg,
                    a_count,
                    has_hooks,
                    has_mcp,
                    has_license,
                    has_changelog,
                    s_avg,
                    total_errors,
                    total_warnings,
                    now,
                    validator_version,
                    current_run_id,
                ),
            )

    # Sanity check: the populator's skill_compliance row count for this run_id
    # should join 1:1 with the inventory's skills table for the same run_id.
    # When they diverge by more than a small threshold, the two scanners are
    # walking different filesystems — historically caused by `skills/` subdirs
    # without SKILL.md being counted as skills (issue #594). Surface this
    # loudly so future drift gets caught immediately instead of silently
    # underweighting the grade rollups.
    if current_run_id is not None:
        try:
            inv_count = c.execute(
                "SELECT COUNT(*) FROM skills WHERE run_id = ?",
                (current_run_id,),
            ).fetchone()[0]
            c.execute(
                "SELECT COUNT(*) FROM skill_compliance WHERE run_id = ?",
                (current_run_id,),
            ).fetchone()[0]
            joined = c.execute(
                """SELECT COUNT(*)
                   FROM skills s
                   INNER JOIN skill_compliance sc
                     ON s.path = sc.skill_path AND s.run_id = sc.run_id
                   WHERE s.run_id = ?""",
                (current_run_id,),
            ).fetchone()[0]
            diff = inv_count - joined
            # Threshold: 10 skills OR 0.5% of inventory, whichever is larger.
            threshold = max(10, inv_count // 200)
            if diff > threshold:
                print(
                    f"[populate-db] WARN: inventory has {inv_count} skills "
                    f"for run_id={current_run_id}, but only {joined} have a "
                    f"compliance row that joins on path. Drift = {diff} "
                    f"(threshold = {threshold}). See issue #594 — usually "
                    f"means scan_packs_plugins_skills counted a subdir of "
                    f"skills/ that has no SKILL.md.",
                    file=sys.stderr,
                )
        except sqlite3.OperationalError:
            # Inventory table may not exist on a fresh DB — skip silently.
            pass

    conn.commit()
    conn.close()


# === MAIN ===


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-file OK lines and grades")
    parser.add_argument(
        "--safety-metrics",
        action="store_true",
        help=(
            "4.1.0 (E4.3/E4.4): emit the safety-ratchet metrics as JSON and exit — "
            "first-party SKILL.md files with bare (unscoped) Bash, the tier-2 "
            "tool-safety finding set, and every YAML shell-substitution occurrence. "
            "Mirror (.source.json) subtrees are excluded: upstream-owned."
        ),
    )
    parser.add_argument(
        "--structural-metrics",
        action="store_true",
        help=(
            "4.1.0 (E8.8): emit missing-required-frontmatter metrics as JSON and exit. "
            "First-party and provenance-marked mirror records are reported separately so "
            "the remediation ratchet can fail closed without editing upstream-owned files."
        ),
    )
    parser.add_argument(
        "--standard",
        action="store_true",
        help="Use standard tier (Anthropic spec exactly: name + description required). This is the default.",
    )
    parser.add_argument(
        "--marketplace",
        action="store_true",
        help="Use marketplace tier (Anthropic spec + IS polish recommendations as warnings, 100-point rubric). Auto-enabled in CI.",
    )
    # Deprecated alias for --marketplace. Kept for one minor version. CI configs
    # and scripts that still pass --enterprise continue to work but warn.
    parser.add_argument(
        "--enterprise",
        action="store_true",
        help="DEPRECATED alias for --marketplace. Use --marketplace instead.",
    )
    parser.add_argument(
        "--fail-on-warn",
        action="store_true",
        help="Treat warnings as errors (enterprise strict mode).",
    )
    parser.add_argument(
        "--check-description-budget",
        action="store_true",
        help="Warn if total skill description chars exceed token budget guidance.",
    )
    parser.add_argument(
        "--min-grade",
        type=str,
        default=None,
        choices=["A", "B", "C", "D"],
        help="Fail if any skill scores below this grade (e.g., --min-grade B)",
    )
    parser.add_argument(
        "--show-low-grades",
        action="store_true",
        help="Show skills with D or F grades even without verbose mode",
    )
    parser.add_argument(
        "--skills-only",
        action="store_true",
        help="Only validate SKILL.md files",
    )
    parser.add_argument(
        "--commands-only",
        action="store_true",
        help="Only validate command files",
    )
    parser.add_argument(
        "--agents-only",
        action="store_true",
        help="Only validate agent files",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON with per-skill scoring data",
    )
    parser.add_argument(
        "--emit-baseline",
        action="store_true",
        help=(
            "Emit the full marketplace compliance baseline JSON keyed by "
            "(path, rule_id, field), then exit. Intended for the dedicated CI "
            "baseline-capture transaction; never hand-edit its output."
        ),
    )
    parser.add_argument(
        "--populate-db",
        type=str,
        default=None,
        metavar="DB_PATH",
        help="Write validation results to SQLite database (e.g., freshie/inventory.sqlite)",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=repo_root,
        help="repository root to validate (default: this checkout)",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Run Intent Solutions Deep Evaluation Engine (10 dimensions, badges, rankings)",
    )
    parser.add_argument(
        "--report-format",
        type=str,
        default="terminal",
        choices=["terminal", "json", "markdown", "html"],
        help="Output format for --deep mode (default: terminal)",
    )
    parser.add_argument(
        "--kernel-shadow",
        action="store_true",
        help=(
            "Compare the hand-authored ALWAYS_REQUIRED set against the kernel "
            "(@intentsolutions/core authoring/v1) effective required set at startup "
            "(advisory; the hand-authored set stays authoritative per DR-049)"
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Promote plugin.json unrecognized-field WARNINGS to errors "
            "(mirrors `claude plugin validate --strict`). Wrong-type fields and "
            "a missing required 'name' are errors regardless of this flag."
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to a single SKILL.md file to validate (optional)",
    )
    args, _unknown = parser.parse_known_args()
    repo_root = args.repo_root.resolve()
    verbose = args.verbose
    machine_output = args.json or args.emit_baseline

    # Kernel shadow (DR-049, advisory): the comparison block is always embedded
    # in --json output; the human-readable startup print is opt-in via
    # --kernel-shadow. Never affects exit codes or verdicts. [11hl]
    kernel_shadow = kernel_shadow_report()
    if args.kernel_shadow:
        print_kernel_shadow(kernel_shadow)

    # Determine validation tier
    # Priority: explicit flag > auto-detect > default (standard)
    explicit_tier_flags = sum(1 for f in (args.marketplace, args.enterprise, args.standard) if f)
    if explicit_tier_flags > 1:
        print("ERROR: Cannot combine --standard, --marketplace, and --enterprise", file=sys.stderr)
        return 1
    if args.enterprise:
        # Keep working for one minor version; warn so CI configs get migrated.
        print(
            "WARN: --enterprise is deprecated, use --marketplace. "
            "(They are equivalent. This alias will be removed in a future release.)",
            file=sys.stderr,
        )
        tier = TIER_MARKETPLACE
    elif args.marketplace:
        tier = TIER_MARKETPLACE
    elif args.standard:
        tier = TIER_STANDARD
    elif os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true":
        tier = TIER_MARKETPLACE  # Auto-detect CI
    else:
        tier = TIER_STANDARD

    if args.emit_baseline:
        if args.standard or args.agents_only or args.commands_only or args.path:
            print(
                "ERROR: --emit-baseline requires a full --marketplace corpus run (no --standard, "
                "single path, --agents-only, or --commands-only)",
                file=sys.stderr,
            )
            return 1
        tier = TIER_MARKETPLACE

    # Single-file mode: validate just one SKILL.md
    if args.path:
        target = Path(args.path).resolve()
        if not target.exists():
            print(f"ERROR: File not found: {args.path}", file=sys.stderr)
            return 1
        if target.is_dir():
            # Plugin directory mode
            result = validate_plugin(target, tier, strict=args.strict)
            print(f"🔍 CLAUDE CODE PLUGIN VALIDATOR v7.0 / schema {SCHEMA_VERSION} ({tier} tier)")
            print(f"   Plugin mode: {target}")
            print(f"{'=' * 70}\n")
            if result["errors"]:
                for error in result["errors"]:
                    print(f"   ERROR: {error}")
            if result["warnings"]:
                for warning in result["warnings"]:
                    print(f"   WARN: {warning}")
            if result.get("infos"):
                for info in result["infos"]:
                    print(f"   INFO: {info}")
            print(f"\n   Skills: {result['skill_count']}, Agents: {result['agent_count']}")
            if result["avg_skill_score"]:
                print(f"   Average skill score: {result['avg_skill_score']:.1f}/100")
            return 1 if result["errors"] else 0
        elif target.name != "SKILL.md" and not target.name.endswith(".md"):
            print(f"ERROR: Expected a SKILL.md, .md file, or plugin directory: {args.path}", file=sys.stderr)
            return 1

        # Single-file SKILL.md/command/agent: emit JSON when --json or
        # --report-format=json. Phase A.0 fixture validation needs
        # machine-parseable output for SKILL.md single-file --marketplace runs.
        # Schema matches the multi-file --json array shape (one element here)
        # plus full errors/warnings lists + breakdown for fixture assertions.
        # Deep-eval JSON is gated separately below on (args.deep and args.report_format == "json").
        json_mode = bool(args.json) or args.report_format == "json"

        if not json_mode:
            print(f"🔍 CLAUDE CODE PLUGIN VALIDATOR v7.0 / schema {SCHEMA_VERSION} ({tier} tier)")
            print(f"   Single-file mode: {target}")
            print(f"{'=' * 70}\n")

        if target.name == "SKILL.md":
            result = validate_skill(target, tier)
            if "fatal" in result:
                if json_mode:
                    print(
                        json_module.dumps(
                            [
                                {
                                    "path": str(target),
                                    "fatal": result["fatal"],
                                },
                                # Trailing advisory element; consumers skip
                                # entries carrying the kernel_shadow key.
                                {"kernel_shadow": kernel_shadow},
                            ]
                        )
                    )
                else:
                    print(f"❌ FATAL: {result['fatal']}")
                return 1

            grade_info = result.get("grade", {})
            score = grade_info.get("score", 0)
            letter = grade_info.get("grade", "F")

            if json_mode:
                print(
                    json_module.dumps(
                        [
                            {
                                "path": str(target),
                                "tier": tier,
                                "schema_version": SCHEMA_VERSION,
                                "score": score,
                                "grade": letter,
                                "errors": result.get("errors", []),
                                "warnings": result.get("warnings", []),
                                "infos": result.get("infos", []),
                                "breakdown": grade_info.get("breakdown", {}),
                            },
                            # Trailing advisory element; consumers skip
                            # entries carrying the kernel_shadow key.
                            {"kernel_shadow": kernel_shadow},
                        ]
                    )
                )
                # Skip the terminal grade-table render below; deep-eval (if --deep)
                # still runs and prints its own JSON via the existing block.
                if not args.deep:
                    return 1 if result["errors"] else 0
            else:
                if result["errors"]:
                    for error in result["errors"]:
                        print(f"   ERROR: {error}")
                if result["warnings"]:
                    for warning in result["warnings"]:
                        print(f"   WARN: {warning}")
                if result.get("infos"):
                    for info in result["infos"]:
                        print(f"   INFO: {info}")

                # Always show grade in single-file mode
                print(f"\n{'=' * 70}")
                print(f"📊 GRADE: {letter} ({score}/100)")
                print(f"{'=' * 70}")
                breakdown = grade_info.get("breakdown", {})
                for pillar_name, pillar_data in breakdown.items():
                    if pillar_name == "modifiers":
                        mod_score = pillar_data.get("score", 0)
                        print(f"  {'Modifiers':<30} {mod_score:+d}")
                        for item_name, (pts, note) in pillar_data.get("items", {}).items():
                            print(f"    {item_name:<28} {pts:+d} - {note}")
                    else:
                        pil_score = pillar_data.get("score", 0)
                        pil_max = pillar_data.get("max", 0)
                        print(f"  {pillar_name.replace('_', ' ').title():<30} {pil_score}/{pil_max}")
                        for item_name, (pts, note) in pillar_data.get("breakdown", {}).items():
                            print(f"    {item_name:<28} {pts} - {note}")
                print(f"{'=' * 70}")

            # Deep eval in single-file mode
            if args.deep and target.name == "SKILL.md":
                try:
                    from deep_eval.engine import DeepEvalEngine
                    from deep_eval.reporter import format_terminal, format_json

                    print(f"\n{'=' * 70}")
                    print("🔬 DEEP EVALUATION")
                    print(f"{'=' * 70}\n")

                    content = target.read_text(encoding="utf-8")
                    fm, body = parse_frontmatter(content)
                    # LLM judging now lives at the workflow layer (see
                    # scripts/pr-prescreen/summarize.py). Validator stays
                    # deterministic.
                    engine = DeepEvalEngine(use_llm=False, verbose=verbose)
                    deep_result = engine.evaluate_skill(
                        target,
                        body,
                        fm,
                        letter_grade=letter,
                        deterministic_score=score,
                    )
                    deep_summary = engine.summary([deep_result])

                    if args.report_format == "json":
                        print(format_json([deep_result], deep_summary))
                    else:
                        print(format_terminal([deep_result], deep_summary, verbose=True))

                    # Write to DB if requested
                    if args.populate_db:
                        from deep_eval.db import populate_deep_eval_db

                        run_id = populate_deep_eval_db(
                            args.populate_db,
                            [deep_result],
                            deep_summary,
                            run_config={"single_file": True, "use_llm": False},
                        )
                        print(f"📊 Deep eval written to {args.populate_db} (run_id={run_id})")

                except ImportError as e:
                    print(f"\n❌ Deep eval not available: {e}")
                except Exception as e:
                    print(f"\n❌ Deep eval failed: {e}")

            return 1 if result["errors"] else 0
        else:
            # Command or agent file
            if "/commands/" in str(target):
                result = validate_command(target)
            elif "/agents/" in str(target):
                result = validate_agent(target)
            else:
                print(f"Cannot determine file type for: {target}")
                print("File must be in a commands/ or agents/ directory, or named SKILL.md")
                return 1

            if "fatal" in result:
                print(f"❌ FATAL: {result['fatal']}")
                return 1
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"   ERROR: {error}")
                return 1
            if result.get("warnings"):
                for warning in result["warnings"]:
                    print(f"   WARN: {warning}")
            print("\n✅ Validation passed")
            return 0

    if args.safety_metrics:

        def _is_mirror(path: Path) -> bool:
            probe = path.parent
            while probe != repo_root and probe != probe.parent:
                if (probe / ".source.json").exists():
                    return True
                probe = probe.parent
            return False

        bare_bash: List[str] = []
        tier2_tool_safety: List[str] = []
        shell_substitution: List[str] = []
        for skill_path in find_skill_files(repo_root):
            if _is_mirror(skill_path):
                continue
            rel = str(skill_path.relative_to(repo_root))
            try:
                content = skill_path.read_text(encoding="utf-8")
                fm, body = parse_frontmatter(content)
            except Exception:
                continue
            if not fm:
                continue
            tools_value = fm.get("allowed-tools")
            parsed = parse_allowed_tools(tools_value) if tools_value else []
            if any(t.strip() == "Bash" for t in parsed):
                bare_bash.append(rel)
                t2_errors, _t2w = tier2_check_tool_safety(body, fm)
                if t2_errors:
                    tier2_tool_safety.append(rel)
            for issue in check_yaml_shell_substitution(fm):
                field = issue.split("'")[1] if "'" in issue else "?"
                shell_substitution.append(f"{rel}::{field}")
        import json as _json

        metrics = {
            "schema_version": SCHEMA_VERSION,
            "bare_bash": sorted(bare_bash),
            "tier2_tool_safety": sorted(tier2_tool_safety),
            "shell_substitution": sorted(shell_substitution),
        }
        print(_json.dumps(metrics, indent=1))
        return 0

    if args.structural_metrics:

        def _is_mirror(path: Path) -> bool:
            probe = path.parent
            while probe != repo_root and probe != probe.parent:
                if (probe / ".source.json").exists():
                    return True
                probe = probe.parent
            return False

        missing_pattern = re.compile(r"^\[frontmatter\] Missing required field: '([^']+)' \(marketplace\)$")
        first_party: List[str] = []
        mirrors: List[str] = []
        for skill_path in find_skill_files(repo_root):
            rel = str(skill_path.relative_to(repo_root))
            result = validate_skill(skill_path, TIER_MARKETPLACE)
            for error in result.get("errors", []):
                match = missing_pattern.match(error)
                if not match:
                    continue
                member = f"{rel}::{match.group(1)}"
                (mirrors if _is_mirror(skill_path) else first_party).append(member)
        import json as _json

        metrics = {
            "schema_version": SCHEMA_VERSION,
            "first_party_missing_required_frontmatter": sorted(first_party),
            "mirror_missing_required_frontmatter": sorted(mirrors),
        }
        print(_json.dumps(metrics, indent=1))
        return 0

    # Determine what to validate
    validate_skills = not args.commands_only and not args.agents_only
    validate_commands = not args.skills_only and not args.agents_only
    validate_agents = not args.skills_only and not args.commands_only

    # Find files based on what we're validating
    skills = find_skill_files(repo_root) if validate_skills else []
    commands = find_command_files(repo_root) if validate_commands else []
    agents = find_agent_files(repo_root) if validate_agents else []

    total_files = len(skills) + len(commands) + len(agents)
    if total_files == 0:
        if args.emit_baseline:
            baseline = marketplace_baseline_payload(
                findings=[],
                skill_files=0,
                command_files=0,
                plugin_dirs=len(find_plugin_json_files(repo_root)),
                agent_files=0,
                grade_a_plus_b=0,
                repo_root=repo_root,
            )
            print(json_module.dumps(baseline, indent=2, sort_keys=True))
            return 0
        print("No files found to validate.")
        return 0

    if not machine_output:
        print(f"🔍 CLAUDE CODE PLUGIN VALIDATOR v7.0 / schema {SCHEMA_VERSION} ({tier} tier)")
        if tier == TIER_MARKETPLACE:
            print("   Marketplace Polish (Anthropic spec + IS 100-point rubric)")
        else:
            print("   Standard (Anthropic spec exactly: name + description required)")
        print(f"{'=' * 70}\n")
        if validate_skills:
            print(f"Found {len(skills)} SKILL.md files")
        if validate_commands:
            print(f"Found {len(commands)} command files")
        if validate_agents:
            print(f"Found {len(agents)} agent files")
        print()

    total_errors = 0
    total_warnings = 0
    total_description_chars = 0
    files_with_errors = []
    files_with_warnings = []
    files_compliant = []

    # Grade tracking
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    grade_scores = []  # For average calculation
    low_grade_skills = []  # Skills with D or F
    below_min_grade = []  # Skills below --min-grade threshold

    grade_thresholds = {"A": 90, "B": 80, "C": 70, "D": 60}
    json_skill_results = []  # Collected for --json output
    baseline_findings: List[Tuple[str, str, str]] = []

    for skill in skills:
        rel = skill.relative_to(repo_root)
        result = validate_skill(skill, tier)

        if "fatal" in result:
            if not machine_output:
                print(f"❌ {rel}: FATAL - {result['fatal']}")
            total_errors += 1
            files_with_errors.append(str(rel))
            json_skill_results.append(
                {
                    "path": str(rel),
                    "fatal": result["fatal"],
                }
            )
            if args.emit_baseline:
                baseline_findings.append(baseline_finding_triple(str(rel), f"[fatal] {result['fatal']}"))
            continue

        has_issues = False

        # Track grade
        grade_info = result.get("grade", {})
        score = grade_info.get("score", 0)
        letter = grade_info.get("grade", "F")
        grade_counts[letter] += 1
        grade_scores.append(score)

        json_skill_results.append(
            {
                "path": str(skill),
                "score": score,
                "grade": letter,
                "errors": len(result.get("errors", [])),
                # Consumers that make a disposition decision need the canonical
                # diagnostic text, not only an opaque count.  This is additive
                # to the long-standing --json contract and keeps classification
                # tied to the validator rather than a second parser.
                "error_details": result.get("errors", []),
                "warnings": len(result.get("warnings", [])),
            }
        )

        # Check min-grade threshold
        if args.min_grade:
            min_threshold = grade_thresholds.get(args.min_grade, 0)
            if score < min_threshold:
                below_min_grade.append((str(rel), score, letter))

        # Track low grades
        if letter in ["D", "F"]:
            low_grade_skills.append((str(rel), score, letter, grade_info.get("breakdown", {})))

        if result["errors"]:
            if not machine_output:
                print(f"❌ {rel}:")
                for error in result["errors"]:
                    print(f"   ERROR: {error}")
            total_errors += len(result["errors"])
            files_with_errors.append(str(rel))
            has_issues = True
            if args.emit_baseline:
                baseline_findings.extend(baseline_finding_triple(str(rel), error) for error in result["errors"])

        if result["warnings"]:
            if not machine_output:
                if not has_issues:
                    print(f"⚠️  {rel}:")
                for warning in result["warnings"]:
                    print(f"   WARN: {warning}")
            total_warnings += len(result["warnings"])
            if str(rel) not in files_with_errors:
                files_with_warnings.append(str(rel))
            has_issues = True

        if result.get("infos") and verbose and not machine_output:
            if not has_issues:
                print(f"💡 {rel}:")
            for info in result["infos"]:
                print(f"   INFO: {info}")

        if verbose and not has_issues and not result.get("infos") and not machine_output:
            print(f"✅ {rel} - {letter} ({score}/100) ({result['word_count']} words, {result['line_count']} lines)")

        if not result["errors"] and not result["warnings"]:
            files_compliant.append(str(rel))

        total_description_chars += int(result.get("description_length") or 0)

    # JSON output mode: emit machine-readable results and exit. The trailing
    # kernel_shadow element is advisory (DR-049); consumers skip entries
    # carrying the kernel_shadow key.
    if args.json:
        print(json_module.dumps(json_skill_results + [{"kernel_shadow": kernel_shadow}]))
        return 0

    # Validate commands
    for cmd in commands:
        rel = cmd.relative_to(repo_root)
        result = validate_command(cmd)

        if "fatal" in result:
            if not machine_output:
                print(f"❌ {rel} (command): FATAL - {result['fatal']}")
            total_errors += 1
            files_with_errors.append(str(rel))
            if args.emit_baseline:
                baseline_findings.append(baseline_finding_triple(str(rel), f"[fatal] {result['fatal']}"))
            continue

        if result["errors"]:
            if not machine_output:
                print(f"❌ {rel} (command):")
                for error in result["errors"]:
                    print(f"   ERROR: {error}")
            total_errors += len(result["errors"])
            files_with_errors.append(str(rel))
            if args.emit_baseline:
                baseline_findings.extend(baseline_finding_triple(str(rel), error) for error in result["errors"])
        elif result["warnings"]:
            if not machine_output:
                print(f"⚠️  {rel} (command):")
                for warning in result["warnings"]:
                    print(f"   WARN: {warning}")
            total_warnings += len(result["warnings"])
            files_with_warnings.append(str(rel))
        else:
            files_compliant.append(str(rel))
            if verbose:
                print(f"✅ {rel} (command) - OK")

    # Validate agents
    json_agent_results = []
    for agent in agents:
        rel = agent.relative_to(repo_root)
        result = validate_agent(agent)

        if "fatal" in result:
            if not machine_output:
                print(f"❌ {rel} (agent): FATAL - {result['fatal']}")
            total_errors += 1
            files_with_errors.append(str(rel))
            json_agent_results.append({"path": str(agent), "errors": 1, "warnings": 0})
            if args.emit_baseline:
                baseline_findings.append(baseline_finding_triple(str(rel), f"[fatal] {result['fatal']}"))
            continue

        err_count = len(result["errors"])
        warn_count = len(result["warnings"])
        json_agent_results.append({"path": str(agent), "errors": err_count, "warnings": warn_count})

        if result["errors"]:
            if not machine_output:
                print(f"❌ {rel} (agent):")
                for error in result["errors"]:
                    print(f"   ERROR: {error}")
            total_errors += len(result["errors"])
            files_with_errors.append(str(rel))
            if args.emit_baseline:
                baseline_findings.extend(baseline_finding_triple(str(rel), error) for error in result["errors"])
        elif result["warnings"]:
            if not machine_output:
                print(f"⚠️  {rel} (agent):")
                for warning in result["warnings"]:
                    print(f"   WARN: {warning}")
            total_warnings += len(result["warnings"])
            files_with_warnings.append(str(rel))
        else:
            files_compliant.append(str(rel))
            if verbose:
                print(f"✅ {rel} (agent) - OK")

    # Validate plugin.json files (batch mode)
    plugin_jsons = find_plugin_json_files(repo_root)
    if plugin_jsons and not machine_output:
        print(f"\nFound {len(plugin_jsons)} plugin.json files")
    for pj_file in plugin_jsons:
        rel = pj_file.relative_to(repo_root)
        result = validate_plugin_json(pj_file, strict=args.strict)

        if result["errors"]:
            if not machine_output:
                print(f"❌ {rel} (plugin.json):")
                for error in result["errors"]:
                    print(f"   ERROR: {error}")
            total_errors += len(result["errors"])
            files_with_errors.append(str(rel))
            if args.emit_baseline:
                baseline_findings.extend(baseline_finding_triple(str(rel), error) for error in result["errors"])
        elif result["warnings"]:
            if not machine_output:
                print(f"⚠️  {rel} (plugin.json):")
                for warning in result["warnings"]:
                    print(f"   WARN: {warning}")
            total_warnings += len(result["warnings"])
            files_with_warnings.append(str(rel))
        else:
            files_compliant.append(str(rel))
            if verbose:
                print(f"✅ {rel} (plugin.json) - OK")

    if args.emit_baseline:
        baseline = marketplace_baseline_payload(
            findings=baseline_findings,
            skill_files=len(skills),
            command_files=len(commands),
            plugin_dirs=len(plugin_jsons),
            agent_files=len(agents),
            grade_a_plus_b=grade_counts["A"] + grade_counts["B"],
            repo_root=repo_root,
        )
        print(json_module.dumps(baseline, indent=2, sort_keys=True))
        return 0

    # Populate compliance database if requested (after all validations complete).
    # A failure here must NOT be swallowed: the freshie cycle's next step
    # (dolt-sync) would tag a run with zero fresh compliance rows and grades.csv
    # would silently regress to previous-run grades. The flag below forces a
    # distinct non-zero exit (see the end of main) so the operator/CI can tell
    # "DB write failed" apart from ordinary corpus compliance errors.
    populate_db_failed = False
    if args.populate_db:
        try:
            populate_compliance_db(
                args.populate_db, json_skill_results, agent_results=json_agent_results, validator_version="5.0.0"
            )
            print(f"\n📊 Compliance data written to {args.populate_db}", flush=True)
            print(f"   skill_compliance: {len(json_skill_results)} rows", flush=True)
            print(f"   agent_compliance: {len(json_agent_results)} rows", flush=True)
        except Exception as e:
            populate_db_failed = True
            print(f"\n❌ Failed to write compliance DB: {e}", file=sys.stderr, flush=True)
            import traceback

            traceback.print_exc()

    # === DEEP EVALUATION ENGINE ===
    if args.deep and skills:
        try:
            from deep_eval.engine import DeepEvalEngine
            from deep_eval.reporter import format_terminal, format_json, format_markdown, format_html
            from deep_eval.db import populate_deep_eval_db

            print(f"\n{'=' * 70}")
            print("🔬 INTENT SOLUTIONS DEEP EVALUATION ENGINE v1.0")
            print(f"{'=' * 70}\n")

            # LLM judging now lives at the workflow layer (see
            # scripts/pr-prescreen/summarize.py). Validator stays deterministic.
            use_llm = False
            engine = DeepEvalEngine(use_llm=use_llm, verbose=verbose)

            # Build skill data for deep eval from already-validated skills
            deep_eval_skills = []
            for skill_path in skills:
                try:
                    content = skill_path.read_text(encoding="utf-8")
                    fm, body = parse_frontmatter(content)
                    # Find matching json result for grade/score
                    matching = [
                        r
                        for r in json_skill_results
                        if Path(r.get("path", "")).resolve() == skill_path.resolve()
                        or r.get("path", "").endswith(str(skill_path.relative_to(repo_root)))
                    ]
                    grade = matching[0].get("grade", "F") if matching else "F"
                    score = matching[0].get("score", 0) if matching else 0
                    deep_eval_skills.append(
                        {
                            "path": str(skill_path),
                            "body": body,
                            "fm": fm,
                            "name": fm.get("name", skill_path.stem),
                            "grade": grade,
                            "score": score,
                        }
                    )
                except Exception:
                    continue

            if deep_eval_skills:
                # Run deep evaluation
                deep_results = engine.evaluate_batch(deep_eval_skills)
                deep_summary = engine.summary(deep_results)

                # Run rankings
                deep_rankings = engine.rank_results(deep_results)

                # Output in requested format
                if args.report_format == "json":
                    print(format_json(deep_results, deep_summary, deep_rankings))
                elif args.report_format == "markdown":
                    print(format_markdown(deep_results, deep_summary, deep_rankings))
                elif args.report_format == "html":
                    html_output = format_html(deep_results, deep_summary, deep_rankings)
                    html_path = repo_root / "deep-eval-report.html"
                    html_path.write_text(html_output, encoding="utf-8")
                    print(f"HTML report written to: {html_path}")
                else:
                    print(format_terminal(deep_results, deep_summary, deep_rankings, verbose=verbose))

                # Write to freshie DB if --populate-db is set
                if args.populate_db:
                    try:
                        run_id = populate_deep_eval_db(
                            args.populate_db,
                            deep_results,
                            deep_summary,
                            rankings=deep_rankings,
                            run_config={"use_llm": use_llm},
                        )
                        print(f"\n📊 Deep eval data written to {args.populate_db} (run_id={run_id})")
                        print(f"   deep_eval_results: {len(deep_results)} rows")
                    except Exception as e:
                        populate_db_failed = True
                        print(f"\n❌ Failed to write deep eval DB: {e}", file=sys.stderr)

        except ImportError as e:
            print(f"\n❌ Deep eval engine not available: {e}")
            print("   Ensure scripts/deep_eval/ package exists")
        except Exception as e:
            print(f"\n❌ Deep eval failed: {e}")
            import traceback

            traceback.print_exc()

    # Show low grade skills if requested
    if args.show_low_grades and low_grade_skills:
        print(f"\n{'=' * 70}")
        print("📉 LOW GRADE SKILLS (D or F)")
        print(f"{'=' * 70}")
        for path, score, letter, breakdown in low_grade_skills:
            print(f"\n{letter} ({score}/100): {path}")
            if "progressive_disclosure" in breakdown:
                pda = breakdown["progressive_disclosure"]
                print(f"   PDA: {pda['score']}/{pda['max']}")
                for key, (pts, note) in pda.get("breakdown", {}).items():
                    print(f"      {key}: {pts} pts - {note}")

    # Summary
    print(f"\n{'=' * 70}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'=' * 70}")
    # The denominator must cover every population the compliant/error lists
    # can contain. Plugin manifests are validated in their own lane below the
    # three markdown lanes; excluding them produced impossible rates (224.1%)
    # whenever manifests passed — blueprint 727 bead 4.12 / 6.9.
    total_validated = len(skills) + len(commands) + len(agents) + len(plugin_jsons)
    if skills:
        print(f"Skills validated: {len(skills)}")
    if commands:
        print(f"Commands validated: {len(commands)}")
    if agents:
        print(f"Agents validated: {len(agents)}")
    if plugin_jsons:
        print(f"Plugin manifests validated: {len(plugin_jsons)}")
    print(f"Total files: {total_validated}")
    print(f"✅ Fully compliant: {len(files_compliant)}")
    print(f"⚠️  Warnings only: {len(files_with_warnings)}")
    print(f"❌ With errors: {len(files_with_errors)}")
    print(f"{'=' * 70}")

    # Compliance rate
    compliant_pct = compute_compliance_rate(len(files_compliant), total_validated)
    print(f"\n📈 Compliance rate: {compliant_pct:.1f}%")

    # Grade Distribution
    print(f"\n{'=' * 70}")
    print("📊 INTENT SOLUTIONS GRADE REPORT")
    print(f"{'=' * 70}")

    avg_score = sum(grade_scores) / len(grade_scores) if grade_scores else 0
    avg_grade = calculate_grade(int(avg_score))
    print(f"Average Score: {avg_score:.1f}/100 ({avg_grade})")
    print()
    print("Grade Distribution:")
    for letter in ["A", "B", "C", "D", "F"]:
        count = grade_counts[letter]
        pct = (count / len(skills) * 100) if skills else 0
        bar = "█" * int(pct / 2)
        emoji = {"A": "🏆", "B": "✅", "C": "⚠️", "D": "📉", "F": "❌"}[letter]
        print(f"  {emoji} {letter}: {count:4d} ({pct:5.1f}%) {bar}")

    # Quality metrics
    print()
    a_b_count = grade_counts["A"] + grade_counts["B"]
    a_b_pct = (a_b_count / len(skills) * 100) if skills else 0
    print(f"Production Ready (A+B): {a_b_count} ({a_b_pct:.1f}%)")

    d_f_count = grade_counts["D"] + grade_counts["F"]
    d_f_pct = (d_f_count / len(skills) * 100) if skills else 0
    print(f"Needs Work (D+F): {d_f_count} ({d_f_pct:.1f}%)")

    print(f"{'=' * 70}")

    if args.check_description_budget and total_description_chars >= TOTAL_DESCRIPTION_BUDGET_WARN:
        msg = (
            f"\n⚠️  Skill description budget: {total_description_chars} chars "
            f"(warn at {TOTAL_DESCRIPTION_BUDGET_WARN}, cap {TOTAL_DESCRIPTION_BUDGET_ERROR})"
        )
        print(msg)
        total_warnings += 1

    # A requested --populate-db that failed overrides every other exit path:
    # exit 2 (distinct from the compliance-error exit 1) so callers — and the
    # operator running the freshie cycle — cannot mistake "DB not written" for
    # the routine corpus-errors failure that CI already tolerates with `|| true`.
    if args.populate_db and populate_db_failed:
        print(
            f"\n❌ --populate-db was requested but the write to {args.populate_db} FAILED "
            f"(see traceback above). Compliance rows for this run were NOT written — "
            f"do NOT run dolt-sync until this is fixed, or grades.csv will silently "
            f"regress to the previous run's grades.",
            file=sys.stderr,
        )
        return 2

    # Check min-grade violations
    if args.min_grade and below_min_grade:
        print(f"\n❌ {len(below_min_grade)} skill(s) below minimum grade {args.min_grade}:")
        for path, score, letter in below_min_grade[:10]:  # Show first 10
            print(f"   {letter} ({score}/100): {path}")
        if len(below_min_grade) > 10:
            print(f"   ... and {len(below_min_grade) - 10} more")
        return 1

    # When --min-grade is set, errors are REPORTED but only grade violations BLOCK.
    # This allows CI to enforce quality floor without requiring zero compliance gaps.
    if args.min_grade:
        if total_errors > 0:
            print(
                f"\n⚠️  {total_errors} compliance errors reported ({tier} tier) — not blocking (--min-grade {args.min_grade} gate passed)"
            )
            print(f"   All graded skills meet minimum grade {args.min_grade}")
        else:
            print(f"\n✅ All skills fully compliant! ({tier} tier)")
        return 0

    if total_errors > 0:
        print(f"\n❌ Validation FAILED with {total_errors} errors ({tier} tier)")
        if tier == TIER_MARKETPLACE:
            print("\nTo fix: Address errors above. The IS marketplace tier requires the 8-field")
            print("enterprise set (name, description, allowed-tools, version, author, license,")
            print("compatibility, tags) per schema 3.3.0+ — missing fields are errors, not warnings.")
            print("Use --standard for Anthropic-spec-only validation (name + description only).")
        return 1
    elif total_warnings > 0 and args.fail_on_warn:
        print(f"\n❌ Validation FAILED due to {total_warnings} warning(s) (--fail-on-warn)")
        return 1
    elif total_warnings > 0:
        print(f"\n⚠️  Validation PASSED with {total_warnings} warnings ({tier} tier)")
        print("(Warnings are best practices / marketplace polish - not blocking)")
        return 0
    else:
        print(f"\n✅ All skills fully compliant! ({tier} tier)")
        if tier == TIER_MARKETPLACE:
            print("   - Anthropic spec (name + description) ✓")
            print("   - AgentSkills.io optional fields ✓")
            print("   - Intent Solutions marketplace polish ✓")
            print("   - 100-point grading ✓")
        else:
            print("   - Anthropic spec (name + description) ✓")
        return 0


if __name__ == "__main__":
    sys.exit(main())
