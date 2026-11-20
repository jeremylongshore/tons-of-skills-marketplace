---
name: swift-ci-portability
description: Sets up GitHub Actions CI for Swift Package Manager projects (minimal macOS build+test workflow, Xcode/macOS version matrix, .build caching, runner image selection) and diagnoses/prevents environment-dependent Swift bugs that pass locally but fail on CI (JSONDecoder ISO8601 fractional seconds, NumberFormatter locale grouping, Date/timezone assumptions, locale-dependent string sorting, hardcoded paths, filesystem case-sensitivity, Bundle.module resource paths, Decimal/Double formatting). Use when asked for "swift CI", "GitHub Actions swift test", when "tests pass locally but fail on CI", or when debugging "locale" or "Foundation differences" between macOS/Xcode versions. Trigger with "/swift-ci-portability".
allowed-tools: Read, Write, Edit, Bash(swift:*), Bash(mkdir:*), Bash(cp:*), Bash(env:*)
version: 1.0.0
author: chsistrying
license: MIT
compatibility: Swift Package Manager projects on GitHub Actions (macOS runners)
tags: [swift, ci, github-actions, testing]
---

# Swift CI & Portability

## Overview

Two jobs, one skill: get a SwiftPM project onto GitHub Actions CI quickly,
and stop (or diagnose) the specific class of bug where tests pass on a
developer's Mac but fail on CI - or pass on one CI runner and fail on
another.

## Prerequisites

- A Swift Package Manager project (`Package.swift`) hosted on GitHub with
  Actions enabled.
- `swift` toolchain locally for reproducing CI failures.

## When to use this

- Setting up CI for a SwiftPM package/app for the first time.
- A test suite is green locally but red on GitHub Actions (or red on one
  matrix row and green on another).
- You're about to write code that touches dates, locales, number
  formatting, file paths, or bundled resources, and want to avoid known
  traps up front rather than debug them later.

## Instructions

Setting up GitHub Actions CI:

1. Copy the template workflow into the repo:

   ```bash
   mkdir -p .github/workflows
   cp assets/ci.yml.template .github/workflows/ci.yml
   ```

2. Open `.github/workflows/ci.yml` and adjust to the project:
   - **Runner image / Xcode version** - the `test` job pins one
     macOS/Xcode combination as the fast required check. Pick versions
     that match what your team actually develops against. Check
     currently available images and their preinstalled Xcode versions at
     https://github.com/actions/runner-images (search the macOS READMEs)
     before picking a runner label like `macos-14` or `macos-15`.
   - **Matrix rows** (`test-matrix` job) - list the oldest and newest
     macOS/Xcode combination you need to support. This is what catches
     the Foundation-version-dependent bugs cataloged in
     `references/portability-traps.md` - they show up as one matrix row
     failing while others pass.
   - **Cache key** - the template keys the `.build` / SwiftPM cache on
     `hashFiles('**/Package.resolved')`, so the cache invalidates exactly
     when dependencies change. Leave this as-is unless you have a reason
     to scope it differently (e.g. a monorepo with multiple packages).
   - **Test invocation** - `swift test --parallel` is the default;  add
     `--enable-code-coverage`, `--filter <TestName>`, or
     `--sanitize=thread` as needed.
   - Delete the `test-matrix` job if a single-version check is enough for
     now (you can always reinstate it later - see references doc for why
     you might want it sooner rather than later).
   - Uncomment the Linux job only if the package needs to build under
     server-side Swift; note the comment in the template that Linux uses
     a different Foundation implementation (`swift-corelibs-foundation`),
     so expect divergence beyond what's cataloged here.

3. Commit and push. Confirm the workflow runs on the next PR/push to
   `main`.

4. **Make the fast `test` job a required status check** in the repo's
   branch protection settings, and let `test-matrix` run as an
   informational (non-blocking) check if you kept it - this gives fast
   feedback on every push while still surfacing cross-version drift.

### Picking runner images / Xcode versions

- GitHub's `macos-14` / `macos-15` labels map to specific Xcode default
  versions that change over time; pin the Xcode version explicitly with
  `xcode-select` (as the template does) rather than relying on whatever
  the runner's default happens to be on a given day - GitHub updates
  runner images regularly and an unpinned default Xcode can silently
  change under you.
- If you need an Xcode version not preinstalled on the runner image,
  use the `maxim-lobanov/setup-xcode` action to install it, or fall back
  to a self-hosted runner.
- Prefer testing against the oldest Xcode/macOS you claim to support and
  the newest stable one - that pair is what surfaces the Foundation
  version drift covered under Troubleshooting below.

## Output

A committed `.github/workflows/ci.yml` with a fast required `test` job and an
optional informational version-matrix job, plus (when debugging) a root-cause
diagnosis mapped to a specific trap in `references/portability-traps.md` with
a fix at the narrowest layer.

## Troubleshooting

Diagnosing "passes locally, fails on CI":

This class of bug is almost always one of:

1. A **library behavior difference across Foundation versions** (older
   vs. newer macOS/Xcode runner) - the timestamp/number-formatting traps
   below.
2. An **implicit environment dependency** - timezone, locale, working
   directory, home directory - that differs between the developer's
   machine and the CI runner.
3. A **build/resource-resolution difference** - stale local build
   artifacts masking a `Bundle.module` or path bug that a clean CI
   checkout exposes.

Read `references/portability-traps.md` for the full catalog
(symptom -> cause -> fix), including two traps verified in a real
project:

- **JSONDecoder `.iso8601` silently rejects fractional-second
  timestamps** (`"2026-07-10T10:00:00.000Z"`) on older Foundation,
  dropping records with no visible error on affected runners.
- **NumberFormatter grouping separators differ**: `en_US_POSIX` has
  grouping size 0 (no thousands separators) by definition, so tests that
  assert `"9,876"` while using a POSIX locale are inherently
  version-fragile.

Also cataloged: `Date()`/timezone-dependent assertions, locale-dependent
string sort order, hardcoded `/Users/...` paths, filesystem
case-sensitivity assumptions, `Bundle.module` resource resolution in
tests, and `Decimal`/`Double` string-description differences.

## Examples

Don't guess - gather facts, then reproduce locally:

```bash
# What does CI actually see? (the template workflow already prints this)
swift --version
xcodebuild -version
defaults read -g AppleLocale   # locale
date +%Z                        # timezone
sw_vers                         # OS version

# Reproduce a stripped/CI-like environment locally instead of guessing:
env -i HOME="$HOME" PATH=/usr/bin:/bin swift test      # strip inherited env
LANG=C.UTF-8 LC_ALL=en_US_POSIX swift test              # force a locale
TZ=UTC swift test                                        # force a timezone
```

If the failure only reproduces on one CI matrix row (e.g. only on
`macos-13`, or only on the newest Xcode), that immediately tells you
whether you're chasing an "older Foundation" or "newer Foundation" trap -
narrow the catalog search in `references/portability-traps.md`
accordingly.

Fix at the narrowest layer: inject explicit locale/timezone/clock
dependencies and use custom decoding/formatting strategies (see the
catalog for concrete code) rather than papering over failures with
`#if os(...)` guards or skipping tests on specific runners - that just
defers the bug to whichever environment you didn't test.

## Resources

- `assets/ci.yml.template` - copy-paste GitHub Actions workflow (minimal
  job + version matrix job, with caching and environment-printing steps
  built in).
- `references/portability-traps.md` - the trap catalog and full
  debugging methodology; read this when a specific bug is suspected
  rather than trying to memorize it up front.
