---
title: "Sieve :copy dies: rebuild the reply copy in the IMAP poller"
description: "Rebuild the inbox-reply copy loop in the IMAP poller with a named skip set as the safety net when the server-side Sieve redirect dies."
date: "2026-10-02"
tags: ["catalyst-onboarding", "imap", "mxroute", "devops"]
featured: false
canonical: "https://startaitools.com/posts/moved-the-reply-loop-in-app-when-sieve-died/"
---
MXroute disabled the Sieve `:copy` redirect on a shared mailbox in March 2024, without SRS, and stopped forwarding human replies to the owner. The shared mailbox kept receiving them. The runbook still said the copy rule was active. Two years later, the owner noticed.

The cleanest fix was to stop trusting the runbook and rebuild the copy loop in the IMAP poller. The poller already had every inbound message indexed by Message-ID and review class. Adding a single job that re-emits the body to the owner only when a skip rule says it is safe, turned the poller into the loop's source of truth. Five hundred ninety eight tests cover UIDVALIDITY reset, retries, and the uncertain-send reconcile.

**The skip set, named out loud.** This is the safety net, not the transport. The poller drops the copy when any of these match:

```text
skip if:
  From is the service mailbox
  From matches noreply | no-reply | donotreply | do-not-reply | mailer-daemon | postmaster
  Auto-Submitted header is anything other than "no"
  message is a bounce
  message is our own Bcc copy
  Message-ID is one we already wrote
  From host is the Documenso signing service
```

Every rule has a unit test. A separate integration suite covers the catch-up case where the poller falls behind and resumes mid-stream. Migration 0010 expands two columns to nullable (`outbound_message.case_id`, `inbound_message.reviewed_at` and `reviewed_by`) so the new path can write what it needs without touching existing rows.

**Why the runbook had a false claim.** Section 2d of runbook 019 said a Sieve `:copy` rule was forwarding human replies to the owner. The rule existed. MXroute disabled the `redirect` action server-side in 2024. The rule has been inert since. Diagnostic output from `imap4flags` confirmed it: Sieve ran only when the script was redirect-free, and fell back to keep when a redirect was present. The runbook now says so.

**The guard that almost shipped silent.** The earlier send-email helper accepted an unknown flag and forwarded under the operator's login with the new envelope sender. The user would have sent under `jeremy@` with an `agreements@` From. The new helper refuses at startup unless the installed sender supports `--sender-env-file` and the credentials file is readable. Exit 2, nothing runs. That is the kind of failure a guard test catches, not a hopeful review.

## Also shipped

- Welcome email re-vendored at v1.11 with the LinkedIn highlight restored. v1.10 stays deployed under its own hash and `welcome_sent` events record the version.
- Five Catalyst task records now carry a 2026-10-02 production evidence entry. Each carries a machine-written production note. None are closed.
- The readiness gate audit got re-run against live production. `python -m catalyst.ops flags` inside a container printed `VIOLATION` for every `ON` flag, because the approvals file is not mounted into containers and the deploy pipes it in on stdin. The fix landed in the runbook, not in the container. A monthly `catalyst-restore-drill.service` and `.timer` were added.
- Readiness gate 2.11 marked done now that the outside-in probes are merged.
- CI lint and unit job timeout raised from 15 to 25 minutes. The job was cancelled at 15 minutes twice on the readiness re-audit while the dev box was loaded (load average 9 to 18). Same suite runs in 10 minutes on a quiet runner and 16 under load. A larger limit beat trimming the suite because the failure is runner contention, not a slow test.

## Use this

- When an external copy path dies, name the skip set explicitly before rebuilding the loop in the poller. The skip set is what makes the rebuild safe.
- When a runbook describes a path that runs outside your process, verify it with a live diagnostic, not a re-read. The Sieve redirect was inert for two years before the runbook caught up.
- When a shared mailbox has a From address different from the operator's login, refuse at startup if the sender does not support per-message credentials. Silent fallback is the failure mode.

## Related Posts

- {{< ref "rehearse-before-production-catches-what-tests-cant.md" >}}
- {{< ref "link-public-surface-to-deployment-thesis.md" >}}
