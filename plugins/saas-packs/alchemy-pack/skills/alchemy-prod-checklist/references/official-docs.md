# Alchemy Production Readiness Decision: first-party evidence

Reviewed: 2026-09-12

Alchemy's current public documentation establishes the general service contract. The selected account, plan, application, credential, chain, endpoint, feature support, package lock, observed responses, and dashboard settings remain execution evidence for the actual environment.

- [Feature support by chain](https://www.alchemy.com/docs/reference/feature-support-by-chain)
- [Alchemy error reference](https://www.alchemy.com/docs/reference/error-reference)
- [Throughput](https://www.alchemy.com/docs/reference/throughput)
- [Pricing plans](https://www.alchemy.com/docs/reference/pricing-plans)
- [API-key best practices](https://www.alchemy.com/docs/best-practices-when-using-alchemy)
- [Alchemy documentation](https://www.alchemy.com/docs)
- [Create an API key](https://www.alchemy.com/docs/create-an-api-key)
- [API-key header authentication](https://www.alchemy.com/docs/how-to-use-api-keys-in-http-headers)
- [Supported chains](https://www.alchemy.com/docs/reference/node-supported-chains)

## Current contract notes

- The `alchemy-sdk` JavaScript repository is archived and deprecated. New JavaScript EVM work uses viem; transacting applications and Portfolio support use `@alchemy/wallet-apis`; Solana work uses Solana Web3.js.
- Application API keys, Admin access keys, Notify management tokens, webhook signing keys, and wallet signing authority are distinct. Never substitute one credential class for another.
- RPC chain availability does not prove that a Data, NFT, Portfolio, Wallet, Simulation, or webhook feature is supported on that chain. Recheck both supported-chain and feature matrices.
- Throughput is account-level and evaluated over a rolling ten-second token-bucket window. Method costs, plan capacity, pricing, and elastic-demand behavior are mutable; use current account evidence.
- Portfolio fanout can return HTTP 200 with top-level `error.partialErrors`. Failed networks can be absent from pagination and require fresh, bounded retry requests.
- Notify signatures use HMAC-SHA256 over the exact raw request body and the per-webhook signing key, with the digest in `X-Alchemy-Signature`.
- Alchemy permits restricted frontend application-key patterns under current guidance, including allowlists, and recommends short-lived JWTs where appropriate. Admin, Notify, signing, and confidential server credentials do not move to the browser.
- Skill invocation does not grant authority to access credentials or personal data, increase capacity or spend, change registrations, deploy, replay, sign, broadcast, rotate, revoke, or delete.

## Evidence rules

- Recheck linked first-party pages at execution and record source date plus account, application, chain, feature, endpoint, and version identities.
- Prefer returned headers, request IDs, response states, dashboard observations, and account terms over remembered constants.
- When first-party pages conflict or observed behavior differs, fail closed, preserve redacted evidence, and resolve the discrepancy before a side effect.
