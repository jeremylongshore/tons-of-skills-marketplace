# Code Formatter Plugin v2.0.1

A comprehensive code formatting plugin for Claude Code that automatically formats your code using Prettier and other formatting tools. Includes automatic formatting hooks, validation commands, and Agent Skills for intelligent formatting assistance.

## ✨ Features

- **Automatic Formatting** - Format code automatically after edits using PostToolUse hooks
- **Format Validation** - Check if files are properly formatted without changes
- **Agent Skills** - Intelligent formatting assistance that activates on keywords
- **Multiple File Types** - Supports JS, TS, JSON, CSS, MD, YAML, HTML, Vue, Svelte
- **Custom Commands** - `/format` and `/format-check` for manual control
- **CI/CD Ready** - Integration scripts for GitHub Actions and other pipelines
- **Configurable** - Use your own Prettier config or defaults

## 🚀 Installation

```bash
# Add the marketplace
/plugin marketplace add jeremylongshore/claude-code-plugins

# Install the formatter plugin
/plugin install formatter@claude-code-plugins-plus
```

## 📋 Prerequisites

The plugin requires Node.js, npm/npx, and `jq` for native hook-event parsing:

```bash
# Check if Node.js is installed
node --version

# Install Prettier globally (optional)
npm install -g prettier

# Or use npx (no installation needed)
npx prettier --version
```

## 🎯 Usage

### Automatic Formatting (Hooks)

The plugin automatically formats files after you edit them:

1. When Claude uses the `Write` or `Edit` tool
2. The PostToolUse hook triggers
3. Files are automatically formatted with Prettier
4. You see the formatting applied immediately

### Manual Commands

**Format files:**

```bash
# Format all files in project
/format

# Format specific directory
/format src/

# Format specific file
/format src/app.js

# Format with custom config
/format --config .prettierrc.strict src/
```

**Check formatting:**

```bash
# Check all files
/format-check

# Check specific files
/format-check **/*.js

# Use in CI/CD (exits with error if unformatted)
/format-check || exit 1
```

### Agent Skills

The plugin's Agent Skill activates when you mention:

- "format my code"
- "fix formatting"
- "apply code style"
- "check formatting"
- "make code consistent"
- "clean up code"

Example:

```
User: "Please format my JavaScript files"
Claude: [Activates code-formatter skill and formats all JS files]
```

## ⚙️ Configuration

### Prettier Configuration

Create a `.prettierrc` file in your project:

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

### Ignore Files

Create `.prettierignore` to skip files:

```
# Dependencies
node_modules/
vendor/

# Build outputs
dist/
build/
*.min.js
*.min.css

# Generated files
coverage/
*.lock
```

### Hook Configuration

The plugin's hooks are configured in `hooks/hooks.json`:

- **PostToolUse** - Runs after Write/Edit operations
- **PreToolUse** - Optional validation before editing (disabled by default)

The scripts read the matching group's `enabled` flag in `hooks/hooks.json`.
To disable automatic formatting, set the **PostToolUse** group's `enabled` to
`false`. The optional **PreToolUse** validation stays inert while its flag is
`false`, before checking Prettier or attempting an `npx` call. These flags are
controls implemented by this plugin's scripts; Claude Code does not enforce
individual-hook disablement through group-level `enabled` metadata.

Automatic formatting reads native `tool_input.file_path`, with
`tool_response.filePath` as a fallback, only for successful Write/Edit events.
Legacy payload paths remain supported for manual callers. Explicit filename
invocations of `validate-format.sh` remain available regardless of the optional
hook's enable flag.

## 🔧 Scripts

The plugin includes two main scripts:

### format.sh

- Main formatting script
- Handles file detection and Prettier execution
- Supports multiple file types
- Includes error handling and logging

### validate-format.sh (NEW)

- Validates formatting without changes
- Perfect for pre-commit checks
- Returns exit codes for CI/CD
- Detailed logging and debugging

Both scripts are executable and support debug mode:

```bash
# Enable debug mode
export FORMATTER_DEBUG=true

# Check logs
tail -f plugins/examples/formatter/logs/formatter.log
```

## 🧪 Testing

To test the plugin installation:

```bash
# 1. Check if plugin is installed
/plugin list

# 2. Test format checking
echo 'const x={a:1,b:2}' > test.js
/format-check test.js

# 3. Test formatting
/format test.js
cat test.js  # Should show formatted code

# 4. Test Agent Skill
# Just say: "format my code"
```

## 📊 Supported File Types

| Extension | Language | Support Level |
|-----------|----------|--------------|
| .js, .jsx | JavaScript | ✅ Full |
| .ts, .tsx | TypeScript | ✅ Full |
| .json | JSON | ✅ Full |
| .css, .scss | CSS/SASS | ✅ Full |
| .md, .mdx | Markdown | ✅ Full |
| .yaml, .yml | YAML | ✅ Full |
| .html | HTML | ✅ Full |
| .vue | Vue | ✅ Full |
| .svelte | Svelte | ✅ Full |
| .graphql | GraphQL | ✅ Full |
| .xml | XML | ⚠️ Limited |

## 🚨 Troubleshooting

### Plugin Not Loading

```bash
# Reinstall the plugin
/plugin uninstall formatter@claude-code-plugins-plus
/plugin install formatter@claude-code-plugins-plus

# Check plugin status
/plugin list
```

### Prettier Not Found

```bash
# Install Prettier globally
npm install -g prettier

# Or ensure npx is available
which npx
```

### Formatting Not Working

1. Check if Node.js is installed: `node --version`
2. Verify script permissions: `ls -la scripts/`
3. Check for syntax errors in target files
4. Enable debug mode and check logs
5. Ensure files aren't in .prettierignore

### Hook Not Triggering

1. Check if hooks are enabled in hooks.json
2. Verify the matcher pattern matches your operation
3. Check the plugin is properly installed
4. Look for errors in Claude Code output

## 🔄 Updates

### v2.0.1 (2025-12-13)

- 🐛 Fixed duplicate hooks loading error (Issue #149)
- 🔧 Removed redundant hooks reference from plugin.json
- ✅ Claude Code now auto-discovers hooks/hooks.json

### v2.0.0 (2025-12-12)

- ✅ Fixed missing validate-format.sh script (Issue #147)
- ✨ Added comprehensive Agent Skills
- 📝 Enhanced plugin description with trigger phrases
- 🎯 Added format and format-check commands
- 📚 Complete documentation rewrite
- 🔧 Improved error handling and logging

### v1.0.0 (2025-10-11)

- Initial release with basic formatting hooks

## 👨‍💻 Contributing

Found a bug or have a suggestion? Please open an issue at:
https://github.com/jeremylongshore/claude-code-plugins/issues

## 📜 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Thanks to @beepsoft for reporting Issue #147
- Prettier team for the excellent formatting tool
- Claude Code community for feedback and suggestions

---

**Author**: Jeremy Longshore
**Email**: jeremy@intentsolutions.io
**Repository**: https://github.com/jeremylongshore/claude-code-plugins
