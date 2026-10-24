# Observation payload boundary review

`scripts/audit-boundary.py` inventories the supplied observation response JSON against a reviewed field policy and checks supplied project retention and coverage evidence. It makes no network calls, creates no export, rewrites no data and performs no deletion. A passing result is `matches-supplied-policy`, not “safe,” “anonymous,” “deleted,” “encrypted” or “compliant.”

```sh
python3 scripts/audit-boundary.py private-boundary-receipt.json
```

Exit 0 matches the supplied policy; exit 1 needs investigation; exit 2 holds invalid, unreadable or oversized input with a fixed error code. Keep real receipts private. Output contains counts, configured retention days, fixed findings, hashes of unapproved paths and a SHA-256 of the complete input bytes. Names, pointer strings, keys, credentials, row identities and payload values are not echoed. Hashes can still correlate operational evidence and require an appropriate sharing policy. The original files remain sensitive.

## Owned receipt and native evidence

The wrapper is our format, not a Langfuse API. `project_lookup` retains the native project GET response, while every `pages` entry retains actual Observations API v2 request arguments and native `{data, meta}` response JSON. Do not reconstruct success-shaped pages or substitute a UI access window for a project retention setting.

```json
{
  "schema_version": 1,
  "receipt_kind": "observation-boundary-review",
  "context": {
    "project_id": "reviewed-project",
    "reviewed_at": "2026-10-02T12:00:00Z",
    "captured_at": "2026-10-02T11:59:00Z",
    "from_start_time": "2026-10-01T00:00:00Z",
    "to_start_time": "2026-10-02T00:00:00Z",
    "collection_complete": true
  },
  "policy": {
    "project_id": "reviewed-project",
    "review_ref": "private-field-and-retention-review",
    "maximum_age_seconds": 300,
    "maximum_retention_days": 30,
    "allowed_field_paths": [
      "/data/*/id",
      "/data/*/traceId",
      "/data/*/projectId",
      "/data/*/startTime",
      "/meta"
    ]
  },
  "project_lookup": {
    "data": [
      {
        "id": "reviewed-project",
        "name": "reviewed-name",
        "organization": { "id": "reviewed-org", "name": "reviewed-org-name" },
        "metadata": {},
        "retentionDays": 30
      }
    ]
  },
  "coverage_reviews": {
    "access_permissions": "private-reviewed-permission-evidence",
    "dataset_items": "private-reviewed-dataset-scope",
    "audit_logs": "private-reviewed-audit-scope",
    "external_copies": "private-reviewed-copy-inventory",
    "retention_execution": "private-reviewed-retention-execution"
  },
  "pages": [
    {
      "request": {
        "fields": "core,basic",
        "limit": 50,
        "fromStartTime": "2026-10-01T00:00:00Z",
        "toStartTime": "2026-10-02T00:00:00Z"
      },
      "response": { "data": [], "meta": {} }
    }
  ]
}
```

The empty example intentionally cannot establish observation coverage. Replace it with actual retained rows and requests. Field groups may return more fields than the example policy allows: those are findings, not a reason to expand the policy automatically. Review the purpose and approval of each additional field. The tool audits the parsed response structure, not the byte-level serialization of a separate file or the original SDK export. Retain the original capture and mapping receipt to bind it to the input hash.

## Field policy

Paths use JSON Pointer escaping: `~1` for a slash and `~0` for a tilde. `*` is a local extension matching **one array position only**. `/data/*/id` covers IDs in observation rows; `/data/*/metadata/*` cannot approve arbitrary object keys. Literal object keys named `*` are outside this policy syntax. Paths are exact leaves, not subtree grants. Empty objects, empty arrays and null count as leaves, so an empty `metadata` object still needs its own approval. `/meta` approves an empty terminal metadata object; a page containing a cursor needs a separate `/meta/cursor` path.

All response keys are visited, including fields the analyzer does not recognize. No object spread, ignored metadata subtree or substring test can make an unknown leaf disappear. Unapproved paths are reported only as hashes, preserving object-versus-array distinctions. This is deliberately **not PII detection**: an approved string field may still contain a secret or personal data. Inspect values privately under the appropriate policy, and do not treat field approval as permission to publish the raw payload. This tool does not produce a sanitized replacement export.

Bounds are 2 MiB for the receipt, 100 pages, 1,000 rows per page, 10,000 unique observations, 50,000 leaves, 64 nesting levels, 1,000 approved paths and 256 characters per key. At most 100 unapproved path hashes are emitted, with full counts and a truncation flag. Split legitimately larger work into independently scoped reviews; never truncate evidence and mark the collection complete.

## Scope, project and completeness

The project lookup must select exactly the reviewed project, and every row must match it. This checks the correspondence of supplied evidence; it does not independently authenticate the account or permissions. Keep the region, credential binding and permission review privately available. A user role or key prefix is not an API capability test.

Use explicit `fromStartTime` and `toStartTime` with an inclusive start and exclusive end. Every returned row must fit that window. The closed window is bounded here to 90 days as a **local review limit**, not a provider entitlement or completeness guarantee. Capture must follow the selected window, review must follow capture, and evidence age must meet the owner's policy, bounded to one day. These timestamps are supplied declarations, not a trusted clock.

Retain a fixed query while following opaque `meta.cursor` values until the terminal response omits cursor. Gaps, cycles, query changes and duplicate observation identities are held; a missing terminal page or `collection_complete: false` remains a finding. A `traceId` restriction is supported and disclosed in the report. Advanced filters are held rather than replayed incorrectly. Cursor exhaustion only covers this selected query and accessible history; it proves neither an atomic snapshot nor a complete project export. An empty selection never establishes coverage.

## Retention and other stores

Native `retentionDays` omitted, null or zero does not establish a configured deletion period. A positive setting must be at least three days and no longer than the reviewed owner maximum. This checks **configuration**, not enforcement or deletion completion. SDK 6.0.2's generated type documents null but only types an optional number; fixture checks omit the unset field rather than casting away that mismatch.

Keep Cloud access windows separate from deletion policies. Project retention does not remove saved dataset items or audit logs, and retained external copies need their own policy. Each coverage review is a private evidence reference, not a string that magically proves the control. Missing references remain findings; supplied references still require actual human or separately authorized evidence review. `retention_execution` should identify the reviewed enforcement evidence and its limits, not just repeat a configuration screenshot.

For source-side exposure, inspect export-stage masking and all relevant instrumentations separately. Late observation updates or regex replacements do not prove that raw data never left the application. `ENCRYPTION_KEY` must not be treated as proof of database, disk or blob encryption. If deletion is requested, establish all relevant stores and access limits and obtain its separate authorization; this analyzer executes no destructive workflow and issues no legal, privacy, security or DoD certification.

Primary sources: [retention](https://langfuse.com/docs/administration/data-retention), [deletion and verification limits](https://langfuse.com/docs/administration/data-deletion), [RBAC and project keys](https://langfuse.com/docs/administration/rbac), [export-stage masking](https://langfuse.com/docs/observability/features/masking), [self-hosted hardening](https://langfuse.com/self-hosting/configuration/hardening), and [native API contracts](https://api.reference.langfuse.com/).
