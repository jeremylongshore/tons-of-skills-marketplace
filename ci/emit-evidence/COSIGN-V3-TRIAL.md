# Cosign v3 compatibility trial

Tracks `claude-yszw`. Preparing or merging this lane does not approve a dispatch.
Obtain the owner's approval for the exact main commit before invoking public
Fulcio/Rekor/TSA signing services. Both production workflows retain Cosign v2.5.2.

The `Emit signed evidence manifest` workflow has an optional boolean dispatch
input, `cosign_v3_trial`, defaulting to false. With that input true on `main`, only
the artifact-only trial runs. Pushes and ordinary dispatches retain the existing
production path. Trial concurrency is unique to its run and cannot supersede a
production emission. The trial has read-only repository access plus the OIDC
permission required for signing; it cannot write a release.

After approval and merge, dispatch that workflow on main with
`cosign_v3_trial=true`. Record the exact source SHA, run ID and attempt. It emits
real source gate-result bundles through the existing producer, signs with pinned
Cosign v3.0.6, verifies with the existing exact workflow identity and issuer, and
assembles a manifest. Missing signatures, failed verification or failed assembly
stop the job. The artifact upload contains the bundles, signatures, manifest,
installed version and `trial-receipt.json`; retention is 14 days. Download and
retain the evidence before expiry. Nothing is uploaded to `evidence-latest`.

A successful trial proves producer-side verification only. The receipt therefore
records `consumer_verification: not_run` and `published: false`. Do not rewrite it
into an adoption result. Separately run the actual reports-hub production Sigstore
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
