---
name: langfuse-data-boundary-auditor
description: |
  Audit supplied Langfuse observation payloads for unapproved fields, incomplete
  cursor coverage and retention evidence gaps. Separate project retention from
  Cloud access windows and dataset/audit/external-copy scope. Use when reviewing this evidence. Trigger with "review a
  Langfuse debug export", "did anonymization leave metadata?" or "does retention
  cover all these Langfuse records?".
allowed-tools: Read, Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [langfuse, data-boundaries, retention, privacy-review, diagnostics]
compatibility: Python 3.10+ standard library; supplied native project and observation JSON evidence. No credentials, networking, masking or deletion is performed.
argument-hint: '[boundary-review.json]'
---

# Langfuse Data Boundary Auditor

## Overview

Compare supplied observation response fields with an explicitly reviewed owner
policy and identify project/retention/coverage gaps. Unknown fields, empty
containers and nested metadata are still data. A matching field policy is not
anonymization, permission to publish, proof of deletion or legal compliance.

This operator produces an evidence ledger. It never creates an export, rewrites
customer data, rotates credentials, changes retention or deletes records.

## Prerequisites

- The reviewed purpose, project and absolute selection window.
- A privately reviewed field allowlist, evidence-age bound and retention limit.
- Native project lookup and observation pages with stable queries and cursor
  metadata, using the [receipt contract](references/receipt-contract.md).
- Separate access, dataset, audit-log, external-copy and retention-execution
  review references, or explicit gaps for missing evidence.
- Python 3.10+ and authorization to inspect the supplied material.

Offline analysis needs no authentication. Any separate read needs existing
approved scope; a user role or key prefix does not establish API permissions.
Keep the original receipt private even when its diagnostic output contains hashes.

## Instructions

### Step 1: Define what is being reviewed

Identify the exact captured observation selection and intended use. Preserve
the source artifacts and mapping receipt. Do not present one page, a filtered
query or an API access window as a complete historical project inventory.

State which stores and exports are outside this scan. Project lookup and review
references are supplied evidence; the helper does not independently authenticate
them or inspect the referenced controls.

### Step 2: Review the field policy before scanning

Use exact JSON Pointer leaf paths with `~1` and `~0` escaping. The local `*`
extension matches array positions only, not arbitrary object keys or subtrees.
Empty objects, arrays and null remain leaves. Read the
[contract](references/receipt-contract.md) before approving paths.

Do not expand the allowlist automatically after a failure. A permitted string
can still contain secrets or personal data; field approval is not value-level
PII detection. Regex replacement, object spread and late updates cannot prove
that raw content was never transmitted.

### Step 3: Run the bounded audit

```sh
python3 scripts/audit-boundary.py private-boundary-review.json
```

Run from this skill's directory. Inspect unapproved path hashes/counts, project
and window correspondence, query stability, terminal cursors, capture age and
declared collection completeness. Resolve path hashes privately against the
original evidence; do not copy raw keys or values into a shared report.

### Step 4: Assess retention and other-store coverage

An omitted, null or zero `retentionDays` does not establish configured deletion.
Positive configuration must fit the reviewed owner bound, but configuration
alone is not evidence that deletion executed. Cloud access windows limit reads;
they are not deletion policies.

Review saved dataset items, audit logs and external copies separately. Missing
coverage references remain findings; present references still require actual
evidence review. Trace deletion or retention cannot be generalized into a claim
that all copies of a person's data are gone.

Source-side export-stage masking, permission enforcement and database/disk/blob
encryption require their own evidence. Do not treat an `ENCRYPTION_KEY` setting
as proof of full storage encryption or turn this report into a security/DoD
certification.

### Step 5: Return the bounded finding ledger

For each finding record its fixed code, private evidence pointer, impact,
confidence, missing coverage and next check. Keep selected-query correspondence,
source-side exposure, configured retention and actual deletion evidence separate.
Any remediation or destructive request requires its own authorized workflow.

## Output

Return `langfuse-boundary-review.json` and a supplied-data summary of field-policy
correspondence, unapproved leaf/path counts, selection completeness, configured
retention and independent coverage gaps. `matches-supplied-policy` is limited to
the supplied payload and policy; it does not authorize sharing the input.

## Examples

- **An anonymized export still contains nested metadata:** report unapproved
  leaves, preserve the original evidence privately and review actual values;
  do not declare the remaining payload anonymous.
- **The UI shows only 30 days:** obtain the configured project retention
  evidence and review other stores instead of claiming older records were deleted.
- **Page one ends with a cursor:** retain incomplete-selection findings; do not
  certify the export or deletion inventory as complete.
- **Retention is configured, dataset review is absent:** report the configuration
  separately from the unresolved dataset scope and execution evidence.

## Error Handling

Exit 0 matches the supplied policy, exit 1 needs investigation, and exit 2 holds
invalid/unreadable/oversized evidence with a fixed code. Preserve held and partial
states. Do not manufacture review references, truncate a manifest, alter source
values or relax the policy just to obtain a passing result.

## Resources

- [Receipt, field-path policy, bounds and primary references](references/receipt-contract.md).
- [Evaluation specification](eval-spec.yaml): no live privacy/deletion evaluation is implied.
