---
title: "Claude Code Stop Hook: Block Until Reads and Tests Are Real"
description: "A Claude Code Stop hook can hold an agent until required file reads and real test counts exist. Run it in observe mode first, then enforce."
date: "2026-11-27"
tags: ["claude-code", "ai-agents", "testing", "automation", "python"]
featured: false
canonical: "https://startaitools.com/posts/claude-code-stop-hook-skill-compliance-gate/"
---
An AI coding agent can finish a task and say "tests passed" without having read the files its skill told it to read or run the tests its skill told it to run. (A skill is a packaged set of instructions the agent loads for a task.) Nothing in the session separates a claimed pass from a measured one. By the end of this post you will have the shape of a fix for Claude Code (Anthropic's coding agent for the terminal): a small policy file and one Python hook script that refuse to let the agent stop until fresh, machine-recorded evidence exists. A hook is a command the agent's host program runs on session events, such as a tool call or the agent trying to stop.

The finding is narrow. A skill's instructions are a request. They are not proof. Proof has to come from something the agent cannot satisfy by typing a sentence. Here that is a script (I call it the collector) that reads the required files and launches the tests itself, plus a Stop hook, run by the host program, that checks the collector's record before the agent is allowed to finish. This is for anyone who ships skills or instruction files to a coding agent and needs to know whether the steps were followed. The evidence behind it is one skill on one host version, and the limits are listed near the end.

## The policy file

Everything the gate (the policy file plus the hook script) checks lives in one JSON file. I ran it as a pilot on one skill, named `verify-skill-gates`. This is its reviewed policy as it stands now (it first shipped with `mode` set to `observe`):

```json
{
  "schema": "audit-harness/skill-gates/v1",
  "mode": "enforce",
  "skill": "verify-skill-gates",
  "inputs": [
    "scripts/skill-gates-claude.py",
    "tests/skill-gates/test_claude.py",
    "examples/skill-gates/check.py"
  ],
  "must_read": [
    "examples/skill-gates/README.md",
    "examples/skill-gates/verify-skill-gates/SKILL.md"
  ],
  "must_run": [
    {
      "id": "adapter-replay",
      "argv": ["python3", "examples/skill-gates/check.py"],
      "timeout_ms": 60000,
      "min_tests": 9
    }
  ],
  "checklist": ["required-reads", "adapter-replay", "fresh-evidence"],
  "deny_tools": ["WebFetch"]
}
```

Five fields carry the policy. `must_read` lists files whose bytes the agent has to pull through the collector. `must_run` lists commands by exact argv, each with a timeout and a minimum test count. `deny_tools` names tools refused outright. `mode` is `observe` or `enforce`. `inputs` declares further files whose change invalidates old evidence. The other three are labels: `schema` and `skill` identify the policy, and `checklist` names the items the final report lists.

The schema string belongs to audit-harness (a separate package of deterministic test-quality checks, first shipped in [v0.1.0](https://startaitools.com/posts/audit-harness-v010-enforcement-travels-with-code/)). The collector imports the harness verifier source with an exact SHA256 check rather than restating the policy semantics, so there is one definition of what "assessed" means.

The script has two roles. As a hook, it receives session events from Claude Code. As a command line tool, it has three actions (`read`, `run` and `report`) that the skill tells the agent to invoke as its steps. `read` emits a required file's bytes and records their digest. `run` launches a declared command. `report` prints the result row. A sentence from the agent changes nothing in the record. Only those actions do.

## Four hook events, one command

The hook registration is one command, reused for `UserPromptSubmit`, `PreToolUse` (matcher `.*`), `PostToolUse` (matcher `.*`) and `Stop`, each with a 10 second timeout. The Stop hook entry:

```json
"Stop": [{"hooks": [{"type": "command",
  "command": "python3 \"$CLAUDE_PROJECT_DIR/scripts/skill-gates-claude.py\" hook --policy \"$CLAUDE_PROJECT_DIR/examples/skill-gates/gates.json\" --root \"$CLAUDE_PROJECT_DIR\"",
  "timeout": 10}]}]
```

Each event has one job:

- `UserPromptSubmit` starts a new receipt (a machine-written record proving a step really ran) when the user explicitly invokes `/verify-skill-gates`, and hands the session ID to the skill.
- `PreToolUse` denies exact tool names in `deny_tools`. This applies in both modes.
- `PostToolUse` observes. It never converts a tool's claimed success into evidence.
- `Stop` assesses the receipt. In enforce mode, missing evidence returns exit code 2, which tells Claude Code to refuse the stop (the limits section says when that does not hold).

Activation is deliberately narrow. The skill sets `disable-model-invocation: true`, and automatic invocation or calls through the Skill tool do not activate the pilot. Only an explicit slash command does. A clean Stop deactivates the gate for later tasks in the session.

## Why not trust the tool output, or ask the agent?

Three obvious approaches fail. Two of them read a claim, and the third arrives too late.

Asking the agent to report what it did produces prose. The skill's own text says the pilot cannot prove the final prose is true, and the `report` step does not inspect or certify the assistant's final message. It emits a `gate-result/v1` row from the receipt instead.

Watching `PostToolUse` for a Bash call that ran the test command looks closer, but it still trusts whatever the tool returned. One of the ten replay tests (offline tests that drive the script as a real process) exists to pin this: `test_post_tool_does_not_accept_tool_success_as_command_evidence`. Evidence only comes from the collector's own `run` action, which launches the declared argv itself.

Scanning the transcript afterward is late. The point is to stop the agent while it can still do the work, not to grade it after it has left.

## What `run` actually records

The `run` action launches the declared argv without a shell and keeps completion status, exit code, actual test counts and a stdout hash. The command has to print one JSON object with integer `tests_passed` and `tests_failed`. The pilot's runner is short enough to show whole:

```python
#!/usr/bin/env python3
"""Run the actual offline hook-adapter suite and publish counts, never a claimed pass."""
import json
import sys
import unittest

sys.dont_write_bytecode = True
suite = unittest.defaultTestLoader.discover("tests/skill-gates", pattern="test_*.py")
result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
failed = len(result.failures) + len(result.errors)
print(json.dumps({"tests_passed": result.testsRun - failed - len(result.skipped), "tests_failed": failed}))
sys.exit(0 if result.wasSuccessful() and result.testsRun > 0 and not result.skipped else 1)
```

Three details matter. Skips are subtracted from the passed count. Any skip also makes the runner exit 1, so a skipped test fails the run outright. Zero tests run is a failure exit as well. `min_tests` is a floor the verifier checks against the measured passed count: 9 in this policy, against a suite that currently has 10 tests. Timeout, output overflow, nonzero exit, malformed counts and changed inputs never pass.

## Write order: revoke the old pass before the new run

The interesting code is not the checks. It is the order of writes around them. Here is the core of the `run` branch:

```python
if any(receipt["reads"].get(p) != current["inputs"][p] for p in policy["must_read"]):
    raise ValueError("read current required files before running checks")
receipt["report"] = None
# Clear prior success durably BEFORE launch: interruption cannot preserve an old pass.
receipt["commands"][args.item] = {"status": "running"}
atomic(state_path, state)
result = completed(command, current["tools"][args.item]["path"], root)
if gate.identity(root, policy, policy_hash, __file__) != current:
    result["status"] = "inputs_changed"
```

Three rules are encoded there. You cannot run before you have read the current bytes of the required files. A prior pass is wiped to disk before the new process starts, so killing the run mid-flight leaves "running", not the old success. And if any declared input changed while the tests ran, the result is marked `inputs_changed` instead of trusted.

One lookup in that excerpt needs a note. `current["inputs"]` is the digest map for every tracked file. The verifier builds it from `inputs`, `must_read` and any file named in a command's argv, which is why a `must_read` path can be looked up there.

The `report` action needed the same treatment, and the first version did not have it. A Greptile review finding pointed out that a failed rerun of `report` could leave the previous completed report in place. The fix revokes the old completion and writes that to disk first. The new report is set in memory right after, and written to disk only after the output row is built, printed and flushed (that later write is outside this excerpt):

```python
elif action == "report":
    # Revoke old completion before attempting serialization/output. A failed
    # rerun of report must not leave a prior completed report behind.
    receipt["report"] = None
    atomic(state_path, state)
    receipt["report"] = {"checklist": policy["checklist"], "identity_sha256": binding}
```

`test_failed_report_cannot_complete_gate_and_can_recover` pins the corrected behavior, and all 10 process-replay tests pass against it. The pattern generalizes: any step that records success should revoke the old success durably before it attempts the new one.

## Freshness, scope and state

Changing a declared input, the policy, the executable or the implementation invalidates old evidence. On the next `read` or `run`, the collector resets the receipt and every required action has to be repeated. The tracked set is `inputs`, `must_read` and files named in a command's argv. Anything else is outside the freshness guarantee, so the README tells you to list every relevant source, lockfile and configuration in `inputs`. Inputs must be regular workspace files of at most 1 MiB.

State lives under `~/.local/state/iep-skill-gates/<scope>/`, where scope binds workspace, policy path and session. Files are 0600, directories 0700, writes are locked and atomic. The log holds events, finding codes, mode and block decisions, and nothing else: no prompts, file bodies or command output. That makes it safe to keep and useless for reconstructing what the agent wrote, which is the intended trade.

## Observe first, then enforce

The gate shipped in observe mode, opt-in, as the committed default. In observe mode a Stop with missing evidence is logged with its findings but not blocked. Tool denial still applies.

Then came controlled sessions on Claude Code 2.1.332. The observation sessions produced two incomplete Stops and one clean Stop. The two incomplete ones are the useful part: one came from an incomplete provider checkout (the checkout that supplies the verifier), the other from Bash being withheld so the agent could not run the collector. Neither was the agent cutting corners. Both were the environment, which is what observe mode is for. In enforce mode, a Stop like the second one blocks a session that has no way to produce the evidence. The record does not itemize a fix for each cause. It does show a clean observe Stop and a complete run under enforce, so a working setup existed before enforce became the committed mode.

Observe mode cannot show a block, because it never blocks. So the qualification had a second half: controlled trials with the policy set to `enforce`, recorded as the evidence for the change that made enforce the committed mode. An ordinary complete invocation finished. An omission trial blocked a Stop, then recovered in the same session after real reads, a 10-test run and a report. Both halves are needed. A gate that blocks but cannot be satisfied in-session is a trap, and a gate that never blocks has not been shown to work. The promotion itself was small (+13/-7): the `mode` field, the README, a re-pin of the harness manifest (the hash list that pins reviewed files) and the rollback steps.

The README is specific about how to read the logs. Count evaluated `Stop` events as opportunities and those with findings as unmet opportunities. Count `begin` events (each start of a gated session) separately. Repeated stops in one scope are correlated observations, not independent samples. False blocks and missed violations need independent replay to label; the log cannot infer them.

Rollback is one field: set `mode` back to `observe`, run `pnpm run harness:init` then `pnpm run harness:verify`, review the policy and manifest entry together, and start a fresh session.

## What this does not prove

The limits are part of the result, so they stay in.

- `read` proves byte access, not understanding.
- The evidence is trusted local and unsigned. The same OS user can edit the state. This is not an execution attestation or a sandbox.
- `deny_tools` is a workflow deny list. Another tool can have equivalent capabilities.
- Interruptions may skip `Stop` entirely. Missing hook scripts or disabled hooks protect nothing.
- Repeated `Stop` requests stay blocked while evidence is incomplete, including when `stop_hook_active` is set, but the host controls the retry limit.
- The qualification covers one skill on one host version. A different task or host starts again in observe.
- The Python replay suite sits outside the repo's TypeScript coverage and calls no live model. The code change installs nothing globally and releases nothing.

For scale: the collector landed as +728/-5 across 17 files, with the full build passing 2,814 tests (one existing skip) across 183 files.

The code, the pilot skill and the README are at [examples/skill-gates](https://github.com/jeremylongshore/j-rig-skill-binary-eval/tree/main/examples/skill-gates).

## Use this

- Write a policy file for one skill with `must_read`, `must_run` (exact argv plus `min_tests`), `deny_tools` and `mode: "observe"`, and make the test runner print machine counts that subtract skips and fail on zero.
- In every step that records success, revoke the previous success to disk before launching the new attempt, and commit the new result only after its output is fully written.
- Explain every incomplete Stop seen in observe before going further. Then trial the policy with `enforce` in controlled sessions, and make it the committed mode only after one blocked Stop recovers in the same session.

## Frequently asked questions

### How do I stop Claude Code from claiming tests passed without running them?

The agent's word is not the check. Give the gate a policy file that lists the files the agent must read and the commands it must run, with a minimum test count on each command. The collector launches the declared command itself and records the counts, so a sentence typed by the agent cannot satisfy the check.

### Why is a skill's instruction to run tests not enough?

A skill's instructions are a request, not proof. Watching tool output still trusts a claim, and scanning the transcript afterward grades the agent after it has left. Evidence has to come from the collector's own run action, and the Stop is assessed while the agent can still do the work.

### What is the difference between observe mode and enforce mode?

In observe mode, a Stop with missing evidence is logged with its findings but not blocked. In enforce mode, the same Stop returns exit code 2, which tells Claude Code to refuse the stop. Tool denial applies in both modes. Make enforce the committed mode only after a controlled enforce trial shows a blocked Stop recovering in the same session.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do I stop Claude Code from claiming tests passed without running them?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The agent's word is not the check. Give the gate a policy file that lists the files the agent must read and the commands it must run, with a minimum test count on each command. The collector launches the declared command itself and records the counts, so a sentence typed by the agent cannot satisfy the check."
      }
    },
    {
      "@type": "Question",
      "name": "Why is a skill's instruction to run tests not enough?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A skill's instructions are a request, not proof. Watching tool output still trusts a claim, and scanning the transcript afterward grades the agent after it has left. Evidence has to come from the collector's own run action, and the Stop is assessed while the agent can still do the work."
      }
    },
    {
      "@type": "Question",
      "name": "What is the difference between observe mode and enforce mode?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "In observe mode, a Stop with missing evidence is logged with its findings but not blocked. In enforce mode, the same Stop returns exit code 2, which tells Claude Code to refuse the stop. Tool denial applies in both modes. Make enforce the committed mode only after a controlled enforce trial shows a blocked Stop recovering in the same session."
      }
    }
  ]
}
</script>

## Related Posts

- [A CRAP score gate that could pass on an empty measurement](https://startaitools.com/posts/crap-score-gate-prove-denominator/)
- [A green result only covers what it ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/)
- [Fixing Claude Code hooks: the new matcher format](https://startaitools.com/posts/fixing-claude-code-hooks-the-new-matcher-format/)
