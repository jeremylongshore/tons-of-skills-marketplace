#!/bin/bash
# Native PreToolUse JSON arrives on stdin; an explicit filename remains a CLI audit.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
    echo "Workflow validation requires Python 3; refusing unchecked operation." >&2
    exit 2
fi
# Convert unexpected interpreter failures to the native blocking status as well.
python3 "$SCRIPT_DIR/validate-workflow.py" "$@" || {
    status=$?
    if [[ $# -gt 0 ]]; then exit "$status"; fi
    exit 2
}
