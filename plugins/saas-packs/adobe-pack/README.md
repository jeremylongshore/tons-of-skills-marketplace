# Adobe Skill Pack

Thirty evidence-backed Claude Code workflows for operating Adobe Firefly, Photoshop API v2, PDF Services, Adobe I/O Events, App Builder, Developer Console identity, and enterprise access.

Every skill includes a dated first-party Adobe evidence map, explicit approval boundaries, negative-path validation, and content-safe output requirements. The pack does not teach Service Account JWT, Photoshop API v1, `/sensei/cutout`, the retired Firefly Services Lightroom API, fixed universal rate limits, invented latency benchmarks, or guessed pricing.

## Installation

```bash
/plugin install adobe-pack@claude-code-plugins-plus
```

## Operator lanes

| Lane | Skills | Outcome |
|---|---:|---|
| Identity and governance | 5 | Correct S2S vs user auth, entitlement, product profiles, safe rotation, access review |
| Firefly, Photoshop, and PDF | 6 | Current async jobs, Photoshop v2, document custody, output validation, cleanup |
| Events and App Builder | 5 | Authentic event delivery, isolated workspaces, CI, deploy, local Runtime fidelity |
| Reliability and operations | 9 | Error triage, diagnostics, backpressure, incidents, observability, capacity, readiness |
| Architecture and migration | 5 | Current reference designs, variant decisions, environment isolation, EOL-safe migrations |

## Current non-negotiables

- OAuth Server-to-Server is for application- or organization-owned data; user-owned data requires Adobe User Authentication and explicit consent.
- Adobe Service Account JWT is deprecated and is not a fallback.
- Photoshop API v1 and the Firefly Services Lightroom API reached end of life on July 31, 2026.
- Firefly and other asynchronous workflows follow returned status and cancellation URLs with bounded polling and reconciliation.
- PDF inputs and outputs have an explicit custody, retention, signed-URL, and deletion contract.
- I/O Events handlers authenticate delivery, deduplicate at-least-once events, and acknowledge before asynchronous processing.
- AIO CLI v11+ deploys App Builder through IMS login or OAuth Server-to-Server CI credentials, not Runtime namespace auth.
- Mutable limits, pricing, SDK versions, model versions, and supported storage domains are rechecked at execution time.

## Quality contract

All 30 `SKILL.md` files target marketplace Grade A and Tier-2 GREEN under `validate-skillmd`. Each skill uses only `Read`, `Glob`, `Grep`, `Write`, and `Edit`; a skill invocation does not authorize network access, credentials, Adobe content, consent, uploads, generation, spend, deployment, registration changes, replay, cancellation, credential deletion, or asset deletion.

## Source and support

- Marketplace: <https://tonsofskills.com/>
- Adobe Developer Console documentation: <https://developer.adobe.com/developer-console/docs/guides/>
- Adobe Firefly Services documentation: <https://developer.adobe.com/firefly-services/docs/>
- Adobe PDF Services documentation: <https://developer.adobe.com/document-services/docs/>
- Adobe I/O Events documentation: <https://developer.adobe.com/events/docs/>
- Adobe App Builder documentation: <https://developer.adobe.com/app-builder/docs/>
- Adobe service status: <https://status.adobe.com/>

License: MIT.
