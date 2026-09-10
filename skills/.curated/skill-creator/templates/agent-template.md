---
name: {{AGENT_NAME}}
description: "{{CONCISE_AGENT_SPECIALTY_20_1536_CHARS}}"
# IS marketplace-required fields:
tools: [Read, Glob, Grep]                # Allowlist; scope to the actual workflow
model: inherit                           # sonnet|haiku|opus|fable|inherit|full Claude model ID
color: blue                              # red|blue|green|yellow|purple|orange|pink|cyan
version: 1.0.0
author: "{{AUTHOR_NAME}} <{{AUTHOR_EMAIL}}>"
tags: [{{TAG_1}}, {{TAG_2}}]
disallowedTools: []                      # IS denylist form; camelCase on agents
skills: []                               # Skill names to preload
background: false
# Optional tuning fields (include as needed):
# effort: medium                         # low|medium|high|xhigh|max
# maxTurns: 15                           # Max agentic loop iterations
# memory: project                        # user|project|local
# isolation: worktree                    # Isolated git worktree
# initialPrompt: "Start with the intake." # First turn when launched via --agent
# experimental:                          # Claude Code v2.1.248+
#   cacheTtl: 5m                         # 5m|1h
# Standalone agents require these under the IS contract. Claude Code ignores
# them in plugin agents, so omit them there:
# hooks: {}
# mcpServers: []                          # Server names or one-key inline definitions
# permissionMode: default                 # manual is an alias for default
---

# {{AGENT_TITLE}}

{{ONE_LINE_ROLE_STATEMENT}}

## Role

{{DETAILED_ROLE_DESCRIPTION_2_3_SENTENCES. What domain does this agent specialize in?
What unique perspective or methodology does it bring? What is it NOT responsible for?}}

## Inputs

You receive these parameters in your prompt:

- **{{INPUT_1}}**: {{DESCRIPTION}}
- **{{INPUT_2}}**: {{DESCRIPTION}}
- **{{INPUT_3}}**: {{DESCRIPTION}}

## Process

### Step 1: {{STEP_TITLE}}

{{DETAILED_INSTRUCTIONS_FOR_STEP}}

### Step 2: {{STEP_TITLE}}

{{DETAILED_INSTRUCTIONS_FOR_STEP}}

### Step 3: {{STEP_TITLE}}

{{DETAILED_INSTRUCTIONS_FOR_STEP}}

### Step 4: {{STEP_TITLE}}

{{DETAILED_INSTRUCTIONS_FOR_STEP}}

## Output Format

{{DESCRIBE_STRUCTURED_OUTPUT_FORMAT}}

```json
{
  "{{FIELD_1}}": "{{DESCRIPTION}}",
  "{{FIELD_2}}": [
    {
      "{{SUBFIELD}}": "{{DESCRIPTION}}"
    }
  ],
  "summary": {
    "{{METRIC_1}}": 0,
    "{{METRIC_2}}": 0
  }
}
```

## Guidelines

- **{{GUIDELINE_1}}**: {{EXPLANATION}}
- **{{GUIDELINE_2}}**: {{EXPLANATION}}
- **{{GUIDELINE_3}}**: {{EXPLANATION}}
- **{{GUIDELINE_4}}**: {{EXPLANATION}}

## When Activated

You activate when:

- {{ACTIVATION_CONDITION_1}}
- {{ACTIVATION_CONDITION_2}}
- {{ACTIVATION_CONDITION_3}}

## Communication Style

- {{STYLE_TRAIT_1}}
- {{STYLE_TRAIT_2}}
- {{STYLE_TRAIT_3}}

## Success Criteria

Good output includes:

- {{QUALITY_MARKER_1}}
- {{QUALITY_MARKER_2}}
- {{QUALITY_MARKER_3}}

Poor output is:

- {{ANTI_PATTERN_1}}
- {{ANTI_PATTERN_2}}
- {{ANTI_PATTERN_3}}
