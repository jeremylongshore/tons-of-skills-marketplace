#!/bin/bash
# Skills Janitor - Swipe TUI
# Tinder for your Claude Code skills. Score-sorted deck, swipe left to stage
# delete, right to keep. Pure bash + ANSI, zero deps (uses python3 only to
# parse the deck JSON, same as the rest of the project).
#
# Must run from an interactive terminal. Inside Claude Code, prefix with `!`
# so the shell — not the Bash tool — handles stdin:
#   !bash ~/.claude/skills/skills-janitor/scripts/swipe.sh

set -euo pipefail

command -v python3 &>/dev/null || { echo "ERROR: python3 required" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPLY_MODE=""
DECK_FILE=""
LOG_FILE="$HOME/.skills-janitor/log.jsonl"
DECISIONS_DIR="$HOME/.skills-janitor"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --apply) APPLY_MODE="$2"; shift 2 ;;
        --deck) DECK_FILE="$2"; shift 2 ;;
        -h|--help)
            cat <<'HELP'
Usage: swipe.sh [--deck <file>] [--apply <decisions.json>]

Tinder for your Claude Code skills. Reviews a score-sorted deck of all
installed skills, lets you keep / skip / stage-delete each one, then applies
the deletions on confirmation.

  --deck <file>       Use existing deck JSON instead of regenerating
  --apply <file>      Skip the TUI and apply decisions saved earlier with `save`
HELP
            exit 0
            ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ────────────────────────────────────────────────────────────────────────────
# Apply-mode short circuit
# ────────────────────────────────────────────────────────────────────────────
if [[ -n "$APPLY_MODE" ]]; then
    [[ -f "$APPLY_MODE" ]] || { echo "Decisions file not found: $APPLY_MODE" >&2; exit 1; }
    DECK_FILE="$APPLY_MODE"
    SKIP_TUI=1
else
    SKIP_TUI=0
fi

# ────────────────────────────────────────────────────────────────────────────
# Sanity checks for TUI mode
# ────────────────────────────────────────────────────────────────────────────
if [[ "$SKIP_TUI" == "0" ]]; then
    if [ ! -t 0 ]; then
        cat >&2 <<'MSG'
Swipe needs an interactive terminal. Inside Claude Code, prefix the command
with `!` so the shell handles stdin:
  !bash ~/.claude/skills/skills-janitor/scripts/swipe.sh

For the same data in list form, run /janitor-report or /janitor-value instead.
MSG
        exit 1
    fi
    COLS=$(tput cols)
    LINES_T=$(tput lines)
    if [[ "$COLS" -lt 50 ]]; then
        echo "Swipe needs at least 50 columns. Yours: $COLS. Resize and retry." >&2
        exit 1
    fi
    if [[ "$LINES_T" -lt 22 ]]; then
        echo "Swipe needs at least 22 rows. Yours: $LINES_T. Resize and retry." >&2
        exit 1
    fi
fi

# ────────────────────────────────────────────────────────────────────────────
# Build deck (unless one was passed in)
# ────────────────────────────────────────────────────────────────────────────
if [[ -z "$DECK_FILE" ]]; then
    DECK_FILE=$(mktemp -t janitor-deck.XXXXXX.json)
    bash "$SCRIPT_DIR/swipe-build-deck.sh" "$DECK_FILE" >/dev/null
fi

# Extract card data into a TSV the bash loop can read
DECK_TSV=$(mktemp -t janitor-deck.XXXXXX.tsv)
trap 'rm -f "$DECK_TSV"; restore_term 2>/dev/null || true' EXIT

DECK_META=$(python3 - "$DECK_FILE" "$DECK_TSV" <<'PYEOF'
import json, sys
deck = json.load(open(sys.argv[1]))
# bash `read` with IFS=$'\t' collapses consecutive tabs (because tab is
# whitespace), so empty fields would shift later columns. Replace empty
# values with a sentinel that bash decodes back to empty.
SENTINEL = "_"
def s(v):
    if v is None or v == "":
        return SENTINEL
    return str(v).replace("\t", " ").replace("\n", "\\n")
with open(sys.argv[2], "w") as f:
    for c in deck["cards"]:
        v = c.get("verdict", {})
        row = [
            s(c.get("id")),
            s(c.get("name")),
            s(c.get("scope")),
            s(c.get("namespace")),
            s(c.get("path")),
            s(c.get("tokens", 0)),
            s(c.get("desc_tokens", 0)),
            s(f'{c.get("tokens_pct_budget", 0):.1f}'),
            s(c.get("invocations", 0)),
            s(c.get("last_used", "never")),
            s(c.get("days_since_use")),
            s(f'{v.get("score", 0):.1f}'),
            s(v.get("label")),
            s(v.get("tone", "neutral")),
            s(c.get("description")),
            s(c.get("decision")),
        ]
        f.write("\t".join(row) + "\n")
print(len(deck["cards"]), deck.get("budget", 200000))
PYEOF
)
TOTAL=$(echo "$DECK_META" | awk '{print $1}')
BUDGET=$(echo "$DECK_META" | awk '{print $2}')

