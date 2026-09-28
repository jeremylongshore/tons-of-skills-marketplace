#!/usr/bin/env node

/**
 * Claude Plugin Validator v2.0
 *
 * Validates Claude Code plugins for completeness and best practices.
 * Can scan individual plugins or all installed plugins.
 * Provides detailed fix instructions and auto-fix capabilities.
 *
 * Usage:
 *   npx claude-plugin-validator ./my-plugin
 *   npx claude-plugin-validator --installed
 *   npx claude-plugin-validator --installed --fix
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
  bold: '\x1b[1m',
  dim: '\x1b[2m'
};

// Fix templates
const FIX_TEMPLATES = {
  LICENSE: `MIT License

Copyright (c) ${new Date().getFullYear()} <YOUR NAME>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`,

  README: `# Plugin Name

Brief description of what this plugin does.

## Installation

\`\`\`bash
/plugin install <plugin-name>@<marketplace>
\`\`\`

## Usage

Describe how to use the plugin with examples.

## Features

- Feature 1
- Feature 2
- Feature 3

## License

MIT`,

  PLUGIN_JSON: (name) => `{
  "name": "${name || 'my-plugin'}",
  "version": "1.0.0",
  "description": "Description of what this plugin does",
  "author": {
    "name": "Your Name",
    "email": "your.email@example.com"
  },
  "license": "MIT",
  "keywords": ["claude-code", "plugin"]
}`,

  SKILL_FRONTMATTER: `---
name: skill-name
description: |
  What this skill does and when to use it.
  Trigger phrases: "analyze code", "check quality", "optimize performance"
allowed-tools: Read, Grep, Bash
version: 1.0.0
---

## How This Skill Works

Detailed explanation of the skill workflow.

## When to Use

- Use case 1
- Use case 2

## Examples

User: "analyze my code"
Skill activates → reads files → provides analysis`
};

// Detailed fix instructions
const FIX_INSTRUCTIONS = {
  'missing-readme': {
    title: 'Missing README.md',
    description: 'Every plugin needs a README.md file for documentation.',
    why: 'Users need to understand what your plugin does and how to use it.',
    fix: [
      '1. Create README.md in your plugin root directory',
      '2. Include: description, installation, usage, features, license',
      '3. Add examples and screenshots if applicable'
    ],
    example: FIX_TEMPLATES.README,
    autofix: true
  },

  'missing-license': {
    title: 'Missing LICENSE',
    description: 'Open source plugins require a LICENSE file.',
    why: 'Clarifies usage rights and protects both you and users.',
    fix: [
      '1. Create LICENSE file in plugin root',
      '2. MIT License is recommended for open source',
      '3. Update copyright year and author name'
    ],
    example: FIX_TEMPLATES.LICENSE,
    autofix: true
  },

  'missing-plugin-json': {
    title: 'Missing .claude-plugin/plugin.json',
    description: 'Plugin manifest is required for Claude Code to recognize your plugin.',
    why: 'Defines plugin metadata like name, version, description, author.',
    fix: [
      '1. Create .claude-plugin directory',
      '2. Add plugin.json with required fields',
      '3. Ensure valid JSON syntax'
    ],
    example: (name) => FIX_TEMPLATES.PLUGIN_JSON(name),
    autofix: true
  },

  'invalid-json': {
    title: 'Invalid JSON Syntax',
    description: 'Configuration file has JSON syntax errors.',
    why: 'Claude Code cannot parse invalid JSON files.',
    fix: [
      '1. Use a JSON validator or linter',
      '2. Common issues: trailing commas, unquoted keys, missing brackets',
      '3. Run: cat file.json | jq'
    ],
    autofix: false
  },

  'missing-2025-schema': {
    title: 'Skill Missing 2025 Schema Fields',
    description: 'Skills should include allowed-tools and version fields.',
    why: 'Improves security, performance, and user transparency.',
    fix: [
      '1. Add allowed-tools to SKILL.md frontmatter',
      '2. Add version field for tracking updates',
      '3. Include trigger phrases in description'
    ],
    example: FIX_TEMPLATES.SKILL_FRONTMATTER,
    autofix: true
  },

  'script-not-executable': {
    title: 'Script Not Executable',
    description: 'Shell scripts must have execute permissions.',
    why: 'Non-executable scripts will fail when Claude tries to run them.',
    fix: [
      '1. Make script executable: chmod +x script.sh',
      '2. Add shebang: #!/bin/bash',
      '3. Verify: ls -l script.sh (should show -rwxr-xr-x)'
    ],
    autofix: true
  },

  'hardcoded-secret': {
    title: 'Hardcoded Secret Detected',
    description: 'Never hardcode passwords, API keys, or credentials.',
    why: 'Security risk - secrets will be exposed in published plugins.',
    fix: [
      '1. Remove hardcoded value',
      '2. Use environment variables: process.env.API_KEY',
      '3. Prompt user at runtime if needed',
      '4. Document required env vars in README'
    ],
    autofix: false
  },

  'deprecated-opus': {
    title: 'Deprecated "opus" Model',
    description: 'The "opus" model identifier was deprecated in v1.0.46.',
    why: 'Plugins using "opus" will fail in newer Claude Code versions.',
    fix: [
      '1. Replace "opus" with "sonnet" for advanced reasoning',
      '2. Or use "haiku" for simple, fast tasks',
      '3. Update all command/agent frontmatter'
    ],
    autofix: true
  },

  'no-components': {
    title: 'No Plugin Components',
    description: 'Plugin must have at least one component directory.',
    why: 'Plugins need commands, agents, hooks, skills, scripts, or mcp to function.',
    fix: [
      '1. Create at least one: commands/, agents/, skills/, hooks/, scripts/, mcp/',
      '2. Add .md files for commands/agents or SKILL.md for skills',
      '3. Ensure proper frontmatter in markdown files'
    ],
    autofix: false
  }
};

class PluginValidator {
  constructor(pluginPath, options = {}) {
    this.pluginPath = path.resolve(pluginPath);
    this.pluginName = path.basename(this.pluginPath);
    this.options = options;
    this.errors = [];
    this.warnings = [];
    this.passes = [];
    this.fixes = [];
    this.score = 0;
    this.maxScore = 0;
  }

  log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
  }

  error(message, fixKey = null, points = 10) {
    this.errors.push({ message, fixKey });
    this.maxScore += points;
  }

  warning(message, fixKey = null, points = 5) {
    this.warnings.push({ message, fixKey });
    this.maxScore += points;
  }

  pass(message, points = 10) {
    this.passes.push(message);
    this.score += points;
    this.maxScore += points;
  }

  addFix(fixKey, data = {}) {
    if (FIX_INSTRUCTIONS[fixKey]) {
      this.fixes.push({ fixKey, data });
    }
  }

  checkFileExists(filename, required = true, points = 10, fixKey = null) {
    const filePath = path.join(this.pluginPath, filename);
    const exists = fs.existsSync(filePath);

    if (exists) {
      this.pass(`✓ ${filename} exists`, points);
      return true;
    } else {
      if (required) {
        this.error(`✗ ${filename} missing (REQUIRED)`, fixKey, points);
        if (fixKey) this.addFix(fixKey, { filename, filePath });
      } else {
        this.warning(`⚠ ${filename} missing (recommended)`, fixKey, points);
      }
      return false;
    }
  }

  validateJSON(filename, schema = null) {
    const filePath = path.join(this.pluginPath, filename);

    if (!fs.existsSync(filePath)) {
      return false;
    }

    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const data = JSON.parse(content);

      if (filename === '.claude-plugin/plugin.json') {
        this.validatePluginManifest(data);
      }

      this.pass(`✓ ${filename} is valid JSON`, 5);
      return data;
    } catch (err) {
      this.error(`✗ ${filename} is invalid JSON: ${err.message}`, 'invalid-json', 10);
      this.addFix('invalid-json', { filename, error: err.message });
      return false;
    }
  }

  validatePluginManifest(data) {
    const required = ['name', 'version', 'description', 'author'];

    required.forEach(field => {
      if (!data[field]) {
        this.error(`✗ plugin.json missing required field: ${field}`, 'missing-plugin-json', 5);
      } else {
        this.pass(`✓ plugin.json has ${field}`, 2);
      }
    });

    if (data.author && typeof data.author === 'string') {
      this.error('plugin.json "author" must be an object {name, email?}, not a string', 'string-author', 5);
    }
    if (data.author && typeof data.author === 'object' && !data.author.name) {
      this.error('plugin.json author object must have "name" field', 'missing-author-name', 3);
    }

    if (data.version && !/^\d+\.\d+\.\d+$/.test(data.version)) {
      this.warning(`⚠ version should follow semver format (x.y.z)`, null, 3);
    }

    // Check for deprecated opus model
    if (JSON.stringify(data).includes('"opus"')) {
      this.error('✗ plugin.json contains deprecated "opus" model identifier', 'deprecated-opus', 10);
      this.addFix('deprecated-opus', { file: 'plugin.json' });
    }
  }

  validateSkills() {
    const skillsDir = path.join(this.pluginPath, 'skills');

    if (!fs.existsSync(skillsDir)) {
      this.warning('⚠ No skills directory found', null, 5);
      return;
    }

    const skillDirs = fs.readdirSync(skillsDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);

    if (skillDirs.length === 0) {
      this.warning('⚠ Skills directory is empty', null, 5);
      return;
    }

    this.pass(`✓ Found ${skillDirs.length} skill(s)`, 5);

    skillDirs.forEach(skillName => {
      const skillFile = path.join(skillsDir, skillName, 'SKILL.md');

      if (!fs.existsSync(skillFile)) {
        this.error(`✗ Skill "${skillName}" missing SKILL.md`, null, 5);
        return;
      }

      const content = fs.readFileSync(skillFile, 'utf8');

      if (!content.startsWith('---')) {
        this.error(`✗ Skill "${skillName}" missing YAML frontmatter`, 'missing-2025-schema', 5);
        this.addFix('missing-2025-schema', { skill: skillName, file: skillFile });
        return;
      }

      const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
      if (!frontmatterMatch) {
        this.error(`✗ Skill "${skillName}" has invalid frontmatter`, null, 5);
        return;
      }

      const frontmatter = frontmatterMatch[1];

      const has2025Schema =
        frontmatter.includes('allowed-tools:') &&
        frontmatter.includes('version:');

      if (has2025Schema) {
        this.pass(`✓ Skill "${skillName}" complies with 2025 schema`, 5);
      } else {
        this.warning(`⚠ Skill "${skillName}" missing 2025 schema fields`, 'missing-2025-schema', 5);
        this.addFix('missing-2025-schema', { skill: skillName, file: skillFile });
      }

      if (!frontmatter.includes('description:')) {
        this.error(`✗ Skill "${skillName}" missing description`, null, 5);
      } else {
        this.pass(`✓ Skill "${skillName}" has description`, 2);
      }
    });
  }

  validateScripts() {
    const scriptsDir = path.join(this.pluginPath, 'scripts');

    if (!fs.existsSync(scriptsDir)) {
      return;
    }

    const scripts = fs.readdirSync(scriptsDir)
      .filter(f => f.endsWith('.sh'));

    scripts.forEach(script => {
      const scriptPath = path.join(scriptsDir, script);
      // Stat and read through one descriptor so the mode checked belongs to
      // the bytes scanned. O_NONBLOCK keeps a FIFO from hanging the validator.
      const fd = fs.openSync(scriptPath, fs.constants.O_RDONLY | (fs.constants.O_NONBLOCK || 0));
      let stats;
      let content;
      try {
        stats = fs.fstatSync(fd);
        content = stats.isFile() ? fs.readFileSync(fd, 'utf8') : '';
      } finally {
        fs.closeSync(fd);
      }

      const isExecutable = (stats.mode & 0o111) !== 0;

      if (isExecutable) {
        this.pass(`✓ Script ${script} is executable`, 2);
      } else {
        this.error(`✗ Script ${script} is not executable`, 'script-not-executable', 5);
        this.addFix('script-not-executable', { script, scriptPath });
      }


      if (content.includes('rm -rf /')) {
        this.error(`✗ Script ${script} contains dangerous command: rm -rf /`, 'hardcoded-secret', 20);
      }

      if (content.includes('eval(') || content.includes('eval ')) {
        this.warning(`⚠ Script ${script} uses eval() (potential security risk)`, null, 5);
      }
    });
  }

  checkSecrets() {
    const dangerous = [
      { pattern: /password\s*=\s*["'][^"']+["']/, msg: 'hardcoded password', fixKey: 'hardcoded-secret' },
      { pattern: /api[_-]?key\s*=\s*["'][^"']+["']/, msg: 'hardcoded API key', fixKey: 'hardcoded-secret' },
      { pattern: /secret\s*=\s*["'][^"']+["']/, msg: 'hardcoded secret', fixKey: 'hardcoded-secret' },
      { pattern: /AKIA[0-9A-Z]{16}/, msg: 'AWS access key', fixKey: 'hardcoded-secret' },
      { pattern: /-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----/, msg: 'private key', fixKey: 'hardcoded-secret' }
    ];

    const searchDirs = ['commands', 'agents', 'scripts', 'hooks'];
    let foundSecrets = false;

    searchDirs.forEach(dir => {
      const dirPath = path.join(this.pluginPath, dir);
      if (!fs.existsSync(dirPath)) return;

      const files = this.getAllFiles(dirPath);

      files.forEach(file => {
        const content = fs.readFileSync(file, 'utf8');

        dangerous.forEach(({ pattern, msg, fixKey }) => {
          if (pattern.test(content)) {
            this.error(`✗ ${path.relative(this.pluginPath, file)} contains ${msg}`, fixKey, 20);
            this.addFix(fixKey, { file: path.relative(this.pluginPath, file), type: msg });
            foundSecrets = true;
          }
        });
      });
    });

    if (!foundSecrets) {
      this.pass('✓ No hardcoded secrets detected', 10);
    }
  }

  getAllFiles(dir) {
    const files = [];
    const items = fs.readdirSync(dir, { withFileTypes: true });

    for (const item of items) {
      const fullPath = path.join(dir, item.name);
      if (item.isDirectory()) {
        files.push(...this.getAllFiles(fullPath));
      } else {
        files.push(fullPath);
      }
    }

    return files;
  }

  hasComponents() {
    const components = ['commands', 'agents', 'hooks', 'skills', 'scripts', 'mcp'];
    const found = components.filter(c => fs.existsSync(path.join(this.pluginPath, c)));

    if (found.length === 0) {
      this.error('✗ No component directories found', 'no-components', 10);
      this.addFix('no-components');
    } else {
      this.pass(`✓ Has ${found.length} component(s): ${found.join(', ')}`, 10);
    }
  }

  validate() {
    this.log('\n' + '='.repeat(60), 'cyan');
    this.log(`🔍 Validating Plugin: ${this.pluginName}`, 'bold');
    this.log('='.repeat(60) + '\n', 'cyan');

    this.log('📄 Checking Required Files...', 'blue');
    this.checkFileExists('README.md', true, 10, 'missing-readme');
    this.checkFileExists('LICENSE', true, 10, 'missing-license');
    this.checkFileExists('.claude-plugin/plugin.json', true, 10, 'missing-plugin-json');

    this.log('\n📋 Validating Configuration Files...', 'blue');
    this.validateJSON('.claude-plugin/plugin.json');

    if (fs.existsSync(path.join(this.pluginPath, '.claude-plugin/hooks.json'))) {
      this.validateJSON('.claude-plugin/hooks.json');
    }

    this.log('\n🧩 Checking Plugin Components...', 'blue');
    this.hasComponents();
    this.validateSkills();
    this.validateScripts();

    this.log('\n🔒 Security Checks...', 'blue');
    this.checkSecrets();

    this.generateReport();
  }

  generateReport() {
    this.log('\n' + '='.repeat(60), 'cyan');
    this.log('📊 VALIDATION REPORT', 'bold');
    this.log('='.repeat(60), 'cyan');

    if (this.passes.length > 0) {
      this.log(`\n✅ PASSED (${this.passes.length})`, 'green');
      this.passes.forEach(p => this.log(`  ${p}`, 'green'));
    }

    if (this.warnings.length > 0) {
      this.log(`\n⚠️  WARNINGS (${this.warnings.length})`, 'yellow');
      this.warnings.forEach(w => this.log(`  ${w.message}`, 'yellow'));
    }

    if (this.errors.length > 0) {
      this.log(`\n❌ ERRORS (${this.errors.length})`, 'red');
      this.errors.forEach(e => this.log(`  ${e.message}`, 'red'));
    }

    if (this.fixes.length > 0 && this.options.showFixes !== false) {
      this.showFixInstructions();
    }

    const percentage = this.maxScore > 0 ? Math.round((this.score / this.maxScore) * 100) : 0;
    const grade =
      percentage >= 90 ? 'A' :
      percentage >= 80 ? 'B' :
      percentage >= 70 ? 'C' :
      percentage >= 60 ? 'D' : 'F';

    this.log('\n' + '='.repeat(60), 'cyan');
    this.log(`🎯 SCORE: ${this.score}/${this.maxScore} (${percentage}%) - Grade: ${grade}`,
      grade === 'A' ? 'green' : grade === 'F' ? 'red' : 'yellow');
    this.log('='.repeat(60) + '\n', 'cyan');

    if (percentage === 100) {
      this.log('🎉 Perfect! Your plugin is ready for publication!\n', 'green');
    } else if (percentage >= 80) {
      this.log('👍 Good! Address warnings for best practices.\n', 'yellow');
    } else if (percentage >= 60) {
      this.log('⚠️  Needs improvement. Fix errors before publishing.\n', 'yellow');
    } else {
      this.log('❌ Plugin is not ready. Please fix critical errors.\n', 'red');
    }

    return { score: this.score, maxScore: this.maxScore, percentage, grade, errors: this.errors.length };
  }

  showFixInstructions() {
    this.log('\n' + '='.repeat(60), 'magenta');
    this.log('🔧 HOW TO FIX ISSUES', 'bold');
    this.log('='.repeat(60), 'magenta');

    const uniqueFixes = [...new Set(this.fixes.map(f => f.fixKey))];

    uniqueFixes.forEach((fixKey, index) => {
      const instruction = FIX_INSTRUCTIONS[fixKey];
      if (!instruction) return;

      this.log(`\n${index + 1}. ${instruction.title}`, 'bold');
      this.log(`   ${instruction.description}`, 'dim');
      this.log(`\n   WHY: ${instruction.why}`, 'yellow');
      this.log('\n   FIX:', 'cyan');
      instruction.fix.forEach(step => this.log(`   ${step}`, 'cyan'));

      if (instruction.example) {
        const example = typeof instruction.example === 'function'
          ? instruction.example(this.pluginName)
          : instruction.example;

        this.log('\n   EXAMPLE:', 'green');
        example.split('\n').slice(0, 10).forEach(line => {
          this.log(`   ${line}`, 'dim');
        });
        if (example.split('\n').length > 10) {
          this.log('   ...', 'dim');
        }
      }

      if (instruction.autofix && this.options.autofix) {
        this.log('\n   ✨ Auto-fix available! (use --fix flag)', 'green');
      }
    });

    if (this.options.autofix) {
      this.log('\n' + '='.repeat(60), 'magenta');
      this.log('Auto-fixing issues...', 'green');
      this.applyFixes();
    } else {
      this.log('\n' + '='.repeat(60), 'magenta');
      this.log('💡 Tip: Use --fix flag to automatically fix some issues', 'cyan');
      this.log('   npx claude-plugin-validator ./plugin --fix\n', 'dim');
    }
  }

  applyFixes() {
    const appliedFixes = [];

    this.fixes.forEach(({ fixKey, data }) => {
      const instruction = FIX_INSTRUCTIONS[fixKey];
      if (!instruction || !instruction.autofix) return;

      try {
        switch (fixKey) {
          case 'missing-readme':
            fs.writeFileSync(data.filePath, FIX_TEMPLATES.README);
            appliedFixes.push(`✓ Created ${data.filename}`);
            break;

          case 'missing-license':
            fs.writeFileSync(data.filePath, FIX_TEMPLATES.LICENSE);
            appliedFixes.push(`✓ Created ${data.filename}`);
            break;

          case 'missing-plugin-json':
            const pluginDir = path.dirname(data.filePath);
            if (!fs.existsSync(pluginDir)) {
              fs.mkdirSync(pluginDir, { recursive: true });
            }
            fs.writeFileSync(data.filePath, FIX_TEMPLATES.PLUGIN_JSON(this.pluginName));
            appliedFixes.push(`✓ Created ${data.filename}`);
            break;

          case 'script-not-executable':
            fs.chmodSync(data.scriptPath, 0o755);
            appliedFixes.push(`✓ Made ${data.script} executable`);
            break;
        }
      } catch (err) {
        this.log(`   ✗ Failed to fix ${fixKey}: ${err.message}`, 'red');
      }
    });

    if (appliedFixes.length > 0) {
      this.log('\n📝 Applied Fixes:', 'green');
      appliedFixes.forEach(fix => this.log(`   ${fix}`, 'green'));
      this.log('\n💡 Re-run validator to verify fixes\n', 'cyan');
    }
  }
}

// Find all installed plugins
function findInstalledPlugins() {
  const claudeDir = path.join(os.homedir(), '.claude', 'plugins');

  if (!fs.existsSync(claudeDir)) {
    return [];
  }

  const plugins = [];
  const entries = fs.readdirSync(claudeDir, { withFileTypes: true });

  entries.forEach(entry => {
    if (entry.isDirectory()) {
      const pluginPath = path.join(claudeDir, entry.name);
      if (fs.existsSync(path.join(pluginPath, '.claude-plugin/plugin.json'))) {
        plugins.push({ name: entry.name, path: pluginPath });
      }
    }
  });

  return plugins;
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const flags = {
    installed: args.includes('--installed'),
    fix: args.includes('--fix'),
    showFixes: !args.includes('--no-fixes'),
    verbose: args.includes('--verbose')
  };

  const pluginPaths = args.filter(arg => !arg.startsWith('--'));

  if (args.length === 0 || args.includes('--help')) {
    console.log(`
${colors.bold}Claude Plugin Validator v2.0${colors.reset}

${colors.cyan}Validate plugins for completeness and best practices${colors.reset}

Usage:
  ${colors.green}npx claude-plugin-validator <path-to-plugin>${colors.reset}
  ${colors.green}npx claude-plugin-validator --installed${colors.reset}
  ${colors.green}npx claude-plugin-validator --installed --fix${colors.reset}

Options:
  ${colors.yellow}--installed${colors.reset}    Validate all installed plugins in ~/.claude/plugins
  ${colors.yellow}--fix${colors.reset}           Auto-fix common issues (LICENSE, README, permissions)
  ${colors.yellow}--no-fixes${colors.reset}      Don't show fix instructions
  ${colors.yellow}--verbose${colors.reset}       Show detailed output
  ${colors.yellow}--help${colors.reset}          Show this help message

Examples:
  ${colors.dim}npx claude-plugin-validator ./my-plugin${colors.reset}
  ${colors.dim}npx claude-plugin-validator --installed${colors.reset}
  ${colors.dim}npx claude-plugin-validator ./my-plugin --fix${colors.reset}

Features:
  ✓ Required files (README.md, LICENSE, plugin.json)
  ✓ 2025 schema compliance (allowed-tools, version)
  ✓ Security checks (no hardcoded secrets)
  ✓ Script permissions (chmod +x)
  ✓ Detailed fix instructions with examples
  ✓ Auto-fix for common issues
    `);
    process.exit(0);
  }

  if (flags.installed) {
    const plugins = findInstalledPlugins();

    if (plugins.length === 0) {
      console.log(`${colors.yellow}No installed plugins found in ~/.claude/plugins${colors.reset}`);
      process.exit(0);
    }

    console.log(`${colors.cyan}Found ${plugins.length} installed plugin(s)${colors.reset}\n`);

    const results = [];

    plugins.forEach((plugin, index) => {
      const validator = new PluginValidator(plugin.path, flags);
      const result = validator.validate();
      results.push({ name: plugin.name, ...result });

      if (index < plugins.length - 1) {
        console.log('\n' + '━'.repeat(60) + '\n');
      }
    });

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log(`${colors.bold}📊 SUMMARY OF ALL PLUGINS${colors.reset}`);
    console.log('='.repeat(60) + '\n');

    results.forEach(r => {
      const color = r.grade === 'A' ? 'green' : r.grade === 'F' ? 'red' : 'yellow';
      console.log(`${colors[color]}${r.name}: ${r.percentage}% (${r.grade}) - ${r.errors} error(s)${colors.reset}`);
    });

    const avgScore = Math.round(results.reduce((sum, r) => sum + r.percentage, 0) / results.length);
    console.log(`\n${colors.cyan}Average Score: ${avgScore}%${colors.reset}\n`);

    process.exit(results.some(r => r.errors > 0) ? 1 : 0);

  } else if (pluginPaths.length > 0) {
    const pluginPath = pluginPaths[0];

    if (!fs.existsSync(pluginPath)) {
      console.error(`${colors.red}Error: Plugin directory not found: ${pluginPath}${colors.reset}`);
      process.exit(1);
    }

    const validator = new PluginValidator(pluginPath, flags);
    const result = validator.validate();

    process.exit(result.errors > 0 ? 1 : 0);

  } else {
    console.error(`${colors.red}Error: No plugin path specified${colors.reset}`);
    console.log(`Run ${colors.cyan}npx claude-plugin-validator --help${colors.reset} for usage`);
    process.exit(1);
  }
}

module.exports = PluginValidator;
