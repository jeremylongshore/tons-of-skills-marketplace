# Account Abstraction Reference

Read this when:

- The user asks about AA modes, sponsorship, or chain defaults.
- `aomi tx sign` returns an AA error and you need to pick a flag.
- The user explicitly requests `4337` or `7702`.

## Execution Model (v0.4.2)

**Local `aomi tx sign` is EOA-only.** AA execution moved to the backend lane and is rolling out. The CLI no longer attempts AA locally, and there is no local mode fallback.

Requesting AA on the signing path is a hard error:

```
$ aomi tx sign tx-1 --aa
AA execution now runs in the backend lane (rolling out); use --eoa for local execution.
```

Any of these selects AA execution and therefore fails `aomi tx sign`:

| Input | Effect |
|---|---|
| `--aa` | selects AA → `tx sign` errors |
| `--aa-provider alchemy\|pimlico` | selects AA → `tx sign` errors |
| `--aa-mode 4337\|7702` | selects AA → `tx sign` errors |
| `AOMI_AA_PROVIDER` / `AOMI_AA_MODE` in the environment | same as the flags — **`tx sign` errors even with no flag passed** |
| `--eoa` | plain EOA — the default, and the only local signing path |
| (nothing) | plain EOA |

`--aa` and `--eoa` cannot be combined, and `--aa-provider` / `--aa-mode` cannot be combined with `--eoa`.

**If a user reports that every `aomi tx sign` fails with the backend-lane message and they passed no flags, check for `AOMI_AA_PROVIDER` / `AOMI_AA_MODE` in their environment and have them unset those.**

## AA Preferences

`--aa-provider` and `--aa-mode` are *preferences synced to backend `user_state.evm.aa`* (as `{mode, provider}`), not local execution switches. The backend lane consumes them. The skill does not set these on its own initiative.

Local signing has no persistent AA config, and the skill never configures provider credentials itself.

## AA Modes

| Mode   | Flag             | Meaning                          | Gas |
| ------ | ---------------- | -------------------------------- | --- |
| `4337` | `--aa-mode 4337` | Bundler + paymaster UserOperation via smart account. Gas sponsored by paymaster. | Paymaster pays |
| `7702` | `--aa-mode 7702` | Native EIP-7702 type-4 transaction with delegation. EOA signs authorization + sends tx to self. | EOA pays |

**7702 requires the signing EOA to have native gas tokens** (ETH, MATIC, etc.). There is no paymaster/sponsorship for 7702. 4337 is the gasless path.

## AA Providers

| Provider | Value                   | Notes                            |
| -------- | ----------------------- | -------------------------------- |
| Alchemy  | `--aa-provider alchemy` | 4337 (sponsored via gas policy), 7702 (EOA pays gas) |
| Pimlico  | `--aa-provider pimlico` | 4337 (sponsored via dashboard policy) |

## Gas: the rule the skill must follow

Because local signing is EOA-only, **the signing EOA must hold native gas on the destination chain** — there is no local sponsorship path to fall back on.

Before signing on an L2, confirm the EOA has a small amount of native gas (~0.0005 ETH equivalent is enough). If the user is sending USDC-only to an L2 with no native gas, tell them signing will fail until they fund the EOA with native gas on that chain.

Do not promise the user "AA will pay for gas". When the CLI emits a viem `insufficient funds for transfer` error, do not retry with different flags — stop and tell the user to fund the destination chain.

## Supported Chains

Chains in the v0.4.2 CLI chain table:

| Chain                 | ID       | Notes |
| --------------------- | -------- | ----- |
| Ethereum              | 1        | |
| Polygon               | 137      | |
| Arbitrum              | 42161    | |
| Base                  | 8453     | |
| Base Sepolia          | 84532    | testnet |
| Optimism              | 10       | |
| Sepolia               | 11155111 | testnet |
| Linea Mainnet         | 59144    | |
| Linea Sepolia Testnet | 59141    | testnet |
| Monad                 | 143      | |
| Monad Testnet         | 10143    | testnet |
| Robinhood Chain       | 4663     | |
| MegaETH               | 4326     | |
| Anvil (local)         | 31337    | local dev chain |

Solana is supported for sign-only flows via `--solana-private-key` and `--cluster` (`mainnet-beta`, `devnet`, `testnet`, or the CAIP-2 forms `solana:mainnet` / `solana:devnet` / `solana:testnet`).

Per-chain AA availability and default mode are reported by the backend through `aomi chain list` — read it there rather than assuming. Historically the backend defaulted to 7702 on Ethereum, Polygon, Arbitrum, Base, and Optimism, but this is backend state and can change independently of the CLI version.

## RPC Guidance By Chain

Use an RPC that matches the pending transaction's chain — Ethereum txs → Ethereum RPC, Base txs → Base RPC, and so on.

Practical rule:

- `--chain` affects the wallet/session context for chat and request building.
- `--rpc-url` affects where `aomi tx sign` estimates and submits the transaction.
- Treat them as separate controls and keep them aligned with the transaction you are signing.
