---
title: "Pin the Installer and Add a Renewer"
description: "A CI tool that floats is a gate whose behaviour changes without a commit. Pin the installer, then add a renewer so the pin is refreshed by review."
date: "2026-09-24"
tags: ["ci-cd", "devops", "release-engineering", "supply-chain"]
featured: false
canonical: "https://startaitools.com/posts/pin-the-installer-and-add-a-renewer/"
---
## The day the registry broke main

Three times on the morning of 2026-09-19, the main branch across the Intent Solutions estate turned red. Each break ran through the same kind of gate: a lint or test tool installed by CI without a pin. The diff was empty. The commits had landed the day before. The same source files were producing different verdicts because the registry had been free to choose what to serve.

The line that named it, from the rationale in startaitools PR #106:

> An upstream release turned main red three times on 2026-09-19 across the estate with no diff to blame. A lint or test tool that floats is a CI gate whose behaviour changes without a commit.

That sentence is the finding. Everything that happened on 2026-09-24 followed from it. A floating tool is a gate whose behaviour changes without a commit. The pin is what turns the random walk back into a gate.

## The diff that closes it

Startaitools is the local anchor because the blog pipeline runs on it. PR #106 (commit `7232f61e`) merged 2026-09-25 00:39 CDT and shipped two files at once, which is the point:

`scripts-lint.yml` pinned the install:

```
pip install ruff==0.16.9 pytest==9.1.1
```

`.github/dependabot.yml` gained the missing `pip` ecosystem, weekly, with a limit of five open PRs:

