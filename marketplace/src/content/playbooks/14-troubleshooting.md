---
title: "Troubleshooting Guide"
description: "Debug common Claude Code plugin issues. Skill activation failures, validation errors, build problems, and performance issues with step-by-step fixes."
category: "Operations"
wordCount: 2000
readTime: 10
featured: false
order: 14
tags: ["troubleshooting", "debugging", "errors", "fix", "support"]
prerequisites: []
relatedPlaybooks: ["12-beginner-onboarding", "05-incident-debugging"]
---

<p>When things go wrong with Claude Code plugins, this guide helps you diagnose and fix the most common issues quickly. Each section covers a specific problem with symptoms, root causes, and step-by-step fixes.</p>

<h2>Issue 1: Skill Doesn't Activate</h2>

<h3>Symptoms</h3>

<ul>
<li>You mention a topic the skill should handle, but Claude doesn't use it</li>
<li>The skill doesn't appear in <code>/skills</code> output</li>
<li>Slash command for the skill doesn't work</li>
</ul>

<h3>Root Causes & Fixes</h3>

<h3>1. Missing trigger phrases in description</h3>

<p>Claude uses the <code>description</code> field to decide when to activate a skill. If it lacks clear trigger language, Claude won't know when to use it.</p>

<pre><code class="language-yaml"># Bad: vague description
description: "Helps with Docker stuff"

# Good: clear trigger phrases
description: |
  Use when the user wants to harden a Dockerfile, audit container
  security, or optimize Docker image size. Activate for any Docker
  or container-related security questions.</code></pre>

<h3>2. <code>user-invocable</code> is set to false</h3>

<p>If a skill has <code>user-invocable: false</code> in its frontmatter, it won't appear in the <code>/</code> menu and can't be triggered directly:</p>

<pre><code class="language-yaml"># This hides the skill from the / menu
user-invocable: false

# Remove this line or set to true to make the skill available
user-invocable: true</code></pre>

<h3>3. Plugin not installed or loaded</h3>

<pre><code class="language-bash"># Check if the plugin is installed
/plugins

# Reinstall if missing
/plugin marketplace add jeremylongshore/claude-code-plugins</code></pre>

<h3>4. Frontmatter parsing error</h3>

<p>Invalid YAML in the frontmatter silently prevents skill loading. Validate the SKILL.md:</p>

<pre><code class="language-bash"># Validate a specific skill file
python3 scripts/validate-skills-schema.py --skills-only --verbose plugins/category/plugin-name/skills/skill-name/SKILL.md</code></pre>

<hr>

<h2>Issue 2: Validation Errors</h2>

<h3>Symptoms</h3>

<ul>
<li>Enterprise validation returns a low score</li>
<li>CI fails on the validation step</li>
<li>Specific field errors in validation output</li>
</ul>

<h3>Diagnosis</h3>

<pre><code class="language-bash"># Run enterprise validation with verbose output
python3 scripts/validate-skills-schema.py --enterprise --verbose path/to/SKILL.md

# Check for specific field issues
python3 scripts/validate-skills-schema.py --enterprise path/to/SKILL.md 2>&1 | grep "FAIL\|ERROR\|WARN"</code></pre>

<h3>Common Validation Failures</h3>

<table>
<thead>
<tr>
<th>Error</th>
<th>Cause</th>
<th>Fix</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>missing required field: name</code></td>
<td>Frontmatter missing <code>name</code></td>
<td>Add <code>name: skill-name</code> to frontmatter</td>
</tr>
<tr>
<td><code>missing required field: description</code></td>
<td>No description provided</td>
<td>Add multi-line description with trigger phrases</td>
</tr>
<tr>
<td><code>missing required field: allowed-tools</code></td>
<td>No tool allowlist</td>
<td>Add <code>allowed-tools: Read, Glob, Grep</code></td>
</tr>
<tr>
<td><code>invalid tool: bash</code></td>
<td>Lowercase or unscoped Bash</td>
<td>Use <code>Bash(npm:*)</code> or <code>Bash(git:*)</code></td>
</tr>
<tr>
<td><code>unscoped Bash detected</code></td>
<td>Bare <code>Bash</code> in allowed-tools</td>
<td>Scope it: <code>Bash(command:pattern)</code></td>
</tr>
<tr>
<td><code>description too short</code></td>
<td>Description under minimum length</td>
<td>Expand with use cases and trigger phrases</td>
</tr>
</tbody>
</table>

<h3>Quick Fix Template</h3>

<p>If your skill is missing multiple required fields, use this template as a starting point:</p>

