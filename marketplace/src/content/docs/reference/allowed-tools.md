---
title: 'Allowed Tools Reference'
description: 'Complete reference for all valid tools in the Claude Code plugin system, including tool descriptions, scoped Bash patterns, least-privilege principles, and recommended tool combinations for common skill types.'
section: 'reference'
order: 4
keywords:
  - "allowed-tools"
  - "tools"
  - "permissions"
  - "Bash"
  - "Read"
  - "Write"
  - "Edit"
  - "Glob"
  - "Grep"
  - "security"
  - "least privilege"
officialLinks:
  - title: 'Claude Code Skills Documentation'
    url: 'https://code.claude.com/docs/en/skills'
  - title: 'Claude Code Tool Use'
    url: 'https://code.claude.com/docs/en/overview'
relatedDocs:
  - 'concepts/skills'
  - 'guides/write-a-skill'
  - 'reference/skill-frontmatter'
---

## Pre-approval is not an exclusive tool list

A skill's `allowed-tools` grants pre-approval for the listed tools during the turn that invokes it. It does not remove unlisted tools: the user's permission settings still govern them. The grant clears on the next user message, even though the skill's instructions remain in context. Managed settings can further restrict which grants apply.

To remove tools while the skill is active, use the documented `disallowed-tools` field. Skills use kebab-case; agents use `disallowedTools` and also have a separate `tools` allowlist. Read the current [native skills reference](https://code.claude.com/docs/en/skills) and [subagent reference](https://code.claude.com/docs/en/sub-agents) for runtime semantics.

## Common tools

This table is illustrative, not an exhaustive runtime or validator registry:

| Tool                    | Typical use                                   | Boundary to review                                                                  |
| ----------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------- |
| `Read`, `Glob`, `Grep`  | Inspect selected files and locate evidence    | Reads can still expose secrets or private data                                      |
| `Write`, `Edit`         | Author or modify files                        | Review intended paths and preserve unrelated work                                   |
| `Bash`                  | Run commands                                  | Shell commands can write files, contact networks, or invoke other interpreters      |
| `WebFetch`, `WebSearch` | Fetch a known URL or search documentation     | A known URL need not require a search; avoid sending sensitive content              |
| `Agent`                 | Delegate a bounded task                       | Review the delegated tools, context, and ownership; `Task` is a compatibility alias |
| `Skill`                 | Invoke another skill                          | Review that skill's instructions and pre-approvals too                              |
| `AskUserQuestion`       | Obtain missing input                          | Do not use it as a substitute for an actual permission policy                       |
| `NotebookEdit`          | Modify notebook cells                         | Notebook code and outputs can contain sensitive data                                |
| `TodoWrite`             | Runtime task-list integration where available | Repository work tracking still follows this project's Beads requirements            |

Consult the installed runtime's tools and `scripts/validate-skills-schema.py` for recognized names. Tool names are case-sensitive. A name accepted by a static validator is not proof the runtime exposes it in every host.

## Scoped Bash pre-approval

```yaml
allowed-tools: Read, Glob, Grep, Bash(npm:*), Bash(git status:*)
```

This narrows which Bash calls are pre-approved; it does not create a sandbox or ban other shell commands. Other commands can still be permitted by the user's settings or a separate grant. Prefix patterns and shell parsing require care; do not describe a short prefix as a complete security boundary.

Do not use unscoped `Bash` merely because a guide includes shell snippets. Review the commands actually needed, their input and output paths, credentials, and possible network or destructive effects. Listing only read-oriented tools does not by itself establish a read-only process if other permissions remain available.

## Denying tools

This is a field fragment for a skill, not a complete marketplace skill:

```yaml
disallowed-tools: AskUserQuestion
```

This is an agent tuning fragment, not the full required agent envelope:

```yaml
tools: Read, Glob, Grep
disallowedTools: [Write, Edit, Bash]
```

A deny entry containing a Bash specifier in an agent can remove the whole Bash tool, not just that command. For command-level restrictions, use the actual documented permission policy or an independently tested guard; do not invent a partial denylist contract.

## Choose permissions from the workflow

| Workflow               | Candidate pre-approvals                  | Additional review                                                    |
| ---------------------- | ---------------------------------------- | -------------------------------------------------------------------- |
| Local evidence review  | `Read`, `Glob`, `Grep`                   | Selected paths, private data, and inherited permissions              |
| Code authoring         | Needed file tools                        | Exact files, overwrite behavior, and generated ownership             |
| Build or test          | Narrow command scopes                    | Scripts may install dependencies, spawn children, or use the network |
| Documentation research | `WebFetch` and, when needed, `WebSearch` | Source trust, outbound data, and current primary authority           |
| Orchestration          | `Agent` and/or `Skill` when needed       | Child context, scope, capabilities, and completion evidence          |

These are design starting points, not a certification ladder. Bash already permits network-capable programs when allowed; adding a web tool is not the only way network access becomes possible. `Edit` does not technically require a `Read` grant, although reading the actual file before changing it is sound authoring practice.

## Validate without overstating the result

From the repository root, substituting an actual authored plugin directory:

```bash
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/category/my-plugin/
```

The current validator can report malformed or unknown tool entries and advisory body-versus-declaration mismatches. Such warnings are not evidence that a tool ran, that omitted tools were blocked, or that provider authorization was verified. The eight-field marketplace contract and the runtime permission model are separate facts.

Use [the frontmatter reference](/docs/reference/skill-frontmatter) for complete examples and [STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md) for the canonical ownership and approval boundaries.
