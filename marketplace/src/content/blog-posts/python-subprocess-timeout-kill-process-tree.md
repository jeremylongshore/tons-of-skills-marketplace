---
title: "Python subprocess Timeout: Kill the Whole Process Tree"
description: "On a Python subprocess timeout, kill every descendant, not just the child. A grandchild could finish a webhook POST after the caller got unknown."
date: "2026-11-21"
tags: ["python", "debugging", "devops", "automation"]
featured: false
canonical: "https://startaitools.com/posts/python-subprocess-timeout-kill-process-tree/"
---
A timeout that kills only the process you started leaves the processes that process started running. In a notification adapter, a code review showed that a webhook POST could still finish after the caller had already been told the call was unknown. This post covers the failure, the fix, and the test that checks the grandchild is actually dead, so you can apply the same pattern to your own timeouts.

## The chain that outlived its parent

The adapter sends alerts by running a shell script. That shell runs a transport script, which runs python3, which makes the Discord POST. The request runs in python3, below the shell the adapter started, out of reach of anything that signals only that shell.

The adapter enforces two limits: a 20 second deadline and 16 KiB of output. When the deadline passed, it called `kill()` on the shell process. The shell died. The python3 process did not.

On deadline, the adapter returned `unknown`. That word is the trap. A caller reads unknown as "it may not have sent." The adapter never resends on its own, but if a person or a later run sends the alert again while the orphaned POST also completes, the alert pages twice. The orphan also keeps the webhook secret in its environment for as long as it runs.

## How it was found

The tests did not catch this. An automated reviewer, OpenCodeReview, ran on the pull request and flagged that a killed bash could let the POST complete after the adapter reported unknown. Earlier review runs on the same PR timed out on `adapter.py` and returned partial coverage. The PR body records those runs as partial, never as approval.

The sources record no duplicate page from production. The bug was found in review, on a pull request that is still open.

## The fix: freeze the whole tree before killing it

Linux exposes every process under `/proc`. Each process has a `stat` file. After the command name in parentheses, the first field is the process state and the second is the parent PID (the code splits on the last `)` because command names can contain spaces and parentheses). Read them all, build a parent-to-children map, and walk it breadth first from the root PID.

Killing the tree is then two passes:

```python
def terminate_tree(pid):
    for signal_number in (SIGSTOP, SIGKILL):
        for target in [pid] + descendants(pid):
            try:
                os.kill(target, signal_number)
            except ProcessLookupError:
                pass
```

The first pass sends SIGSTOP to the root and every descendant, so the tree stops growing. The second pass rescans the tree and sends SIGKILL. The rescan picks up any child forked before its parent was stopped. Stopped processes still show up in `/proc`, so the rescan sees every process still parented under the root.

The adapter does not start a new session or process group. The outer worker creates the adapter's process group and kills that group on timeout. A new group inside the adapter would move the grandchildren out of that group, where the outer cleanup cannot reach them. The commit message puts it the same way: a new group would escape cleanup.

The walk has a limit. It follows parent links. A process that has been reparented before the walk runs is no longer under the root PID, so the walk will not find it. The adapter's README says standalone dispatch is not the complete containment boundary. The outer worker is.

## A test that proves the grandchild is gone

The new test, `test_deadline_kills_grandchild_transport`, uses a fake library. The fake library's shell records its own PID (the child), and its dispatch starts a `bash -c` process that writes its own PID to a file and spins forever. That second bash stands in for the process making the POST (the grandchild). A fake clock jumps past the 20 second deadline once the grandchild exists.

The test asserts two things. First, `dispatch()` returns `unknown`. Second, for both the child and the grandchild PID, `os.kill(pid, 0)` must raise `ProcessLookupError` or `/proc` must report state `Z`. A zombie (a finished process its parent has not yet reaped) counts as killed for this check.

The stand-in is bash, not the real POST. The test shows the tree kill works. It does not show that a real Discord request is blocked. The commit reports 17 passing tests, including this one.

The original code called `kill()` on a process object from the standard library's `subprocess` module. The docs for that method are at https://docs.python.org/3/library/subprocess.html. The method signals the child you started and nothing that child started. That gap is what this fix covers.

## Where this stands

The pull request is still open. Deployment is not authorised. All evidence so far is fixture evidence, not actual external delivery. Killing the tree stops the orphan, but it cannot undo a POST that was already delivered. The README says a lost provider response may follow delivery, and no automatic resend is authorised. So the fix narrows the duplicate-page risk. It does not remove the unknown result.

## Use this

- Before you SIGKILL a timed-out child, collect its descendants from `/proc` and send SIGSTOP to the whole tree first.
- If an outer process group already owns cleanup, do not start a new session or group inside the call. It puts your children out of reach.
- In your timeout test, start a stand-in grandchild, move the clock past the deadline, and assert the grandchild PID is gone, not just that the function returned.

## Related Posts

- [Exit codes lie about the state the next run inherits](https://startaitools.com/posts/exit-zero-is-not-push-ok/)
- [A heartbeat proves a job ran, not that it succeeded](https://startaitools.com/posts/liveness-without-health-is-theater/)
- [A static analyzer found a real TOCTOU race in audit code](https://startaitools.com/posts/codeql-caught-the-race-i-dismissed/)