if [[ "$TOTAL" -eq 0 ]]; then
    echo "No skills to swipe. Install some with /plugin install first." >&2
    exit 0
fi

# Read cards into parallel arrays. Sentinel "_" decodes back to empty (see
# python emitter above for why this dance is needed).
declare -a IDS NAMES SCOPES NAMESPACES PATHS TOKENS DESC_TOKENS PCTS USES LAST_USED DAYS SCORES LABELS TONES DESCS DECISIONS
unsentinel() { [[ "$1" == "_" ]] && echo "" || echo "$1"; }
while IFS=$'\t' read -r id name scope ns path tok dtok pct inv lu days score label tone desc dec; do
    IDS+=("$(unsentinel "$id")"); NAMES+=("$(unsentinel "$name")")
    SCOPES+=("$(unsentinel "$scope")"); NAMESPACES+=("$(unsentinel "$ns")")
    PATHS+=("$(unsentinel "$path")"); TOKENS+=("$(unsentinel "$tok")")
    DESC_TOKENS+=("$(unsentinel "$dtok")")
    PCTS+=("$(unsentinel "$pct")"); USES+=("$(unsentinel "$inv")")
    LAST_USED+=("$(unsentinel "$lu")"); DAYS+=("$(unsentinel "$days")")
    SCORES+=("$(unsentinel "$score")"); LABELS+=("$(unsentinel "$label")")
    TONES+=("$(unsentinel "$tone")"); DESCS+=("$(unsentinel "$desc")")
    DECISIONS+=("$(unsentinel "$dec")")
done < "$DECK_TSV"

# ────────────────────────────────────────────────────────────────────────────
# ANSI helpers
# ────────────────────────────────────────────────────────────────────────────
ESC=$'\033'
CLEAR="${ESC}[2J${ESC}[H"
HIDE_CURSOR="${ESC}[?25l"
SHOW_CURSOR="${ESC}[?25h"
RESET="${ESC}[0m"
DIM="${ESC}[2m"
BOLD="${ESC}[1m"
RED="${ESC}[31m"
GREEN="${ESC}[32m"
YELLOW="${ESC}[33m"
GRAY="${ESC}[90m"

restore_term() {
    printf "%s" "$SHOW_CURSOR$RESET"
    stty echo icanon 2>/dev/null || true
}

# ────────────────────────────────────────────────────────────────────────────
# Card rendering
# ────────────────────────────────────────────────────────────────────────────
CARD_WIDTH=60
INNER_WIDTH=$((CARD_WIDTH - 6))  # "│  " (3) + content + "  │" (3)

