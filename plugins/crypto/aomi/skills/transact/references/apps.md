# Apps Reference

Read this when:

- The user asks "what apps are available?" or names a category (CEX, lending, perps, prediction, social).
- You need to pick `--app` for a request and want to see the catalog.
- You need a usage example for a specific app.

## Discovering Apps

The set of installed apps is dynamic — the catalog below is a snapshot. Always confirm against the live CLI:

```bash
aomi app list       # enumerate apps exposed by the backend
aomi app current    # show the currently active app
```

Select an app for a chat turn with `--app <name>` or set `AOMI_APP=<name>` for a multi-command shell. When an app needs provider credentials, the aomi CLI reports at runtime what is missing. The user configures those credentials themselves; the skill does not perform that setup unless the user explicitly asks (see SKILL.md "Secret Ingestion").

## App Catalog

All apps share a common base toolset (`send_transaction_to_wallet`, `encode_and_simulate`, `get_account_info`, `get_contract_abi`, etc.). The tools listed below are the app-specific additions. The "Credentials" column indicates whether an app needs user-configured credentials at all; the CLI reports the specific names at runtime when something is missing.

| App | Description | App-Specific Tools | Credentials |
|-----|-------------|-------------------|-------------|
| `default` | General-purpose on-chain agent with web search | `brave_search` | None |
| `binance` | Binance CEX — prices, order book, klines | `binance_get_price`, `binance_get_depth`, `binance_get_klines` | Exchange credentials |
| `bybit` | Bybit CEX — orders, positions, leverage | `brave_search` (no Bybit-specific tools yet) | Exchange credentials |
| `cow` | CoW Protocol — MEV-protected swaps via batch auctions | `get_cow_swap_quote`, `place_cow_order`, `get_cow_order`, `get_cow_order_status`, `get_cow_user_orders` | None |
| `defillama` | DefiLlama — TVL, yields, volumes, stablecoins | `get_token_price`, `get_yield_opportunities`, `get_defi_protocols`, `get_chain_tvl`, `get_protocol_detail`, `get_dex_volumes`, `get_fees_overview`, `get_protocol_fees`, `get_stablecoins`, `get_stablecoin_chains`, `get_historical_token_price`, `get_token_price_change`, `get_historical_chain_tvl`, `get_dex_protocol_volume`, `get_stablecoin_history`, `get_yield_pool_history` | None |
| `dune` | Dune Analytics — execute and fetch SQL queries | `execute_query`, `get_execution_status`, `get_execution_results`, `get_query_results` | Provider token |
| `dydx` | dYdX perpetuals — markets, orderbook, candles, trades | `dydx_get_markets`, `dydx_get_orderbook`, `dydx_get_candles`, `dydx_get_trades`, `dydx_get_account` | None |
| `gmx` | GMX perpetuals — markets, positions, orders, prices | `get_gmx_prices`, `get_gmx_signed_prices`, `get_gmx_markets`, `get_gmx_positions`, `get_gmx_orders` | None |
| `hyperliquid` | Hyperliquid perps — mid prices, orderbook | `get_meta`, `get_all_mids` | None |
| `kaito` | Kaito — crypto social search, trending, mindshare | `kaito_search`, `kaito_get_trending`, `kaito_get_mindshare` | Provider token |
| `kalshi` | Kalshi prediction markets via Simmer SDK | `simmer_register`, `simmer_status`, `simmer_briefing` | SDK token |
| `khalani` | Khalani cross-chain intents — quote, build, submit | `get_khalani_quote`, `build_khalani_order`, `submit_khalani_order`, `get_khalani_order_status`, `get_khalani_orders_by_address` | None |
| `lifi` | LI.FI aggregator — cross-chain swaps & bridges | `get_lifi_swap_quote`, `place_lifi_order`, `get_lifi_bridge_quote`, `get_lifi_transfer_status`, `get_lifi_chains` | Optional provider token |
| `manifold` | Manifold prediction markets — search, bet, create | `list_markets`, `get_market`, `get_market_positions`, `search_markets`, `place_bet`, `create_market` | Provider token |
| `molinar` | Molinar on-chain world — move, explore, chat | `molinar_get_state`, `molinar_look`, `molinar_move`, `molinar_jump`, `molinar_chat`, `molinar_get_chat`, `molinar_get_new_messages`, `molinar_get_players`, `molinar_collect_coins`, `molinar_explore`, `molinar_create_object`, `molinar_customize`, `molinar_ping` | None |
| `morpho` | Morpho lending — markets, vaults, positions | `get_markets`, `get_vaults`, `get_user_positions` | None |
| `neynar` | Farcaster social — users, search | `get_user_by_username`, `search_users` | Provider token |
| `okx` | OKX CEX — tickers, order book, candles | `okx_get_tickers`, `okx_get_order_book`, `okx_get_candles` | Exchange credentials |
| `oneinch` | 1inch DEX aggregator — quotes, swaps, allowances | `get_oneinch_quote`, `get_oneinch_swap`, `get_oneinch_approve_transaction`, `get_oneinch_allowance`, `get_oneinch_liquidity_sources` | Provider token |
| `para` | Para — MPC wallet management across EVM, Solana, Cosmos (threshold signing) | (Para wallet tools — confirm with `aomi app current` after selecting) | Provider token |
| `para-consumer` | Para Consumer — consumer-wallet helper: prices, yield, swap quotes, bridge routes | (Consumer-facing read tools — confirm via runtime) | Provider token |
| `polymarket` | Polymarket prediction markets — search, trade, CLOB | `search_polymarket`, `get_polymarket_details`, `get_polymarket_trades`, `resolve_polymarket_trade_intent`, `build_polymarket_order_preview` | None |
| `polymarket-rewards` | Polymarket LP — liquidity provisioning into reward-enrolled markets, ranked by reward APY | (LP scoring + position tools — confirm via runtime) | Provider token |
| `x` | X/Twitter — users, posts, search, trends | `get_x_user`, `get_x_user_posts`, `search_x`, `get_x_trends`, `get_x_post` | Provider token |
| `yearn` | Yearn Finance — vault discovery, details | `get_all_vaults`, `get_vault_detail`, `get_blacklisted_vaults` | None |
| `zerox` | 0x DEX aggregator — swaps, quotes, liquidity | `get_zerox_swap_quote`, `place_zerox_order`, `get_zerox_swap_chains`, `get_zerox_allowance_holder_price`, `get_zerox_liquidity_sources` | Provider token |

