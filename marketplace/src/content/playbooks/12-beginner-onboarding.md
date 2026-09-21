---
title: "Beginner Onboarding"
description: "Complete getting-started guide: install plugins, run your first skill, customize your setup. From zero to productive in 15 minutes."
category: "Getting Started"
wordCount: 2200
readTime: 11
featured: true
order: 12
tags: ["onboarding", "getting-started", "installation", "beginner", "quickstart"]
prerequisites: []
relatedPlaybooks: ["13-production-setup", "14-troubleshooting"]
---

<p>Go from zero to productive with Claude Code plugins in 15 minutes. This playbook walks you through installation, running your first skill, exploring the ecosystem, and customizing your setup for maximum productivity.</p>

<h2>Step 1: Install Claude Code</h2>

<h3>Prerequisites</h3>

<ul>
<li>Node.js 18+ installed</li>
<li>A terminal (macOS Terminal, iTerm2, Windows Terminal, or any Linux terminal)</li>
<li>An Anthropic API key or Claude Pro/Team subscription</li>
</ul>

<h3>Install Claude Code CLI</h3>

<p>Install Claude Code globally via npm:</p>

<pre><code class="language-bash"># Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify installation
claude --version</code></pre>

<p>If you see a version number, you're ready to go. Visit the <a href="https://code.claude.com/docs">official Claude Code documentation</a> for detailed setup instructions, including authentication and configuration.</p>

<h3>First Launch</h3>

<pre><code class="language-bash"># Start Claude Code in any project directory
cd your-project/
claude</code></pre>

<p>Claude Code will start an interactive session. You can now chat with Claude about your codebase, run commands, and use plugins.</p>

<hr>

<h2>Step 2: Install Your First Plugin</h2>

<h3>The Tons of Skills Marketplace</h3>

<p>The <a href="https://tonsofskills.com">Tons of Skills marketplace</a> hosts 346+ plugins with 1,900+ skills covering everything from code review to DevOps to SaaS integrations.</p>

<h3>Install the Marketplace Plugin</h3>

<p>Run this command inside a Claude Code session:</p>

<pre><code class="language-bash">/plugin marketplace add jeremylongshore/claude-code-plugins</code></pre>

<p>This installs the full marketplace plugin collection. You'll see a confirmation message listing the installed plugins and available skills.</p>

<h3>Verify Installation</h3>

<pre><code class="language-bash"># List installed plugins
/plugins

# You should see the marketplace plugins listed with their versions</code></pre>

<p><strong>Tip</strong>: If the install fails, check your internet connection and ensure you have the latest version of Claude Code. See the <a href="/playbooks/14-troubleshooting/">Troubleshooting Guide</a> for common fixes.</p>

<hr>

<h2>Step 3: Explore Available Skills</h2>

<h3>Browse Skills in the CLI</h3>

<p>Use the <code>/skills</code> command to see all available skills in your current session:</p>

<pre><code class="language-bash"># List all available skills
/skills

# You'll see skills organized by plugin, with descriptions
# showing when each skill activates</code></pre>

<h3>Browse Online</h3>

<p>For a richer browsing experience, visit <a href="https://tonsofskills.com/explore">tonsofskills.com/explore</a>. The web interface offers:</p>

<ul>
<li><strong>Search</strong>: Find skills by keyword, category, or use case</li>
<li><strong>Filters</strong>: Filter by category (AI/ML, DevOps, Security, etc.)</li>
<li><strong>Skill details</strong>: See full descriptions, allowed tools, and usage examples</li>
<li><strong>Install commands</strong>: Copy-paste install commands directly</li>
</ul>

<h3>Skill Categories</h3>

<table>
<thead>
<tr>
<th>Category</th>
<th>Skills</th>
<th>Example Use Cases</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>AI/ML</strong></td>
<td>50+</td>
<td>Model validation, prompt engineering, Vertex AI</td>
</tr>
<tr>
<td><strong>DevOps</strong></td>
<td>40+</td>
<td>CI/CD pipelines, Docker, Kubernetes, Terraform</td>
</tr>
<tr>
<td><strong>Security</strong></td>
<td>30+</td>
<td>Code auditing, dependency scanning, OWASP checks</td>
</tr>
<tr>
<td><strong>SaaS Packs</strong></td>
<td>200+</td>
<td>Supabase, Stripe, Retell AI, Firebase integrations</td>
</tr>
<tr>
<td><strong>Code Quality</strong></td>
<td>60+</td>
<td>Linting, formatting, code review, test generation</td>
</tr>
</tbody>
</table>

<hr>

<h2>Step 4: Run a Skill</h2>

<h3>Your First Skill Run</h3>

<p>Let's run a practical skill to validate a SKILL.md file. This is a great first skill because it gives immediate, actionable feedback:</p>

<pre><code class="language-bash"># Run the skill validator on any SKILL.md file
/validate-skillmd path/to/SKILL.md</code></pre>

<p>The validator will check your skill file against the specification and report any issues with frontmatter fields, allowed tools, or content structure.</p>

<h3>How Skills Activate</h3>

<p>Skills in Claude Code activate in two ways:</p>

<ul>
<li><strong>Slash commands</strong>: Explicitly invoke with <code>/skill-name</code> (e.g., <code>/validate-skillmd</code>)</li>
<li><strong>Auto-activation</strong>: Skills activate automatically when Claude detects a relevant context based on the skill's <code>description</code> field</li>
</ul>

<h3>Example: Running More Skills</h3>

<pre><code class="language-bash"># Code review skill
/code-review src/main.ts

# Generate tests
/test-gen src/utils.ts

# Check for security issues
/security-audit</code></pre>

