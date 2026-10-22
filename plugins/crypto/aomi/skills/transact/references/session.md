# Session Reference

Read this when:

- You need to know **where** conversation history, pending txs, or signed receipts live.
- `aomi tx list` returns `No active session` and you need to recover the right session.
- The user asks "what's in `~/.aomi/`?" or wants to clean up old sessions.
- You're picking between `--new-session`, `aomi session resume <N>`, and just letting the active session continue.

> The command group is `aomi session ...` — and has been since at least v0.1.42. There is no `aomi thread` command on the npm CLI. Note the backend HTTP API still uses `/api/thread/*` paths, so "thread" remains correct for the API and the concept; it is only wrong as a CLI command.

## Two-tier storage model

A session is split across two stores. Knowing what lives where prevents wrong-place lookups.

**Backend (the aomi server)** holds the durable record:

- The full conversation transcript (user prompts + assistant prose).
- All tool calls + tool outputs the agent made silently.
- System events (BYOK key changes, sponsorship decisions, etc.).
- Indexed by a `sessionId` UUID.

`aomi session log`, `aomi session events`, and the message replay in `aomi session status` all hit the backend with the local `sessionId`. If the backend is unreachable or the sessionId is wrong, these will silently return empty or fail.

**Local on disk** (`$AOMI_STATE_DIR` if set, else `~/.aomi/`) holds the lookup keys and the parts the wallet flow needs:

- `sessionId` and `clientId` (UUIDs the backend uses to find the rest).
- `publicKey`, `chainId`, `baseUrl` (current wallet/chain/backend context).
- `pendingTxs[]` and `signedTxs[]` (full calldata, gas estimates, hashes — same data the backend has, mirrored locally so `aomi tx list` works without a network round-trip).
- `secretHandles{}` (handle names only — values are never stored locally).
- `localId`, `createdAt`, `updatedAt` (local bookkeeping).

The local state is what `aomi tx list`, `aomi tx sign`, and `aomi config current` read from. None of these touch the backend. Linked wallets and account login methods are a separate, account-scoped view — see `aomi account links`.

## File layout

```
~/.aomi/
├── active-session.txt              # one line, the local session id (e.g. "43")
└── sessions/
    ├── session-1.json
    ├── session-2.json
    ├── ...
    └── session-<N>.json            # one file per local session
```

State files are written `0600` and the directories `0700`. A legacy single-file state at `$XDG_RUNTIME_DIR/aomi-session.json` (or `$TMPDIR/aomi-session.json`) is migrated into this layout on first run.

Each `session-<N>.json` is the local source of truth for that session. Inspecting it is safe — it does not contain credential values, only handle names. Useful when debugging:

```bash
cat ~/.aomi/sessions/session-43.json | jq '{sessionId, chainId, publicKey, pending: (.pendingTxs|length), signed: (.signedTxs|length)}'
```

## The `active-session.txt` mechanic

`aomi tx list`, `aomi tx sign`, and `aomi tx simulate` all need an **active** session. The active session is just the local id stored in `~/.aomi/active-session.txt`. Set automatically by:

- `aomi --prompt "..."` (creates or reuses one)
- `aomi chat "..."` (same)
- `aomi --new-session ...` (creates a new one)
- `aomi session new` (creates a new one, no chat)
- `aomi session resume <id>` (sets active to an existing session)

Cleared by `aomi session close` and sometimes by errors mid-flight.

**The "No active session" recovery pattern**: if `aomi tx list` reports `No active session. Run \`aomi chat\` first.`, run `aomi session list` to find the right session by topic or pending count, then `aomi session resume <N> > /dev/null && aomi tx list` in the same shell call (the active-session pointer can be lost between subprocess invocations).

Note that `No active session. Run \`aomi account login\` first.` is a *different* error — that one is about account auth, not the local session pointer.

## Lifecycle: `--new-session` vs `resume` vs neither

Three rules, in order:

1. **Starting fresh work in a new assistant thread or terminal**: pass `--new-session` on the first chat command. Old session context (pending txs from previous tasks, accumulated message tokens) won't bleed in.
2. **Continuing a task you started earlier (same session)**: don't pass `--new-session`. The active session persists across `aomi` invocations; the next `aomi chat "proceed"` lands in the same conversation.
3. **Picking up a previous session by id**: `aomi session resume <N>` first, then issue commands. Useful when `aomi tx list` shows pending txs you need to sign from a session that was closed earlier.

Selectors accept the backend session id, `session-N`, or bare `N`.

Account login lives under `account`: `aomi account login` for the browser/native flow, `aomi account whoami` to inspect the active account, and `aomi account links` to inspect linked wallets and login methods. Local signing keys are separate — `aomi wallet set` / `aomi wallet current`.

## Cleanup hygiene

Sessions accumulate. After a few weeks of use, `~/.aomi/sessions/` can hold 50–100+ files. Cleanup is safe:

```bash
aomi session list                   # see what's there, with topics + pending counts
aomi session delete <id>            # delete one — safe if no pending txs
aomi session close                  # clear active pointer; next chat starts fresh
```

**Before deleting a session, check it has no pending wallet requests** (`aomi tx list` after `aomi session resume <id>`). Deleting a session with pending txs orphans them — the backend may still know about them, but the local CLI loses the calldata and ids needed to sign.

The `secretHandles{}` block in a session JSON is safe to read and inspect. The values they reference are stored on the backend, scoped to that session's `clientId`. `aomi secret clear` removes them from the backend; deleting the session locally does not.

## When to override the state dir

`AOMI_STATE_DIR` lets the user point the CLI at a non-default state root. Common reasons:

- Test setups: `AOMI_STATE_DIR=$(mktemp -d) aomi --prompt "..."` — clean slate per run, no contamination of the user's main `~/.aomi/`.
- Multiple identities: separate dirs for separate wallets / backends, switched via shell function or `direnv`.

The skill itself does not set this variable. If the user wants isolation, they configure it in their own shell.

There is no `AOMI_CONFIG_DIR` — the CLI does not read it.
