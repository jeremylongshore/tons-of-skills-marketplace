---
name: create-plugin
description: Interactive plugin creator with marketplace-grade validation and scaffolding
shortcut: cp
author: Jeremy Longshore <jeremy@intentsolutions.io>
version: 2.0.0
---
# Create Plugin - Interactive Workflow

You are creating a **production-grade Claude Code plugin** with marketplace-validated quality standards.

## Step 1: Ask User About Plugin Type

Use AskUserQuestion to ask:

**Question:** "What type of plugin do you want to create?"

**Options:**

1. **Commands Only** - Slash commands (like /deploy, /test)
   - Description: Creates a plugin with custom slash commands for repeatable workflows

2. **Agent Only** - Specialized AI agent
   - Description: Creates a domain expert agent with specialized knowledge and capabilities

3. **Skills Only** - Auto-invoked agent skills
   - Description: Creates skills that activate automatically based on conversation context

4. **Full Plugin** - Commands + Agents + Skills
   - Description: Creates a comprehensive plugin with all component types

## Step 2: Ask About Plugin Purpose

Use AskUserQuestion to ask:

**Question:** "Describe what your plugin should do"

**Guide user to provide:**

- Purpose (what problem it solves)
- Trigger phrases (how users will invoke it)
- Key features (what it should include)

## Step 3: Ask About Category

Use AskUserQuestion with categories:

**Question:** "Which category best fits your plugin?"

**Options:**

- productivity
- security
- devops
- ai-ml
- database
- api-development
- crypto
- finance
- performance
- business-tools
- testing
- examples

## Step 4: Generate Plugin Structure

Based on answers, create:

### Directory Structure

```
plugins/[category]/[plugin-name]/
├── .claude-plugin/
│   └── plugin.json          # Manifest
├── README.md                 # Documentation
├── LICENSE                   # MIT recommended
├── commands/ (if selected)
│   └── [command-name].md
├── agents/ (if selected)
│   └── [agent-name].md
└── skills/ (if selected)
    └── [skill-name]/
        ├── SKILL.md
        ├── scripts/
        ├── references/
        └── assets/
```

### Generate plugin.json

```json
{
  "name": "[kebab-case-name]",
  "version": "1.0.0",
  "description": "[Generated from user's description - MUST include 'Use when...' and 'Trigger with...']",
  "author": {
    "name": "Jeremy Longshore",
    "email": "jeremy@intentsolutions.io",
    "url": "https://intentsolutions.io"
  },
  "license": "MIT",
  "keywords": [
    "[category]",
    "[relevant-keywords]"
  ]
}
```

### Generate SKILL.md (Marketplace-Compliant)

**CRITICAL: All skills MUST pass marketplace validation:**

```markdown
---
name: [skill-name]
description: |
  [Action-oriented third-person description].
  Use when [specific scenarios].
  Trigger with "[example user phrases]" or "[alternative phrases]".
allowed-tools: Read, Write, Bash(git:*), Bash(npm:*)
version: 1.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
---

# [Skill Title]

[Purpose statement - 1-2 sentences explaining what this skill does]

## Overview

[High-level explanation of the skill's capabilities and when to use it]

## Prerequisites

- [Requirement 1]
- [Requirement 2]
- [etc.]

## Instructions

### Step 1: [First action]

[Detailed explanation]

### Step 2: [Second action]

[Detailed explanation]

### Step 3: [Final action]

[Detailed explanation]

## Output

[What the user receives after execution]

## Error Handling

[Common errors and how to resolve them]

## Examples

### Example 1: [Scenario]

```

User: [example input]

Skill: [what it does]

Result: [expected output]

```

### Example 2: [Another scenario]

```

[Another example]

```

## Resources

- ${CLAUDE_SKILL_DIR}/references/[reference-file.md] - [Description]
- External link: [Resource name]
```

## Step 5: Validate with Marketplace Validator

After creating all files, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/skills/plugin-validator/scripts/validate_plugin_marketplace.py plugins/[category]/[plugin-name]/
```

**Requirements for passing validation:**

- ✅ Description includes "Use when..." phrase
- ✅ Description includes "Trigger with..." phrase
- ✅ Third-person voice only (no "I can" or "You should")
- ✅ Scoped Bash permissions (Bash(git:*), not plain Bash)
- ✅ All required sections present: Overview, Prerequisites, Instructions, Output, Error Handling, Examples, Resources
- ✅ Section content is non-empty (>20 chars per section)
- ✅ Instructions have numbered steps
- ✅ Body under 500 lines
- ✅ Kebab-case name matching folder name
- ✅ Semver version format (X.Y.Z)

## Step 6: Add to Marketplace

1. Add entry to `.claude-plugin/marketplace.extended.json`
2. Run `pnpm run sync-marketplace`
3. Validate: `./scripts/validate-all-plugins.sh plugins/[category]/[plugin-name]/`

## Step 7: Report Results

Show user:

```
✅ Plugin created successfully!

📁 Location: plugins/[category]/[plugin-name]/
📝 Files created:
   - .claude-plugin/plugin.json
   - README.md
   - LICENSE
   [+ other files based on type]

🔍 Marketplace Validation: [PASSED/FAILED with X errors]

📦 Marketplace: [UPDATED/PENDING]

Next steps:
1. Review generated files
2. Customize README with examples
3. Test: /plugin install [plugin-name]@claude-code-plugins-plus
```

## Error Handling

### Validation Failures

If marketplace validation fails:

1. Show specific errors
2. Offer to fix automatically
3. Re-run validation after fixes

### Duplicate Plugin Names

If plugin name exists:

1. Suggest alternative names
2. Ask user to choose different name
3. Retry creation

## Best Practices

- **Always use scoped Bash** - Never `Bash`, always `Bash(git:*)` or `Bash(npm:*)`
- **Third-person voice** - "Validates code" not "I can validate" or "You can validate"
- **Include trigger phrases** - Help Claude recognize when to activate
- **Progressive disclosure** - Keep SKILL.md under 500 lines, use references/ for details
- **Step-by-step instructions** - Use numbered lists or step headings
- **Non-empty sections** - All required sections must have meaningful content

## Success Criteria

Plugin creation succeeds when:

- ✅ All files generated correctly
- ✅ Marketplace validation passes (100% compliance)
- ✅ Marketplace entry added
- ✅ Plugin installs successfully

---

**This command implements Jeremy's workflow:**

1. Ask user what kind of plugin
2. User describes purpose
3. Generate with marketplace-grade validation
4. Validate automatically
5. Add to marketplace
6. Done!
