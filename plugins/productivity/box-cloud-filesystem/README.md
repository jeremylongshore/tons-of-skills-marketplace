# Box Cloud Filesystem

Reviewed cloud-file workflows for AI agents using the official
[Box CLI](https://github.com/box/boxcli). Search, download, upload, create
versions, and share Box content with explicit target checks and receipts.

Version 2 changes the workspace hook to queue-only behavior: ordinary local
Write/Edit operations never upload to Box automatically.

## Install

### Agent Skills CLI

```bash
npx skills add jeremylongshore/box-cloud-filesystem --skill box-cloud-filesystem
```

### Claude Code plugin

```text
/plugin marketplace add jeremylongshore/box-cloud-filesystem
/plugin install box-cloud-filesystem@box-cloud-filesystem
```

The standalone marketplace catalog is bundled in this repository. Review plugin
hooks and scripts before installation.

## Prerequisites

- Node.js 18 or later.
- Current supported Box CLI 4.x (`npm install --global @box/cli`) installed only
  after operator review.
- Box authentication; interactive use normally starts with `box login`.
- Bash and `jq` for Claude Code workspace queue hooks.

Verify the active identity:

```bash
box version
box users:get me --json
```

JWT and Client Credentials Grant configurations require a Box Platform App,
appropriate scopes, secure configuration, and administrator authorization. Do
not put access tokens in prompts or command arguments.

## Explicit Box operations

```bash
box folders:items 0 --json
box search "quarterly report" --type file --json
box files:download FILE_ID --destination ./report.pdf
box files:upload ./report.md --parent-id FOLDER_ID --json
box files:versions:upload FILE_ID ./report.md --json
box files:share FILE_ID --access collaborators --json
```

Use numeric IDs for identity, inspect the parent before uploads, compare remote
modification time before version updates, and confirm audience before sharing.
Deletion, open/public links, overwriting conflicts, and bulk operations require
an explicit target summary and user approval.

## Reviewed workspace queue

Initialize a selected Box folder and local workspace:

```bash
./scripts/box-init-workspace.sh FOLDER_ID /tmp/box-workspace
```

Initialization downloads the folder and enables queue-only hooks. Later
Write/Edit events add eligible paths to `.box-sync-pending`; hidden and
credential-like paths are skipped. The Stop hook reports pending files and never
uploads them. Initialization refuses a non-empty local destination to avoid
overwriting existing work.

Before a Box sync, re-read every remote item, classify create/update/conflict/skip
actions, show the plan, and obtain approval. Apply approved changes with explicit
Box CLI commands and clear only entries with verified receipts.

## Included components

| Component | Purpose |
|---|---|
| `skills/box-cloud-filesystem/SKILL.md` | Main Agent Skill and safety contract |
| `hooks/hooks.json` | Queue changed workspace paths and report pending review |
| `scripts/box-init-workspace.sh` | Download an approved Box folder and create local config |
| `scripts/box-sync-on-write.sh` | Local queue hook; no Box API calls |
| `scripts/box-sync-summary.sh` | Report pending files; no Box API calls |

## Security model

- No automatic upload from a Write/Edit hook.
- No automatic Box deletion.
- No access-token arguments or credential values in output.
- Collaborators-only links are the narrow example; public/open links require
  explicit confirmation.
- Workspace paths are canonicalized and restricted to the configured root.
- Local configuration is written with mode 0600.

## Links

- [Box CLI](https://github.com/box/boxcli)
- [Box Developer documentation](https://developer.box.com/)
- [Box security model](https://developer.box.com/guides/security/)
- [Tons of Skills](https://tonsofskills.com)

## License

MIT
