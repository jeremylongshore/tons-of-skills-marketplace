---
name: swiftpm-app-bundle
description: Package a Swift Package Manager (SwiftPM) executable target — an AppKit or SwiftUI app built without an Xcode project — into a distributable macOS .app bundle and an unsigned .dmg. Use when the user wants to package .app, build a DMG, turn a SwiftPM executable to app bundle, prepare a menu bar app distribution, ship a Swift command-line/GUI target as a double-clickable Mac app, or asks about Info.plist / .icns / LSUIElement / codesign / notarization for a package-based (no .xcodeproj) macOS app. Trigger with "/swiftpm-app-bundle".
allowed-tools: Read, Write, Bash(swift:*), Bash(hdiutil:*), Bash(chmod:*), Bash(xattr:*), Bash(plutil:*)
version: 1.1.0
author: chsistrying
license: MIT
compatibility: macOS 12+; Xcode Command Line Tools (swift, codesign, xcrun); hdiutil (bundled with macOS)
tags: [swift, swiftpm, macos, packaging, dmg]
---

# SwiftPM App Bundle

## Overview

Turns a SwiftPM `.executableTarget` into a real macOS `.app` bundle plus an
unsigned `.dmg`, with no Xcode project involved. This is the common path for
small AppKit/SwiftUI utilities (menu bar apps, single-window tools) that are
built with `swift build` and never had an `.xcodeproj` to begin with.

## Prerequisites

- macOS 12+ with Xcode Command Line Tools (`swift`, `codesign`, `xcrun`).
- `hdiutil` (bundled with macOS) for DMG creation.
- A `Package.swift` with at least one `.executable` product.

## When to use this skill

- The repo has a `Package.swift` with an `.executable` product but no `.app`
  bundle, no `.xcodeproj`/`.xcworkspace`, and the user wants something they
  (or testers) can double-click, or a `.dmg` to hand out.
- The user mentions: "package .app", "make a DMG", "SwiftPM executable to app
  bundle", "menu bar app distribution", "ship this as a Mac app".

## What it does NOT do

- Does not sign or notarize anything (see `references/signing-notarization.md`
  for that — it requires a paid Apple Developer account).
- Does not create an Xcode project. If the user actually wants a proper
  Xcode-managed app target, that's a different task — ask before assuming.

## Usage

From the repo root (the directory containing `Package.swift`):

```bash
scripts/package_app.sh
```

With no flags it will:
1. Auto-detect the app name from the first `.executable(name: "...")` product
   in `Package.swift`.
2. `swift build -c release` that product.
3. Assemble `dist/<App>-<version>-unsigned-<timestamp>/<App>.app`.
4. Stage a DMG with the `.app` plus an `/Applications` symlink and build
   `<App>-<version>-unsigned.dmg` in the same output directory.

Common flags (`scripts/package_app.sh --help` for the full list):

| Flag | Purpose |
|---|---|
| `--app-name NAME` | Override auto-detection |
| `--bundle-id ID` | Default is `com.example.<lowercased-app-name>` — always override this for a real release |
| `--version STRING` | Default `0.1.0` |
| `--min-os STRING` | `LSMinimumSystemVersion`, default `13.0` |
| `--menu-bar` | Sets `LSUIElement=true` (no Dock icon / no app switcher entry) |
| `--icon PATH` | Embed a `.icns`; auto-picked up from `assets/<AppName>.icns` if present |
| `--skip-dmg` | Build just the `.app`, skip DMG staging |

