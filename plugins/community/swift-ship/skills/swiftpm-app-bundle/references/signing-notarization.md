# Signing & Notarization

## What "unsigned" means for your users

`package_app.sh` produces an **unsigned** `.app` / `.dmg`. macOS Gatekeeper will
block a normal double-click launch of unsigned software downloaded from the
internet ("cannot be opened because the developer cannot be verified" or
"is damaged and can't be opened").

Tell your users to do one of the following instead of double-clicking:

1. **Right-click (or Control-click) the app → Open → Open**, in the dialog
   that appears. This bypasses Gatekeeper for that one app, once.
2. Or, from Terminal, remove the quarantine attribute after mounting the DMG:
   ```bash
   xattr -dr com.apple.quarantine /Applications/YourApp.app
   ```
3. As a last resort: System Settings → Privacy & Security → scroll to the
   bottom → "Open Anyway" (appears after a blocked launch attempt).

This is expected, normal friction for unsigned indie/hobby distribution and is
not a bug in the packaging script.

## Upgrade path: signing + notarization

Everything below **requires an active, paid Apple Developer Program
membership** ($99/year) and a "Developer ID Application" certificate. It is
not available on a free Apple ID.

### 1. Get a Developer ID Application certificate

Create it in Xcode (Settings → Accounts → Manage Certificates → "+" →
"Developer ID Application") or via the Apple Developer portal, then ensure it
is installed in your login Keychain.

### 2. Codesign the app bundle

Sign with the hardened runtime enabled (required for notarization):

```bash
codesign --force --deep --timestamp \
  --options runtime \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  /path/to/YourApp.app
```

Verify:

```bash
codesign --verify --deep --strict --verbose=2 /path/to/YourApp.app
spctl --assess --type execute --verbose /path/to/YourApp.app
```

If your app needs entitlements (e.g. network access sandboxing, no sandbox at
all for a plain distributed app, etc.), pass `--entitlements YourApp.entitlements`.

### 3. Build the DMG, then sign it too (optional but recommended)

```bash
codesign --force --timestamp \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  /path/to/YourApp.dmg
```

### 4. Submit for notarization

```bash
xcrun notarytool submit /path/to/YourApp.dmg \
  --apple-id "you@example.com" \
  --team-id "TEAMID" \
  --password "app-specific-password" \
  --wait
```

Use an [app-specific password](https://support.apple.com/en-us/102654), not
your normal Apple ID password. Prefer storing credentials in a keychain
profile once and referencing it by name:

```bash
xcrun notarytool store-credentials "notary-profile" \
  --apple-id "you@example.com" --team-id "TEAMID" --password "app-specific-password"

xcrun notarytool submit /path/to/YourApp.dmg --keychain-profile "notary-profile" --wait
```

If notarization fails, inspect the log:

```bash
xcrun notarytool log <submission-id> --keychain-profile "notary-profile"
```

### 5. Staple the notarization ticket

Stapling embeds the approval in the artifact so Gatekeeper can validate it
offline (no network call needed at first launch):

```bash
xcrun stapler staple /path/to/YourApp.dmg
xcrun stapler validate /path/to/YourApp.dmg
```

With a signed, notarized, stapled DMG, users can double-click normally with
no Gatekeeper warning.
