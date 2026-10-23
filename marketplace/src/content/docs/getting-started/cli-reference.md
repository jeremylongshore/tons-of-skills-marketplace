---
title: 'ccpi CLI Quick Reference'
description: 'The delivered ccpi command surface, portable skill commands, plugin guidance, placeholders, and current JSON and scope limitations.'
section: 'getting-started'
order: 4
keywords:
  - "ccpi CLI"
  - "ccpi commands"
  - "Claude Code CLI"
  - "plugin management CLI"
  - "ccpi install"
  - "ccpi validate"
  - "ccpi doctor"
officialLinks:
  - title: 'ccpi on npm'
    url: 'https://www.npmjs.com/package/@intentsolutionsio/ccpi'
  - title: 'Claude Code CLI Reference'
    url: 'https://code.claude.com/docs/en/cli-reference'
relatedDocs:
  - 'getting-started/installation'
  - 'reference/cli-commands'
---

## Overview

The `ccpi` helper and the native `claude` CLI are separate programs. Some `ccpi` commands inspect or install portable skill trees; others display plugin-management guidance. Several registered commands are still placeholders. This page describes the tracked implementation, not an assumed feature roadmap.

Install and version checks, after reviewing the package and its prerequisites:

```bash
npm install -g @intentsolutionsio/ccpi
ccpi --version
ccpi --help
```

Repository-level commands follow the runtime contract in `AGENTS.md`; independently consumable packages can have their own documented floor. Do not infer a package's supported runtime from an old website example.

## Delivered command surface

| Command                                       | Current behavior and boundary                                                            |
| --------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `ccpi install [plugin]`                       | Catalog lookup and installation guidance; not a general native transaction engine        |
| `ccpi upgrade`                                | Upgrade guidance; does not apply a complete plugin upgrade transaction                   |
| `ccpi list`                                   | Inspect installed plugins; `--all` requests available catalog entries                    |
| `ccpi doctor`                                 | Diagnostics; `--fix` can create directories and refresh catalogs                         |
| `ccpi marketplace`                            | Marketplace connection guidance; supports `--verify`                                     |
| `ccpi marketplace-add` / `marketplace-remove` | Marketplace management helpers                                                           |
| `ccpi validate [path]`                        | Legacy validation entry point with `--skills`, `--frontmatter`, `--strict`, and `--json` |
| `ccpi skills list-harnesses`                  | Read the shipped portable harness registry                                               |
| `ccpi skills doctor`                          | Diagnose installed portable skill receipt/source integrity                               |
| `ccpi skills install <source>`                | Bounded local portable skill installation with a receipt                                 |

There are no delivered `ccpi update`, `remove`, `info`, or `init` commands. `ccpi search <query>` currently prints a coming-soon message rather than searching names or descriptions. Use the website [Explore](/explore) and search interface. `ccpi analytics` and the `ccpi install --skills` flag are also placeholders; the delivered `ccpi skills` subtree is separate.

## Plugin guidance versus native installation

This is a real current catalog name:

```bash
ccpi install api-test-automation
```

The helper currently prints legacy native scope flags. Do not copy those flags as authoritative current Claude syntax. The native route is:

```bash
claude plugin marketplace add jeremylongshore/tons-of-skills-marketplace
claude plugin install api-test-automation@claude-code-plugins-plus --scope project
```

Native scopes are `user`, `project`, and `local`; see the [current platform reference](https://code.claude.com/docs/en/discover-plugins). Claude also has native update support. `ccpi upgrade` is not a substitute for that complete operation, and uninstall/reinstall is not a required universal update procedure.

`ccpi install` registers `--yes`, `--global`, `--all`, `--pack`, and `--category`. These describe the helper's own options, not current native flags. Built-in pack guidance can contain historical plugin names: check each member against the current catalog instead of assuming an advertised pack is a verified runnable set. Avoid broad `--all` installation merely to follow a tutorial.

## Portable skills

Inspect the registry before choosing a harness:

```bash
ccpi skills list-harnesses --json
ccpi skills doctor --harness claude-code --scope project --json
```

The shipped registry distinguishes verified-native, standard-compatible, native-extension, research-required, and unsupported concepts; not every classification implies a usable install target. Current public support is narrower than the full set of recorded harnesses. A standard-compatible row is not evidence that all Claude-specific behavior is supported.

The following writes only if a reviewed local source and supported destination pass validation. Start with the dry run:

```bash
ccpi skills install /absolute/path/to/review-diff --harness claude-code --scope project --dry-run --json
ccpi skills install /absolute/path/to/review-diff --harness claude-code --scope project --json
ccpi skills doctor --harness claude-code --scope project --source-repo /absolute/path/to/trusted/source-repository --skill review-diff --json
```

The source must be a skill directory containing `SKILL.md` (or that file's path). Review the destination and project working directory before removing `--dry-run`. Receipts and doctor checks address installed-tree/source integrity; they do not prove a quality grade, successful provider behavior, or native activation in every harness. Staged update, repair, rollback, and quality-evidence binding are not delivered by these commands.

## Validation and JSON limitations

Use the repository's canonical validator for repository skill checks:

```bash
python3 scripts/validate-skills-schema.py --standard /absolute/path/to/review-diff/SKILL.md
python3 scripts/validate-skills-schema.py --marketplace --verbose /absolute/path/to/review-diff/SKILL.md
```

The Python validator defaults to standard outside CI; CI auto-selects marketplace unless a tier is explicit. Marketplace mode requires all eight metadata fields. Choose the tier deliberately rather than relying on stale CLI help wording.

The legacy `ccpi validate` currently emits a deprecation banner **before** its result, including with `--json`. Redirecting its stdout is therefore not guaranteed to yield a single parseable JSON document. Its strict handling also differs by mode: frontmatter strict can promote warnings, while skill paths do not uniformly fail for every warning. Do not build a security gate around a claimed uniform strict/JSON behavior that the implementation does not provide.

The Python validator's existing `--fail-on-warn` is an explicit warning policy. Default warning diagnostics are distinct from errors. This documentation does not change either program's exit-code policy.

## Helper paths and catalog source

The current `detectClaudePaths` implementation uses these helper paths:

| Host           | CCPI configuration root         |
| -------------- | ------------------------------- |
| Linux or macOS | `~/.claude`                     |
| Windows        | `<home>/AppData/Roaming/Claude` |

The helper uses `plugins` and `marketplaces` below that root and recognizes a current-directory `.claude-plugin` directory for its project detection. It does not currently implement an XDG override. These are CCPI implementation facts, not a replacement for native Claude's configuration reference.

Its catalog source is the canonical repository's raw `.claude-plugin/marketplace.json`, not an assumed website `/catalog.json` endpoint. Source, cache, deployment, and installed state can differ.

## Diagnostics and safe scripting

`ccpi doctor --json` is useful for diagnostics; review output before sharing it. `ccpi doctor --fix` is a writing operation, not a read-only inspection. Keep credentials and private paths out of public bug reports.

Inspect `--help` for the installed version and record the exact command and source revision when reporting behavior. No command examples here certify that an installer, provider, or native server was executed successfully.
