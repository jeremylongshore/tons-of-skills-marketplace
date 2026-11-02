# Swift portability traps: passes locally, fails on CI

Catalog format per trap: **Symptom -> Cause -> Fix**. Each entry is
self-contained; skim for the symptom that matches, then read that section.

The first two entries were confirmed in a real project (2026-07) - not
theoretical - by comparing behavior across macOS 14 vs. newer runners. The
rest are well-documented, widely-hit traps included for completeness.

---

## 1. JSONDecoder `.iso8601` rejects fractional-second timestamps (VERIFIED)

**Symptom:** A JSON payload with timestamps like `"2026-07-10T10:00:00.000Z"`
decodes fine on your Mac and on newer CI runners, but on an older runner
(e.g. `macos-14` with an older swift-foundation) the same field throws
`DecodingError.dataCorrupted` or - worse - the whole record is silently
dropped by a `try?` / `compactMap` upstream, so tests fail with "expected 10
records, got 7" and no visible error.

**Cause:** `JSONDecoder.DateDecodingStrategy.iso8601` is backed by
`ISO8601DateFormatter` configured *without* `.withFractionalSeconds` on
older Foundation. A timestamp with milliseconds (`.000Z`) does not match
that formatter's expected format and fails to parse. Newer swift-foundation
versions are more lenient and accept both forms, which is exactly why this
bug is invisible locally (if your Mac has a newer Foundation/Xcode) and
newly-hired failures on CI where the runner image is older, or vice versa -
it can bite in either direction depending on which side is "older."

**Fix:** Never rely on the built-in `.iso8601` strategy when the data source
might include fractional seconds. Use a custom strategy that tries both
formatters:

```swift
extension JSONDecoder.DateDecodingStrategy {
    /// Accepts ISO 8601 timestamps with or without fractional seconds,
    /// unlike the built-in `.iso8601` strategy whose behavior differs
    /// across Foundation versions.
    static let iso8601Flexible = custom { decoder in
        let container = try decoder.singleValueContainer()
        let string = try container.decode(String.self)

        let withFractional = ISO8601DateFormatter()
        withFractional.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        if let date = withFractional.date(from: string) {
            return date
        }

        let withoutFractional = ISO8601DateFormatter()
        withoutFractional.formatOptions = [.withInternetDateTime]
        if let date = withoutFractional.date(from: string) {
            return date
        }

        throw DecodingError.dataCorruptedError(
            in: container,
            debugDescription: "Expected ISO8601 date string, got \(string)"
        )
    }
}

// Usage:
let decoder = JSONDecoder()
decoder.dateDecodingStrategy = .iso8601Flexible
```

**Test it:** add a fixture/unit test that decodes both
`"2026-07-10T10:00:00Z"` and `"2026-07-10T10:00:00.000Z"` explicitly. This
is cheap insurance and would have caught the real-world case that motivated
this catalog.

---

## 2. NumberFormatter grouping separator differs by locale/Foundation version (VERIFIED)

**Symptom:** A test asserts a formatted number equals `"9,876"`. It passes
on your Mac and fails on CI (or vice versa) with the actual value `"9876"`
- no comma, everything else about the formatter identical.

**Cause:** The formatter (or its locale) resolves to `en_US_POSIX`, which
by definition has **grouping size 0** - it does not insert thousands
separators regardless of `usesGroupingSeparator`. Some Foundation versions
apply `usesGroupingSeparator = true` more strictly than others when the
locale itself declares no grouping, so you can observe `"9876"` on one
Foundation version and `"9,876"` on another purely due to how strictly the
grouping-size-0 rule is enforced. `en_US_POSIX` is a common default in test
code because people reach for it as a "stable, locale-independent" choice
- it is stable, but it is stable at "no grouping," which is rarely what the
test author intended.

**Fix:** Never use `en_US_POSIX` (or any POSIX/C locale) when you need
grouped numeric output. Pin the formatter to a real locale that defines
grouping, and assert against that locale explicitly:

```swift
let formatter = NumberFormatter()
formatter.numberStyle = .decimal
formatter.usesGroupingSeparator = true
formatter.locale = Locale(identifier: "en_US")   // NOT en_US_POSIX
formatter.groupingSeparator = ","                // pin explicitly for tests

XCTAssertEqual(formatter.string(from: 9876), "9,876")
```

