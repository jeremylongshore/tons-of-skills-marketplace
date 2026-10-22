#!/bin/bash
# Skills Janitor - Platform Path Detection
# Detects Claude Code and OpenAI Codex skill directories
# Source this file: source "$(dirname "$0")/paths.sh"

# --- Claude Code paths ---
CLAUDE_USER_SKILLS="$HOME/.claude/skills"
CLAUDE_PROJECT_SKILLS="./.claude/skills"

# --- Claude Code plugin paths ---
# Active marketplace: ~/.claude/plugins/marketplaces/<plugin>/skills/<skill>/SKILL.md
#   (some plugins use ~/.claude/plugins/marketplaces/<plugin>/.claude/skills/ instead)
# Versioned cache:    ~/.claude/plugins/cache/<owner>/<plugin>/<version>/skills/<skill>/SKILL.md
# Sources:            ~/.claude/sources/<source>/skills/<skill>/SKILL.md
PLUGIN_MARKETPLACES="$HOME/.claude/plugins/marketplaces"
PLUGIN_CACHE="$HOME/.claude/plugins/cache"
PLUGIN_SOURCES="$HOME/.claude/sources"
INSTALLED_PLUGINS_FILE="$HOME/.claude/plugins/installed_plugins.json"

# --- OpenAI Codex paths ---
CODEX_USER_SKILLS="$HOME/.agents/skills"
CODEX_PROJECT_SKILLS="./.agents/skills"

# --- Aggregate all valid skill directories ---
# Each entry uses `|` as a separator (filesystem paths cannot contain `|`):
#   scope|platform|namespace|path
# namespace is empty for user/project/codex; set to the plugin or source name
# for plugin/source skills.
ALL_SKILL_DIRS=()

add_dir() {
    local path="$1" scope="$2" platform="$3" namespace="${4:-}"
    # An explicit `if` (not `[[ ]] &&`) so a missing directory doesn't make
    # the function return 1 — every caller sources this under `set -e`, and
    # the bare && form silently killed all scripts on machines without e.g.
    # ~/.agents/skills (any Claude-only install).
    if [[ -d "$path" ]]; then
        ALL_SKILL_DIRS+=("$scope|$platform|$namespace|$path")
    fi
}

add_dir "$CLAUDE_USER_SKILLS" "user" "claude"
add_dir "$CODEX_USER_SKILLS" "user" "codex"

# Deduplicate project dirs (avoid scanning same real path twice when running
# from $HOME, where ./.claude/skills resolves to the same place as
# ~/.claude/skills)
_add_project_dir() {
    local path="$1" platform="$2"
    if [[ ! -d "$path" ]]; then
        return 0
    fi
    local real_path
    real_path=$(cd "$path" 2>/dev/null && pwd -P || echo "")
    local dominated=false
    # ${arr[@]+...} guard: bash 3.2 treats "${arr[@]}" on an EMPTY array as an
    # unbound variable under `set -u`. Same idiom used on every expansion below.
    for existing in ${ALL_SKILL_DIRS[@]+"${ALL_SKILL_DIRS[@]}"}; do
        local existing_path="${existing##*|}"
        local existing_real
        existing_real=$(cd "$existing_path" 2>/dev/null && pwd -P || echo "")
        if [[ "$real_path" == "$existing_real" ]]; then
            dominated=true
            break
        fi
    done
    if [[ "$dominated" == "false" ]]; then
        ALL_SKILL_DIRS+=("project|$platform||$path")
    fi
}

_add_project_dir "$CLAUDE_PROJECT_SKILLS" "claude"
_add_project_dir "$CODEX_PROJECT_SKILLS" "codex"

