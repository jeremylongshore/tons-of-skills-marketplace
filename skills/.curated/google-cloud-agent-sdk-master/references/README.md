# Google Cloud ADK References

These references support the `google-cloud-agent-sdk-master` skill.

- `SKILL.full.md` is the current lifecycle and migration guide for Google's
  maintained `agents-cli`.
- The public command `/create-agent` scaffolds a Google ADK application. It is
  distinct from `/agent-creator`, which creates Claude Code subagent definition
  files.

## Authority

Use primary Google sources and the installed CLI in this order:

1. `agents-cli <command> --help` for the installed command contract
2. https://github.com/google/agents-cli
3. https://google.github.io/agents-cli/
4. https://google.github.io/adk-docs/

Agent Starter Pack is a migration source only. Google placed it in maintenance
mode and directs new projects to `agents-cli`.

## Drift Check

Before answering a version-sensitive question, verify the live source with
`WebFetch` or use `WebSearch` restricted to official Google domains. Do not cache
template names, model IDs, deployment flags, regional availability, or prices in
the skill.
