---
name: code-formatter
description: 'Execute automatically formats and validates code files using Prettier
  and other formatting tools.

  Use when users mention "format my code", "fix formatting", "apply code style",

  "check formatting", "make code consistent", or "clean up code formatting".

  Handles JavaScript, TypeScript, JSON, CSS, Markdown, and many other file types.
  Trigger with relevant phrases based on skill purpose.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(cmd:*)
version: 2.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- example
- typescript
- code-formatter
compatibility: Designed for Claude Code
---
# Code Formatter

## Overview

Formats and validates code files using Prettier and related formatting tools. Supports JavaScript, TypeScript, JSON, CSS, Markdown, and many other file types.

## Prerequisites

- Node.js (v16+) and npm/npx installed
- Prettier available globally (`npm install -g prettier`) or locally in the project
- Write permissions for target files and configuration directories
- Supported file types present in the project (`.js`, `.jsx`, `.ts`, `.tsx`, `.json`, `.css`, `.md`)

## Instructions

1. Check whether Prettier is available by running `npx prettier --version`. If missing, install it locally with `npm install --save-dev prettier` or globally with `npm install -g prettier`.
2. Detect existing configuration by searching for `.prettierrc`, `.prettierrc.json`, `prettier.config.js`, or a `"prettier"` key in `package.json`. If no configuration exists, create a `.prettierrc` with sensible defaults (see `${CLAUDE_SKILL_DIR}/references/implementation.md`).
3. Run `npx prettier --check "**/*.{js,jsx,ts,tsx,json,css,md}" --ignore-path .prettierignore` to identify files that need formatting. Report the count and list of non-conforming files.
4. Apply formatting to identified files using `npx prettier --write` on the target paths. For single files, specify the exact path; for directories, use glob patterns.
5. Create or update `.prettierignore` to exclude generated outputs (`dist/`, `build/`, `*.min.js`, `*.min.css`), dependencies (`node_modules/`, `vendor/`), and lock files.
6. Optionally set up pre-commit enforcement by installing `husky` and `lint-staged`, then configuring `lint-staged` in `package.json` to run `prettier --write` on staged files matching supported extensions.
7. Run a final `npx prettier --check` to confirm all target files now conform to the configured style rules.

## Output

A formatting execution report containing:

- Count of files checked and files reformatted
- List of files that were modified with before/after formatting status
- Configuration file(s) created or updated (`.prettierrc`, `.prettierignore`)
- Any git hook integration changes applied
- Confirmation of final formatting compliance

## Error Handling

| Error | Cause | Solution |
|---|---|---|
| `prettier: command not found` | Prettier not installed globally or locally | Run `npm install -g prettier` or `npx prettier --version` to use npx |
| Syntax errors in source files | Malformed code that Prettier cannot parse | Fix syntax errors first using `npx eslint --fix-dry-run <file>` then retry formatting |
| Configuration conflicts | Multiple `.prettierrc` files or conflicting `editorconfig` | Locate all config files with `find . -name ".prettier*"` and consolidate to a single config |
| Permission denied on write | File or directory lacks write permission | Run `chmod u+w <file>` to grant write access |
| Parser not found for file type | Unsupported file extension or missing Prettier plugin | Install the appropriate Prettier plugin (e.g., `prettier-plugin-svelte`) or exclude the file type |

## Examples

**Format a single file:**
Trigger: "Format src/app.js"
Process: Run `npx prettier --write src/app.js`. Report the file as reformatted or already conformant.

**Project-wide formatting setup:**
Trigger: "Set up code formatting for this project."
Process: Create `.prettierrc` with project defaults, create `.prettierignore` excluding build outputs, run `npx prettier --write "src/**/*.{js,ts,json,css}"`, install `husky` and `lint-staged` for pre-commit hooks, verify compliance.

**Check formatting without modifying files:**
Trigger: "Check formatting across the project."
Process: Run `npx prettier --check "**/*.{js,jsx,ts,tsx,json,css,md}"`. Report non-conforming files with their paths. Suggest `npx prettier --write` to fix.

## Resources

- `${CLAUDE_SKILL_DIR}/references/implementation.md` -- detailed implementation guide with configuration examples
- `${CLAUDE_SKILL_DIR}/references/errors.md` -- common error scenarios and solutions
- [Prettier documentation](https://prettier.io/docs/en/) -- official configuration and CLI reference
- [ESLint](https://eslint.org/) -- complementary linting and code quality tool
- [Husky](https://typicode.github.io/husky/) -- git hooks for pre-commit formatting enforcement
