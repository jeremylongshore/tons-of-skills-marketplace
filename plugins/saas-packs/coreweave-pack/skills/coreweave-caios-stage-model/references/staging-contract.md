# Model staging contract

Community-contributed; not affiliated with CoreWeave.

Use a dedicated AWS CLI profile and virtual-hosted addressing. Credentials stay in
the approved credential provider; do not print environment variables, copy keys into
manifests or embed userinfo in endpoint URLs. The helper deliberately supports the
external HTTPS `cwobject.com` endpoint only. CoreWeave documents a separate in-cluster
LOTA endpoint; this pack does not infer equivalent TLS or routing semantics.

Sources inspected 2026-11-05:

- [AWS CLI client configuration](https://docs.coreweave.com/products/storage/object-storage/using-object-storage/s3-clients/aws)
- [Object operations](https://docs.coreweave.com/products/storage/object-storage/using-object-storage/manage-objects)
- [Multipart cleanup](https://docs.coreweave.com/products/storage/object-storage/buckets/abort-multipart-uploads)

An artifact manifest binds model provenance/license, exact source size/SHA-256,
bucket/prefix ownership, object key and version, upload completion and read-back
size/SHA-256. Verify large objects incrementally; SHA-256 calculation must not load
the whole model into RAM. A returned ETag is not portable SHA-256 evidence. Keep the
exact key/version manifest for retention and rollback rather than assuming a prefix
belongs exclusively to this attempt.

A pre-upload review legitimately returns incomplete integrity evidence. No upload
has yet been observed. After transfer, pass actual read-back observations to the
same helper; never fill expected values into observed fields to obtain a pass.
Local fixtures use synthetic observations only. No bucket, object or multipart
operation was performed to validate this pack.
