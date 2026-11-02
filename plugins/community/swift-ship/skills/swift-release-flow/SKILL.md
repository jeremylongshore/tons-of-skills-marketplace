---
name: swift-release-flow
description: Drives a clean, end-to-end release of a macOS/Swift app hosted on GitHub — preflight checks, version bump, CHANGELOG update, DMG build, git tag, and GitHub release. Use when asked to cut a release, publish a version, ship a new build, create a GitHub release DMG, or tag and release a macOS app. Trigger with "/swift-release-flow".
allowed-tools: Read, Write, Edit, Bash(git status:*), Bash(git rev-parse:*), Bash(git fetch:*), Bash(git log:*), Bash(git branch:*), Bash(git switch:*), Bash(git add:*), Bash(git commit:*), Bash(git tag:*), Bash(git push:*), Bash(gh auth:*), Bash(gh run:*), Bash(gh api:*), Bash(gh pr:*), Bash(gh release create:*), Bash(gh release view:*), Bash(gh release delete:*), Bash(swift:*), Bash(hdiutil:*), Bash(grep:*), Bash(ls:*)
version: 1.1.0
author: chsistrying
license: MIT
compatibility: Requires git and the GitHub CLI (gh), authenticated
tags: [swift, macos, release, github]
---

# Swift Release Flow

## Overview

Ship a macOS/Swift app release from a clean `main` to a published GitHub
release, in order. Do not skip steps. Stop and report if any preflight check
fails — never force through a red signal.

## Approval boundaries

This skill changes things outside the working tree: it pushes commits and
tags, publishes a GitHub release, and (only when recovering from a bad cut)
deletes a release or tag. Those operations sit behind three gates. At each
gate, stop, print the exact commands about to run with their real arguments,
and wait for an explicit "yes" from the user in the conversation. The original
"cut a release" request, a green preflight, or approval at an earlier gate is
never approval for a later gate.

- **Gate 1 — publish commits.** Immediately before the first `git push`
  (Step 3).
- **Gate 2 — tag and release.** Immediately before pushing the tag and
  running `gh release create` (Step 5), once the artifact path, size, and
  prerelease flag are known and can be shown.
- **Gate 3 — delete or re-cut.** Immediately before any `gh release delete`,
  `git tag -d`, or `git push origin :refs/tags/...` (Edge cases). Gate 3 is
  always a separate confirmation from Gates 1 and 2, even in the same session.

If the user declines at any gate, stop there and report what was and was not
done. Nothing in this skill force-pushes, rewrites history, edits branch
protection, or works around a rejected push.

### Protected branches and PR-based releases

Before Gate 1, check how the repository accepts changes to `main`:

```bash
gh api "repos/{owner}/{repo}/branches/main/protection" >/dev/null 2>&1 \
  && echo "main is protected" || echo "main is not protected (or protection is not readable)"
gh pr list --state merged --search "release" --limit 5   # do releases land via PRs?
```

If `main` is protected, or the project's history shows releases landing
through pull requests (a CONTRIBUTING.md rule, prior `Release vX.Y.Z` PRs), do
not push to `main` directly. Commit the version bump on a `release/vX.Y.Z`
branch, push that branch (Gate 1 still applies), open a PR with
`gh pr create`, and wait for it to be merged before continuing to Step 4.
Tag the merge commit on `main`, not the branch tip.

## Prerequisites

- `git` and the GitHub CLI (`gh`), authenticated against the repo.
- A packaging/DMG script in the repo (Step 4 locates it) — see the
  companion `swiftpm-app-bundle` skill if none exists yet.
- A `CHANGELOG.md` following Keep a Changelog conventions (created in
  Step 3 if missing).

## Instructions

### Step 0 — Confirm the target version

Ask (or infer from CHANGELOG "Unreleased" content) what kind of release this
is, then decide the version per semver-for-apps guidance:

- **Patch (X.Y.Z+1)**: bug fixes, crash fixes, performance, copy/UI tweaks,
  no new user-facing capability.
- **Minor (X.Y+1.0)**: new feature, new preference/menu item, new supported
  file type, a workflow users will notice and want to know about.
- **Major (X+1.0.0)**: breaking change to data format, dropped OS support,
  a rewrite, or the maintainer explicitly wants to signal a big jump.
- **0.x**: while pre-1.0, treat minor bumps liberally — everything is
  "still moving," and 0.x releases are prerelease by default (see Step 5).

State the chosen version back before proceeding.

### Step 1 — Preflight

Run these and stop on any failure — report exactly what's red and let the
user decide how to fix it. Do not attempt to "fix around" a red preflight
(e.g., don't force-push, don't skip tests) without explicit instruction.

```bash
git status --porcelain            # must be empty — stop if dirty
git rev-parse --abbrev-ref HEAD   # must be "main" (or confirm the release branch)
git fetch origin main --quiet
git rev-parse HEAD origin/main    # HEAD should match origin/main (or be ahead only if intentional)
gh auth status                    # must be authenticated — see Edge cases if not
gh run list --branch main --limit 5   # latest run for HEAD's commit must be green
```

