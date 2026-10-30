---
name: j-rig
description: >-
  Inspect and use the J-Rig refiner CLI to bootstrap evaluation metadata, score
  a skill with an authorized provider, propose edits and inspect stored candidates.
  Use when improving an existing SKILL.md with evaluation evidence. Trigger with
  "refine this skill", "bootstrap an eval set" or "skill refiner status".
allowed-tools: Read, Write, Edit, Glob, Bash(j-rig:*), Bash(git:*), Bash(pnpm exec j-rig:*)
version: 0.2.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: Apache-2.0
compatibility: Designed for Claude Code; requires a separately installed compatible J-Rig CLI for refiner commands
argument-hint: '[refine bootstrap|score|propose|apply|status|render-report] <target>'
tags:
  - skill-refiner
  - eval-guided
  - skill-md
  - meta-tooling
  - hooks
---

# J-Rig Skill Refiner

## Overview

Use the existing refiner CLI to inspect a skill, generate a bounded edit proposal
and collect evaluation evidence. Distinguish a proposal, a stored candidate,
measured improvement and an approved source change. These are separate steps;
command success is not proof that a candidate improves behavior.

The bundled hooks are experimental integration code. They do not establish an
automatic quality gate. Read [the audited command and hook limits](references/command-and-hook-contract.md)
before relying on them or using a different CLI release.

## Prerequisites

- An existing skill directory containing `SKILL.md`, the requested operation and
  an agreed working directory for `.j-rig/refiner` artifacts.
- A separately installed compatible `@intentsolutions/jrig-cli`. Prefer an existing
  project-pinned installation; do not install or upgrade packages merely to inspect
  a skill. Use the resolved CLI version and its `refine --help` as evidence.
- For evaluation or proposal calls, an authorized provider/model, input-data scope,
  credential source and bounded spend/run scope. A present key is not authorization.
- For source changes, the project's review rules and actual promotion decision.

## Auth and data

`score` and `propose` can transmit skill or evaluation content to a provider and
incur charges. Use only the approved route and runtime secret source; never put a
key in a command example, report, committed file or terminal output. The audited
CLI supports multiple provider routes; Anthropic is not universally required.
Select provider and model explicitly rather than relying on whichever key happens
to be present. Respect existing evaluation wrappers and database boundaries;
refiner work must not write to a Freshie runtime database.

The offline commands also write local artifacts where indicated below. Use an
agreed scratch/project location and do not enable or invoke hooks as a side effect
of evaluating a skill. If provider authorization is missing, continue inspection or
requested offline preparation and leave provider-dependent steps pending.

## Instructions

1. Use Glob to find the selected skill and Read its content and evaluation spec.
   Record its source revision/hash, intended behavior and relevant constraints.
   Use Bash(git:\*) for authorized diff inspection, preserving unrelated work.
2. Inspect the installed CLI version and help using Bash(j-rig:_) or the
   project-pinned Bash(pnpm exec j-rig:_) launcher. The command table in the linked
   reference describes the audited versions, not every future release. Do not
   silently change tools or route through a global CLI with a different version.
3. For requested offline preparation, bootstrap metadata or inspect status in the
   selected working directory. Record the actual stored object addresses and
   source hashes; a generated eval-set label does not prove independent held-out
   cases were executed.
4. When evaluation is authorized, establish the baseline with the actual approved
   eval spec, runner, model/provider and input hashes. Preserve case-level outcomes
   and failures. Check the selected runner's binding to the intended eval inputs;
   the audited refiner score adapter does not itself forward eval-set items.
5. When proposal generation is authorized, request a bounded candidate and inspect
   its operations and parent hash. In the audited CLI, `propose` stores an edit
   proposal without shadow scoring. Do not label it accepted or non-regressing
   merely because the command succeeded.
6. If candidate materialization is requested, `apply` stores a candidate version;
   inspect its output. It does not by itself rewrite `SKILL.md` or move the best
   pointer in the audited version. Review any candidate in an isolated copy and
   evaluate it under the same frozen case and runner conditions as the baseline.
7. Compare actual per-case outcomes and aggregate results against the agreed
   acceptance rule. An aggregate increase alone does not prove no case regressed.
   Report missing evidence or runner failures rather than inventing a verdict.
8. After the user's source-change decision or prior delegated authority, use Edit
   or Write to apply the selected text to the selected skill, preserve metadata and
   review the diff. Follow normal validation and PR rules. Do not invent a
   `promote` CLI verb, hand-edit a best pointer or claim a signed report from a
   rendering command.

## Output

Report the requested operation and its observed result, including:

- Exact CLI/refiner versions, skill source/hash and artifact working directory.
- Proposal store address, candidate/source hashes and actual files changed.
- Actual eval-spec, provider/model and case results when evaluation ran.
- Baseline/candidate comparison, uncertainty and approval/promotion status.
- Skipped stages and the specific missing input or authorization.

The refiner store and log live beneath `.j-rig/refiner` in the working directory.
Keep their input content and credentials within the agreed data scope. A rendered
Markdown/HTML report is presentation, not a cryptographic signature or proof of
improvement. Do not publish artifacts unless that action is authorized.

## Error Handling

| Situation                                 | Recovery                                                                                              |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| CLI absent or incompatible                | Report the available version and missing command; do not install or upgrade automatically.            |
| Provider authorization or key unavailable | Leave score/propose pending and continue requested offline inspection.                                |
| Proposal parent or anchor does not match  | Inspect source drift and regenerate/review within authorization; do not force the edit.               |
| Stored object cannot be found             | Check the working directory and full store address; do not substitute a text hash or truncated label. |
| Score lacks runner/case binding           | Mark comparison inconclusive and inspect actual spec/invocation before claiming held-out success.     |
| Hook logs a capture or advisory message   | Report the actual hook limit; do not infer a scored rollout, paid run success or blocked commit.      |

## Examples

**Inspect an existing setup:** use the project's resolved launcher, for example:

```bash
pnpm exec j-rig --version
pnpm exec j-rig refine --help
pnpm exec j-rig refine status my-skill --json
```

**Requested offline preparation:** from the agreed artifact working directory:

```bash
j-rig refine bootstrap /path/to/my-skill --json
```

Record the generated metadata and its limits; this command is not a behavioral run.

**Authorized proposal:** after an approved provider/model/data/spend scope exists:

```text
j-rig refine propose /path/to/my-skill --provider <approved-provider> --model <approved-model> --json
j-rig refine apply /path/to/my-skill --proposal <full-store-address> --json
```

Inspect the stored candidate and gather authorized baseline/candidate evidence.
Do not redirect the complete JSON result into `SKILL.md` or treat `apply` as promotion.

## Resources

- [Version-bound commands, store hashes and actual hook behavior](references/command-and-hook-contract.md)
- [J-Rig CLI package](https://www.npmjs.com/package/@intentsolutions/jrig-cli)
- [Refiner package](https://www.npmjs.com/package/@intentsolutions/refiner)
- [Canonical source repository](https://github.com/jeremylongshore/j-rig-skill-binary-eval)
