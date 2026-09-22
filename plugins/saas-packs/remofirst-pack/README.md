# RemoFirst Operator Skill Pack

> Evidence-backed Claude Code workflows for RemoFirst EOR, contractors, payroll,
> security, support, and supported HRIS connectors (12 skills)

## What This Covers

This pack helps authorized RemoFirst client operators plan and review sensitive
work without letting an agent silently approve payroll, move money, disclose
worker data, or change production records. Each skill links to dated first-party
evidence and defines its human approval boundary.

The reviewed public RemoFirst documentation describes the client platform,
operator-controlled reports and CSV workflows, and named Workday and ADP
connectors. It does **not** publish a general first-party API/SDK, endpoint,
authentication, versioning, quota, or retry contract. If RemoFirst gives a
customer a private integration contract, that written contract is authoritative.

## Installation

```bash
/plugin install remofirst-pack@claude-code-plugins-plus
```

## Skills Included

| Skill | Operator lane |
| --- | --- |
| `remofirst-install-auth` | Activate a client account, enable 2FA, and assign least-privileged groups |
| `remofirst-hello-world` | Perform a metadata-only first-session readiness check |
| `remofirst-local-dev-loop` | Rehearse workflows locally with entirely synthetic data |
| `remofirst-sdk-patterns` | Select a supported Workday, ADP, report, CSV, or private-contract boundary |
| `remofirst-core-workflow-a` | Control country-specific EOR employee onboarding |
| `remofirst-core-workflow-b` | Control contractor onboarding through first funded payout |
| `remofirst-common-errors` | Triage workflow, payroll, invoice, payment, access, and connector failures |
| `remofirst-debug-bundle` | Prepare a privacy-safe support escalation bundle |
| `remofirst-rate-limits` | Plan operational cutoffs and connector cadence without invented API quotas |
| `remofirst-security-basics` | Review 2FA, groups, exports, credentials, DPA, and worker-data handling |
| `remofirst-prod-checklist` | Gate payroll approval and invoice funding with two-person controls |
| `remofirst-upgrade-migration` | Cut over a supported workflow or connector with reconciliation and rollback |

## Operating Boundary

- Use redacted counts, totals, hashes, mappings, and state summaries in artifacts.
- Keep credentials, recovery codes, worker documents, bank data, tax data, and
  payroll rows out of repositories and support bundles.
- Require explicit human approval for account/group changes, production syncs,
  onboarding submission, payroll/time approval, offboarding, and payment.
- Confirm country rules, live payroll dates, and customer-specific contracts with
  RemoFirst or qualified owners for the actual worker and period.

## Primary Documentation

- [RemoFirst client resource hub](https://knowledgebase.remofirst.com/hc/en-us/articles/42339401785620-RemoPack-Clients-Resource-Hub)
- [Workday connector guide](https://knowledgebase.remofirst.com/hc/en-us/articles/53164120410644-Workday-RemoFirst-Integration-Client-Guide)
- [ADP connector guide](https://knowledgebase.remofirst.com/hc/en-us/articles/39824562179348-ADP-Workforce-Now-Connecting-to-RemoFirst)
- [RemoFirst support](https://knowledgebase.remofirst.com/hc/en-us/articles/40237072233236-How-do-I-contact-RemoFirst-for-support)

## License

MIT
