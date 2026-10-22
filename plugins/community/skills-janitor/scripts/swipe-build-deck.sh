#!/bin/bash
# Skills Janitor - Swipe Deck Builder
# Joins scan + tokencost + usage data into a sorted deck of cards for the
# swipe TUI. Each card has the verdict score, label, and everything the TUI
# needs to render and act on a skill. Sort order is "most likely waste first"
# so a user can hit `← delete` through the top of the deck and quit early.

set -euo pipefail

command -v python3 &>/dev/null || { echo "ERROR: python3 required" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Per-process default path — a fixed /tmp name made concurrent runs clobber
# each other's decks.
OUTPUT="${1:-/tmp/janitor-swipe-deck.$$.json}"

# Refresh usage data (writes data/usage-history.json that tokencost reads)
bash "$SCRIPT_DIR/usage.sh" --json >/dev/null 2>&1 || true

# Get tokencost JSON (this already joins scan + usage for us)
TMP_TOKEN=$(mktemp)
trap "rm -f $TMP_TOKEN" EXIT
bash "$SCRIPT_DIR/tokencost.sh" --json > "$TMP_TOKEN" 2>/dev/null

# Get raw scan output for the scope + path detail (tokencost flattens these)
TMP_SCAN=$(mktemp)
TMP_MCP=$(mktemp)
trap "rm -f $TMP_TOKEN $TMP_SCAN $TMP_MCP" EXIT
bash "$SCRIPT_DIR/scan.sh" > "$TMP_SCAN" 2>/dev/null

# MCP servers join the deck too (v1.7) — their tool schemas are always
# loaded, so an unused server is prime swipe material.
bash "$SCRIPT_DIR/mcp.sh" --json > "$TMP_MCP" 2>/dev/null || echo '{}' > "$TMP_MCP"

python3 - "$TMP_TOKEN" "$TMP_SCAN" "$OUTPUT" "$TMP_MCP" <<'PYEOF'
import json, sys, os
from datetime import datetime, timezone

token_file, scan_file, out_file = sys.argv[1], sys.argv[2], sys.argv[3]
mcp_file = sys.argv[4] if len(sys.argv) > 4 else ""

with open(token_file) as f:
    tcost = json.load(f)
with open(scan_file) as f:
    scan = json.load(f)

# Index scan records two ways: by realpath (primary — two physical copies of
# the same skill name must map to their OWN cards/paths, or one copy becomes
# undeletable) and by qualified_name (fallback).
scan_by_realpath = {}
scan_index = {}
for s in scan.get("skills", []):
    qn = s.get("qualified_name") or s.get("folder")
    scan_index.setdefault(qn, s)
    p = s.get("path")
    if p:
        try:
            scan_by_realpath[os.path.realpath(p)] = s
        except OSError:
            pass

budget = tcost.get("budget", 200000)
cards = []

for s in tcost.get("skills", []):
    name = s["name"]
    rp = s.get("realpath") or ""
    scan_match = (scan_by_realpath.get(os.path.realpath(rp)) if rp else None) \
        or scan_index.get(name, {})

    tokens = s.get("tokens", 0)
    tokens_pct = (tokens / budget * 100) if budget > 0 else 0
    invocations = s.get("usage_count", 0)
    last_used = s.get("last_used", "never")
    scope = scan_match.get("scope", s.get("scope", "user"))
    namespace = scan_match.get("namespace")
    path = scan_match.get("path", "")
    description = scan_match.get("description", "") or ""

    # Days since last use
    days_since = None
    if last_used and last_used != "never":
        try:
            lu = datetime.fromisoformat(last_used.replace("Z", "+00:00")) if "T" in last_used else datetime.strptime(last_used, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_since = (datetime.now(timezone.utc) - lu).days
        except Exception:
            pass

    # Verdict score: most-likely-waste first
    score = tokens_pct * 10
    if invocations == 0:
        score += 50
    if days_since is not None and days_since > 60:
        score += 25
    score -= invocations * 5
    if scope == "project":
        score -= 30  # project skills are usually intentional, downrank

    # Verdict label by bucket. Wording is careful not to claim the body is
    # permanent context cost — ranking still weighs total SKILL.md size
    # (an unused skill with a 22k body is a prime delete candidate), but the
    # "cost" language stays honest about what's always loaded.
    if score >= 70:
        verdict_label = "Unused + heavy on trigger — prime delete candidate"
        verdict_tone = "warn"
    elif score >= 40:
        verdict_label = "Rarely used"
        verdict_tone = "neutral"
    elif score >= 10:
        verdict_label = "Occasional use"
        verdict_tone = "neutral"
    else:
        verdict_label = "Active — probably keep"
        verdict_tone = "good"

    cards.append({
        "id": f"{scope}::{name}",
        "name": name,
        "scope": scope,
        "namespace": namespace,
        "path": path,
        "tokens": tokens,
        "desc_tokens": s.get("desc_tokens", 0),
        "body_tokens": s.get("body_tokens", 0),
        "tokens_pct_budget": round(tokens_pct, 2),
        "invocations": invocations,
        "last_used": last_used,
        "days_since_use": days_since,
        "description": description,
        "verdict": {
            "score": round(score, 1),
            "label": verdict_label,
            "tone": verdict_tone,
        },
    })

# --- MCP server cards (v1.7) ---
# No token guesses (schemas live server-side): the deck shows call counts
# from real transcripts. Unused servers rank high — their schemas are the
# always-loaded cost you can't see.
mcp = {}
if mcp_file:
    try:
        mcp = json.load(open(mcp_file))
    except Exception:
        mcp = {}
for srv in mcp.get("servers", []):
    scope = srv.get("scope", "mcp-user").split(",")[0]
    calls = srv.get("calls", 0)
    lu = srv.get("last_used", "never")
    days_since = None
    if lu and lu != "never":
        try:
            days_since = (datetime.now(timezone.utc) - datetime.strptime(lu, "%Y-%m-%d").replace(tzinfo=timezone.utc)).days
        except Exception:
            pass
    score = 40.0            # connected server = always-loaded tool schemas
    if calls == 0:
        score += 45
    if days_since is not None and days_since > 30:
        score += 15
    score -= calls * 2
    if score >= 70:
        label, tone = "Connected but unused — schemas load for nothing", "warn"
    elif score >= 40:
        label, tone = "Rarely called MCP server", "neutral"
    else:
        label, tone = "Actively used MCP server — keep", "good"
    tools_used = srv.get("distinct_tools_used", 0)
    desc = f"MCP server ({srv.get('transport','stdio')}). {calls} calls, {tools_used} distinct tools used in the lookback window. Configured in: {srv.get('origin','?')}"
    cards.append({
        "id": f"{scope}::{srv['name']}",
        "name": srv["name"],
        "scope": scope,
        "namespace": srv.get("origin") if scope == "mcp-plugin" else None,
        "path": srv.get("origin", ""),
        "tokens": 0,
        "desc_tokens": 0,
        "body_tokens": 0,
        "tokens_pct_budget": 0.0,
        "invocations": calls,
        "last_used": lu,
        "days_since_use": days_since,
        "description": desc,
        "verdict": {"score": round(score, 1), "label": label, "tone": tone},
    })

# Sort by score descending (most waste first)
cards.sort(key=lambda c: -c["verdict"]["score"])

deck = {
    "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "budget": budget,
    "total_cards": len(cards),
    "cards": cards,
}

with open(out_file, "w") as f:
    json.dump(deck, f, indent=2)

# Print summary to stderr so callers can pipe stdout
total_tokens = sum(c["tokens"] for c in cards)
likely_waste = sum(1 for c in cards if c["verdict"]["score"] >= 70)
print(f"Built deck: {len(cards)} cards, {total_tokens:,} total tokens", file=sys.stderr)
print(f"Likely waste: {likely_waste} cards (score >= 70)", file=sys.stderr)
print(f"Output: {out_file}", file=sys.stderr)
PYEOF

echo "$OUTPUT"
