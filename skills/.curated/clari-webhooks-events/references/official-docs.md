# First-party Clari evidence

Consulted on 2026-09-13 for `clari-webhooks-events`.

## Source snapshots

- [Clari Revenue API reference](https://developer.clari.com/default/documentation/external_spec): OpenAPI 3.0.0, published contract version 5.0.0, HTML SHA-256 `3fa7e772eebc3b2461fa12561a82520d4069668c2c35220c6f54fd0dbda1b5e1`
- [Clari Copilot API reference](https://api-doc.copilot.clari.com/): OpenAPI 3.0.1, published contract version 1.0.0, `spec.yaml` SHA-256 `e971686786068874001b8491189e233e634403e46bd3576a896cf02fb21774e6`
- [Clari public GitHub organization](https://github.com/clari): reviewed for a provider-maintained public Revenue or Copilot SDK; none was treated as authoritative for these workflows

## Contracts used

- `GET /audit/events` provides direct audit-event retrieval with pagination.
- `POST /export/activity` uses the shared asynchronous export job workflow.
- The current public Revenue contract does not define a general webhook subscription endpoint.

## Scope

This skill turns the relevant public provider contracts into one bounded operator outcome. It does not claim Clari certification, private tenant access, commercial terms, webhook functionality absent from the published contract, or successful customer-data execution without a retained runtime receipt.

## Verification boundary

- Re-check hosts, versions, headers, endpoint shapes, permissions, limits, status values, and mutation semantics before execution.
- Preserve exact forecast, job, event, call, workspace, and entity identifiers while redacting credentials and customer payloads.
- Never include `apikey`, `partnerkey`, `X-Api-Key`, `X-Api-Password`, revenue values, participant data, transcripts, recordings, or signed URLs in evidence.
- Treat export submission, job cancellation, ingestion, Copilot CRM writes, credential lifecycle changes, and downstream publication as explicit operator-approved mutations.
