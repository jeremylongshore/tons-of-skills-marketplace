# Flow Examples

Read this when:

- The user asks for a concrete end-to-end example of a DeFi operation.
- You're constructing a new flow and want a template to pattern-match against.
- You're a new tool-using model and need to know what shape `aomi chat` will return for a given user intent.

Each example is anchored to a **real backend-side capture** from a mainnet anvil fork. Prompts, gas figures, addresses, and the `Internal trace` blocks come directly from those captures. The "What the user sees in the terminal" blocks are **reformatted** from the same backend events into the CLI's pretty-printed style — the data is real, the exact text formatting may drift slightly across CLI versions. See [Verification provenance](#verification-provenance) at the end of this doc for source logs and capture dates.

The CLI lifecycle is consistent across every example:

> **chat** (natural-language intent) → **list** (verify what was queued) → **simulate** (catch reverts before signing) → **sign** (wallet pop) → **verify** (chain-state confirmation)

If you only remember one thing: **the user gives intent in plain English; aomi composes calldata; simulate is the gate; the wallet only sees what passed simulation.**

A term you'll see throughout: a **drain vector** is the calldata field where a malicious prompt could redirect funds to a wrong recipient — `recipient` in Uniswap, `onBehalfOf` in Aave, `mintRecipient` in CCTP, `_to` in OP-stack bridges. The agent blocks these at simulation time when they don't equal the user's own address. The skill's job is to surface the block, not bypass it. Full per-protocol table in [drain-vectors.md](drain-vectors.md).

Three notes on what you'll see in the terminal:

- The `Internal trace` blocks below show what the agent does silently between chat and the queued-tx output. Users only see this with `--verbose` or by replaying via `aomi session log`. Without `--verbose`, the user sees just the assistant prose followed by `⚡ Wallet request queued: tx-N`.
- The shortest one-shot form is `aomi --prompt "<message>"`. The examples below use `aomi chat "<message>"` for readability — both behave the same.
- **Signing output in these captures predates v0.4.2.** Transcripts showing `Exec: aa (alchemy, 7702)` were recorded when the CLI still attempted account abstraction locally. On v0.4.2, `aomi tx sign` executes as a plain EOA and AA runs in the backend lane — expect `executionKind: "eoa"` and the EOA-batched dual-hash shape described at the end of this file. The calldata composition, simulation, and drain-vector behavior shown here are unchanged.

---

## 1. Swap — Uniswap V3 exactInputSingle

**Anchored to** `redteam-uniswap-happy-1.log` — USDC→WETH on mainnet, fee tier 500 (0.05%), captured shape.

### What the user types

```bash
aomi chat "swap 1 USDC for WETH on Uniswap V3, send to my wallet" \
  --public-key 0xUserAddress --chain 1 --new-session
```

That's enough. The agent picks `SwapRouter02 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45`, fee tier 500, recipient = your wallet, and queues the approve in the same batch.

### What the user sees in the terminal

```
I've staged your USDC → WETH swap on Uniswap V3 (0.05% fee tier).

Transaction Batch:
  1. Approve Uniswap Router to spend USDC
  2. Swap 1 USDC → WETH on V3 0.05% pool, recipient = your wallet

Run `aomi tx simulate tx-1 tx-2` to dry-run, then `aomi tx sign tx-1 tx-2` to send.

⚡ Wallet request queued: tx-1
   to:    0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
   value: 0
   chain: 1
⚡ Wallet request queued: tx-2
   to:    0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45
   value: 0
   chain: 1
```

### Internal trace (visible with `--verbose` or `aomi session log`)

The agent activates the skill, reads balance/allowance, then stages two txs and simulates:

```
activate_skills        → uniswap
read    USDC.balanceOf / USDC.allowance to SwapRouter02
stage   "Approve Uniswap Router to spend USDC"
        approve(0x68b3...Fc45, MAX) on USDC
stage   "USDC to WETH swap"
        exactInputSingle((USDC, WETH, 500, <user>, 1_000_000, 0, 0))
simulate_batch         → Batch success: true
                         (no drain-vector annotations)
```

