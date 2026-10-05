#!/usr/bin/env bash
# Install the generated skill redirect block into the existing Caddy fragment.
# Run as root on the tonsofskills.com VPS after the matching static release is live.
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
CHECK_ONLY=0
if [[ ${1:-} == "--check" ]]; then
  CHECK_ONLY=1
  shift
fi
# With no SOURCE argument (the deploy path), install every generated fragment the repository
# owns, in a fixed order: the Snowflake v2 skill tombstones, then the retired-path map.
DEFAULT_SOURCES=("$SCRIPT_DIR/snowflake-v2-redirects.caddy" "$SCRIPT_DIR/retired-path-redirects.caddy")
if [[ -n ${1:-} ]]; then
  SOURCES=("$1")
else
  SOURCES=("${DEFAULT_SOURCES[@]}")
fi
TARGET=${2:-/etc/caddy/tonsofskills-redirects.caddy}
MAIN_CONFIG=${3:-/etc/caddy/Caddyfile}
BEGIN_MARKER='# BEGIN tons-of-skills generated skill redirects'
END_MARKER='# END tons-of-skills generated skill redirects'

if [[ $CHECK_ONLY -eq 0 && ${EUID} -ne 0 ]]; then
  echo "install-skill-redirects: must run as root" >&2
  exit 77
fi
for path in "${SOURCES[@]}" "$TARGET" "$MAIN_CONFIG"; do
  [[ -f "$path" ]] || { echo "install-skill-redirects: missing file: $path" >&2; exit 66; }
done

TMP_DIR=$(mktemp -d)
BACKUP="${TARGET}.bak.$(date -u +%Y%m%dT%H%M%SZ)"
INSTALLED=0

cleanup() {
  rm -rf -- "$TMP_DIR"
}
rollback_on_error() {
  local status=$?
  set +e
  if [[ $INSTALLED -eq 1 && -f "$BACKUP" ]]; then
    cp --preserve=mode,ownership,timestamps -- "$BACKUP" "$TARGET"
    # Reload only a configuration that validates. If the restored file does not validate,
    # leave the running Caddy process on its last good in-memory config and fail loudly.
    if sudo -n -u caddy caddy validate --config "$MAIN_CONFIG" >/dev/null 2>&1; then
      systemctl reload caddy
      echo "install-skill-redirects: rolled back to $BACKUP" >&2
    else
      echo "install-skill-redirects: CRITICAL: restored $BACKUP does not validate; NOT reloading Caddy." >&2
      echo "install-skill-redirects: the running process keeps its last good config; fix $TARGET by hand before any reload." >&2
      cleanup
      exit 70
    fi
  fi
  cleanup
  exit "$status"
}
trap cleanup EXIT
trap rollback_on_error ERR

SOURCE="$TMP_DIR/generated.caddy"
cat -- "${SOURCES[@]}" > "$SOURCE"

python3 - "$TARGET" "$TMP_DIR/base.caddy" "$BEGIN_MARKER" "$END_MARKER" <<'PY'
import sys
from pathlib import Path

source, output, begin, end = sys.argv[1:]
lines = Path(source).read_text(encoding="utf-8").splitlines()
kept = []
inside = False
seen_begin = seen_end = 0
for line in lines:
    if line == begin:
        if inside:
            raise SystemExit("nested generated redirect marker")
        inside = True
        seen_begin += 1
        continue
    if line == end:
        if not inside:
            raise SystemExit("unmatched generated redirect end marker")
        inside = False
        seen_end += 1
        continue
    if not inside:
        kept.append(line)
if inside or seen_begin != seen_end or seen_begin > 1:
    raise SystemExit("malformed generated redirect marker pair")
Path(output).write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
PY

MATCHER_ID='@(redir[0-9]+|retired[0-9a-f]+)'
grep -oE "$MATCHER_ID" "$TMP_DIR/base.caddy" | sort -u > "$TMP_DIR/existing.ids" || true
grep -oE "$MATCHER_ID" "$SOURCE" | sort -u > "$TMP_DIR/new.ids" || true
DUPLICATES=$(grep -oE "^$MATCHER_ID" "$SOURCE" | sort | uniq -d)
if [[ -n "$DUPLICATES" ]]; then
  echo "install-skill-redirects: duplicate generated matcher(s): $DUPLICATES" >&2
  exit 65
fi
COLLISIONS=$(comm -12 "$TMP_DIR/existing.ids" "$TMP_DIR/new.ids")
if [[ -n "$COLLISIONS" ]]; then
  echo "install-skill-redirects: matcher collision(s): $COLLISIONS" >&2
  exit 65
fi

{
  cat "$TMP_DIR/base.caddy"
  echo "$BEGIN_MARKER"
  cat "$SOURCE"
  echo "$END_MARKER"
} > "$TMP_DIR/candidate.caddy"

python3 - "$MAIN_CONFIG" "$TARGET" "$TMP_DIR/candidate.caddy" "$TMP_DIR/Caddyfile" <<'PY'
import sys
from pathlib import Path

main, target, candidate, output = sys.argv[1:]
text = Path(main).read_text(encoding="utf-8")
needle = f"import {target}"
if text.count(needle) != 1:
    raise SystemExit(f"expected exactly one {needle!r} in main Caddyfile")
Path(output).write_text(text.replace(needle, f"import {candidate}"), encoding="utf-8")
PY

# Parse the complete configuration against the candidate import before touching live state.
caddy adapt --config "$TMP_DIR/Caddyfile" >/dev/null
if [[ $CHECK_ONLY -eq 1 ]]; then
  echo "install-skill-redirects: candidate valid; sha256=$(sha256sum "$TMP_DIR/candidate.caddy" | awk '{print $1}')"
  exit 0
fi
cp --preserve=mode,ownership,timestamps -- "$TARGET" "$BACKUP"
install -o root -g root -m 0644 "$TMP_DIR/candidate.caddy" "$TMP_DIR/target.next"
mv -f -- "$TMP_DIR/target.next" "$TARGET"
INSTALLED=1

# Validate as the service user so Caddy can open its configured log writers.
sudo -n -u caddy caddy validate --config "$MAIN_CONFIG" >/dev/null
systemctl reload caddy
INSTALLED=0
trap - ERR

echo "install-skill-redirects: installed=$(sha256sum "$TARGET" | awk '{print $1}') backup=$BACKUP"
