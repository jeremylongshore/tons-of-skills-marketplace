# Command Reference

Full command surface for the TypeScript `aomi` CLI (or `npx @aomi-labs/client@latest` equivalent), verified against `@aomi-labs/client` v0.4.2. The skill invokes read forms freely; `set`/mutating forms only when the user explicitly asks.

Top-level commands in v0.4.2: `chat`, `tx`, `session`, `model`, `app`, `chain`, `wallet`, `account`, `logout`, `config`, `secret`.

## Chat

```bash
aomi chat "<message>"                                  # one-shot send and exit
aomi --prompt "<message>"                              # root-level compatibility form
aomi                                                   # interactive REPL
aomi chat "<message>" --new-session
aomi chat "<message>" --verbose                        # stream tool calls and agent output
aomi chat "<message>" --model <rig>
aomi chat "<message>" --public-key 0xUserAddress --chain 1
aomi chat "<message>" --app khalani --chain 137
aomi chat "<message>" --account-bearer "$AOMI_ACCOUNT_BEARER"
```

- Quote the message.
- On the first command in a new assistant session, prefer `--new-session`.
- Pass `--public-key` on the first wallet-aware message.
- Use `--app`, `--model`, `--chain` to change the active context for the next request.

Running bare `aomi` starts the REPL, which has its own commands: `/heap` (help), `/app <name>`, `/model <rig>|list|show`, `/key <provider:key>|show|clear`, and `:exit`. The skill drives one-shot forms, not the REPL.

## Transactions

```bash
aomi tx list                                           # pending/signed requests
aomi tx simulate <id> [<id> ...] [--cluster devnet]     # dry-run a batch on a fork / cluster
aomi tx sign <id> [<id> ...] [--cluster devnet]         # sign and submit
```

Duplicate ids in one `aomi tx sign` call are rejected. When an id is ambiguous across chains, use the chain-qualified selector shown by `aomi tx list` — `evm:tx-1` or `svm:tx-1`.

`aomi tx sign` is **EOA-only** in v0.4.2 — see [account-abstraction.md](account-abstraction.md).

## Sessions

```bash
aomi session list                                      # local sessions with topic + pending count
aomi session new
aomi session resume <id>                               # set active pointer
aomi session delete <id>                               # remove (check no pending txs first)
aomi session status                                    # current session summary
aomi session log                                       # replay conversation + tool output
aomi session events                                    # raw backend system events
aomi session close                                     # clear active pointer; next chat starts fresh
```

Selectors accept the backend session id, `session-N`, or `N`.

## Secrets

```bash
aomi secret list                                       # handle names only, no values
aomi secret clear                                      # drop all configured secrets
aomi secret add NAME=<value> [NAME=...]                # user-directed only (see workflows.md)
```

## Apps and Models

```bash
aomi app list
aomi app current
aomi model list
aomi model current
aomi model set <rig>                                   # persist model for current session
```

`aomi chat --model <rig> "<message>"` applies a model for one turn without persisting it. Pick an app per turn with `--app <name>` or `AOMI_APP=<name>`. The installed set is dynamic — confirm with `aomi app list`. Full catalog and per-app credential requirements in [apps.md](apps.md).

## Chain

```bash
aomi chain list
aomi chain current
aomi chain set <id>                                    # only when user asked to change default
```

## Wallet

```bash
aomi wallet set <evm-hex-key>                          # user-directed EVM 0x key (default)
aomi wallet set --evm <evm-hex-key>                    # explicit EVM form
aomi wallet set --solana <base58-key>                  # user-directed Solana keypair
aomi wallet current                                    # configured wallet address
aomi wallet whoami                                     # authenticated backend account
```

`aomi wallet set` persists local signing material under `AOMI_STATE_DIR` (default `~/.aomi`). After running, confirm with the derived address or Solana public key — never repeat the key value back.

## Account

```bash
aomi account login                                     # browser auth, mint account bearer
aomi account login --provider privy                    # provider browser auth ("privy" or "para")
aomi account login --wallet                            # native CLI SIWE with configured EVM wallet
aomi account login --solana                            # native CLI SIWS with configured Solana wallet
aomi account login --no-browser                        # skip provider auth, use native SIWE
aomi account whoami                                    # inspect authenticated account
aomi account links                                     # login methods and linked wallets
aomi account link [--provider <p>] [--wallet] [--solana] [--label <text>]
aomi account unlink <id> [--yes]                       # id, identity:<id>, or wallet:<id>
aomi account rename <id> --label <text>
aomi account update [--display-name <name>] [--avatar-url <url>]
aomi account delete --yes
aomi account sessions                                  # local CLI sessions for account switching
aomi account switch <id>
aomi logout                                            # also available as `aomi account logout`
```

## Config

```bash
aomi config current                                    # backend URL
aomi config set-backend <url>                          # repoint CLI at a different backend
```

## Flags and Env Vars

Flags override environment variables.

