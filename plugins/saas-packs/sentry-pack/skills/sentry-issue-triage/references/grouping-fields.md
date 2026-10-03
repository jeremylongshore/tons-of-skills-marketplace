# Grouping field names the investigator may cite

Salvaged from cut `sentry-sdk-patterns` as names, not a cookbook.

- Event JSON: `fingerprint`, `exception.values[].type`, `exception.values[].value`, `exception.values[].stacktrace.frames`, `message` / `logentry`.
- SDK fingerprint array may include the literal `{{ default }}`. Omitting it is an AI-grouping opt-out for that event (OP03).
- Issue JSON: `metadata`, `culprit`, `count`, `userCount`, `firstSeen`, `lastSeen`, `status`, tags `release` and `environment`.
- "Event Grouping Information" in the product is the human view of which level won (fingerprint, stack, exception, message). Custom rules beat built-in Sentry fingerprints on **new** events.

Do not cite a field the payload does not have. Do not claim stack-trace rules apply to performance issues.
