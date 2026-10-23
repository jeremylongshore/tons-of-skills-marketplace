---
title: 'ccpi CLI Command Reference'
description: 'Complete command reference for the ccpi CLI tool, including syntax, options, examples, and common workflows for installing, managing, and validating Claude Code plugins.'
section: 'reference'
order: 5
keywords:
  - "ccpi"
  - "CLI"
  - "command line"
  - "install"
  - "search"
  - "validate"
  - "update"
  - "remove"
  - "marketplace"
officialLinks:
  - title: 'ccpi on npm'
    url: 'https://www.npmjs.com/package/@intentsolutionsio/ccpi'
  - title: 'Claude Code Plugins Documentation'
    url: 'https://code.claude.com/docs/en/plugins'
relatedDocs:
  - 'getting-started/installation'
  - 'getting-started/cli-reference'
  - 'reference/plugin-json-schema'
---

## Scope and version

`ccpi` is the Tons of Skills companion CLI, published as `@intentsolutionsio/ccpi`; `tons` is an additional binary name. This reference describes the registered command surface in the repository's 3.x CLI. It is not the native `claude plugin` command reference.

```bash
npm install -g @intentsolutionsio/ccpi
ccpi --version
ccpi --help
```

Node.js 22+ is required by the standalone package. Repository commands require Node 22.12+. A global install or `npx` invocation executes package code; choose the package version and trust boundary deliberately.

## Guided marketplace workflows

### install

```bash
ccpi install git-commit-smart
ccpi install --pack devops
ccpi install --category security
ccpi install --all
```

The optional positional argument is a marketplace plugin name, not a GitHub URL or local directory. The implementation looks up catalog entries and prints commands to run in Claude Code; it does not clone and register arbitrary repositories. `--path` is not supported.

Registered options are `-y, --yes`, `--global`, `--all`, `--skills`, `--pack <name>`, and `--category <name>`. The legacy `--skills` option reports a coming-soon message; it is separate from the implemented portable `skills install` command below. Consult help for the current built-in pack roster instead of assuming every category is also a pack.

The guided plugin output may use obsolete native scope flags. For an actual native install, use the current documented syntax:

```bash
claude plugin install git-commit-smart@claude-code-plugins-plus --scope project
```

Native scopes are `user`, `project`, and `local`, with user as the default. See [installation](/docs/getting-started/installation) for scope and reload behavior.

### list

```bash
ccpi list
ccpi list --all
```

`-a, --all` selects available catalog entries rather than only installed plugins. An installation record is not proof that every server or hook launches successfully.

### upgrade

```bash
ccpi upgrade --check
ccpi upgrade --all
ccpi upgrade --plugin git-commit-smart
```

The implementation compares catalog and installation versions and prints guided upgrade instructions. It does not apply every update automatically. Native plugin management has its own update behavior; review [the native guide](https://code.claude.com/docs/en/discover-plugins) and installed help before acting. Do not infer preservation of all plugin data from a printed companion message.

### marketplace

```bash
ccpi marketplace
ccpi marketplace --verify
ccpi marketplace-add
ccpi marketplace-remove
```

`marketplace-add` and `marketplace-remove` print native setup/removal guidance. `marketplace --verify` checks the expected local marketplace path and catalog-file presence; it is not a full catalog parse, authentication test, or arbitrary private-source configuration facility. There is no `ccpi marketplace add <repo>` subcommand.

### doctor

```bash
ccpi doctor
ccpi doctor --json
```

Doctor inspects its implemented environment, directory, registry, and catalog checks. It does not authenticate a user's account or prove runtime tool enforcement. `--fix` allows supported repairs such as directory creation and catalog refresh; review the intended paths before allowing those writes.

### search and analytics

```bash
ccpi search terraform
ccpi analytics
```

Both commands are currently placeholders that print coming-soon messages. They do not implement fuzzy ranking, usage analysis, or the fictional result tables found in older versions of this page. Use [Explore](/explore) and [Skills](/skills) for the shipped website search.

## Authoring validation

```bash
ccpi validate ./my-plugin
ccpi validate ./my-plugin --skills
ccpi validate ./my-plugin --frontmatter
ccpi validate ./my-plugin --strict
```

The companion delegates to its local skill and Markdown frontmatter checkers and prints a notice pointing to the authoritative Python validator. Do not treat it as the native manifest validator, a complete SPDX/URL/README gate, or a security scanner. Its strict behavior is implementation-specific; it is not a substitute for the repository's marketplace tier or required CI checks.

`--json` is registered, but some companion validation paths print a notice before JSON. Consumers must not assume stdout is a single JSON document without verifying the installed version's output contract.

From the repository root, use explicit tiers for authoritative checks:

```bash
# Upstream format floor, not marketplace acceptance
python3 scripts/validate-skills-schema.py --standard --verbose plugins/category/my-plugin/

# Repository marketplace contract and rubric
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/category/my-plugin/

# Agents have a separate strict repository contract
python3 scripts/validate-skills-schema.py --agents-only --verbose plugins/category/my-plugin/

# Native manifest loading rules
claude plugin validate ./plugins/category/my-plugin
```

The category and plugin path here are placeholders: substitute an existing author-owned directory. Native, companion, Python, and kernel checks have different scopes. The Python marketplace validator remains authoritative; kernel shadow checks do not silently replace it. [STANDARDS.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/STANDARDS.md) names the owners.

For CI or a shell script, preserve failure status:

```bash
set -euo pipefail
python3 scripts/validate-skills-schema.py --marketplace --verbose plugins/category/my-plugin/
```

Do not append `|| echo "Validation failed"` and then treat the script's zero exit as validation success.

## Portable skills

Portable skills are a different artifact and installation route from native plugins:

```bash
ccpi skills list-harnesses --json
ccpi skills install ./path/to/one-skill --harness claude-code --scope project --dry-run --json
ccpi skills doctor --harness claude-code --scope project --source-repo . --skill skill-name --json
```

The source path, harness ID, and skill name are illustrative. Select an advertised harness and review dry-run output before an actual write. Byte identity, structural validity, and retained behavioral quality evidence are different properties; an install receipt alone does not establish the last one.

## Unsupported commands and configuration

There are no `ccpi update`, `ccpi remove`, or `ccpi info` commands in this version. Use the native plugin manager for native updates and uninstall operations.

The current CLI source does not implement `CCPI_CATALOG_URL`, `CCPI_PLUGIN_DIR`, `CCPI_CACHE_TTL`, or the platform-specific `catalog-cache.json` paths described in older versions of this page. Setting those variables does not configure an invented cache or private registry. Use supported help and reviewed source/harness options instead of deleting guessed files.

## Exit status and automation

Check each command's actual exit status and output. Commander usage failures and companion failures commonly exit 1; do not rely on a special exit-2 validation code. A zero exit from a guided command means it printed guidance, not that the printed operation ran.

`./scripts/quick-test.sh` is a repository sanity workflow that installs dependencies and runs selected checks; it is not a complete simulation of hosted CI. Required contexts and their owners are recorded in [CLAUDE.md](https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/CLAUDE.md) and the linked CI routing documents.
