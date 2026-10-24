## Reforge Mode Workflow

Triggered by `/skill-creator --reforge <plugin-name>`. Targets an existing forge-generated plugin (must have `.forge/research.md`) and regenerates against the current API surface. Required when an API adds/removes endpoints, changes auth, or restructures responses — without reforge the plugin's `references/api-surface.md` rots over months.

**Bumps the plugin version** (`patch` for endpoint adds, `minor` for new compound commands, `major` for breaking surface changes — auto-detected from the diff between old and new `api-surface.md`).

### Reforge Gate 0: Locate the existing forge

```bash
PLUGIN_DIR=$(find plugins -type d -name "$1" | head -1)
[ -f "$PLUGIN_DIR/.forge/research.md" ] || { echo "Not a forge-generated plugin: $1"; exit 1; }
[ -f "$PLUGIN_DIR/skills/$1/references/api-surface.md" ] || { echo "Missing api-surface.md — corrupt forge artifacts"; exit 1; }
```

If `.forge/research.md` doesn't exist, the plugin wasn't produced by forge — abort. Suggest re-forging from scratch via `/skill-creator --forge <api>` if the user wants to convert hand-authored to forge-managed.

### Reforge Gate 1: Recover NOI

Read `references/noi.md`. **Do not re-prompt the user for NOI** unless the user passed `--reset-noi`. The original NOI is the design anchor; reforging rewrites the implementation against the live API but keeps the design discipline.

If `--reset-noi` is passed, run Forge Gate 1 from scratch (hard NOI block; user must rename the secret identity).

### Reforge Gate 2: Re-enumerate API surface

Repeat Forge Gate 3 (API surface research) against the current API. Write the new surface to `.forge/research.md` (append, dated section). Diff against the existing `references/api-surface.md` — capture:

- **Added endpoints**: new since last forge (skill gains capability)
- **Removed endpoints**: gone (skill code that called them needs deprecation/removal)
- **Schema changes**: same endpoint, different response shape (skill code needs adaptation)
- **Auth changes**: e.g. v1 → v2 token format, OAuth scope additions

Write the diff to `.forge/proofs.md` under a new `## Reforge YYYY-MM-DD` section.

### Reforge Gate 3: Recompute domain archetype + compound commands

Re-run Forge Gates 4 and 5 with the updated surface. New endpoints may unlock new compound commands; removed endpoints may break existing ones. Record changes in `references/compound-commands.md` and note removed/deprecated commands in `.forge/proofs.md`.

### Reforge Gate 4: Regenerate skill + agents

Re-run Forge Gate 6 to write fresh:

- `skills/<api-name>/SKILL.md` (preserves frontmatter version per the bump rule above; updates body sections that cover the new/changed/removed endpoints)
- `agents/<api>-expert.md` (refreshes against the new surface)
- `agents/<api>-analyst.md` (refreshes compound-command implementations)
- `skills/<api-name>/scripts/sync-cache.sh` (only if the schema delta requires SQL changes — usually unchanged)

Preserve any **engineer-authored sections** in SKILL.md marked with `<!-- ENGINEER-EDIT-START -->...<!-- ENGINEER-EDIT-END -->` comments — reforge does not overwrite human refinements.

### Reforge Gate 5: Static validation and requested behavioral evidence

Apply Forge Gate 7 from `forge-workflow.md`: Grade A plus static checks, with behavioral execution only under explicit authorization. Preserve missing/failed behavioral evidence and repository promotion requirements. Append the new report to `.forge/proofs.md`.

### Reforge Gate 6: Output

1. Bump plugin version per the auto-detected scope (patch/minor/major).
2. Open a PR titled `chore(reforge): <plugin-name> against API surface YYYY-MM-DD`.
3. PR description includes:
   - Surface diff summary (added/removed/changed endpoints)
   - New compound commands (if any) + removed compound commands (if any)
   - Validation report
   - Link to `.forge/proofs.md` reforge section
4. Tag the commit with the new version: `<plugin-name>@<X.Y.Z>`.

### Drift detection trigger

Schedule a weekly cron (separate from `/skill-creator`) that:

1. Walks forge-generated entries in the canonical catalog (`generated: true`), resolving their declared source paths and confirming `.forge/research.md`; the runtime `plugin.json` does not own this classification
2. For each, fetches the live API surface and diffs against `references/api-surface.md`
3. Opens a GitHub issue when drift is detected, tagged `forge-drift`, with the diff in the body
4. Maintainer takes the issue, runs `/skill-creator --reforge <plugin-name>` to resolve

The cron itself is separate work (Phase 5C continued — bead). This skill defines the manual reforge entry point.
