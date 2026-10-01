# Hermes Tweet Skill card

This is a public self-assessment, not NVIDIA verification.

Do not present Hermes Tweet as NVIDIA-verified unless the release also includes
a clean SkillSpector scan report, Tier-3 eval data, `BENCHMARK.md`,
`skill.oms.sig`, and signature verification instructions for the exact reviewed
skill directory.

## Owner

- Published by Xquik.
- **Repository.** https://github.com/Xquik-dev/hermes-tweet
- Licensed under MIT.
- **Version.** 0.1.13
- **Primary Skill.** `SKILL.md`

## Use case

Hermes Tweet helps Hermes Agent users find X/Twitter endpoints, perform
authenticated X/Twitter reads, and run explicitly approved X/Twitter workflow
actions through the bundled Hermes Tweet tools.

Use it for:

- Searching tweets, reading tweet details, replies, and user profiles.
- Preparing action previews for posts, replies, follows, direct messages,
  monitors, webhooks, extraction jobs, media workflows, and giveaway draws.
- Keeping X/Twitter automation inside catalog-listed Xquik API routes.

Do not use it for account connection, re-authentication, billing, credit top-up,
support tickets, or direct HTTP fallback routes.

## Inputs and configuration

- **Required configuration.** Set `XQUIK_API_KEY` in the runtime
  environment. Never request, echo, log, or store the value.
- **Action gate.** Set `HERMES_TWEET_ENABLE_ACTIONS=true` before
  write-capable tool calls.
- **Project plugin gate.** Set `HERMES_ENABLE_PROJECT_PLUGINS=true` for
  trusted local Hermes project plugin loading.
- **User input.** Accept natural language, endpoint choices, and explicit action
  payload approval.

## Capabilities

- **Tools.** `tweet_explore`, `tweet_read`, and `tweet_action`.
- **Network.** Required only through catalog-listed Xquik API routes reached by
  those tools.
- **Shell.** Not required for normal operation. Use Hermes CLI commands only for
  installation and registry diagnostics.
- **Files.** Not required for normal operation. Do not write reports, credentials,
  logs, screenshots, or cached payloads unless the user asks for an explicit
  export workflow.
- **MCP.** Not required.

## Outputs

- Endpoint recommendations from `tweet_explore`.
- Concise summaries of authenticated read results from `tweet_read`.
- Action previews, JSON-like payloads, and post-call summaries for
  user-approved `tweet_action` calls.
- Troubleshooting guidance for missing configuration or disabled action gates.

## Side effects

- `tweet_explore` has no external side effects.
- `tweet_read` performs authenticated reads.
- `tweet_action` may change account or workflow state only after explicit user
  approval and only when the action gate is enabled.

## Known risks and mitigations

- **Broad requests.** Start with `tweet_explore`, prefer `tweet_read`, and require a
  user-approved endpoint plus payload before `tweet_action`.
- **Exposed secrets.** Ask only for environment configuration, never key values, and
  never put credentials in tool arguments.
- **Guessed endpoints.** Accept only catalog-listed `/api/v1/...` paths. Reject direct
  HTTP fallbacks.
- **Account changes.** Keep `HERMES_TWEET_ENABLE_ACTIONS=false` by default. Summarize
  side effects before any account-changing call.

## Release trust gate

Before broad enterprise release or any NVIDIA-verified claim:

1. Run SkillSpector against the complete skill directory.
2. Resolve critical or high findings.
3. Add Tier-3 eval data and `BENCHMARK.md` for the reviewed release.
4. Sign the exact reviewed skill directory and publish `skill.oms.sig`.
5. Verify the published directory with the expected certificate chain.

## References

- `SKILL.md`
- `README.md`
- `after-install.md`
- `SECURITY.md`
