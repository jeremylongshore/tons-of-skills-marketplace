---
name: langfuse-prompt-release-guardian
description: |
  Review Langfuse prompt promotions or rollbacks using explicit versions, fresh
  label snapshots, reviewed content hashes and runtime variable contracts.
  Verify supplied prompt webhooks without treating signatures as release
  approval. Use when reviewing this evidence. Trigger with "promote this Langfuse prompt", "check a prompt rollback" or
  "is this signed prompt update enough to deploy?".
allowed-tools: Read, Bash(python3:*)
version: 2.0.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags: [langfuse, prompts, release-review, rollback, webhooks]
compatibility: Python 3.10+ standard library; supplied native prompt API snapshots. Optional webhook verification uses an existing approved secret through a named environment variable.
argument-hint: '[prompt-release-receipt.json]'
---

# Langfuse Prompt Release Guardian

## Overview

Prepare an evidence-bound prompt promotion or rollback proposal. Check which
version a label actually resolved to, whether reviewed content changed and
whether the runtime supplies required variable/placeholder names. A signed
webhook is event evidence, not deployment authority or a current label snapshot.
No helper assigns labels, deploys prompts, starts CI or calls a model.

## Prerequisites

- The reviewed project/region, target label, current version and explicit
  candidate or rollback version.
- Fresh native label/version GET snapshots captured without SDK cache/fallback
  substitution, plus reviewed content fingerprints and change reference.
- The runtime variable/placeholder name contract and config-change policy.
- Python 3.10+ and the [release receipt contract](references/release-receipt-contract.md).

Offline release analysis needs no authentication. A separately authorized
webhook review needs the existing approved signing secret through an environment
variable; never print it or put its value in arguments or receipts.

## Instructions

### Step 1: Establish the exact change

Name the target label and both versions. Do not infer the baseline from `latest`,
choose an arbitrary previous version or silently fall back from a missing label.
Confirm the project binding separately; native prompt content alone cannot
prove which credentials or account produced it.

### Step 2: Review and pin the snapshots

Read [release-receipt-contract.md](references/release-receipt-contract.md). Preserve
actual queries and responses, resolution settings and capture times. Review
prompt content, config and resolved dependencies privately before recording
their fingerprints. Never overwrite a reviewed hash automatically after drift.

```sh
python3 scripts/inspect-release.py private-release-receipt.json --fingerprints
python3 scripts/inspect-release.py private-release-receipt.json
```

Run relative to this skill's directory. Preparation mode emits unreviewed hashes
and exits 1; it cannot pass a release gate. The reviewed mode checks evidence age,
version/label state, content pins, config permission and runtime name availability.

### Step 3: Investigate compatibility and quality

Check both current and candidate runtime contracts so a rollback is usable too.
Type changes need a runtime migration review. Complex Mustache syntax remains
held for offline compilation with the actual pinned application SDK; do not
simplify production templates merely to obtain a passing helper result.

Name availability does not establish correct values, types, rendering, injection
resistance or model quality. Attach case-level experiment evidence tied to the
reviewed prompt/config and dataset/evaluator identities. An improved average or
successful compile cannot replace critical-case regression checks.

### Step 4: Verify webhook evidence only when relevant

Use [webhook verification](references/webhook-verification.md) for a supplied
event's exact raw body, captured header and approved secret. Authenticate before
parsing; preserve project binding, timestamp policy and replay-history gaps.

The verifier does not persist or atomically claim deduplication state. Repeated
or out-of-order events, including separate label gain/loss events, require current
API snapshots. Do not trigger CI, apply labels or treat a signed `deleted` event
as authorization for a compensating mutation.

### Step 5: Return a proposal with release preconditions

Preserve all findings. A reviewable proposal still needs owner release authority,
fresh pre-change label verification, applicable role/protected-label controls,
runtime cache/fallback consideration and post-change observation. Record those
as outstanding preconditions, not actions already performed by this skill.

## Output

Return `langfuse-prompt-release-review.json` and a short supplied-data proposal:
explicit versions and direction, evidence age/content checks, compatibility and
quality gaps, webhook status when relevant, and remaining release preconditions.
Exclude prompt text, sensitive config, raw signatures, secrets and private names
from the shared report.

## Examples

- **Candidate adds a variable the app never sends:** retain the runtime-contract
  blocker even if a content reviewer approved the wording.
- **Rollback targets an older chat prompt:** check its placeholders/config and
  type compatibility rather than assuming every older version is safe.
- **Signature is valid but history is missing:** report replay unchecked; fetch
  fresh label evidence within authorization instead of deploying the event body.
- **Current label moved after review:** report drift and obtain a new review;
  a previously recorded hash is not a compare-and-swap transaction.

## Error Handling

Release analysis exits 0 only for a reviewable proposal, 1 for findings or
unreviewed fingerprints, and 2 for held input. Webhook verification exits 0 only
for an authenticated event absent from the supplied history, 1 for a duplicate
or unchecked replay history, and 2 for held input. Neither exit 0 means release
approval, durable deduplication, present deployment state or production safety.

## Resources

- [Release receipt and fingerprint contract](references/release-receipt-contract.md).
- [Webhook byte verification and replay boundaries](references/webhook-verification.md).
- [Evaluation specification](eval-spec.yaml): proposed behavioral criteria, not completed evaluation evidence.
