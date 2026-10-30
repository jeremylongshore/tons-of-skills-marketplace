# Access diagnostics retained from the authentication tutorial

Establish the numeric GA4 property ID (`123456789`), not a `G-...` measurement ID,
stream ID, account ID or Google Cloud project number. Record the approved
principal, property, Cloud project used for API/quota purposes and intended read
scope. A valid credential does not prove access to the intended property.

Prefer an existing approved keyless path: a local user's Application Default
Credentials for interactive work, an attached workload identity on supported
Google Cloud runtimes, or configured workload identity federation elsewhere.
Service-account keys are not the default prerequisite. Do not create a key,
change property access or grant IAM to make this investigation pass.

Check both authorization layers without exposing secrets:

1. Identify which principal the approved ADC source represents. A CLI's active
   interactive account can differ from the credentials an SDK discovers.
2. Confirm that principal has the required GA4 property access for reporting.
   The Data API's `analytics.readonly` scope constrains the token; it does not
   grant property membership. Enabling the API in a Cloud project also does not
   grant GA4 property access.
3. Confirm the approved Cloud/quota project and Data API availability. Preserve
   a sanitized error code and the attempted method; do not paste access tokens,
   client secrets, credential JSON, user identifiers or raw provider errors.
4. Distinguish invalid/expired credentials, insufficient OAuth scope, missing
   property access, disabled API/quota project and quota exhaustion. Resolve the
   identified boundary through the operator's existing process. Do not rotate
   unrelated credentials or retry a permission failure indefinitely.

The bundled collector uses the Analytics read-only scope and discovers existing
ADC only after an explicit live invocation and validated plan. It never performs
interactive login or edits credential files. If no approved credentials are
available, use supplied-data mode and report that live access is unverified.

For externally supplied OAuth client credentials, follow the organization's
approved application/consent workflow; the pack does not publish a universal
consent configuration. For unavoidable existing service-account keys, keep them
out of the repository and reports under the established secret-management
policy. Renaming a plaintext key to a `.sops` filename does not encrypt it.

BigQuery has a separate access model: a GA4 property role does not grant dataset
or query-job permissions. Export Guardian documents the metadata-only scope and
the additional existing authority needed for an explicitly requested dry run.

Primary sources: [Data API quickstart](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart-client-libraries),
[Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials),
[service-account key practices](https://cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys).
