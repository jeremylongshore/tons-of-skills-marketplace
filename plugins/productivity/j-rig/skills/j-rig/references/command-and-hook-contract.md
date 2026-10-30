# Audited refiner command and hook contract

## Evidence scope

Audited 2026-10-25 from this marketplace's installed, lockfile-selected
`@intentsolutions/jrig-cli@0.3.0` and `@intentsolutions/refiner@0.4.0` distribution
code. This is source inspection, not a provider run, behavioral acceptance test or
assessment of every published version. npm metadata also reported latest 0.5.0;
that release was not installed or audited here. Inspect the chosen release before
assuming these contracts apply to it.

| Audited distribution file    | SHA-256                                                            |
| ---------------------------- | ------------------------------------------------------------------ |
| jrig-cli 0.3.0 dist/index.js | `2d85bc3a317c65b41701d6b23ed60b84c900a1770fe79ded5b2c3995d84627a8` |
| refiner 0.4.0 dist/index.js  | `f2955211e59f6bd962f4df39ff41c38d39dde7ba6844ac4b04d526b367a17584` |

The registered `refine` command group is real. This plugin supplies a skill and
hooks, not separate wrapper commands implementing additional verbs.

## Commands in the audited version

| Command                                                   | Actual side effect and limit                                                                                                                  |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `refine bootstrap <skill-dir>`                            | Deterministically reads the skill and stores skill/eval metadata; no executed held-out result.                                                |
| `refine score <skill-dir>`                                | Delegates to `j-rig eval` and stores an aggregate score record; provider-backed and potentially billable.                                     |
| `refine propose <skill-dir>`                              | Calls the selected model and stores an edit proposal. No baseline/candidate scoring or acceptance gate is called here.                        |
| `refine apply <skill-dir> --proposal <hash>`              | Applies operations to an in-memory document and stores the candidate. Does not write the skill file or call the best-pointer setter.          |
| `refine status <skill-id>`                                | Reads the store/log and current best pointer. Some stored-event output is not filtered to that skill; inspect hashes and content for lineage. |
| `refine render-report <report.md> --output <report.html>` | Parses the required report format and renders HTML; does not sign or establish the truth of a report's verdict.                               |

There is no registered `refine promote` verb. A library best-pointer method exists,
but the listed `apply` handler does not call it. Do not invent a CLI promotion step
or manipulate pointers merely to make status look complete.

## Evaluation and address binding

The score adapter invokes `j-rig eval <skill-dir> --json --models <model>` and adds
an explicit provider when selected. It associates an eval-set hash with the stored
score record, but does not forward the generated eval-set items to that subprocess.
Inspect the actual evaluator spec and invocation; the metadata hash alone cannot
prove which cases ran. The aggregate pass rate also does not prove per-case
non-regression, independence, or a statistically established improvement.

The store address is a hash over the stored value object. A document's own text
hash is a different identifier. Use full store addresses for proposal lookup;
inspect the stored object and parent text hash rather than assuming a printed,
truncated or embedded hash is interchangeable.

`apply --json` returns an object containing the candidate text and a store hash.
It does not return a plain Markdown file. A source revision is a separate,
authorized edit followed by the project's validation and review process.

## Bundled hooks as shipped

| Hook                     | Actual behavior and limits                                                                                                                                                                                                                                                                             |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| L1 sinker, PostToolUse   | Looks for a SKILL.md edit, tries the working-directory validator, otherwise prints guidance; exits zero. It is advisory and is not a skill effectiveness test.                                                                                                                                         |
| L2 line, Stop            | Reads custom `skill_id`/`last_skill` fields, appends capture records and counts them. At a threshold it can launch a detached `j-rig refine propose ... --model sonnet` if the CLI is available. It does not inspect scored-rollout evidence, pass an explicit provider or inspect background success. |
| L3 hook, PreToolUse Bash | Detects some git commit/push strings and staged SKILL.md paths, rate-limits advisories and inspects status when possible. The agentic blocking implementation is a commented stub; the script never executes an exit-two regression block.                                                             |

L2 capture records are not scored rollouts; a threshold message is not a successful
refiner pass. Provider/model auto-selection and background spend must not be
assumed authorized. These scripts are preserved by this documentation repair;
reliable rollout capture, explicit authorization, concurrency and a real blocking
gate require separate runtime work and review. Do not enable or exercise the hooks
as a side effect of following this skill.

## Source references

- [CLI 0.3.0 package](https://www.npmjs.com/package/@intentsolutions/jrig-cli/v/0.3.0)
- [Refiner 0.4.0 package](https://www.npmjs.com/package/@intentsolutions/refiner/v/0.4.0)
- [Canonical refiner source](https://github.com/jeremylongshore/j-rig-skill-binary-eval/tree/main/packages/refiner)
- Bundled `hooks/sinker.sh`, `hooks/line.sh`, `hooks/hook.sh` and `hooks/hooks.json`
  are the authority for this plugin's hook behavior; their descriptions do not add
  runtime enforcement that the scripts do not implement.
