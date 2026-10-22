#!/usr/bin/env bash
# researcher-build.sh — build a per-repo dossier of contribution rules.
#
# Usage:
#   researcher-build.sh <owner>/<repo> [--no-link-follow] [--stdout]
#
# Default behavior: writes the dossier to
#   $CONTRIBUTE_STATE_DIR/research/<owner>__<repo>.md
# and prints "→ wrote dossier to <path>" to stderr so the caller has feedback.
#
# Override the output path via CONTRIBUTE_RESEARCH_DIR env var (the dossier
# lands at $CONTRIBUTE_RESEARCH_DIR/<owner>__<repo>.md).
#
# Refresh preserves the three manual section bodies. Pass --stdout for a
# merged preview without writing; never redirect it over the existing dossier.
#
# What it pulls:
#   - Repo metadata (stars, default branch, archived, push activity)
#   - Policy file inventory (CONTRIBUTING, CLA, DCO, AI_POLICY, SECURITY,
#     CODEOWNERS, PR template, code of conduct, governance)
#   - Raw CONTRIBUTING.md (with key excerpts)
#   - External links named by CONTRIBUTING.md, listed without fetching them
#   - External merge friendliness (last 90 days)
#   - Bots that auto-review on this repo (sampled from a recent PR)
#   - Convention detection: commit format, branch naming, sign-off, CLA, AI
#
# Design notes:
#   - Read-only against GitHub. Never writes to upstream.
#   - Uses temp dir for intermediate files; cleans up on exit.
#   - Optional GitHub reads degrade gracefully; required metadata must succeed.
#   - Ambiguous manual boundaries or publication failures refuse the refresh.

set -uo pipefail

: "${CONTRIBUTE_STATE_DIR:?CONTRIBUTE_STATE_DIR must be explicitly set}"
export CONTRIBUTE_STATE_DIR

REPO=""
NO_LINK_FOLLOW=""
TO_STDOUT=0
for arg in "$@"; do
  case "$arg" in
    --no-link-follow) NO_LINK_FOLLOW="--no-link-follow" ;;
    --stdout)         TO_STDOUT=1 ;;
    -h|--help)        /usr/bin/sed -n '2,16p' "$0" | /usr/bin/sed 's/^# \{0,1\}//'; exit 0 ;;
    -*)               /usr/bin/echo "unknown flag: $arg" >&2; exit 64 ;;
    *)                if [[ -z "$REPO" ]]; then REPO="$arg"; else /usr/bin/echo "extra arg: $arg" >&2; exit 64; fi ;;
  esac
done

