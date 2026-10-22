#!/usr/bin/env bash
# Initialize an opt-in local workspace from one Box folder.
# Usage: box-init-workspace.sh <BOX_FOLDER_ID> [WORKSPACE_PATH]
# Remote reads happen here; later Write/Edit hooks only queue local changes.

set -euo pipefail

box_folder_id="${1:?Usage: box-init-workspace.sh <BOX_FOLDER_ID> [WORKSPACE_PATH]}"
workspace_path="${2:-/tmp/box-workspace}"
config_root="${XDG_CONFIG_HOME:-${HOME}/.config}/box-cloud-filesystem"
config_path="${config_root}/config.json"

if ! command -v box >/dev/null 2>&1; then
  echo "Error: Box CLI not found. Review installation at https://github.com/box/boxcli" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 1
fi

if ! [[ "$box_folder_id" =~ ^[0-9]+$ ]]; then
  echo "Error: Box folder ID must contain digits only." >&2
  exit 1
fi

if ! box users:get me --json >/dev/null; then
  echo "Error: Box CLI is not authenticated. Run 'box login' and retry." >&2
  exit 1
fi

if [ -e "$workspace_path" ] && [ ! -d "$workspace_path" ]; then
  echo "Error: Workspace target exists and is not a directory." >&2
  exit 1
fi

if [ -d "$workspace_path" ] &&
  [ -n "$(find "$workspace_path" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
  echo "Error: Workspace must be new or empty to avoid overwriting local files." >&2
  exit 1
fi

mkdir -p "$workspace_path" "$config_root"
workspace_path="$(cd "$workspace_path" && pwd -P)"

echo "Downloading Box folder ${box_folder_id} to ${workspace_path}..."
box folders:download "$box_folder_id" \
  --destination "$workspace_path" \
  --create-path

echo "Building top-level file manifest..."
box folders:items "$box_folder_id" \
  --json \
  --fields name,id,type,content_modified_at \
  > "${workspace_path}/.box-manifest.json"

temporary_config="$(mktemp "${config_root}/config.XXXXXX")"
jq -n \
  --arg workspace "$workspace_path" \
  --arg folder_id "$box_folder_id" \
  --arg initialized_at "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
  '{
    workspace: $workspace,
    box_folder_id: $folder_id,
    initialized_at: $initialized_at,
    queue_changes: true,
    auto_upload: false
  }' > "$temporary_config"
chmod 600 "$temporary_config"
mv "$temporary_config" "$config_path"

item_count="$(jq '[.entries[]? | select(.type == "file")] | length' \
  "${workspace_path}/.box-manifest.json")"

echo "Box workspace initialized:"
echo "  Local path: ${workspace_path}"
echo "  Box folder: ${box_folder_id}"
echo "  Top-level files: ${item_count}"
echo "  Write/Edit behavior: queue only; no automatic Box upload"
