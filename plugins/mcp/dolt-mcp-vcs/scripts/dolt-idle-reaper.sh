#!/usr/bin/env bash
# dolt-idle-reaper.sh — gracefully stop idle bd-managed `dolt sql-server`
# processes so they don't accumulate (the "18 sprawled servers" problem).
#
# Provably non-destructive: a server is reaped ONLY when it is both (a) idle past
# the threshold AND (b) holding a CLEAN working set (nothing uncommitted). bd
# auto-restarts a workspace's dolt server on the next bd command, so stopping a
# clean idle one loses nothing — worst case is a ~2s respawn latency. Data lives
# in Dolt (durable) + the .beads JSONL.
#
# Why the clean-working-set gate: SIGTERM only flushes uncommitted writes when bd
# runs the server with `--dolt-auto-commit batch` (flushBatchCommitOnShutdown).
# In server mode the auto-commit default is `off`, where SIGTERM does NOT flush —
# so a server holding uncommitted working-set changes could lose them. We refuse
# to reap any server whose working set is dirty OR whose status we cannot
# determine (missing query toolchain, unreachable server, query error) — fail
# safe, never reap blind.
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
#   github.com/dolthub/dolt-mcp/mcp/cmd/dolt-mcp-server@latest), and
#   scripts/dolt-mcp-client.py beside this script.
#
# Cron (every 30 min):
#   3,33 * * * * /path/to/dolt-idle-reaper.sh >> ~/.local/state/dolt-reaper/reap.log 2>&1
set -uo pipefail

# Cron runs with a minimal PATH; make the verification toolchain reachable.
export PATH="$HOME/go/bin:/usr/local/bin:$PATH"

IDLE_MIN="${IDLE_MIN:-90}"
DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

# The dolt-mcp client used to read each server's working set. Defaults to the
# copy sitting beside this script (self-contained); override with
# BEADS_DOLT_MCP_CLIENT.
SELF_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
MCP_CLIENT="${BEADS_DOLT_MCP_CLIENT:-$SELF_DIR/dolt-mcp-client.py}"

LOGDIR="$HOME/.local/state/dolt-reaper"
mkdir -p "$LOGDIR"
LOCK="$LOGDIR/.lock"
exec 9>"$LOCK"
flock -n 9 || { echo "[$(date '+%F %T')] another reaper run is active; skip."; exit 0; }

now=$(date +%s)
idle_secs=$(( IDLE_MIN * 60 ))
reaped=0 kept=0 skipped=0 total=0

# Resolve a server process's workspace root from its cwd (cwd is either the
# workspace root or its .beads/dolt data-dir).
ws_root() {
  local cwd="$1"
  case "$cwd" in
    */.beads/dolt) echo "${cwd%/.beads/dolt}" ;;
    */.beads)      echo "${cwd%/.beads}" ;;
    *)             echo "$cwd" ;;
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

# Extract the server's listen port from its cmdline (bd uses `-P <port>`; also
# tolerate `--port`/`=`-joined forms).
server_port() {
  tr '\0' ' ' < "/proc/$1/cmdline" 2>/dev/null \
    | grep -oE '(-P|--port)[ =]*[0-9]+' | grep -oE '[0-9]+' | head -1
}

# working_set_clean <port> — return 0 ONLY if every user database on the server
# has an empty working set. Return 1 (skip) on ANY uncommitted change, query
# error, unreachable server, or missing toolchain. Conservative by design.
working_set_clean() {
  local port="$1" dbs db n any_user=0
  [ -n "$port" ] || return 1
  command -v python3 >/dev/null 2>&1 || return 1
  command -v dolt-mcp-server >/dev/null 2>&1 || return 1
  [ -f "$MCP_CLIENT" ] || return 1

  dbs=$(python3 "$MCP_CLIENT" --port "$port" list_databases 2>/dev/null) || return 1
  [ -n "$dbs" ] || return 1

  while IFS= read -r db; do
    case "$db" in
      ''|Database|'---'|information_schema|mysql|performance_schema|sys|dolt) continue ;;
    esac
    any_user=1
    n=$(python3 "$MCP_CLIENT" --port "$port" --database "$db" --branch main \
          query "SELECT COUNT(*) AS dirty FROM dolt_status" 2>/dev/null \
        | grep -oE '^[0-9]+' | head -1)
    [ -n "$n" ] || return 1      # couldn't determine -> not clean
    [ "$n" = "0" ] || return 1   # uncommitted changes -> not clean
  done <<EOF
$dbs
EOF

  [ "$any_user" = "1" ] || return 1   # no user DB seen -> unexpected -> not clean
  return 0
}

echo "[$(date '+%F %T')] reaper start (IDLE_MIN=$IDLE_MIN, dry-run=$DRY)"
for pid in $(pgrep -f 'dolt sql-server' 2>/dev/null); do
  total=$((total+1))
  cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null) || { continue; }
  ws=$(ws_root "$cwd")
  short=$(echo "$ws" | sed "s#$HOME/##")
  act=$(latest_activity "$ws")
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

  # Idle past threshold — only reap if the working set is provably clean.
  port=$(server_port "$pid")
  if working_set_clean "$port"; then
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
echo "[$(date '+%F %T')] reaper done — $total servers, $reaped $([ $DRY -eq 1 ] && echo would-reap || echo reaped), $skipped skipped-dirty, $kept kept (active within ${IDLE_MIN}m). bd respawns clean reaps on next use."
