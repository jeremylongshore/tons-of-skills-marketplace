#!/usr/bin/env bash
# Stop hook: report local changes awaiting an explicit reviewed Box sync.

set -euo pipefail

config_root="${XDG_CONFIG_HOME:-${HOME}/.config}/box-cloud-filesystem"
config_path="${config_root}/config.json"
[ -f "$config_path" ] || exit 0

workspace_path="$(jq -r '.workspace // empty' "$config_path" 2>/dev/null)"
[ -n "$workspace_path" ] && [ -d "$workspace_path" ] || exit 0

canonical_workspace="$(cd "$workspace_path" && pwd -P)"
pending_path="${canonical_workspace}/.box-sync-pending"
[ -s "$pending_path" ] || exit 0

pending_count="$(wc -l < "$pending_path" | tr -d ' ')"
echo "Box sync review required: ${pending_count} local file(s) are pending."
while IFS= read -r relative_path; do
  printf '  - %s\n' "$relative_path"
done < "$pending_path"
echo "No Box upload was performed. Review remote state and explicitly sync approved files."
