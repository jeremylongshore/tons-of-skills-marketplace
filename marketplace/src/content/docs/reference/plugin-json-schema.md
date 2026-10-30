---
title: 'plugin.json Schema Reference'
description: 'Reference for native plugin.json metadata and the stricter marketplace publication envelope, including field definitions, validation rules, and CI enforcement details.'
section: 'reference'
order: 2
keywords:
  - 'plugin.json'
  - 'schema'
  - 'manifest'
  - 'plugin structure'
  - 'validation'
  - 'CI'
  - 'metadata'
officialLinks:
  - title: 'Claude Code Plugins Documentation'
    url: 'https://code.claude.com/docs/en/plugins'
  - title: 'Claude Code Plugin Structure'
    url: 'https://code.claude.com/docs/en/plugins-reference#standard-layout'
relatedDocs:
  - 'concepts/plugins'
  - 'guides/build-a-plugin'
  - 'reference/plugin-categories'
---

## Two contracts, not one field allowlist

A plugin manifest belongs at `.claude-plugin/plugin.json` under the plugin root. Native Claude Code supports more than eight properties, including component paths and runtime configuration. Its current manifest documentation makes `name` the required field when a manifest is supplied; some native plugin layouts can omit the manifest entirely.

That permissive runtime floor is not this marketplace's publication contract. The pinned kernel's `authoring/v1` marketplace envelope requires `name`, `version`, `description`, `author`, `homepage`, `license`, `keywords`, and `commands`. Additional supported fields remain possible. The repository's authoritative validator and advisory kernel lanes have distinct roles; see [STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md).

Use the current [native manifest reference](https://code.claude.com/docs/en/plugins-reference), the pinned kernel schema, and the repository validator instead of treating this page as a second schema authority.

## Marketplace manifest example

The following is a complete metadata envelope for an illustrative instruction plugin with no command files. URLs and identity are examples to replace with the author's actual public project information:

```json
{
  "name": "example-review",
  "version": "1.0.0",
  "description": "Review a selected configuration and produce a bounded, evidence-linked report.",
  "author": { "name": "Example Maintainer" },
  "homepage": "https://example.com/example-review",
  "repository": "https://github.com/example/example-review",
  "license": "MIT",
  "keywords": ["configuration", "review"],
  "commands": []
}
```

| Field         | Marketplace use                                                                       |
| ------------- | ------------------------------------------------------------------------------------- |
| `name`        | Kebab-case identity, unique within its marketplace; use a coherent directory identity |
| `version`     | Display-version surface; follow the repository's governed bump workflow               |
| `description` | Factual summary of the plugin's actual behavior                                       |
| `author`      | Object with a `name`; optional `email` and `url` belong inside it                     |
| `homepage`    | Valid user-facing project or documentation URL, required by the marketplace envelope  |
| `license`     | Actual distribution license; do not infer one from a missing field                    |
| `keywords`    | Relevant discovery terms as an array                                                  |
| `commands`    | Explicit command paths, or an empty array when none are supplied                      |
| `repository`  | Optional source URL; it does not replace source registration or provenance review     |

For a command file, use a path such as `./commands/review.md` in `commands` and keep the file inside the plugin. Path forms and default discovery rules differ by component; consult the native reference rather than guessing from one example.

## Other native fields

Claude Code also documents fields such as `displayName`, `skills`, `agents`, `hooks`, `mcpServers`, `lspServers`, `dependencies`, `userConfig`, `metadata`, and other supported extension surfaces. Whether a field is usable depends on its exact documented shape and the runtime version.

Do not add npm's `scripts` or `main` to the plugin manifest to create a runtime build. Put Node package metadata in `package.json`, and declare the actual server command in MCP configuration.

An unrecognized field produces a warning in the repository's default manifest check; `--strict` promotes that warning to an error. Missing native `name` and wrong field types remain errors. A native validator's warning about optional metadata is different from a marketplace envelope failure.

## Ownership and generated files

The plugin manifest describes the artifact. The editable `.claude-plugin/marketplace.extended.json` describes the marketplace listing and its `source` path. `marketplace.json`, catalog projections, generated package manifests, and the README catalog section are derived; use their canonical generators.

Pure external mirrors are upstream-owned. Submit fixes upstream and use the reviewed source-specific sync path; do not patch their manifests locally to pass a gate.

## Version namespaces

Do not assume npm package and plugin display versions must be identical. The approved repository formula moves display surfaces by MINOR and the npm surface by PATCH for routine updates. Follow [blueprint 727 V1](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/000-docs/727-AT-ARCH-master-modernization-blueprint.md) and the current auto-bump implementation. Do not manually promote an npm minor or skip automation to make strings match.

## Validate each relevant layer

From the repository root, replacing the illustrative path:

```bash
claude plugin validate ./plugins/category/example-review
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/category/example-review/
```

The companion `ccpi validate` is a useful local check, but does not implement every native manifest or marketplace kernel requirement. A JSON parse alone proves neither runtime support nor safe behavior.

## MCP and other runtime plugins

An MCP plugin uses the same manifest concept, plus an actual server configuration and runtime artifacts. The protocol is language-independent. When the command is `node`, a JavaScript argument need not be directly executable; a directly executed script needs its own interpreter/shebang and permissions. In both cases the clean installation must contain the entry point and required dependencies.

Use an absolute plugin-relative entry in the server argument:

```json
{
  "mcpServers": {
    "example-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/dist/index.js"]
    }
  }
}
```

This is a native stdio configuration excerpt, not proof of marketplace prescreen compliance or a successful server launch. Do not add unsupported runtime fields merely to satisfy a tracking overlay; review the relevant owner contract separately.

## Common failures

| Observation                      | Action                                                                                           |
| -------------------------------- | ------------------------------------------------------------------------------------------------ |
| Author is a string               | Use an object with the actual author's `name`                                                    |
| Homepage or `commands` absent    | Complete the marketplace envelope; do not confuse it with the native minimum                     |
| Unknown field warning            | Check spelling and current field support before changing strictness                              |
| Component not found              | Check the exact path, containment, installed bytes, and component discovery rules                |
| Plugin installs but server fails | Inspect actual runtime dependencies, absolute entry, environment, protocol lifecycle, and stderr |
| Catalog and manifest disagree    | Fix the authored owner surface and regenerate; do not hand-edit derived files                    |