If CI is red on HEAD: **stop**. Do not tag or release on top of a failing
build. Report the failing run (`gh run view <id> --log-failed`) and wait.

Then run the project's local test suite (find it — `swift test`,
`xcodebuild test -scheme <Scheme>`, or a `scripts/test*.sh`) and confirm it
passes before continuing.

### Step 2 — Version bump

Find every place the version string lives — check all of these, don't
assume there's only one:

```bash
grep -rn "VERSION" --include="*.sh" scripts/ 2>/dev/null
grep -rln "CFBundleShortVersionString\|CFBundleVersion" . --include="*.plist"
grep -rln "MARKETING_VERSION\|CURRENT_PROJECT_VERSION" . --include="*.pbxproj" --include="*.xcconfig"
grep -rn "version" Package.swift 2>/dev/null
```

Typical locations to check and update consistently to the same X.Y.Z:

- `Info.plist` / `Info-template.plist`: `CFBundleShortVersionString` (X.Y.Z)
  and `CFBundleVersion` (build number — usually bump this too, even on a
  patch release, since it must strictly increase for Sparkle/appcast users).
- `*.xcconfig` or `project.pbxproj`: `MARKETING_VERSION`,
  `CURRENT_PROJECT_VERSION`.
- `scripts/*.sh`: hardcoded `VERSION="X.Y.Z"` vars used by the packaging
  script.
- `Package.swift` if it declares a version.

Update every hit to the agreed version. If a build-number field exists
separately from the marketing version, bump it too (increment by 1) so
update-checking mechanisms see a strictly newer build.

### Step 3 — CHANGELOG and release notes

