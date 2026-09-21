# Abridge Skill Pack

Eighteen production operator workflows for health systems deploying Abridge clinical documentation. The pack covers consent, clinician review, Linked Evidence, Epic handoff, access, synthetic testing, rollout, privacy, security, capacity, support, and change control.

Each skill is grounded in current public Abridge product or support material and clearly separates those public facts from tenant-specific implementation contracts. The pack does not claim a public Abridge SDK, REST sandbox, universal API hostname, webhook catalog, quota header, generic FHIR write, or customer-deployed Abridge backend.

## Installation

```bash
/plugin install abridge-pack@claude-code-plugins-plus
```

## Workflow Map

| Domain | Skills |
|---|---|
| Access and pilot | `abridge-install-auth`, `abridge-hello-world`, `abridge-local-dev-loop` |
| Clinical and EHR workflow | `abridge-core-workflow-a`, `abridge-core-workflow-b`, `abridge-sdk-patterns` |
| Reliability and support | `abridge-common-errors`, `abridge-debug-bundle`, `abridge-rate-limits`, `abridge-performance-tuning` |
| Delivery and operations | `abridge-ci-integration`, `abridge-deploy-integration`, `abridge-prod-checklist` |
| Governance and change | `abridge-security-basics`, `abridge-cost-tuning`, `abridge-reference-architecture`, `abridge-upgrade-migration`, `abridge-webhooks-events` |

## Current Product Boundaries

- [Recording basics](https://support.abridge.com/hc/en-us/articles/30207826574739-Recording-Basics) directs clinicians to follow organizational consent guidance, select the patient, record, create the note, and review it in the Web Editor.
- [Web Editor guidance](https://support.abridge.com/hc/en-us/articles/30279907940371-Abridge-Web-Editor-Basics) documents clinician review and editing before sending a note.
- [Linked Evidence](https://support.abridge.com/hc/en-us/articles/30235128433811-Verify-a-Note-With-Linked-Evidence) supports verification of generated text against transcript or audio; it does not replace clinician review.
- [Epic handoff guidance](https://support.abridge.com/hc/en-us/articles/30235172323731-Send-an-Abridge-Note-Into-Epic) documents Send Now and SmartLink behavior, including manual-path limitations.
- The [Abridge Trust Center](https://trust.abridge.com/) and [data-security guidance](https://support.abridge.com/hc/en-us/articles/30235294201619-Data-Security) provide public posture evidence. Tenant control details still require approved contract and implementation records.

See each skill's `references/official-docs.md` for its dated source set and evidence boundary.

## Safety Boundary

Use synthetic data or the health system's designated test-record process. Do not copy patient audio, transcripts, note text, identifiers, credentials, private vendor specifications, or Trust Center reports into repositories, ordinary tickets, examples, or test fixtures.

## License

MIT