if [[ -z "$REPO" || ! "$REPO" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
  /usr/bin/echo "usage: $0 <owner>/<repo> [--no-link-follow] [--stdout]" >&2
  exit 64
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh: not authenticated" >&2
  exit 65
fi

TMPDIR=$(/usr/bin/mktemp -d) || exit 73
trap 'rm -rf "$TMPDIR"' EXIT
NOW=$(/usr/bin/date -u +%Y-%m-%dT%H:%M:%SZ)
NINETY_AGO=$(/usr/bin/date -u -d '90 days ago' +%s)

log() { /usr/bin/echo "researcher-build: $*" >&2; }

# ---- 1. Repo metadata ----
log "[1/8] fetching repo metadata for $REPO"
META_FILE="$TMPDIR/meta.json"
gh api "repos/$REPO" > "$META_FILE" 2>/dev/null || { log "ERROR: repo $REPO not accessible"; exit 66; }
STARS=$(jq -r '.stargazers_count // 0' < "$META_FILE")
DEFAULT_BRANCH=$(jq -r '.default_branch // "main"' < "$META_FILE")
ARCHIVED=$(jq -r '.archived // false' < "$META_FILE")
PUSHED_AT=$(jq -r '.pushed_at // ""' < "$META_FILE")
LICENSE=$(jq -r '.license.spdx_id // "UNKNOWN"' < "$META_FILE")
LANG=$(jq -r '.language // "unknown"' < "$META_FILE")
DESC=$(jq -r '.description // ""' < "$META_FILE" | /usr/bin/head -c 200)

# ---- 2. Policy file inventory ----
log "[2/8] inventorying policy files"
declare -A POLICY_FILES
# Map: filename → display name. Try multiple paths per file (root + .github/).
for entry in \
  "CONTRIBUTING.md:CONTRIBUTING" \
  ".github/CONTRIBUTING.md:CONTRIBUTING" \
  "CODE_OF_CONDUCT.md:CODE_OF_CONDUCT" \
  ".github/CODE_OF_CONDUCT.md:CODE_OF_CONDUCT" \
  "SECURITY.md:SECURITY" \
  ".github/SECURITY.md:SECURITY" \
  "CLA.md:CLA" \
  "CLA.txt:CLA" \
  "DCO.md:DCO" \
  "DCO.txt:DCO" \
  "AI_POLICY.md:AI_POLICY" \
  "GOVERNANCE.md:GOVERNANCE" \
  "SETUP.md:SETUP" \
  "DEVELOPMENT.md:DEVELOPMENT" \
  ".github/CODEOWNERS:CODEOWNERS" \
  "CODEOWNERS:CODEOWNERS" \
  ".github/PULL_REQUEST_TEMPLATE.md:PR_TEMPLATE" \
  ".github/pull_request_template.md:PR_TEMPLATE" \
  "PULL_REQUEST_TEMPLATE.md:PR_TEMPLATE" \
  ".github/ISSUE_TEMPLATE.md:ISSUE_TEMPLATE_LEGACY" \
  ".github/issue_template.md:ISSUE_TEMPLATE_LEGACY" \
  "ISSUE_TEMPLATE.md:ISSUE_TEMPLATE_LEGACY"
do
  PATH_PART="${entry%:*}"
  KEY="${entry##*:}"
  # Skip if we already found this kind of file
  [[ -n "${POLICY_FILES[$KEY]:-}" ]] && continue

  # Probe by exit code, not by output. Earlier implementation captured stdout
  # and tested for non-empty — but `gh api` on 404 prints the error-shaped
  # JSON body ("{\"message\":\"Not Found\",...}") to stdout BEFORE jq runs,
  # and the existing `2>/dev/null` only silences stderr. Net effect: EXISTS
  # was non-empty for every probe, so every candidate file was claimed to
  # exist regardless of reality. Fix: redirect stdout to /dev/null too and
  # rely on the gh exit code as the existence signal.
  if gh api "repos/$REPO/contents/$PATH_PART" >/dev/null 2>&1 ; then
    POLICY_FILES[$KEY]="$PATH_PART"
  fi
done

# Also probe `docs/` subdir for projects (like secureblue) that house policy
# docs there instead of at the repo root. Only fills in slots that are still
# empty after the root + .github/ probes above.
for entry in \
  "docs/CONTRIBUTING.md:CONTRIBUTING" \
  "docs/CODE_OF_CONDUCT.md:CODE_OF_CONDUCT" \
  "docs/SECURITY.md:SECURITY" \
  "docs/CLA.md:CLA" \
  "docs/DCO.md:DCO" \
  "docs/AI_POLICY.md:AI_POLICY" \
  "docs/GOVERNANCE.md:GOVERNANCE" \
  "docs/SETUP.md:SETUP" \
  "docs/DEVELOPMENT.md:DEVELOPMENT" \
  "docs/PULL_REQUEST_TEMPLATE.md:PR_TEMPLATE"
do
  PATH_PART="${entry%:*}"
  KEY="${entry##*:}"
  [[ -n "${POLICY_FILES[$KEY]:-}" ]] && continue
  if gh api "repos/$REPO/contents/$PATH_PART" >/dev/null 2>&1 ; then
    POLICY_FILES[$KEY]="$PATH_PART"
  fi
done

# ---- 2b. Issue template directory inventory (.github/ISSUE_TEMPLATE/) ----
# A repo can have a single legacy template (handled above) OR a directory of
# templates (the modern pattern: bug-report.md, feature-request.md, design.md, etc.).
# We list every .md file in that dir so SKILL.md can pick the right one when
# drafting a Design Issue or feature request.
log "[2b/8] inventorying issue template directory"
declare -a ISSUE_TEMPLATES=()
ISSUE_TEMPLATE_DIR_LISTING=$(gh api "repos/$REPO/contents/.github/ISSUE_TEMPLATE" 2>/dev/null \
  | jq -r 'if type == "array" then .[] | select(.type == "file" and (.name | endswith(".md") or endswith(".yml") or endswith(".yaml"))) | .name else empty end' 2>/dev/null \
  || /usr/bin/echo "")
if [[ -n "$ISSUE_TEMPLATE_DIR_LISTING" ]] ; then
  while read -r TPL ; do
    [[ -n "$TPL" ]] && ISSUE_TEMPLATES+=("$TPL")
  done <<< "$ISSUE_TEMPLATE_DIR_LISTING"
fi

# ---- 3. Fetch CONTRIBUTING raw + extract links ----
log "[3/8] fetching + parsing CONTRIBUTING"
CONTRIB_RAW="$TMPDIR/contributing.md"
CONTRIB_PATH="${POLICY_FILES[CONTRIBUTING]:-}"
if [[ -n "$CONTRIB_PATH" ]] ; then
  gh api "repos/$REPO/contents/$CONTRIB_PATH" --jq '.content' 2>/dev/null \
    | /usr/bin/base64 -d > "$CONTRIB_RAW" 2>/dev/null \
    || /usr/bin/printf '' > "$CONTRIB_RAW"
fi
CONTRIB_BYTES=$(/usr/bin/wc -c < "$CONTRIB_RAW" 2>/dev/null || echo 0)

# Extract http(s) links from CONTRIBUTING — for depth-1 follow
LINKS_FILE="$TMPDIR/links.txt"
if [[ -s "$CONTRIB_RAW" ]] ; then
  /usr/bin/grep -oE 'https?://[A-Za-z0-9._/?&=#%~+:-]+' "$CONTRIB_RAW" \
    | /usr/bin/sed 's/[).,;:!]*$//' \
    | /usr/bin/sort -u > "$LINKS_FILE"
else
  : > "$LINKS_FILE"
fi

# ---- 4. Record external references without fetching untrusted URLs ----
# A repository controls CONTRIBUTING.md and therefore controls every extracted
# URL. Fetching those URLs would let an untrusted repository probe local or
# private-network endpoints. The portable distribution records references only.
declare -a DISCOVERED_LINKS=()
if [[ "$NO_LINK_FOLLOW" != "--no-link-follow" && -s "$LINKS_FILE" ]] ; then
  log "[4/8] listing external references without fetching them"
  while read -r URL ; do
    [[ "${#DISCOVERED_LINKS[@]}" -ge 15 ]] && break
    DISCOVERED_LINKS+=("$URL")
  done < "$LINKS_FILE"
else
  log "[4/8] external reference listing disabled"
fi

# ---- 5. External merge friendliness (last 90d) ----
log "[5/8] computing merge friendliness"
PRS_FILE="$TMPDIR/prs.json"
gh api "repos/$REPO/pulls?state=closed&sort=updated&direction=desc&per_page=100" > "$PRS_FILE" 2>/dev/null \
  || /usr/bin/printf '[]' > "$PRS_FILE"
EXT_COUNT=$(jq --arg cutoff "$NINETY_AGO" '
  [.[]
    | select(.merged_at != null)
    | select((.merged_at|fromdateiso8601) >= ($cutoff|tonumber))
    | select(.author_association == "CONTRIBUTOR" or .author_association == "FIRST_TIME_CONTRIBUTOR" or .author_association == "FIRST_TIMER" or .author_association == "NONE")
    | select(.user.type != "Bot")
  ] | length' < "$PRS_FILE" 2>/dev/null || echo 0)
LAST_EXT=$(jq -r '
  [.[]
    | select(.merged_at != null)
    | select(.author_association == "CONTRIBUTOR" or .author_association == "FIRST_TIME_CONTRIBUTOR" or .author_association == "NONE")
    | select(.user.type != "Bot")
  ] | sort_by(.merged_at) | reverse | .[0].merged_at // ""
  | if . == "" then "(none)" else .[0:10] end' < "$PRS_FILE" 2>/dev/null || echo "(err)")

# ---- 6. Bot detection (sample most-recently-updated merged PR) ----
log "[6/8] sampling review bots from a recent merged PR"
RECENT_PR=$(jq -r '[.[] | select(.merged_at != null)] | .[0].number // empty' < "$PRS_FILE" 2>/dev/null)
declare -a REVIEW_BOTS=()  # init empty (set -u)
if [[ -n "$RECENT_PR" ]] ; then
  REVIEWERS=$(gh pr view "$RECENT_PR" --repo "$REPO" --json reviews,comments \
    --jq '([.reviews[].author.login] + [.comments[].author.login]) | unique' 2>/dev/null)
  if [[ -n "$REVIEWERS" ]] ; then
    while read -r LOGIN ; do
      # Bot heuristic: ends in -bot, starts with app/, contains "bot" or "copilot" or "greptile" or "coderabbit" or "renovate" or "dependabot"
      if /usr/bin/echo "$LOGIN" | /usr/bin/grep -qiE 'bot$|^app/|copilot|greptile|coderabbit|renovate|dependabot|github-actions|deploy-status' ; then
        REVIEW_BOTS+=("$LOGIN")
      fi
    done < <(/usr/bin/echo "$REVIEWERS" | jq -r '.[]')
  fi
fi

# ---- 7. Convention detection ----
log "[7/8] detecting conventions from repository-hosted CONTRIBUTING"
ALL_TEXT="$TMPDIR/all-text.txt"
/usr/bin/cat "$CONTRIB_RAW" > "$ALL_TEXT"

detect() { /usr/bin/grep -qiE "$1" "$ALL_TEXT" 2>/dev/null && echo "true" || echo "false" ; }

CLA_REQUIRED=$(detect '\b(CLA|contributor license agreement)\b')
DCO_REQUIRED=$(detect '\b(DCO|developer certificate of origin|signed-off-by|sign-off)\b')
AI_DISCLOSURE=$(detect '\b(AI[-_ ]?(generated|assisted|policy|disclos)|Claude|Copilot|ChatGPT|LLM)\b')
CONVENTIONAL_COMMITS=$(detect '\bconventional commits?\b|^[a-z]+\([a-z-]+\): ')
ETIQUETTE_REQUIRED=$(detect 'comment on the issue|request assignment|let.{0,20}know you.{0,5}working|don.{0,3}t.{0,10}assign')
# Try to grab a test command pattern
TEST_CMD=$(/usr/bin/grep -ioE '(make|cargo|pnpm|yarn|npm|pytest|sbt|go) (test|test-cov|lint|format-check|typecheck|check)[^`\n]*' "$ALL_TEXT" 2>/dev/null | /usr/bin/head -1 | /usr/bin/sed 's/[`"]//g' | /usr/bin/cut -c1-100)

# ---- 8. Emit the dossier ----
log "[8/8] emitting dossier ($CONTRIB_BYTES bytes CONTRIBUTING, ${#DISCOVERED_LINKS[@]} external references listed, $EXT_COUNT ext merges)"

policy_list_yaml() {
  for KEY in "${!POLICY_FILES[@]}" ; do
    /usr/bin/printf '  - %s: %s\n' "$KEY" "${POLICY_FILES[$KEY]}"
  done | /usr/bin/sort
}

bot_list_yaml() {
  if [[ "${#REVIEW_BOTS[@]}" -eq 0 ]] ; then
    /usr/bin/printf '  - (none detected)\n'
  else
    for B in "${REVIEW_BOTS[@]}" ; do
      /usr/bin/printf '  - %s\n' "$B"
    done | /usr/bin/sort -u
  fi
}

issue_templates_section() {
  if [[ "${#ISSUE_TEMPLATES[@]}" -eq 0 ]] ; then
    if [[ -n "${POLICY_FILES[ISSUE_TEMPLATE_LEGACY]:-}" ]] ; then
      local TPL="${POLICY_FILES[ISSUE_TEMPLATE_LEGACY]}"
      /usr/bin/printf -- '- Legacy single-template at `%s` ([view](https://github.com/%s/blob/%s/%s)) — fetch this and fill it in.\n' \
        "$TPL" "$REPO" "$DEFAULT_BRANCH" "$TPL"
    else
      /usr/bin/echo "_No issue templates detected. The repo accepts free-form issue bodies. Fall back to a generic Design MD shape (problem / proposal / diff preview / test results)._"
    fi
  else
    /usr/bin/echo "_When opening a Design Issue / bug / feature request, **fetch the matching template first** and fill in its sections — do NOT replace the structure. The repo's reviewers expect this shape._"
    /usr/bin/echo
    for T in "${ISSUE_TEMPLATES[@]}" ; do
      /usr/bin/printf -- '- `%s` — [view](https://github.com/%s/blob/%s/.github/ISSUE_TEMPLATE/%s)\n' \
        "$T" "$REPO" "$DEFAULT_BRANCH" "$T"
    done
    /usr/bin/echo
    /usr/bin/echo "**To fetch a template body for filling in:**"
    /usr/bin/echo
    /usr/bin/echo '```bash'
    /usr/bin/printf 'gh api "repos/%s/contents/.github/ISSUE_TEMPLATE/<name>" --jq .content | base64 -d\n' "$REPO"
    /usr/bin/echo '```'
  fi
}

linked_sources_yaml() {
  if [[ "${#DISCOVERED_LINKS[@]}" -eq 0 ]] ; then
    /usr/bin/printf '  - (none listed)\n'
  else
    for U in "${DISCOVERED_LINKS[@]}" ; do
      /usr/bin/printf '  - { url: "%s", status: "not-fetched" }\n' "$U"
    done
  fi
}

# Resolve the stable destination, but never truncate it while generating.
RESEARCH_DIR="${CONTRIBUTE_RESEARCH_DIR:-$CONTRIBUTE_STATE_DIR/research}"
OUTPUT_FILE="$RESEARCH_DIR/$(/usr/bin/echo "$REPO" | /usr/bin/sed 's|/|__|').md"
GENERATED="$TMPDIR/generated.md"

# Only rendering is fail-fast. Optional GitHub discovery above retains its
# existing fallback behavior. Check the complete render before publication.
(
set -e
/usr/bin/cat <<DOSSIER
---
repo: $REPO
last_refreshed: $NOW
default_branch: $DEFAULT_BRANCH
archived: $ARCHIVED
stars: $STARS
language: $LANG
license: $LICENSE
last_pushed_at: $PUSHED_AT
external_merge_rate_90d: $EXT_COUNT
last_external_merge_at: $LAST_EXT
cla_required: $CLA_REQUIRED
dco_required: $DCO_REQUIRED
ai_disclosure_required: $AI_DISCLOSURE
conventional_commits: $CONVENTIONAL_COMMITS
etiquette_comment_required: $ETIQUETTE_REQUIRED
local_check_command: "${TEST_CMD:-(not detected)}"
policy_files:
$(policy_list_yaml)
issue_templates:
$(if [[ "${#ISSUE_TEMPLATES[@]}" -eq 0 ]] ; then
    /usr/bin/printf '  - (none — repo has no .github/ISSUE_TEMPLATE/ dir)\n'
  else
    for T in "${ISSUE_TEMPLATES[@]}" ; do
      /usr/bin/printf -- '  - { name: "%s", url: "https://github.com/%s/blob/%s/.github/ISSUE_TEMPLATE/%s" }\n' "$T" "$REPO" "$DEFAULT_BRANCH" "$T"
    done
  fi)
review_bots:
$(bot_list_yaml)
linked_sources:
$(linked_sources_yaml)
---

# $REPO — rules of engagement

> Auto-generated by researcher-build.sh on $NOW. Refresh with the contribute-prepare researcher role for $REPO (or any time CONTRIBUTING changes upstream).

## TL;DR

- $STARS ★ · $LANG · license: $LICENSE · default branch: \`$DEFAULT_BRANCH\`
- External merge velocity: **$EXT_COUNT** PRs in last 90d (last: $LAST_EXT)
- CLA: **$CLA_REQUIRED** · DCO: **$DCO_REQUIRED** · AI disclosure required: **$AI_DISCLOSURE**
- Etiquette comment required before claiming: **$ETIQUETTE_REQUIRED**
- Conventional Commits style: **$CONVENTIONAL_COMMITS**
- Local pre-PR command (detected): \`${TEST_CMD:-(none — read CONTRIBUTING)}\`

## Description

$DESC

## Policy file inventory

$(for KEY in "${!POLICY_FILES[@]}" ; do /usr/bin/printf -- '- **%s** → \`%s\` ([view](https://github.com/%s/blob/%s/%s))\n' "$KEY" "${POLICY_FILES[$KEY]}" "$REPO" "$DEFAULT_BRANCH" "${POLICY_FILES[$KEY]}" ; done | /usr/bin/sort)

## CONTRIBUTING.md — key excerpts

DOSSIER

# Excerpt the most actionable headed sections from CONTRIBUTING
if [[ -s "$CONTRIB_RAW" ]] ; then
  # Pull sections with names that hint at "things you must do"
  /usr/bin/awk '
    /^##+ / { keep = 0 }
    /^##+ .*([Cc]hecklist|[Pp]re-PR|[Bb]efore|[Tt]esting|[Tt]est|[Ww]orkflow|[Pp]ull [Rr]equest|[Bb]ranch|[Cc]ommit|[Ss]tyle|[Ff]ormat|[Aa]I|[Cc]ode [Qq]uality|[Cc]onvention|[Hh]ow to [Cc]ontribute|[Rr]eview|[Cc]ontribution [Ff]low|[Rr]ules)/ { keep = 1 }
    keep { print; if (++emitted >= 150) exit }
  ' "$CONTRIB_RAW"
  /usr/bin/echo
  /usr/bin/echo "_(excerpt only — full file: https://github.com/$REPO/blob/$DEFAULT_BRANCH/$CONTRIB_PATH)_"
else
  /usr/bin/echo "_No CONTRIBUTING.md found at the repo root or .github/. Read CODE_OF_CONDUCT.md and the PR template instead._"
fi

/usr/bin/cat <<TAIL

## External references (not fetched)

$(if [[ "${#DISCOVERED_LINKS[@]}" -eq 0 ]] ; then
    /usr/bin/echo "_No external references listed._"
  else
    /usr/bin/echo "_These URLs came from repository-controlled text and were not retrieved. Review them manually before opening._"
    /usr/bin/echo
    for U in "${DISCOVERED_LINKS[@]}" ; do
      /usr/bin/printf -- '- <%s>\n' "$U"
    done
  fi)

## Issue templates (use the matching one when opening a Design Issue or bug)

$(issue_templates_section)

## Bots that auto-review on this repo (sampled from PR #${RECENT_PR:-?})

$(bot_list_yaml | /usr/bin/sed 's/^  - /- /')

## Pet peeves & known triggers

_Specific things that get PRs closed at THIS repo. Manually + LLM-curated. Survives refresh — researcher does NOT auto-populate this section. Add an entry every time you observe a pet peeve in the wild._

- _(no entries yet — populate as observations land)_

## Failure log

_Chronological record of past closures with reasons at this repo. Auto-appended on \`status: dropped\` transitions; never overwritten on refresh._

## Notes

_Free-form area for the human to leave per-repo intuition. Survives refresh._

TAIL

) > "$GENERATED"
RENDER_RESULT=$?
if [[ "$RENDER_RESULT" -ne 0 ]]; then
  log "ERROR: dossier rendering failed; destination unchanged"
  exit "$RENDER_RESULT"
fi

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 73
PUBLISH_ARGS=()
[[ "$TO_STDOUT" -eq 1 ]] && PUBLISH_ARGS+=(--stdout)
python3 "$SCRIPT_DIR/researcher-refresh.py" "$GENERATED" "$OUTPUT_FILE" "${PUBLISH_ARGS[@]}" || exit $?
if [[ "$TO_STDOUT" -eq 0 ]]; then
  log "→ wrote dossier to $OUTPUT_FILE"
fi
