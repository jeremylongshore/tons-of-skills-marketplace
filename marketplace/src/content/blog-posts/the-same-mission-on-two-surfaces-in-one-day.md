---
title: "The Same Mission on Two Surfaces in One Day"
description: "Two new Omarchy entry repos scaffold the same game on the same day: one as a QML bar-widget teaser with a single local mission and a fixed parent-guide link, one as a downloadable Electron desktop app with a six-mission chapter and a seven-day trial."
date: "2026-09-10"
tags: ["omarchy", "marketplace", "release-engineering", "product-launch", "electron", "qml"]
featured: false
canonical: "https://startaitools.com/posts/the-same-mission-on-two-surfaces-in-one-day/"
---
The day's pattern is the pairing. Two brand new Omarchy entry repos landed on
the same theme, "Beacon Nine", on the same day, on two different deployment
surfaces. One is the free bar teaser that lives inside the Omarchy launcher.
The other is the downloadable desktop game. Both ship the same opening
mission on purpose: a player who finishes the teaser ends one click away from
the full chapter, and a player who installs the desktop app gets the same
mission as the first of six consequential trail choices.

## omarchy-omaquest-entry: the bar-widget teaser

The teaser repo committed its entire scaffold in a single feat on 2026-09-10
at 16:14 UTC (`d189383`). It is the only Omarchy entry plugin of its kind:
the manifest declares two kinds (`overlay`, `bar-widget`), one entry point
for each, and a bar widget that renders under aliases including `omaquest`,
`the-beacon-wakes`, and `beacon-nine`. The teaser runs locally in QML and
JavaScript. The runtime ships without accounts, saves, telemetry, payment flow, a daemon, or gameplay network traffic. The single outbound action is a user-triggered
`xdg-open` to one fixed HTTPS URL on `oma.intentsolutions.io`, and it is
gated behind a completed mission and an explicit parent-information handoff.

The gameplay is exact typing. The overlay loads a mission, the player types
the visible transmission character-by-character, and the model increments the
attempt count on a wrong key without ever advancing the prompt. Correct keys
draw the route across a canyon map. The route is drawn by the QML layer; the
state and progression live in the Node `module.exports` surface of
`Model.js`, and `Overlay.qml` may call only top-level ES5 functions that
appear on that export. The contract test in `tests/contract.test.js` walks
every `Model.*()` call from QML and verifies the export, plus proves the
manifest, bar host, overlay, and IPC handler share one module ID.

The plugin carries the marketplace claim ledger at `contracts/marketplace.md`:
six rows that pair a marketing claim, the shipped source line that backs it,
and the executable proof that exercises the claim. The proof column names
the relevant gate (C31, C34, C35, C41, C42, the contract tests, the model
tests, the hash-bound Buzz render receipt).

The follow-up commits the same day tightened the launch. `aa1fdce fix:
render the mission in progress for marketplace proof` updated `Overlay.qml`
(9 lines added) and `tests/contract.test.js` (9 lines added) so the
marketplace preview could show the mission in progress, not the title screen.
`eae40a5 test: record clean OmaQuest shell render evidence` sealed the
Buzz-rig render: `.render-proof.json` now carries fingerprint
`eba0574023db7f33b56b979ea8d057ed0cbc20420c9d6878dd774c4a5c8d15e4`,
preview sha256 `f172fc1f...`, dimensions `1280 x 720`, nonblack coverage 1,
and `.rig-proof.json` records `omarchyPluginValidate: 0` and `qmllintErrors:
0` against source commit `97cdb6b`. The 90 KB `preview.png` is the
hash-bound capture that the marketplace preview reuses.

