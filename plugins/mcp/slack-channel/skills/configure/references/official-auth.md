# Slack token and Socket Mode authority

Use Slack's current documentation as the authority for token types, scopes,
revocation, and Socket Mode behavior. The plugin's prefix checks are a local
safety guard, not proof that a token is live or sufficiently scoped.

## Token roles

| Token                | Prefix  | Purpose                                            | Required CCSC capability                        |
| -------------------- | ------- | -------------------------------------------------- | ----------------------------------------------- |
| Bot User OAuth Token | `xoxb-` | Authorizes the installed bot's Slack Web API calls | Granted bot scopes in the app configuration     |
| App-level token      | `xapp-` | Represents the app across installations            | `connections:write` for `apps.connections.open` |

Socket Mode creates a temporary WebSocket URL at runtime. Do not print, persist,
or reuse that URL. A successful HTTP response is insufficient: Slack methods
return an application-level `ok` field and may return an `error` while HTTP
transport succeeds.

## Credential handling

1. Copy tokens directly from the Slack app settings.
2. Pass them only to the terminal-side `configure` workflow.
3. Write the complete `.env` once and set mode `0600`.
4. Never echo token values during confirmation or diagnostics.
5. For rotation, regenerate or revoke in Slack, overwrite `.env` through
   `configure`, restart the channel, and run `install doctor`.
6. If a token appears in logs, chat, shell history, or a committed file, revoke
   it before continuing.

## Official documentation

- [Slack token types](https://docs.slack.dev/authentication/tokens/)
- [Using Socket Mode](https://docs.slack.dev/apis/events-api/using-socket-mode/)
- [`apps.connections.open`](https://docs.slack.dev/reference/methods/apps.connections.open/)
- [`auth.test`](https://docs.slack.dev/reference/methods/auth.test/)
