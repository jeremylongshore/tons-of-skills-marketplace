# GA4 pack

Investigate conflicting reports, missing measurement signals and BigQuery export
gaps with executable evidence checks. The v2 rebuild retains the `ga4-pack`
install identity and consolidates five tutorials into three operator workflows.

**Install:** `/plugin install ga4-pack@claude-code-plugins-plus`

Freshie run 139 grades the three workflows A/92, A/95 and A/97. See the
[value decision](000-docs/001-AT-ADEC-operator-value-review.md) and
[validation evidence](000-docs/002-RA-AUDT-v2-validation-evidence.md) for the
immutable source, public inventory receipt and verification limits.

| Workflow | Concrete output |
| --- | --- |
| [Report Forensics](skills/ga4-report-forensics/SKILL.md) | A comparison ledger separating scope, identity, quality and row-coverage differences from hypotheses. |
| [Measurement Verifier](skills/ga4-measurement-verifier/SKILL.md) | Expected-event observations with count, truncation and deployment-window limits. |
| [Export Guardian](skills/ga4-export-guardian/SKILL.md) | Daily/intraday evidence and gaps, plus an optional SQL-bound dry-run risk assessment. |

Each workflow has a stdlib analyzer, a bounded optional SDK collector, a receipt
contract, primary references and behavioral evaluation cases. Supplied-data mode
works without credentials. Live collection requires an explicit live invocation,
an approved target and existing credentials. Development checks use synthetic
transports; they do not establish live property access or model-evaluation results.

Python 3.10+ is required; historical/export analysis also needs IANA timezone
data. Optional collectors use `google-analytics-data` or `google-cloud-bigquery`
from an approved environment. No key creation, IAM grants, tracking changes,
export setup or paid query execution is performed. A successful dry run does not
approve spend. Keep analytics receipts and SQL in approved local storage.

## Migration from v1

| Previous skill | Successor and preserved coverage |
| --- | --- |
| `ga4-auth-setup` | Report Forensics [access diagnostics](skills/ga4-report-forensics/references/access-diagnostics.md); property identity, ADC and authorization boundaries. |
| `ga4-data-api-query` | Report Forensics; bounded collection, request semantics, pagination and report-quality evidence. |
| `ga4-common-reports` | Report Forensics [report definitions](skills/ga4-report-forensics/references/report-definitions.md); exact windows, non-additive users, scopes, cohorts and funnel limits. |
| `ga4-realtime-api` | Measurement Verifier; observed event names/counts and honest realtime/deployment limits. |
| `ga4-bigquery-export` | Export Guardian; metadata coverage, daily/intraday selection and dry-run scan risk. |

The replacement intentionally removes standalone authentication tutorials,
copy-paste report slots and export-installation promises. Cohorts and custom
query shapes remain supported through explicitly mapped supplied evidence;
the bounded collectors hold unsupported shapes rather than silently dropping them.
Permanent public skill-page redirects and source retirement accompany the v2
release after normal review, generation and checks.

The exact pre-rebuild source is commit
`dd9cf1c487edb19fe504463b9aadf73afb6c05a4`, path
`plugins/saas-packs/ga4-pack/`. Preserve that Git receipt when reviewing retirement.
A rollback restores that source tree, reverses only this migration’s five
redirect entries, restores canonical pack metadata, and regenerates derived
catalog/curated projections through the normal reviewed workflow. Do not roll
back unrelated marketplace changes or rewrite history.

For portfolio-wide business interpretation and publishing, use `web-analytics`.
This pack diagnoses GA4 evidence. It does not instrument events, certify consent
or identify a root cause from an empty report alone.