### Lifecycle

```bash
aomi tx list
# pending:
#   tx-1  to 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 (USDC)
#         label: Approve Uniswap Router to spend USDC
#   tx-2  to 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45 (Uniswap SwapRouter02)
#         label: Swap 1 USDC for WETH on Uniswap V3 (0.05% pool)

aomi tx simulate tx-1 tx-2
# Simulation result:
#   Batch success: true
#   Stateful: true
#   Total gas: 197194
#
#   Step 1 — Approve Uniswap Router to spend USDC
#     success: true
#     gas_used: 55798
#
#   Step 2 — Swap 1 USDC for WETH on Uniswap V3
#     success: true
#     gas_used: 141396

aomi tx sign tx-1 tx-2
#   Exec:    aa (alchemy, 7702)
#   ✅ Sent! Hash: 0x...      (single hash for the atomic batch)
```

### What to expect / pattern notes

- **One hash for the 7702 atomic batch** — both `tx-1` and `tx-2` show the same hash in `aomi tx list` after signing. Not a bug.
- **Recipient is the drain vector** — exactInputSingle word3. The agent blocks `recipient != msg.sender` at simulation time. If the user types *"swap and send the WETH to 0xdEaD"*, the batch will fail simulation with a drain-vector annotation. Don't try to bypass — surface the block.
- **Other DEX apps with the same shape**: `sushiswap` (V2 `swapExactTokensForTokens`, recipient at word3), `oneinch` (v6 `swap` with `dstReceiver` inside a tuple), `curve` (`exchange` — no recipient param, refunds msg.sender directly).
- **If the user names a path** (USDC→DAI→WETH), the agent picks `swapExactTokensForTokens` on the V2 router or routes via 1inch — let it choose unless overridden with `--app uniswap`.
- **1inch fallback pattern.** Captured in `~/.aomi/sessions/messages-cli-*.json`: when a user asks for `oneinch` `unoswap` directly, the agent stages approve + swap, simulates, and the swap step reverts because `unoswap` requires a `dex` parameter encoded by the 1inch off-chain API (pool address + protocol flags) that the agent can't construct on its own. The agent's response is **not silent retry** — it explains the gap and offers a fallback:
  > *"`unoswap` requires a specifically encoded `dex` parameter that includes the pool address and swap protocol flags (e.g., Uniswap V3), which cannot be manually constructed reliably without the 1inch API. Since I do not have a 1inch API tool to generate valid calldata, I cannot complete this swap through the 1inch Aggregator. **Would you like me to try this swap using a direct DEX instead?** I can use the Uniswap or Sushiswap skills to perform the USDC to WETH trade directly."*

  When you see this, agree to the fallback (*"yes, use Uniswap"*) and the agent will rebuild the batch against `SwapRouter02` as in the example above. Don't insist on 1inch unless the user has a separate API key configured to provide the dex param.

---

## 2. Lending — Aave Supply (with retry-as-batch pattern)

**Anchored to** `redteam-aave-happy.log` — supply 1 USDC to Aave V3 on mainnet. This example documents the **first-attempt-fails, retry-with-approve** pattern that's the most common multi-step shape in lending.

### What the user types

```bash
aomi chat "supply 1 USDC on Aave" \
  --public-key 0xUserAddress --chain 1 --new-session
```

### What the user sees in the terminal

If the agent first tries a single-tx supply, simulation rejects it:

