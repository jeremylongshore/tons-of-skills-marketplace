---
name: coreweave-caios-stage-model
description: Plan CAIOS model transfers and verify exact object sizes, checksums and
  prefix ownership from supplied evidence. Use when reviewing CoreWeave caios stage
  model or checking supplied operational evidence. Trigger with "coreweave caios stage
  model".
allowed-tools: Read, Write, Edit, Bash(python3:*), Grep
version: 1.15.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Portable local Python 3.12+ fixture workflow; optional platform commands
  require separately approved credentials.
tags:
- coreweave
- gpu-cloud
- operations
- offline
---
# CAIOS model staging review

> Community-contributed; not affiliated with, endorsed by, or sponsored by CoreWeave, Inc.

## Overview

Plan CAIOS model transfers and verify exact object sizes, checksums and prefix ownership from supplied evidence.
Use Read for supplied evidence and references, Write for a local report, Edit for a proposed local plan, and Grep for relevant log excerpts. Bash is restricted to Python helpers; no helper makes account calls.

## Prerequisites

- Python 3.12+, the supplied evidence contract and explicit intended context/namespace.
- An owner-reviewed resource scope, timestamps, model provenance and applicable platform versions.
- Redacted local inputs; no kubeconfig, token or customer payload in fixtures or reports.

## Cost and safety gate

Before creating or uploading anything, complete the [mandatory cost gate](references/cost-gate.md).
Show the exact resources, GPU type/count and supplied hourly rate, all other costs,
expiry and teardown. Obtain explicit user confirmation for the reviewed artifact.
Default to local review; neither this helper nor a JSON receipt authorizes execution.

## Instructions

1. Read the evidence contract and classify missing inputs before reviewing a result.
2. Inspect the supplied scope and timestamps. Never fall back to a current context.
3. Run the local helper and preserve the full status, findings and input digest.
4. Resolve blockers and collect missing evidence through an authorized operator.
5. Verify the outcome against the acceptance criteria; distinguish supplied evidence from live observation.

## Examples

Use the fixture replay below before processing redacted operator evidence.

## Output

A JSON report with status, findings, observations, input SHA-256 and evidence boundary.

## Error Handling

| Condition | Response |
| --- | --- |
| Invalid or mismatched input | Stop with a blocker and request corrected evidence. |
| Stale or missing observations | Return incomplete; do not infer healthy or zero cost. |
| Unsupported platform shape | Use a reviewed adapter before claiming compatibility. |

## Resources

- [Primary platform reference](https://docs.coreweave.com/products/storage/object-storage/using-object-storage/manage-objects)
- [CoreWeave official skills](https://github.com/coreweave/skills) for vendor-maintained workflows.

## Offline verification

Supply `endpoint`, `prefix`, prefix_owned, license_reviewed, public_access, cost_gate_reviewed, and an `objects` inventory of key/size_bytes/sha256/uploaded_size_bytes/downloaded_sha256/upload_complete. Use the documented HTTPS cwobject.com endpoint with virtual-hosted addressing. The helper compares supplied read-back SHA-256 and size; ETag alone is insufficient, particularly for multipart objects. It does not upload, download or verify the honesty of supplied checksums. Retain a version-specific object manifest so cleanup cannot remove another model or version.

From this skill directory, replay the synthetic example (its timestamp is intentionally
fixed; it contains no account data):

```bash
python3 scripts/review-transfer.py --input tests/fixtures/example.json --as-of 2026-11-05T12:01:00Z
```

For current evidence, omit `--as-of`; it defaults to current UTC. Required common
fields: `schema: coreweave-evidence/v1`, `captured_at`, `context`, `namespace`,
`expected_context`, `expected_namespace`. The scope must agree and evidence must
be at most five minutes old. Explicit replay time is for testing historical fixtures,
not a way to make stale production evidence current.

Exit 0 / `reviewed` means the supplied assertions satisfy this bounded contract;
2 / `blocked` requires correction; 3 / `incomplete` requires more evidence. Read the
findings rather than relying only on exit status. Scripts never execute text from
inputs, call a cloud API or authorize a change. Fixture and package checks are
separate from model behavior and live compatibility.

- [Input contract and limitations](references/evidence-contract.md)
- [Skill blueprint and acceptance](docs/BLUEPRINT.md)

## Staging procedure after owner approval

1. Confirm model license/provenance, source SHA-256 and exact byte size. Use an
   existing owner-approved bucket and a dedicated versioned prefix; new buckets
   require their own plan. Inventory every object before proposing a transfer.
2. Use a dedicated AWS CLI profile with virtual-hosted addressing and approved
   least-privilege credentials. Workload identity is preferable where supported.
   This workflow targets the external TLS endpoint `https://cwobject.com`; an
   in-cluster LOTA integration needs its own reviewed endpoint contract.
3. Preview exact object transfers. Complete the cost gate for storage, transfer,
   requests, retained versions and incomplete multipart uploads. Confirm the
   manifest digest and scope before removing `--dryrun` from an upload command.
4. After uploading, retain the returned object/version identity and read the object
   back to a private temporary location. Compare SHA-256 and byte size with the
   source. Do not substitute ETag for a content digest. Feed these observations to
   the local transfer reviewer and retain the manifest with the result.
5. On failure, retain the failed object/upload ID for diagnosis. Cleanup targets
   only an explicitly approved object version or multipart upload ID. Never run
   recursive bucket/prefix deletion as generic teardown.

```bash
: "${CW_PROFILE:?approved profile}" "${CW_BUCKET:?approved bucket}"
: "${CW_OBJECT_KEY:?exact owned object key}" "${MODEL_FILE:?local model file}"
sha256sum "$MODEL_FILE"
aws --profile "$CW_PROFILE" --endpoint-url https://cwobject.com s3 cp \
  "$MODEL_FILE" "s3://$CW_BUCKET/$CW_OBJECT_KEY" --dryrun
# STOP: user must confirm the exact transfer manifest and cost before upload.
# Teardown, only after verifying the exact owned version and retention decision:
: "${CW_OBJECT_VERSION:?approved owned version}"
aws --profile "$CW_PROFILE" --endpoint-url https://cwobject.com s3api delete-object \
  --bucket "$CW_BUCKET" --key "$CW_OBJECT_KEY" --version-id "$CW_OBJECT_VERSION"
```

These are operator instructions, not commands run during this pack's tests. The
[staging contract](references/staging-contract.md) separates local fixture proof
from storage observations and documents credential and checksum boundaries.
