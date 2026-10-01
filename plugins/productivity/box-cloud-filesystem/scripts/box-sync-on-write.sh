#!/usr/bin/env bash
# PostToolUse hook: queue changed local files for a reviewed Box sync.
# This hook never calls Box and never performs a remote write.

set -euo pipefail
umask 077

input_json="$(cat)"
file_path="$(jq -r '.tool_input.file_path // .tool_input.file // empty' \
  <<<"$input_json" 2>/dev/null)"
[ -n "$file_path" ] || exit 0

config_root="${XDG_CONFIG_HOME:-${HOME}/.config}/box-cloud-filesystem"
config_path="${config_root}/config.json"
[ -f "$config_path" ] || exit 0

queue_changes="$(jq -r '.queue_changes // false' "$config_path" 2>/dev/null)"
[ "$queue_changes" = "true" ] || exit 0

workspace_path="$(jq -r '.workspace // empty' "$config_path" 2>/dev/null)"
[ -n "$workspace_path" ] && [ -d "$workspace_path" ] || exit 0

canonical_workspace="$(cd "$workspace_path" && pwd -P)"
[ -e "$file_path" ] || exit 0
[ ! -L "$file_path" ] || exit 0
file_directory="$(cd "$(dirname "$file_path")" && pwd -P)"
canonical_file="${file_directory}/$(basename "$file_path")"

case "$canonical_file" in
  "$canonical_workspace"/*) ;;
  *) exit 0 ;;
esac

[ -f "$canonical_file" ] || exit 0
relative_path="${canonical_file#"$canonical_workspace"/}"
case "$relative_path" in
  *$'\n'*|*$'\r'*) exit 0 ;;
esac
normalized_path="$(printf '%s' "$relative_path" | tr '[:upper:]' '[:lower:]')"

case "/$normalized_path" in
  */.*|*credential*|*secret*|*token*|*private-key*|*.pem|*.p12|*.pfx)
    exit 0
    ;;
esac

pending_path="${canonical_workspace}/.box-sync-pending"
if ! grep -Fqx -- "$relative_path" "$pending_path" 2>/dev/null; then
  printf '%s\n' "$relative_path" >> "$pending_path"
fi
