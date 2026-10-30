# Skill Creator

Create, validate and refresh skills against the existing IS marketplace contract.
The paired agent creator emits the IS plugin or standalone enterprise templates;
adapt them to another target repository's canonical gate.

## Features

- **Create mode**: Build complete skill packages from scratch with interactive wizard
- **Validate mode**: Grade existing skills against the Intent Solutions 100-point rubric
- **Auto-fix**: Automatically apply improvements to boost marketplace scores
- **Forge / reforge**: Manual API-driven generation and refresh, with separate build-time `.forge/` evidence
- **Evaluation**: Requested model comparisons and description optimization; static results remain separate

## Install

```bash
ccpi install skill-creator
```

Or copy `skills/skill-creator/` for standalone skill authoring. Copy the companion
`skills/agent-creator/` as well when generating agents. Static grading requires
the target's canonical IS validator; missing tooling is reported as unverified.

## Usage

```
/skill-creator              # Interactive skill creation
/skill-creator validate     # Grade an existing skill
/skill-creator optimize     # Requested description optimization
/skill-creator --forge API  # Generate from an API after its scope is known
/skill-creator --reforge PLUGIN # Refresh a generated plugin
```

## What's Included

| Directory | Purpose |
|-----------|---------|
| `skills/skill-creator/SKILL.md` | Main skill (works standalone) |
| `skills/agent-creator/` | Context-specific agent generation |
| `skills/skill-creator/references/` | Maintained authority and mode workflows |
| `references/` | Compatibility links to the maintained guides |
| `scripts/validate-skill.py` | Automated validation + 100-point grading |
| `skills/skill-creator/templates/` | Skill and agent skeletons |
| `templates/skill-template.md` | Compatible copy of the skill skeleton |

## Grading Rubric (100 points)

| Pillar | Max Points |
|--------|-----------|
| Progressive Disclosure | 30 |
| Ease of Use | 25 |
| Utility | 20 |
| Spec Compliance | 15 |
| Writing Style | 10 |
| Modifiers | +/-5 |

Grade scale: A (90+), B (80-89), C (70-79), D (60-69), F (<60)

## Author

Jeremy Longshore ([@jeremylongshore](https://github.com/jeremylongshore))

## License

MIT
