# Private diagnostic collection

Use the [main collector](../SKILL.md) after approving the target, queries and pinned
CLI. It creates a unique owner-only directory and archive with `umask 077`; it does
not authorize a remote operation or sanitize arbitrary command output.

Do not collect `.env`, shell history, home-directory package logs, raw CLI status,
or credentials merely because they are accessible. A multiline secret can survive
line-oriented `s/=.*/.../` masking, and a matching log line can contain request data.
Record selected runtime/package versions and approved observations instead.

Inspect `version-status.tsv` and `inspect-status.tsv` before interpreting output.
A file can contain an error or partial output. Nonzero receipts remain failures;
a published platform-status response does not prove this project is healthy.

The archive is an unreviewed local candidate. Create a separate minimized export,
review every included field and file for secrets/personal data, and obtain approval
for those exact bytes before sharing through the intended support channel. Keep
private originals under the operator's approved retention policy. Do not invent a
health endpoint or attach this candidate automatically.
