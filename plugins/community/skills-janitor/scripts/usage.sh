#!/bin/bash
# Skills Janitor - Usage Tracking
# Parses conversation history to track skill invocation frequency

set -euo pipefail

command -v python3 &>/dev/null || { echo "ERROR: python3 required" >&2; exit 1; }

# --- Defaults ---
WEEKS=4
JSON_OUTPUT=false
DATA_DIR="$(cd "$(dirname "$0")/.." && pwd)/data"

# --- Parse args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --weeks) WEEKS="$2"; shift 2 ;;
        --json) JSON_OUTPUT=true; shift ;;
        -h|--help) echo "Usage: usage.sh [--weeks N] [--json]"; exit 0 ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# --- Export for Python ---
export WEEKS JSON_OUTPUT DATA_DIR HISTORY_FILE

# --- Load platform paths ---
source "$(dirname "$0")/paths.sh"

# --- Paths ---
USER_SKILLS="$CLAUDE_USER_SKILLS"
PROJECT_SKILLS="$CLAUDE_PROJECT_SKILLS"

# Resolve the conversation-history file. Order: explicit CLAUDE_CONFIG_DIR,
# the standard install location, then multi-account config dirs. The old
# code hardcoded a single non-standard path, so standard installs found no
# history and every skill was reported as "never used".
HISTORY_FILE=""
for _cand in \
    "${CLAUDE_CONFIG_DIR:-/nonexistent}/history.jsonl" \
    "$HOME/.claude/history.jsonl" \
    "$HOME"/.claude-account-*/history.jsonl; do
    if [[ -f "$_cand" ]]; then
        HISTORY_FILE="$_cand"
        break
    fi
done

if [[ -z "$HISTORY_FILE" ]]; then
    echo "WARNING: Claude history file not found (looked in \$CLAUDE_CONFIG_DIR, ~/.claude, ~/.claude-account-*)" >&2
    echo "Usage tracking requires Claude Code conversation history; counts will show as 0." >&2
    # Don't exit - still scan skills for inventory
fi

# --- Ensure data dir exists ---
mkdir -p "$DATA_DIR"

# --- Collect skills and their descriptions ---
export SKILLS_TMPFILE=$(mktemp)
trap "rm -f $SKILLS_TMPFILE" EXIT

collect_skills() {
    local dir="$1"
    local scope="$2"
    local namespace="${3:-}"
    [[ -d "$dir" ]] || return 0

    for skill_dir in "$dir"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local name
        name=$(basename "$skill_dir")

        # Skip self
        [[ "$name" == "skills-janitor" ]] && continue

        local skill_file=""
        [[ -f "$skill_dir/SKILL.md" ]] && skill_file="$skill_dir/SKILL.md"
        [[ -f "$skill_dir/Skill.md" ]] && skill_file="$skill_dir/Skill.md"
        [[ -z "$skill_file" ]] && continue
        [[ ! -e "$skill_file" ]] && continue

        local desc
        desc=$(extract_description "$skill_file" | tr '[:upper:]' '[:lower:]')

        # Qualified name matches Claude's invocation syntax for plugin skills
        # (e.g. "marketing-skills:image"). Slash-command matching below uses
        # this exact form to detect plugin-skill invocations in history.
        local display_name="$name"
        [[ -n "$namespace" ]] && display_name="${namespace}:${name}"

        # Realpath lets python dedupe one physical skill reachable from two
        # roots (e.g. ~/.claude/skills/foo -> ~/.agents/skills/foo symlink),
        # which previously produced duplicate rows in every report.
        local realpath
        realpath=$(cd "$skill_dir" 2>/dev/null && pwd -P || echo "$skill_dir")

        printf '%s\t%s\t%s\t%s\n' "$scope" "$display_name" "$realpath" "$desc" >> "$SKILLS_TMPFILE"
    done
}

# Scan all platforms (Claude Code + Codex + plugins + sources)
_usage_scan() { collect_skills "$1" "$2" "$4"; }
for_each_skill_dir _usage_scan

