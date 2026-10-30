---
title: 'How to Build a Claude Code Plugin'
description: 'Complete guide to building a Claude Code plugin from scratch. Covers plugin.json configuration, commands, skills, agents, directory structure, validation, and testing with full code examples.'
section: 'guides'
order: 2
keywords:
  - 'plugin'
  - 'plugin.json'
  - 'commands'
  - 'agents'
  - 'skills'
  - 'Claude Code plugin'
  - 'plugin development'
  - 'build plugin'
officialLinks:
  - title: 'Anthropic Claude Code Documentation'
    url: 'https://code.claude.com/docs/en/'
  - title: 'Anthropic Plugins Reference'
    url: 'https://code.claude.com/docs/en/plugins'
relatedDocs:
  - 'concepts/plugins'
  - 'reference/plugin-json-schema'
  - 'guides/publish-to-marketplace'
---

## Choose the artifact

An instruction plugin groups skills, commands, and agents around a useful workflow. Markdown-only instruction plugins do not need a compiled runtime. Hooks, MCP servers, LSP servers, or other runtime components have their own executable and dependency contracts; “every plugin is plain text” is not a general rule.

Use a plugin for a coherent capability, not a collection of unrelated promises. Review existing [marketplace entries](/explore) and determine whether a portable standalone skill is enough before adding native plugin components.

## Create the layout

```bash
mkdir -p my-plugin/.claude-plugin
mkdir -p my-plugin/skills/configuration-review
mkdir -p my-plugin/agents
```

A minimal authored plugin can contain:

```text
my-plugin/
  .claude-plugin/plugin.json
  README.md
  LICENSE
  skills/configuration-review/SKILL.md
```

Optional `commands/`, `agents/`, hooks, and runtime files belong at their documented plugin locations. The repository's [templates](https://github.com/jeremylongshore/tons-of-skills-marketplace/tree/main/templates) are starting points; validate the generated artifact against the current contract rather than assuming an old template certifies it.

## Write the manifest

This complete metadata envelope is illustrative; replace identity, license, and URLs with the actual project's information:

```json
{
  "name": "example-review",
  "version": "1.0.0",
  "description": "Review selected configuration files and return evidence-linked observations.",
  "author": { "name": "Example Maintainer" },
  "homepage": "https://example.com/example-review",
  "repository": "https://github.com/example/example-review",
  "license": "MIT",
  "keywords": ["configuration", "review"],
  "commands": []
}
```

The author is an object. Homepage and `commands` are required by the marketplace kernel envelope, even though native Claude Code is more permissive. The native manifest supports many properties beyond this example; unknown-property warnings, strict failures, and wrong-type errors have different meanings. See [the manifest reference](/docs/reference/plugin-json-schema) and [native manifest documentation](https://code.claude.com/docs/en/plugins-reference).

## Add a complete skill

Use the complete `configuration-review` example in [Write a skill](/docs/guides/write-a-skill). Include the eight marketplace fields and substantive prerequisites, instructions, output, error handling, and examples. Link real supporting files with relative Markdown links.

A file called `reference.md` does not become useful merely because it exists. Include the actual constraints, current primary sources, and reviewed cases needed for the task.

## Optional commands

Legacy command files live under `commands/`; native skills are preferred for new work where they serve the same purpose. This is a command-file example, not a marketplace skill envelope:

```markdown
---
name: review-config
description: Review the explicitly selected configuration and return a bounded report.
argument-hint: '<existing-file>'
---

Read the user's selected project file and cite observed issues with exact lines.
Treat `$ARGUMENTS` as untrusted input, not shell code. Stop when the path is
missing, ambiguous, outside the selected project, or requires unrelated secrets.
Do not edit files or claim live service verification.
```

If you ship `commands/review-config.md`, declare its actual path as appropriate in the manifest and validate it with the current command contract. The native invocation is namespaced, such as `/example-review:review-config`, not a promise that `/review-config` is globally unique.

## Optional agents

Use [Create an agent](/docs/guides/create-an-agent) for a complete plugin-agent example. Agents support a `tools` allowlist as well as `disallowedTools`; skills' `allowed-tools` pre-approves tools and is not an exclusive allowlist. Do not add banned `capabilities`, `expertise_level`, or `activation_priority` fields to an agent.

A worker that can use Bash or an external tool may change state even when `Write` and `Edit` are denied. Validate the actual tool boundary, not only the prose's claim to be read-only.

## Write the README

Document the actual outcome, component names, supported runtime, dependencies, installation route, examples, failure behavior, and license. Clearly label sketches and untested deployment examples. Do not describe a static rubric score as production or security certification.

For development, load a reviewed local directory:

```bash
claude --plugin-dir ./my-plugin
```

For a plugin published through a marketplace, users add that marketplace and install its registered name. There is no `claude /plugin add owner/repo` installation syntax in this workflow.

## Validate each layer

From the repository root, with the actual plugin path:

```bash
claude plugin validate ./my-plugin
python3 scripts/validate-skills-schema.py --standard --verbose ./my-plugin/
python3 scripts/validate-skills-schema.py --marketplace --verbose ./my-plugin/
python3 scripts/validate-skills-schema.py --agents-only --verbose ./my-plugin/
```

These checks have different scopes. Use the explicit standard flag when demonstrating the upstream floor; marketplace mode enforces the repository's eight-field contract. Agents have their own strict contract. The absent historical `validate-all-plugins.sh` is not a supported command.

Run meaningful local checks for scripts, dependencies, and runtime components you actually ship. Verify successful use, denied or malformed input, missing prerequisites, failure propagation, and cleanup. A schema pass does not prove secrets are absent or dangerous behavior impossible.

## Catalog and generated output

For an approved repository-owned plugin, add its actual `source` entry to `.claude-plugin/marketplace.extended.json` and use the canonical producers. Pure external mirrors follow upstream-first registration and source-specific sync; do not hand-edit them.

```bash
pnpm run sync-marketplace
```

Skill-content changes can require canonical verification and additional projections. `./scripts/quick-test.sh` is a sanity workflow, not a guaranteed 30-second simulation of every hosted gate. The current rubric bands are A90, B80, C70, and D60, with F below60; neither a grade nor a code example automatically grants featured placement or publication approval.

Follow [STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md) and the [current contribution guide](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/.github/CONTRIBUTING.md), then [submit the plugin](/docs/guides/publish-to-marketplace) with scoped evidence.
