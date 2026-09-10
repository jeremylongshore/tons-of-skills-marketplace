# Google Cloud Agent SDK

Claude Code guidance for building and operating Google ADK applications with
Google's maintained [`agents-cli`](https://github.com/google/agents-cli).

## What This Plugin Does

- Activates a repo-aware Google ADK lifecycle skill.
- Provides `/create-agent` as a Google application-scaffolding command.
- Covers local development, evaluations, Agent Runtime, Cloud Run, GKE, Gemini
  Enterprise publication, observability, and Agent Starter Pack migration.
- Uses current official documentation and installed CLI help instead of cached
  template, model, region, or pricing claims.

## Two Different Kinds of Agent

The generic command name predates Claude Code's richer custom-subagent surface.
The two workflows are not interchangeable:

| Request | Use |
|---|---|
| Create a Google ADK application that runs locally or on Google Cloud | `/create-agent` or `google-cloud-agent-sdk-master` |
| Create a Claude Code `agents/*.md` definition | `/agent-creator` from the skill-creator plugin |

`/create-agent` is retained for compatibility, but its first step now enforces
this scope check.

## Current Google Toolchain

Google placed Agent Starter Pack in maintenance mode and moved active
development to `google/agents-cli`. Start new projects with:

```bash
uvx google-agents-cli setup
agents-cli create PROJECT_NAME
```

Or install Google's upstream skills without the CLI setup:

```bash
npx skills add google/agents-cli
```

Existing projects can use the maintained scaffold workflow:

```bash
agents-cli scaffold enhance
agents-cli scaffold upgrade
```

Always inspect `agents-cli --help` and the relevant subcommand help before
constructing flags. The project evolves independently of this plugin.

## Install This Plugin

```bash
ccpi install 004-jeremy-google-cloud-agent-sdk
```

Or in Claude Code:

```text
/plugin install 004-jeremy-google-cloud-agent-sdk@claude-code-plugins-plus
```

## Local Lifecycle

The generated project owns its exact configuration and checks. Current command
families include:

```bash
agents-cli install
agents-cli lint
agents-cli run "smoke test"
agents-cli eval run
```

Do not deploy a project whose local smoke test or evaluation lane fails.

## Cloud Lifecycle

Current Google guidance covers Agent Runtime, Cloud Run, and GKE. Resolve the
installed release's targets from:

```bash
agents-cli deploy --help
agents-cli infra --help
```

Gemini Enterprise registration is a separate action:

```bash
agents-cli publish gemini-enterprise --help
```

Before provisioning or publishing, review the exact Google Cloud project,
region, IAM identity, secrets path, network exposure, quota, rollback, and
current service pricing. The plugin deliberately does not embed fixed prices.

## Safety

- Never store API keys, service-account JSON, or access tokens in source control.
- Never install tools, authenticate, scaffold over files, provision, deploy, or
  publish without showing the exact action and target first.
- Keep cloud endpoints authenticated unless the user explicitly approves public
  exposure.
- Treat security as a property of the configured IAM, network, data, secrets,
  tools, and runtime; avoid absolute "secure by default" claims.

## Contents

```text
commands/create-agent.md
skills/google-cloud-agent-sdk-master/SKILL.md
skills/google-cloud-agent-sdk-master/references/
```

## Primary Sources

- [Google agents-cli](https://github.com/google/agents-cli)
- [agents-cli documentation](https://google.github.io/agents-cli/)
- [Agent Starter Pack migration](https://google.github.io/agents-cli/reference/from-agent-starter-pack/)
- [Google ADK documentation](https://google.github.io/adk-docs/)

## License

MIT
