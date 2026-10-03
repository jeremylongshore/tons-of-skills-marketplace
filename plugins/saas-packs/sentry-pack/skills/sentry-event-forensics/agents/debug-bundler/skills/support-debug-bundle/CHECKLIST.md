# support-debug-bundle

**Owner:** `sentry-event-forensics` → `debug-bundler`
Only when the user asked for a support bundle.

## Collect

- SDK name and version from `package.json` / `requirements.txt` / `go.mod`, not from memory.
- Init snippet. DSN reduced to host (`oXXXX.ingest.sentry.io` or the region host). The DSN is a write credential; still do not paste an auth token beside it.
- `sentry-cli info` output **after** `scripts/redact-support-bundle.py`.
- Whether a test capture was sent, and the event id if the UI showed one. Never invent the id.
- Release string and environment string actually configured. Empty environment is a finding, not "production."

## Redact

```bash
python3 scripts/redact-support-bundle.py --json draft.txt
```

The bundle fails if `sntrys_` remains or if `SENTRY_AUTH_TOKEN=` still has a value. `contains_sntrys` must be false.

## Leave out

- Raw auth tokens, session cookies, `Authorization` headers.
- Full event payloads with email, IP, or request bodies. Those are PII. A bundle that needs them goes through `sentry-pii-scrub-enforcer` first, as a recommendation, not a dump.
- A claim that the SDK upgrade worked.

## Do not

- Upload the bundle to Sentry. `--apply` is refused.
- Spawn this agent from a drop diagnosis.
