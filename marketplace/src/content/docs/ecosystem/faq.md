---
title: 'Claude Code Plugins FAQ'
description: 'Frequently asked questions about Claude Code plugins, the Tons of Skills marketplace, skills, agents, MCP servers, installation, troubleshooting, and publishing. Clear answers with links to detailed docs.'
section: 'ecosystem'
order: 4
keywords:
  - "Claude Code FAQ"
  - "plugin FAQ"
  - "skills FAQ"
  - "Claude Code troubleshooting"
  - "plugin installation help"
  - "SKILL.md help"
  - "ccpi FAQ"
  - "Claude Code marketplace FAQ"
officialLinks:
  - title: 'Claude Code Overview'
    url: 'https://code.claude.com/docs/en/overview'
  - title: 'Claude Code Skills'
    url: 'https://code.claude.com/docs/en/skills'
  - title: 'Claude Code Plugins'
    url: 'https://code.claude.com/docs/en/plugins'
  - title: 'Claude Code Best Practices'
    url: 'https://code.claude.com/docs/en/best-practices'
relatedDocs:
  - 'getting-started/installation'
  - 'ecosystem/marketplace-overview'
  - 'ecosystem/official-anthropic-docs'
  - 'ecosystem/community-resources'
---

## What does the marketplace provide?

Tons of Skills provides a curated catalog, searchable documentation, and plugin and skill discovery. Use the current [Explore](/explore) and [Skills](/skills) pages for their generated public counts. The editable catalog, public plugin index, and discovered skills have different denominators, so old totals should not be treated as current receipts.

The canonical repository is [jeremylongshore/tons-of-skills-marketplace](https://github.com/jeremylongshore/tons-of-skills-marketplace). This catalog complements Anthropic's official marketplaces; it is not a claim that Claude Code has no other registry or catalog.

## How do I install a plugin?

After adding the marketplace, native installation uses an explicit scope:

```bash
claude plugin marketplace add jeremylongshore/tons-of-skills-marketplace
claude plugin install api-test-automation@claude-code-plugins-plus --scope project
```

`user`, `project`, and `local` have distinct sharing boundaries. Inspect the installation summary and follow reload or next-session instructions. The `ccpi install` helper currently prints legacy scope guidance; that output is not the authority for current native flags. See [your first plugin](/docs/getting-started/first-plugin/) for the bounded walkthrough.

## Can I install a downloaded directory manually?

For development, explicitly load a reviewed plugin with `claude --plugin-dir /absolute/path/to/plugin`. Copying files into a cache directory does not itself register or enable them. Downloaded Cowork archives and portable skill directories have their own installation and runtime prerequisites; they are not interchangeable with all native plugin components.

## How are skills discovered and invoked?

Claude discovers skill metadata and loads the full body on invocation. It does not place every installed `SKILL.md` body permanently into context. Users can invoke a user-invocable plugin skill by its namespaced slash name; `argument-hint` is helpful but not required.

`user-invocable: false` blocks explicit user invocation. Claude can still invoke the skill unless `disable-model-invocation: true` restricts that route too. Legacy command files remain supported; new reusable instructions generally belong in skills.

## What is the difference between a skill and an agent?

A skill supplies instructions and optional resources. An agent is a delegated worker with a separate context and configured tools. Agents support both a `tools` allowlist and a `disallowedTools` denylist. A skill's `allowed-tools` preapproves tools for the invocation; it is not an exclusive capability sandbox.

Both skills and agents support model-dependent `effort`. Fields such as `capabilities`, `expertise_level`, and `activation_priority` are not native agent runtime controls and are rejected by this repository's agent validator. See [agents](/docs/concepts/agents/) for the local contract.

## Are instruction plugins safe because they are Markdown?

Markdown can contain dynamic command preprocessing and instructions to execute tools. Plugins can include hooks, scripts, and MCP configuration. There is no supported fixed percentage of instruction-only plugins that establishes safety. Review actual source, dependencies, permissions, provenance, and data handling before enabling a plugin.

## What metadata is required?

Native formats are intentionally permissive. This marketplace requires eight skill fields: `name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, and `tags`. Missing fields are errors at marketplace tier. Plugin manifests and agents have separate contracts; do not apply the skill field set to every artifact.

## What do grades and badges prove?

The static skill rubric weights progressive disclosure (30), ease of use (25), utility (20), specification compliance (15), and writing style (10), with modifiers. Letter grades are A ≥90, B ≥80, C ≥70, D ≥60, and F below 60. Stub classification is separate from the grade.

The current plugin verification projection averages skill scores and assigns gold at 90, silver at 75, and bronze at 60. Those badge thresholds are not the same as the letter-grade bands. A static grade or badge is not proof of a successful provider call, secure execution, clean-checkout behavioral evidence, or production readiness. Consult the current grading and gate authorities for those distinct questions.

## How do updates and removal work?

Use current native plugin update and uninstall operations from the [plugin management documentation](https://code.claude.com/docs/en/discover-plugins). Do not assume removal is necessary for an update or that uninstall/reinstall preserves all plugin-specific configuration and persistent data.

The tracked helper command is `ccpi upgrade`, not `ccpi update`. It currently prints guidance rather than performing a complete upgrade transaction. There are no delivered `ccpi info` or `ccpi remove` commands. Check the [CLI reference](/docs/getting-started/cli-reference/) before scripting the helper.

## Does CLI search work?

`ccpi search <query>` currently prints a coming-soon message; it does not search catalog fields. Use the website search. `ccpi analytics` and `ccpi install --skills` are also placeholders. The separate `ccpi skills` subtree is delivered for portable skill inspection and bounded installation; it must not be confused with the placeholder flag.

## Which runtime and site versions apply?

Repository commands follow the current Node/runtime contract in `AGENTS.md` and `000-docs/814-DR-STND-node-runtime-contract.md`. Independently consumable packages may have separate documented floors. The site uses Astro as pinned in `marketplace/package.json`; an old “Astro 5” description is not the current dependency authority.

## Where should I report a problem?

Use the canonical repository's contribution and issue guidance. Include exact versions, source revision, a minimal reproduction, and redacted diagnostics. A validation warning is not automatically a defect or a waiver; its rule, actual source location, and acceptance criteria need assessment.
