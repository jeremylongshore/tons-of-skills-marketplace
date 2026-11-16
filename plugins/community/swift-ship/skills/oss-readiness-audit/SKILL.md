---
name: oss-readiness-audit
description: Systematic pre-publish audit for a project about to go public on GitHub (open source release or portfolio piece). Use when a repo is about to get its first commit/push, or when the user says things like "ready to publish", "open source my project", "push to GitHub first time", "portfolio repo review", "is this repo ready for GitHub", "can I make this public", or asks to check for secrets/leftover artifacts before sharing a repo. Walks a checklist covering git repo scope, .gitignore coverage, secrets/PII sweep, LICENSE, README completeness, misleading naming, internal process docs, doc consistency, and CI — gathering evidence with shell commands and producing a blocker/recommended/nice-to-have report. Language-agnostic across Swift, Node, Python, Rust, Go, etc. Trigger with "/oss-readiness-audit".
allowed-tools: Read, Glob, Grep, Bash(git:*), Bash(grep:*), Bash(find:*), Bash(du:*), Bash(file:*)
version: 1.0.0
author: chsistrying
license: MIT
compatibility: Language-agnostic; requires git and standard Unix shell tools
tags: [open-source, audit, security, github]
---

# OSS Readiness Audit

## Overview

A pre-publish checklist for a repo that is about to become public on GitHub. Run every
check below, gather the evidence with the given commands, then produce the report in
the template at the end.

## Prerequisites

- `git` plus standard Unix shell tools (`grep`, `find`, `du`) — nothing
  language-specific; the checks work the same on Swift, Node, Python, Rust, or Go
  projects.
- Read access to the full project tree, including dotfiles.

**Golden rule: fix every BLOCKER before the first commit, not after.** Once a commit
lands, its content lives in `.git` history forever — even if a later commit deletes it,
anyone who clones the repo can still recover the old blob. A `.gitignore` added after
the fact does not retroactively remove already-tracked files, and history rewrites
(`git filter-repo`, BFG, `reset --hard` + fresh init) are only cheap and safe while the
repo has never been pushed. So: run this audit, fix blockers, THEN `git init` /
first commit, THEN push.

If the repo already has commits and/or has already been pushed, say so explicitly in
the report — the remediation for a blocker changes from "fix before committing" to
"history surgery required, and rotate any leaked secret immediately."

---

## How to use

1. Confirm the project root directory with the user if it's ambiguous.
2. Go through items 1–10 in order. For each: run the commands, note pass/fail, and
   collect the evidence (file paths, byte counts, match counts) you'll need for the
   report.
3. Item 1 gates everything else — if the repo scope is wrong, stop and flag it before
   doing anything that touches git (no `git add`, no `git commit`).
4. Produce the final report using the template at the bottom. Do not silently fix
   things — list findings and proposed remediations, then act only once the user
   agrees (unless they've asked you to just fix everything you find).

---

## BLOCKERS

### 1. Git repo scope

The real incident this item is derived from: a project directory sat *inside* a git
repo whose root was the user's home directory. Had `git add -A && git push` been run
from the project directory, the entire home folder — every other project, dotfiles,
caches — would have been staged and could have been pushed to a public remote.

Commands:
```bash
git rev-parse --show-toplevel      # where does git think the repo root is?
pwd                                  # where is the project actually?
git rev-parse --is-inside-work-tree  # sanity check you're in a repo at all
```

- **Pass**: `--show-toplevel` output equals the project directory (or a directory that
  legitimately IS the whole project, e.g. a monorepo where this is intentional).
- **Fail**: `--show-toplevel` resolves to a parent directory — home directory, a
  directory with sibling unrelated projects, `Desktop`, `Documents`, etc.

If there are zero commits yet (fresh `git init` scenario), still check what a first
`git add -A` would sweep in before running it for real:
```bash
git add -n -A | head -100          # dry run: lists what WOULD be staged
git add -n -A | wc -l              # how many files total
```
Scan that list for anything outside the project's own tree (other project folders,
`.ssh`, `.aws`, `.env` files belonging to unrelated tools, etc).

**Remediation**: If the toplevel is wrong, do not commit or push from here. Either
(a) run a fresh `git init` inside the actual project directory so it becomes its own
repo root, or (b) if a repo with unwanted scope already has commits, treat this as
sensitive — do not push it; create a clean repo scoped correctly and copy only the
project's files in.

---

### 2. `.gitignore` before the first commit

