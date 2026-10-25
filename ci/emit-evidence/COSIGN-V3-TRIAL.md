# Cosign v3 compatibility trial

Tracks Beads task `claude-yszw`: produce a real v3 bundle, verify it in the
producer and the actual reports hub, then separately review production adoption.
Preparing or merging this lane does not approve a dispatch. Before activation,
the owner must configure the `cosign-v3-trial` GitHub environment with exactly
one required reviewer: `jeremylongshore` (user ID 213859472), and one custom
branch policy for branch `main`. This change does not create or update those
settings. Do not bypass environment protection rules.

The approval job has no OIDC permission. After GitHub's environment gate, it
checks the exact source SHA, reviewer/branch configuration and the workflow run's
recorded owner approval through read-only API calls. Missing configuration,
unprotected auto-created environments, other reviewers or absent owner approval
fail closed. The signing job depends on that job and has no environment itself:
this preserves the producer's branch-ref OIDC subject rather than substituting an
environment-scoped subject. These checks have local fixtures; no live approval
or v3 signing run is included in this change. Actual consumer acceptance remains
a separate requirement before a reviewed production pin update.

Obtain the owner's approval for the exact main commit before invoking public
Fulcio/Rekor/TSA signing services. Both production workflows retain Cosign v2.5.2.

The `Emit signed evidence manifest` workflow has an optional boolean dispatch
input, `cosign_v3_trial`, defaulting to false. With that input true on `main`, only
the trial runs without publishing a release. Pushes and ordinary dispatches retain the existing
production path. Trial concurrency is unique to its run and cannot supersede a
production emission. The trial has read-only repository access plus the OIDC
permission required for signing; it cannot write a release.

After approval and merge, dispatch that workflow on main with
`cosign_v3_trial=true` and `approved_source_sha` set to the exact approved
40-character main commit. The approval job fails before signing if that value is
missing, malformed, or differs from its actual source SHA. If main advances,
obtain fresh approval; do not silently substitute the new SHA. Record the exact source SHA, run ID and attempt. It emits
real source gate-result bundles through the existing producer, signs with pinned
Cosign v3.0.6, verifies with the existing exact workflow identity and issuer, and
assembles a manifest. Missing signatures, failed verification or failed assembly
stop the job. The artifact upload contains the bundles, signatures, manifest,
installed version output and `trial-receipt.json`; the upload requests 14-day
retention, subject to repository policy. Download and
retain the evidence before expiry. Nothing is uploaded to `evidence-latest`.

A successful trial proves producer-side verification only. `trial-receipt.json`
is unsigned run metadata written after manifest assembly; it is not covered by
the manifest or the signatures and must not be used as attestation evidence.
It records the requested release, completed producer commands, consumer
verification as not run, and no release publication. The installed binary's own
version output is retained separately. The signed bundles and verification logs
are the producer evidence; do not turn the sidecar into an adoption result. Separately run the actual reports-hub production Sigstore
verifier against these exact downloaded bytes under its existing pinned issuer,
workflow identity, trust roots and transparency threshold. Record the consumer
source commit, dependency lock digest, commands and unedited results. Preserve
negative checks for modified payloads and mismatched identities. Do not substitute
the offline verifier, a flag-parsing check, a third-party bundle, or a relaxed
transparency/identity policy.

Only after both producer and actual consumer acceptance are evidenced may a
separate reviewed change remove the v2.5.2 pins. A failed or incompatible trial
leaves production unchanged; retain its logs and fix the incompatibility before
another approved trial. No release, dashboard ingestion, trust-policy change or
production pin update is part of this lane.

## Implementation references

The trial uses the requested Cosign release's default signing endpoints and trust
configuration; it does not separately pin Fulcio/Rekor/TSA endpoints or roots.
The copied signing/verification step bodies are checked against the production
steps, while actual consumer acceptance remains untested. Do not change the
reports hub's trust policy to make a trial pass.

- [Environment API and required-reviewer configuration](https://docs.github.com/en/rest/deployments/environments)
- [Workflow run approval history](https://docs.github.com/en/rest/actions/workflow-runs#get-the-review-history-for-a-workflow-run)
- `check-trial-approval.mjs`: validates configuration and this run's owner review.
- `merge-check-pages.mjs`: combines all check-run pages before producer validation.
- `emit-evidence.ts`: validates complete required-context reports and builds rows.

Trial bundles use the production workflow identity and have no signed trial
marker. Keep them out of `evidence-latest` and production ingestion until the
separate adoption review; unsigned artifact labels do not make that distinction
cryptographic. Signature-verification output remains in workflow logs, under
the repository's log-retention policy.

The required-check waiters retry unavailable, incomplete or changing paginated
reports within the existing 30-attempt bound; exhaustion fails before signing.
The publication workflow obtains its merger from the workflow-run commit in a
separate checkout, while retaining the payload's exact source checkout. Current
callers invoke that reusable workflow locally from the same workflow commit.

Cosign v3.0.6 still defines `--new-bundle-format` for both
[signing](https://github.com/sigstore/cosign/blob/v3.0.6/cmd/cosign/cli/options/sign.go)
and [verification](https://github.com/sigstore/cosign/blob/v3.0.6/cmd/cosign/cli/options/verify.go).
A CLI failure still fails the trial and remains diagnostic evidence, never an
excuse to weaken identity, transparency or consumer checks.