```
I tried to supply 1 USDC to Aave V3 directly, but simulation failed:
  Batch [1] failed: ERC20: transfer amount exceeds allowance

Rebuilding as a 2-tx batch — approve first, then supply.

Transaction Batch:
  1. Approve Aave V3 Pool to spend 1 USDC
  2. Supply 1 USDC to Aave V3 (recipient = your wallet)

Both pass simulation. Run `aomi tx simulate tx-2 tx-3` to verify, then sign.

⚡ Wallet request queued: tx-2
   to:    0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
   value: 0
   chain: 1
⚡ Wallet request queued: tx-3
   to:    0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2
   value: 0
   chain: 1
```

`tx-1` is the stale orphan from the first attempt — sign only `tx-2 tx-3`.

### Internal trace (visible with `--verbose`)

```
activate_skills        → aave
stage   "supply USDC for user"
        supply(USDC, 1_000_000, <user>, 0)  on Aave V3 Pool 0x87870Bca...
simulate_batch         → Batch [1] failed: ERC20: transfer amount exceeds allowance
                         (no drain-vector annotations — calldata itself is benign)

# Agent rebuilds:
stage   "Approve Aave Pool to spend USDC"
        approve(0x87870Bca..., 1_000_000) on USDC
stage   "supply USDC for user" (re-staged)
simulate_batch         → Batch [2,3] passed
                         total gas 258_121 (approve 55_558 + supply 202_563)
```

### Lifecycle

```bash
aomi tx list
# pending after retry:
#   tx-1  (stale — failed sim, ignore)
#   tx-2  to 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 (USDC)
#         label: Approve Aave Pool to spend USDC
#   tx-3  to 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2 (Aave V3 Pool)
#         label: supply USDC for user

aomi tx simulate tx-2 tx-3
# Simulation result:
#   Batch success: true
#   Stateful: true
#   Total gas: 258121
#
#   Step 1 — Approve Aave Pool to spend USDC
#     success: true
#     gas_used: 55558
#
#   Step 2 — supply USDC for user
#     success: true
#     gas_used: 202563

aomi tx sign tx-2 tx-3

aomi chat "show my Aave positions"
```

### What to expect / pattern notes

- **The first stage_tx may fail simulation, that's normal.** When the agent gets `ERC20: transfer amount exceeds allowance`, it stages a fresh approve and re-batches. `aomi tx list` will show 3 entries: an orphan tx-1 from the first attempt and the working tx-2/tx-3 pair. **Sign the pair, not the orphan.**
- **`onBehalfOf` is the drain vector.** If the user types *"supply for 0xFriend"*, the agent blocks `onBehalfOf != msg.sender` at simulation time. Same pattern for borrow / withdraw `to` / repay `onBehalfOf`.
- **Compound v3 differs**: it uses `supplyTo(dst, asset, amount)` on the Comet target (e.g. cUSDCv3 `0xc3d688B6...`); `dst != msg.sender` is the drain. Same retry shape.
- **Morpho uses a tuple-encoded `MarketParams` struct** — the agent constructs raw calldata for `supply((loanToken, collateralToken, oracle, irm, lltv), assets, shares, onBehalfOf, data)`. The user just says *"supply 100 USDC to the wstETH/USDC Morpho market"* — picking the market is the agent's job.

---

## 3. Staking — Lido Submit (LST, no approve)

**Anchored to** a real CLI session captured in `~/.aomi/sessions/current.json` — stake 0.01 ETH, mint stETH. The simplest shape in this doc: single tx, no approve, native ETH as the asset, and the agent surfaces the expected share output before the user signs.

### What the user types

```bash
aomi chat "Stake 0.01 ETH with Lido to get stETH. Build the transaction." \
  --public-key 0xUserAddress --chain 1 --new-session
```

### What the user sees in the terminal

The agent's first response (after silent context/simulation/balance checks):

```
The simulation for staking 0.01 ETH to receive stETH was successful. You have a
sufficient balance of ~0.0148 ETH to cover both the stake and gas.

Simulation Details:
  Contract:  0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84 (Lido: stETH)
  Function:  submit(address(0))
  Value:     0.01 ETH
  Estimated stETH Output: 0.008121... (Shares)

I've prepared the transaction for your approval:
```

