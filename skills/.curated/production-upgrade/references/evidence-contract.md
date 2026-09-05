# Upgrade evidence contract

Evidence is a reproducible record, not a confidence statement. Store one JSON
manifest beside the upgrade records and validate it with
`scripts/audit_evidence.py`.

## Required fields

- `schema_version`: `1`.
- `subject`: stable ID and semantic version.
- `source_revision`: exact 40-64 character hexadecimal revision.
- `research`: one or more HTTPS primary sources with verification dates, a
  bounded pain-catalog path, and an explicit gaps array.
- `decisions`: paths for architecture, threat model, and migration records.
- `validation.commands`: successful commands with retained artifact SHA-256.
- `validation.baseline_delta`: a deliberately broken case with non-zero result
  and retained artifact SHA-256.
- `validation.adversarial_cases`: positive integer.
- `review`: independence fact, reviewer identity when independent, exact reviewed
  revision, and findings.
- `release`: explicit authorization and publication booleans.

All referenced paths are relative to the declared repository root, regular
files, non-symlinked, and contained by that root. The audit helper reads and
validates the manifest but never executes its recorded commands.

## Claim rules

- Missing or malformed evidence is `BLOCKED`.
- Valid implementation evidence without independent review is `CANDIDATE`.
- Independent review must be performed by a genuinely separate identity and
  bound to `source_revision`; otherwise it remains self-review.
- Independent review without release approval is `REVIEWED`.
- `RELEASE-READY` requires independent review and explicit exact-revision
  authorization.
- `published: true` with `authorized: false` is invalid.

Never include credentials, tokens, cookies, authorization headers, private
keys, raw customer content, or presigned URLs in evidence.
