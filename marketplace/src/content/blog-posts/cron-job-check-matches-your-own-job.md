---
title: "Check If a Cron Job Is Running: Grep Matches Your Own Job"
description: "A cron job's grep of the process table matches the job that runs it. Walk /proc ancestors: an ancestor means you are the job, a sibling means a real collision."
date: "2026-11-16"
tags: ["ci-cd", "devops", "automation", "debugging"]
featured: false
canonical: "https://startaitools.com/posts/cron-job-check-matches-your-own-job/"
---
## How do I check if a cron job is already running without matching your own job?

Walk `/proc` for your own ancestors before you call a collision. Build the chain up from the shell that runs the check, then classify every process whose command line mentions the job: an ancestor means you are the job, so do the work; a sibling means a genuine collision, so let it finish or accept the duplicate row.

A scheduled job that checks whether it is already running can match its own process tree (the chain of processes the job starts) and conclude that a competing run owns the work. Reading `/proc`, the Linux filesystem that holds one directory per running process, for your own ancestors settles it: an ancestor match means you are the job, a sibling match means a genuine collision.

That near miss came out of an agent run that nearly handed the night's work to a process that did not exist. The rule that settled it was older than the run, already written down in a project note after an earlier instance. Here is the near miss, the running check that caused it, and the rule.

## The cron job is a chain of processes, not one process

The nightly compile on this box is not a plain script. A scheduler (cron) fires a shell, that shell runs a Python entry script, the entry script runs a bash wrapper, and the wrapper runs the agent that does the actual work, wrapped in a timeout and a pseudo-terminal helper (`script`) so its output is captured. Every stage stays alive while the run works.