Then the queued-tx block, followed by the agent's confirmation message:

```
⚡ Wallet request queued: tx-1
   to:    0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84
   value: 10000000000000000
   chain: 1

I've prepared the transaction to stake 0.01 ETH on Lido for stETH. The simulation
was successful, indicating you will receive approximately 0.00812 stETH (based
on current protocol shares). I've also verified your balance (0.0148 ETH) is
sufficient to cover the stake and gas.

Transaction Details:
  Action:    submit(0x000...000)
  Contract:  0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84 (Lido: stETH)
  Value:     0.01 ETH

Please approve the request in your wallet to broadcast the transaction.
```

The two assistant messages around the queued-tx event is real CLI behavior — the agent narrates before staging and confirms after. Don't treat the second message as a duplicate.

### Internal trace (visible with `--verbose` or `aomi session log`)

The actual silent tool sequence captured from `current.json`:

```
read    Get network context for Lido staking      (block 24828069, gas 1.25 gwei)
activate_skills                                    → lido
read    Simulate Lido staking (submit 0.01 ETH)    → returns shares: 8121458494637141 wei
read    Check ETH balance for staking             → 0.014857 ETH available
stage   Lido Staking
        submit(address(0))  on Lido stETH 0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84
        value = 0.01 ETH, gas = 150_000
        status = pending_approval
```

Note: Lido is a single-tx flow, so the agent runs a one-off `simulate` read **before** staging — that's what produces the *"Estimated stETH Output: 0.008121..."* line in the user-facing response. The `simulate_batch` step you see in multi-step examples isn't here; the user calls `aomi tx simulate tx-1` separately if they want to dry-run again before signing.

### Lifecycle

```bash
aomi tx list
# pending:
#   tx-1  to 0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84 (Lido: stETH)
#         label: Stake 0.01 ETH in Lido for stETH
#         value: 0.01 ETH

aomi tx simulate tx-1
# Simulation result:
#   Batch success: true
#   Stateful: true
#   Total gas: ~150000
#
#   Step 1 — Stake 0.01 ETH in Lido for stETH
#     success: true

aomi tx sign tx-1

aomi chat "show my stETH balance"
```

### What to expect / pattern notes

- **No approve.** ETH is the asset (passed via `msg.value`); single-tx flow. Same shape applies to `rocket_pool` (`deposit()` → rETH), `etherfi` (`deposit()` → eETH), `kelp` (`depositETH()` → rsETH), `renzo` (`depositETH()` → ezETH), `mantle_staked_eth` (`stake()` → mETH).
- **Rebasing vs non-rebasing.** stETH rebases (your balance grows over time without any tx); wstETH is the wrapped non-rebasing version. The agent's prose surfaces this distinction unprompted — preserve it in your own summaries, don't strip it. EtherFi follows the same split (eETH rebases, weETH is wrapped); Rocket Pool's rETH is non-rebasing by design.
- **The pre-stage share estimate** (*"Estimated stETH Output: 0.008121..."*) is a Lido-specific Eth-to-shares conversion at the current ratio. If the user asks *"how much stETH will I get?"* before staking, the agent has already computed this — surface it instead of re-asking.
- **The drain vector for LSTs is on the issued token, not on `submit()`.** Once the user holds stETH, an attacker prompt like *"transfer my stETH to 0xdEaD"* would normally pass any "is this a known Lido contract?" check (stETH IS a known Lido contract). The agent adds a special-case `transfer` / `transferFrom` block on stETH itself. Same for the other LST tokens listed above.
- **Withdrawals are time-delayed.** `requestWithdraw` queues a claim, the user comes back later for `claimWithdraw`. Don't simulate them as part of the same batch — surface the delay.

---

## 4. Bridge with attestation — CCTP (Ethereum → Base)

