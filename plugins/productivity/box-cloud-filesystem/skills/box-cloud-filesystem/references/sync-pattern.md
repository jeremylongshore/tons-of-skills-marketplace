# Reviewed Workspace Sync Pattern

The local workspace is a review surface, not a bidirectional mount. Initialization
downloads a selected Box folder and captures top-level item metadata. Hooks queue
eligible local changes but never write to Box.

## 1. Establish identity and scope

```bash
box users:get me --json
box folders:items FOLDER_ID --json --fields name,id,type,content_modified_at
```

Confirm the account, Box folder ID, and local destination. Initialization is an
external read plus local writes, so run it only after the user selects both
targets. The destination must be new or empty:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/box-init-workspace.sh FOLDER_ID /tmp/box-workspace
```

The script writes a mode-0600 config under the host configuration directory. It
sets `queue_changes: true` and `auto_upload: false`.

## 2. Work locally

Write/Edit hooks append eligible relative paths to `.box-sync-pending`. They skip
hidden files and names that look like credentials, secrets, tokens, or private
keys. A Stop hook reports the queue without clearing it.

This is intentionally not an auto-sync system. A local edit never proves that a
remote overwrite is safe.

## 3. Build a sync plan

For every queued path:

1. Confirm the local file still exists and remains inside the canonical
   workspace path.
2. Match it against the manifest by exact relative path or verified file ID.
3. Re-read remote metadata with `box files:get FILE_ID --json`.
4. Compare `content_modified_at` with the manifest snapshot.
5. Classify the path:

| Local state | Remote state | Proposed action |
|---|---|---|
| Changed known file | Unchanged since snapshot | Version upload |
| New file | No name collision in verified folder | New upload |
| Missing local file | Existing remote file | No remote action |
| Changed known file | Remote also changed | Conflict; ask user |
| Credential-like or hidden path | Any | Skip |
| Nested path without verified remote parent mapping | Any | Skip and resolve parent |

Show the full create/update/conflict/skip plan. Obtain approval before applying
it, including the exact Box folder and file IDs.

## 4. Apply only approved actions

```bash
box files:versions:upload FILE_ID LOCAL_PATH --json
box files:upload LOCAL_PATH --parent-id FOLDER_ID --json
```

Never use a name match as identity for an update. Never translate local deletion
into remote deletion. Never add `--yes` to suppress confirmation for exposure or
destructive actions.

## 5. Verify and settle the queue

Re-read each affected item and record its returned ID, version, and modification
time. Remove a queue entry only after the corresponding Box receipt is verified.
Leave conflicts and failed items in the queue.

Report a table:

| Local path | Action | Box ID | Verification |
|---|---|---|---|
| `approved-report.md` | version upload | `12345` | current metadata matched |
| `new-summary.md` | new upload | `67890` | parent ID and name matched |
| `budget.xlsx` | skipped | `24680` | remote changed after snapshot |

## Recovery

- Stale manifest: re-list the Box folder and rebuild a proposed mapping; do not
  overwrite the manifest until IDs are verified.
- Reused workspace path: re-run initialization for the intended folder and
  confirm the config points to the canonical path.
- Partial upload: re-list remote items, retain unresolved queue entries, and do
  not repeat successful uploads.
- Queue-only hook failure: local work is unaffected and no Box write occurred.