# --- Transcript-based Skill invocations (v1.7) ---
# Session transcripts record every Skill tool_use — including skills Claude
# auto-triggered, which the slash-command history can't see. Pre-filter with
# grep (transcript trees run to GBs) over files inside the lookback window.
export SKILL_CALLS_TMP=$(mktemp)
trap "rm -f $SKILLS_TMPFILE $SKILL_CALLS_TMP" EXIT
_DAYS=$(( WEEKS * 7 ))
_seen_tr_roots=""
for _proj_root in "${CLAUDE_CONFIG_DIR:-/nonexistent}/projects" "$HOME/.claude/projects" "$HOME"/.claude-account-*/projects; do
    [[ -d "$_proj_root" ]] || continue
    _rr=$(cd "$_proj_root" 2>/dev/null && pwd -P || echo "$_proj_root")
    case "|$_seen_tr_roots|" in *"|$_rr|"*) continue ;; esac
    _seen_tr_roots="$_seen_tr_roots|$_rr"
    find "$_proj_root" -name "*.jsonl" -type f -mtime "-$_DAYS" 2>/dev/null \
        | while IFS= read -r _tf; do
            LC_ALL=C grep -h '"name":"Skill"' "$_tf" 2>/dev/null || true
        done >> "$SKILL_CALLS_TMP"
done

# --- Run analysis ---
python3 << 'PYEOF'
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

WEEKS = int(os.environ.get("WEEKS", "4"))
JSON_OUTPUT = os.environ.get("JSON_OUTPUT", "false") == "true"
SKILLS_FILE = os.environ.get("SKILLS_TMPFILE", "")
HISTORY_FILE = os.environ.get("HISTORY_FILE", "")
DATA_DIR = os.environ.get("DATA_DIR", "")

# System commands to filter out (not skill invocations)
SYSTEM_COMMANDS = {
    "/status", "/resume", "/exit", "/mcp", "/plugin", "/usage", "/clear",
    "/effort", "/rename", "/login", "/skills", "/compact", "/model",
    "/config", "/permissions", "/reload-plugins", "/add-dir", "/ide",
    "/vim", "/output-style", "/rate-limit-options", "/help", "/doctor",
    "/memory", "/init", "/cost", "/review", "/terminal-setup", "/fast",
    "/hooks", "/listen", "/bug", "/diff", "/pr-comments", "/context",
    "/logout", "/approved-tools", "/plan", "/todos"
}

# --- Load skills, deduping by realpath ---
# One physical SKILL.md reachable from two roots (Claude + Codex symlink
# installs) previously produced two identical rows whose counts read from the
# same counter — pure display noise. Keep one record; merge scope labels.
skills = []
_by_realpath = {}
if SKILLS_FILE and os.path.isfile(SKILLS_FILE):
    with open(SKILLS_FILE) as f:
        for line in f:
            # rstrip("\n") ONLY — .strip() ate the trailing tab of rows whose
            # description is empty, collapsing them into the legacy 3-column
            # shape with desc = the filesystem path (and no realpath dedup).
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t", 3)
            if len(parts) == 3:  # tolerate old 3-column rows
                scope, name, desc = parts
                realpath = ""
            elif len(parts) == 4:
                scope, name, realpath, desc = parts
            else:
                continue
            key = realpath or f"{scope}/{name}"
            if key in _by_realpath:
                existing = _by_realpath[key]
                if scope not in existing["scopes"]:
                    existing["scopes"].append(scope)
                continue
            rec = {"scope": scope, "scopes": [scope], "name": name, "desc": desc}
            _by_realpath[key] = rec
            skills.append(rec)
for s in skills:
    s["scope"] = ",".join(sorted(s.pop("scopes")))

# --- Extract keywords (reuse logic from detect_dupes.sh) ---
STOP_WORDS = {
    "use", "when", "the", "user", "wants", "to", "or", "and", "a", "an",
    "this", "skill", "also", "that", "for", "with", "in", "on", "of",
    "is", "are", "it", "be", "as", "at", "by", "from", "their", "they",
    "has", "have", "do", "does", "can", "will", "about", "not", "but",
    "if", "its", "into", "your", "you", "how", "what", "which", "any",
    "all", "each", "every", "both", "more", "most", "other", "some",
    "such", "than", "too", "very", "just", "only", "own", "same",
    "mentions", "says", "asks", "help", "create", "make", "build",
    "improve", "optimize", "review", "write", "generate", "set", "up",
    "see", "page", "content", "product", "want", "like", "need",
    "would", "should", "could", "get", "using", "used", "new", "way"
}

def extract_keywords(desc):
    words = re.findall(r'[a-z]+', desc.lower())
    return set(w for w in words if w not in STOP_WORDS and len(w) > 2)

# Build skill keyword map
skill_keywords = {}
for s in skills:
    skill_keywords[s["name"]] = extract_keywords(s["desc"])

