#!/usr/bin/env bash
# Grep built artifacts for debugId. Absence means the running bytes were not injected.
# Cite both action-release sources; do not pick a winner URL.
# This script does not call the Sentry API. The Python twin imports sentry_readonly
# only to refuse --apply. Logic lives in grep_debug_id.py so the allowlisted
# python3 tool and this shell entrypoint share one implementation.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -lt 1 ]]; then
  echo "usage: $0 <built-file-or-dir>..." >&2
  exit 1
fi
exec python3 "$HERE/grep_debug_id.py" "$@"