If the production code intentionally uses `en_US_POSIX` for something
else (e.g. stable machine-readable output, decimal-point parsing
independent of user locale), keep that usage but do not also expect grouped
output from it - the two goals conflict. Split into two formatters if both
behaviors are needed.

**Test it:** any test asserting an exact formatted-number string should
pin `formatter.locale` explicitly rather than depending on
`Locale.current` or `Locale(identifier: "en_US_POSIX")` and hoping for
grouping.

---

## 3. `Date()` / timezone-dependent assertions

**Symptom:** A test that computes "start of day" or "is this within the
last 24 hours" passes locally but fails on CI, or fails only near midnight
UTC / around DST transitions.

**Cause:** GitHub Actions runners are UTC by default; your dev machine is
whatever timezone you're in. Code (or tests) that use
`Calendar.current` / `TimeZone.current` implicitly depends on the
runner's system timezone, which is not the same as the developer's.
`Calendar.current.startOfDay(for:)`, day-of-week math, and "is today"
checks are the usual culprits.

**Fix:** Inject a fixed `Calendar`/`TimeZone` into the code under test
rather than reading `.current`; in tests, construct
`Calendar(identifier: .gregorian)` with an explicit `TimeZone(identifier:
"UTC")` (or whatever zone the test intends) instead of relying on the
ambient system zone. For "now"-dependent logic, inject a `Date` (or a
`() -> Date` clock) instead of calling `Date()` directly, so tests can pin
a fixed instant.

---

## 4. String sort order differs under different locales

**Symptom:** `["Zebra", "apple", "Ärger"].sorted()` (or a similar list
containing mixed case / diacritics) produces a different order locally
vs. on CI, or a snapshot/golden-file test of sorted output flips order
intermittently.

**Cause:** Plain `<` / `sorted()` on `String` uses Unicode scalar
ordering by default in some contexts but code that instead calls
`localizedCompare` / `localizedStandardCompare` (or `NSString` bridging,
which often does under the hood) depends on `Locale.current`. If
`Locale.current` differs between your machine and the CI runner (or if
CI has no user locale set), sort order for accented/mixed-case strings can
differ.

**Fix:** For deterministic tests, sort with an explicit ordering that does
not depend on locale (`sorted(by: <)` on scalar/UTF-8 view, or
`String.compare(_:options:)` with an explicit `Locale`) rather than
`localizedCompare`/`localizedStandardCompare` with the ambient locale. If
locale-aware sorting is the actual feature under test, pin the locale
explicitly (`string.compare(other, options: [], range: nil, locale:
Locale(identifier: "en_US"))`) instead of relying on `Locale.current`.

---

## 5. Hardcoded `/Users/...` paths

**Symptom:** A test or script works on the developer's Mac and fails on
CI with "file not found," referencing a path like
`/Users/yourname/Developer/project/fixtures/...`.

**Cause:** An absolute path was hardcoded (often pasted from Xcode's
"Copy Path" or a debugger) instead of being derived relative to the
source file, the package root, or a bundled resource. CI runners use a
different home directory and checkout path (typically
`/Users/runner/work/<repo>/<repo>` on macOS runners).

**Fix:** Never hardcode absolute paths in source or tests. Use
`#filePath`/`#file` to derive a path relative to the test file, or use
`Bundle.module` for packaged resources (see trap 7), or read from an
environment variable set explicitly by CI/local scripts. If a script
needs the repo root, derive it (`git rev-parse --show-toplevel`) rather
than hardcoding it.

---

## 6. Filesystem case-sensitivity assumptions

**Symptom:** A file reference like `import "Config.JSON"` or a path
comparison that mixes case works locally (macOS default is
case-insensitive but case-preserving APFS) and fails on a case-sensitive
runner or a case-sensitive APFS volume, with "file not found" despite the
file visibly being there.

**Cause:** Default macOS volumes are case-insensitive, so
`readme.MD` and `README.md` resolve to the same file locally. Some CI
runners, Docker-based Linux jobs, or explicitly-configured case-sensitive
APFS volumes are not forgiving of this. Git itself is also
case-sensitive in its index even on a case-insensitive filesystem, which
can cause a related but distinct class of bugs (two files differing only
in case both existing in the repo).

