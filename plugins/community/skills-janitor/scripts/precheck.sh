#!/bin/bash
# Skills Janitor - Pre-Install Overlap Check
# Checks if a new skill would duplicate existing ones before installing

set -euo pipefail

command -v python3 &>/dev/null || { echo "ERROR: python3 required" >&2; exit 1; }
command -v curl &>/dev/null || { echo "ERROR: curl required" >&2; exit 1; }

# --- Load platform paths ---
source "$(dirname "$0")/paths.sh"

# --- Defaults ---
SOURCE=""
JSON_OUTPUT=false

# --- Parse args ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) JSON_OUTPUT=true; shift ;;
        -h|--help)
            echo "Usage: precheck.sh <github-url-or-path> [--json]"
            echo ""
            echo "Check if a skill overlaps with anything already installed."
            echo ""
            echo "Examples:"
            echo "  precheck.sh https://github.com/user/my-skill"
            echo "  precheck.sh https://github.com/user/repo/tree/main/skills/my-skill"
            echo "  precheck.sh ~/path/to/skill-folder"
            exit 0
            ;;
        -*) echo "Unknown option: $1" >&2; exit 1 ;;
        *)
            if [[ -z "$SOURCE" ]]; then
                SOURCE="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$SOURCE" ]]; then
    echo "ERROR: Source required. Usage: precheck.sh <github-url-or-path> [--json]" >&2
    exit 1
fi

# --- Collect installed skill descriptions ---
export TMPFILE=$(mktemp)
trap "rm -f $TMPFILE $TMPFILE.new" EXIT

extract_skills() {
    local dir="$1"
    local scope="$2"
    [[ -d "$dir" ]] || return 0

    for skill_dir in "$dir"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local name
        name=$(basename "$skill_dir")
        [[ "$name" == "skills-janitor" ]] && continue

        local skill_file=""
        [[ -f "$skill_dir/SKILL.md" ]] && skill_file="$skill_dir/SKILL.md"
        [[ -f "$skill_dir/Skill.md" ]] && skill_file="$skill_dir/Skill.md"
        [[ -z "$skill_file" ]] && continue
        [[ ! -e "$skill_file" ]] && continue

        local desc
        desc=$(extract_description "$skill_file" | tr '[:upper:]' '[:lower:]')

        printf '%s\t%s\t%s\n' "$scope" "$name" "$desc" >> "$TMPFILE"
    done
}

# Scan all platforms (Claude Code + Codex)
_precheck_scan() { extract_skills "$1" "$2"; }
for_each_skill_dir _precheck_scan

# --- Fetch or read the new skill ---
NEW_SKILL_CONTENT=""