An unattended job on this box has to get two things right: what it is looking at, and what it is about to touch. The second half is written up for the cron that mirrors this blog to a sister site at 4am in [Git Plumbing for an Unattended Cron on a Shared Checkout](https://startaitools.com/posts/git-plumbing-unattended-cron-shared-checkout/): the same unattended shape, landing a file into a checkout that interactive sessions also use, where the porcelain commands fail and plumbing does not.

So the nightly is a chain of about ten processes. When the run asks whether a nightly already owns this window, a window being one night's slice of work, the truthful answer is yes, and the interesting part is who. The check it reached for was the obvious one, a grep over the process table for the job name:

```bash
# The check as written.
ps -eo cmd | grep teamkb-compile

# The same check with the detail that shows who owns what. Run later in the
# day, from a second run.
ps -eo pid,ppid,lstart,etimes,cmd | grep -iE 'teamkb-compile|nightly-entry|claude -p'
```

## What the ps grep returned

```text
2418556 2418553 Mon Nov 16 03:30:00 2026  1939 /bin/sh -c PATH=... TEAMKB_COMPILE_TIMEOUT=4500 /home/jeremy/bin/teamkb-compile-daily.sh >> ... 2>&1
2418573 2418556 Mon Nov 16 03:30:00 2026  1939 python3 /home/jeremy/.local/lib/teamkb-compile/current/nightly-entry.py
2449252 2418573 Mon Nov 16 03:59:02 2026   198 bash /home/jeremy/.local/lib/teamkb-compile/releases/1a6a5f474c64b3c6edc3790e9da261030bc0ad6a/teamkb-compile-daily.sh
2449332 2449252 Mon Nov 16 03:59:02 2026   197 /usr/bin/timeout --kill-after=10s 4500 script -e -q -a -c /home/jeremy/.local/bin/claude -p '/teamkb-compile 2026-11-14 2026-11-15 --auto' ...
2449333 2449332 Mon Nov 16 03:59:02 2026   197 script -e -q -a -c /home/jeremy/.local/bin/claude -p '/teamkb-compile 2026-11-14 2026-11-15 --auto' ...
2449334 2449333 Mon Nov 16 03:59:02 2026   197 sh -c /home/jeremy/.local/bin/claude -p '/teamkb-compile 2026-11-14 2026-11-15 --auto' ...
```

Every line of that listing is an ancestor of the shell that ran the check. There is no competing process in it.

The bare listing does not say that. It is six lines with the job's name in the command column and two different start times, which reads like a nightly from an earlier window plus a second one that started later. Only the parent column gives the chain away, and only if you trace it by hand. The run summary from that morning puts it plainly:

> ps -eo cmd | grep teamkb-compile matched my *own* invocation and read exactly like 'a sibling nightly already owns this window' - I was about to stand down and let it run.

The nightly session had said so at 09:32, before it checked anything. The line that settled it reads:

> Important find - the nightly for this exact date is already running (cron-launched, same window/mode). Checking its progress before I write anything.

It was about to hand the window to itself.

## The ancestor walk through /proc

The decisive check is cheap. Walk up from your own PID through the parent chain in `/proc`, and then ask where the matching process sits in that chain.

```bash
echo "--- my ancestor chain ---"; P=$$; while [ "$P" != "1" ] && [ -n "$P" ]; do L=$(/usr/bin/tr '\0' ' ' < /proc/$P/cmdline 2>/dev/null | /usr/bin/cut -c1-160); echo "$P :: $L"; P=$(/usr/bin/awk '{print $4}' /proc/$P/stat 2>/dev/null); [ -z "$P" ] && break; done
```

```text
2459099 :: /usr/bin/zsh -c source /home/jeremy/.claude/shell-snapshots/snapshot-zsh-1794823149094-1xifn3.sh ...
2449335 :: /home/jeremy/.local/bin/claude -p /teamkb-compile 2026-11-14 2026-11-15 --auto --mcp-config ...
2449334 :: sh -c /home/jeremy/.local/bin/claude -p '/teamkb-compile 2026-11-14 2026-11-15 --auto' ...
2449333 :: script -e -q -a -c /home/jeremy/.local/bin/claude -p '/teamkb-compile 2026-11-14 2026-11-15 --auto' ...
2449332 :: /usr/bin/timeout --kill-after=10s 4500 script -e -q -a -c ...
2449252 :: bash /home/jeremy/.local/lib/teamkb-compile/releases/1a6a5f474c64b3c6edc3790e9da261030bc0ad6a/teamkb-compile-daily.sh
2418573 :: python3 /home/jeremy/.local/lib/teamkb-compile/current/nightly-entry.py
2418556 :: /bin/sh -c PATH=... /home/jeremy/bin/teamkb-compile-daily.sh >> /home/jeremy/.local/state/teamkb-compile-daily/cron.log 2>&1
2418553 :: /usr/sbin/CRON -f -P
3194076 :: /usr/sbin/cron -f -P
```

Two compile sessions ran on this box that morning, and they hit the same trap about half an hour apart. The listing above is the retry session's ps check at 10:02Z and the walk below is the same session's ancestor walk at 10:03Z, the one running the 2026-11-14 target after the previous attempt hit its deadline. The quotes that follow are from the nightly session at 09:32Z, which was running the 2026-11-15 window and reached the same false positive about half an hour earlier.

The chain ends in the scheduler. Every process between the scheduler and the shell running the check is an ancestor of that shell, so the walk does not find a competing run. It finds the chain of processes the run in question belongs to, and everything above the check is the job's own machinery.

The project's memory file already carried the rule, written after an earlier instance of the same bug. Before concluding that a nightly is running, walk your own ancestor chain and ask whether the matching process is an ancestor of you or a sibling. An ancestor means you are the nightly, there is no collision, and you must do the compile yourself. A sibling means a genuine collision, and you let it finish or accept the duplicate row.

The rule was already written down, and the nightly session went looking for it. Two minutes later its log reads:

> The watcher fired - but the memory's decisive check is the ancestor walk, not ps. Doing that now, plus reading the resolution.

Less than a minute later:

> Ancestor walk is decisive - I *am* the nightly. nightly-entry.py -> teamkb-compile-daily.sh -> timeout -> script -> claude -p '/teamkb-compile 2026-11-15 2026-11-16 --auto' -> me. The ps grep matched my own invocation - the documented false-positive.

That same nightly session went on to claim the receipts (a machine-written record proving a step really ran) for that night's capture file, and the claim held. They came from the capture tool that run was configured with: 19 of 19 hash-matched, 0 unattributed. That is the proof the work happened rather than being deferred to a phantom.

## Ancestor or sibling

Here is the classification, written so the liveness check can carry it:

```bash
# My own ancestor chain, as a space-separated PID list.
# Field 4 of /proc/$PID/stat is the parent, unless the command name in
# parentheses holds a space. The awk read below is the one that ran on
# 2026-11-16. The robust read takes the field after the last ')':
#   PPID=$(/usr/bin/sed -E 's/^.*\) [A-Za-z] ([0-9]+).*/\1/' "/proc/$PID/stat")
ANC=""
P=$$
while [ -n "$P" ] && [ "$P" != "1" ]; do
  ANC="$ANC $P"
  P=$(/usr/bin/awk '{print $4}' /proc/$P/stat 2>/dev/null)
  [ -z "$P" ] && break
done

# Every process whose command line mentions the job, minus the grep itself.
for pid in $(ps -eo pid=,cmd= | grep -F 'teamkb-compile' | grep -v ' grep ' | awk '{print $1}'); do
  case " $ANC " in
    *" $pid "*) echo "ancestor $pid : I am the job, do the work" ;;
    *)          echo "sibling  $pid : genuine collision, wait or accept the duplicate" ;;
  esac
done
```

The decision fits in two rows:

| Where the match sits | What it means | What the job does |
|---|---|---|
| Ancestor of the shell running the check | The check is running inside the job, so the job is the caller | Do the work now |
| Sibling of that shell | A second copy of the scheduled job is genuinely in flight | Let it finish and write the row, or accept the duplicate row |

One caveat on reading `/proc/$PID/stat`. Field 4 is the parent, but field 2 is the executable name in parentheses and it can hold spaces and parentheses of its own. A space alone shifts every later field for an awk read, and the parentheses are why the robust read takes the field after the last ')'. The walk above used the awk read, which is what ran on 2026-11-16; the sed read in the comment is the one to copy when a command name holds spaces.

Two outcomes, and they are not close in weight. An ancestor means the check is running inside the job, so the job is the caller and the caller does the work. Anything that is not an ancestor, a second copy of the scheduled job in flight or a leftover from an older run, is a collision to respect, and the window belongs to it until it writes its own row.

The sibling case carries a decision inside it, and the decision is yours rather than the rule's. Let the competing run finish and write the row, or let both run and accept that two rows exist for one date. What the classification rules out is the third option, where the caller quietly exits and nobody writes anything at all.

That third option is a helper that has become a gate. The general form of that defect is in [A Sidecar Fault Should Not Block the Main Deliverable](https://startaitools.com/posts/the-sidecar-must-never-block-the-deliverable/): a background helper that sits on the main path and blocks the output it exists to support. Here the helper is the liveness check and the deliverable is the verified row, so a check that cannot prove a collision must not close the window.

The walk has to run from inside the job, in a shell that descends from the job's own process tree. `$$` is the PID of the shell that runs the check, so the chain starts at the check and climbs to the agent, then to the scheduler. Run the same script from an interactive terminal and every match comes back a sibling, which is the honest answer for a process outside the job.

## Why not the obvious approach

**Why not exclude my own PID?** The matches are not you, they are your ancestors. The listing above holds six PIDs and not one of them is the PID of the shell running the check, so `grep -v $$` leaves all six behind with the same blind spot as the original check.

**Why not trust the lock?** The compile lock was held, and that fact was true and useless. A lock answers "is a holder present", and the holder was the caller's own ancestor tree. The lock has no way to say "held by me", because from the lock's side the holder is a PID and the caller is a different PID.

**Why not match on a unique run id?** Changing the string does not change the shape of the problem. The wrapper builds every stage of the tree from the same text, so a run id in that text lands in the command line of every stage, the way the job name lands there now. The grep would find your own ancestors again under a different name.

**Why not ask the scheduler?** Cron does not track its children. From outside, the process table holds a set of PIDs with a start time, which is the same evidence the grep already gave.

The class of mistake is not new on this box. A burn-in watchdog latched onto a phantom io spike on a healthy stack, and the rule that came out of it is in [Do Not Blindly Restart](https://startaitools.com/posts/do-not-blindly-restart/): classify the signal before you act on it, and let the unknown path stay the safe path. Here the action is not a restart but a stand down, and the signal is a name match on the job's own ancestor tree.

## What closes a window: the verified row

The other half of this failure is what counts as done. A date closes only on its own verified row, not on the fact that memories landed or that a row exists for a neighbouring date. The dispatcher recomputes the pending set every night as the known pending dates minus the ones with a verified row for that date and mode, a mode being the run mode the session was launched in, then sends the night's target first and the sorted remainder after it. A date with no verified row is retried every night until it verifies, and one failing date does not block the next one.

That is why the pending queue already carried the 2026-11-14 target, with a seven-day lookback. It had been killed at its 3000s deadline and left pending: the attempt that ran on the night of 2026-11-15 was the one that died, and its target was 2026-11-14. The retry session that did the ancestor walk was itself the in-flight job for that target, started at 03:59:02. When the false positive nearly ended that session early, the target would have had neither a verified row nor a second attempt, so it would have come back the next night anyway.

Two rows for one date and zero rows for one date are not the same problem. A duplicate row is noise that somebody has to reconcile. A missing row is a date with no evidence that it ran at all, and the dispatcher keeps offering it back.

## What the false positive cost

The rule exists because this was not the first time. On 2026-11-16 the false positive cost about two minutes and a watcher set up for a job that did not exist. It was never acted on: the walk came before the session gave the window away. On 2026-11-03 the same mistake parked a run for about 25 minutes watching itself, and nearly produced a duplicate row for 2026-11-02.

MiniMax M3 and MiniMax M3.1 Flash ran the two nightly compile sessions on this machine, and the false positive happened in both. The sharp moment was not an argument between a human and a model. It was a session correcting its own earlier conclusion. The nightly session decided a competing nightly owned the window and was about to stand down; the ancestor walk inverted that a couple of minutes later, and the same session did the work it had been about to hand to a phantom job.

## FAQ

### How do I check whether a cron job is already running without matching my own job?

Walk your own ancestors in `/proc` and classify each match by where it sits in that chain. Build the chain from the shell that runs the check (`$$`) upward through the parent field of `/proc/$PID/stat`, then compare it against every process whose command line mentions the job. A matching process that is an ancestor of the checker means the checker is running inside the job, so you are the job and you do the work. A matching process that is a sibling means a second copy is genuinely in flight, so you let it finish or accept the duplicate row.

### How do I find the parent PID of a process on Linux?

Field 4 of `/proc/$PID/stat` holds the parent PID, and reading it repeatedly from `$$` builds the chain of ancestors up to the scheduler. Field 2 is the executable name in parentheses and it can hold spaces and parentheses of its own. A space alone shifts every later field for an awk read, and the parentheses are why a robust read takes the field after the last `)`. The ancestor walk above uses that chain to decide whether a matching process is an ancestor or a sibling.

### Why does the process grep match my own cron job?

Because the job is a chain of processes and every stage stays alive while the run works. On this box the chain is cron, a shell, `nightly-entry.py`, the `teamkb-compile-daily.sh` wrapper, `timeout`, `script`, and the agent process, and the job name shows up in the command line of every stage below the scheduler. A grep for the job name therefore returns the job's own machinery, which reads exactly like a competing run. Excluding your own PID does not fix it, because the matches are your ancestors and not the shell running the check.

### What should the job do when the check finds a sibling process?

Let the competing run finish and write the row, or let both run and accept that two rows exist for one date. What the classification rules out is the third option, where the caller quietly exits and nobody writes anything at all.

### When is a nightly window actually done?

A date closes only on its own verified row. A neighbouring date's row, a memory saying the run happened, or a lock being held are all weaker evidence than the row itself. The dispatcher recomputes the pending set every night, so a date with no verified row is retried until it verifies, and one failing date does not block the next one.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do I check whether a cron job is already running without matching my own job?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Walk your own ancestors in /proc and classify each match by where it sits in that chain. Build the chain from the shell that runs the check ($$) upward through the parent field of /proc/$PID/stat, then compare it against every process whose command line mentions the job. A matching process that is an ancestor of the checker means the checker is running inside the job, so you are the job and you do the work. A matching process that is a sibling means a second copy is genuinely in flight, so you let it finish or accept the duplicate row."
      }
    },
    {
      "@type": "Question",
      "name": "How do I find the parent PID of a process on Linux?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Field 4 of /proc/$PID/stat holds the parent PID, and reading it repeatedly from $$ builds the chain of ancestors up to the scheduler. Field 2 is the executable name in parentheses and it can hold spaces and parentheses of its own. A space alone shifts every later field for an awk read, and the parentheses are why a robust read takes the field after the last ). The ancestor walk above uses that chain to decide whether a matching process is an ancestor or a sibling."
      }
    },
    {
      "@type": "Question",
      "name": "Why does the process grep match my own cron job?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Because the job is a chain of processes and every stage stays alive while the run works. On this box the chain is cron, a shell, nightly-entry.py, the teamkb-compile-daily.sh wrapper, timeout, script, and the agent process, and the job name shows up in the command line of every stage below the scheduler. A grep for the job name therefore returns the job's own machinery, which reads exactly like a competing run. Excluding your own PID does not fix it, because the matches are your ancestors and not the shell running the check."
      }
    },
    {
      "@type": "Question",
      "name": "What should the job do when the check finds a sibling process?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Let the competing run finish and write the row, or let both run and accept that two rows exist for one date. What the classification rules out is the third option, where the caller quietly exits and nobody writes anything at all."
      }
    },
    {
      "@type": "Question",
      "name": "When is a nightly window actually done?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A date closes only on its own verified row. A neighbouring date's row, a memory saying the run happened, or a lock being held are all weaker evidence than the row itself. The dispatcher recomputes the pending set every night, so a date with no verified row is retried until it verifies, and one failing date does not block the next one."
      }
    }
  ]
}
</script>

