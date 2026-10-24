# Prompt version and label review

`scripts/inspect-release.py` compares two supplied native prompt snapshots against an explicit owner review policy. It proposes promotion or rollback by **version**, checks simple variable/placeholder name availability, and holds stale, changed or incompatible evidence. It does not fetch prompts, compile them, call a model, assign labels, change configuration or execute a release.

```sh
python3 scripts/inspect-release.py private-release-receipt.json
```

Exit 0 means `reviewable-proposal`, not approval or deployment. Exit 1 means investigation is needed; `--fingerprints` also exits 1 and emits `unreviewed-fingerprints`, preventing preparation mode from accidentally passing a release gate. Exit 2 means malformed, unreadable, oversized or otherwise held input. Input is limited to 2 MiB. Reports exclude names, labels, text, chat messages, configuration and review-reference strings; hashes and version numbers remain operational metadata.

## Evidence wrapper

This is an owned local format. The nested `request` and `response` retain actual native prompt API values; the wrapper itself is not a provider request.

```json
{
  "schema_version": 1,
  "receipt_kind": "prompt-release-review",
  "context": {
    "project_id": "reviewed-project",
    "project_binding_review_ref": "private-account-binding-review",
    "reviewed_at": "2026-10-01T12:01:00Z",
    "maximum_age_seconds": 300
  },
  "policy": {
    "project_id": "reviewed-project",
    "name": "reviewed-prompt",
    "label": "production",
    "current_version": 2,
    "candidate_version": 3,
    "review_ref": "private-reviewed-change",
    "current_sha256": "<reviewed current fingerprint>",
    "candidate_sha256": "<reviewed candidate fingerprint>",
    "runtime_variables": ["user"],
    "runtime_placeholders": [],
    "allow_config_change": false
  },
  "current": {
    "name": "reviewed-prompt",
    "captured_at": "2026-10-01T12:00:00Z",
    "request": { "label": "production", "resolve": true },
    "response": {
      "name": "reviewed-prompt",
      "version": 2,
      "type": "text",
      "labels": ["production"],
      "tags": [],
      "prompt": "Hello {{user}}",
      "config": { "model": "reviewed-model" },
      "resolutionGraph": null
    }
  },
  "candidate": {
    "name": "reviewed-prompt",
    "captured_at": "2026-10-01T12:00:00Z",
    "request": { "version": 3, "resolve": true },
    "response": {
      "name": "reviewed-prompt",
      "version": 3,
      "type": "text",
      "labels": ["staging"],
      "tags": [],
      "prompt": "Welcome {{user}}",
      "config": { "model": "reviewed-model" },
      "resolutionGraph": null
    }
  }
}
```

The example's fingerprint placeholders are intentionally invalid. Preparation requires privately reviewing the actual snapshots and computing their fingerprints with `--fingerprints`; then record the reviewed values and review reference. Do not automatically copy new hashes over drift findings. A hash proves correspondence with the supplied reviewed bytes, not that anyone actually reviewed their quality or holds release authority.

The fingerprint is SHA-256 of UTF-8, sorted-key, compact Python JSON over exactly `name`, `version`, `type`, `prompt`, `config` and `resolutionGraph`, using `ensure_ascii=False` and `allow_nan=False`. Missing config/graph normalize to null. It is an **owned serialization**, not an SDK hash or RFC 8785 canonicalization. Preserve parsed numeric representations when reproducing it. Labels and tags are excluded from content hashes because they can change independently; the target label is checked separately. A resolved dependency graph, when returned, is included so a dependency change cannot silently reuse the same review hash.

Capture the current version by the exact target label and the candidate by an explicit numeric version using the native v2 prompt GET API (`client.api.prompts.get(name, request)` in the JS SDK). `resolve: true` is required in both retained requests. Use a separately authorized read-only capture, bypassing high-level prompt caches/fallbacks; high-level SDK prompt-client objects are not these native responses. Preserve the returned fields and timestamp rather than constructing success-shaped snapshots. Native responses do not themselves establish project binding, so retain the reviewed account/region/credential binding reference separately. The tool checks correspondence of supplied declarations, not provider authentication.

The current response must retain the target label and match the reviewed current version. The candidate must match its explicit requested version and must not already carry that label in this pre-change review. Same-version changes are held. The automatically maintained `latest` label is not a manual release target. Missing labels never justify substituting `latest` or another environment. A rollback selects an older explicit version and applies the same runtime compatibility checks; “it worked before” is insufficient.

`maximum_age_seconds` is the owner's local evidence-age policy, bounded here to one day. Capture timestamps must not be in the future or older than that policy relative to the supplied review time. It is not a provider cache TTL, transaction guarantee or trusted clock. Reads are not atomic: re-read the target label and review expected-version preconditions immediately before an independently authorized change. Another actor may move it after capture. Account for each deployed application's cache/fallback behavior and separately verify post-change resolution; this tool performs neither step.

## Runtime and quality boundaries

For simple `{{identifier}}` templates, both the current and candidate variable-name sets must be available in the reviewed `runtime_variables` list. Chat placeholders (`type: "placeholder"`, `name`) must be available in `runtime_placeholders`. Chat messages use `role` and string `content`, with an optional `type: "chatmessage"`. Prompt type changes require a runtime migration review; config changes also require `allow_config_change: true` in addition to a reviewed content hash. Extra runtime variables are allowed. Values, data types, rendering, injection resistance and model output are **not** proven by name availability.

Current JS SDK compilation uses Mustache, whose full grammar includes more than simple names. Sections, partials, dotted lookups, delimiter changes, triple braces, malformed/ambiguous delimiters and other unsupported constructs stay `template-needs-sdk-compile-review`; the helper never guesses how they render. Conduct offline compile fixtures against the actual pinned application SDK for those cases, including empty/missing inputs, chat placeholders and rollback compatibility. Preserve that independent review evidence; it does not erase this analyzer's finding. Do not rewrite a legitimate production template into a simpler one just to get exit 0.

Before release authority is exercised, attach case-level experiment evidence tied to the reviewed prompt/version/config and relevant dataset/evaluator identities. Use the experiment guardian for missing/errored cases and critical regressions; a signature, a matching hash, or a variable-name check is not evidence of model quality. Protect labels through the platform's available permissions when appropriate, and verify the applicable edition/role controls rather than inferring them from a key prefix.

Related evidence: [webhook-verification.md](webhook-verification.md). A verified webhook can motivate a fresh snapshot capture; it cannot replace it.

Primary contracts: [version and label resolution](https://langfuse.com/docs/prompt-management/features/prompt-version-control), [variables](https://langfuse.com/docs/prompt-management/features/variables), [message placeholders](https://langfuse.com/docs/prompt-management/features/message-placeholders), and the [API reference](https://api.reference.langfuse.com/). SDK native request/response fixture checks use `@langfuse/client` 6.0.2; they are not provider calls.