# --- Parse history ---
now = datetime.now(timezone.utc)
cutoff = now - timedelta(weeks=WEEKS)

# Tracking structures
explicit_counts = defaultdict(lambda: defaultdict(int))  # skill -> week -> count
estimated_counts = defaultdict(lambda: defaultdict(int))
last_used = {}  # skill -> timestamp
weekly_totals = defaultdict(int)

# Missing history is a soft condition (warned by the bash wrapper): skills
# are still inventoried, all counts stay 0. The old unguarded open() made
# the whole script die with a traceback on standard installs.
history_lines = []
if HISTORY_FILE and os.path.isfile(HISTORY_FILE):
    with open(HISTORY_FILE) as f:
        history_lines = f.readlines()

for line in history_lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        display = entry.get("display", "").strip()
        ts = entry.get("timestamp", 0)
        if not display or not ts:
            continue

        entry_time = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        if entry_time < cutoff:
            continue

        week_key = entry_time.strftime("%Y-W%W")

        # --- Explicit command detection (Claude / and Codex $.) ---
        is_slash = display.startswith("/")
        is_dollar = display.startswith("$.")
        if is_slash or is_dollar:
            cmd = display.split()[0].rstrip()
            if is_slash and cmd in SYSTEM_COMMANDS:
                continue

            # Match against known skills. Plugin skills are registered under
            # their qualified name (<plugin>:<skill>) but Claude Code accepts
            # the bare form too (`/janitor-audit` for
            # `skills-janitor:janitor-audit`) — match both, exact-name first
            # across all skills so a user-scope skill wins over a bare plugin
            # alias with the same name.
            cmd_name = cmd.lstrip("/").lstrip("$.")
            matched = None
            for s in skills:
                if cmd_name == s["name"]:
                    matched = s
                    break
            if matched is None and ":" not in cmd_name:
                for s in skills:
                    if ":" in s["name"] and cmd_name == s["name"].split(":", 1)[1]:
                        matched = s
                        break
            if matched is not None:
                name = matched["name"]
                explicit_counts[name][week_key] += 1
                last_used[name] = max(
                    last_used.get(name, entry_time), entry_time
                )
                weekly_totals[week_key] += 1
        else:
            # --- Natural language detection ---
            input_words = set(re.findall(r'[a-z]+', display.lower()))
            input_keywords = input_words - STOP_WORDS

            if len(input_keywords) < 3:
                continue

            for s in skills:
                kw = skill_keywords.get(s["name"], set())
                if not kw:
                    continue

                common = input_keywords & kw
                union = input_keywords | kw
                similarity = len(common) / len(union) if union else 0

                # Higher threshold (50%) to avoid false positives
                if similarity > 0.5 and len(common) >= 3:
                    estimated_counts[s["name"]][week_key] += 1
                    if s["name"] not in last_used or entry_time > last_used[s["name"]]:
                        last_used[s["name"]] = entry_time
                    weekly_totals[week_key] += 1

# --- Transcript Skill invocations (real tool_use records) ---
# Highest-fidelity source: includes auto-triggered skills. Counted into
# explicit_counts under the matching registry name (qualified or bare).
SKILL_CALLS = os.environ.get("SKILL_CALLS_TMP", "")
_sk_rx = re.compile(r'"name":"Skill".{0,400}?"skill":"([^"]+)"', re.S)
_ts_rx = re.compile(r'"timestamp":"([0-9T:.\-]+)')
if SKILL_CALLS and os.path.isfile(SKILL_CALLS):
    with open(SKILL_CALLS, errors="replace") as f:
        for line in f:
            for m in _sk_rx.finditer(line):
                inv = m.group(1)
                ts_m = _ts_rx.search(line)
                try:
                    t = datetime.fromisoformat(ts_m.group(1)[:19]).replace(tzinfo=timezone.utc) if ts_m else None
                except Exception:
                    t = None
                if t is None or t < cutoff:
                    continue
                wk = t.strftime("%Y-W%W")
                matched = None
                for s in skills:
                    if inv == s["name"]:
                        matched = s
                        break
                if matched is None and ":" not in inv:
                    for s in skills:
                        if ":" in s["name"] and inv == s["name"].split(":", 1)[1]:
                            matched = s
                            break
                if matched is not None:
                    name = matched["name"]
                    explicit_counts[name][wk] += 1
                    if name not in last_used or t > last_used[name]:
                        last_used[name] = t
                    weekly_totals[wk] += 1

