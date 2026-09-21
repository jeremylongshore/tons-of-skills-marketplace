# Persona Operator Skill Pack

> Eighteen production-grade Claude Code skills for Persona inquiry lifecycles, verification evidence, authentic webhooks, privacy, rate control, delivery, and recovery.

## Installation

```bash
/plugin install persona-pack@claude-code-plugins-plus
```

The pack assumes an authorized Persona environment, the correct REST base `https://api.withpersona.com/api/v1`, and a deliberately pinned dated API version. It does not provide legal advice or turn provider verification status into an automatic customer decision.

## Skills

| Skill | Operator outcome |
| --- | --- |
| `persona-install-auth` | Establish environment-scoped, least-privilege API authentication |
| `persona-hello-world` | Prove a replay-safe sandbox inquiry create-and-read path |
| `persona-local-dev-loop` | Run deterministic synthetic and raw-webhook fixture loops |
| `persona-sdk-patterns` | Build a tolerant typed JSON:API adapter |
| `persona-core-workflow-a` | Operate account-linked inquiry and session lifecycles |
| `persona-core-workflow-b` | Separate verification evidence from business decisions |
| `persona-common-errors` | Triage API, inquiry, session, webhook, and throttle failures |
| `persona-debug-bundle` | Produce a redacted, hashed diagnostic manifest |
| `persona-rate-limits` | Control environment limits and product quotas from live evidence |
| `persona-security-basics` | Protect PII, keys, session tokens, webhooks, and redaction |
| `persona-prod-checklist` | Gate production with accountable evidence and rollback |
| `persona-upgrade-migration` | Migrate dated API versions with canary and rollback |
| `persona-ci-integration` | Enforce offline contracts and bounded sandbox smoke tests |
| `persona-deploy-integration` | Release immutable configuration without event loss |
| `persona-webhooks-events` | Authenticate, deduplicate, order, and reconcile events |
| `persona-performance-tuning` | Replace polling with event-driven bounded reconciliation |
| `persona-cost-tuning` | Remove accidental usage without weakening policy |
| `persona-reference-architecture` | Design an account-linked KYC control plane |

## Non-negotiable boundaries

- REST calls use environment-scoped bearer authentication and an explicit `Persona-Version`.
- Webhook signatures cover `timestamp + "." + rawBody`; duplicate and out-of-order delivery are expected.
- Inquiry session tokens are client capabilities, not API keys, and should not be logged.
- Identity evidence, provider status, and the application’s decision policy remain separate.
- Redaction is destructive and governed; sandbox contains no real verification outcome.

Each skill contains a first-party evidence file with a retrieval date and split SHA-256 fingerprints so documentation drift is reviewable.

## Documentation

- [Persona API introduction](https://docs.withpersona.com/api-introduction)
- [Creating inquiries](https://docs.withpersona.com/creating-inquiries)
- [Inquiry sessions](https://docs.withpersona.com/inquiry-sessions)
- [Webhook best practices](https://docs.withpersona.com/webhooks-best-practices)
- [Rate limiting](https://docs.withpersona.com/rate-limiting)
- [Versioning](https://docs.withpersona.com/versioning)

## License

MIT