```
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

Both files have to land together. The pin locks today's behaviour. The renewer refreshes it under review rather than by surprise. A pin with no renewer rots in place until someone remembers to look. A renewer with no pin schedules churn that the registry controls.

CI run 36098736195 came back all-green with both files in place. The lint gate stopped floating the moment the version got named.

## Why three lanes

The estate is not one codebase. Pinning a Python tool, a Ruby tool, and a GitHub Actions shell installer in a single PR would merge three unrelated owners, three unrelated histories, and three unrelated failure modes into one diff. The sweep ran as three parallel lanes from a single root cause instead.

| Lane | Stack | What got pinned |
|---|---|---|
| A | Python linter and test deps (13 repos) | `ruff` and `pytest` to the version each repo's last green run resolved |
| B | Ruby Gemfile.lock (9 wild-* gems) | Lock files committed, `rubocop 1.91.0` and `rubocop-rspec 3.10.2` pinned, dependabot on bundler and github-actions |
| C | GitHub Actions shell installers (6 first-wave repos, plus a second wave) | SHA-pinned actions and tarballs (lychee, markdownlint-cli2, gitleaks, govulncheck, actionlint, golangci, syft, ollama, ad-m/github-push-action) |

Lane A (Python linter and test deps) hit 13 repos. Irsb PR #10 pinned `ruff==0.16.8`. Perception-with-intent PR #17 pinned `pytest==9.1.1`. Plugins-nixtla PR #40 came back 54 of 54 checks green after pinning. Stci-standard-inference-token-cost-index PR #15 pinned both `ruff==0.16.9` and `pytest==9.1.1`, 7 of 7 checks green. Coastal-realty-ops PR #62 pinned `ruff==0.15.22` and `pytest==9.1.1`. Intent-eval-lab PR #374 cleared a pre-existing pytest freshness red that had been waiting for the pin. The versions differ because each repo's last green run resolved a different snapshot.

Lane B (Ruby Gemfile.lock) hit 9 wild-* gems. Every Gemfile.lock got committed, the ignore rule for the lock got removed, dependabot picked up the `bundler` and `github-actions` ecosystems, and `rubocop 1.91.0` with `rubocop-rspec 3.10.2` got pinned at the last green versions. All CI green on Ruby 3.2 and 3.3, all squash-merged, branches deleted. The original repos under `~/000-projects/wild-*` were left alone. The lane only touched the scratchpad clones. One note for anyone who works on these: `admin-tools-mcp`'s lock pins the git dep `wild-capability-gate` at `929d95e`. A `bundle update` would advance it. Do that on its own PR.

Lane C (GitHub Actions shell installers and actions) hit 6 repos on the first wave. Bobs-big-brain-registrar PR #353 pinned `markdownlint-cli2@0.23.3`, SHA-pinned `lychee v2.9.0` and `gitleaks-action v3.0.0`. Iam-bob-eino PR #14 pinned `govulncheck v1.8.0`, `gitleaks v8.30.1`, and SHA-pinned the syft action, with dependabot on `gha` and `gomod`. Iam-local-rag PR #21 SHA-pinned the `ollama v0.34.4` tarball with its sha256, and added `gha` dependabot. Hustle PR #79 SHA-pinned `ad-m/github-push-action v1.3.0`. Iam-git-with-intent PR #112 replaced a `rustup` plus nonexistent-crate combo with `npm @beads/bd@1.3.0`. Resume-realtime PR #4 SHA-pinned the rust toolchain at `nightly-2024-10-01`, set `cargo-leptos 0.3.9 --locked`, and pinned `tailwind v3.4.19` with sha256.

A second wave SHA-pinned the major actions (lychee, markdownlint, gitleaks, actionlint, golangci) across the remaining repos.

The models that worked the lanes on 2026-09-24 were MiniMax M3, Claude Opus 5 5, Claude Fable 5 1, Claude Sonnet 5, GPT 6 Astra, and Claude Opus 5. The cross-session journal shows 8 sessions and 1,219 minutes of span across 6 models, with 49 entries tagged `pin sweep`. The reason that number matters is the split itself. Lanes A, B, and C were dispatched in parallel from a single root cause. A git log records the PRs. The journal records that the day was a coordinated sweep, not three unrelated coincidences.

## Pin to latest, or pin to what last green resolved

Pin to the version the green run actually resolved, not to whatever the registry serves today. An upstream release the day before is what made main flip red three times across the Intent Solutions estate with no diff to blame. Capture the resolved version with `pip freeze`, `npm ls`, `bundle list`, or `cargo tree`, then pin to that.

The PR body reasoned through the choice. Pin to latest sounds right and is wrong here. Latest can itself introduce new findings. The 2026-09-25 green run resolved `ruff 0.16.9` and `pytest 9.1.1`, and those are what got pinned. The install used `--quiet`, so it echoed no version. The pin sits at the registry latest only because the last green run happened to coincide with that latest.

The risk the PR body flagged is real. A `pip install ruff` line that floats to whatever the registry serves today is the failure mode that broke main on 2026-09-19. Pinning to whatever the registry serves today does not fix it for tomorrow's run. The defensible move is to name the version that the green run actually resolved, not the version the registry will serve tomorrow. Lane A picked different versions across repos because each repo's last green run resolved a different snapshot. Pins that match the resolved version are the right pin.

## What did not work

Two repos in lane A had pre-existing lint debt that the pin could not clear. Waygate-mcp PR #5 had a Test and Quality job red on pre-existing `black --check` debt before the pin landed. The pins themselves were green. The gate stayed red because of the pre-existing finding. Crypto-agent PR #2 had a lint job red on the same `black --check` debt. Test and docker passed. Lane D, the black reformat cleanup, landed the reformat. The pre-existing ruff and isort debt kept the lint job red after the cleanup.

The honest read: the sweep pinned the tool. It did not pin the findings. A floating tool was the cause of the 2026-09-19 red flips. Pre-existing lint debt is its own problem, with its own lane, its own PRs, and its own clock.

## Also shipped

The same day carried five unrelated lines that did not belong to the pin sweep. MCP SDK 2.x ports landed in `plugins-nixtla`, `plugins-moat`, and `claude-code-plugins`. Intent-mail moved to zod 4 with TypeScript 6 and the ESLint 10 flat config. Coastal-realty-ops took the Invelo correction. Braves re-exported its beads. Bobs-big-brain-compiler shipped v1.23.0.

## Use this

- Audit your own CI for floating installs. Run `grep -nE 'pip install|gem install|npm install -g|brew install|actions/[a-z]+@' .github/workflows/*.yml` and count any line that resolves a name without a version.
- Run `gh extension list | grep dependabot` (or `dependabot --version` in your local toolchain). If the renewer is not installed or configured, the pin will rot.
- For each green run, capture the resolved version. `pip freeze`, `npm ls`, `bundle list`, `cargo tree`. The pin should match what last green resolved, not what the registry serves today.

## FAQ

### Should CI tool installs pin to the registry's latest version?

No. Pin to the version the green run actually resolved. Pinning to `latest` replaces one floating resolution with another floating resolution. The 2026-09-19 estate break showed exactly that failure mode. Capture the resolved version with `pip freeze`, `npm ls`, `bundle list`, or `cargo tree`, then pin to that.

### Why did my CI go red with no code change?

A floating lint or test tool resolved a different snapshot on different days. Three CI runs on 2026-09-19 turned main red across the Intent Solutions estate without any commit on the source files. The diff was empty and the commits had landed the day before. Pinning the installer to a named version is what stops the random walk.

### What is the difference between a pin and a renewer?

A pin freezes today's behaviour at a named version. A renewer (Dependabot or a similar scheduled bot) refreshes that pin under review rather than by surprise. A pin without a renewer rots in place until someone remembers to look. A renewer without a pin schedules churn that the registry controls.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Should CI tool installs pin to the registry's latest version?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. Pin to the version the green run actually resolved. Pinning to latest replaces one floating resolution with another floating resolution. The 2026-09-19 estate break showed exactly that failure mode. Capture the resolved version with pip freeze, npm ls, bundle list, or cargo tree, then pin to that."
      }
    },
    {
      "@type": "Question",
      "name": "Why did my CI go red with no code change?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A floating lint or test tool resolved a different snapshot on different days. Three CI runs on 2026-09-19 turned main red across the Intent Solutions estate without any commit on the source files. The diff was empty and the commits had landed the day before. Pinning the installer to a named version is what stops the random walk."
      }
    },
    {
      "@type": "Question",
      "name": "What is the difference between a pin and a renewer?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A pin freezes today's behaviour at a named version. A renewer (Dependabot or a similar scheduled bot) refreshes that pin under review rather than by surprise. A pin without a renewer rots in place until someone remembers to look. A renewer without a pin schedules churn that the registry controls."
      }
    }
  ]
}
</script>

## Related Posts

- [Fix the Dependabot Pile-Up: Policy Over Patches](https://startaitools.com/posts/dependabot-pile-up-fix-the-policy/)
- [Transitive CVE Clearance: The Dual-Layer Pattern](https://startaitools.com/posts/transitive-cve-clearance-dual-layer-pattern/)
- [Software Supply Chain Security After Axios](https://startaitools.com/posts/software-supply-chain-security/)
