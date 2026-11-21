---
title: "Claude Code OpenTelemetry: Drop user.email, Sum the Deltas"
description: "A loopback OpenTelemetry Collector for Claude Code telemetry: delete user.email before export, write plain JSON lines, and sum delta points for totals."
date: "2026-11-09"
tags: ["claude-code", "opentelemetry", "observability", "privacy", "devops"]
featured: false
canonical: "https://startaitools.com/posts/claude-code-opentelemetry-drop-user-email-sum-deltas/"
---
If you want to record your own or your team's Claude Code telemetry (token, cost and session usage), its OpenTelemetry export (sent over OTLP, the open standard protocol for logs and metrics) will do it, and it writes your signed-in account email onto log records and metric points whenever the email is available. I set up a local OpenTelemetry Collector (a small service that receives and forwards that data) that deletes that field and writes plain JSON lines. Summing the points in those files gives Claude Code token usage and cost totals that add up, as long as no points go missing.

When you finish, you have a collector listening only on localhost that keeps session, token and cost records on local disk without the email. One counting rule matters: each metric point (one numeric reading per export) is a delta (only the change since the previous export), so the total is the sum of all points. Reading the last point gives you the wrong number.

## The OpenTelemetry export carries user.email

Turning the export on takes a handful of environment variables. What comes with them is the problem.

Claude Code's monitoring docs mark `user.email` as "Always included when available." They list switches for some other attributes, such as the session ID, account UUID and version. None of the switches covers the email.

The fix is a drop processor (the attributes processor with `action: delete`): one collector rule that deletes a named field before anything is written. In an early trial without the rule, the token usage points carried `user.email` among 11 attribute keys. With the rule in place, a pre-install trial of two short headless Claude Code sessions against a scratch collector showed the email on 0 of 150 log records and 0 of 14 metric points. The account UUID and organization ID stayed. They are opaque IDs rather than an address, though each is still stable per account, and they are what lets you split usage per account.

## OpenTelemetry Collector config for Claude Code

Claude Code gets the environment block below. The endpoint is the loopback HTTP receiver. The host name and namespace are placeholders.

```json
{
  "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
  "OTEL_METRICS_EXPORTER": "otlp",
  "OTEL_LOGS_EXPORTER": "otlp",
  "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
  "OTEL_EXPORTER_OTLP_ENDPOINT": "http://127.0.0.1:14318",
  "OTEL_RESOURCE_ATTRIBUTES": "host.name=<your-host>,service.namespace=<your-namespace>"
}
```

I left `OTEL_LOG_USER_PROMPTS` and `OTEL_LOG_TOOL_DETAILS` unset. The docs say prompt content is logged only when the first one is set. Setting or removing any of these keys affects new sessions only.

The collector side, with both pipelines:

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 127.0.0.1:14318
processors:
  attributes/drop-email:
    actions:
      - key: user.email
        action: delete
exporters:
  file/metrics:
    path: /data/metrics.jsonl
    format: json
    flush_interval: 5s
    rotation: {max_megabytes: 100, max_days: 0, max_backups: 0}
  file/logs:
    path: /data/logs.jsonl
    format: json
    flush_interval: 5s
    rotation: {max_megabytes: 100, max_days: 0, max_backups: 0}
service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [attributes/drop-email]   # memory_limiter and batch omitted here
      exporters: [file/metrics]
    logs:
      receivers: [otlp]
      processors: [attributes/drop-email]
      exporters: [file/logs]