# --- Build results ---
all_skill_names = [s["name"] for s in skills]
results = []
for s in skills:
    name = s["name"]
    exp_total = sum(explicit_counts[name].values())
    est_total = sum(estimated_counts[name].values())
    total = exp_total + est_total
    lu = last_used.get(name)
    lu_str = lu.strftime("%Y-%m-%d") if lu else "never"
    weeks_since = int((now - lu).days / 7) if lu else -1

    results.append({
        "name": name,
        "scope": s["scope"],
        "explicit": exp_total,
        "estimated": est_total,
        "total": total,
        "last_used": lu_str,
        "weeks_since_use": weeks_since,
        "explicit_weekly": dict(explicit_counts[name]),
        "estimated_weekly": dict(estimated_counts[name]),
    })

# Sort: most used first, then alphabetical
results.sort(key=lambda x: (-x["total"], x["name"]))

active_skills = [r for r in results if r["total"] > 0]
unused_skills = [r for r in results if r["total"] == 0]

# --- Save persistent data ---
if DATA_DIR:
    usage_file = os.path.join(DATA_DIR, "usage-history.json")
    existing = {}
    if os.path.isfile(usage_file):
        try:
            with open(usage_file) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = {}

    # Merge: keep last 12 weeks
    all_weeks = set(existing.get("weekly_totals", {}).keys())
    all_weeks.update(weekly_totals.keys())
    sorted_weeks = sorted(all_weeks)[-12:]

    merged_weekly = {}
    for w in sorted_weeks:
        merged_weekly[w] = weekly_totals.get(w, existing.get("weekly_totals", {}).get(w, 0))

    save_data = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period_weeks": WEEKS,
        "total_skills": len(results),
        "active_skills": len(active_skills),
        "unused_skills": len(unused_skills),
        "weekly_totals": merged_weekly,
        "skills": {r["name"]: {
            "explicit": r["explicit"],
            "estimated": r["estimated"],
            "total": r["total"],
            "last_used": r["last_used"],
        } for r in results}
    }

    with open(usage_file, "w") as f:
        json.dump(save_data, f, indent=2)

# --- Output ---
if JSON_OUTPUT:
    output = {
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "period_weeks": WEEKS,
        "cutoff_date": cutoff.strftime("%Y-%m-%d"),
        "total_skills": len(results),
        "active_count": len(active_skills),
        "unused_count": len(unused_skills),
        "skills": results,
        "weekly_totals": dict(sorted(weekly_totals.items())),
    }
    print(json.dumps(output, indent=2, default=str))
else:
    period_start = cutoff.strftime("%Y-%m-%d")
    period_end = now.strftime("%Y-%m-%d")

    print(f"=== Skills Janitor - Usage Report ===")
    print(f"Period: {period_start} to {period_end} ({WEEKS} weeks)")
    print(f"Total skills tracked: {len(results)}")
    print()

    if active_skills:
        print("--- Most Used ---")
        print(f"  {'Skill':<35} {'Explicit':>8} {'Estimated':>9} {'Total':>5}  {'Last Used':<10}")
        for r in active_skills:
            print(f"  {r['name']:<35} {r['explicit']:>8} {r['estimated']:>9} {r['total']:>5}  {r['last_used']:<10}")
        print()

    if unused_skills:
        print(f"--- Never Used ({len(unused_skills)} skills) ---")
        for r in unused_skills[:15]:
            print(f"  {r['name']:<35} ({r['scope']})")
        if len(unused_skills) > 15:
            print(f"  ... and {len(unused_skills) - 15} more")
        print()

    if weekly_totals:
        print("--- Weekly Trend ---")
        print(f"  {'Week':<12} {'Invocations':>12}")
        for week in sorted(weekly_totals.keys()):
            print(f"  {week:<12} {weekly_totals[week]:>12}")
        print()

    pct_active = (len(active_skills) / len(results) * 100) if results else 0
    pct_unused = (len(unused_skills) / len(results) * 100) if results else 0
    print("=== Summary ===")
    print(f"  Active skills: {len(active_skills)} / {len(results)} ({pct_active:.0f}%)")
    print(f"  Unused skills: {len(unused_skills)} ({pct_unused:.0f}%)")
    if active_skills:
        top = active_skills[0]
        print(f"  Most used: {top['name']} ({top['total']} total)")
    if pct_unused > 50:
        print(f"  Recommendation: Consider removing {len(unused_skills)} unused skills to reduce context overhead")

PYEOF
