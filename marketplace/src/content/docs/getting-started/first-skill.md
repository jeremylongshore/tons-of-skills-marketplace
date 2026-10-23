---
title: 'Your First Agent Skill'
description: 'Create a local review skill with all eight marketplace fields, an actual linked reference, explicit validation, and local plugin loading.'
section: 'getting-started'
order: 3
keywords:
  - "Claude Code skills"
  - "SKILL.md"
  - "agent skills"
  - "write a skill"
  - "Claude Code skill tutorial"
  - "skill frontmatter"
  - "auto-activating skills"
officialLinks:
  - title: 'Claude Code Skills Documentation'
    url: 'https://code.claude.com/docs/en/skills'
  - title: 'Claude Code Plugin Structure'
    url: 'https://code.claude.com/docs/en/plugins'
relatedDocs:
  - 'getting-started/first-plugin'
  - 'concepts/skills'
  - 'guides/write-a-skill'
---

## Overview

This tutorial creates a local plugin containing one read-only review skill. It demonstrates the repository's marketplace metadata contract without changing native Claude's permissive format. It does not claim that the example is already published, behaviorally evaluated, or suitable for every repository.

Use a new scratch directory you control. Do not overwrite an installed plugin or place secrets in the example files.

## Step 1: Create the layout

```text
example-review-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── review-diff/
│       ├── SKILL.md
│       └── references/
│           └── review-checklist.md
├── README.md
└── LICENSE
```

Create those files using your editor. Paths in this tutorial are illustrative and relative to this new plugin directory. Native standard-layout discovery can work without a manifest, but a repository submission has stricter metadata and documentation requirements.

## Step 2: Add truthful manifest metadata

Put this illustrative manifest in `.claude-plugin/plugin.json`, then replace the author and homepage with truthful project metadata before publication:

```json
{
  "name": "example-review-plugin",
  "version": "1.0.0",
  "description": "Review supplied diffs using a bounded local checklist.",
  "author": { "name": "Example Team" },
  "homepage": "https://example.com/example-review-plugin",
  "license": "MIT",
  "keywords": ["review", "testing"],
  "commands": []
}
```

`author` is an object, not a string. The empty `commands` array is appropriate because this example supplies a skill rather than legacy command files. Include the actual license text and a README explaining scope and prerequisites. This sample is not an exhaustive native manifest field allowlist.

## Step 3: Write the complete skill

Place the following in `skills/review-diff/SKILL.md`. The outer fence is deliberately longer than its inner output fence:

````markdown
---
name: review-diff
description: Review a user-supplied Git diff for concrete correctness risks and missing tests without modifying files.
allowed-tools: Read, Grep, Glob
version: 1.0.0
author: Example Team
license: MIT
compatibility: Claude Code with access to the local repository and a user-supplied diff.
tags: [review, testing]
---

# Review Diff

## Overview

Review the supplied diff and relevant source files. This skill does not require
package installation, test execution, or provider access.

## Prerequisites

The user supplies the diff, repository location, and review focus. Confirm that
the source is available before making claims about it.

## Instructions

1. Identify changed behavior and the callers affected by it.
2. Read the relevant source and existing tests without modifying them.
3. Apply the [review checklist](references/review-checklist.md).
4. Report only findings supported by the supplied diff and inspected source.
5. Separate observed facts from behavior requiring execution to verify.

## Output

```text
Finding: path and location — concrete risk and suggested test
Uncertainty: information or execution needed to establish behavior
```

## Error Handling

If source or the diff is missing, ask for it. If a tool is denied, report the
limitation. Do not invent test, installation, or provider results.

## Examples

Input: a diff changes an error handler to return success on a read failure.
Output: identify the changed failure path and suggest an operational-error test.

## Resources

Use the bundled [review checklist](references/review-checklist.md) to inspect
failure paths and distinguish source facts from unexecuted behavior. The user's
supplied diff and selected repository source provide the evidence for findings;
the checklist alone does not establish that any defect exists or tests passed.
````

### Required fields

All eight fields are required at marketplace tier: `name`, `description`, `allowed-tools`, `version`, `author`, `license`, `compatibility`, and `tags`. Missing fields are errors. Native Claude and the Agent Skills open standard have separate permissive floors; that distinction does not make tracking metadata optional here.

`allowed-tools` grants invocation-time preapproval; it does not prevent every other tool from being called under normal permission rules. The read-only intent in this example is not a sandbox. Do not add broad Bash permission or a package installer simply to make the tutorial convenient.

If a future skill needs Bash, use separate supported patterns such as `Bash(git diff *)` and `Bash(git status *)`. Do not combine unrelated expressions inside one `Bash(...)` rule. Review command semantics and permission settings independently.

## Step 4: Create the linked reference

Put this content in `skills/review-diff/references/review-checklist.md`:

```markdown
# Review Checklist

- Identify what behavior changed and which caller relies on it.
- Inspect error and refusal paths, not only successful output.
- Check whether an existing test would expose the suspected defect.
- Distinguish source evidence from unexecuted behavior.
- Exclude credentials and unnecessary private data from the report.
```

The actual Markdown link in `SKILL.md` points to this same-skill file. “See API docs” without a href would not provide that navigation. Keep resource links within the supported skill boundary and create targets before claiming they exist.

## Step 5: Validate explicitly

From a checkout of this repository with the documented prerequisites installed, substitute the actual scratch path:

```bash
python3 scripts/validate-skills-schema.py --standard /absolute/path/to/example-review-plugin/skills/review-diff/SKILL.md
python3 scripts/validate-skills-schema.py --marketplace --verbose /absolute/path/to/example-review-plugin/skills/review-diff/SKILL.md
```

The explicit flags distinguish native-floor checks from marketplace requirements. Inspect warnings as well as errors. The validator's existing `--fail-on-warn` changes how warnings affect that invocation's exit status; this tutorial does not adopt a new gate or require a particular static grade.

Static checks do not establish that a skill performs a useful review. They also do not certify security, successful native activation, or a live provider. Test those boundaries separately with authorized, non-sensitive fixtures.

## Step 6: Load the local plugin

Use the actual plugin root, not the repository root or skill subdirectory:

```bash
claude --plugin-dir /absolute/path/to/example-review-plugin
```

Then invoke the namespaced skill in that session:

```text
/example-review-plugin:review-diff
```

Supply a small non-sensitive diff and check whether the report is supported by the source. A plain `claude` invocation does not automatically register an arbitrary current-directory plugin. Do not install dependencies or execute repository code as part of this read-only trial.

## Optional features and next steps

Skills can support arguments, forked context, model-dependent effort, and lifecycle hooks. Learn each feature from the [native skills reference](https://code.claude.com/docs/en/skills) before adding it. Hook event keys are names such as `PreToolUse`, not `pre-tool-call`; use the actual nested hook schema and stdin JSON contract.

For larger skills, move detailed material into linked references while keeping the main workflow usable. Static content-density scoring is not a new minimum word-count acceptance rule. Before contributing, follow repository review and generation instructions; do not hand-edit catalogs or assume a template is current merely because it exists.