if [[ "$SOURCE" == http* ]]; then
    # GitHub URL - try to fetch SKILL.md
    RAW_URL=""

    # Convert various GitHub URL formats to raw content URL
    # https://github.com/user/repo -> try main branch SKILL.md
    # https://github.com/user/repo/tree/main/skills/name -> specific path
    if echo "$SOURCE" | grep -qE 'github\.com/[^/]+/[^/]+/tree/[^/]+/'; then
        # Has a path: extract owner/repo/branch/path. The branch is in the
        # URL, so no main/master guessing — but DO fetch it (this branch
        # historically computed RAW_URL and never downloaded it).
        RAW_URL=$(echo "$SOURCE" | sed -E 's|github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)|raw.githubusercontent.com/\1/\2/\3/\4/SKILL.md|; s|/+SKILL\.md$|/SKILL.md|')
        NEW_SKILL_CONTENT=$(curl -sL -f "$RAW_URL" 2>/dev/null || true)
        if [[ -z "$NEW_SKILL_CONTENT" ]]; then
            NEW_SKILL_CONTENT=$(curl -sL -f "${RAW_URL%SKILL.md}Skill.md" 2>/dev/null || true)
        fi
    elif echo "$SOURCE" | grep -qE 'github\.com/[^/]+/[^/]+/?$'; then
        # Just repo root - try common locations
        REPO_PATH=$(echo "$SOURCE" | sed -E 's|https?://github\.com/||; s|/$||')
        # Try: SKILL.md, skills/*/SKILL.md
        for try_path in "SKILL.md" "Skill.md"; do
            RAW_URL="https://raw.githubusercontent.com/$REPO_PATH/main/$try_path"
            NEW_SKILL_CONTENT=$(curl -sL -f "$RAW_URL" 2>/dev/null || true)
            if [[ -n "$NEW_SKILL_CONTENT" ]]; then
                break
            fi
            RAW_URL="https://raw.githubusercontent.com/$REPO_PATH/master/$try_path"
            NEW_SKILL_CONTENT=$(curl -sL -f "$RAW_URL" 2>/dev/null || true)
            if [[ -n "$NEW_SKILL_CONTENT" ]]; then
                break
            fi
        done

        # If not found at root, try to find via GitHub API
        if [[ -z "$NEW_SKILL_CONTENT" ]]; then
            GITHUB_TOKEN="${GITHUB_TOKEN:-}"
            # Array, not a quoted string: the old form passed `-H "Authorization: ..."`
            # as ONE argument with literal quotes, sending a garbage header.
            AUTH_ARGS=()
            [[ -n "$GITHUB_TOKEN" ]] && AUTH_ARGS=(-H "Authorization: token $GITHUB_TOKEN")

            # Search for SKILL.md in the repo
            API_URL="https://api.github.com/search/code?q=filename:SKILL.md+repo:$REPO_PATH"
            SEARCH_RESULT=$(curl -sL -f -H "Accept: application/vnd.github.v3+json" -H "User-Agent: skills-janitor/1.5.0" ${AUTH_ARGS[@]+"${AUTH_ARGS[@]}"} "$API_URL" 2>/dev/null || true)

            if [[ -n "$SEARCH_RESULT" ]]; then
                FIRST_PATH=$(echo "$SEARCH_RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['items'][0]['path'] if d.get('items') else '')" 2>/dev/null || true)
                if [[ -n "$FIRST_PATH" ]]; then
                    RAW_URL="https://raw.githubusercontent.com/$REPO_PATH/main/$FIRST_PATH"
                    NEW_SKILL_CONTENT=$(curl -sL -f "$RAW_URL" 2>/dev/null || true)
                    if [[ -z "$NEW_SKILL_CONTENT" ]]; then
                        RAW_URL="https://raw.githubusercontent.com/$REPO_PATH/master/$FIRST_PATH"
                        NEW_SKILL_CONTENT=$(curl -sL -f "$RAW_URL" 2>/dev/null || true)
                    fi
                fi
            fi
        fi
    else
        RAW_URL="$SOURCE"
        NEW_SKILL_CONTENT=$(curl -sL -f "$RAW_URL" 2>/dev/null || true)
    fi

    if [[ -z "$NEW_SKILL_CONTENT" ]]; then
        echo "ERROR: Could not fetch SKILL.md from $SOURCE" >&2
        echo "Try providing a direct URL to the SKILL.md file or a local path." >&2
        exit 1
    fi
else
    # Local path
    LOCAL_PATH="$SOURCE"
    if [[ -d "$LOCAL_PATH" ]]; then
        if [[ -f "$LOCAL_PATH/SKILL.md" ]]; then
            LOCAL_PATH="$LOCAL_PATH/SKILL.md"
        elif [[ -f "$LOCAL_PATH/Skill.md" ]]; then
            LOCAL_PATH="$LOCAL_PATH/Skill.md"
        else
            echo "ERROR: No SKILL.md found in $LOCAL_PATH" >&2
            exit 1
        fi
    fi

    if [[ ! -f "$LOCAL_PATH" ]]; then
        echo "ERROR: File not found: $LOCAL_PATH" >&2
        exit 1
    fi

    NEW_SKILL_CONTENT=$(cat "$LOCAL_PATH")
fi

# Save new skill content for Python
echo "$NEW_SKILL_CONTENT" > "$TMPFILE.new"

