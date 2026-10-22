#!/bin/bash
# Skills Janitor - Lint Check
# Validates skills against best practices

set -euo pipefail

# --- Load platform paths ---
source "$(dirname "$0")/paths.sh"

USER_SKILLS="$CLAUDE_USER_SKILLS"
PROJECT_SKILLS="$CLAUDE_PROJECT_SKILLS"

ISSUES=0
WARNINGS=0
INFO=0

print_issue() {
    local severity="$1"
    local skill="$2"
    local message="$3"

    case "$severity" in
        critical) echo "  [CRITICAL] $skill: $message"; ((ISSUES++)) || true ;;
        warning)  echo "  [WARNING]  $skill: $message"; ((WARNINGS++)) || true ;;
        info)     echo "  [INFO]     $skill: $message"; ((INFO++)) || true ;;
    esac
}

lint_skill() {
    local path="$1"
    local scope="$2"
    local name
    name=$(basename "$path")

    # Skip self
    [[ "$name" == "skills-janitor" ]] && return

    # Check if symlink is broken
    if [[ -L "$path" && ! -e "$path" ]]; then
        print_issue "critical" "$name" "Broken symlink -> $(readlink "$path" 2>/dev/null || echo 'unknown')"
        return
    fi

    # Find skill file
    local skill_file=""
    [[ -f "$path/SKILL.md" ]] && skill_file="$path/SKILL.md"
    [[ -f "$path/Skill.md" ]] && skill_file="$path/Skill.md"

    if [[ -z "$skill_file" ]]; then
        # No SKILL.md = support folder (_shared, _docs, _temp, plugin dirs, etc.) — skip silently
        return
    fi

    # Check frontmatter exists
    if ! head -1 "$skill_file" | grep -q '^---'; then
        print_issue "critical" "$name" "Missing frontmatter (no opening ---)"
        return
    fi

    # Check closing frontmatter
    local fm_close
    # \r? so a CRLF file is not misreported as "missing closing ---"
    fm_close=$(awk 'NR>1 && /^---\r?$/{print NR; exit}' "$skill_file")
    if [[ -z "$fm_close" ]]; then
        print_issue "critical" "$name" "Missing closing --- in frontmatter"
        return
    fi

    # Extract frontmatter
    local frontmatter
    frontmatter=$(sed -n "2,$((fm_close - 1))p" "$skill_file")

    # Check name field
    local name_field
    # NB: trim with sed, never xargs — xargs parses shell quoting and aborts with
    # "unterminated quote" on any apostrophe (user's, Don't), and the old
    # `|| echo ""` swallowed that into a bogus "missing field" finding.
    # The `|| true` is still required: grep exits 1 when the field is absent,
    # and a bare assignment propagates that under `set -e`.
    name_field=$(echo "$frontmatter" | grep -E '^name:' | sed 's/^name:[[:space:]]*//' | tr -d '"' | tr -d "'" | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' || true)
    if [[ -z "$name_field" ]]; then
        print_issue "warning" "$name" "Missing 'name' field in frontmatter"
    elif [[ "$(echo "$name_field" | tr '[:upper:]' '[:lower:]')" != "$(echo "$name" | tr '[:upper:]' '[:lower:]')" && "$(echo "$name_field" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')" != "$(echo "$name" | tr '[:upper:]' '[:lower:]')" ]]; then
        print_issue "info" "$name" "Folder name '$name' doesn't match skill name '$name_field'"
    fi

    # Check description field — supports inline and every YAML block-scalar header
    local desc_raw
    desc_raw=$(echo "$frontmatter" | grep -E '^description:' | sed 's/^description:[[:space:]]*//' | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' || true)

    # A block-scalar header is [|>] plus an optional chomp indicator (- or +) and
    # an optional explicit indent digit: | |- |+ |2 > >- >+ >2 >-2 … Matching only
    # bare "|" and ">" left "description: >-" parsed as the two-character string
    # ">-", which then tripped both the "too short" and "no trigger word" checks.
    local desc
    if [[ -z "$desc_raw" || "$desc_raw" =~ ^[|\>][-+]?[0-9]*$ || "$desc_raw" =~ ^[|\>][0-9]*[-+]?$ ]]; then
        # Block scalar: collect indented lines following 'description:'
        desc=$(echo "$frontmatter" | awk '
            /^description:/ { capture=1; next }
            capture && /^[[:space:]]+/ { line=$0; sub(/^[[:space:]]+/, "", line); printf "%s ", line }
            capture && /^[^[:space:]]/ { exit }
        ' | sed 's/[[:space:]]*$//')
    else
        desc="$desc_raw"
    fi

    if [[ -z "$desc" ]]; then
        print_issue "critical" "$name" "Missing 'description' field - Claude can't trigger this skill"
    else
        local desc_len=${#desc}

        # Length check
        if [[ $desc_len -lt 30 ]]; then
            print_issue "warning" "$name" "Description too short ($desc_len chars) - should be 50-200 for good triggering"
        elif [[ $desc_len -gt 500 ]]; then
            print_issue "info" "$name" "Description is long ($desc_len chars) - consider trimming to < 300"
        fi

        # Trigger word check
        if ! echo "$desc" | grep -qi -E '(when|trigger|use for|invoke|mention|says|asks|also use|use this|relevant|appropriate|helps with|designed for)'; then
            print_issue "warning" "$name" "Description doesn't explain when to trigger - add 'Use when...' or 'Also use when...'"
        fi

        # Check disable-model-invocation: auto-loaded skills need a meaningful description
        local dmi
        dmi=$(echo "$frontmatter" | grep -E '^disable-model-invocation:' | sed 's/^disable-model-invocation:[[:space:]]*//' | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' || true)
        if [[ "$dmi" == "true" && $desc_len -lt 50 ]]; then
            print_issue "warning" "$name" "Skill uses disable-model-invocation but description is very short — Claude may not trigger it correctly"
        fi
    fi

    # Check body content
    local body_lines
    # `|| true`, not `|| echo 0` — grep -c already prints "0" on no matches
    body_lines=$(tail -n +"$((fm_close + 1))" "$skill_file" | grep -c '[^ ]' 2>/dev/null || true)
    body_lines=${body_lines:-0}
    if [[ "$body_lines" -lt 3 ]]; then
        print_issue "warning" "$name" "Very little body content ($body_lines non-empty lines)"
    fi

    # Check for gotchas section
    if ! grep -qi 'gotcha' "$skill_file" 2>/dev/null; then
        print_issue "info" "$name" "No Gotchas section - consider adding common pitfalls"
    fi

    # Check total size
    local total_lines
    total_lines=$(wc -l < "$skill_file" | tr -d ' ')
    if [[ "$total_lines" -gt 500 ]]; then
        print_issue "info" "$name" "Skill file is large ($total_lines lines) - consider using progressive disclosure with reference files"
    fi
}

echo "=== Skills Janitor - Lint Report ==="
echo ""

echo "--- User Skills ($USER_SKILLS) ---"
if [[ -d "$USER_SKILLS" ]]; then
    for skill_dir in "$USER_SKILLS"/*; do
        [[ -d "$skill_dir" || -L "$skill_dir" ]] || continue
        lint_skill "${skill_dir%/}" "user"
    done
fi

# Only scan project skills if they're different from user skills
USER_REAL=$(cd "$USER_SKILLS" 2>/dev/null && pwd -P || echo "")
PROJECT_REAL=$(cd "$PROJECT_SKILLS" 2>/dev/null && pwd -P || echo "")
if [[ -d "$PROJECT_SKILLS" && "$USER_REAL" != "$PROJECT_REAL" ]]; then
    echo ""
    echo "--- Project Skills ($PROJECT_SKILLS) ---"
    for skill_dir in "$PROJECT_SKILLS"/*; do
        [[ -d "$skill_dir" || -L "$skill_dir" ]] || continue
        lint_skill "${skill_dir%/}" "project"
    done
fi

# Scan Codex skills
if [[ -d "$CODEX_USER_SKILLS" ]]; then
    echo ""
    echo "--- Codex User Skills ($CODEX_USER_SKILLS) ---"
    for skill_dir in "$CODEX_USER_SKILLS"/*; do
        [[ -d "$skill_dir" || -L "$skill_dir" ]] || continue
        lint_skill "${skill_dir%/}" "codex-user"
    done
fi
if [[ -d "$CODEX_PROJECT_SKILLS" ]]; then
    CODEX_P_REAL=$(cd "$CODEX_PROJECT_SKILLS" 2>/dev/null && pwd -P || echo "")
    CODEX_U_REAL=$(cd "$CODEX_USER_SKILLS" 2>/dev/null && pwd -P || echo "")
    if [[ "$CODEX_P_REAL" != "$CODEX_U_REAL" ]]; then
        echo ""
        echo "--- Codex Project Skills ($CODEX_PROJECT_SKILLS) ---"
        for skill_dir in "$CODEX_PROJECT_SKILLS"/*; do
            [[ -d "$skill_dir" || -L "$skill_dir" ]] || continue
            lint_skill "${skill_dir%/}" "codex-project"
        done
    fi
fi

echo ""
echo "=== Summary ==="
echo "  Critical: $ISSUES"
echo "  Warnings: $WARNINGS"
echo "  Info:     $INFO"
echo "  Total:    $((ISSUES + WARNINGS + INFO))"
