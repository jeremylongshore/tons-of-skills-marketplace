# First-party Persona evidence

Consulted on 2026-09-13 for `persona-cost-tuning`.

## Authority boundary

Persona documentation defines the API, inquiry, verification, session, webhook, environment, and redaction behavior. This skill treats local examples as implementation guidance, not legal advice, a compliance certification, a pricing promise, or proof that any person passed identity verification.

## Sources used

- [API introduction](https://docs.withpersona.com/api-introduction)
- [API quickstart](https://docs.withpersona.com/api-quickstart-tutorial)
- [API keys](https://docs.withpersona.com/api-keys)
- [Rate limits](https://docs.withpersona.com/rate-limiting)
- [Webhook best practices](https://docs.withpersona.com/webhooks-best-practices)
- [Request idempotence](https://docs.withpersona.com/idempotence)
- [Create an inquiry](https://docs.withpersona.com/api-reference/inquiries/create-an-inquiry)
- [Creating inquiries](https://docs.withpersona.com/creating-inquiries)
- [Versioning](https://docs.withpersona.com/versioning)
- [Inquiry sessions](https://docs.withpersona.com/inquiry-sessions)
- [Resuming inquiries](https://docs.withpersona.com/resuming-inquiries)
- [Verification types](https://docs.withpersona.com/verification-types)
- [Environments](https://docs.withpersona.com/environments)
- [Redact an inquiry](https://docs.withpersona.com/api-reference/inquiries/redact-an-inquiry)

## Snapshot fingerprints

- API introduction Markdown SHA-256: `63e5f1079542954e91f4f597ba40a72d` + `4841c339021bcda28aa6acf716551d5f`.
- API quickstart Markdown SHA-256: `0a264ee7a46c6503129e7a83a4c2f1db` + `502ab94b61169a5a3a4f06190d30304c`.
- API keys Markdown SHA-256: `e5dcad6d7f85b322` + `70d7c93513539c0` + `00774487bd94f0ce55b3e64b58bc6b2a88`.
- Rate limits Markdown SHA-256: `9af3d9ba3b179ef6d5d5b85dbf924988` + `5a242599ef09e55130c9652e5ce8c9d5`.
- Webhook best practices Markdown SHA-256: `a674a82497f5c4e275be680324fc84d04` + `ae672214c1ee78a32cf774434ec65db`.
- Request idempotence Markdown SHA-256: `ccf19dab3c4363e3311af34868036fdfc` + `f74bf2f85488d7843cd9fed4aa9b83b`.
- Create an inquiry Markdown SHA-256: `4e4fd95061a76849ecb8daf46ab6f21f` + `e383fe02483d2d19c46741e5e99adbab`.
- Creating inquiries Markdown SHA-256: `18640f3d2a7f542d078d42b63f1b08ff` + `cf3bd0e67bc3fb0ecd7f7b0bffff0afc`.
- Versioning Markdown SHA-256: `166d3e485847ca3273a88fe6667ae4ea` + `6d7d7924b2c57f6d5cf141b96dd5cf32`.
- Inquiry sessions Markdown SHA-256: `165edadc8d429efcfe06e35f8dbcb5d80` + `b3657004c433c78f9fc60eba0a77a9b`.
- Resuming inquiries Markdown SHA-256: `0e3e014800d2d59c32d26f70fb3ac100` + `9b752be1819327a00ba798c9774888c8`.
- Verification types Markdown SHA-256: `7518423e2b28b2b2a242e21970d84204` + `84bd554aeccf523bd66226ffde89c8b3`.
- Environments Markdown SHA-256: `a9b0c8f66207067cd76a3fc94291ebc5` + `5ff649a9c2fb4c78c24316437e98d61a`.
- Redact an inquiry Markdown SHA-256: `d6f9674f46e24ee936efab6f077d2d32` + `7069b304a3cb819bd9fe787a1a1581f5`.

## Product facts applied

- Sandbox has no usage charges and performs simulated checks.
- Idempotency keys must not be derived from customer reference IDs.
- Product quotas and environment request limits are different capacity signals.

## Maintenance rule

Re-fetch the linked first-party Markdown pages before changing authentication, API hosts, dated versions, request shapes, inquiry sessions, verification mappings, webhook signatures, limits, idempotency, environment behavior, or redaction guidance. Record the retrieval date and split SHA-256 fingerprints; do not silently preserve stale claims.