Commands:
```bash
test -f .gitignore && echo "exists" || echo "MISSING"
cat .gitignore 2>/dev/null

# Find heavy/generated directories anywhere in the tree (examples — not exhaustive,
# adapt to the project's actual toolchain):
#   .build/, DerivedData/           -> Swift/Xcode
#   node_modules/, dist/, .next/    -> JS/TS
#   __pycache__/, .venv/, venv/     -> Python
#   target/                          -> Rust / Java(Maven)
#   bin/, obj/                       -> .NET
#   .DS_Store, Thumbs.db             -> OS junk
#   .idea/, .vscode/, *.iml          -> IDE junk
find . -maxdepth 4 \( -name .build -o -name DerivedData -o -name node_modules \
  -o -name dist -o -name .next -o -name __pycache__ -o -name .venv -o -name venv \
  -o -name target -o -name .DS_Store -o -name .idea \) -print

# Measure the damage — size of everything that WOULD be swept in without a gitignore:
du -sh .build node_modules dist DerivedData __pycache__ .venv target 2>/dev/null
```

- **Pass**: `.gitignore` exists and is in place before the first commit; none of the
  generated/artifact directories show up in `git status` or `git ls-files`.
- **Fail**: any build artifact, dependency directory, or OS/IDE junk file is untracked-
  but-about-to-be-added, or (worse) already tracked.

Report the size found via `du -sh` as "N MB at risk of being committed."

If already committed:
```bash
git ls-files | grep -E '\.build/|node_modules/|dist/|DerivedData/|__pycache__/|/target/|\.DS_Store'
```
Any hits mean artifacts are already tracked — `git rm -r --cached <path>` plus adding
the ignore rule, and if unpushed, folding that into history cleanup rather than a
visible "remove build artifacts" commit is preferable (but not essential — this isn't
a secret, just noise).

**Remediation**: Write a `.gitignore` scoped to the project's actual language/toolchain
(use github/gitignore templates as a starting point, don't cargo-cult irrelevant
entries), add it, confirm the artifact directories no longer appear in
`git status --porcelain`, then commit.

---

### 3. Secrets / personal info sweep

Commands (run over the working tree; run again over git history if the repo already
has commits):
```bash
# Common secret shapes
grep -RInE "sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|xox[baprs]-[0-9A-Za-z-]+" \
  --exclude-dir={.git,node_modules,.build,dist,DerivedData,venv,.venv} .

# Generic key/token/password/secret assignments
grep -RInE "(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9/+_.=-]{12,}" \
  --exclude-dir={.git,node_modules,.build,dist,DerivedData,venv,.venv} .

# Absolute personal paths that shouldn't ship in code/docs
grep -RInE "/Users/[A-Za-z0-9_.-]+" --exclude-dir={.git,node_modules,.build,dist} .

# Personal email addresses
grep -RInE "[A-Za-z0-9._%+-]+@(gmail|yahoo|icloud|outlook|hotmail)\.com" \
  --exclude-dir={.git,node_modules,.build,dist} .

# .env or credential files that shouldn't be tracked
find . -maxdepth 4 \( -name ".env" -o -name ".env.*" ! -name "*.env.example" \
  -o -name "*.pem" -o -name "*credentials*" \) -not -path "*/node_modules/*"

# If commits already exist, also check history — a deleted secret still lives in
# earlier commits:
git log -p | grep -nE "sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}" | head
```

- **Pass**: no real secrets, no `.env` (only `.env.example`), no personal absolute
  paths or personal emails in code/docs/comments.
- **Fail**: any hit that is a real credential, a real personal path, or a real email —
  use judgment on false positives (e.g. `/Users/username` in a code *comment example*
  vs. a hardcoded path a build script actually uses).

