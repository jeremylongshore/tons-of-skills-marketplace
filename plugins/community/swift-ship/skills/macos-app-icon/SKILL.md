---
name: macos-app-icon
description: Generates a complete macOS .icns app icon file from a single source image (SVG or PNG at least 1024px). Use when asked to create/build/generate a macOS app icon, .icns file, AppIcon, iconset, or to fix a blurry/missing/wrong-size app icon, or to wire an icon into an Xcode project or app bundle. Also covers menu bar / status bar icon requirements (separate from .icns). Trigger with "/macos-app-icon".
allowed-tools: Read, Write, Bash(qlmanage:*), Bash(sips:*), Bash(iconutil:*), Bash(file:*)
version: 1.1.0
author: chsistrying
license: MIT
compatibility: Requires macOS with qlmanage, sips, and iconutil (all ship with macOS; no third-party install needed).
tags: [macos, icon, icns, swift, design]
---

# macOS App Icon Generator

## Overview

Build a macOS `.icns` app icon from one source image (SVG or PNG), and wire it
into an app. A `.icns` file packs all ten required icon sizes (16px through
1024px, @1x and @2x) into the single artifact macOS expects in an app bundle.

## Prerequisites

- macOS with `qlmanage`, `sips`, `iconutil`, and `file` — all ship with the OS,
  nothing to install.
- A square source image: SVG, or PNG at least 1024x1024.

## Instructions

Quick start — run the bundled script:

```bash
scripts/make_icns.sh <input-image> <output.icns>
```

The script:
1. Validates required tools (`sips`, `iconutil`, `file`) and the input file.
2. If input is `.svg`, renders it to a 1024px PNG via `qlmanage`.
3. If input is `.png`, uses it directly (warns if smaller than 1024px or non-square).
4. Generates all required sizes into a temp `.iconset` folder.
5. Compiles the `.iconset` into `.icns` via `iconutil`.
6. Cleans up the temp folder and prints the final `file` output to confirm validity.

Run it with no args (or `-h`) for usage help.

## Examples

```bash
# SVG source, output next to it
scripts/make_icns.sh AppIcon.svg AppIcon.icns

# 1024px PNG source, output into a build directory
scripts/make_icns.sh artwork_1024.png build/AppIcon.icns
```

## Output

A valid `.icns` file at the path you specified, confirmed by `file` reporting
`Mac OS X icon`. Intermediate `.iconset` folders are cleaned up automatically.
Wire the result into an app via the sections below.

## Manual workflow (no script)

If you need to do this by hand or the script is unavailable, run the exact
commands below.

**1. Get a 1024x1024 PNG.**

From SVG:

```bash
qlmanage -t -s 1024 -o /tmp/icon_render AppIcon.svg
# writes /tmp/icon_render/AppIcon.svg.png
```

From an existing PNG >= 1024px, just use it as-is.

**2. Create the iconset folder and generate every required size:**

```bash
mkdir icon.iconset
SRC=source_1024.png

sips -z 16 16     "$SRC" --out icon.iconset/icon_16x16.png
sips -z 32 32     "$SRC" --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     "$SRC" --out icon.iconset/icon_32x32.png
sips -z 64 64     "$SRC" --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   "$SRC" --out icon.iconset/icon_128x128.png
sips -z 256 256   "$SRC" --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   "$SRC" --out icon.iconset/icon_256x256.png
sips -z 512 512   "$SRC" --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   "$SRC" --out icon.iconset/icon_512x512.png
sips -z 1024 1024 "$SRC" --out icon.iconset/icon_512x512@2x.png
```

**3. Compile to .icns:**

```bash
iconutil -c icns icon.iconset -o AppIcon.icns
rm -rf icon.iconset
```

**4. Verify:**

```bash
file AppIcon.icns
# expect: "AppIcon.icns: Mac OS X icon, ..."
```

## Design guidance

- Source artwork should be square. macOS renders icons inside a rounded-rect
  "squircle" mask automatically for most contexts — **do not** pre-mask/round
  the corners yourself, or you'll get double-masking artifacts.
- Leave roughly a 10% transparent margin around the visual content (i.e. the
  drawn artwork occupies about the center 80–90% of the 1024x1024 canvas).
  Icons that bleed to the edge look oversized next to system icons.
- Prefer a source >= 1024x1024 so the largest size (`icon_512x512@2x.png`,
  itself 1024x1024) isn't upscaled.
- Flatten the SVG (embed/inline any linked images, fonts, or `<use href>`
  external refs) before rendering — see Edge Cases below.

