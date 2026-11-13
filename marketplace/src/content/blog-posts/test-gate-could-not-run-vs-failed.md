---
title: "Test Gate Exit Codes: Add a Could-Not-Run Result (pytest)"
description: "A test gate needs a pinned interpreter and a could-not-run exit code beside its test verdict. Here \\"No module named pytest\\" cost six weekly agent runs."
date: "2026-11-08"
tags: ["ai-agents", "testing", "ci-cd", "automation", "python", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/test-gate-could-not-run-vs-failed/"
---
An unattended agent took the same work item six Sundays in a row, and the test gate refused it every time. All six logs show the same line, "No module named pytest," right before the gate's verdict, and the gate reported it as the same FAIL a real test failure gets. This post shows how to report "could not run" separately from "ran and failed," how to pin the interpreter a gate calls, and how to stop re-queuing work when the gate itself could not run. The code change is small.

## Six weekly runs on the same failing gate

The worker is a headless agent, meaning one with no person at a terminal, that a weekly cron job starts. Each run takes the open work item with the lowest priority number and tries to implement it on a new branch. The work item is a bead (a tracked task record in the repo's issue database). This one asked for better alerting on a monitoring check. That check had stayed quiet for five weeks while a metric sat past its alert threshold, because it only alerted when a breach began or got worse.

Before the worker opens a pull request, a gate must pass. The gate is a set of deterministic checks, meaning checks with no model in the loop. It runs shellcheck, ruff, the pipeline invariants and pytest, in that order.

Here is each run's record. The three timeout Sundays share a row.

| Sunday | Agent exit | Agent seconds | Gate result |
|---|---|---|---|
| 2026-10-04 | clean | 1455 | FAIL pytest |
| 2026-10-11, 10-18 and 10-25 | timeout (124), all three | 2700 to 2701 | FAIL pytest, all three |
| 2026-11-01 | clean | 2270 | FAIL pytest |
| 2026-11-08 | clean | 1398 | FAIL pytest |

The agent sessions add up to about 13,200 seconds, or 3.7 hours. Three runs hit the 2700-second timeout while the agent was still waiting for a background job to report back. In two of those logs the job was the gate or its pytest suite, which takes about 19 minutes when it can run at all. No human was in the loop, so nothing stopped the cycle.

Two runs also reported a passing suite. The 2026-11-01 run claimed 1672 passed and 7 skipped. The 2026-11-08 run claimed 1695 passed and 7 skipped. Neither claim reached the gate. The worker's own header comment says it plainly: "The agent's own claim that tests pass is not evidence."

## Why the gate printed FAIL for a missing module

The pytest step lives in lint-all.sh. It calls python3 without a path, so the interpreter it runs depends on PATH, the list of folders the shell searches for commands.

```bash
step "pytest"
if python3 -m pytest tests/ -q 2>&1 | tail -1; then ok "tests pass"
else bad "pytest"; fi
```

In the worker's run, PATH resolved python3 to /usr/bin/python3, the system interpreter. That interpreter had no pytest module. Trimmed to the pytest step, the log reads:

```text
== pytest
/usr/bin/python3: No module named pytest
   FAIL pytest
```

A few lines later the worker logs that the gate failed, that it is not opening a pull request, and that the branch is left in place for inspection. Between those lines the gate prints a reminder that "CI runs exactly these."

The worker treats every failed gate the same way. It sets the bead back to open, writes a note and calls the cron failure alert. Trimmed, the block looks like this:

```bash
if bash scripts/blog/lint-all.sh >>"$LOG" 2>&1; then
  log "Gate PASSED"
else
  bd update "$BEAD" --status open >/dev/null 2>&1 || true
  bd-sync note "$BEAD" "Worker implemented this but lint-all.sh failed; branch ${BRANCH} left for inspection. Log: $LOG" >/dev/null 2>&1 || true
  cron_fail "blog-recommendation-worker" "Bead ${BEAD}: gate FAILED, no PR opened. Branch ${BRANCH}. Check ${LOG}"
  exit 13
fi
```

Nothing in that block separates "the tool is missing" from "a test failed." Both end as worker exit 13. The bead notes show the result six times, with the same sentence each Sunday: "Worker implemented this but lint-all.sh failed."

The continuous integration (CI) workflow runs the same command. The file scripts-lint.yml installs pytest==9.1.1 and Pillow with pip, then runs python3 -m pytest tests/ -q. The command matches. The CI and cron environments differ. The gate's own message says "CI runs exactly these," which is true of the command and false of the interpreter.

## The venv fix that never reached the gate

On 2026-11-08, Claude Sonnet 5 ran the worker. It found a branch from 2026-11-01 with a complete implementation, reviewed it and cherry-picked it. Then it hit the same missing module. Its steps, in order:

- It tried `python3 -m pip install --user pytest`. PEP 668, the externally managed environment rule that blocks pip from writing into the system Python, refused it.
- It checked whether apt offered a python3-pytest package. It did not install one.
- It read scripts-lint.yml to find the pytest version CI pins.
- It built a virtual environment (venv) in /tmp, installed pytest==9.1.1 and Pillow, and ran lint-all.sh with that venv first on PATH.
- The run came back green: 1695 passed, 7 skipped. The agent committed the change and removed the venv as tidy-up.

The worker's gate ran 24 seconds after the agent exited and failed on the same missing module.

The agent's diagnosis was correct. Its summary said the earlier branch "had failed only because its sandbox lacked pytest." Its commit body said the run used a fresh venv, "not a workaround of the gate itself." The fix was real. It was also local. The new commit sat on a local branch beside the one it was copied from, neither pushed, with no pull request. The 1695 count came from the agent's own shell, and the gate never reached a count.

## Why not install pytest in the agent's shell and rerun?

Installing pytest in whatever shell hit the error is the obvious fix, and the agent tried it. It does not hold as a design, for three reasons.

It fixes one shell. The agent's venv lived in its own shell. The worker's interpreter is a different one, so the next Sunday starts from the same missing module.

It cannot be a user install here. The system Python refuses pip installs under PEP 668, so the fix has to be a venv, and a venv the agent builds in /tmp and then deletes protects nothing.

It makes the verdict depend on who ran it. A gate that passes in an agent's shell and fails under cron is measuring the shell. The gate should measure the same thing every run.

The pinned interpreter below also installs pytest. The difference is where it lives and who owns it: a fixed path the gate calls on every run, built once from the CI pin.

## How should a test gate report a tool it cannot run?

Make the gate exit with its own code when a required tool cannot run, and make the caller branch on that code. In the worker's failing runs, a missing pytest module printed the same FAIL as a real test failure, and the worker turned both into exit 13. The proposed change calls a pinned interpreter by absolute path, has the gate exit 69 when it cannot import pytest, and has the worker treat 69 as a separate outcome.

I would make three changes. None of them is in the repo. The first is a pinned interpreter for the gate. The second is a distinct gate exit code for "could not run." The third is a worker branch that reads that code instead of collapsing it. The sketch below shows all three, as a shape and not a tested patch.

```bash
# Sketch only, not in the repo.
# In lint-all.sh: pin the interpreter and name the failure.
GATE_PY="/opt/blog-gate/venv/bin/python3"  # a path you choose, built with the CI pytest pin
if ! "$GATE_PY" -c 'import pytest' 2>/dev/null; then
  echo "GATE COULD NOT RUN: $GATE_PY cannot import pytest" >&2
  exit 69  # EX_UNAVAILABLE in sysexits.h; real test failures still go through bad() and exit 1
fi
if "$GATE_PY" -m pytest tests/ -q 2>&1 | tail -1; then ok "tests pass"
else bad "pytest"; fi

# In the worker: read the gate's status instead of collapsing it.
bash scripts/blog/lint-all.sh >>"$LOG" 2>&1
gate_rc=$?
if [ "$gate_rc" -eq 69 ]; then
  # park the bead with one "gate could not run" note and one alert
  exit 15  # 11 through 14 and 64 already mean other things in this worker
elif [ "$gate_rc" -ne 0 ]; then
  # the existing code-failure path: reopen, note, alert
  exit 13
fi
```

The gate's exit code is the part the worker can act on, and only if the worker reads it. Today the worker collapses every non-zero gate result into 13. With the split, 13 means a gate ran and found a problem, and 69 from the gate means it never ran.

On 69, the worker should not reopen the bead as though the code had failed. I would set the bead to a status other than open (the picker only takes open beads), write one note with the words "gate could not run," and alert once. The bead goes back to open when someone fixes the environment, not when the calendar says Sunday.

## What it cost

Six Sundays produced about 13,200 agent-seconds, six identical notes on one bead and six calls to the failure alert. The bead went back to open after the last run. The finished work sits on two local branches, never pushed, with no pull request.

## Use this

- Give the gate its own pinned interpreter. Build a venv at a fixed path, install the pytest version CI pins, and call that Python by absolute path instead of python3 from PATH.
- Exit with a separate code when a required tool cannot be imported, and make the caller branch on it. A could-not-run result should park the work item with one note and one alert, not reopen it for the next run.
- Rerun the gate from the cron environment before you trust an agent's green result. Start with the gate block in [scripts/blog/blog-recommendation-worker.sh](https://github.com/jeremylongshore/startaitools.com/blob/master/scripts/blog/blog-recommendation-worker.sh), since that is where the reopen happens.

## Frequently asked questions

### Why does a cron job say No module named pytest when CI runs the same command?

The cron worker's gate runs python3 from PATH, which resolved to /usr/bin/python3, a system interpreter with no pytest module. CI installs pytest==9.1.1 and Pillow with pip before running the same command, so the command matches and the environment does not.

### Why not just install pytest and rerun the gate?

The agent's venv lived in its own shell, so the worker's interpreter would still lack pytest the next Sunday. On this machine, PEP 668 blocks user installs into the system Python, which leaves a venv as the only path. A gate that passes in an agent's shell and fails under cron is measuring the shell.

### Why does pip refuse to install pytest into the system Python?

PEP 668 is the rule that blocks pip from writing into the system Python. In the worker's run, `python3 -m pip install --user pytest` was refused under it. That leaves a venv as the only path on this machine, and the agent deleted its venv in /tmp after the run.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Why does a cron job say No module named pytest when CI runs the same command?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The cron worker's gate runs python3 from PATH, which resolved to /usr/bin/python3, a system interpreter with no pytest module. CI installs pytest==9.1.1 and Pillow with pip before running the same command, so the command matches and the environment does not."
      }
    },
    {
      "@type": "Question",
      "name": "Why not just install pytest and rerun the gate?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The agent's venv lived in its own shell, so the worker's interpreter would still lack pytest the next Sunday. On this machine, PEP 668 blocks user installs into the system Python, which leaves a venv as the only path. A gate that passes in an agent's shell and fails under cron is measuring the shell."
      }
    },
    {
      "@type": "Question",
      "name": "Why does pip refuse to install pytest into the system Python?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "PEP 668 is the rule that blocks pip from writing into the system Python. In the worker's run, python3 -m pip install --user pytest was refused under it. That leaves a venv as the only path on this machine, and the agent deleted its venv in /tmp after the run."
      }
    }
  ]
}
</script>

## Related Posts

- [Six Systems Reporting Nothing](https://startaitools.com/posts/the-status-nothing-could-write-to/)
- [Make the Guard Prove It Can Fail](https://startaitools.com/posts/the-gate-that-could-not-fail/)
- [Every Check Should Report What It Did Not Look At](https://startaitools.com/posts/the-lane-that-reviewed-nothing/)
