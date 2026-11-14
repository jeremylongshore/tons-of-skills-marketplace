---
name: hyperflow-agents-skill
description: Inspect or update validated Hyperflow primary, general, and lightweight model-role preferences at global, project, or session scope.
version: 8.0.0
---
# Hyperflow Agents Skill

Show the effective model role, provider adapter, scope, and configuration revision. Resolve identifiers from actual provider configuration/catalog and authentication state. Never invent model IDs, write provider credentials, or modify a shared delegate fleet file.

The host running this chat remains the coordinator. Hyperflow settings choose delegates per role; they never switch the outer host. Use only capabilities exposed by the active host. Resolve `<plugin-root>` to this installed plugin's directory and invoke `node <plugin-root>/runtime/cli.mjs`.

```text
node <plugin-root>/runtime/cli.mjs agents-config
node <plugin-root>/runtime/cli.mjs agents-config set <role> <harness> <provider/model> [global|project|session RUN_ID]
```

Available roles:

- `primary`: planning, integration decisions, and correctness review in an independent lane. Default delegate: native Codex `gpt-6.1-sol`.
- `general`: difficult implementation, security work, the final consolidated security review, and security fixes. Default: `zai/glm-5.3`. Implementation, security review, and security repair each use separate lanes.
- `lightweight`: routine implementation, which is the default for new tasks. Default: `zai/glm-5.3-flash`. Most clearly scoped implementation should stay here; mark difficult work complex and security work security.

Models are configurable delegate preferences. The workflow policy fixes the roles for each task and review phase. Availability requires catalog validation and a successful dispatch. A profile selects a delegate harness and model only when that adapter is available; this does not certify the delegate or the active host. Validate overlays in global, project, then session order. An active run freezes its approved bindings for all task and review lanes; session edits apply only after recompilation and restart. Effort is assigned per task during planning as `low`, `medium`, or `high`, shown in the workflow and phase records, and validated against that delegate's actual support; unsupported levels are rejected rather than silently substituted. Never silently change the surrounding chat model. Changing delegates requires a checkpoint and explicit restart with a structured handoff.

Show supported effort or variant from the actual adapter. Preserve valid independent work and completed results when a role changes. Report unavailable configuration or authentication as a blocker; never silently fall back.

The pinned upstream delegate relay is optional. Install it only with the explicit `setup-delegates` command. It is not fetched during startup, planning, or ordinary installation.

## Writing

Before writing plans, questions, status updates, review findings or delivery summaries, apply the shared [unslop writing rules](../hyperflow-plan/references/unslop.md). Preserve technical meaning and evidence.
