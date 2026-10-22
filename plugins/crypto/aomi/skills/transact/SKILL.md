---
name: aomi-transact
description: >
  Build natural-language crypto agents, web3 assistants, and trading bots that read
  and write EVM chain state. Aomi turns prompts ("swap 1 ETH for USDC", "open a 3x
  GMX long", "bet $100 on Polymarket") into wallet-signed transactions on Ethereum,
  Base, Arbitrum, Optimism, Polygon, Linea — non-custodial, fork-simulated. Use when
  the user wants a crypto/DeFi agent, AI trading/wallet assistant, or on-chain
  execution against Uniswap, Aave, Lido, GMX, Hyperliquid, Polymarket, Binance, OKX,
  or 40+ other protocols. Trigger with prompts about swaps, lending, bridging,
  staking, perps, prediction markets, or any DeFi/CEX action needing a wallet
  signature. Account-abstraction aware with EIP-7702/4337 in the backend lane; local CLI
  signing is EOA. MUST NOT fabricate
  or echo credentials; values reach the CLI only when the user explicitly supplied them.
compatibility: 'Verified against @aomi-labs/client v0.4.2. Install globally via npm install -g @aomi-labs/client@latest, or run on demand via npx @aomi-labs/client@latest. A pre-existing global aomi binary is NOT upgraded by installing this skill — check aomi --version and upgrade if it is below 0.4.2, since the account command group and local AA signing behavior changed in 0.4.x. The CLI defaults to https://chat.aomi.dev (api.aomi.dev is the legacy host). viem and Solana signing dependencies are bundled by the package. Designed for claude-code; also works with Cursor, Codex CLI, Gemini, and any agent runtime that supports the Anthropic skill spec.'
license: MIT
version: "0.11.0"
author: 'aomi-labs <hello@aomi.dev>'
tags: [crypto, defi, web3, evm, ethereum, wallet, account-abstraction, trading, mcp, agent]
allowed-tools: 'Bash(aomi:*), Bash(npx:*)'
metadata:
  author: 'aomi-labs <hello@aomi.dev>'
  version: "0.11.0"
  repository: aomi-labs/skills
  homepage: https://github.com/aomi-labs/skills/tree/main/aomi-transact
permissions:
  files:
    read: [~/.aomi/]
    write: [~/.aomi/]
    deny_write: [SOUL.md, MEMORY.md, AGENTS.md]
  network:
    allow: [chat.aomi.dev]
    deny: "*"
  shell:
    - aomi
    - npx @aomi-labs/client@latest
  tools: []
risk_tier: L2
requires:
  binaries: [aomi, npx]
---

# Aomi Transact

## Overview

Aomi Transact drives the `aomi` TypeScript CLI to build natural-language crypto agents and web3 assistants. It composes calldata, fork-simulates transactions as a batch, and stages wallet requests for explicit user signing — non-custodial throughout. Current chain metadata includes Ethereum, Polygon, Arbitrum, Base, Base Sepolia, Optimism, Sepolia, Linea, Linea Sepolia, Monad, Monad Testnet, Robinhood Chain, MegaETH, and local Anvil. The npm CLI is the production/end-user surface; the Rust `aomi-cli` in `product-mono` is an in-process dev/test CLI with a *different command surface* — never mix the two. For deep references, see [commands.md](references/commands.md), [workflows.md](references/workflows.md), [gotchas.md](references/gotchas.md), [account-abstraction.md](references/account-abstraction.md), [apps.md](references/apps.md), [examples.md](references/examples.md), [session.md](references/session.md), [drain-vectors.md](references/drain-vectors.md), [troubleshooting.md](references/troubleshooting.md).

## Prerequisites

- Node.js 18+ with npm or npx
- `@aomi-labs/client` v0.4.2 or newer: `npm install -g @aomi-labs/client@latest`
- For EVM signing: a 0x-prefixed private key via `aomi wallet set`, `--private-key`, or `PRIVATE_KEY`
- For Solana sign-only flows: a base58 or JSON keypair via `aomi wallet set --solana`, `--solana-private-key`, or `SOLANA_PRIVATE_KEY`
- Optional: `AOMI_ACCOUNT_BEARER` / `--account-bearer` for authenticated account-bound requests
- Native gas on the destination chain for the signing EOA — local signing is EOA-only, so there is no sponsorship fallback

## Instructions

1. Detect the CLI and **check its version**: `aomi --version 2>/dev/null || npx @aomi-labs/client@latest --version`. If it prints below `0.4.2`, stop and tell the user to run `npm install -g @aomi-labs/client@latest`, or prefix every command with `npx @aomi-labs/client@latest` instead. An already-installed global `aomi` is never upgraded by installing this skill, and the pre-0.4 surface differs.
2. Start a new session: `aomi chat "<task>" --new-session`
3. Inspect queue: `aomi tx list`
4. For multi-step flows, simulate first: `aomi tx simulate tx-1 tx-2`
5. Sign: `aomi tx sign tx-1`
6. Verify: `aomi session status` or `aomi session log`

For the full procedure (read-only requests, building wallet requests, signing policy, batch simulation, secret ingestion), see [workflows.md](references/workflows.md).

## Examples

```bash
aomi chat "what is the price of ETH?" --new-session
aomi chat "swap 1 ETH for USDC" --new-session --public-key 0xYourAddress --chain 1
aomi tx list && aomi tx simulate tx-1 tx-2 && aomi tx sign tx-1 tx-2
aomi chat "stake 0.5 ETH on Lido" --app lido --chain 1 --new-session
```

Four end-to-end walkthroughs (approve+swap, lending, bridging, staking) in [examples.md](references/examples.md). Per-app first-turn examples (Khalani, 0x, Polymarket, Binance, Neynar) in [apps.md](references/apps.md#usage-examples).

## Output

- `aomi chat`: agent response or `⚡ Wallet request queued: tx-N`
- `aomi tx list`: table of pending/signed tx ids with `batch_status`
- `aomi tx simulate`: per-step success/failure, revert reason, gas usage
- `aomi tx sign`: transaction hash and on-chain confirmation

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `insufficient funds for transfer` | Signing EOA has no native gas | Fund the EOA on the destination chain — local signing has no sponsorship path |
| `AA execution now runs in the backend lane` | An AA path was selected on `tx sign` | Drop `--aa`/`--aa-provider`/`--aa-mode`; if no flags were passed, unset `AOMI_AA_PROVIDER`/`AOMI_AA_MODE` |
| `stateful: false` in simulation | Wrong batch order | Reorder tx ids to match execution dependency |
| `RPC 401`/`429` | Rate-limited or missing key | Set `--rpc-url` to authenticated endpoint |
| No tx queued after chat | Agent returned quote first | Run `aomi tx list`; send a confirmation reply |
| Orphaned `tx-N` in list | Previous simulation failed | Only sign txs with `batch_status: passed` |
| `Failed to get apps/models: HTTP 404` | Public backend does not expose that introspection route | Treat `app list`/`model list` as backend-dependent; do not block chat/sign flows on it |

Full troubleshooting in [troubleshooting.md](references/troubleshooting.md).

## Safety Justification

This skill is `risk_tier: L2` because it can sign and broadcast on-chain transactions. The permissions manifest enforces least privilege:

- **Shell allowlist** scopes execution to `aomi` and `npx @aomi-labs/client@latest` only — no arbitrary subprocesses.
- **Network allowlist** restricts outbound traffic to `chat.aomi.dev` (the CLI's default backend; `api.aomi.dev` is the legacy host). User-supplied `--rpc-url` endpoints are resolved by the CLI itself; operators must review them before allowing signing.
- **File scope** is read+write to `~/.aomi/` only; identity files (`SOUL.md`, `MEMORY.md`, `AGENTS.md`) are deny-listed against writes per OWASP AST03 mitigation #3.
- **No blind signing.** Multi-step flows go through `aomi tx simulate` on a forked chain before `aomi tx sign`. Drain-vector calldata fields (`recipient`, `onBehalfOf`, `mintRecipient`, `_to`) are blocked at simulation time when they do not equal `msg.sender` — see [drain-vectors.md](references/drain-vectors.md).
- **Opaque credentials.** The skill never fabricates, derives, or echoes credential values; setup commands run only when the user explicitly asks and supplies the value in this turn. Full rules in [gotchas.md → Hard Rules](references/gotchas.md#hard-rules).

## When to Use

- The user wants to chat with the Aomi agent from the terminal.
- The user wants balances, prices, routes, quotes, or transaction status.
- The user wants to build, simulate, confirm, sign, or broadcast wallet requests.
- The user wants to inspect or switch apps, models, chains, or sessions.
- The user wants to inspect or change Account Abstraction preferences (synced to the backend lane).
- The user wants to authenticate a CLI account with `aomi account login`, inspect it with `aomi account whoami`, or inspect linked wallets and login methods with `aomi account links`.
- The user wants to build a new app from an API spec or SDK — use the companion skill **aomi-build**.

## Command Surface

```
aomi                                Interactive REPL
aomi --prompt "<message>"           Send one prompt and exit
aomi chat <message>                 Send a message
aomi tx list|simulate|sign
aomi session list|new|resume|delete|status|log|events|close
aomi model list|set|current
aomi app list|current
aomi chain list|set|current
aomi wallet set|current|whoami
aomi account login|whoami|logout|links|link|unlink|rename|update|delete|sessions|switch
aomi logout
aomi config set-backend|current
aomi secret list|clear|add
```

There is **no** `aomi thread`, `aomi cron`, `aomi login`, or `aomi wallet ls|dev-key|set-mode` on this CLI — those belong to the separate Rust `aomi-cli`. `aomi deploy` is advertised in `--help` but unreachable in v0.4.2 (fix pending in aomi-labs/aomi#467). Full command reference, flags, and env vars in [commands.md](references/commands.md).

## Resources

- Source repository: https://github.com/aomi-labs/skills/tree/main/aomi-transact
- npm package: https://www.npmjs.com/package/@aomi-labs/client
- Companion skill for adding new protocol integrations: [aomi-build](https://github.com/aomi-labs/skills/tree/main/aomi-build)
- Account abstraction deep-dive: [references/account-abstraction.md](references/account-abstraction.md)
- Drain-vector catalog (security): [references/drain-vectors.md](references/drain-vectors.md)
- End-to-end transaction examples: [references/examples.md](references/examples.md)
- Troubleshooting playbook: [references/troubleshooting.md](references/troubleshooting.md)
- OWASP AST03 (Over-Privileged Skills) spec: https://owasp.org/www-project-agentic-skills-top-10/ast03
- Anthropic skill spec: https://docs.claude.com/en/docs/claude-code/skills
