# Claude Plugin Validator

**Validate Claude Code plugins for completeness and best practices before publishing.**

Ensure your plugin meets quality standards with automated checks for required files, JSON validity, 2026 schema compliance, security vulnerabilities, and more.

## Quick Start

```bash
# Run without installing (recommended)
npx claude-plugin-validator ./my-plugin

# Or install globally
npm install -g claude-plugin-validator
claude-plugin-validator ./my-plugin
```

## What It Checks

### ✅ Required Files
- `README.md` - Plugin documentation
- `LICENSE` - Open source license (MIT recommended)
- `.claude-plugin/plugin.json` - Plugin manifest

### 📋 Configuration Validation
- Valid JSON syntax in all config files
- Required manifest fields (name, version, description, author)
- Semantic versioning format (x.y.z)
- Valid model identifiers (`sonnet`, `haiku`, `opus`, or `claude-*`)

### 🧩 Plugin Components
- At least one component directory (commands, agents, hooks, skills, scripts, mcp)
- Agent Skills frontmatter validation
- 2026 schema compliance (`allowed-tools`, `version` fields)
- Trigger phrase presence in skill descriptions

### 🔒 Security Checks
- No hardcoded passwords
- No hardcoded API keys
- No AWS credentials
- No private keys
- No dangerous commands (`rm -rf /`, `eval()`)

### 🛠️ Script Quality
- Shell scripts are executable (`chmod +x`)
- No dangerous patterns in scripts

## Output Example

```
============================================================
🔍 Validating Plugin: my-awesome-plugin
============================================================

📄 Checking Required Files...

📋 Validating Configuration Files...

🧩 Checking Plugin Components...

🔒 Security Checks...

============================================================
📊 VALIDATION REPORT
============================================================

✅ PASSED (15)
  ✓ README.md exists
  ✓ LICENSE exists
  ✓ .claude-plugin/plugin.json exists
  ✓ plugin.json has name
  ✓ plugin.json has version
  ✓ plugin.json has description
  ✓ plugin.json has author
  ✓ .claude-plugin/plugin.json is valid JSON
  ✓ Has 2 component(s): commands, skills
  ✓ Found 1 skill(s)
  ✓ Skill "my-skill" complies with 2026 schema
  ✓ Skill "my-skill" has description
  ✓ Script deploy.sh is executable
  ✓ No hardcoded secrets detected

⚠️  WARNINGS (1)
  ⚠ Skill "my-skill" description could include clearer trigger phrases

============================================================
🎯 SCORE: 90/95 (95%) - Grade: A
============================================================

🎉 Perfect! Your plugin is ready for publication!
```

## Grading System

| Grade | Score | Status |
|-------|-------|--------|
| **A** | 90-100% | ✅ Ready for publication |
| **B** | 80-89% | 👍 Good, address warnings |
| **C** | 70-79% | ⚠️ Needs improvement |
| **D** | 60-69% | ⚠️ Fix errors before publishing |
| **F** | <60% | ❌ Not ready, fix critical issues |

## Usage in CI/CD

Add to your GitHub Actions workflow:

```yaml
name: Validate Plugin

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Plugin
        run: npx claude-plugin-validator ./
```

## Exit Codes

- `0` - Validation passed (warnings allowed)
- `1` - Validation failed (critical errors found)

## Common Issues

### Missing LICENSE

```bash
❌ ERRORS (1)
  ✗ LICENSE missing (REQUIRED)
```

**Fix:** Add a LICENSE file (MIT recommended):

```bash
# Use MIT License template
curl -o LICENSE https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt
```

### Invalid plugin.json

```bash
❌ ERRORS (1)
  ✗ .claude-plugin/plugin.json is invalid JSON
```

**Fix:** Validate JSON syntax:

```bash
cat .claude-plugin/plugin.json | jq
```

### Invalid Model Identifier

```bash
❌ ERRORS (1)
  ✗ plugin.json contains invalid model identifier
```

**Fix:** Use a valid model ID:

```json
{
  "model": "sonnet"  // or "haiku", "opus", "claude-*"
}
```

### Script Not Executable

```bash
❌ ERRORS (1)
  ✗ Script deploy.sh is not executable (chmod +x)
```

**Fix:** Make scripts executable:

```bash
chmod +x scripts/*.sh
```

### Missing 2025 Schema Fields

```bash
⚠️  WARNINGS (1)
  ⚠ Skill "my-skill" missing 2026 schema fields (allowed-tools, version)
```

**Fix:** Add frontmatter to SKILL.md:

```yaml
---
name: my-skill
description: |
  What this skill does. Trigger phrases: "run analysis", "check performance"
allowed-tools: Read, Grep, Bash
version: 1.0.0
---
```

## Programmatic Usage

```javascript
const PluginValidator = require('claude-plugin-validator');

const validator = new PluginValidator('./my-plugin');
validator.validate();

// Access results
console.log(`Score: ${validator.score}/${validator.maxScore}`);
console.log(`Errors: ${validator.errors.length}`);
console.log(`Warnings: ${validator.warnings.length}`);
```

## 2025 Schema Compliance

The validator checks for **Anthropic's 2026 Skills Schema** compliance:

### Required Fields

```yaml
---
name: skill-name          # lowercase, hyphens, max 64 chars
description: |            # Clear "what" and "when" with trigger phrases
  What the skill does...
allowed-tools: Read, Write, Edit, Grep  # Tool permissions
version: 1.0.0           # Semantic versioning
---
```

### Tool Categories

- **Read-only:** `Read, Grep, Glob, Bash`
- **Code editing:** `Read, Write, Edit, Grep, Glob, Bash`
- **Web research:** `Read, WebFetch, WebSearch, Grep`
- **Database ops:** `Read, Write, Bash, Grep`

## Best Practices

1. **README.md should include:**
   - Clear description of what the plugin does
   - Installation instructions
   - Usage examples
   - Screenshots/demos (if applicable)

2. **Skills should have:**
   - Clear trigger phrases in description
   - Minimal `allowed-tools` for security
   - Version number for tracking updates

3. **Security:**
   - Never hardcode secrets
   - Use environment variables
   - Request minimal permissions
   - Validate all inputs in scripts

4. **Scripts:**
   - Make executable (`chmod +x`)
   - Add shebangs (`#!/bin/bash`)
   - Use `${CLAUDE_PLUGIN_ROOT}` for paths

## Contributing

Found a bug or want to add checks? Contribute at:
[github.com/jeremylongshore/claude-code-plugins](https://github.com/jeremylongshore/claude-code-plugins)

## Resources

- **Claude Code Docs:** https://docs.claude.com/en/docs/claude-code/
- **Plugin Marketplace:** https://tonsofskills.com/
- **Community:** https://github.com/jeremylongshore/claude-code-plugins/discussions

## License

MIT © 2024-2026 Jeremy Longshore & Contributors

---

**Made with ❤️ by the Claude Code Plugins community**
*Visit [tonsofskills.com](https://tonsofskills.com) for 253 production-ready plugins*