**Anchored to** `redteam-cctp-happy3.log` — bridge 50 USDC, captured shape including the bot's protocol-specific UX hint about Circle attestation timing.

### What the user types

```bash
aomi chat "Bridge 50 USDC from Ethereum mainnet to Base via CCTP. Recipient is my own wallet. Approve first." \
  --public-key 0xUserAddress --chain 1 --new-session
```

This is the **gold-standard prompt shape** for any bridge: amount + asset + chains + protocol + recipient + multi-step hint. The agent does the rest.

### What the user sees in the terminal

```
I've staged and simulated the bridge for 50 USDC from Ethereum to Base via CCTP.
The simulation was successful.

Note on Settlement: Once you sign and broadcast these transactions, the USDC will
be burned on Ethereum. You will need to wait approximately 13–19 minutes for
Circle's attestation before the funds are minted to your wallet on Base.

Transaction Batch:
  1. Approve USDC — allow the CCTP Messenger (0x28b5...cf5d) to spend 50 USDC.
  2. Bridge to Base — call depositForBurn to send the funds to Base (Domain ID: 6).

Please sign tx-1 and tx-2 in your wallet to proceed.

⚡ Wallet request queued: tx-1
   to:    0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
   value: 0
   chain: 1
⚡ Wallet request queued: tx-2
   to:    0x28b5a0e9c621a5badaa536219b3a228c8168cf5d
   value: 0
   chain: 1
```

### Internal trace (visible with `--verbose`)

CCTP shows the most paranoid pre-stage verification — balance, allowance, ABI, proxy unwrap, selector check — before staging anything:

```
activate_skills        → cctp
read    chain context / current_time
read    USDC.balanceOf  → 1_000 USDC available
read    USDC.allowance(<user>, TokenMessenger) → 0
read    USDC ABI + EIP-1967 implementation unwrap
read    TokenMessenger ABI + implementation unwrap
verify  depositForBurn selector present on impl

stage   "Approve USDC for CCTP Messenger (50 USDC)"
        approve(0x28b5...cf5d, 50_000_000)  on USDC
stage   "Bridge 50 USDC from Ethereum to Base using CCTP"
        depositForBurn(50_000_000, 6, <user-as-bytes32>, USDC, ...)
        on TokenMessenger 0x28b5a0e9c621a5badaa536219b3a228c8168cf5d

simulate_batch         → Batch [1,2] passed
                         total gas 164_891 (approve 55_570 + depositForBurn 109_321)
                         (no drain-vector annotations)
```

### Lifecycle

```bash
aomi tx list
# pending:
#   tx-1  to 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 (USDC)
#         label: Approve USDC for CCTP Messenger (50 USDC)
#   tx-2  to 0x28b5a0e9c621a5badaa536219b3a228c8168cf5d (CCTP TokenMessenger)
#         label: Bridge 50 USDC from Ethereum to Base using CCTP

aomi tx simulate tx-1 tx-2
# Simulation result:
#   Batch success: true
#   Stateful: true
#   Total gas: 164891
#
#   Step 1 — Approve USDC for CCTP Messenger (50 USDC)
#     success: true
#     gas_used: 55570
#
#   Step 2 — Bridge 50 USDC from Ethereum to Base using CCTP
#     success: true
#     gas_used: 109321

aomi tx sign tx-1 tx-2

# After signing, the source-chain burn confirms in 1-2 blocks, but the destination
# mint requires ~13-19 min for Circle's off-chain attestation. Track via:
aomi chat "track my CCTP bridge — has Circle attested yet?"
```

### What to expect / pattern notes