Both flags and env vars work (`APP_NAME=`, `BUNDLE_ID=`, `VERSION=`, etc. —
see the script's `--help` output for the full mapping).

### Input rules

Every value that ends up in a path or in `Info.plist` is validated before the
script touches the filesystem, and the run stops with a clear `error:` line
if any of them fails:

| Value | Accepted |
|---|---|
| `--app-name`, `--product` | 1–255 chars of letters, digits, space, `.`, `_`, `-`; starts with a letter or digit; no trailing space or `.`; never `.` or `..`; no `/`, `\`, `:` or control characters |
| `--bundle-id` | reverse-DNS: two or more dot-separated labels of letters, digits and `-` (`com.example.myapp`) |
| `--version`, `--min-os` | 1–3 dot-separated numbers (`1.2.3`, `13.0`) |
| `--icon` | must be an existing regular file |

Values are then XML-escaped when written into the plist (no `sed`/`awk`
interpolation), and the rendered plist is checked with `plutil -lint` when
`plutil` is available. If a user wants a display name outside these rules
(non-ASCII, punctuation), keep the bundle name ASCII and localize
`CFBundleDisplayName` via `InfoPlist.strings` instead of loosening the check.

## Examples

```bash
# Menu bar app with a real bundle id and an icon
scripts/package_app.sh --menu-bar --bundle-id com.example.tokenscope \
  --version 0.2.0 --icon assets/TokenScope.icns

# Just the .app, no DMG, for quick local testing
scripts/package_app.sh --skip-dmg
```

## Output

A timestamped `dist/<App>-<version>-unsigned-<timestamp>/` directory containing
the assembled `<App>.app` bundle and (unless `--skip-dmg`) a compressed
`<App>-<version>-unsigned.dmg` staged with the standard drag-to-Applications
layout.

## Detecting the app name from Package.swift

The script greps for the first `.executable(name: "X"` occurrence. When
briefing a user or writing this by hand, the same rule applies: open
`Package.swift`, find the `products: [ .executable(name: "X", ...) ]` entry.
If there are multiple executable products, ask the user which one they mean,
or pass `--app-name` / `--product` explicitly (`--product` matters when the
Swift product name differs from the desired display/bundle name).

## When to set LSUIElement (menu-bar-only apps)

Set `--menu-bar` (→ `LSUIElement=true`) when the app:
- Lives in the menu bar via `NSStatusItem` / `MenuBarExtra` and has no main
  window the user is meant to switch to via Cmd-Tab, or
- Should not show a Dock icon or appear in the Cmd-Tab app switcher.

Leave it unset (`LSUIElement=false`, the default) for a normal windowed app
that should appear in the Dock and app switcher as usual. Check the source for
`NSStatusBar.system.statusItem` or `MenuBarExtra` in SwiftUI as a strong signal
the app is menu-bar-only.

## DMG staging layout

The script stages the DMG contents in a scratch `dmg/` folder before calling
`hdiutil create -format UDZO`:

```
dmg/
├── YourApp.app          (copy of the built bundle)
└── Applications -> /Applications   (symlink)
```

This is the standard "drag YourApp.app onto Applications" layout users expect
from a Mac installer DMG. Don't skip the symlink — without it, users have to
manually drag the app to `/Applications` via Finder navigation instead of a
single drag within the mounted window.

## Failure modes

- **Missing `NSHighResolutionCapable`** — omitting this key (or leaving it
  `false`) makes the app render blurry on Retina displays. The template
  always sets it `true`; don't remove it when hand-editing a plist.
- **Forgetting `chmod 755` on the binary** — `cp` preserves source
  permissions, which can be `644` from some build/copy pipelines, silently
  producing an app that Finder shows a "no entry" cursor for on launch. The
  script always does `chmod 755` on the copied executable; verify this if the
  bundling steps are done manually instead of via the script.
- **Cached icon not updating on rebuild** — macOS's icon cache can keep
  showing an old icon for an app bundle after replacing its `.icns` or
  `Info.plist`, especially when the app path is reused (same dist folder,
  overwritten in place). The script mitigates this by giving each build its
  own timestamped output directory and by running `xattr -cr` + `touch` on
  the finished bundle. If a stale icon still appears after installing a new
  build, tell the user to either (a) move/rename the `.app` once, or (b) run
  `killall Finder` and/or `qlmanage -r cache` and relaunch.
- **`CFBundleIdentifier` left as the placeholder default** — the script
  defaults to `com.example.<name>`, which is fine for local testing but
  should always be overridden with a real reverse-DNS identifier before
  distributing to anyone else (needed later for signing/notarization too).
- **Building the wrong product** — if `Package.swift` defines multiple
  executables, `--app-name` alone builds a product of that same name; use
  `--product` when the binary/product name differs from the desired app
  display name.
- **Running from the wrong directory** — the script requires `Package.swift`
  at the repo root it's given (`--repo-root`, defaults to cwd). If it errors
  with "no Package.swift found", cd to the repo root or pass `--repo-root`.
- **A build or `hdiutil` step fails partway** — the script exits non-zero,
  deletes the DMG staging folder, and removes the partially assembled
  timestamped output directory so no half-built `.app` is left looking
  distributable. Fix the cause and re-run; nothing needs cleaning by hand.
- **Distributing the unsigned DMG and getting "damaged" complaints** — this
  is expected Gatekeeper behavior for unsigned software, not a packaging bug.
  Point users to `references/signing-notarization.md` for both the
  right-click-to-open workaround and the real signing/notarization path.

## Resources

- `scripts/package_app.sh` — the packaging script described above.
- `assets/Info.plist.template` — parameterized plist consumed by the script
  (placeholders: `__APP_NAME__`, `__BUNDLE_ID__`, `__VERSION__`,
  `__MIN_MACOS_VERSION__`, `__LSUIELEMENT_BOOL__`, and an `@@ICON_BLOCK@@`
  marker line that expands to the `CFBundleIconFile` key/value pair or is
  dropped entirely when no icon is supplied). Placeholders are filled with
  XML-escaped, pre-validated values.
- `tests/` (repo root) — behavioral tests that run this script against
  stubbed `swift`/`hdiutil`/`plutil` and check rejected inputs, bundle
  layout, cleanup, and failure propagation.
- `references/signing-notarization.md` — what unsigned distribution means for
  end users, and the full codesign/notarytool/stapler upgrade path.