<pre><code class="language-yaml">---
name: my-skill-name
description: |
  Use when the user needs help with [specific task].
  Activate for questions about [topic area].
allowed-tools: Read, Write, Edit, Glob, Grep
version: 1.0.0
author: Your Name &lt;email@example.com&gt;
license: MIT
tags: [relevant, tags, here]
---</code></pre>

<hr>

<h2>Issue 3: Plugin Not Found</h2>

<h3>Symptoms</h3>

<ul>
<li><code>/plugins</code> doesn't list your plugin</li>
<li>Install command fails with "plugin not found"</li>
<li>Skills from the plugin don't appear</li>
</ul>

<h3>Fixes</h3>

<h3>1. Verify plugin.json exists</h3>

<pre><code class="language-bash"># Check for the required plugin manifest
ls -la plugins/category/plugin-name/.claude-plugin/plugin.json

# If missing, create it with required fields
cat > plugins/category/plugin-name/.claude-plugin/plugin.json << 'EOF'
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": "Your Name <email@example.com>"
}
EOF</code></pre>

<h3>2. Check marketplace catalog entry</h3>

<p>The plugin must be registered in the marketplace catalog:</p>

<pre><code class="language-bash"># Search for your plugin in the catalog
grep "plugin-name" .claude-plugin/marketplace.extended.json

# If not found, add an entry to marketplace.extended.json
# Then regenerate the CLI catalog:
pnpm run sync-marketplace</code></pre>

<h3>3. Verify plugin.json only has allowed fields</h3>

<p>CI rejects <code>plugin.json</code> files with extra fields. Only these fields are allowed:</p>

<pre><code class="language-json">{
  "name": "...",
  "version": "...",
  "description": "...",
  "author": "...",
  "repository": "...",
  "homepage": "...",
  "license": "...",
  "keywords": []
}</code></pre>

<hr>

<h2>Issue 4: Build Fails</h2>

<h3>Symptoms</h3>

<ul>
<li><code>pnpm install</code> or <code>pnpm build</code> fails</li>
<li>Marketplace build errors</li>
<li>CI build job fails</li>
</ul>

<h3>Fixes</h3>

<h3>1. Check package manager</h3>

<p>The repository enforces strict package manager policy. Using the wrong one will fail:</p>

<pre><code class="language-bash"># Root and all packages: use pnpm
pnpm install
pnpm build

# Marketplace directory ONLY: use npm
cd marketplace/
npm install
npm run build

# NEVER use npm at root or pnpm in marketplace/</code></pre>

<h3>2. Clean install</h3>

<pre><code class="language-bash"># Remove all node_modules and reinstall
rm -rf node_modules packages/*/node_modules plugins/mcp/*/node_modules
pnpm install

# For marketplace
cd marketplace/
rm -rf node_modules
npm install</code></pre>

<h3>3. Check Node.js version</h3>

<pre><code class="language-bash"># Repository builds require Node.js 22.12+
node --version

# If outdated, update via nvm
nvm install 22
nvm use 22</code></pre>

<h3>4. MCP plugin build issues</h3>

<pre><code class="language-bash"># MCP plugins need individual builds
cd plugins/mcp/plugin-name/
pnpm build

# Ensure dist/index.js is executable
chmod +x dist/index.js

# Verify shebang line exists
head -1 dist/index.js
# Should show: #!/usr/bin/env node</code></pre>

<hr>

<h2>Issue 5: Performance Issues</h2>

<h3>Symptoms</h3>

<ul>
<li>Build takes longer than expected</li>
<li>Performance budget check fails in CI</li>
<li>Pages load slowly</li>
</ul>

<h3>Diagnosis</h3>

<pre><code class="language-bash"># Run performance budget checks
node scripts/check-performance.mjs

# Benchmark CLI operations
bash scripts/benchmark-cli.sh

# Check bundle sizes
cd marketplace/
npm run build
du -sh dist/</code></pre>

<h3>Common Performance Fixes</h3>

<table>
<thead>
<tr>
<th>Problem</th>
<th>Cause</th>
<th>Fix</th>
</tr>
</thead>
<tbody>
<tr>
<td>Bundle too large</td>
<td>Large inline content or images</td>
<td>Move assets to external hosting, compress images</td>
</tr>
<tr>
<td>Build too slow</td>
<td>Unoptimized data processing</td>
<td>Check <code>discover-skills.mjs</code> and <code>sync-catalog.mjs</code></td>
</tr>
<tr>
<td>Route count wrong</td>
<td>Missing or orphaned plugin pages</td>
<td>Run <code>pnpm run sync-marketplace</code>, check catalog</td>
</tr>
<tr>
<td>Page too large</td>
<td>Single page exceeds 550KB gzipped</td>
<td>Split content, paginate, or lazy-load sections</td>
</tr>
</tbody>
</table>

