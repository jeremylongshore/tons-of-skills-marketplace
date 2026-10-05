# Triage display runtime contract

## Exposed surface

parse_review_command accepts message_text and returns a ParsedCommand. It recognizes details, file,
dismiss, merge, escalate, monitor, snooze, split, reroute, full-report, and confirm file syntax.
Input is lower-cased before parsing, including free-form arguments.

The parser validates syntax only. It does not load current clusters, check cluster-number bounds,
perform authorization, or execute an action.

## Library-only behavior

formatActionConfirmation() returns canned success language for a valid ParsedCommand. It does not
check an execution receipt. Therefore skill output must not use that helper as proof of mutation.

No MCP tool formats summaries, loads run data, writes terminal state, or sends Slack messages.
Formatting remains a presentation procedure over caller-supplied data.