## Wiring the icon into an app

**Xcode asset catalog (typical app target):**
1. Open `Assets.xcassets` in Xcode, add an "App Icon" image set (or use the
   existing `AppIcon` set already scaffolded by most templates).
2. Drag `AppIcon.icns` onto the asset slot — Xcode auto-extracts the sizes it
   needs (modern Xcode also accepts a single 1024px PNG directly instead of
   an `.icns`, via the "single size" App Icon set style).
3. Ensure the target's Build Settings > "Asset Catalog App Icon Set Name" is
   set to that asset set's name (default `AppIcon`).

**Raw bundle (no Xcode asset catalog, e.g. a hand-built `.app` or a CLI-built
bundle):**
1. Copy `AppIcon.icns` into `YourApp.app/Contents/Resources/`.
2. In `Contents/Info.plist`, set:
   ```xml
   <key>CFBundleIconFile</key>
   <string>AppIcon</string>
   ```
   (Omit the `.icns` extension — `CFBundleIconFile` implies it. Filename must
   match exactly, case-sensitive.)
3. Re-sign/re-bundle as needed, then refresh the icon cache (see Edge Cases).

## Menu bar / status bar icons are NOT the .icns

Menu bar (`NSStatusItem`) icons are a completely separate asset from the app
icon:
- They should be small template images (typically 18x18pt @1x/@2x/@3x, or an
  SF Symbol), rendered in monochrome and automatically tinted/inverted by the
  system for light/dark mode and selection states.
- Set `image.isTemplate = true` on the `NSImage` (or use an asset catalog
  image marked "Render As: Template Image").
- Prefer an SF Symbol (`NSImage(systemSymbolName:accessibilityDescription:)`)
  when a suitable one exists — it inherits correct weight/scale for free.
- Do **not** hand it a full-color, multi-size `.icns` — it will not adapt to
  dark mode or menu bar height and will look out of place next to system
  icons.

## Edge cases

- **Non-square source.** `sips -z H W` scales width/height independently, so
  a non-square source gets stretched/distorted. Pad to a square canvas
  first (e.g. in the design tool, or via `sips --padToHeightWidth`) rather
  than feeding it directly.
- **Source smaller than 1024px.** The largest iconset entries (512, 512@2x =
  1024px) will be upscaled and look soft. Get a bigger source, or accept
  the blur if the icon is only ever shown small.
- **SVG with external references renders blank.** `qlmanage`'s QuickLook
  renderer runs sandboxed and often cannot resolve `<image href="...">`,
  external fonts, or `<use xlink:href="external.svg#id">`. Symptom: the
  rendered PNG is fully transparent/blank even though the SVG looks correct
  in a browser. Fix: inline/flatten all external references in the SVG (or
  export a PNG directly from the design tool — Figma/Illustrator/Sketch
  "Export as PNG @1024px" — and skip `qlmanage` entirely).
- **Icon doesn't update after replacing it (Gatekeeper / icon cache).**
  macOS aggressively caches app icons. After swapping `AppIcon.icns` or
  rebuilding an unsigned/dev app:
  ```bash
  touch YourApp.app
  killall Finder
  # if still stale:
  qlmanage -r cache
  killall Dock
  ```
  For unsigned/ad-hoc-signed builds during development, a full re-copy of
  the `.app` to a new path (or `mv` it) often forces Finder to re-read the
  icon rather than reuse a cached one keyed by the old inode/path. Do not
  delete system cache directories under `/Library/Caches` to force a
  refresh; the steps above are enough, and a stale icon is cosmetic.
- **iconutil fails with "not a valid iconset."** Usually means a required
  filename is missing or misnamed (must exactly match
  `icon_16x16.png`, `icon_16x16@2x.png`, ... `icon_512x512@2x.png`) or the
  folder isn't named `*.iconset`. Re-check the `ls` output against the size
  list above.
- **`file` doesn't show "Mac OS X icon."** If `file AppIcon.icns` doesn't
  report it as an icon, `iconutil` silently wrote something else or failed —
  re-run with a fresh iconset folder rather than reusing a partially-built one.

## Resources

- `scripts/make_icns.sh` — the end-to-end generator described above.
- [Apple HIG: App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons) — sizing, margins, and squircle guidance.
- [Apple docs: `iconutil`](https://developer.apple.com/library/archive/documentation/GraphicsAnimation/Conceptual/HighResolutionOSX/Optimizing/Optimizing.html) — iconset naming requirements.
