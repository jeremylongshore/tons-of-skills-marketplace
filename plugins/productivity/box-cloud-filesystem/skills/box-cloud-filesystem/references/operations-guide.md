# Box CLI Operations Guide

Detailed command reference for Box CLI operations, organized by trust zone.

## Discovering What Exists

List the root folder:

```bash
box folders:items 0 --json
```

Each item has `id`, `type` (file or folder), `name`, `size`. Narrow the output:

```bash
box folders:items FOLDER_ID --json --fields name,id,type,size,modified_at
```

Search across the entire account (full-text and filename):

```bash
box search "quarterly report" --json
box search "*.csv" --type file --json
box search "project-alpha" --type folder --json
```

Get metadata on a specific file:

```bash
box files:get FILE_ID --json --fields name,size,content_modified_at,shared_link,path_collection
```

The `path_collection` field shows the full folder path from root — use it to orient yourself in deep hierarchies.

## Reading Files

Download a single file:

```bash
box files:download FILE_ID --destination /tmp/box-workspace/
```

Download an entire folder:

```bash
box folders:download FOLDER_ID --destination /tmp/box-workspace/ --create-path
```

After downloading, read and process with standard tools. The local copy is the working copy.

## Writing Files

Before uploading, verify the parent folder ID is correct:

```bash
box folders:items FOLDER_ID --json --fields name,id,type
```

Upload a new file:

```bash
box files:upload /path/to/file.txt --parent-id FOLDER_ID
```

Capture the returned file `id` and report it to the user.

If a file with the same name exists, determine the correct action:

- **Updating an existing file?** Use version upload:
  ```bash
  box files:versions:upload FILE_ID /path/to/updated-file.txt
  ```
- **Genuinely new file with a name collision?** Use `--name` to differentiate:
  ```bash
  box files:upload /path/to/file.txt --parent-id FOLDER_ID --name "file-revised.txt"
  ```

Never blindly re-upload when a version update is the right call.

## Creating Folder Structure

```bash
box folders:create 0 "project-alpha"
# Returns new folder ID — use it as parent for sub-folders
box folders:create NEW_FOLDER_ID "src"
box folders:create NEW_FOLDER_ID "docs"
box folders:create NEW_FOLDER_ID "data"
```

## Moving and Organizing

These operations change file locations. Confirm the destination folder ID is correct before executing.

```bash
box files:move FILE_ID DESTINATION_FOLDER_ID
box files:copy FILE_ID DESTINATION_FOLDER_ID
box folders:move FOLDER_ID DESTINATION_FOLDER_ID
box files:delete FILE_ID       # Moves to trash; retention depends on enterprise policy
box folders:delete FOLDER_ID   # Recursive — confirm with user first
```

## Sharing

Sharing is an **exposure operation** — it changes who can see a file. Treat it as higher-risk than writing.

**Access levels (narrowest to broadest):**

| Level | Who can access | When to use | Default? |
|-------|---------------|-------------|----------|
| `collaborators` | Only users explicitly invited | Most tasks — internal handoff, team work | **Narrow example** |
| `company` | Anyone in the same Box enterprise | Org-wide docs, internal wiki links | When user says "share with the team/org" |
| `open` | Anyone with the link, no login required | **Only when user explicitly says "public" or "open"** | **Never default** |

Create a shared link:

```bash
box files:share FILE_ID --access collaborators
box folders:share FOLDER_ID --access collaborators
```

If the user says "share this file" without specifying access, ask who should
receive it rather than inferring an audience. If they say "make it public" or
"open link," confirm first: "This will make the file accessible to anyone with
the link. Proceed?"

Always report: the access level used, the URL generated, and who can access it.

Remove sharing:

```bash
box files:unshare FILE_ID
```

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `Not Found` (404) | Wrong file/folder ID, or item deleted/trashed | Verify the ID with `box search` or re-list the parent folder |
| `Conflict` (409) on upload | File with same name exists in target folder | Use `box files:versions:upload FILE_ID` to update, or `--name` to upload as distinct file |
| `Forbidden` (403) | Auth token lacks permission | Re-run `box login` or check JWT scopes; ensure collaborator access to target folder |
| `Rate Limited` (429) | Too many API calls in succession | Honor returned retry guidance; reduce repeated calls and use supported bulk input where appropriate |
| `Auth expired` | Interactive or application authentication is no longer valid | Run `box login` again for interactive use; application auth requires an approved Box Platform configuration |
| `File too large` | Box enforces per-file size limits by plan | Split large files or check Box plan limits |
| `box: command not found` | CLI not installed or not in PATH | Review the official Box CLI installation instructions and obtain approval before installing packages |
| Empty search results | Search may not show the expected item | Use `box folders:items` to inspect the verified parent directly before retrying |
| `Name collision` | Multiple files with same name in different folders | Always use file ID, never filename, to identify targets |
| `Partial upload failure` | Network interruption during multi-file upload | Re-list target folder to see what succeeded; retry only failed files by ID |
| `Forbidden share` | Cannot create shared link at requested level | Enterprise admin may restrict sharing; fall back to `collaborators` or check admin settings |
| `Local/remote divergence` | File changed on Box since last download | Re-download remote version, diff against local, ask user which to keep |
| `Ambiguous sync state` | Manifest stale, files renamed/moved outside session | Re-list Box folder, rebuild manifest, compare before pushing |

**Recovery principles:**

- Always report what failed and what succeeded — never silently skip.
- If a partial failure occurs during bulk operations, stop and report rather than continuing blindly.
- If state is ambiguous (stale manifest, unexpected files), rebuild state from Box before acting.
