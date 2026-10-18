# cohesivity

Backend services for the apps you build with Claude Code: Postgres, Redis, object storage, hosting, login and email through [Cohesivity](https://cohesivity.ai?ref=gh-tons-of-skills)'s hosted MCP server. No account or API key is needed to start.

## What it includes

- **MCP server** (`.mcp.json`): connects to `https://cohesivity.ai/mcp` over HTTPS. Nothing is installed or run locally.
- **Skill** (`skills/cohesivity`): when to use Cohesivity, reusing the project's `.cohesivity` file instead of creating a second project, reading a service's docs before provisioning it, and keeping keys out of client code and commits.
- **Confirmation hook** (`hooks/hooks.json`): Claude Code asks you before `create_tenant`, `provision_resource` or `claim_tenant` runs.

## Install

```
/plugin install cohesivity@claude-code-plugins-plus
```

## How it works

When a task needs a database or a deploy, Claude loads the skill and asks to create a temporary project (it lasts 72 hours unless you claim it). After you approve, it writes the credentials to `.cohesivity` at the project root (mode 600, gitignored), asks again before provisioning each service, and wires the app to it from server-side code.

## Tools

| Tool                           | What it does                                                    | Asks first |
| ------------------------------ | --------------------------------------------------------------- | ---------- |
| `create_tenant`                | Create a temporary project and return its credentials           | Yes        |
| `provision_resource`           | Provision a service (Postgres, Redis, object storage, hosting, ...) | Yes    |
| `claim_tenant`                 | Get a link to claim the project and keep it                     | Yes        |
| `tenant_status`                | Show the project's lifecycle, limits and services               | No         |
| `get_cohesivity_documentation` | Read the current docs for a service                             | No         |
| `give_feedback`                | Report a problem with Cohesivity                                | No         |

## Notes

- When the tools are used, the requests Claude makes, such as which service to provision, are sent to Cohesivity.
- The server also marks `create_tenant`, `provision_resource` and `claim_tenant` as needing user interaction, and rejects them unless `confirmed: true` is passed.
- Paid actions and plan upgrades need your approval. See [pricing](https://cohesivity.ai/pricing?ref=gh-tons-of-skills) and the [docs](https://cohesivity.ai/docs?ref=gh-tons-of-skills).

## Tests

```
node --test plugins/mcp/cohesivity/tests/*.test.mjs
```

## License

MIT