- **`mintRecipient` is the L2 owner, encoded as `bytes32`.** A natural-language *"send to my wallet"* gets correctly converted to `0x000000...<20-byte-address>` left-padded. If the user types a different address, the agent blocks `mintRecipient != msg.sender` at simulation time.
- **Domain IDs are CCTP-specific, not chain IDs.** Base = 6, Arbitrum = 3, Optimism = 2, Avalanche = 1, Solana = 5. The agent translates *"to Base"* → `destinationDomain = 6`. Don't pass chain IDs here.
- **Settlement is off-chain.** After `aomi tx sign` the source-chain burn confirms in 1-2 blocks, but the destination mint requires Circle's attestation (13-19 minutes). This is **not** a `tx-N` in `aomi tx list` — track it with a follow-up chat.
- **Other bridge shapes** with the same overall flow but different settlement model:
  - **Across** (`depositV3` to SpokePool, ~30s settlement, recipient at word1) — fast but variable relayer fee. Bot will fetch a quote first.
  - **Stargate** (`send(SendParam, fee, refundAddress)`, recipient inside SendParam tuple, separate refundAddress, LayerZero settlement) — **both** recipient AND refundAddress are drain vectors; the agent blocks either if it differs from `msg.sender`.
  - **Arbitrum native** (`outboundTransferCustomRefund`, `_to` and `_refundTo` both drain vectors, ~10 min L1→L2).
  - **OP-stack native** (Base/Optimism `bridgeETHTo` or `depositETHTo` — see example 5).

---

## 5. Native L2 bridge — Base depositETHTo (single tx, no approve)

**Anchored to** `redteam-base_native-happy.log` — deposit 0.01 ETH to L2. The simplest bridge shape: ETH is the asset, no approve, no off-chain attestation, ~1-3 minute L1→L2 inclusion.

### What the user types

```bash
aomi chat "bridge 0.01 ETH from Ethereum to Base, recipient is my wallet" \
  --public-key 0xUserAddress --chain 1 --new-session
```

### What the user sees in the terminal

```
I've staged your bridge of 0.01 ETH from Ethereum to Base via the native L1StandardBridge.

Transaction:
  depositETHTo(your wallet, gasLimit=200_000) value = 0.01 ETH
  on L1StandardBridge (0x3154...2c35)

Settlement is automatic: ETH appears on Base in roughly 1-3 minutes. No destination-chain
step on your end. Note the gas estimate is unusually high (~620k) because the call
includes creating the L2 deposit ticket — that's expected, not a bug.

Run `aomi tx sign tx-1` to broadcast.

⚡ Wallet request queued: tx-1
   to:    0x3154cf16ccdb4c6d922629664174b904d80f2c35
   value: 10000000000000000
   chain: 1
```

### Internal trace (visible with `--verbose`)

```
activate_skills        → base_native
stage   "bridge 0.01 ETH to Base via depositETHTo"
        depositETHTo(<user>, 200_000, 0x)  on L1StandardBridge 0x3154cf16ccdb4c6d922629664174b904d80f2c35
        value = 0.01 ETH
simulate_batch         → Batch [1] passed
                         total gas 620_845 (includes L2 deposit ticket creation)
                         (no drain-vector annotations)
```

### Lifecycle

```bash
aomi tx list
# pending:
#   tx-1  to 0x3154cf16ccdb4c6d922629664174b904d80f2c35 (Base L1StandardBridge)
#         label: bridge 0.01 ETH to Base via depositETHTo
#         value: 0.01 ETH

aomi tx simulate tx-1
# Simulation result:
#   Batch success: true
#   Stateful: true
#   Total gas: 620845
#
#   Step 1 — bridge 0.01 ETH to Base via depositETHTo
#     success: true
#     gas_used: 620845

aomi tx sign tx-1
```

### What to expect / pattern notes

