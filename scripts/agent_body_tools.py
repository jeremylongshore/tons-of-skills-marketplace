# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Jeremy Longshore
"""Marketplace-owned deterministic agent body/tool-list findings.

Extracted unchanged from scripts/validate-skills-schema.py at marketplace commit
0500b275e963c027f6b410e8c49c0446945c574e (MIT; see repository LICENSE).
Original extracted block SHA256: 077954c0abf195d62207ef681f5908b258c59bc546ad0e71f51a8c5aeca4d3a7

The callable returns the existing (errors, warnings) lists, with no filesystem,
network, environment, executable or model access. It is a lexical checker, not
proof that a tool is invoked or blocked at runtime. Missing `tools` and explicitly
empty `tools` retain the same legacy findings here; a host may inherit tools when
the field is omitted. Body prose can describe parent-owned calls. Downstream
adapters must disclose these limits rather than turn findings into execution
claims. Existing marketplace caller severity is intentionally unchanged.
"""

import re
from typing import Any, Dict, List, Tuple

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