| Flag            | Default                 | Purpose                                                   |
| --------------- | ----------------------- | --------------------------------------------------------- |
| `--backend-url` | `https://chat.aomi.dev` | Backend URL (`AOMI_BACKEND_URL`)                          |
| `--api-key`     | `AOMI_API_KEY`          | API key for non-default apps (user-supplied)              |
| `--account-bearer` | `AOMI_ACCOUNT_BEARER` | Account-bound auth bearer                                 |
| `--embedded-provider` | deprecated        | Legacy provider exchange; prefer `--account-bearer`       |
| `--embedded-provider-token` | deprecated  | Legacy provider token; prefer `--account-bearer`          |
| `--app`         | `default`               | Backend app (`AOMI_APP`)                                  |
| `--application-id` | `AOMI_APPLICATION_ID` | Concrete backend application id for dynamic apps         |
| `--model`       | backend default         | Session model (`AOMI_MODEL`)                              |
| `--new-session` | off                     | Create a fresh active session for this command            |
| `--public-key`  | `AOMI_PUBLIC_KEY`       | Wallet address for chat/session context                   |
| `--private-key` | `PRIVATE_KEY`           | EVM signing key for this invocation                       |
| `--solana-private-key` | `SOLANA_PRIVATE_KEY` | Solana signing key for this invocation                |
| `--rpc-url`     | chain RPC default       | RPC override for signing (`CHAIN_RPC_URL`)                |
| `--chain`       | `AOMI_CHAIN_ID`         | Active wallet chain (inherits session chain if unset)     |
| `--cluster`     | `AOMI_SOLANA_CLUSTER`   | Solana cluster (`mainnet-beta`, `devnet`, `testnet`, or CAIP-2) |
| `--payment-method` | `AOMI_PAYMENT_METHOD` | Paid chat rail, e.g. `coinbase`/`x402`                   |
| `--json`        | off                     | Machine-readable JSON where supported                     |
| `--verbose`     | off                     | Extra diagnostics; on `chat`, streams tool calls live     |
| `--eoa`         | the default             | Plain EOA execution (`tx sign`) — local signing is always EOA |
| `--aa`          | off                     | Errors: AA now runs in the backend lane (`tx sign`)       |
| `--aa-provider` | `AOMI_AA_PROVIDER`      | `alchemy` \| `pimlico` preference synced to `user_state`  |
| `--aa-mode`     | `AOMI_AA_MODE`          | `4337` \| `7702` preference synced to `user_state`        |

Root-only flags: `-p`/`--prompt` (send one prompt and exit), `--show-tool` (show tool output in root prompt/REPL mode), `--provider-key PROVIDER:KEY` (save a BYOK provider key before running).

| Env Var           | Default   | Purpose                                |
| ----------------- | --------- | -------------------------------------- |
| `AOMI_STATE_DIR`  | `~/.aomi` | Root directory for local session state |
| `AOMI_BACKEND_URL` | `https://chat.aomi.dev` | Backend URL |
| `AOMI_ACCOUNT_BEARER` | none | Account auth bearer minted by login or supplied by user |
| `AOMI_API_KEY` | none | API key for non-default apps |
| `AOMI_APP` / `AOMI_APPLICATION_ID` | `default` / none | Active app selection |
| `AOMI_MODEL` | backend default | Active model |
| `AOMI_PUBLIC_KEY` | none | Wallet address for chat context |
| `AOMI_CHAIN_ID` | none | Default active chain |
| `CHAIN_RPC_URL` | none | Signing RPC override |
| `PRIVATE_KEY` | none | EVM signing key |
| `SOLANA_PRIVATE_KEY` | none | Solana signing key |
| `AOMI_SOLANA_CLUSTER` | none | Default Solana cluster |
| `AOMI_PAYMENT_METHOD` | none | Paid chat rail |
| `AOMI_AA_PROVIDER` / `AOMI_AA_MODE` | none | AA preferences — **setting either makes `aomi tx sign` fail** (see below) |

## Config Rules

- EVM signing keys must be 0x-prefixed hex. Solana signing keys are base58 or JSON keypairs. Configuring either is a user action, not a skill action.
- `--aa-provider` and `--aa-mode` cannot be used with `--eoa`, and `--aa` cannot be combined with `--eoa`.
- Passing `--aa`, `--aa-provider`, or `--aa-mode` — or exporting `AOMI_AA_PROVIDER` / `AOMI_AA_MODE` — selects AA execution, which `aomi tx sign` rejects with `AA execution now runs in the backend lane (rolling out); use --eoa for local execution.` Unset those env vars before signing locally.
- `--public-key` must match the address derived from `--private-key` when both are given.
- The default signing RPC is one URL. For chain switching, pass `--rpc-url` on `aomi tx sign` with a chain-matching public RPC.
- Solana signing currently materializes legacy pending `solana_sign` requests with unsigned transactions; canonical instruction-only `svm_ixs` requests may not appear as CLI-signable pending txs yet.

For account-abstraction details (modes, providers, sponsorship, chain defaults), see [account-abstraction.md](account-abstraction.md).

## Not in v0.4.2

Removed or never shipped on this CLI — do not emit these:

- `aomi thread ...` → the group is `aomi session ...` (and was in v0.1.42 too); only the backend HTTP API uses `/api/thread/*`
- `aomi wallet ls` / `dev-key` / `set-mode` → `aomi wallet set` / `current` / `whoami`; there is no CLI signing-policy mutation command
- `aomi login` → `aomi account login` (bare `aomi logout` does still exist; on v0.1.x this lived at `aomi wallet login`)
- `aomi cron ls|show|cancel` → no cron surface on this CLI
- `aomi deploy` → advertised in `aomi --help` but not registered as a subcommand in v0.4.2; `aomi deploy` exits with `Unknown command deploy` (fix pending in aomi-labs/aomi#467)
- `AOMI_CONFIG_DIR` → not read; local state is rooted at `AOMI_STATE_DIR`
