#!/usr/bin/env bash
# dolt-idle-reaper.sh — gracefully stop idle bd-managed `dolt sql-server`
# processes so they don't accumulate (the "18 sprawled servers" problem).
#
# Reap only after an idle check and clean main-branch working-set observations
# for every visible user database. Unknown status always keeps the server.
# This is not an atomic shutdown protocol: activity/identity are rechecked, but a
# concurrent write can still race the final check and SIGTERM. Other branches
# and databases hidden from the configured account are not covered. Use only
# for bd-managed servers whose work is on main and whose account sees all DBs.
# Limits and rollback: README.md in jeremylongshore/dolt-mcp-vcs-plugin.
#
# Working-set check: we ask the running server itself, through the dolthub-official
# dolt-mcp client this plugin ships (scripts/dolt-mcp-client.py) — the dolt CLI
# does not reliably honor `--no-tls` for the sql-client connection, so a fresh
# MCP connection is the dependable read path. `SELECT COUNT(*) FROM dolt_status`
# reflects the server's in-memory working set; any non-empty result on any user
# database => dirty => skip.
#
# "Idle" = the workspace's .beads/ activity files (last-touched, issues.jsonl,
# dolt-server.log — the log updates on every query, so reads count too) have not
# changed in $IDLE_MIN minutes.
#
# Usage:
#   dolt-idle-reaper.sh                 # reap CLEAN servers idle > IDLE_MIN (default 90)
#   dolt-idle-reaper.sh --dry-run       # show the dirty-skip / clean-reap split, change nothing
#   IDLE_MIN=120 dolt-idle-reaper.sh    # custom idle threshold
#
# Requires: python3, dolt-mcp-server on PATH (go install
#   github.com/dolthub/dolt-mcp/mcp/cmd/dolt-mcp-server@v0.3.6), and
#   scripts/dolt-mcp-client.py beside this script.
#
# Cron (every 30 min):
#   3,33 * * * * /path/to/dolt-idle-reaper.sh >> ~/.local/state/dolt-reaper/reap.log 2>&1
set -uo pipefail

# Resolve only positively identified bd-managed servers. A Dolt process in a
# repository with .beads is not enough: workspace-root launches require the
# exact bd dolt-server.pid marker. Unrelated/Freshie servers must stay alive.
bd_workspace() {
  local pid="$1" cwd="$2" marker
  case "$cwd" in
    */.beads/dolt)
      [ -d "$cwd" ] || return 1
      echo "${cwd%/.beads/dolt}"
      ;;
    */.beads)
      [ -d "$cwd" ] || return 1
      echo "${cwd%/.beads}"
      ;;
    *)
      marker="$cwd/.beads/dolt-server.pid"
      [ -f "$marker" ] || return 1
      [ "$(cat "$marker" 2>/dev/null)" = "$pid" ] || return 1
      echo "$cwd"
      ;;
  esac
}

# Portable mtime (epoch seconds): GNU stat, then BSD/macOS stat, then date -r.
# Falls back to 0 only when all three fail (missing file / unsupported toolchain),
# which callers treat as "no activity timestamp available."
mtime() {
  stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || date -r "$1" +%s 2>/dev/null || echo 0
}

# Most-recent activity timestamp (epoch) across a workspace's .beads activity files.
latest_activity() {
  local bd="$1/.beads" newest=0 m
  for f in last-touched issues.jsonl dolt-server.log interactions.jsonl; do
    [ -f "$bd/$f" ] || continue
    m=$(mtime "$bd/$f")
    [ "$m" -gt "$newest" ] && newest=$m
  done
  echo "$newest"
}

# Return process start ticks and its single owned IPv4 loopback listener.
# Missing/ambiguous ownership, a different network namespace, or a non-Dolt
# command refuses the candidate. Do not trust its declared command-line port.
server_identity() {
  python3 "$SELF_DIR/reaper_endpoint.py" "$1" 2>/dev/null
}

# working_set_clean <port> — return 0 ONLY if every user database on the server
# has an empty main-branch working set visible to the configured account.
# Return 1 (skip) on ANY uncommitted change, query error, unreachable server,
# or missing toolchain. Conservative by design.
working_set_clean() {
  local port="$1" dbs db n bootstrap='' any_user=0
  local -a rows
  [[ "$port" =~ ^[1-9][0-9]{0,4}$ ]] && [ "$port" -le 65535 ] || return 1
  command -v python3 >/dev/null 2>&1 || return 1
  command -v dolt-mcp-server >/dev/null 2>&1 || return 1
  [ -f "$MCP_CLIENT" ] || return 1

  dbs=$(python3 "$MCP_CLIENT" --host 127.0.0.1 --flavor dolt \
    --port "$port" --database information_schema --branch main list_databases 2>/dev/null) || return 1
  # The text list is only a connection hint: its unescaped rows cannot prove
  # inventory completeness. The pinned query tool needs a user DB for its
  # DOLT_CHECKOUT, so use one ordinary candidate to query encoded schema names.
  mapfile -t rows <<< "$dbs"
  [ "${rows[0]:-}" = Database ] && [ "${rows[1]:-}" = '---' ] || return 1
  for db in "${rows[@]:2}"; do
    [[ "$db" =~ ^[a-zA-Z0-9_][a-zA-Z0-9_.-]*$ ]] || return 1
    case "$db" in
      information_schema|mysql|performance_schema|sys) continue ;;
    esac
    [ -n "$bootstrap" ] || bootstrap="$db"
  done
  [ -n "$bootstrap" ] || return 1
  dbs=$(python3 "$MCP_CLIENT" --host 127.0.0.1 --flavor dolt --port "$port" \
    --database "$bootstrap" --branch main query \
    "SELECT HEX(SCHEMA_NAME) AS database_hex FROM information_schema.SCHEMATA" \
    2>/dev/null) || return 1
  # Validate the whole encoded inventory before emitting any names. Embedded
  # newlines, NULs, Markdown delimiters, non-ASCII, and malformed hex all refuse.
  dbs=$(python3 -c '
import re
import sys
try:
    rows = sys.stdin.read().rstrip("\n").split("\n")
    if rows[:2] != ["database_hex", "---"] or len(rows) < 3:
        raise ValueError("invalid inventory header or empty inventory")
    names = []
    for row in rows[2:]:
        if not re.fullmatch(r"(?:[0-9A-F]{2})+", row):
            raise ValueError("invalid encoded name")
        name = bytes.fromhex(row).decode("ascii")
        if not re.fullmatch(r"[a-zA-Z0-9_][a-zA-Z0-9_.-]*", name):
            raise ValueError("unsupported database identifier")
        names.append(name)
    if len(names) != len(set(names)):
        raise ValueError("duplicate inventory rows")
    print("\n".join(names))
except (ValueError, UnicodeError):
    sys.exit(1)
' <<< "$dbs") || return 1
  mapfile -t rows <<< "$dbs"
  for db in "${rows[@]}"; do
    case "$db" in
      information_schema|mysql|performance_schema|sys) continue ;;
    esac
    # `dolt` is a user database, not a reserved system schema.
    any_user=1
    n=$(python3 "$MCP_CLIENT" --host 127.0.0.1 --flavor dolt --port "$port" \
          --database "$db" --branch main query \
          "SELECT COUNT(*) AS dirty FROM dolt_status" 2>/dev/null) || return 1
    [ "$n" = $'dirty\n---\n0' ] || return 1
  done

  [ "$any_user" = "1" ] || return 1   # no user DB seen -> unexpected -> not clean
  return 0
}

