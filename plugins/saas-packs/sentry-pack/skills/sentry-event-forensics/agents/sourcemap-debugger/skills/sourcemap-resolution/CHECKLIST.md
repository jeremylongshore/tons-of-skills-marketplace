# sourcemap-resolution

**Owner:** `sentry-event-forensics` → `sourcemap-debugger`
**Canonical file.** Release-medic holds a labeled copy for the "upload succeeded, frames still minified" edge. Do not fork a third `resolved_with` essay.

JavaScript Debug IDs only. If the stack is ProGuard, dSYM, or another native artifact, stop and say unspecified.

## Parse

```bash
python3 scripts/parse-resolved-with.py --json event.json --maps-release "<id maps were uploaded under>"
```

Trust the script:

| Field | Meaning |
|---|---|
| `has_debug_meta` | Event has `debug_meta.images[].debug_id`. The running bytes were injected, or at least this event says so. |
| `has_matching_bundle` | Always null here. A debug id on the event does not prove an artifact bundle was uploaded. |
| `resolved_with` | Per frame. Allowed: `debug-id`, `url`, `index`, `release`, `release-old`, `scraping`, `unknown`. |
| `unknown_matchers` | Not in that enum. Do not adopt them. |
| `scraping_seen` | Sentry fetched the file from the web. Not a Debug ID success. Do not put maps on a public CDN to make scraping work. |
| `release_mismatch` | SDK release ≠ maps release. Handoff: release-medic `sourcemap-uploader` via the labeled `ci-sourcemap-upload` copy. Do not invent a second release name. |
| `not_retroactive` | Always true. Uploading maps later does not rewrite this event (RL02). Fingerprint rules do not restack it (OP04). |

`abs_path` on `raw_stacktrace` should match `debug_meta.images[].code_file` when you are checking the inject by hand. The script lists `abs_path` per frame. It does not declare a match.

## Frames can disagree

One event can mix `debug-id` and `scraping`. Do not declare victory off the readable frame.

## What you do not do

- Run `sentry-cli sourcemaps upload`.
- Claim a reprocess.
- Resolve the action-release doc fight. That is the grep on release-medic. Cite it only by pointing at `grep_debug_id.py`.
