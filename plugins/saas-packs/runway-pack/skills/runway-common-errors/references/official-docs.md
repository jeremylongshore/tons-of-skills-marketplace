# First-party Runway evidence

Consulted on 2026-09-13 for `runway-common-errors`.

## Authority boundary

Runway documentation defines the API, authentication, models, task lifecycle, inputs, outputs, moderation, limits, pricing, SDK, and production behavior. This skill treats local examples as implementation guidance, not a pricing promise, rights determination, safety approval, availability guarantee, or proof that generated media meets product policy.

## Sources used

- [Agent context primer](https://docs.dev.runwayml.com/ai-context.md)
- [Generated API reference](https://docs.dev.runwayml.com/api.md)
- [API setup](https://docs.dev.runwayml.com/guides/setup.md)
- [API getting started](https://docs.dev.runwayml.com/guides/using-the-api.md)
- [Official SDKs](https://docs.dev.runwayml.com/api-details/sdks.md)
- [Usage tiers](https://docs.dev.runwayml.com/usage/tiers.md)
- [Pricing](https://docs.dev.runwayml.com/guides/pricing.md)
- [HTTP errors](https://docs.dev.runwayml.com/errors/errors.md)
- [Task failures](https://docs.dev.runwayml.com/errors/task-failures.md)
- [Moderation](https://docs.dev.runwayml.com/api-details/moderation.md)
- [Inputs](https://docs.dev.runwayml.com/assets/inputs.md)
- [Outputs](https://docs.dev.runwayml.com/assets/outputs.md)
- [Ephemeral uploads](https://docs.dev.runwayml.com/assets/uploads.md)
- [Models](https://docs.dev.runwayml.com/guides/models.md)
- [Production checklist](https://docs.dev.runwayml.com/guides/go-live.md)
- [API changelog](https://docs.dev.runwayml.com/api-details/api_changelog.md)

## Snapshot fingerprints

- Agent context primer SHA-256: `9212210e1dec664ca50aa2545fca475e` + `813087dca3654bbcb24d3baef1c3c32f`.
- Generated API reference SHA-256: `f437722c69620ebd` + `30e24a3eeed449a4` + `188344047f9dbf21b0821c3f6035ebdd`.
- API setup SHA-256: `45844eb38fc48193` + `b17e74102aa7a360` + `2c390d4448e224ccef30d04cf6b851b6`.
- API getting started SHA-256: `a30d4f6fcdb4a6a6b864d7a48e213c58` + `ddd90c98dd65de53ccde383c4d14b16e`.
- Official SDKs SHA-256: `6ab40dfa05e1a23ccab5e0c80156c210` + `3c5ea116f1dd3a11f22f338806ba7ee0`.
- Usage tiers SHA-256: `20f3a2274ca6a530f7f1ac1f7977d117` + `c85020a51236865c6638d115161b0103`.
- Pricing SHA-256: `118afd1feeb2bf393cee6873ff1875b6` + `8801a3b0ff2ec3565ded2d6f133560b7`.
- HTTP errors SHA-256: `b8771f4edb28289c8867c2d6e14a99c0` + `52b904b9ccfbd64fb5672893ed597bc6`.
- Task failures SHA-256: `ca0b268f0c3687b087e00a4a40ee77f6` + `cda9fc6f991cd2fb31a0ca6bb7021c47`.
- Moderation SHA-256: `2f07165e7f733fa4b93a8ea2a758e711` + `406e15e6d418557965ea670253050fd9`.
- Inputs SHA-256: `0e73cc0e5987b1c1f63083494cf04932` + `ca6aa0859a5ea1533a9fb658ac6ec53e`.
- Outputs SHA-256: `bb0e42a8f3f788edfd9006bb4f8b1284` + `8f9c6cc48ad1a5ea20922e843a7681c3`.
- Ephemeral uploads SHA-256: `aa6076e04bf4decef3227bc55ca21836` + `f5b93e32de89a651b6dd1439c7d425e2`.
- Models SHA-256: `58f386bf2cd8f96eef42ea43f29817fb` + `1973a0a8ad5dc31c1be659853ad9e9b9`.
- Production checklist SHA-256: `7c59febdd6875514b2ae4cf27c7cdb0d` + `310266c1bc3dc366c5a7c11a3314d655`.
- Changelog SHA-256: `108c3d2c49fdfeb6` + `6394b268ee214282` + `faa04075fcd793a38c36e1ad5a1b9b50`.

## Product facts applied

- HTTP `400`, `401`, `404`, and `405` are not retryable without changing the cause.
- HTTP `429`, `502`, `503`, and `504` may retry with exponential backoff and jitter up to 50 percent.
- Safety task failures are non-retryable and consume credits.

## Maintenance rule

Re-fetch the linked first-party Markdown before changing API hosts, authentication, version headers, endpoint or model fields, task states, polling, cancellation, retries, input limits, output retention, moderation, usage tiers, pricing, SDK guidance, or webhook/event claims. Record the retrieval date and split SHA-256 fingerprints; do not silently preserve stale contracts.
