---
title: "Install Your First Plugin"
description: "Step-by-step guide to browsing the Tons of Skills marketplace, installing a Claude Code plugin, using its skills and commands, and removing plugins you no longer need."
section: "getting-started"
order: 2
keywords: ["install Claude Code plugin", "Claude Code marketplace", "browse plugins", "ccpi install", "plugin commands", "uninstall plugin"]
officialLinks:
  - title: "Claude Code Plugins Documentation"
    url: "https://code.claude.com/docs/en/plugins"
  - title: "Claude Code Slash Commands"
    url: "https://code.claude.com/docs/en/slash-commands"
relatedDocs:
  - "getting-started/installation"
  - "getting-started/first-skill"
  - "concepts/plugins"
---

## Overview

You have Claude Code installed, the `ccpi` CLI is working, and the Tons of Skills marketplace is connected. Now it is time to install a plugin, see what it adds to your Claude Code session, and learn how to manage plugins over time.

This guide uses a concrete example -- the `code-reviewer` plugin -- but the workflow applies to any of the 418 plugins in the marketplace.

## Step 1: Browse the marketplace

There are three ways to find the plugin you want.

### Browse on the web

Visit [tonsofskills.com/explore](/explore) in your browser. The explore page lets you:

- **Search** by name, keyword, or description.
- **Filter** by category (DevOps, Security, Testing, AI/ML, Database, and more).
- **Sort** by name, popularity, or date added.
- **View details** including skill count, command list, agent roster, and full README.

Each plugin card links to a dedicated page with installation instructions, a skill breakdown, and related plugins.

You can also use the [Skills catalog](/skills) to search across all 2,834 individual skills if you know exactly what capability you need but not which plugin provides it.

### Search from the CLI

Use `ccpi search` to find plugins without leaving your terminal:

```bash
ccpi search code-review
```

The search checks plugin names, descriptions, and keywords. Results include the plugin name, version, and a short description.

### List everything

To see the full catalog grouped by category:

```bash
ccpi list --all
```

This prints all 418 plugins organized into categories such as `automation`, `code-analysis`, `devops`, `security`, `testing`, and more.

## Step 2: Review the plugin before installing

Before installing a plugin, check what it provides. On the web, navigate to the plugin's detail page. For example:

```
https://tonsofskills.com/plugins/code-reviewer
```

The detail page shows:

| Section | What you learn |
|---|---|
| Description | What the plugin does and when to use it |
| Skills | Auto-activating SKILL.md files -- Claude uses these automatically when relevant |
| Commands | Slash commands you can invoke manually (e.g., `/review`) |
| Agents | Autonomous sub-agents the plugin defines |
| README | Full documentation, examples, and configuration options |
| Metadata | Version, author, license, keywords |

Understanding the difference between skills, commands, and agents is important:

- **Skills** activate automatically. When Claude detects that a skill's trigger conditions match the current context, it loads the skill's instructions without you doing anything.
- **Commands** are manual. You type a slash command like `/review` to invoke them explicitly.
- **Agents** are autonomous sub-agents that can be delegated to via the `Task` tool. They run in their own context with their own instruction set.

## Step 3: Install the plugin

There are two paths to installation. Both achieve the same result.

### Path A: Guided install via ccpi (recommended for first-timers)

Run the install command from your regular terminal:

```bash
ccpi install code-reviewer
```

The CLI confirms the plugin exists in the marketplace catalog and outputs the exact slash command to run:

