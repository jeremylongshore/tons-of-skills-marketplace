#!/bin/bash
# Existing scan CLI: one implementation owns native JSON/status normalization.
# Exit 0: completed/no known findings; 1: findings/review; 2: incomplete/usage.
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${DEPENDENCY_CHECK_PYTHON:-python3}" "$script_dir/vulnerability_report_parser.py" --scan "$@"