# Print a line inside the card with proper padding (handles trailing spaces)
card_line() {
    local content="$1"
    local pad=$((INNER_WIDTH - ${#content}))
    [ "$pad" -lt 0 ] && pad=0
    printf "│  %s%${pad}s  │\n" "$content" ""
}

card_blank() {
    printf "│%-${CARD_WIDTH}s│\n" "" | sed "s/ /  /g; s/  //$(( (CARD_WIDTH/2) - 1 ))//" >/dev/null
    printf "│%*s│\n" $((CARD_WIDTH - 2)) ""
}

card_divider() {
    local label="$1"
    local prefix="─ ${label} "
    local rest=$((INNER_WIDTH - ${#prefix}))
    [ "$rest" -lt 0 ] && rest=0
    local dashes=""
    for ((d=0; d<rest; d++)); do dashes+="─"; done
    printf "│  ${DIM}%s%s${RESET}  │\n" "$prefix" "$dashes"
}

# Truncate text to a width
trunc() {
    local s="$1" max="$2"
    if [ ${#s} -le "$max" ]; then
        printf "%s" "$s"
    else
        printf "%s…" "${s:0:$((max-1))}"
    fi
}

# Tone → color
tone_color() {
    case "$1" in
        warn) echo "$YELLOW" ;;
        good) echo "$GREEN" ;;
        *)    echo "$GRAY" ;;
    esac
}

render_card() {
    local i="$1"
    local pos=$((i + 1))
    local name="${NAMES[$i]}"
    local scope="${SCOPES[$i]}"
    local ns="${NAMESPACES[$i]}"
    local tokens="${TOKENS[$i]}"
    local pct="${PCTS[$i]}"
    local uses="${USES[$i]}"
    local lu="${LAST_USED[$i]}"
    local days="${DAYS[$i]}"
    local label="${LABELS[$i]}"
    local tone="${TONES[$i]}"
    local desc="${DESCS[$i]}"
    local decision="${DECISIONS[$i]}"

    # Border color reflects decision (if already decided)
    local bcolor="$RESET"
    case "$decision" in
        delete) bcolor="$RED" ;;
        keep)   bcolor="$GREEN" ;;
        skip)   bcolor="$DIM" ;;
    esac

    printf "%s" "$CLEAR"
    printf "%s" "$bcolor"

    # Top border
    printf "╭"
    for ((j=0; j<CARD_WIDTH-2; j++)); do printf "─"; done
    printf "╮\n"

    # Title row: name (left) + position (right)
    local pos_str="[$pos / $TOTAL]"
    local name_max=$((INNER_WIDTH - ${#pos_str} - 2))
    local name_trunc=$(trunc "$name" "$name_max")
    local title_pad=$((INNER_WIDTH - ${#name_trunc} - ${#pos_str}))
    printf "│  ${BOLD}%s${RESET}%${title_pad}s${DIM}%s${RESET}  │\n" "$name_trunc" "" "$pos_str"

    # Separator under title
    printf "│  "
    for ((j=0; j<INNER_WIDTH; j++)); do printf "═"; done
    printf "  │\n"

    # Blank row
    printf "│%*s│\n" $((CARD_WIDTH - 2)) ""

    # Stats rows
    local scope_label="$scope"
    [ -n "$ns" ] && scope_label="$scope · $ns"
    local dtok="${DESC_TOKENS[$i]:-0}"
    local body_tok=$((tokens - dtok))
    [ "$body_tok" -lt 0 ] && body_tok=0
    case "$scope" in
        mcp-*)
            # MCP schemas live server-side — no token guesses, just the fact
            card_line "Context    tool schemas load while connected"
            ;;
        *)
            # "always" = description tokens, permanently in the system prompt;
            # "on trigger" = the body, loaded only when the skill fires.
            card_line "$(printf 'Context    %s always · %s on trigger' "$dtok" "$body_tok")"
            ;;
    esac

    local use_label
    if [ "$uses" -eq 0 ]; then
        use_label="$(printf 'Used       %s0×%s    never invoked' "$DIM" "$RESET")"
    else
        use_label="$(printf 'Used       %s×    last %s' "$uses" "$lu")"
    fi
    # Strip ANSI from length calculation in card_line — use plain variant
    if [ "$uses" -eq 0 ]; then
        card_line "Used       0×    never invoked"
    else
        card_line "$(printf 'Used       %s×    last %s' "$uses" "$lu")"
    fi
    card_line "Scope      $scope_label"

    printf "│%*s│\n" $((CARD_WIDTH - 2)) ""

    # Description divider + 3 lines
    card_divider "Description"
    local desc_decoded="${desc//\\n/ }"
    local desc_max=$((INNER_WIDTH))
    local d_pos=0 line
    for ((dl=0; dl<3; dl++)); do
        if [ "$d_pos" -ge "${#desc_decoded}" ]; then
            card_line ""
        else
            line="${desc_decoded:$d_pos:$desc_max}"
            # Word boundary — if more text follows, back up to last space
            if [ $((d_pos + desc_max)) -lt "${#desc_decoded}" ] && [ "$dl" -lt 2 ]; then
                local space_idx="${line%[![:space:]]*}"
                # Find last space
                local trimmed="${line% *}"
                if [ -n "$trimmed" ] && [ "${#trimmed}" -lt "${#line}" ]; then
                    line="$trimmed"
                fi
            fi
            # Add ellipsis on last visible line if more remains
            if [ "$dl" -eq 2 ] && [ $((d_pos + ${#line})) -lt "${#desc_decoded}" ]; then
                line="${line:0:$((desc_max-1))}…"
            fi
            card_line "$line"
            d_pos=$((d_pos + ${#line}))
            # Skip a leading space on the next line
            while [ "$d_pos" -lt "${#desc_decoded}" ] && [ "${desc_decoded:$d_pos:1}" = " " ]; do
                d_pos=$((d_pos + 1))
            done
        fi
    done

    printf "│%*s│\n" $((CARD_WIDTH - 2)) ""

    # Verdict
    card_divider "Verdict"
    local tcolor=$(tone_color "$tone")
    local marker="·"
    [ "$tone" = "warn" ] && marker="⚠"
    [ "$tone" = "good" ] && marker="✓"
    card_line "$(printf '%s  %s' "$marker" "$label")"

    # Bottom border
    printf "│%*s│\n" $((CARD_WIDTH - 2)) ""
    printf "╰"
    for ((j=0; j<CARD_WIDTH-2; j++)); do printf "─"; done
    printf "╯\n"

    printf "%s" "$RESET"

    # Action hints
    printf "   ${DIM}← delete    ↓ skip    → keep    u undo    i inspect    q quit${RESET}\n"

    # Progress bar
    local bar_width=$((CARD_WIDTH - 12))
    local filled=$(( (pos * bar_width) / TOTAL ))
    local bar=""
    for ((b=0; b<filled; b++)); do bar+="█"; done
    for ((b=filled; b<bar_width; b++)); do bar+="░"; done
    printf "   ${DIM}%s  %d / %d${RESET}\n" "$bar" "$pos" "$TOTAL"
}

# ────────────────────────────────────────────────────────────────────────────
# Inspect view — full SKILL.md description (no truncation)
# ────────────────────────────────────────────────────────────────────────────
show_inspect() {
    local i="$1"
    printf "%s" "$CLEAR"
    printf "${BOLD}%s${RESET}\n\n" "${NAMES[$i]}"
    printf "${DIM}Path:${RESET} %s\n\n" "${PATHS[$i]}"
    printf "${BOLD}Description:${RESET}\n"
    printf "%s\n\n" "${DESCS[$i]//\\n/$'\n'}"
    printf "${DIM}Press any key to return…${RESET}"
    read -rsn1
}

# ────────────────────────────────────────────────────────────────────────────
# Keypress reader — handles arrow escape sequences
# ────────────────────────────────────────────────────────────────────────────
read_key() {
    local key rest
    IFS= read -rsn1 key
    if [[ "$key" == $'\033' ]]; then
        # Could be an arrow (ESC [ X, sent together) or standalone ESC.
        # macOS bash 3 doesn't support fractional -t timeouts; use integer.
        # In practice the 2 trailing bytes of an arrow arrive instantly so
        # `-t 1` just bounds the wait for a standalone ESC press.
        IFS= read -rsn2 -t 1 rest 2>/dev/null || rest=""
        key="$key$rest"
    fi
    echo "$key"
}

# ────────────────────────────────────────────────────────────────────────────
# Apply screen — confirmation summary + actual deletions
# ────────────────────────────────────────────────────────────────────────────
do_apply() {
    local keep=0 delete=0 skip=0 undecided=0
    local deleted_tokens=0 deleted_desc_tokens=0
    local -a delete_paths delete_names delete_scopes delete_tokens_per

    # Tempfiles for plugin aggregation (bash 3 has no associative arrays)
    local plugin_delete_tmp plugin_total_tmp
    plugin_delete_tmp=$(mktemp)
    plugin_total_tmp=$(mktemp)
    # shellcheck disable=SC2064
    trap "rm -f '$DECK_TSV' '$plugin_delete_tmp' '$plugin_total_tmp'; restore_term 2>/dev/null || true" EXIT

    local -a mcp_names mcp_origins
    for ((i=0; i<TOTAL; i++)); do
        local s="${SCOPES[$i]}"
        if [[ "$s" == "plugin" ]] || [[ "$s" == "plugin-source" ]]; then
            echo "${NAMESPACES[$i]}" >> "$plugin_total_tmp"
        fi
        case "${DECISIONS[$i]}" in
            keep) ((keep++)) ;;
            delete)
                ((delete++))
                deleted_tokens=$((deleted_tokens + TOKENS[i]))
                deleted_desc_tokens=$((deleted_desc_tokens + ${DESC_TOKENS[$i]:-0}))
                if [[ "$s" == "plugin" ]] || [[ "$s" == "plugin-source" ]]; then
                    echo "${NAMESPACES[$i]}" >> "$plugin_delete_tmp"
                elif [[ "$s" == "mcp-plugin" ]]; then
                    # plugin-bundled MCP: can't edit the plugin — flag it
                    echo "${NAMESPACES[$i]#plugin:}" >> "$plugin_delete_tmp"
                elif [[ "$s" == mcp-* ]]; then
                    mcp_names+=("${NAMES[$i]}")
                    mcp_origins+=("${PATHS[$i]}")
                else
                    delete_paths+=("${PATHS[$i]}")
                    delete_names+=("${NAMES[$i]}")
                    delete_scopes+=("$s")
                    delete_tokens_per+=("${TOKENS[$i]}")
                fi
                ;;
            skip) ((skip++)) ;;
            "") ((undecided++)) ;;
        esac
    done

    printf "%s" "$CLEAR"
    printf "${BOLD}═══ Swipe Summary ═══${RESET}\n\n"
    printf "Keep:       %3d skills\n" "$keep"
    printf "Skip:       %3d skills\n" "$skip"
    printf "Delete:     %3d skills" "$delete"
    if [[ "$delete" -gt 0 ]]; then
        # Honest framing: only descriptions are permanent context cost; the
        # body total is what those skills could pull in when triggered.
        local body_freed=$((deleted_tokens - deleted_desc_tokens))
        [[ "$body_freed" -lt 0 ]] && body_freed=0
        printf "  ${DIM}(frees ~%s always-loaded tokens + %s on-trigger)${RESET}" \
            "$(printf "%'d" "$deleted_desc_tokens" 2>/dev/null || echo "$deleted_desc_tokens")" \
            "$(printf "%'d" "$body_freed" 2>/dev/null || echo "$body_freed")"
    fi
    printf "\n"
    [[ "$undecided" -gt 0 ]] && printf "Undecided:  %3d skills ${DIM}(treated as skip)${RESET}\n" "$undecided"
    printf "\n"

    if [[ "${#delete_paths[@]}" -gt 0 ]]; then
        printf "${BOLD}Deletions (user/project/codex scope):${RESET}\n"
        for ((j=0; j<${#delete_paths[@]}; j++)); do
            printf "  ${RED}✗${RESET}  %-30s ${DIM}%-8s %s${RESET}\n" "${delete_names[$j]}" "${delete_scopes[$j]}" "${delete_paths[$j]}"
        done
        printf "\n"
    fi

    if [[ ${mcp_names[@]+x} ]] && [[ "${#mcp_names[@]}" -gt 0 ]]; then
        printf "${BOLD}MCP entries to remove${RESET} ${DIM}(config edit with .bak backup):${RESET}\n"
        for ((j=0; j<${#mcp_names[@]}; j++)); do
            printf "  ${RED}✗${RESET}  %-24s ${DIM}%s${RESET}\n" "${mcp_names[$j]}" "${mcp_origins[$j]}"
        done
        printf "\n"
    fi

    # Plugin summary — one line per plugin showing "<deleted> of <total> swiped"
    if [[ -s "$plugin_delete_tmp" ]]; then
        printf "${BOLD}Plugins to review${RESET} ${DIM}(individual plugin skills cannot be deleted):${RESET}\n"
        # Build "plugin deleted total" tuples
        sort "$plugin_delete_tmp" | uniq -c | while read -r n_delete plugin; do
            local n_total
            n_total=$(grep -c "^${plugin}$" "$plugin_total_tmp" || true)
            [[ -z "$n_total" || "$n_total" -eq 0 ]] && n_total="$n_delete"
            printf "  %-25s ${DIM}%s of %s swiped delete${RESET}  →  consider ${BOLD}/plugin uninstall %s${RESET}\n" "$plugin" "$n_delete" "$n_total" "$plugin"
        done
        printf "\n"
    fi

    if [[ "$delete" -eq 0 ]]; then
        printf "${DIM}Nothing staged for deletion. Done.${RESET}\n"
        return 0
    fi

    printf "${BOLD}Apply deletions?${RESET}  ${DIM}[y/N/save]${RESET}  "
    stty echo icanon
    local answer
    read -r answer
    stty -echo

    case "$answer" in
        y|Y|yes)
            # Make log dir
            mkdir -p "$DECISIONS_DIR"
            local ts
            ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
            for ((j=0; j<${#delete_paths[@]}; j++)); do
                local p="${delete_paths[$j]}"
                local n="${delete_names[$j]}"
                local s="${delete_scopes[$j]}"
                if [[ -L "$p" ]]; then
                    # Symlink — remove the link, never follow
                    rm "$p" && printf "${GREEN}unlinked${RESET} %s\n" "$n"
                elif [[ -d "$p" ]]; then
                    rm -rf "$p" && printf "${GREEN}deleted${RESET}  %s\n" "$n"
                else
                    printf "${YELLOW}skipped${RESET}  %s ${DIM}(path missing)${RESET}\n" "$n"
                fi
                # Log
                printf '{"ts":"%s","action":"delete","name":"%s","scope":"%s","path":"%s","tokens":%s}\n' \
                    "$ts" "$n" "$s" "$p" "${delete_tokens_per[$j]:-0}" >> "$LOG_FILE"
            done
            # MCP entries: remove from their config file (with .bak backup)
            if [[ ${mcp_names[@]+x} ]]; then
            for ((j=0; j<${#mcp_names[@]}; j++)); do
                if python3 - "${mcp_names[$j]}" "${mcp_origins[$j]}" <<'PYMCP'
import json, shutil, sys, time
name, origin = sys.argv[1], sys.argv[2]
proj = None
if " [projects -> " in origin:
    cfg_path, rest = origin.split(" [projects -> ", 1)
    proj = rest.rstrip("]")
else:
    cfg_path = origin
try:
    with open(cfg_path) as f:
        data = json.load(f)
except Exception as e:
    sys.exit(f"cannot read {cfg_path}: {e}")
target = data
if proj is not None:
    target = data.get("projects", {}).get(proj, {})
servers = target.get("mcpServers", {})
if name not in servers:
    sys.exit(f"{name} not present in {cfg_path}")
shutil.copy2(cfg_path, cfg_path + ".bak-janitor-" + time.strftime("%Y%m%d%H%M%S"))
del servers[name]
with open(cfg_path, "w") as f:
    json.dump(data, f, indent=2)
PYMCP
                then
                    printf "${GREEN}removed${RESET}  MCP %s ${DIM}(%s)${RESET}\n" "${mcp_names[$j]}" "${mcp_origins[$j]}"
                    printf '{"ts":"%s","action":"mcp-remove","name":"%s","origin":"%s"}\n' \
                        "$ts" "${mcp_names[$j]}" "${mcp_origins[$j]}" >> "$LOG_FILE"
                else
                    printf "${YELLOW}skipped${RESET}  MCP %s ${DIM}(edit failed — config untouched)${RESET}\n" "${mcp_names[$j]}"
                fi
            done
            fi
            printf "\n${DIM}Log: %s${RESET}\n" "$LOG_FILE"
            ;;
        save)
            mkdir -p "$DECISIONS_DIR"
            local save_file="$DECISIONS_DIR/swipe-$(date -u +%Y-%m-%dT%H%M%S).json"
            python3 - "$DECK_FILE" "$save_file" "${DECISIONS[@]}" <<'PYEOF'
import json, sys
deck = json.load(open(sys.argv[1]))
out = sys.argv[2]
decisions = sys.argv[3:]
for i, c in enumerate(deck["cards"]):
    c["decision"] = decisions[i] if i < len(decisions) else ""
deck["saved_at"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
json.dump(deck, open(out, "w"), indent=2)
PYEOF
            printf "\n${GREEN}Decisions saved${RESET} to %s\n" "$save_file"
            printf "${DIM}Apply later with:  swipe.sh --apply %s${RESET}\n" "$save_file"
            ;;
        *)
            printf "\n${DIM}Cancelled. No changes.${RESET}\n"
            ;;
    esac
}

# ────────────────────────────────────────────────────────────────────────────
# Main loop (skipped in --apply mode, where decisions come from the file)
# ────────────────────────────────────────────────────────────────────────────
if [[ "$SKIP_TUI" == "0" ]]; then
    stty -echo
    printf "%s" "$HIDE_CURSOR"

    i=0
    while [[ $i -lt $TOTAL ]]; do
        render_card "$i"
        key=$(read_key)
        case "$key" in
            $'\033[D'|h|d|D)
                DECISIONS[$i]="delete"
                ((i++))
                ;;
            $'\033[C'|l|k|K)
                DECISIONS[$i]="keep"
                ((i++))
                ;;
            $'\033[B'|j|s|S|' ')
                DECISIONS[$i]="skip"
                ((i++))
                ;;
            u|U)
                [[ $i -gt 0 ]] && { ((i--)); DECISIONS[$i]=""; }
                ;;
            i|I)
                show_inspect "$i"
                ;;
            q|Q|$'\033')
                break
                ;;
        esac
    done

    printf "%s" "$SHOW_CURSOR"
fi

do_apply
