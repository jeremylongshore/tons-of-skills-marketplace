# Workhuman Skill Pack

Eighteen contract-first operator skills for Workhuman recognition, rewards, Workday integration, security, and production operations.

## Installation

```bash
/plugin install workhuman-pack@claude-code-plugins-plus
```

## Safety and Contract Boundary

Workhuman publicly describes Social Recognition, a points-based Store, administrator controls, an open API, and managed integrations. It does not publish the universal host, OAuth exchange, `/api/v1/*` routes, payloads, quotas, webhook scheme, or SDK that appeared in the former pack. These skills require current customer-authorized tenant documentation before making any request or configuration change.

Every workflow defaults to inspection, synthetic fixtures, a mutation preview, named approval, bounded execution, reconciliation, and redacted evidence. Production worker, recognition, award, payroll, identity, connector, communication, and spend changes remain with their accountable owners.

## Skills

| Skill | Operator outcome |
|---|---|
| `workhuman-install-auth` | Select SSO, managed-connector, or API access without guessing credentials |
| `workhuman-hello-world` | Prove entitlement through one bounded read-only check |
| `workhuman-local-dev-loop` | Develop with sanitized contract fixtures and a gated live lane |
| `workhuman-sdk-patterns` | Build a typed customer-contract adapter without assuming a public SDK |
| `workhuman-core-workflow-a` | Govern recognition nominations, approvals, awards, and spend |
| `workhuman-core-workflow-b` | Reconcile certified Workday worker and award-data flows |
| `workhuman-common-errors` | Diagnose identity, eligibility, approval, spend, and integration failures |
| `workhuman-debug-bundle` | Produce a privacy-safe customer or vendor support bundle |
| `workhuman-rate-limits` | Discover and enforce tenant-specific capacity and retry rules |
| `workhuman-security-basics` | Review identity, workforce, recognition, reward, and integration controls |
| `workhuman-prod-checklist` | Issue an evidence-backed, fail-closed production decision |
| `workhuman-upgrade-migration` | Migrate API, connector, schema, identity, or program contracts safely |
| `workhuman-ci-integration` | Build fork-safe fixture and contract gates |
| `workhuman-deploy-integration` | Deploy an adapter or managed integration by canary and reconciliation |
| `workhuman-webhooks-events` | Choose a documented connector, event, poll, report, or export mode |
| `workhuman-performance-tuning` | Tune measured workflows without weakening correctness or privacy |
| `workhuman-cost-tuning` | Govern contract, award, redemption, service, and operating cost |
| `workhuman-reference-architecture` | Define HCM, Workhuman, workplace, analytics, and trust boundaries |

## First-Party References

- [Social Recognition](https://www.workhuman.com/platform/social-recognition/)
- [Integrations and open API](https://www.workhuman.com/capabilities/integrations/)
- [Microsoft Teams integration](https://www.workhuman.com/capabilities/integrations/microsoft-teams/)
- [Workhuman Store](https://www.workhuman.com/capabilities/rewards/)
- [Security and privacy](https://www.workhuman.com/why-workhuman/security-and-privacy/)

## Validation

```bash
python3 scripts/validate-skills-schema.py --marketplace --min-grade A --verbose plugins/saas-packs/workhuman-pack
python3 -m unittest tests.test_workhuman_pack_contract
```

## License

MIT