## Also shipped

- A backlog defect found while compiling: 116 candidates stuck in status='inbox', 106 of them captured 2026-07-16 and ten more scattered since. They are re-processed nightly (107 rejected plus 6 flagged that night) and never clear, because a rejected capture has no terminal state. A tracked task already covers it.

## Use this

- Replace the string match in your cron job's liveness check with a walk of your own ancestors in `/proc`. A matching process that is an ancestor of the checker means the checker is the job.
- Decide from the classification and not from the process count. Ancestor means do the work now. Sibling means let it finish or accept the duplicate row.
- Treat a window as open until its own verified row exists. A neighbouring date's row, a memory saying it ran, or a lock being held are all weaker evidence than the row itself.

## Related Posts

- [Do Not Blindly Restart: Designing a Self-Healing Watchdog That Stays Honest](https://startaitools.com/posts/do-not-blindly-restart/): a burn-in watchdog that latched onto a phantom io spike on a healthy stack.
- [Git Plumbing for an Unattended Cron on a Shared Checkout](https://startaitools.com/posts/git-plumbing-unattended-cron-shared-checkout/): the plumbing an unattended job needs before it touches shared state.
- [A Sidecar Fault Should Not Block the Main Deliverable](https://startaitools.com/posts/the-sidecar-must-never-block-the-deliverable/): a helper that fails in the background must not stall the work it supports.
