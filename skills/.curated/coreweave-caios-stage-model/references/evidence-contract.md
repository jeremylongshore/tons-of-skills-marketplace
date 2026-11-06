# Evidence contract: CAIOS model staging review

Community-contributed; not affiliated with CoreWeave.

Supply `endpoint`, `prefix`, prefix_owned, license_reviewed, public_access, cost_gate_reviewed, and an `objects` inventory of key/size_bytes/sha256/uploaded_size_bytes/downloaded_sha256/upload_complete. Use the documented HTTPS cwobject.com endpoint with virtual-hosted addressing. The helper compares supplied read-back SHA-256 and size; ETag alone is insufficient, particularly for multipart objects. It does not upload, download or verify the honesty of supplied checksums. Retain a version-specific object manifest so cleanup cannot remove another model or version.

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

Primary source: https://docs.coreweave.com/products/storage/object-storage/using-object-storage/manage-objects

Contract reviewed 2026-11-05. Repository examples are original. Vendor version and
account-specific availability must be confirmed separately; no live operation was
performed for this pack. See the blueprint for requirements and release boundaries.
