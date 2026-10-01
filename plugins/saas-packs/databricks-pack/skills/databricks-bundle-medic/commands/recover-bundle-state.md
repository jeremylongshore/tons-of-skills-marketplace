---
name: recover-bundle-state
description: Recover a Databricks Asset Bundle deploy stuck on an EOF tfstate read error
aliases: [fix-bundle-eof, bundle-state-recovery]
---

# /recover-bundle-state

Recovers a Databricks Asset Bundle stuck on the D5 state-read bug
(databricks/cli#4986, "unexpected EOF reading terraform.tfstate") using the
`databricks-bundle-medic` skill.

## Usage

```text
/recover-bundle-state [--target <bundle-target>]
```

## What it does

1. Looks for the known-good terraform state backup the `bundle-deploy-guard`
   PreToolUse hook caches under `.databricks/bundle/**/.medic-backups/`.
2. Validates the current state — if it does not parse as JSON, confirms this is the
   #4986 EOF signature.
3. Recommends the recovery: restore the latest known-good backup, then redeploy with
   `DATABRICKS_BUNDLE_ENGINE=direct` (the direct engine never reads the state file, so
   the EOF class cannot recur).
4. Points at `references/bundle-engine-tradeoffs.md` for the engine-switch tradeoffs and
   the preview-status caveat.

Advisory — it never mutates state without showing you the plan first.
