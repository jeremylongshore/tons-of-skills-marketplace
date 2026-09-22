---
name: create-agent
description: Scaffold a Google ADK app with Google's maintained agents-cli
argument-hint: "<project-name> [new|enhance]"
allowed-tools: Read,Glob,Grep,Bash(command -v:*),Bash(uvx:*),Bash(agents-cli:*),AskUserQuestion
model: sonnet
---
# Create a Google Cloud ADK Application

Use Google's maintained `agents-cli` to create or enhance an Agent Development
Kit (ADK) application.

## Important Scope Check

This command creates a runnable Google agent application. It does **not** create
a Claude Code subagent file under `agents/*.md` or `.claude/agents/*.md`.

- For a Claude Code subagent definition, use `/agent-creator`.
- For a Google ADK application, continue here.

Do not treat Agent Starter Pack as the default for a new project. Google placed
that project in maintenance mode and moved active development to
[`google/agents-cli`](https://github.com/google/agents-cli).

## Prerequisites

- Python 3.11 or newer
- `uv` and `uvx`
- Node.js, because `agents-cli setup` installs coding-agent skills
- A project name and whether this is a new or existing codebase
- Google Cloud only for deployment; local development can use an AI Studio key

Use `command -v` only to inspect whether the required executables exist. If a
prerequisite is missing, show the official installation link and stop before
changing the machine.

## Instructions

1. Use `AskUserQuestion` to confirm whether the user wants a new ADK project or
   wants to enhance an existing one. Confirm the target directory before
   writing files.
2. Read the target repository's instructions and inspect its current files with
   `Read`, `Glob`, and `Grep`. Never overwrite an existing application blindly.
3. Inspect the installed CLI contract before constructing flags:

   ```bash
   uvx google-agents-cli --help
   uvx google-agents-cli create --help
   ```

4. Show the exact scaffold command and destination. Run it only after the user
   approves the write:

   ```bash
   uvx google-agents-cli create PROJECT_NAME
   ```

5. For an existing agent project, inspect the repository first, then use the
   current enhancement command shown by CLI help. Current releases expose:

   ```bash
   agents-cli scaffold enhance
   ```

6. Enter the generated project and use its own checked-in configuration as the
   source of truth. Do not invent template names, deployment flags, model IDs,
   regions, or environment variables.
7. Run the generated verification lane. The current CLI provides:

   ```bash
   agents-cli install
   agents-cli lint
   agents-cli run "smoke test"
   agents-cli eval run
   ```

8. If deployment is requested, authenticate explicitly and inspect
   `agents-cli deploy --help`. Present the target, Google Cloud project, region,
   identity, secrets plan, and cost implications before executing deployment.
   Supported deployment guidance currently covers Agent Runtime, Cloud Run, and
   GKE, but availability and flags may change by release.
9. If publishing to Gemini Enterprise is requested, inspect
   `agents-cli publish gemini-enterprise --help` and require a separate approval
   before the external mutation.

## Output

Report:

- project name and absolute destination
- new-project or enhance mode
- exact `agents-cli` version and commands used
- files created or modified
- local lint, smoke, and evaluation results
- deployment or publication status, clearly distinguishing planned from run
- any remaining authentication, quota, or configuration work

## Safety and Approval Boundaries

- Never write until the destination is confirmed.
- Never run `agents-cli setup`, install system dependencies, authenticate,
  provision cloud resources, deploy, publish, or initialize a remote repository
  without showing the exact action first.
- Never put API keys, service-account JSON, access tokens, or credential paths in
  generated source control. Use the generated secret-management pattern.
- Never use `--allow-unauthenticated` unless the user explicitly requests a
  public endpoint and acknowledges the exposure.
- Do not quote fixed prices. Link to current Google Cloud pricing for the chosen
  services because model and infrastructure prices change.

## Error Handling

| Failure | Response |
|---|---|
| User actually wants a Claude Code subagent | Stop and route to `/agent-creator` |
| `uvx` unavailable | Link to the official uv installation guide; do not curl-pipe an installer automatically |
| Destination exists | Inspect it and switch to enhance mode or choose a new destination |
| CLI flag differs | Trust the installed `--help`; do not reuse an old Agent Starter Pack flag |
| Authentication missing | Explain `agents-cli login` and wait for the user to authenticate |
| Cloud API or quota failure | Report the exact service/project/region and preserve local work |
| Verification fails | Keep the project local, surface the failing command, and do not deploy |

## Resources

- [Google agents-cli](https://github.com/google/agents-cli)
- [agents-cli documentation](https://google.github.io/agents-cli/)
- [Google ADK documentation](https://google.github.io/adk-docs/)
- [Agent Starter Pack migration guide](https://google.github.io/agents-cli/reference/from-agent-starter-pack/)