# --- Add plugin skill dirs ---
# Source of truth is installed_plugins.json. Each plugin's installPath points
# at the active version's directory; skills live at <installPath>/skills/ or
# <installPath>/.claude/skills/. Dedup by realpath so a plugin installed at
# both user and project scope (same installPath) is added once.
if [[ -f "$INSTALLED_PLUGINS_FILE" ]] && command -v python3 &>/dev/null; then
    while IFS='|' read -r _plugin_name _plugin_dir; do
        [[ -n "$_plugin_dir" ]] || continue
        [[ -d "$_plugin_dir" ]] || continue
        ALL_SKILL_DIRS+=("plugin|claude|$_plugin_name|$_plugin_dir")
    done < <(python3 - "$INSTALLED_PLUGINS_FILE" <<'PYEOF'
import json, os, sys
try:
    data = json.load(open(sys.argv[1]))
except Exception:
    sys.exit(0)
plugins = data.get("plugins")
if not isinstance(plugins, dict):
    sys.exit(0)
seen = set()
for key, instances in plugins.items():
    plugin_name = key.split("@", 1)[0]
    if not isinstance(instances, list):
        continue
    for inst in instances:
        if not isinstance(inst, dict):
            continue
        install_path = inst.get("installPath", "")
        if not install_path:
            continue
        for sub in ("skills", os.path.join(".claude", "skills")):
            candidate = os.path.join(install_path, sub)
            if os.path.isdir(candidate):
                rp = os.path.realpath(candidate)
                if rp in seen:
                    break
                seen.add(rp)
                print(f"{plugin_name}|{candidate}")
                break
PYEOF
)
fi

# --- Add source skill dirs ---
# ~/.claude/sources/<source>/skills/<skill>/SKILL.md
if [[ -d "$PLUGIN_SOURCES" ]]; then
    for _source_dir in "$PLUGIN_SOURCES"/*/; do
        [[ -d "$_source_dir" ]] || continue
        _source_name=$(basename "$_source_dir")
        _source_skills="${_source_dir%/}/skills"
        [[ -d "$_source_skills" ]] || continue
        ALL_SKILL_DIRS+=("plugin-source|claude|$_source_name|$_source_skills")
    done
fi

# --- Detect which platforms are present ---
HAS_CLAUDE=false
HAS_CODEX=false
for entry in ${ALL_SKILL_DIRS[@]+"${ALL_SKILL_DIRS[@]}"}; do
    if [[ "$entry" == *"|claude|"* ]]; then
        HAS_CLAUDE=true
    elif [[ "$entry" == *"|codex|"* ]]; then
        HAS_CODEX=true
    fi
done

# --- Helper: iterate all skill directories ---
# Usage: for_each_skill_dir <callback_function>
# Callback receives: dir scope platform namespace
# namespace is empty for user/project/codex; set to the plugin or source name
# for plugin/source entries. Existing callbacks that ignore the 4th arg
# continue to work.
for_each_skill_dir() {
    local callback="$1"
    for entry in ${ALL_SKILL_DIRS[@]+"${ALL_SKILL_DIRS[@]}"}; do
        local scope="${entry%%|*}"
        local rest="${entry#*|}"
        local platform="${rest%%|*}"
        rest="${rest#*|}"
        local namespace="${rest%%|*}"
        local path="${rest#*|}"
        "$callback" "$path" "$scope" "$platform" "$namespace"
    done
}

# --- Shared: extract the description from SKILL.md frontmatter ---
# Handles inline scalars AND block scalars. Skills with folded descriptions
# previously read as empty, which made the always-loaded token split report 0
# for them and hid them from duplicate detection.
#
# The block-scalar header is [|>] plus an optional chomp indicator (- or +) and
# an optional explicit indent digit — | |- |+ |2 >- >+ >2 >-2 … Enumerating only
# the four commonest forms left the rest parsed as literal one- or two-character
# descriptions.
extract_description() {
    local file="$1"
    awk '
        { sub(/\r$/, "") }
        NR==1 && /^---$/ {started=1; next}
        started && /^---$/ {exit}
        started && !block && /^description:/ {
            val=$0; sub(/^description:[[:space:]]*/, "", val); gsub(/"/, "", val)
            if (val=="" || val ~ /^[|>][-+]?[0-9]*$/ || val ~ /^[|>][0-9]*[-+]?$/) {block=1; next}
            print val; exit
        }
        started && block && /^[[:space:]]+/ {line=$0; sub(/^[[:space:]]+/, "", line); printf "%s ", line; next}
        started && block {exit}
    ' "$file" 2>/dev/null | sed 's/[[:space:]]*$//'
}

# --- Platform display ---
platform_label() {
    if [[ "$HAS_CLAUDE" == "true" && "$HAS_CODEX" == "true" ]]; then
        echo "Claude Code + Codex"
    elif [[ "$HAS_CODEX" == "true" ]]; then
        echo "Codex"
    else
        echo "Claude Code"
    fi
}