<p><strong>Important</strong>: Each skill specifies which tools it can use via the <code>allowed-tools</code> frontmatter field. This is a security feature that limits what actions a skill can perform.</p>

<hr>

<h2>Step 5: Install a SaaS Pack</h2>

<h3>What Are SaaS Packs?</h3>

<p>SaaS packs are curated collections of skills for specific platforms. Each pack includes 20-30 skills covering installation, configuration, troubleshooting, and advanced usage patterns.</p>

<h3>Install the Supabase Pack</h3>

<pre><code class="language-bash"># Install a SaaS pack
/plugin marketplace add jeremylongshore/claude-code-plugins --path plugins/saas-packs/supabase-pack</code></pre>

<p>Once installed, you get instant access to Supabase-specific skills:</p>

<ul>
<li><strong>supabase-install-auth</strong>: Set up authentication with Supabase</li>
<li><strong>supabase-hello-world</strong>: Quick start project scaffold</li>
<li><strong>supabase-common-errors</strong>: Troubleshoot common Supabase issues</li>
<li><strong>supabase-security-basics</strong>: Row-level security and best practices</li>
<li><strong>supabase-performance-tuning</strong>: Optimize queries and indexes</li>
</ul>

<h3>Available SaaS Packs</h3>

<table>
<thead>
<tr>
<th>Pack</th>
<th>Skills</th>
<th>Platform</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>supabase-pack</strong></td>
<td>30</td>
<td>Supabase (database, auth, storage)</td>
</tr>
<tr>
<td><strong>stripe-pack</strong></td>
<td>30</td>
<td>Stripe (payments, subscriptions)</td>
</tr>
<tr>
<td><strong>retellai-pack</strong></td>
<td>30</td>
<td>Retell AI (voice agents)</td>
</tr>
<tr>
<td><strong>firebase-pack</strong></td>
<td>30</td>
<td>Firebase (hosting, Firestore, auth)</td>
</tr>
</tbody>
</table>

<p>Browse all packs at <a href="https://tonsofskills.com/explore">tonsofskills.com/explore</a> and filter by the SaaS Packs category.</p>

<hr>

<h2>Step 6: Customize Your Setup</h2>

<h3>Model Preferences</h3>

<p>Some skills support model overrides via the <code>model</code> frontmatter field. You can prefer faster models for simple tasks or more capable models for complex analysis:</p>

<pre><code class="language-yaml"># In a skill's SKILL.md frontmatter
model: sonnet    # Fast, cost-effective
model: opus      # Most capable, for complex tasks
model: haiku     # Fastest, for simple lookups</code></pre>

<h3>Add More Plugins</h3>

<p>Install individual plugins for specific needs:</p>

<pre><code class="language-bash"># Install a specific plugin by path
/plugin marketplace add jeremylongshore/claude-code-plugins --path plugins/ai-ml/vertex-ai-validator

# Install from a different repository
/plugin add github-username/plugin-repo</code></pre>

<h3>Project-Level Configuration</h3>

<p>Create a <code>.claude/plugins.json</code> in your project root to define which plugins load for that project:</p>

<pre><code class="language-json">{
  "plugins": [
    "jeremylongshore/claude-code-plugins/plugins/devops/docker-hardener",
    "jeremylongshore/claude-code-plugins/plugins/security/owasp-top-10"
  ]
}</code></pre>

<p>This ensures consistent plugin sets across your team without requiring each developer to install manually.</p>

<h3>Explore Commands and Agents</h3>

<p>Beyond skills, plugins can include:</p>

<ul>
<li><strong>Commands</strong> (<code>commands/*.md</code>): Slash commands for specific actions</li>
<li><strong>Agents</strong> (<code>agents/*.md</code>): Specialized AI agents with custom capabilities and tool restrictions</li>
</ul>

<pre><code class="language-bash"># List available commands
/help

# List available agents (if your plugins include them)
/agents</code></pre>

<hr>

<h2>Tips for Getting the Most Out of Plugins</h2>

<h3>Essential Commands</h3>

<table>
<thead>
<tr>
<th>Command</th>
<th>What It Does</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>/help</code></td>
<td>List all available commands</td>
</tr>
<tr>
<td><code>/skills</code></td>
<td>List all active skills</td>
</tr>
<tr>
<td><code>/plugins</code></td>
<td>List installed plugins</td>
</tr>
<tr>
<td><code>/plugin marketplace add ...</code></td>
<td>Install a plugin</td>
</tr>
</tbody>
</table>

<h3>Best Practices</h3>

<ul>
<li><strong>Start small</strong>: Install one or two plugins first, learn their skills, then expand</li>
<li><strong>Read skill descriptions</strong>: The <code>description</code> field tells you exactly when a skill activates</li>
<li><strong>Check allowed-tools</strong>: Know what tools a skill can use before running it</li>
<li><strong>Use auto-activation</strong>: Write naturally and let skills activate when relevant, rather than always using slash commands</li>
<li><strong>Stay updated</strong>: Check <a href="https://tonsofskills.com">tonsofskills.com</a> for new plugins and updates</li>
</ul>

<h3>Next Steps</h3>

<ul>
<li>Set up <a href="/playbooks/13-production-setup/">production validation and CI/CD integration</a></li>
<li>Learn how to <a href="/playbooks/14-troubleshooting/">troubleshoot common issues</a></li>
<li>Explore the <a href="https://tonsofskills.com/skills">full skills catalog</a> for your tech stack</li>
</ul>

<hr>

<p><strong>Last Updated</strong>: 2026-03-21</p>
<p><strong>Author</strong>: Jeremy Longshore</p>
<p><strong>Related Playbooks</strong>: <a href="/playbooks/13-production-setup/">Production Setup</a>, <a href="/playbooks/14-troubleshooting/">Troubleshooting Guide</a></p>
