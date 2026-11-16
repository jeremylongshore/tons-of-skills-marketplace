# Swift Ship 🚢

![Validate](https://github.com/chsistrying/swift-ship-skills/actions/workflows/validate.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Spec](https://img.shields.io/badge/Agent%20Skills-spec%20compliant-blue)

**Agent Skills that take a Swift/macOS app from "builds on my machine" to a public GitHub release.**

Five skills for Claude Code (and any [Agent Skills](https://agentskills.io)–compatible agent), distilled from shipping a real macOS menu bar app — [TokenScope](https://github.com/chsistrying/TokenScope) — with an AI-agent workflow. Every command in these skills has been run for real; every CI trap documented here actually bit us.

## The skills

| Skill | What it does | When you need it |
|---|---|---|
| [`macos-app-icon`](skills/macos-app-icon) | Generates a complete `.icns` from one SVG/PNG using only built-in macOS tools (`qlmanage`, `sips`, `iconutil`) | "My app has no icon" |
| [`swiftpm-app-bundle`](skills/swiftpm-app-bundle) | Packages a SwiftPM executable into a proper `.app` bundle + DMG — Info.plist, `LSUIElement`, icon embedding, Gatekeeper notes | You built with SwiftPM (no Xcode project) and want something people can download |
| [`swift-ci-portability`](skills/swift-ci-portability) | Sets up GitHub Actions for Swift and diagnoses "passes locally, fails on CI" — with a catalog of real Foundation version/locale traps | Your first CI run is red and you don't know why |
| [`oss-readiness-audit`](skills/oss-readiness-audit) | Systematic pre-publish audit: git repo scope, `.gitignore`, secrets sweep, LICENSE, README, misleading naming, dead code | Before your project's very first public push (language-agnostic) |
| [`swift-release-flow`](skills/swift-release-flow) | Cuts a release end to end: preflight → version bump → CHANGELOG → DMG → tag → GitHub Release | Shipping v0.2.0 |

## Install

### As a Claude Code plugin (recommended)

```
/plugin marketplace add chsistrying/swift-ship-skills
/plugin install swift-ship@swift-ship
```

### Manual (any Agent Skills–compatible tool)

```sh
git clone https://github.com/chsistrying/swift-ship-skills.git
cp -r swift-ship-skills/skills/* ~/.claude/skills/
```

Install a single skill the same way — each directory under `skills/` is self-contained.

## Why these five?

They are the exact gaps between "side project" and "shippable product" that don't show up until you try to publish:

- SwiftPM builds a bare executable — there is no `.app`, no icon, no DMG unless you make them.
- `swift test` passing locally proves nothing about other machines — Foundation's date and locale behavior differs across macOS versions ([documented in the traps catalog](skills/swift-ci-portability/references/portability-traps.md)).
- The riskiest moment of an open-source project is the **first** `git push` — history is permanent, and that's when secrets, build artifacts, and your entire home directory (yes, really — see the audit skill) leak.

## Design principles

- **Progressive disclosure** — each `SKILL.md` stays lean; heavy reference material lives in `references/`, runnable logic in `scripts/`.
- **Built-in tools only** — the macOS skills use `qlmanage`/`sips`/`iconutil`/`hdiutil`; nothing to brew-install.
- **Honest about limits** — unsigned builds get a Gatekeeper warning; the skills say so and document the paid upgrade path instead of pretending.
- **Spec compliant** — validated in CI against the [Agent Skills spec](https://agentskills.io/specification).
- **Bounded side effects** — the release flow stops for explicit confirmation before every push, tag, release, or deletion; the packaging script validates every name, id and version before it touches the filesystem.

## Tests

`tests/` runs the real packaging and icon scripts against stubbed `swift`, `hdiutil`, `sips`, `iconutil`, `qlmanage` and `plutil`, so the suite is deterministic and runs on Linux and on the bash 3.2 that macOS ships. It covers rejected inputs, the resulting `.app`/`Info.plist` layout, cleanup, failure propagation, and the release flow's approval gates.

```sh
bash tests/run_tests.sh
```

## Contributing

Issues and PRs welcome. New skills should follow the [spec](https://agentskills.io/specification), pass `python3 scripts/validate_skills.py` and `bash tests/run_tests.sh`, and document real, tested workflows — no speculative content.

## License

[MIT](LICENSE)