```
Found: code-reviewer v1.2.0
  Automated code review with quality scoring and actionable feedback

Installation Command:

Open Claude Code and run:

   /plugin install code-reviewer@claude-code-plugins-plus --project

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scope explanation:
  --global  : Available in all projects
  --project : Only available in current project
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Copy the `/plugin install` line and paste it into your Claude Code session.

### Path B: Direct install from Claude Code

If you already know the plugin name, skip the CLI step and run the command directly inside Claude Code:

```bash
/plugin install code-reviewer@claude-code-plugins-plus --project
```

Replace `--project` with `--global` if you want the plugin available in every project, not just the current one.

### What happens during installation

When you run `/plugin install`, Claude Code:

1. Downloads the plugin from the marketplace repository.
2. Validates the `plugin.json` manifest for required fields (`name`, `version`, `description`, `author`).
3. Indexes all skills (`skills/*/SKILL.md`), commands (`commands/*.md`), and agents (`agents/*.md`).
4. Makes everything immediately available in the current session.

No restart is needed. Skills, commands, and agents are live the moment installation completes.

## Step 4: Verify the plugin is installed

### From your terminal

```bash
ccpi list
```

This shows all installed plugins with their version and install scope (global or project-local):

```
Installed Plugins:

  code-reviewer v1.2.0
    Automated code review with quality scoring and actionable feedback
    Location: local

Total: 1 plugin
```

### From Claude Code

Inside a Claude Code session, ask Claude directly:

```
What plugins do I have installed?
```

Or use the built-in command:

```bash
/plugin list
```

## Step 5: Use the plugin

Now that the plugin is installed, put it to work.

### Using skills (automatic activation)

Skills activate without any action on your part. If the `code-reviewer` plugin includes a skill that triggers on code review contexts, Claude will use it when you ask questions like:

```
Review the changes in src/auth.ts for security issues.
```

Claude detects that the request matches the skill's trigger description, loads the skill's instructions, and applies its specialized review methodology. You will see the skill name referenced in Claude's response when it activates.

### Using commands (manual invocation)

Commands are invoked with the `/` prefix. Check which commands the plugin added:

```bash
/help
```

This lists all available slash commands, including those from installed plugins. A code reviewer plugin might add:

```
/review        -- Run a comprehensive code review
/review-pr     -- Review a pull request
```

Invoke a command:

```bash
/review src/auth.ts
```

Commands can accept arguments. The `argument-hint` field in the command frontmatter tells Claude Code what to show in autocomplete suggestions.

### Using agents (delegated sub-tasks)

If the plugin defines agents, Claude can delegate sub-tasks to them using the `Task` tool. Agents run in their own isolated context with a defined set of capabilities and turn limits. You do not invoke agents directly -- Claude decides when to delegate based on the agent's description and the current task.

## Step 6: Explore more plugins

Once you are comfortable with the installation workflow, try a few more plugins to see how different categories work.

### Recommended starter plugins

| Plugin | Category | What it does |
|---|---|---|
| `debugger` | debugging | Systematic debugging with root cause analysis |
| `test-automator` | testing | Generate and manage test suites |
| `security-auditor` | security | OWASP-based security scanning |
| `terraform-specialist` | devops | Infrastructure-as-code generation and review |
| `database-optimizer` | database | Query optimization and index recommendations |
| `ui-ux-designer` | frontend | Design system generation and accessibility checks |

### Install a curated pack

If you want a set of related plugins, install a pack:

```bash
ccpi install --pack devops
```

This outputs install commands for all plugins in the devops pack: `terraform-specialist`, `kubernetes-architect`, `deployment-engineer`, `devops-troubleshooter`, `hybrid-cloud-architect`, and `docker-pro`.

Available packs:

| Pack | Plugins | Focus area |
|---|---|---|
| `devops` | 6 | Infrastructure and deployment |
| `security` | 4 | Application and code security |
| `api` | 3 | API design and backend architecture |
| `ai-ml` | 4 | Machine learning and AI engineering |
| `frontend` | 4 | UI development and mobile |
| `backend` | 10 | Language-specific backend expertise |
| `database` | 4 | Database administration and optimization |
| `testing` | 4 | Testing, debugging, and performance |

## Uninstalling plugins

If a plugin is no longer needed, remove it from inside Claude Code:

```bash
/plugin uninstall code-reviewer@claude-code-plugins-plus
```

The plugin's skills, commands, and agents are immediately removed from the session. No restart required.

### When to uninstall

- **Project scope cleanup** -- remove plugins that are irrelevant to the current project to keep Claude's context focused.
- **Before upgrading** -- the current upgrade workflow requires uninstalling the old version before installing the new one. See [ccpi upgrade](/docs/getting-started/cli-reference) for details.
- **Troubleshooting** -- if a plugin causes unexpected behavior, uninstall it and run `ccpi doctor` to verify system health.

## Managing plugins across projects

Plugins installed with `--project` scope only load when Claude Code is running in that specific project directory. This is a feature, not a limitation -- it keeps your skill surface area relevant to the task at hand.

For plugins you want everywhere, use `--global`:

```bash
/plugin install debugger@claude-code-plugins-plus --global
```

A common pattern is to install general-purpose plugins globally and domain-specific plugins per project:

| Scope | Example plugins | Rationale |
|---|---|---|
| Global | `debugger`, `code-reviewer`, `test-automator` | Useful in every codebase |
| Project | `terraform-specialist`, `fastapi-pro`, `flutter-expert` | Relevant only to specific tech stacks |

## Troubleshooting

### Plugin installed but commands not showing

Make sure you ran the `/plugin install` command inside Claude Code, not in your regular terminal. The `/plugin` prefix only works in a Claude Code session.

If the command was run correctly but commands still do not appear, try:

```bash
/plugin list
```

If the plugin is listed but its commands are missing, the command files may have invalid frontmatter. Run validation:

```bash
ccpi validate
```

### "Plugin not found in marketplace"

The plugin name is case-sensitive and must match exactly. Use `ccpi search` with a partial name to find the correct spelling:

```bash
ccpi search reviewer
```

If the marketplace catalog is stale, refresh it:

```bash
ccpi marketplace-add
```

### Skills not activating

Skills activate based on their `description` field in SKILL.md frontmatter. If Claude is not picking up a skill, it may be because the current request does not match the skill's trigger conditions. Try rephrasing your request to more closely match the skill's described use case.

You can also check which skills are available by asking Claude:

```
What skills do you have from installed plugins?
```

## Next steps

- [Your First Agent Skill](/docs/getting-started/first-skill) -- learn how skills work and build one from scratch.
- [ccpi CLI Quick Reference](/docs/getting-started/cli-reference) -- every command at a glance.
- [Browse all skills](/skills) -- search the full catalog of 2,834 skills.
- [Explore plugins](/explore) -- filter, compare, and discover plugins on the web.
