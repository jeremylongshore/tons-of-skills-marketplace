---
name: box-cloud-filesystem
description: |
  Manage Box files with the official Box CLI using reviewed, receipt-backed
  reads, uploads, version updates, and sharing. Use when a user asks to search,
  download, upload, update, organize, share, or synchronize Box content,
  and trigger with "upload to Box", "search Box", "share this Box file", or
  "review my Box sync queue."
allowed-tools: "Read,Write,Edit,Glob,Grep,Bash(box:*)"
argument-hint: "[search|download|upload|update|share|sync] [target]"
version: "2.0.0"
author: "Jeremy Longshore <jeremy@intentsolutions.io>"
license: "MIT"
compatibility: "Explicit operations require Node.js 18+, Box CLI 4.x, Box authentication, and network access. Claude Code workspace queue hooks additionally require Bash and jq. Other Agent Skills hosts can use explicit Box CLI mode."
tags: [box, cloud-storage, filesystem, sync, collaboration, document-management]
model: inherit
effort: medium
---

# Box Cloud Filesystem

## Overview

Operate Box through numeric file and folder IDs, narrow sharing defaults, and
verified receipts. The plugin's Write/Edit hook only queues local workspace
changes for review and never uploads automatically; see the
[reviewed sync pattern](references/sync-pattern.md) for the complete flow.

## Prerequisites

```bash
box version
box users:get me --json
```

- Install the current supported Box CLI 4.x through an operator-approved Node
  package workflow; do not install packages automatically.
- Use `box login` for interactive OAuth. JWT and CCG require a Box Platform App,
  appropriate scopes, secure configuration, and enterprise admin authorization.
- Never request or pass access tokens through chat or the CLI `--token` flag.
- The bundled workspace scripts require Bash and `jq`.

## Workflow

1. Classify the request as discover, read, create, update, expose, synchronize,
   or destructive.
2. Verify the active Box identity with `box users:get me --json` and report the
   account or enterprise without exposing credentials.
3. Discover the target by listing or searching. Use `Read`, `Glob`, and `Grep`
   only for the local files the user placed in scope.
4. Resolve every remote target to a numeric Box ID. Names are not unique.
5. Preview the operation:
   - uploads: local path, size, parent folder ID, and collision result;
   - updates: file ID, local path, and remote `content_modified_at`;
   - sharing: target ID, access level, download/edit flags, and expiry;
   - deletion or bulk moves: every target and recoverability.
6. Execute only the operation the user authorized. Ask before public/open links,
   deletes, bulk reorganizations, overwriting remote changes, or widening app
   access. Use `Write` or `Edit` only for requested local artifacts.
7. Re-read the affected Box item and return the receipt contract below.

## Trust zones

| Zone | Examples | Boundary |
|---|---|---|
| Read | search, list, metadata, download | Stay within the requested account/folder scope |
| Create | upload, create folder | Verify parent ID and name collision |
| Update | version upload, move, copy | Verify file ID and remote modification time |
| Expose | shared link, collaborator access | Confirm audience and access settings |
| Destructive | delete, bulk move | Explicit request plus target summary |

Never use `--yes` to suppress a Box CLI confirmation for expose or destructive
operations.

## Current command surface

```bash
box folders:items FOLDER_ID --json --fields name,id,type,content_modified_at
box search "query" --type file --json
box files:get FILE_ID --json --fields name,size,content_modified_at,shared_link
box files:download FILE_ID --destination LOCAL_PATH
box files:upload LOCAL_PATH --parent-id FOLDER_ID --json
box files:versions:upload FILE_ID LOCAL_PATH --json
box files:share FILE_ID --access collaborators --json
```

Use `box COMMAND --help` as command truth. The
[operations guide](references/operations-guide.md) covers moves, folders,
sharing, and recovery.

## Reviewed workspace queue

Initialize only when the user explicitly selects a Box folder and local path:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/box-init-workspace.sh FOLDER_ID /tmp/box-workspace
```

Initialization performs a Box read, downloads the folder, and stores a
permission-restricted local config. Subsequent Write/Edit hooks add eligible
relative paths to `.box-sync-pending`; hidden files and credential-like names are
excluded. The Stop hook reports the queue and performs no upload.

Before syncing, list each remote item again, compare modification timestamps,
show create/update/conflict groups, and obtain approval. Upload changed known
files with `files:versions:upload`; upload genuinely new files with
`files:upload`. Never infer a remote deletion from a missing local file.

## Output

Return:

- Box account context and target folder ID;
- operation and local/remote target;
- created or updated file/folder ID;
- sharing access, expiry, and URL when applicable;
- preflight comparison and any conflict;
- command exit result plus post-operation metadata;
- queued/skipped paths and the reason.

## Error Handling

- **401/expired auth:** run `box login`; never ask for a token in chat.
- **403:** report the missing scope or collaboration/admin boundary; do not widen
  access automatically.
- **404:** verify identity and ID by re-listing the parent.
- **409/name collision:** choose a version upload or an explicitly distinct name.
- **429:** honor retry guidance and reduce/batch read operations; do not loop
  indefinitely.
- **Remote changed since download:** stop and ask whether to keep remote, local,
  or both.
- **Partial bulk failure:** re-list the target, report confirmed successes, and
  retry only unresolved items after approval.
- **Hook queue failure:** preserve local work; report that no Box upload occurred.

## Examples

Update an existing file without creating a duplicate:

```bash
box files:get FILE_ID --json --fields name,content_modified_at
box files:versions:upload FILE_ID approved-report.md --json
box files:get FILE_ID --json --fields name,version_number,content_modified_at
```

Create a collaborators-only link after confirming the audience:

```bash
box files:share FILE_ID --access collaborators --json
```

## Resources

- [Box CLI operations and recovery](references/operations-guide.md)
- [Reviewed workspace synchronization](references/sync-pattern.md)
- [Box CLI source and generated command docs](https://github.com/box/boxcli)
- [Box security model](https://developer.box.com/guides/security/)
