# Events not appearing

Walk `silent-drop-diagnosis` top to bottom. Common mis-labels:

| What people say | What it usually is |
|---|---|
| "DSN is broken" and `beforeSend` returns null | `beforeSend` |
| "Sentry is down" on Lambda | missing `flush()` / transport |
| "We are dropping 40%" from the usage chart | They added filtered + dropped. Make them split it. Quota script. |
| "Source maps are flaky" | Late upload, no reprocessing, or release mismatch. Not a drop. |
| "beforeSend scrubs the replay" | False. Replay privacy is a different hook. |

`debug: true` is a way to see the SDK's own log. It is not a cause.
