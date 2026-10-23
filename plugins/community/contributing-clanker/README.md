# contributing-clanker

> Portable, least-authority workflow for respectful AI-assisted OSS contributions.

`contributing-clanker` helps contributors check upstream policy, avoid duplicate
work, prepare evidence, and publish only what a human has reviewed. It is
model-agnostic: Claude-specific helper agents are optional adapters, not runtime
requirements.

## Trust model at a glance

The plugin exposes three separately invoked skills:

| Skill | Default authority | What it can do |
|---|---|---|
| `contribute` | Read-only | Audit issues, pull requests, policies, and readiness |
| `contribute-prepare` | Local writes | Create explicitly scoped state/worktrees, drafts, tests, and gate evidence |
| `contribute-publish` | Reviewed GitHub write | Perform one exact action after fresh human approval |

Installing the plugin creates no state, clones, hooks, credentials, background
jobs, or GitHub objects. Invoking `contribute` also performs no writes.

## Distribution boundary

The canonical source for the public package is this tracked marketplace
directory. A maintainer's personal checkout, installed-skill symlink, and
`CONTRIBUTE_STATE_DIR` are private runtime inputs, not publication sources.

- Do not mirror or bulk-copy a personal `contributing-clanker` checkout into
  this directory.
- Do not package candidate records, dossiers, logs, credentials, worktrees, or
  user-authored gates.
- Do not add install/uninstall hooks that create, migrate, or synchronize local
  state.
- Port changes deliberately, review the marketplace diff, and run the
  portability regression tests before publication.

Catalog and website projections are generated only from this tracked directory.
They do not read the maintainer's home directory or configured runtime state.

## Thirty-second start

Start with the safe audit:

```text
/contribute qualify owner/repository#123
```

The result is `ready-to-prepare`, `needs-information`, `wait`, or `skip`, with
evidence and the next safe action.

If preparation is appropriate, choose two absolute paths inside your own
profile or workspace and initialize them explicitly:

```bash
export CONTRIBUTE_STATE_DIR=/your/profile/state/contributing-clanker
export CONTRIBUTE_WORKSPACE_DIR=/your/profile/worktrees/contributions

bash <contribute-prepare-skill-dir>/scripts/setup.sh \
  --state-dir "$CONTRIBUTE_STATE_DIR" \
  --workspace-dir "$CONTRIBUTE_WORKSPACE_DIR"
```

Then invoke `contribute-prepare`. It produces a review packet and states that no
external action occurred. Invoke `contribute-publish` separately only when you
want to review and approve a specific GitHub action.

## Why the split exists

Community skill installers should not inherit another operator's home layout,
persistent state, agents, credentials, or approval identity. The split makes the
authority boundary visible and enforceable:

- audit works without persistent state;
- preparation has no default paths and no GitHub mutation authority;
- publication cannot install dependencies or write local tracking state;
- authentication proves identity but never substitutes for approval; and
- repository instruction files apply only inside that repository.

The design responds directly to the Hermes interoperability report in
[issue #1321](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1321).

## Local preparation model

After explicit setup, the chosen state directory contains:

```text
candidates/   Markdown records for selected issues
research/     Cached repository-policy dossiers
user-gates/   Optional user-authored deterministic gates
check-runs/   Gate evidence
test-logs/    Local test output
profile.md    User-selected languages and constraints
log.jsonl     Append-only local workflow events
```

The chosen workspace directory contains only repositories the user explicitly
selected. Bundled gates are read from the installed skill package; they are not
copied into a hidden home directory.

## Publication boundary

Before any comment, issue, branch push, or pull request, `contribute-publish`
must show:

- exact repository and target;
- complete content or refspec;
- commit SHA and changed files;
- tests, linters, and gate evidence; and
- CLA/DCO, AI disclosure, warnings, and overrides.

Fresh approval applies to that exact action only. The skill does not merge,
force-push, approve reviews, bypass repository rules, or delete branches without
a separate explicit review and approval.

## Requirements

- `git`
- `jq`
- GitHub CLI (`gh`) authenticated through the user's normal credential store
- Bash and Python 3 (standard library only) for the optional deterministic
  preparation scripts
- the target repository's own build/test dependencies, only when preparation is
  explicitly requested

No token value should be placed in plugin state or prompts.

## Verification

From the marketplace repository:

```bash
python3 scripts/validate-skills-schema.py --marketplace \
  plugins/community/contributing-clanker

python3 scripts/validate-unicode-hygiene.py \
  plugins/community/contributing-clanker/skills/contribute/SKILL.md \
  plugins/community/contributing-clanker/skills/contribute-prepare/SKILL.md \
  plugins/community/contributing-clanker/skills/contribute-publish/SKILL.md
```

The preparation runtime includes focused shell regression tests under
`skills/contribute-prepare/scripts/test-*.sh`. Dossier preservation has an offline
regression suite: `python3 -m unittest tests.test_researcher_refresh -v`.

Dossier refresh preserves the exact `Pet peeves & known triggers`, `Failure log`,
and `Notes` section bodies, including subheadings and fenced examples. Run the
builder directly; use `--stdout` for a merged preview, never a redirect over the
existing dossier. Ambiguous manual sections refuse refresh. Publication is
atomic and retains existing permission bits; new dossiers start with mode 0600.
Coordinate concurrent editors because the
final change check and replacement are separate operations. Ownership and
extended filesystem metadata are not retained by replacement.

## Compatibility

The core contract is host-neutral. Hosts may load the optional definitions in
`contribute-prepare/agents/`, or perform those bounded roles inline. No
Claude-specific command, path, memory store, or subagent is required.

## License

MIT. Public package source:
https://github.com/jeremylongshore/tons-of-skills-marketplace/tree/main/plugins/community/contributing-clanker
