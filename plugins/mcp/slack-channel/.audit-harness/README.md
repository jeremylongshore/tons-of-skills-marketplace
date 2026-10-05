# @intentsolutions/audit-harness

[![npm](https://img.shields.io/npm/v/@intentsolutions/audit-harness?color=cb3837&logo=npm)](https://www.npmjs.com/package/@intentsolutions/audit-harness)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Provenance](https://img.shields.io/badge/sigstore-provenance-066da5)](https://www.npmjs.com/package/@intentsolutions/audit-harness)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U5S225PTME)

Part of the **[Intent Eval Platform](https://github.com/intent-solutions-io/intent-eval-platform)** — the umbrella grouping the platform's six repos: five converge via a shared Evidence Bundle schema (`intent-eval-core`, `intent-eval-lab`, `audit-harness`, `j-rig-skill-binary-eval`, `intent-rollout-gate`), plus `intent-eval-dashboard` as a satellite consumer (not part of the convergence taxonomy).

Deterministic test-enforcement toolkit. Companion to the `audit-tests` and `implement-tests` Claude Code skills — but usable standalone in any repo that wants hash-pinned, escape-scanned, AI-resistant quality gates.

**On "AI-resistant", precisely:** the hash-pin is a *complete* guarantee for the files you pin — they cannot change without an explicit, committed re-pin. The escape-scan is a *heuristic net* over the staged diff: it catches the common escapes (deleted tests, lowered coverage floors, new skip markers, architecture-rule bypasses), not every conceivable dodge. Deliberately not claiming bulletproof.

## What it is

A small CLI dispatching 17 released deterministic commands (shell + stdlib-Python scripts) — an 18th, `audit-harness migration-notes`, is on disk and staged for the next release (see CHANGELOG `[Unreleased]`):

| Command | Purpose |
|---|---|
| `audit-harness verify` | Verify hash-pinned artifacts haven't changed since `--init` |
| `audit-harness init` | Pin the current state of engineer-owned policy files |
| `audit-harness list` | Show pinned files |
| `audit-harness escape-scan --staged` | Detect AI attempts to lower test thresholds, delete tests, bypass architecture rules |
| `audit-harness cred-gate` | Provider-credential PASS/FAIL gate — FAIL if a declared secret, provider-key shape, or serialized env leaks into the artifact about to be signed |
| `audit-harness arch` | Run language-appropriate architecture-rule checker (dependency-cruiser / import-linter / ArchUnit / deptrac / arch-go) |
| `audit-harness bias` | Count common test-bias patterns |
| `audit-harness gherkin-lint` | Advisory Gherkin quality check |
| `audit-harness crap` | CRAP (Complexity × Coverage) scorer — Python, Go, JS/TS, Rust |
| `audit-harness emit-evidence` | Wrap a gate-result JSON envelope in an in-toto Statement v1 (predicate `gate-result/v1`) |
| `audit-harness classify` | Read-only repo classifier → an `audit-profile/v1` value (never writes) |
| `audit-harness conform` | Read-only conformance gate-runner → `gate-result/v1` rows against bundled content-addressed schemas |
| `audit-harness audit` | Read-only testing-depth gate-runner → coverage presence per pyramid layer + crap-score |
| `audit-harness scan` | Read-only security/hygiene/skill-quality gate-runner (gitleaks / osv-scanner / Semgrep / syft / markdownlint / lychee) |
| `audit-harness fp-rate` | Measure each gate's false-positive / false-negative rate over a labeled corpus |
| `audit-harness currency` | Advisory poll-freshness report over the per-upstream pin relation |
| `audit-harness gen-layer-applicability` | Project the canonical audit-profile registry into `layer-applicability.md` |

## Install

Pick the install flavor that matches your repo's ecosystem — all three publish the same CLI surface.

**Node / JS / TS** (from npm):

```bash
pnpm add -D @intentsolutions/audit-harness
# or: npm install --save-dev @intentsolutions/audit-harness
# or: yarn add --dev @intentsolutions/audit-harness
```

**Python** (from PyPI):

```bash
pip install intent-audit-harness
# or inside a project venv:
python -m pip install intent-audit-harness
```

**Rust** (from crates.io):

```bash
cargo install intent-audit-harness
```

**Any other language** (Go, Ruby, PHP, Java, .NET, shell, etc.) — vendor the scripts:

```bash
curl -sSL https://raw.githubusercontent.com/jeremylongshore/intent-audit-harness/main/install.sh | bash
```

## Quick usage

### Pre-commit hook (`.husky/pre-commit`)

```bash
#!/usr/bin/env sh
pnpm exec audit-harness escape-scan --staged
pnpm exec audit-harness verify
```

### CI workflow (`.github/workflows/ci.yml`)

```yaml
  containment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: pnpm/action-setup@v5
      - uses: actions/setup-node@v6
        with: { node-version: '20', cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec audit-harness verify
      - run: pnpm exec audit-harness escape-scan --range origin/main..HEAD
```

### Engineer workflow — change a policy threshold

```bash
# 1. Edit tests/TESTING.md to change coverage.line from 80 to 75
# 2. Re-init to accept the change
pnpm exec audit-harness init
# 3. Commit the updated manifest alongside the policy change
git add tests/TESTING.md .harness-hash
git commit -m "chore(test): lower coverage floor to 75"
```

## The containment model

The harness enforces this rule: **policy changes must be conscious, not silent.**

Engineer-owned files (`tests/TESTING.md`, package test scripts, CI workflows,
coverage and mutation configs, acceptance features, and architecture rules) are
hashed into a manifest. Any diff that changes their content without a fresh
`audit-harness init` is caught by pre-commit / CI and **REFUSED**. Ordinary
application source is deliberately outside this denominator.

AI agents remain useful (they can read policy, they can implement within constraints). What they can't do is silently weaken the constraints. That's the entire design.

The same walls can close the loop **before a push leaves the machine**:
`audit-harness worktree-run --pre-push` checks the exact ref being pushed in a
disposable `git worktree` — `verify` + `escape-scan` on the push range stay
fail-closed, `conform` + `audit` contribute advisory gate-result/v1 rows — then
removes the worktree. It has no push authority, no LLM stage, and never writes
to the repo. Wire it as a lefthook `pre-push` job (this repo's `lefthook.yml`
is the reference) so CI becomes confirmation instead of discovery.

See `audit-tests/references/philosophy.md` in the companion skill for the full rationale.

## The 7-layer testing taxonomy

This harness sits inside a larger framework:

```text
L7  Acceptance / RTM / Personas / Journeys     ← WHAT are we proving?
L6  E2E / BDD / Visual regression              ← User-level guarantees
L5  Perf / Security (SAST/DAST) / A11y / Chaos ← Non-functional
L4  Integration / Contract / Migration         ← Infrastructure wiring
L3  Unit + Coverage + Mutation + Arch + CRAP   ← Code-level correctness  ← audit-harness lives here
L2  Static analysis / Lint / Types / Secrets   ← Read-only scanning
L1  Git hooks / CI enforcement                 ← The cheapest gate       ← audit-harness enables this
```

The harness commands serve L1 (escape-scan in pre-commit + CI) and L3 (CRAP, architecture, bias, hash-pin).

## Exit codes

Important for CI scripting:

| Exit | Command | Meaning |
|---|---|---|
| 0 | any | Clean |
| 1 | escape-scan | CHALLENGE — requires engineer-approved comment |
| 2 | verify | `HARNESS_TAMPERED` — pinned file changed |
| 2 | escape-scan | REFUSE — pipeline halted |
| 3 | verify | No manifest (fresh repo, not an error) |

## Language support

Most scripts are language-agnostic (shell + regex). CRAP has per-language backends:

| Language | CRAP | Arch | Notes |
|---|---|---|---|
| Python | radon + coverage.py | import-linter | full support |
| JS/TS | complexity-report + c8 | dependency-cruiser | full support |
| Go | gocyclo + go test -cover | arch-go | full support |
| Rust | rust-code-analysis + tarpaulin | (custom) | coverage integration pending |
| Java/Kotlin | — | ArchUnit | via language-native tooling |
| .NET | — | ArchUnitNET | via language-native tooling |
| PHP | — | deptrac | via language-native tooling |

## License

Apache 2.0 — see [LICENSE](./LICENSE) and [NOTICE](./NOTICE).

**Note:** versions `0.x` shipped under the MIT license. Starting with `v1.0.0`, the project is licensed under Apache 2.0. Existing `0.x` releases on npm remain available under their original MIT terms; new releases (`>= 1.0.0`) are Apache 2.0.

## Related

- [`audit-tests` Claude Code skill](https://github.com/jeremylongshore/intent-audit-harness#related) — diagnostic pipeline that uses this harness
- [`implement-tests` Claude Code skill](https://github.com/jeremylongshore/intent-audit-harness#related) — filesystem-mutating installer that installs this harness as part of L1/L3 setup

## Versioning

SemVer. Breaking changes to the CLI surface bump major; new commands bump minor; bug fixes bump patch.

## Contributing

This is infrastructure code. Changes need to be conservative. Before opening a PR:

1. Read `audit-tests/references/philosophy.md` (in the companion skill) to understand the escape-grammar design
2. Run `bash scripts/escape-scan.sh --staged` on your own diff — yes, the harness tests itself
3. Add test cases if you're adding a new pattern to escape-scan or a new command to the CLI