```

The real config also has a gRPC receiver, a health check, `memory_limiter` and `batch`, and a second exporter on each pipeline that feeds a local SigNoz backend. All listeners bind 127.0.0.1. Processors run before exporters, so the email is gone before any exporter sees the record. `max_days: 0` turns off age-based removal, and `max_backups: 0` keeps every rotated file. There is no compression key, so the output is plain JSON lines.

## Why not the obvious approach?

Three moves look reasonable at first. I rejected all three: one after testing it, one after it had already put a wrong rule in the notes.

**Compress the file.** The file exporter has a zstd mode, and it is the first thing you reach for with a log file. In the first trial, telemetry from headless Claude Code sessions landed in a zstd file that neither zstdcat nor jq could read. I reproduced it with one probe record posted to the HTTP receiver. The file came back with a binary prefix and was not JSON:

```console
$ od -A d -t x1 -N 8 logs.jsonl
0000000 00 00 00 8a 28 b5 2f fd
$ jq -c . logs.jsonl
# exit status 5
```

`zstdcat` could not decode it either; it printed the raw length-prefixed bytes. Stripping the 4-byte big-endian length and decoding the first frame (138 bytes) recovered JSON containing the probe. The data survived, but the standard tools could not read the file as delivered. I removed compression. The plan is for Borg (the nightly backup tool) to compress the files at backup time instead. The first archive containing them was still pending, so that part is not yet proven.

**Allowlist the attributes.** An allowlist keeps the fields you name and drops everything else. It is the safer default for fields you have not read yet, and it could keep the account UUID and organization ID just as well. I chose the single delete rule anyway, because it is one line and leaves every other field as Claude Code sent it. That is a trade-off, not a win. A delete rule only removes the key it names. A future field that carries an address passes through until someone adds a rule for it, which is why the first check under "Use this" has to be repeated.

**Read the last point.** The metrics are monotonic Sums with delta temporality (`aggregationTemporality` 1, which is DELTA). Each point is the increment since the previous export. The last point is one interval, not the total. An earlier README note in this build said to take the last cumulative point, and that note was the actual error. One review also argued the metrics were histograms. The trial receipt (a machine-written record that a step really ran) shows they are Sums, so that claim was wrong.

## Summing delta points for token and cost totals

The trial showed four Claude Code metrics (`claude_code.session.count`, `claude_code.cost.usage`, `claude_code.token.usage` and `claude_code.active_time.total`). These are two of them from one headless session, condensed from the exporter output (in the raw file the field is `aggregationTemporality`):

```json
{"name":"claude_code.token.usage","type":"sum","temporality":1,"monotonic":true}
{"name":"claude_code.cost.usage","type":"sum","temporality":1,"monotonic":true}
```

The window total is the sum of every point in it. Each point is only an increment, so a skipped point undercounts. The live install below lost one session's request event during an outage; metric-point loss was not measured. For a per-account split, group the sums by `user.account_uuid`. The same numbers also appear on the `claude_code.api_request` log events, which carry `input_tokens`, `output_tokens` and `cost_usd`.

## What the reviews caught

The first version had real defects. OpenCodeReview (14 findings) and two MiniMax reviews found that it stored the account email. They also found that the installer had no rollback, that a config change on a bind mount never recreated the container, and that claims ran ahead of the evidence. The installer now validates the config first, recreates the container with `--force-recreate`, and restores the previous copy if the new one does not come up healthy. Its test has 31 cases, 24 of them planted faults.

Not every finding was right. Claude Opus 5.5, the build session, accepted the valid findings and refuted two with evidence: the histogram claim, and a claim that an evidence rebinding was missing (it was in the diff). The second MiniMax review, the adversarial one, made me narrow the wording. The 100 MB file rotation is configured. It is not yet exercised. Claude Fable 5.1 ran the headless trial sessions that generated the telemetry, including the first trial that exposed the zstd framing.

## What the live install showed

On the live install, the collector came up with zero restarts and listened on loopback only. No prompt or tool-detail logging keys were set in the settings environment.

- A session with only the settings change exited 0. API request events went from 0 to 1.
- A session with the collector stopped exited 0 in 11 seconds. When the collector came back, it was healthy.
- After a Docker restart, the next session took the events from 1 to 2. The outage session's event never arrived. Claude Code did not hold it for the collector to receive later.
- Across 140 log records and 14 metric points in the live files, none carried `user.email`. The email domain appeared 0 times.
- Four records carried prompt or response attributes. Each held the literal value `<REDACTED>`.

## What the receipts do not show

- **Prompt and response content in general.** The redaction count covers four records from test sessions, not every event type Claude Code can emit.
- **How much an outage loses.** The event count shows one session's event went missing. It does not measure metric points lost, or what happens with a longer outage.
- **Backups.** The install is marked manually verified, not fully verified, because its sessions were test runs. The first backup archive containing the data directory was still pending.
- **Rotation.** Configured, not exercised.
- **A SigNoz outage.** That exporter is configured to retry for 60 seconds and then drop. Whether a SigNoz outage affects the file outputs was not tested.

## Also shipped

- Set `cleanupPeriodDays` to 3650, so the 1,581 local session transcripts on disk (2.6 GB) are no longer subject to Claude Code's default cleanup.
- Added the second exporter to a loopback SigNoz stack, whose first live check landed 71 log rows and 4 token-usage samples with `user.email` on 0 rows.

## FAQ

### Can I keep my email out of Claude Code OpenTelemetry data?

None of the documented switches covers user.email, so the fix is a drop processor in a local OpenTelemetry Collector that deletes the field before anything is written. In the pre-install trial the email appeared on 0 of 150 log records and 0 of 14 metric points after the rule, while the account UUID and organization ID stayed. A delete rule only removes the key it names, so a future field that carries an address passes through until a rule is added for it. Check your own output by running one session and grepping the files for your email domain.

### Are Claude Code OpenTelemetry metrics delta or cumulative?

The token and cost metrics are delta. They are monotonic Sums with aggregationTemporality 1, which is DELTA, so each point is the increment since the previous export and the last point covers only one interval. The window total is the sum of every point. A skipped point undercounts, and in the live install a session run while the collector was down never delivered its event.

### How do I total Claude Code tokens and cost from OpenTelemetry?

Sum every delta point of claude_code.token.usage or claude_code.cost.usage in the time window. For a per-account split, group those sums by user.account_uuid. The same figures also appear on claude_code.api_request log events as input_tokens, output_tokens and cost_usd. Do not read the last point, since it covers one export interval only.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Can I keep my email out of Claude Code OpenTelemetry data?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "None of the documented switches covers user.email, so the fix is a drop processor in a local OpenTelemetry Collector that deletes the field before anything is written. In the pre-install trial the email appeared on 0 of 150 log records and 0 of 14 metric points after the rule, while the account UUID and organization ID stayed. A delete rule only removes the key it names, so a future field that carries an address passes through until a rule is added for it. Check your own output by running one session and grepping the files for your email domain."
      }
    },
    {
      "@type": "Question",
      "name": "Are Claude Code OpenTelemetry metrics delta or cumulative?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The token and cost metrics are delta. They are monotonic Sums with aggregationTemporality 1, which is DELTA, so each point is the increment since the previous export and the last point covers only one interval. The window total is the sum of every point. A skipped point undercounts, and in the live install a session run while the collector was down never delivered its event."
      }
    },
    {
      "@type": "Question",
      "name": "How do I total Claude Code tokens and cost from OpenTelemetry?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Sum every delta point of claude_code.token.usage or claude_code.cost.usage in the time window. For a per-account split, group those sums by user.account_uuid. The same figures also appear on claude_code.api_request log events as input_tokens, output_tokens and cost_usd. Do not read the last point, since it covers one export interval only."
      }
    }
  ]
}
</script>

## Use this

- Check the drop before you trust it, and again after each Claude Code upgrade, since a delete rule misses any new field. Bind the receivers to 127.0.0.1, run one session, then `grep -c` your email domain across the output files. The trial found zero. Field names are listed in the monitoring docs at https://code.claude.com/docs/en/monitoring-usage.
- Write plain JSON lines (`format: json`, no exporter compression), then check them with `jq -c . logs.jsonl`. That is the check the zstd file failed.
- Total tokens and cost by summing every delta point in the window, and group by `user.account_uuid` for a per-account split. Do not read the last point, and keep the collector up, because a session run while it was down never delivered its request event.

## Related Posts

- [Four false-pass traps in restore verification for a SigNoz staging stack](https://startaitools.com/posts/a-green-recovery-drill-can-still-be-lying/)
- [An agent transcript pipeline that strips email addresses before export](https://startaitools.com/posts/wild-deep-dive-3-observability/)
- [A self-healing watchdog for the SigNoz staging stack](https://startaitools.com/posts/do-not-blindly-restart/)