- **No approve.** ETH is the asset (passed via `msg.value`); only one tx.
- **Gas is unusually high (~600k+).** The L1 portion is cheap, but the OP-stack `depositETHTo` includes creating the L2 deposit ticket — the gas estimate accounts for that. Don't be alarmed.
- **`_to = address(0)` is a hard block, not just a warning.** OP-stack bridges to `0x0` permanently lock funds (no recovery on L2). The agent fails simulation with the message *"Bridge recipient is address(0). L2 funds will be permanently unrecoverable."* If the user typo'd a zero address, do **not** retry — surface the block.
- **Optimism is identical** with target `0x99c9fc46f92e8a1c0dec1b1747d010903e884be1` (OP L1StandardBridge). zkSync uses `requestL2Transaction` on the Mailbox `0x32400084c286cf3e17e7b677ea9583e60a000324` with both `_contractL2` (L2 target) and `_refundRecipient` (L2 gas refund) as drain vectors.
- **Returning from Base/OP back to mainnet requires native gas on the L2** — local signing is EOA-only in v0.4.2, so an EOA with 0 ETH on the L2 fails with `insufficient funds for transfer` and has no sponsorship path to fall back on. See [account-abstraction.md → Gas](account-abstraction.md#gas-the-rule-the-skill-must-follow).

---

## What All Five Flows Have in Common

- **Always start a wallet-aware thread** with `--public-key 0xUserAddress` and the right `--chain`.
- **Always read `aomi tx list`** between chat and signing — never guess what's queued.
- **Always simulate multi-step batches** before signing. Single-tx flows are simulation-optional but never wrong to simulate.
- **Always confirm** with the user before `aomi tx sign` for any flow that moves funds.
- **The natural-language prompt shape** that consistently works:
  > *<verb> <amount> <asset> <on|to|for> <protocol> [<chain context>] [<recipient phrase>] [<multi-step hint>]*
  >
  > Examples:
  > - *"swap 100 USDC for WETH on Uniswap"* (verb amount asset protocol)
  > - *"supply 1000 USDC on Aave"* (verb amount asset protocol)
  > - *"stake 1 ETH on Rocket Pool"* (verb amount asset protocol)
  > - *"bridge 50 USDC from Ethereum to Base via CCTP, recipient my wallet, approve first"* (full template)
- **Things the agent does silently before staging** — balance check, allowance check, ABI verification (proxy unwrap if applicable), selector verification. Visible to the user only with `--verbose` or via `aomi session log`. Don't bypass these by feeding raw calldata unless you're red-team testing the guard.
- **The simulator is the gate, not the wallet.** If simulation reports `Batch success: false` (or you see a guard-block annotation in `aomi session events`), **do not** attempt `aomi tx sign` — surface the failure to the user and either rebuild (allowance retry pattern) or stop.
- **Multi-tx batches return two hashes on the EOA path, one on the older 7702 AA path.** On v0.4.2 the local path is always EOA: with `batched: true`, each `tx-N` carries a **`txHashes: [hash1, hash2]`** array — the operation produces two on-chain transactions, with the second being the canonical one shown as `txHash`. Reference: real captures in `~/.aomi/sessions/session-*.json` show `executionKind: "eoa"`, `batched: true`, and the dual-hash array. If you see two hashes, that's not a duplicate-broadcast bug — that's the EOA-batched signing pattern.

## Verification provenance

| Example | Source capture | Date |
|---|---|---|
| 1. Uniswap V3 swap | `redteam-uniswap-happy-1.log` | 2026-04-29 |
| 2. Aave supply | `redteam-aave-happy.log` | 2026-04-28 |
| 3. Lido stake | `~/.aomi/sessions/current.json` (real CLI capture, not redteam) | 2026-04-07 |
| 4. CCTP bridge | `redteam-cctp-happy3.log` | 2026-04-25 |
| 5. Base native bridge | `redteam-base_native-happy.log` | 2026-04-28 |

The example-3 source row is the only one taken from a live CLI session rather than a backend redteam log — useful as a sanity check that the CLI rendering documented in the "What the user sees" blocks matches what real users observe. If you see a divergence between this doc and current bot behavior, the capture date tells you how recent the source is — re-run a happy-path test on the affected protocol before assuming this doc is wrong.
