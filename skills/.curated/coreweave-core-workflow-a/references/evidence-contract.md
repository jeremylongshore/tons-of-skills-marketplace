# Evidence contract: Inference deployment preflight

Community-contributed; not affiliated with CoreWeave.

The helper consumes an InferenceService object in `manifest`, CRD names in `crds`, `controller_version`, `model_provenance` (license_reviewed and SHA-256), `expected_model`, and a supplied `endpoint_result` (status_code, model, accepted). It checks observedGeneration against metadata.generation, GPU limits, bounded replicas and the model response independently. It supports the KServe model predictor shape in the fixture, not every custom predictor. Do not substitute Deployment readiness for endpoint acceptance. A source digest is not proof of the served weights unless the endpoint acceptance procedure binds that digest.

## Input and review boundary

The packaged `tests/fixtures/example.json` is the complete normalized input example.
`cases.json` includes specific negative outcomes as well as stale, wrong-scope and
injected-instruction variants. Inputs are supplied observations, not authenticated
proof. Review the source of every boolean assertion. The common envelope records
intended and observed scope plus a timezone-aware capture timestamp. Output includes
the SHA-256 of the actual bytes read, never a token or raw log excerpt.

Read-only collection commands and upload/deploy commands belong to the human-approved
operator workflow. Helper parsing is intentionally independent of credentials and
network availability. Unknown nested platform formats fail closed; add a reviewed
fixture before extending an adapter.

## Source and review

Primary source: https://kserve.github.io/website/

Contract reviewed 2026-11-05. Repository examples are original. Vendor version and
account-specific availability must be confirmed separately; no live operation was
performed for this pack. See the blueprint for requirements and release boundaries.