main() {
  # Cron runs with a minimal PATH; make the verification toolchain reachable.
  export PATH="$HOME/go/bin:/usr/local/bin:$PATH"

  IDLE_MIN="${IDLE_MIN:-90}"
  [[ "$IDLE_MIN" =~ ^[1-9][0-9]{0,5}$ ]] || { echo "invalid IDLE_MIN" >&2; return 2; }
  DRY=0
  if [ "$#" -gt 1 ] || { [ "$#" -eq 1 ] && [ "$1" != --dry-run ]; }; then
    echo "usage: dolt-idle-reaper.sh [--dry-run]" >&2
    return 2
  fi
  [ "${1:-}" = "--dry-run" ] && DRY=1

  # The dolt-mcp client used to read each server's working set. Defaults to the
  # copy sitting beside this script (self-contained); override with
  # BEADS_DOLT_MCP_CLIENT.
  SELF_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
  MCP_CLIENT="${BEADS_DOLT_MCP_CLIENT:-$SELF_DIR/dolt-mcp-client.py}"

  LOGDIR="$HOME/.local/state/dolt-reaper"
  mkdir -p "$LOGDIR"
  LOCK="$LOGDIR/.lock"
  exec 9>"$LOCK"
  flock -n 9 || { echo "[$(date '+%F %T')] another reaper run is active; skip."; exit 0; }

  now=$(date +%s)
  idle_secs=$(( IDLE_MIN * 60 ))
  reaped=0 kept=0 skipped=0 total=0

  echo "[$(date '+%F %T')] reaper start (IDLE_MIN=$IDLE_MIN, dry-run=$DRY)"
  for pid in $(pgrep -f 'dolt sql-server' 2>/dev/null); do
    total=$((total+1))
    cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null) || { continue; }
    ws=$(bd_workspace "$pid" "$cwd") || { kept=$((kept+1)); continue; }
    short=$(echo "$ws" | sed "s#$HOME/##")
    act=$(latest_activity "$ws")
    observed_act=$act
    if [ "$act" -eq 0 ]; then
      # No activity files found — fall back to the process start time via /proc
      # (Linux-only path; on other platforms mtime returns 0 and we use now).
      act=$(mtime "/proc/$pid"); [ "$act" -eq 0 ] && act=$now
    fi
    age_min=$(( (now - act) / 60 ))
    if [ "$(( now - act ))" -lt "$idle_secs" ]; then
      kept=$((kept+1))
      continue
    fi

    # Require an owned endpoint before connecting, then recheck identity and
    # activity after querying. Keep the process if anything changed meanwhile.
    identity=$(server_identity "$pid") || identity=''
    port="${identity##* }"
    if [ -n "$identity" ] && working_set_clean "$port"; then
      current_identity=$(server_identity "$pid") || current_identity=''
      current_act=$(latest_activity "$ws")
      if [ "$identity" != "$current_identity" ] || [ "$current_act" != "$observed_act" ]; then
        kept=$((kept+1))
        continue
      fi
      if [ "$DRY" -eq 1 ]; then
        echo "  WOULD REAP  pid=$pid port=${port:-?} idle=${age_min}m clean  $short"
      else
        kill -TERM "$pid" 2>/dev/null \
          && echo "  reaped      pid=$pid port=${port:-?} idle=${age_min}m clean  $short" \
          || echo "  reap-failed pid=$pid  $short"
      fi
      reaped=$((reaped+1))
    else
      echo "  SKIP-DIRTY  pid=$pid port=${port:-?} idle=${age_min}m  $short — uncommitted/undeterminable working set; NOT reaping"
      skipped=$((skipped+1))
    fi
  done
  echo "[$(date '+%F %T')] reaper done — $total servers, $reaped $([ $DRY -eq 1 ] && echo would-reap || echo reaped), $skipped skipped-dirty, $kept kept (active, changed, or unowned). bd respawns clean reaps on next use."

}

# Sourcing defines functions only, allowing hermetic tests of the real loop.
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
