## Validation Workflow

When the user wants to validate, grade, or audit an existing skill:

### Step V1: Locate the Skill

Ask for the SKILL.md path or detect from context. Common locations:

- `~/.claude/skills/{name}/SKILL.md` (global)
- `.claude/skills/{name}/SKILL.md` (project)

### Step V2: Run Validator

```bash
# Standard tier (Anthropic spec exactly: name + description required)
python3 ~/000-projects/claude-code-plugins/scripts/validate-skills-schema.py {path}/SKILL.md

# Marketplace tier (100-point rubric, all eight marketplace fields required)
python3 ~/000-projects/claude-code-plugins/scripts/validate-skills-schema.py --marketplace {path}/SKILL.md

# Deep evaluation (10 dimensions, badges, Elo ranking)
python3 ~/000-projects/claude-code-plugins/scripts/validate-skills-schema.py --deep {path}/SKILL.md

# Deterministic package check (run from the marketplace root; use an absolute target)
pnpm exec j-rig check "/absolute/path/to/skill-directory" --json

# Behavioral evaluation is separate and opt-in: /validate-skillmd Step 2.7
# routes authorized runs through scripts/run-jrig-eval.sh.
```

`--deep` is deterministic content assessment, not skill execution. The legacy
`--thorough` flag is not implemented by the Python validator; unknown arguments
are currently ignored, so an exit code cannot establish behavioral coverage.

### Step V3: Review the Actual Results

Read the target validator's reported score, grade, errors and warnings. Its
current implementation owns the rubric and weights; do not substitute a copied
historical table. A deterministic deep assessment is separate from executing a
skill against a model. Neither score implies complete behavioral coverage.

See [validation rules](validation-rules.md) for evidence classes, canonical
commands and how to retain missing or failed results.

### Step V4: Report Results

Present the grade report with specific fix recommendations. Prioritize fixes by point value (highest first).

### Step V5: Auto-Fix (if requested)

If the user says "fix it" or "auto-fix", apply the suggested improvements:

1. Add missing sections (Overview, Prerequisites, Output)
2. Add "Use when" / "Trigger with" to description
3. Move author/version from metadata to top-level
4. Fix path variables to `${CLAUDE_SKILL_DIR}/`
5. Re-run grading to confirm improvement