**Remediation**: Delete/replace secrets, **rotate any real key that was ever
committed** (assume it's compromised even if unpushed but especially if pushed),
add `.env` (real) to `.gitignore` and keep `.env.example` with placeholder values,
replace absolute personal paths with relative paths or environment variables. If a
secret is already in history and the repo has been pushed, this is urgent: rotate the
credential first, then scrub history with `git filter-repo` or the BFG Repo-Cleaner.

---

### 4. LICENSE present and filled in

Commands:
```bash
ls LICENSE LICENSE.md LICENSE.txt 2>/dev/null
grep -iE "copyright|\(c\)" LICENSE* 2>/dev/null
```

- **Pass**: a LICENSE file exists, matches an intentional choice (MIT/Apache-2.0/etc),
  and the copyright line has a real name and real year — not a template placeholder
  like `[year] [fullname]` or `<name>`.
- **Fail**: no LICENSE file, or one present but still reading `[fullname]`/`[year]`.

**Remediation**: Pick a license (choosealicense.com, or `gh api
licenses/<key>` for the canonical text), fill in `Copyright (c) <year> <Full Name>`,
commit at repo root as `LICENSE`.

---

### 5. README lets a stranger build and run it

Commands:
```bash
test -f README.md && wc -l README.md
grep -inE "^#+ *(install|setup|prerequisite|requirement|build|usage|getting started|run|quick ?start)" README.md
grep -inE "\`\`\`" README.md | wc -l        # are there any fenced code/command blocks?
grep -inE "!\[.*\]\(.*\.(png|jpg|jpeg|gif|webm|mp4)\)" README.md   # screenshots/demo media
```

- **Pass**: README states prerequisites (language/runtime version, package manager,
  OS constraints), gives copy-pasteable install/build/run commands, and — if the
  project has a GUI or visible output — includes at least one screenshot or short
  clip/gif.
- **Fail**: README is a title + one paragraph with no runnable commands; a stranger
  cloning the repo cold would not know what to type.

**Remediation**: Add explicit, copy-pasteable command blocks for install/build/run,
state exact prerequisite versions, add screenshots (drag into the repo under
`docs/` or `assets/` and reference with relative paths) for anything with a UI.

---

## HIGH PRIORITY

### 6. Misleading leftover naming

Reviewers judge a codebase by the names in it. A file/class called `Placeholder`,
`Stub`, `WIP`, `TODO`, `Dummy`, `Temp` that turns out to be real, load-bearing
production code reads as either unfinished or dishonest.

Commands:
```bash
grep -RIlnE "Placeholder|Stub|WIP|Dummy|TempImpl" \
  --include=*.{swift,ts,tsx,js,jsx,py,go,rs,java,kt,cs} \
  --exclude-dir={.git,node_modules,.build,dist,DerivedData} .

grep -RInE "TODO|FIXME|XXX" \
  --include=*.{swift,ts,tsx,js,jsx,py,go,rs,java,kt,cs} \
  --exclude-dir={.git,node_modules,.build,dist,DerivedData} . | wc -l
```
For each hit, check whether the file/symbol is actually wired into the real code path
(not itself dead) — if so, it's misleadingly named, not actually a stub.

Also look for dead code kept alive only by its own tests (nothing in the shipping
product calls it): for a given symbol, grep its usages and check whether every
reference outside its own definition is inside a `test`/`Tests`/`spec` path.

- **Pass**: names reflect what the code actually does; no dead code whose only
  "user" is its own test file.
- **Fail**: real, in-use code named like a stub/placeholder; test-only dead code left
  in the shipping source tree.

**Remediation**: Rename to describe actual behavior; delete dead code (tests included)
or move genuinely experimental code behind a clearly-labeled `experimental/` path.

---

### 7. Internal process docs shouldn't be the README's front page

If the README's top sections are AI-agent prompts, orchestration notes, or "here's
how I directed Claude/Copilot to build this" narration rather than what the tool
does and how to use it, that's a bad first impression for anyone landing on the repo.

Commands:
```bash
head -100 README.md | grep -inE "prompt|orchestrat|agent instructions|system prompt|multi-agent|copilot instructions|claude code"
```

- **Pass**: README opens with what the project is, what it does, and how to install/
  run it. Any "how this was built with AI assistance" content is a short note, or
  lives in an appendix/closing section, or in `docs/development-process.md`
  linked from the bottom of the README.
- **Fail**: the first thing a visitor sees is prompt engineering / agent orchestration
  detail instead of the product.

**Remediation**: Move that content to the end of the README under a heading like
"Development Process" / "Built with AI Assistance", or out to its own doc, and lead
with user-facing content instead.

---

### 8. Docs consistency

Commands:
```bash
find . -maxdepth 3 -iname "*audit*" -o -iname "*status*" -o -iname "*report*" -o -iname "*summary*"
grep -RInE "[0-9]+ (tests?|files?|modules?|endpoints?)" --include=*.md .
```
Compare any counts/status claims (test counts, feature lists, "N modules complete")
across README, CONTRIBUTING, and any status/audit docs found above — flag
contradictions.

- **Pass**: no conflicting numbers/claims between docs; any point-in-time snapshot
  doc (an old audit, a dated status report) is clearly marked with its date and
  something like "Snapshot as of <date> — may not reflect current state."
- **Fail**: two docs claim different test counts or feature completeness with no
  explanation; a stale audit/status doc reads as if it's current.

**Remediation**: Reconcile the numbers, or delete/archive stale docs under
`docs/archive/`, and stamp any necessarily-historical doc with its date and a
staleness disclaimer.

---

### 9. CI: minimal build+test workflow, plus badge

Commands:
```bash
find .github/workflows -type f 2>/dev/null
cat .github/workflows/*.yml 2>/dev/null | grep -iE "run:|test|build"
grep -inE "workflows.*badge\.svg|github\.com/.+/actions" README.md
```

- **Pass**: at least one workflow exists that builds the project and runs its test
  suite on push/PR, and the README shows the corresponding status badge.
- **Fail**: no `.github/workflows`, or a workflow exists but doesn't actually run
  tests, or no badge in the README (a badge with no working CI is worse than no
  badge — check it's real, not decorative).

**Remediation**: Add a minimal workflow appropriate to the language/toolchain (a
matrix isn't required — one job that installs deps, builds, and runs tests is
enough to prove the suite is real) and add
`![CI](https://github.com/<owner>/<repo>/actions/workflows/<file>.yml/badge.svg)`
near the top of the README.

---

## NICE-TO-HAVE

### 10. Polish: badges, CONTRIBUTING, naming, releases, repo metadata

Commands:
```bash
test -f CONTRIBUTING.md && echo present || grep -i "contributing" README.md
basename "$(git rev-parse --show-toplevel)"        # local dir name
git remote get-url origin 2>/dev/null               # compare to remote repo name
gh release list 2>/dev/null
gh repo view --json description,repositoryTopics 2>/dev/null
```

Check, and note as nice-to-have (not blocking):
- Badges beyond CI (license, version, platform) present and accurate.
- `CONTRIBUTING.md` exists at root or is linked from the README.
- Repo name on GitHub matches the product/project name (no leftover placeholder repo
  names from scaffolding).
- At least one tagged Release with build artifacts, if the project produces
  distributable output.
- Repo description and topics are set on GitHub (helps discoverability).

**Remediation**: quick wins — add the missing piece, or explicitly decide "not doing
this for v1" and move on. None of these block publishing.

---

## Output

The deliverable is the filled-in report below. Complete all ten items first. Be
concrete: reference exact file paths, counts, and command output rather than vague
impressions.

```markdown
# OSS Readiness Audit — <project name>

**Verdict:** [READY TO PUBLISH | NOT READY — blockers below | READY WITH CAVEATS]
**Repo state:** [no commits yet | has local commits, not pushed | already pushed]

## Blockers (must fix before first commit / before pushing)
- [ ] 1. Git repo scope — <finding>
- [ ] 2. .gitignore — <finding, MB at risk>
- [ ] 3. Secrets/PII sweep — <finding>
- [ ] 4. LICENSE — <finding>
- [ ] 5. README build/run instructions — <finding>

## Recommended (fix before or shortly after publishing)
- [ ] 6. Misleading naming / dead code — <finding>
- [ ] 7. Internal process docs placement — <finding>
- [ ] 8. Docs consistency — <finding>
- [ ] 9. CI workflow + badge — <finding>

## Nice-to-have
- [ ] 10. Badges / CONTRIBUTING / repo naming / releases / topics — <finding>

## Notes
<anything time-sensitive, e.g. "secret X must be rotated regardless of what else
happens here">
```

## Examples

A finding written the useful way, with evidence:

> **Item 2 — FAIL.** `.gitignore` missing `.build/`; a dry-run `git add -n -A | wc -l`
> stages 4,312 files including 210 MB of build artifacts (`du -sh .build` = 210M).
> Remediation: add `.build/` to `.gitignore` before the first commit.

versus the vague way that this skill forbids: "gitignore could be better."

## Limitations

- The secrets sweep is a grep-based heuristic, not a guarantee — it catches common
  key formats and filenames, but a leaked credential in an unusual format can slip
  through. Rotate anything suspicious regardless.
- If the repo has already been pushed, this audit can only report the exposure;
  cleanup requires history surgery (`git filter-repo`/BFG) plus secret rotation.

## Resources

- [choosealicense.com](https://choosealicense.com) — picking and filling in a LICENSE (item 4).
- [github/gitignore](https://github.com/github/gitignore) — canonical `.gitignore` templates per language (item 2).
- [git filter-repo](https://github.com/newren/git-filter-repo) — history surgery when a blocker is found after commits exist.

Remember: if any blocker is still open, the verdict is **NOT READY**, full stop —
recommended and nice-to-have items don't offset an open blocker. And if the repo
hasn't been pushed yet, say so explicitly, because it's the last moment fixes are
free instead of requiring history surgery.