When a "Credentials" entry says *Exchange credentials*, *Provider token*, or *SDK token*, ask the user to configure that app's credentials in their own terminal (or — only if they explicitly ask — run `aomi secret add` with the value they supply).

To build a new app from an API spec or SDK, use the companion skill **aomi-build**.

## Usage Examples

Each example shows the canonical first chat turn for that category. Follow the standard workflow afterwards: `aomi tx list` → (`aomi tx simulate` for multi-step) → `aomi tx sign`.

### Solver Networks — `khalani`

Cross-chain intents executed by a solver network. Khalani returns multiple solver routes per quote; prefer the one that offers a `TRANSFER` deposit method when present.

**Get a quote (read).** Requires `--public-key` even for read-only quotes — without it the agent refuses with "I need a connected wallet to fetch a Khalani quote."

```bash
aomi chat "quote bridging 50 USDC from Polygon to Base via Khalani. Prefer a TRANSFER deposit method if available." \
  --app khalani --public-key 0xUserAddress --chain 137 --new-session
```

Verified response shape (historical real-backend capture; re-check against the current backend before treating exact app output as stable):

```
Route Options:
  1. Hyperstream (Native Filler)  ⭐ supports TRANSFER
     Deposit Methods:  CONTRACT_CALL, TRANSFER
     Amount Out:       49.950049 USDC
     Duration:         ~10s
     Fee:              ~0.05 USDC (~0.1%)
  2. Across
     Deposit Methods:  CONTRACT_CALL only
     Amount Out:       49.984261 USDC
     Duration:         ~2s
     Gas:              0.032 POL (~$0.02)
  3. DeBridge
     Deposit Methods:  CONTRACT_CALL only
     Amount Out:       49.681958 USDC
     Duration:         ~2 min
     Gas:              0.108 POL (~$0.08)
```