# --- Security scan of the candidate (v1.6) ---
# Local path: scan the real directory (includes bundled scripts).
# Remote URL: scan the fetched SKILL.md (injection phrases, hidden unicode,
# smuggled payloads — scripts aren't fetched, note that in the output).
SEC_JSON=""
SEC_SCOPE_NOTE=""
SCRIPT_DIR_PC="$(cd "$(dirname "$0")" && pwd)"
if [[ "$SOURCE" != http* && -d "$SOURCE" ]]; then
    SEC_JSON=$(bash "$SCRIPT_DIR_PC/security.sh" --path "$SOURCE" --json 2>/dev/null || echo "")
    SEC_SCOPE_NOTE="full directory (SKILL.md + bundled files)"
else
    SEC_TMPDIR=$(mktemp -d -t janitor-precheck.XXXXXX)
    printf '%s\n' "$NEW_SKILL_CONTENT" > "$SEC_TMPDIR/SKILL.md"
    SEC_JSON=$(bash "$SCRIPT_DIR_PC/security.sh" --path "$SEC_TMPDIR" --json 2>/dev/null || echo "")
    rm -rf "$SEC_TMPDIR"
    SEC_SCOPE_NOTE="fetched SKILL.md only — bundled scripts are NOT fetched; re-check after cloning"
fi
export SEC_JSON SEC_SCOPE_NOTE

# --- Export for Python ---
export JSON_OUTPUT SOURCE

python3 << 'PYEOF'
import os
import re
import json
import sys

SOURCE = os.environ.get("SOURCE", "")
JSON_OUTPUT = os.environ.get("JSON_OUTPUT", "false") == "true"
TMPFILE = os.environ.get("TMPFILE", "")

# Security scan results (from security.sh, run by the bash wrapper)
SEC_SCOPE_NOTE = os.environ.get("SEC_SCOPE_NOTE", "")
try:
    _sec = json.loads(os.environ.get("SEC_JSON", "") or "{}")
    _sec_skill = (_sec.get("skills") or [{}])[0]
    SEC_VERDICT = _sec_skill.get("verdict", "UNKNOWN")
    SEC_FINDINGS = _sec_skill.get("findings", [])
except Exception:
    SEC_VERDICT, SEC_FINDINGS = "UNKNOWN", []

# --- Stop words (same as detect_dupes.sh) ---
STOP_WORDS = {
    "use", "when", "the", "user", "wants", "to", "or", "and", "a", "an",
    "this", "skill", "also", "that", "for", "with", "in", "on", "of",
    "is", "are", "it", "be", "as", "at", "by", "from", "their", "they",
    "has", "have", "do", "does", "can", "will", "about", "not", "but",
    "if", "its", "into", "your", "you", "how", "what", "which", "any",
    "all", "each", "every", "both", "more", "most", "other", "some",
    "such", "than", "too", "very", "just", "only", "own", "same",
    "mentions", "says", "asks", "help", "create", "make", "build",
    "improve", "optimize", "review", "write", "generate", "set", "up"
}

def extract_keywords(text):
    words = re.findall(r'[a-z]+', text.lower())
    return set(w for w in words if w not in STOP_WORDS and len(w) > 2)

