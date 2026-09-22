---
# Required (AgentSkills.io)
# NOTE: name and description must NOT contain XML tags (< or >)
name: {{SKILL_NAME}}
description: |
  {{PURPOSE_STATEMENT}}. Use when {{WHEN_TO_USE}}.
  Trigger with "/{{SKILL_NAME}}" or "{{NATURAL_TRIGGER}}".

# Tools (recommended)
allowed-tools: "{{TOOLS_CSV}}"
# Optional defense-in-depth denylist (schema 3.7.0+) — must never overlap allowed-tools
# disallowed-tools: "Bash(rm:*),Bash(curl:*),Bash(wget:*),Bash(sudo:*)"

# Identity (top-level, NOT inside metadata)
version: 1.0.0
author: {{AUTHOR_NAME}} <{{AUTHOR_EMAIL}}>
license: MIT
compatibility: "{{ENVIRONMENT_REQUIREMENTS}}"
tags: [{{TAG_1}}, {{TAG_2}}]

# Claude Code extensions (include as needed)
model: inherit
# effort: high
# argument-hint: "[arg-description]"
# arguments: [arg-name]
# disable-model-invocation: false
# user-invocable: true
# context: fork
# agent: general-purpose
# background: false
# paths: ["src/**"]
# shell: bash

# Optional spec fields
# metadata:
#   category: {{CATEGORY}}
---

# {{SKILL_TITLE}}

{{PURPOSE_STATEMENT_1_2_SENTENCES}}

## Overview

{{WHAT_THIS_SKILL_SOLVES_AND_WHY_IT_EXISTS}}

## Prerequisites

- {{PREREQUISITE_1}}
- {{PREREQUISITE_2}}

## Instructions

### Step 1: {{STEP_1_TITLE}}

{{STEP_1_DETAILED_INSTRUCTIONS}}

### Step 2: {{STEP_2_TITLE}}

{{STEP_2_DETAILED_INSTRUCTIONS}}

### Step 3: {{STEP_3_TITLE}}

{{STEP_3_DETAILED_INSTRUCTIONS}}

## Output

{{DESCRIPTION_OF_EXPECTED_OUTPUT_FORMAT}}

## Examples

### {{EXAMPLE_1_TITLE}}

**Input:**

```
{{EXAMPLE_1_INPUT}}
```

**Output:**

```
{{EXAMPLE_1_OUTPUT}}
```

### {{EXAMPLE_2_TITLE}}

**Input:**

```
{{EXAMPLE_2_INPUT}}
```

**Output:**

```
{{EXAMPLE_2_OUTPUT}}
```

## Edge Cases

- {{EDGE_CASE_1}}
- {{EDGE_CASE_2}}

<!-- Optional: Include for quality-critical workflows -->
<!-- ## Feedback Loop
Run validation after each major step. If issues found, fix and re-validate:
1. Execute step
2. Validate output
3. If validation fails → fix → return to step 2
4. Maximum 3 iterations before reporting -->

<!-- Optional: Include if skill documents deprecated approaches -->
<!-- ## Old Patterns
These patterns are deprecated but users may encounter them:
| Old Pattern | Replacement | Why Changed |
|-------------|-------------|-------------|
| {{OLD_1}} | {{NEW_1}} | {{REASON_1}} | -->

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| {{ERROR_1}} | {{CAUSE_1}} | {{SOLUTION_1}} |
| {{ERROR_2}} | {{CAUSE_2}} | {{SOLUTION_2}} |

## Resources

- ${CLAUDE_SKILL_DIR}/references/{{REFERENCE_1}}.md - {{REFERENCE_1_PURPOSE}}
- ${CLAUDE_SKILL_DIR}/scripts/{{SCRIPT_1}}.py - {{SCRIPT_1_PURPOSE}}