`97cdb6b docs: align the model contract with Beacon Nine` then renamed the
contract reference from `Panel.qml` to `Overlay.qml`, tightened the model
contract ("deterministic mission state, prompt progression, accuracy, route
progress") and removed the older line about external response fixtures. The teaser has no external data contract of its own. The harness-hash rolled to match.

The gate lane that ships with the plugin is sixteen scripts, C28 through
C44: c28 voice no-dashes, c29 private names, c30 markdown strikethrough,
c31 QML security, c34 exec injection, c35 runtime dependency, c36 QML
overflow, c38 SSRF host allowlist, c40 panel design, c41 state file
hygiene, c42 local resource budget, c43 marketplace presentation, c44
installable tree (the same C44 shipped yesterday in contributing-clanker,
moved here too). Every gate ships in `scripts/gates/` and is called from
`scripts/run-plugin-gates.sh`.

## omarchy-typing-adventure: the desktop game

The desktop game committed its first feat on 2026-09-10 as well
(`2d4c8fa feat: build OmaQuest playable preview`, 71 files, 10843
insertions). The product is the same opening act from a different surface:
a local Electron + TypeScript game that packages a Vite renderer for Linux
AppImage, with a seven-day local trial and an Ed25519-signed offline
license import. The gameplay surface is broader: six missions across
Signal, Rover, and Orbit trail choices, twelve transmissions in the
chapter, mission-boundary checkpoints that survive a reload, accuracy,
clean-key streak, WPM, completed-transmission results, and an explicit
pause and resume that never discards unfinished input.

The substantive code at first commit: `src/main.ts` 518 lines,
`src/game.ts` 98 lines, `src/style.css` 285 lines, `electron/main.cjs`
111 lines, `index.html`, `vite.config.ts`, `playwright.config.ts`,
`eslint.config.js`. The test lane is broad: Vitest unit tests, Stryker
mutation tests, Playwright E2E for browser and packaged, a Playwright
config for the generated AppImage under an isolated Linux profile, plus a
deterministic screenshot capture (`tools/capture.mjs`) that produces the
five documented product screenshots.

The product brief is the matching half of the pairing. `PRODUCT.md`
explicitly notes that "a separate Omarchy plugin is the planned playable
teaser: one original local mission and a fixed link to the parent-facing
product page. It is not to be submitted until this game MVP is complete."
The teaser launched the same day the game MVP landed its first playable
preview, by design. The desktop product ID is still `omaquest` during the
rename; the player-facing name is "The Beacon Wakes", and the same alias
shows up in the teaser manifest.

The brand voice profile shipped at the same commit (`brand/voice-profile.md`):
"an inventive mission guide that treats young players as capable builders
and gives parents clear, credible reasons to trust the experience." It
gives concrete do-and-don't pairs: "Tune the receiver. Type the signal
before it fades." versus "Hey, little genius. Let us do a super-fun typing
exercise." The voice and the contract claim ledger are the two pieces of
documentation that travel to both repos.

## omarchy-listening-post-entry: beads only

A third Omarchy entry repo touched git on the same day, but only by a
beads init (`e178496 bd init: initialize beads issue tracking`): 6 files,
237 insertions, no source code. It is on the same estate as the other two
but unrelated to the launch; the substantive change there is the issue
tracker.

## Why the pairing matters

The free teaser and the paid desktop game are the same opening mission in
two different distributions. A player who finishes the teaser in the
Omarchy bar sees one fixed link to the parent-facing product page; a
parent who installs the desktop app gets the same mission as mission one
of six. The teaser does not install the game, collect child data, process
payment, or promise physical inventory, all four of which are explicit
boundaries in both repos' manifests. The pattern is the deliberate
two-surface launch, the playable hook in the launcher plus the
downloadable chapter next to it, with one fixed link connecting them.

The day's receipts are the Buzz rig render on the teaser
(`previewSha256: f172fc1f...`) and the Ed25519 license import plus
AppImage packaging on the desktop. Neither repo shipped a debugging story;
both shipped initial scaffolds of complementary surfaces.

## Related Posts

- [Hardening a Marketplace in One Day](https://startaitools.com/posts/hardening-a-marketplace-in-one-day/) (2026-09-08, the C44 gate that now ships with the teaser)
- [A 953-line skill entry fits the budget again](https://startaitools.com/posts/a-953-line-skill-entry-fits-the-budget-again/) (2026-09-09, the contributor workflow refactor)
- [The Corrected Record Was Still Wrong](https://startaitools.com/posts/the-corrected-record-was-still-wrong/) (2026-09-06, the same-day site rebuild lesson that informs the teaser claim ledger)
