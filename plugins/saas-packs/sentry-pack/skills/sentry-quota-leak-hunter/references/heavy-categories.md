# Replays and logs (CQ07)

Replay is the heaviest client recorder. Prefer `replay.start()` on a named flow, or error-triggered replays, over a blanket `replaysSessionSampleRate`. State which sessions you will not have.

Logs: if the logging integration is on, Sentry receives what you emit. Filter with `beforeSendLog` or the logger level. Debug logs eat the `log_item` / `log_byte` meters.

`beforeSend` does not implement either control.

Privacy (unmask, block) is PII `replay-privacy`. Quota only opens the labeled copy when replay accepted > 0.

Attachments are a separate stored-byte category. Do not add them into errors.