Follow [Keep a Changelog](https://keepachangelog.com) conventions.

1. Open `CHANGELOG.md`. Find the `## [Unreleased]` section.
2. Rename it to a new dated release heading, and add a fresh empty
   `## [Unreleased]` above it:

```markdown
## [Unreleased]

## [X.Y.Z] - YYYY-MM-DD
### Added
- ...
### Fixed
- ...
### Changed
- ...
```

3. Draft **user-facing release notes** from those entries — this is a
   rewrite, not a copy-paste of commit messages. Convert commit-speak into
   benefit language:
   - `fix: null deref in exporter` → "Fixed a crash that could occur when
     exporting large projects."
   - `feat: add dark mode toggle` → "Added a Dark Mode toggle in
     Preferences."
   - Drop anything purely internal (refactors, CI config, dependency
     bumps) unless it has a user-visible effect (e.g., "faster startup").
4. Save these notes to a temp file for use in Step 5, e.g.
   `/tmp/release-notes-X.Y.Z.md`, with a top line `## X.Y.Z` and grouped
   bullets.

Commit the version bump + CHANGELOG together:

```bash
git add -A
git commit -m "Release vX.Y.Z"
```

**Gate 1 — publish commits.** Run the protected-branch check from
"Approval boundaries", show the user `git log -1 --stat` and the exact push
command, and wait for their confirmation. Only then:

```bash
git push origin main
# protected main / PR-based releases instead:
#   git switch -c release/vX.Y.Z && git push -u origin release/vX.Y.Z
#   gh pr create --title "Release vX.Y.Z" --body-file /tmp/release-notes-X.Y.Z.md
```

Re-check CI on this new commit before moving on (`gh run list --branch main
--limit 3`) — don't tag a commit whose CI hasn't finished or has failed.

### Step 4 — Build the artifact

Locate the packaging script — don't assume a name, search for it:

```bash
ls scripts/*dmg* scripts/*release* scripts/*package* scripts/*build* 2>/dev/null
```

If exactly one plausible script is found, run it. If several exist or none
do, ask which to use rather than guessing:

```bash
./scripts/build-dmg.sh          # example — use the actual script found
```

Verify the resulting artifact is a valid, mountable disk image before
trusting it:

```bash
hdiutil verify path/to/AppName-X.Y.Z.dmg
```

`hdiutil verify` must report the image is valid. If it fails, do not
proceed to tagging — rebuild and re-verify.

Also sanity-check the artifact isn't accidentally huge or empty:

```bash
ls -lh path/to/AppName-X.Y.Z.dmg
```

### Step 5 — Tag and release

**Gate 2 — tag and release.** Before running anything in this step, report
the tag name and target commit, the DMG path and size from Step 4, whether
the release will be marked prerelease, and the notes file. Wait for the
user's confirmation. Approval at Gate 1 does not carry over.

Create an annotated tag (not lightweight — annotated tags carry the release
message and author, and are what `gh release` expects):

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

Create the GitHub release, attaching the artifact and using the notes file
from Step 3:

```bash
gh release create vX.Y.Z path/to/AppName-X.Y.Z.dmg \
  --title "vX.Y.Z" \
  --notes-file /tmp/release-notes-X.Y.Z.md
```

Mark as prerelease when either is true:

- The version is `0.x.y` (pre-1.0, still stabilizing), **or**
- The build is unsigned / not notarized.

```bash
gh release create vX.Y.Z path/to/AppName-X.Y.Z.dmg \
  --title "vX.Y.Z" \
  --notes-file /tmp/release-notes-X.Y.Z.md \
  --prerelease
```

If the build is unsigned, always append this note to the release notes
before publishing (macOS Gatekeeper will otherwise confuse users):

```markdown
> **Note:** This build is unsigned. macOS Gatekeeper will warn that it
> can't be opened. To run it: right-click (or Control-click) the app in
> Finder and choose **Open**, then confirm in the dialog that appears.
> You only need to do this once.
```

### Step 6 — Post-release verification

```bash
gh release view vX.Y.Z --web        # confirm the page looks right
gh release view vX.Y.Z              # confirm asset is attached, notes render
```

Confirm:
- The DMG asset is listed and its size looks right (matches Step 4's `ls -lh`).
- Notes render correctly (no broken Markdown from the CHANGELOG rewrite).
- Prerelease flag is set correctly for 0.x/unsigned builds, not set for
  stable signed 1.x+ builds.

If the project bumps to a "next dev" version after release (e.g.,
`X.Y.(Z+1)-dev` or reopening `Unreleased` with a `-SNAPSHOT` marker), do
that now and commit. This is another push, so ask again before running it
(Gate 1 covered the release commit only):

```bash
# only if the project follows this convention — check for prior examples
# in git log before doing this
git commit -am "Begin X.Y.(Z+1) development"
git push origin main
```

Finally, remind the user to announce the release (README badge, socials,
release channel, etc.) — this skill does not post announcements itself.

## Output

A published GitHub release: annotated `vX.Y.Z` tag on a green `main`, the
verified DMG attached as an asset, user-facing release notes, the prerelease
flag set correctly for 0.x/unsigned builds, and the CHANGELOG carrying a fresh
empty `[Unreleased]` section. Every external mutation along the way was
confirmed at the gate that fences it.

## Examples

```bash
# A typical 0.x patch release of an unsigned menu bar app
git status --porcelain && gh run list --branch main --limit 1   # preflight
git commit -am "Release v0.2.1"
#   -> Gate 1: user confirms the push
git push origin main
./scripts/build-dmg.sh && hdiutil verify dist/App-0.2.1.dmg     # artifact
#   -> Gate 2: user confirms tag v0.2.1 + prerelease with dist/App-0.2.1.dmg (4.1 MB)
git tag -a v0.2.1 -m "v0.2.1" && git push origin v0.2.1
gh release create v0.2.1 dist/App-0.2.1.dmg --title "v0.2.1" \
  --notes-file /tmp/release-notes-0.2.1.md --prerelease
```

## Edge cases

**Tag already exists locally or on remote.**
Never silently overwrite a tag someone else may have pulled. Show which tag
exists where (`git tag -l vX.Y.Z`, `git ls-remote --tags origin vX.Y.Z`) and
what commit it points to. **Gate 3 — delete or re-cut:** wait for a separate,
explicit confirmation before deleting anything, then:

```bash
git tag -d vX.Y.Z                       # delete local
git push origin :refs/tags/vX.Y.Z       # delete remote
git tag -a vX.Y.Z -m "vX.Y.Z"           # re-create
git push origin vX.Y.Z
```

**CI is red on HEAD.** Stop. Do not tag, build, or release. Report the
failing job (`gh run view <run-id> --log-failed`) and wait for a fix or
explicit override instruction.

**`gh` is not authenticated.**

```bash
gh auth status
gh auth login
```

Do not attempt releases via raw API calls or tokens as a workaround unless
explicitly asked.

**Artifact exceeds GitHub's 2GB per-file release-asset limit.**
`gh release create` will fail the upload. Options to raise with the user:
split the DMG, host it externally (e.g., S3) and link it in the release
notes, or reduce artifact size (strip debug symbols, compress more
aggressively). Do not silently truncate or skip the asset.

**Re-cutting a botched release** (wrong artifact, wrong notes, bad tag).
**Gate 3 — delete or re-cut:** state exactly what will be deleted (release,
local tag, remote tag) and wait for a separate confirmation. Users may have
already downloaded the asset, so this is never done silently:

```bash
gh release delete vX.Y.Z --yes     # remove the GitHub release
git tag -d vX.Y.Z                  # delete local tag
git push origin :refs/tags/vX.Y.Z  # delete remote tag
```

Then restart from Step 4 (rebuild) or Step 5 (retag) as needed — re-verify
the artifact with `hdiutil verify` again, and pass Gate 2 again before
re-releasing.

**Local tests pass but no CI is configured for this repo.** Note this
explicitly in your report instead of silently treating it as "green" — a
missing CI check is not the same as a passing one.

## Resources

- [Keep a Changelog](https://keepachangelog.com) — the CHANGELOG conventions Step 3 follows.
- [Semantic Versioning](https://semver.org) — the version-choice guidance behind Step 0.
- [`gh release` manual](https://cli.github.com/manual/gh_release) — flags for assets, notes, and prerelease handling.
