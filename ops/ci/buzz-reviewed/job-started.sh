#!/usr/bin/env bash
# Python runs isolated from job-controlled module paths and user site packages.
set -euo pipefail
exec /usr/bin/python3 -I /usr/local/lib/ccpi-reviewed/guard.py