**Fix:** Always match filename case exactly in source, `Package.swift`
resource declarations, and import/include statements. Don't rely on
case-insensitive resolution as a matter of style, even where the local
filesystem tolerates it.

---

## 7. `Bundle.module` resource paths in tests

**Symptom:** A test that loads a bundled resource (fixture JSON, image,
etc.) via `Bundle.module` works when run from Xcode but fails under
`swift test` on CI (or vice versa), with "resource not found in bundle."

**Cause:** `Bundle.module` resolution depends on how the package was
built and where the generated resource bundle ends up (SwiftPM
synthesizes this per-target, and its output location can differ between
an Xcode-managed build and a plain `swift build`/`swift test` invocation,
especially across Swift toolchain versions). If a resource isn't declared
in `Package.swift`'s `resources:` for the right target, or the target
mixes up test-resource vs. main-resource bundles, it may resolve locally
by accident (e.g. stale build artifacts) and fail cleanly on a fresh CI
checkout.

**Fix:** Explicitly declare all test fixtures under the test target's
`resources:` in `Package.swift` (`.copy` or `.process` as appropriate),
and always start CI from a clean checkout/build so accidental local-only
resolution can't mask the problem. When debugging, print
`Bundle.module.bundlePath` and `Bundle.module.paths(forResourcesOfType:
inDirectory:)` to see what's actually resolved on each machine.

---

## 8. `Decimal`/`Double` string description differences

**Symptom:** A test asserts `String(describing: someDecimal)` or
`"\(someDouble)"` equals an exact string, and the trailing digits or
exponent formatting differ between Foundation versions or platforms
(e.g. `"0.1"` vs `"0.10000000000000001"`, or differing rounding in
`Decimal`'s string conversion).

**Cause:** `Double`'s and `Decimal`'s default string conversions are not
guaranteed byte-stable across Swift/Foundation versions - internal
formatting algorithms (shortest round-trippable representation vs. fixed
precision) have changed between releases, and `Decimal` in particular has
had known cross-version differences in its `description`/
`NSDecimalNumber` bridging behavior.

**Fix:** Never assert exact string equality on a floating-point or
`Decimal` description. Compare numeric values directly
(`XCTAssertEqual(a, b, accuracy: 0.0001)` for `Double`, or `Decimal`
equality) and, if a formatted string genuinely needs to be asserted, use
an explicit `NumberFormatter`/`FloatingPointFormatStyle` with pinned
locale and precision (see trap 2) instead of the default description.

---

## General debugging methodology for "works locally, fails on CI"

When a test fails on CI but not locally (or the reverse), don't guess -
gather environment facts first, on both sides, then narrow:

1. **Print the environment on CI** (the `ci.yml.template` in `assets/`
   already does this): `swift --version`, `xcodebuild -version`,
   current locale (`defaults read -g AppleLocale`), timezone (`date +%Z`),
   and OS version (`sw_vers`). Compare against the same output run
   locally.

2. **Reproduce the CI environment locally** rather than staring at logs:
   - Strip your shell environment: `env -i HOME=$HOME PATH=/usr/bin:/bin swift test`
     removes inherited env vars (locale, custom `TZ`, etc.) that might be
     masking or causing the bug.
   - Force a specific locale: `LANG=C.UTF-8 LC_ALL=en_US_POSIX swift test`
     (or whatever locale CI actually resolves to) to reproduce
     locale-dependent formatting bugs like trap 2 without needing CI
     access.
   - Force a specific timezone: `TZ=UTC swift test` to reproduce
     timezone-dependent bugs like trap 3.
   - If the failure is Xcode/Foundation-version-specific, install the
     older/newer Xcode via `xcodes` and re-run with
     `sudo xcode-select -s /Applications/Xcode_<version>.app` to match the
     CI runner's toolchain exactly rather than guessing from your primary
     Xcode install.

3. **Bisect by runner/matrix row**: if you already run the matrix job in
   `ci.yml.template`, the failure pattern across rows (fails only on
   macos-13, or only on the newest Xcode) directly tells you whether it's
   an "older Foundation" or "newer Foundation" trap, which narrows the
   catalog search above immediately.

4. **Once reproduced locally, fix at the narrowest layer**: prefer fixing
   the actual code (custom date/number strategies, explicit locale/TZ
   injection) over papering over it with `#if os(...)` / runner-specific
   skips - the latter just defers the bug to whichever environment you
   didn't test.
