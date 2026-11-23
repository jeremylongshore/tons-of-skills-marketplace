---
title: "GitHub Webhook IP Allowlist: Add the New Hook Ranges"
description: "A static IP allowlist on a GitHub webhook receiver 404s deliveries from new hook ranges. GitHub does not redeliver, and health checks stay green."
date: "2026-11-22"
tags: ["devops", "debugging", "automation", "ci-cd"]
featured: false
canonical: "https://startaitools.com/posts/github-webhook-ip-allowlist-new-hook-ranges/"
---
If your GitHub webhook receiver sits behind an IP allowlist, GitHub can start delivering from a range your list does not contain, and your server never hears about it. This post covers how that happened to us, what it cost, and how to build a drift check (a scheduled comparison of your list against GitHub's) that proves its own alerts reach a person.

## How a static allowlist dropped 28% of deliveries

Our hooks subdomain runs behind Caddy (a web server acting as reverse proxy), and its virtual host admits only GitHub's published hook ranges. Everything else gets a 404. That outer layer is deliberate: forged requests are refused before they cost the receiver a process. The receiver still verifies each delivery's HMAC signature, a keyed hash GitHub attaches to every request, and that check is separate.

The weak point is the list itself. It is static, and GitHub adds ranges without notice. When GitHub delivers from a new range, Caddy answers 404, not 5xx. GitHub does not redeliver a failed delivery on its own. The receiver never sees the request. Its counters stay flat, its alerts stay quiet, and the health endpoint stays green. The service is healthy. It is just not being reached.

That is what we found on the VPS. The hooks access log held 62,055 POSTs. Of those, 17,538 (28%) got a 404, and every one came from three ranges missing from our list: 9.234.98.160/28, 9.234.98.176/28 and 9.234.106.48/28. GitHub had added them in October. Our committed and deployed copies matched each other and held six ranges, so nothing on the box disagreed with the repo. The repo was simply behind GitHub.

## The drift checker that reported the gap for weeks

We had an allowlist drift checker. It runs as a systemd service and has reported "DRIFT live-vs-deployed" every day since 2026-10-08. Nobody acted on any of it. From 2026-11-12 the reason is known: the team chat relay the alerts were meant for was retired that day, and they went to the spool, the queue where undelivered alerts wait. For the five weeks before that, the records I have do not show why the daily failure went unnoticed. The relay retirement is a second, separate failure, covered below.

## Why not let the checker fix it?

The obvious fix is to have the checker fetch the meta endpoint at 04:00 and rewrite the Caddy allowlist itself. We did not build it that way. The script header says it detects and does not apply. Rewriting a production ingress allowlist from a remote API response is a supply-chain hole. Anyone who could spoof or compromise that response would widen our allowlist for us, automatically, with no human in the loop.

So the checker compares, and the comparison has two directions because each gap means something different. Sketch of the logic, not the production script:

```sh
# Sketch of the comparison logic, not the production script.
curl -s https://api.github.com/meta | jq -r '.hooks[]' | sort > live.txt
sort deployed-allowlist.txt > deployed.txt
sort committed-allowlist.txt > committed.txt

comm -3 live.txt deployed.txt        # GitHub changed its ranges
comm -3 deployed.txt committed.txt   # someone hand-edited the box
```

A non-empty first diff means GitHub changed its ranges, and real deliveries may already be failing. A non-empty second diff means someone hand-edited the box. Both raise an alert. Neither applies a fix.

The other obvious approach is to trust the health checks. They stayed green while deliveries were failing, and that is the design problem. A check that runs inside the receiver cannot see a request that Caddy refused before it arrived.

## The Caddy matcher and the three missing hook ranges

Here is the shape of the rule. This is a hypothetical Caddyfile fragment with placeholder names, not our file:

```
hooks.example.com {
    @github remote_ip 192.30.252.0/22 185.199.108.0/22 140.82.112.0/20
    handle @github {
        reverse_proxy localhost:8080
    }
    handle {
        respond 404
    }
}
```

Anything outside the matcher gets a 404 before the receiver sees it. Adding a range means appending it to the matcher line, then caddy validate and a reload.

The three new ranges went into the committed allowlist as a reviewed repo change. That change widens the allowlist by 48 addresses, which GitHub publishes as its own. The receiver still rejects any request without a valid signature. The change does nothing on the box until it is applied, and at merge the apply was waiting for the owner's go-ahead. It ran about half an hour later. After the reload the checker reported nine ranges with live, deployed and committed in agreement, and the first deliveries from the new ranges were answered 200.

Verification: the meta endpoint returned the same nine ranges from the VPS and from the dev box, and the drift checker's drill mode, a self-test that stubs the fetch and the alert path, passed 12 of 12. The nine ranges are the six we already had plus the three missing ones.

Deliveries already dropped are a separate problem. GitHub does not redeliver them on its own, so our recovery path is the reconciler, the catch-up job meant to pick up missed events. We have not checked it for gaps yet.

## Why the alerts went quiet

This is a different failure from the stale allowlist, and from 2026-11-12 it is the reason the stale allowlist stayed hidden. Buzz, the self-hosted team chat relay, was retired on 2026-11-12. We then moved the shared alert library's default transport to Discord. But four alert producers passed the Buzz notifier explicitly: a VPS liveness sweep (a job that checks other jobs are still alive), a deploy notifier, a staging burn-in watchdog and a runtime helper. A caller that names a transport never sees the default, so their alerts kept landing in the spool. The liveness sweep matters most here: the drift checker's daily failure turns the sweep red, and the sweep's digest was one of the alerts that never left the box.

The logs show it. The VPS spool gained two liveness digests (periodic health summaries) on 11-21 and 11-22, and the unit journal shows "channel discovery failed ... dns error." The dev-box spool gained 37 Dolt push failures. Dolt is a version-controlled SQL database, and our task tracker runs on it.

The fix was to unpin, not re-pin. Re-pinning would break again at the next transport change. Callers now leave the variable empty, which means "follow the library's default transport":

```sh
# Before: the caller names a transport, so the library default never applies.
AF_BUZZ_CMD="<pinned notifier>"

# After: empty means "use the alert library's default transport".
AF_BUZZ_CMD=""
```

The change also includes a regression test that fails if any producer pins the retired transport. The test reports 36 passed, 0 failed on the new source. Run against the previous source, it reports 35 passed and 1 failed, with "alert producer still pins the retired Buzz transport." A guard that has never failed is not evidence, so we ran it against the old code to see it fail. The principle is laid out in [Make the Guard Prove It Can Fail](https://startaitools.com/posts/the-gate-that-could-not-fail/).

Still unfinished: each caller needs a redeploy and a delivery receipt, a machine-written record that a real alert arrived.

## How the allowlist gap was found

The allowlist gap was found while working the alert-delivery incident, not from the drift alerts. Reading the undelivered spool and the failing checks behind it is what surfaced the checker's daily DRIFT result. The incident work ran across twelve Claude Code sessions on Claude Fable 5.1 over one day.

## Use this

- Compare your GitHub webhook IP allowlist against the live hooks list today with `curl -s https://api.github.com/meta | jq -r '.hooks[]'`. The key is documented at https://docs.github.com/en/rest/meta/meta.
- Run both comparisons on a schedule, live against deployed and deployed against committed, and make any non-empty diff exit non-zero so the scheduler reports it.
- Test the alert, not only the checker. Break a copy on purpose, confirm the message reaches a channel a person reads, and keep the delivery receipt as evidence.

## Frequently asked questions

### Where does GitHub publish its webhook IP ranges?

GitHub publishes its current hook ranges under the `hooks` key at `api.github.com/meta`, documented at https://docs.github.com/en/rest/meta/meta. Run `curl -s https://api.github.com/meta | jq -r '.hooks[]'` to list them. GitHub adds ranges without notice, so compare the list on a schedule.

### Does GitHub redeliver a webhook that failed?

Not on its own. GitHub does not redeliver a failed delivery by itself, so a request refused at the allowlist stays lost unless a catch-up job recovers it. Our reconciler, the catch-up job for this receiver, has not been checked for gaps yet.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Where does GitHub publish its webhook IP ranges?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "GitHub publishes its current hook ranges under the hooks key at api.github.com/meta, documented at https://docs.github.com/en/rest/meta/meta. Run curl -s https://api.github.com/meta | jq -r '.hooks[]' to list them. GitHub adds ranges without notice, so compare the list on a schedule."
      }
    },
    {
      "@type": "Question",
      "name": "Does GitHub redeliver a webhook that failed?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Not on its own. GitHub does not redeliver a failed delivery by itself, so a request refused at the allowlist stays lost unless a catch-up job recovers it. Our reconciler, the catch-up job for this receiver, has not been checked for gaps yet."
      }
    }
  ]
}
</script>

## Related posts

- [Six Systems Reporting Nothing](https://startaitools.com/posts/the-status-nothing-could-write-to/): a health check that lied, and a reporter that could not report.
- [Wrong-mode green is not a gate](https://startaitools.com/posts/wrong-mode-green-is-not-a-gate/): a freshness gate that accepts the wrong mode flag still exits green.
- [The Refusal Nobody Heard](https://startaitools.com/posts/the-refusal-nobody-heard/): a correct refusal that nothing was wired to hear.