**Build and submit the order (write).** After the user picks a route, confirm in the same thread:

```bash
aomi chat "proceed with Hyperstream using the TRANSFER method"
aomi tx list                               # confirm the wallet request was queued
aomi tx sign tx-1 --rpc-url <polygon-rpc>  # source-chain RPC must match
```

Notes:

- Khalani internally exposes Across, DeBridge, and other solvers as routes. If the standalone `across` app is unavailable on the active backend, go through Khalani and pick the Across route at quote time.
- Single-chain intents work too: `--app khalani --chain 1` for an Ethereum-only request.
- Inspect open orders: `aomi chat "list my open Khalani orders" --app khalani --public-key 0xUserAddress` (read-only, but still wallet-aware).
- If the agent returns a quote without queueing a wallet request, that's expected — you have to explicitly say "proceed".

### Cross-Chain — `zerox`

0x aggregator for swaps and cross-chain liquidity. Good for "best-price" single-chain swaps and for swaps spanning chains where 0x has coverage.

```bash
# Best-price swap on Base
aomi chat "best price to swap 1 ETH for USDC on Base via 0x" \
  --app zerox --chain 8453 --new-session

# Cross-chain swap — let the aggregator pick the route
aomi chat "swap 100 USDC on Arbitrum for ETH on Optimism via 0x" \
  --app zerox

# List supported chains
aomi chat "which chains does 0x support today?" --app zerox
```

Notes:

- `zerox` requires a provider token. If `aomi tx sign` fails because credentials are missing, ask the user to configure their 0x credentials (do not invent or paste them on the user's behalf).
- For approve-and-swap on a single chain, simulate the batch with `aomi tx simulate tx-1 tx-2` before signing.

### Prediction Markets — `polymarket`

Search markets, inspect details, build trade previews on Polymarket's CLOB. Polymarket lives on Polygon — pass `--chain 137`.

**Find markets (read).** No wallet required for search:

```bash
aomi chat "find 3 active Polymarket markets about US politics in 2026; list them with id and current YES price" \
  --app polymarket --new-session
```

Verified response shape (historical real-backend capture; re-check against the current backend before treating exact app output as stable):

```
1. Trump out as President before GTA VI?
   Market ID: 540820   YES: 0.52   Liquidity: $19,447   Volume: $622,047
2. Xi Jinping out before 2027?
   Market ID: 559651   YES: 0.0775 Liquidity: $108,298  Volume: $8,416,434
3. Will Gavin Newsom win the 2028 Democratic presidential nomination?
   Market ID: 559652   YES: 0.2705 Liquidity: $678,162  Volume: $24,719,477
```

**Build a buy preview (write-leaning).** Requires `--public-key` and `--chain 137`. Returns an unsigned preview the user must explicitly confirm before any tx is queued:

```bash
aomi chat "build a YES buy preview for \$5 on Polymarket market 559651. Just build the preview, do not place it." \
  --app polymarket --public-key 0xUserAddress --chain 137 --new-session
```

Verified preview shape:

```
Polymarket Order Preview
  Market:           Xi Jinping out before 2027?
  Market ID:        559651
  Side:             BUY YES
  Order Type:       Market Order (Fill-or-Kill)
  Amount:           $5.00 USDC
  Current YES:      0.0775 (~7.75%)
  Estimated Shares: ~64.52
  Wallet:           0xUserAddress
  Network:          Polygon (137)
  Status:           Preview only — no order placed
```

**Place the order (write).** Once the user confirms:

```bash
aomi chat "place the order"
aomi tx list                                # confirm a wallet request was queued
aomi tx sign tx-1                           # EOA signing on Polygon (needs native POL for gas)
```

Notes:

- `build_polymarket_order_preview` returns an unsigned order for review. `aomi tx list` shows nothing until the user confirms with "place the order" or similar.
- `resolve_polymarket_trade_intent` maps natural-language trades ("buy YES on Xi for $5") to a concrete market+side+size before the preview step. Useful when the user describes a trade casually.
- `polymarket-rewards` is a separate app (LP-side, not trader-side) — see catalog above.

### CEX — `binance`

Read-only market data from Binance. No on-chain signing involved.

```bash
# Spot price snapshot
aomi chat "what is BTCUSDT trading at on Binance?" \
  --app binance --new-session

# Top-of-book depth
aomi chat "show me top 5 levels of the ETHUSDT order book on Binance" \
  --app binance

# Recent klines
aomi chat "1h klines for SOLUSDT for the last 24 hours from Binance" \
  --app binance
```

Notes:

- `binance` needs Exchange credentials. The skill never invents these. If `aomi chat` fails because credentials are missing, ask the user to configure them on their side.
- This is a data app — no `tx-N` will be queued from these commands. `aomi tx list` is not part of this flow.

### Social — `neynar`

Farcaster user lookup and search via Neynar.

```bash
# Look up a user
aomi chat "look up the Farcaster user 'dwr.eth' via Neynar" \
  --app neynar --new-session

# Search by handle
aomi chat "search Farcaster for users matching 'aomi'" --app neynar
```

Notes:

- `neynar` requires a provider token. Same rule as the other token-gated apps: ask the user to configure it.
- Like `binance`, this is a read-only data app — no wallet requests are queued.

### Social — `x`

X/Twitter user lookup, post fetching, and search.

```bash
# Look up a user
aomi chat "look up the X user @AnthropicAI - return handle, follower count, and bio" \
  --app x --new-session

# Search posts
aomi chat "search X for posts mentioning 'claude code' from the last week, top 3 with handle and text" \
  --app x

# Trending topics
aomi chat "what's trending on X right now?" --app x
```

Read-only data app — no wallet requests are queued. The X app needs a provider token configured on the backend.

> **TODO — not verified end-to-end.** On the live backend at the time of capture, both lookup and search returned "I don't have access to the X API at the moment due to authentication issues" — the X provider token was not configured for the test account. The shape of the call is correct; the backend response when the token *is* configured has not been captured here. When you have a working setup, replace this note with the real response shape (handle, follower_count, bio for `get_x_user`; array of posts for `search_x`).

### Bridging — Across (no standalone app)

If the user-facing `across` app is unavailable on the active backend, Across is still commonly reachable two ways:

1. **As a route inside Khalani.** Khalani's solver network lists Across alongside Hyperstream and DeBridge in its quote response — pick the Across route at quote time.
2. **As a tool the agent picks itself.** Asking any wallet-aware app for a bridge may produce an Across-routed wallet request even without `--app khalani`. Re-check the generated SpokePool address against the active chain before signing.

```bash
# Option 1 — via Khalani (lets Khalani's solver pick Across)
aomi chat "quote bridging 50 USDC from Polygon to Base via Khalani" \
  --app khalani --public-key 0xUserAddress --chain 137 --new-session
# Then: aomi chat "proceed with the Across route"

# Option 2 — direct (let the agent pick Across as the tool)
aomi chat "Bridge 1 USDC from Ethereum mainnet to Base via Across. Include approve as a separate tx so we can simulate the batch." \
  --public-key 0xUserAddress --chain 1 --new-session
aomi tx list
aomi tx sign tx-1 tx-2
```

Observed behavior in earlier CLI/backend captures:

- Across requests carry an expiring `fillDeadline`. If the agent's first build expires by the time simulation runs, the agent automatically rebuilds with a fresh deadline and the new tx-N will pass. **Old failed attempts remain visible in `aomi tx list`** with `batch_status: "Batch [N,M] failed at step 2: 0x..."` — sign only the txs whose status reads `Batch [...] passed`.
- The mainnet→L2 leg signs cleanly with the EOA's small ETH stash paying gas.
- The L2→mainnet leg requires the EOA to have native gas on the L2 — local signing is EOA-only, so there is no sponsor path to fall back on. See [account-abstraction.md → Gas](account-abstraction.md#gas-the-rule-the-skill-must-follow).

> **TODO — direct integration.** If a standalone `across` app gets added later, replace this stub with read + write examples in the same shape as the other entries.