<h3>Performance Budget Reference</h3>

<pre><code class="language-bash"># Current limits (enforced by CI)
Total bundle (gzipped):    19.5 MB
Largest file (gzipped):    550 KB
Build time:                < 10 seconds
Route count:               1,600 - 2,000</code></pre>

<hr>

<h2>Issue 6: SaaS Pack Missing Skills</h2>

<h3>Symptoms</h3>

<ul>
<li>A SaaS pack has fewer skills than expected</li>
<li>Skills listed in TRACKER.csv aren't present as files</li>
<li>Pack validation reports missing skills</li>
</ul>

<h3>Diagnosis</h3>

<pre><code class="language-bash"># Check the tracker for expected skills
cat plugins/saas-packs/pack-name/TRACKER.csv

# Count actual skill directories
ls -d plugins/saas-packs/pack-name/skills/*/

# Compare expected vs actual
diff <(grep -o '"[^"]*"' plugins/saas-packs/pack-name/TRACKER.csv | sort) \
     <(ls -d plugins/saas-packs/pack-name/skills/*/ | xargs -I{} basename {} | sort)</code></pre>

<h3>Regenerating Missing Skills</h3>

<p>If skills are listed in the tracker but missing from the filesystem, regenerate them:</p>

<pre><code class="language-bash"># Regenerate the pack using the generator script
python3 scripts/generate-pack.py --pack pack-name --regenerate-missing

# Validate the regenerated skills
python3 scripts/validate-skills-schema.py --enterprise plugins/saas-packs/pack-name/</code></pre>

<h3>Manual Skill Creation</h3>

<p>If the generator isn't available, create skills manually following the pack's existing structure:</p>

<pre><code class="language-bash"># Use an existing skill as a template
cp -r plugins/saas-packs/pack-name/skills/existing-skill/ \
      plugins/saas-packs/pack-name/skills/new-skill/

# Edit the SKILL.md with the correct content
# Then validate
python3 scripts/validate-skills-schema.py --enterprise \
  plugins/saas-packs/pack-name/skills/new-skill/SKILL.md</code></pre>

<hr>

<h2>Getting Help</h2>

<h3>Self-Service Resources</h3>

<ul>
<li><strong>Marketplace</strong>: <a href="https://tonsofskills.com">tonsofskills.com</a> - Browse plugins, skills, and documentation</li>
<li><strong>Playbooks</strong>: <a href="https://tonsofskills.com/playbooks">tonsofskills.com/playbooks</a> - In-depth guides for specific topics</li>
<li><strong>Plugin validation</strong>: Run <code>python3 scripts/validate-skills-schema.py --enterprise --verbose</code> for detailed diagnostics</li>
</ul>

<h3>Community Support</h3>

<ul>
<li><strong>GitHub Issues</strong>: <a href="https://github.com/jeremylongshore/claude-code-plugins/issues">Report bugs and request features</a></li>
<li><strong>Discussions</strong>: <a href="https://github.com/jeremylongshore/claude-code-plugins/discussions">Ask questions and share tips</a></li>
</ul>

<h3>Pro Support</h3>

<p>For production deployments and enterprise needs:</p>

<ul>
<li><strong>Intent Solutions</strong>: Professional support for Claude Code plugin deployments</li>
<li><strong>Custom plugin development</strong>: Bespoke skills and SaaS packs for your tech stack</li>
<li><strong>Training</strong>: Team onboarding and best practices workshops</li>
</ul>

<h3>Diagnostic Checklist</h3>

<p>When reporting issues, include this information for faster resolution:</p>

<pre><code class="language-bash"># Gather diagnostic info
echo "=== Environment ==="
node --version
pnpm --version
claude --version

echo "=== Plugin Status ==="
ls .claude-plugin/

echo "=== Validation ==="
python3 scripts/validate-skills-schema.py --enterprise --verbose 2>&1 | tail -20

echo "=== Recent Errors ==="
# Include any error messages from your terminal</code></pre>

<hr>

<p><strong>Last Updated</strong>: 2026-03-21</p>
<p><strong>Author</strong>: Jeremy Longshore</p>
<p><strong>Related Playbooks</strong>: <a href="/playbooks/12-beginner-onboarding/">Beginner Onboarding</a>, <a href="/playbooks/05-incident-debugging/">Incident Debugging</a></p>
