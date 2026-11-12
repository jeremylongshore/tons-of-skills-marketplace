# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Jeremy Longshore
"""Marketplace-owned skill production heuristics, not runtime security proof.

Extracted from validate-skills-schema.py at ed4778951a4007d1ca56781a468233212e371502.
Keep the full repository MIT LICENSE when redistributing. Caller supplies the
canonical fence pattern; the source-owned descriptor records its packaged form.
Warnings/errors and ordering intentionally retain the legacy behavior.
"""

import re
from pathlib import Path
from typing import Any, List, Tuple


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


def tier2_check_orchestration_bounds(body: str, *, fence_pattern: re.Pattern[str]) -> Tuple[List[str], List[str]]:
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
        if fence_pattern.match(line):
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


def validate_tier2_production_gate(
    path: Path, body: str, fm: dict, *, fence_pattern: re.Pattern[str]
) -> Tuple[List[str], List[str], List[str]]:
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
    e5, w5 = tier2_check_orchestration_bounds(body, fence_pattern=fence_pattern)

    errors.extend(e1 + e2 + e3 + e4 + e5)
    warnings.extend(w1 + w2 + w3 + w4 + w5)
    return errors, warnings, infos