def parse_frontmatter(content):
    """Extract name and description from SKILL.md frontmatter."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return "", ""
    name = ""
    desc = ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            name = re.sub(r'^name:\s*', '', line).strip().strip('"')
        if line.startswith("description:"):
            desc = re.sub(r'^description:\s*', '', line).strip().strip('"')
    return name, desc

# --- Load new skill ---
with open(TMPFILE + ".new") as f:
    new_content = f.read()

new_name, new_desc = parse_frontmatter(new_content)
if not new_name:
    # Try to extract from source URL
    new_name = SOURCE.rstrip("/").split("/")[-1]

new_keywords = extract_keywords(new_desc)
# Also add name words
name_words = set(new_name.replace("-", " ").split())
new_keywords.update(w.lower() for w in name_words if len(w) > 2)

# --- Load installed skills ---
installed = []
if TMPFILE and os.path.isfile(TMPFILE):
    with open(TMPFILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 2)
            if len(parts) < 3:
                continue
            scope, name, desc = parts
            installed.append({"scope": scope, "name": name, "desc": desc})

# --- Compare ---
overlaps = []
for skill in installed:
    skill_keywords = extract_keywords(skill["desc"])
    # Also add skill name words
    sname_words = set(skill["name"].replace("-", " ").split())
    skill_keywords.update(w.lower() for w in sname_words if len(w) > 2)

    common = new_keywords & skill_keywords
    union = new_keywords | skill_keywords
    similarity = len(common) / len(union) if union else 0

    if similarity > 0.15:  # Lower threshold to catch partial overlaps
        overlaps.append({
            "name": skill["name"],
            "scope": skill["scope"],
            "similarity": round(similarity * 100),
            "common_keywords": sorted(common)[:10],
            "description": skill["desc"],
        })

overlaps.sort(key=lambda x: -x["similarity"])

# --- Determine verdict ---
if overlaps and overlaps[0]["similarity"] >= 60:
    verdict = "HIGH_OVERLAP"
    verdict_msg = "High overlap detected - likely duplicate"
elif overlaps and overlaps[0]["similarity"] >= 30:
    verdict = "MODERATE_OVERLAP"
    verdict_msg = "Moderate overlap - review before installing"
else:
    verdict = "SAFE"
    verdict_msg = "No significant overlap - safe to install"

# --- Output ---
if JSON_OUTPUT:
    output = {
        "source": SOURCE,
        "new_skill": {
            "name": new_name,
            "description": new_desc,
            "keywords": sorted(new_keywords),
        },
        "verdict": verdict,
        "security": {
            "verdict": SEC_VERDICT,
            "scope": SEC_SCOPE_NOTE,
            "findings": SEC_FINDINGS,
        },
        "overlaps": overlaps[:10],
        "installed_count": len(installed),
    }
    print(json.dumps(output, indent=2))
else:
    print("=== Skills Janitor - Pre-Install Check ===")
    print()
    print(f"  Checking: {new_name}")
    print(f"  Source: {SOURCE}")
    print(f"  Description: {new_desc[:120]}")
    print(f"  Keywords: {', '.join(sorted(new_keywords)[:10])}")
    print()
    print(f"  Scanned {len(installed)} installed skills")
    print()

    if overlaps:
        high = [o for o in overlaps if o["similarity"] >= 60]
        moderate = [o for o in overlaps if 30 <= o["similarity"] < 60]
        low = [o for o in overlaps if o["similarity"] < 30]

        if high:
            print("  --- HIGH OVERLAP (likely duplicates) ---")
            for o in high:
                print(f"    [{o['similarity']}%] {o['name']} ({o['scope']})")
                print(f"         Shared: {', '.join(o['common_keywords'][:6])}")
                print(f"         Existing desc: {o['description'][:80]}")
                print()

        if moderate:
            print("  --- MODERATE OVERLAP (review before installing) ---")
            for o in moderate:
                print(f"    [{o['similarity']}%] {o['name']} ({o['scope']})")
                print(f"         Shared: {', '.join(o['common_keywords'][:6])}")
                print()

        if low:
            print(f"  --- LOW OVERLAP ({len(low)} skills with minor keyword matches) ---")
            for o in low[:3]:
                print(f"    [{o['similarity']}%] {o['name']}")
            if len(low) > 3:
                print(f"    ... and {len(low) - 3} more")
            print()
    else:
        print("  No overlaps found with installed skills.")
        print()

    # Security section
    print()
    print(f"  --- Security ({SEC_SCOPE_NOTE}) ---")
    if SEC_VERDICT == "PASS":
        print("  No suspicious patterns found.")
    elif SEC_VERDICT == "UNKNOWN":
        print("  Security scan unavailable.")
    else:
        print(f"  VERDICT: {SEC_VERDICT}")
        for fnd in SEC_FINDINGS:
            print(f"    {fnd.get('severity','?'):<6} {fnd.get('title','')}")
            print(f"           {fnd.get('evidence','')[:110]}")
    print()

    # Verdict
    if verdict == "HIGH_OVERLAP":
        print(f"  VERDICT: {verdict_msg}")
        print(f"  Consider using the existing skill instead, or remove it first.")
    elif verdict == "MODERATE_OVERLAP":
        print(f"  VERDICT: {verdict_msg}")
        print(f"  The new skill may partially overlap with existing ones.")
    else:
        print(f"  VERDICT: {verdict_msg}")

PYEOF
