# Verify a supplied webhook before using it as release evidence

`scripts/verify-webhook.py` is an offline verification tool, not an HTTP server or release executor. It authenticates the original request bytes against a supplied secret, checks the requested project and the basic event envelope, and compares an event hash with a supplied replay receipt. It never changes labels, sends requests, launches CI, stores replay state, or proves that a prompt is currently deployed.

Use this only with an owner-authorized private evidence capture. No production webhook or real signing secret is needed for the repository tests; their bodies and signing material are synthetic.

```sh
python3 scripts/verify-webhook.py private-body.json \
  --header-file private-signature.txt \
  --secret-env REVIEWED_WEBHOOK_SECRET \
  --project-id reviewed-project-id \
  --seen-receipt private-processed-events.json
```

Provision the secret through the approved local environment mechanism. Do not put its value in arguments, terminal output, fixtures, receipts or a committed file. The option names an environment variable; the script does not fetch secret-manager values or inspect other variables. A missing variable holds the review. Project IDs are visible in local process arguments; use an appropriately private review environment.

The header file contains the captured `x-langfuse-signature` value, with an optional trailing line ending. Keep the body file's bytes exactly as received. Langfuse's format is `t=<unix-seconds>,v1=<sha256-hex>`, signing the timestamp, a period and the raw body. This tool requires exactly those two fields and a 32-byte digest, then uses a constant-time comparison. It does not authenticate a parsed/reformatted JSON document or the old bare-body HMAC recipe. Malformed headers, duplicate fields, wrong signatures and a wrong project are held. JSON is parsed only after the byte-level signature check.

Our **local receiver-review policy** permits at most 300 seconds in either direction between the header timestamp and review time. This is not a provider freshness SLA. The default review time is the local clock; synchronize that clock. `--now` accepts an explicit integer for reproducible fixtures or historical evidence review. Choosing a historical time means verifying validity **at that supplied time**, not proving freshness now. Keep the supplied time in the review record and never use historical review to admit stale requests to a production receiver.

The supported envelope uses `id`, timezone-aware `timestamp`, `type: "prompt-version"`, `apiVersion: "v1"`, `action` and `prompt`. Actions are `created`, `updated` or `deleted`. The prompt includes its ID, name, positive integer version, project ID, labels, type and content. Text content is a string; chat content is an array. This verifier checks the basic envelope only, not every chat message, template, configuration or dependency. It never compiles a prompt or approves a release based on authenticated content.

The supplied replay receipt is our format, not a Langfuse endpoint:

```json
{
  "schema_version": 1,
  "project_sha256": "<64 lowercase hex characters>",
  "processed_event_sha256": []
}
```

`project_sha256` hashes the UTF-8 project ID. Each processed event digest hashes the UTF-8 project ID, one zero byte, then the UTF-8 event ID. The same event ID remains a duplicate if its body changes or it is signed again. The CLI reports the digest but **does not add it to this list**. Do not reset or truncate history and call the result replay-safe. Its bound is 10,000 unique hashes; use the application's durable deduplication system for larger histories.

For a real receiver, acceptance needs a durable atomic claim keyed by project and event ID, appropriate retention, and a transaction/outbox design for downstream work. A read-then-write JSON file or this offline check cannot prevent concurrent duplicate processing. The owner must define recovery after a crash between claiming an event and handling it. This script's successful result is evidence about the supplied inputs, not proof those controls exist.

Exit 0 means `authenticated-supplied-event`: valid signature and envelope, matching project, and absent from the supplied history. Exit 1 means either `duplicate-supplied-event` or `signature-valid-replay-unchecked`. Omit `--seen-receipt` when history is unavailable; do not invent an empty receipt to obtain exit 0. Exit 2 holds malformed, unreadable, oversized or unauthenticated inputs and emits a fixed error code. The body and replay file are each bounded at 2 MiB, the header at 128 bytes and signing material at 4 KiB. These are tool limits, not claims about provider limits.

Reports contain hashes, a version number, fixed action/type, label count and review timestamps. Names, labels, content, configuration, secrets and signatures are not echoed. Hashes can still correlate operational records; apply the owner's handling policy. The input files remain sensitive and are not deleted or sanitized.

Webhook delivery can be repeated or arrive out of order. A label update may produce separate events for the version gaining it and the version losing it; do not deduplicate solely by prompt name/version or treat a single event as a complete label snapshot. A valid signature also does not make old payload state current. Fetch uncached, explicit version/label evidence through a separately authorized read-only path before preparing a promotion or rollback proposal. Changes still need the owner's release authority.

Primary authority: [Langfuse webhook contract](https://langfuse.com/docs/prompt-management/features/webhooks-slack-integrations) and [prompt version/label semantics](https://langfuse.com/docs/prompt-management/features/prompt-version-control). The five-minute review window, strict parsing, replay receipt, report schema and bounds above are owned by this tool.
