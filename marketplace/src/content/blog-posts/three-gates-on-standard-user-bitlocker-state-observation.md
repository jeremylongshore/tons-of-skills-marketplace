---
title: "Three Gates on Standard-User BitLocker State Observation"
description: "Standard-user BitLocker state observation has three gates. A Codex audit caught the third one on three failure modes; two were the kind it was built to find."
date: "2026-09-13"
tags: ["windows", "security", "bitlocker", "go", "fail-closed", "code-review", "ai-augmented-engineering"]
featured: false
canonical: "https://startaitools.com/posts/three-gates-on-standard-user-bitlocker-state-observation/"
---
## The day started with a P1 on merge day

Closing intent-blue-gold Epic 1+2 was supposed to be the easy part. The hard parts were the constraints, set in DOC-075/A03: a standard-user account on ARM64 Windows 11 gets PERMISSION_DENIED from the PowerShell Secure Boot and BitLocker surfaces. WMI is out. COM is out. Elevation is out. Anything that requires a privileged token is out. Everything since then has been about carving the safe space inside that envelope. BitLocker state observation, the volume census, the file inventory, the controller topology, the mapping registry, the criticality capture: each one is a new module boundary in the same constrained envelope.

I ran Codex (GPT-5.6 Sol) read-only against the day's merge candidates on purpose. Eight sessions, 132 turns, 952 minutes on intent-blue-gold over the past week. The audit was not a polish pass. It was a closure gate. It surfaced three P1 blockers. Two of them were exactly the kind of failure the audit exists to catch.

The three gates that have to hold together are: the observer contract, the bounded native provider, and the fixture-boundary authorization. Gate 3 was the one that slipped. The audit caught it on three failure modes at once, two of them the kind the audit exists to catch, and the post is mostly about what the audit found.

## Gate 1: the observer contract

The observer contract is the seam between the constrained envelope and any code that wants to read BitLocker state. Anything that talks to `GetFveLogicalVolumeInformation`-equivalent surfaces has to enter through this contract. Here is the seam in Go.

```go
// BitlockerObserver is the standard-user entry point. It returns
// State with the OBSERVED bit set only when the call ran through
// the helper, the helper authenticated, and the fixture boundary
// held. Anything else is OBSERVED=false, even if the bytes look
// reasonable.
type BitlockerObserver interface {
    Observe(ctx context.Context, vol VolumeRef) (State, error)
}

// State has three meaningful bits:
// OBSERVED  = we ran the native probe and got a result
// CACHED    = we have a non-stale prior observation for this vol
// UNAVAIL  = the probe ran but the OS returned access denied or
//            empty; we treat that as no information, not as "off"
type State struct {
    Volume    VolumeRef
    Status    string // protect_state strings, NOT raw OS bytes
    Observed  bool
    Cached    bool
    Unavail   bool
    Source    ProbeSource
}
```

The interesting bit is `Observed`. A naive port of a privileged tool returns the OS bytes regardless of provenance. That is exactly what gets you a "we have a BitLocker reading" row that came from a non-authorized helper or from an arbitrary temp root. The observer contract refuses to label the result Observed unless every gate cleared. The byte string is still in `Status`, but downstream code is supposed to ignore `Status` when `Observed` is false. That is the contract.

## Gate 2: the bounded native provider

Gate 2 is the provider that does the actual syscall. Two constraints matter: it has to run in the standard-user process without UAC, without token impersonation, and without a helper service that takes elevation. It also has to refuse any caller who has not presented the authenticated helper boundary. The provider entry point.

```go
func (p *NativeProvider) QueryVolume(ctx context.Context, vol VolumeRef) (State, error) {
    if !p.helperBoundary.Authorized(vol) {
        // Fail closed: an unauthorized caller gets the same answer
        // they would get from an unauthenticated probe. No detail,
        // no exception type, no "near miss" leak.
        return State{Volume: vol, Unavail: true}, ErrBoundaryClosed
    }
    if !vol.IsFixtureAuthorized() {
        // The fixture boundary: even an authenticated helper can
        // not cross outside the manifest-verified fixture. This
        // is gate 3, but we enforce it at the provider entry to
        // avoid a second code path that needs the same guarantee.
        return State{Volume: vol, Unavail: true}, ErrOutsideFixture
    }
    return p.queryViaSyscall(ctx, vol)
}
```

`queryViaSyscall` is the boring part. `FsctlEnumerateVolumeInformation` with a `BITLOCKER_INFORMATION` header, `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS` for layout, fall through to the registry path when the helper IPC returned access denied. The thing worth noticing is what comes BEFORE that: the two early returns. An unauthorized caller and an out-of-fixture caller both get `Unavail: true` with `Observed: false`. They get the same answer a probe that genuinely failed would have given. There is no signal that says "we are not telling you because of X."

That is fail-closed by construction. The audit did not flag this gate.

## Gate 3: the fixture-boundary authorization (the failure)

Gate 3 was the failure. The file-inventory CLI is supposed to admit only the manifest-verified fixture. The fixture is a checked-in blob with a hash pinned in `fixture.manifest`. Anything else is a synthetic root, and synthetic roots are test-only. The CLI was supposed to refuse a synthetic root at admission. Here is what the gate looks like.

```go
// Authorized root check. The CLI calls this before any work.
func (a *FixtureAuth) Authorize(root string) error {
    manifest, err := LoadManifest()
    if err != nil {
        return err // no manifest, no authorization, fail closed
    }
    pinned := manifest.CanonicalRoot()
    if !pathEqual(root, pinned) {
        // Synthetic roots are valid in tests, but the production
        // CLI is not a test. Production admission refuses them.
        return ErrSyntheticRootRejected
    }
    if !manifest.HashMatches(root) {
        // The pinned root is the right path but the bytes don't
        // match. That is a fixture drift, also a hard refusal.
        return ErrFixtureDrift
    }
    return nil
}
```

That is what the code is supposed to do. Codex found that `prototypes/blue-windows/cmd/file-inventory/main.go:54-76` accepts any directory containing a user-created marker and then scans its `Desktop`, `Documents`, `Downloads`, and `Pictures` children. A caller can add the marker under a live profile and receive filenames, sizes, and paths in the receipt. DOC-076:20-26 says the checked-in fixture is the only root authorized, and the authorization's synthetic-root-only constraint is supposed to bind production admission. The code did not bind it. The CLI was test-friendly and production-broken in the same binary.

The minimal fix is to call `FixtureAuth.Authorize` from `main.go:54-76` before any traversal. The CLI keeps its test ergonomics because the test harness can register a synthetic root with the test-only `RegisterSynthetic` hook, but the production binary refuses anything except the canonical fixture or a manifest-verified immutable fixture. That is what is shipping today. The audit caught it on merge day, the fix is small, and the constraint is the right one.

## The TOCTOU reparse replacement (gate 3, the second finding)

The same audit flagged a separate failure in `scan.go:185-216`: path-based `ReadDir`, `Lstat`, then recursive `ReadDir`. A validated directory can be swapped for a reparse point mid-traversal. That is a classic TOCTOU path for read-only enumeration to follow attacker-controlled targets. The standard fix on Linux is `O_DIRECTORY | O_NOFOLLOW`, then keep the file descriptor and enumerate from it. On Windows the equivalent is to open with `FILE_FLAG_OPEN_REPARSE_POINT` and the standard share-mode set, capture the handle, and re-validate the reparse status from the handle before walking into children. The sketch:

```go
// Linux side: open the directory once, hold the fd, refuse to walk
// a reparse change observed post-open.
fd, err := unix.Open(path, unix.O_RDONLY|unix.O_DIRECTORY|unix.O_NOFOLLOW, 0)
if err != nil { return err }
defer unix.Close(fd)
// Snapshot the reparse status at open time, then compare against
// each entry's d_type before deciding to descend. (The full
// re-validation lives in the production helper; the sketch is the
// shape, not the implementation.)
entries, err := unix.Getdents(fd)
```

The Windows side is heavier (handle capture plus `DeviceIoControl(FSCTL_GET_REPARSE_POINT)` per candidate), but the principle is the same: validate once, keep the handle, refuse a reparse change observed after open. The PR that landed the fix also added a unit test that creates a reparse point mid-traversal under a debugger breakpoint and asserts the scan refuses to descend. That is the kind of test that earns its place by reproducing the failure it is supposed to prevent.

## The non-reparse offline file (the stale classifier, gate 3 by association)

The third finding is closer to a stale classifier than a security boundary failure, but it is still P1 because the classifier decides what downstream code does with the result. `prototypes/blue-windows/cloudstate/observe_windows.go:41-42` returns `StateLocal` whenever `FILE_ATTRIBUTE_REPARSE_POINT` is absent. The `OFFLINE`, `RECALL_ON_OPEN`, and `RECALL_ON_DATA_ACCESS` flags are examined later in `classifyWindowsState` at lines 73-74, which is unreachable for non-reparse files. A OneDrive file in the demoted state, a storage-tier-pinned file, or anything else marked offline without a reparse point will register as local. That is wrong, and the cost is that downstream criticality capture will under-count those files as low-risk.

The fix is to evaluate the offline/recall mask before the non-reparse `StateLocal` return. A non-reparse file with `FILE_ATTRIBUTE_OFFLINE` should classify as `CLOUD_ONLY` (or `UNKNOWN/unavailable` if we want to be conservative on recall flags we cannot yet test on every Windows SKU). The native probe needs a regression test for a non-reparse offline file. That is also shipping today.

## Why not the obvious approach?

The obvious approach for standard-user state observation is to shell out to `manage-bde -status` and parse the text. That is what every PowerShell script in the wild does. It works on a privileged user. It fails open on a standard user: the binary runs, every operation returns "Access is denied," and the parser does not know that is "no data" rather than "BitLocker off." The classifier ends up reporting everything as off.

The other obvious approach is to elevate. `manage-bde` is the right tool for the privileged envelope. Elevation is not available here. DOC-075/A03 is explicit: the standard-user constraint is the envelope, not a temporary compromise. WMI stays out. COM stays out. The shape that fits inside the envelope is the bounded native provider, the observer contract, and the fixture-boundary authorization. They are less convenient than `manage-bde`. They are what works inside the envelope.

## Adjacent finding on the NVMe health-log parser

The audit surfaced a separate bug in the NVMe health-log parser. The parser used wrong offsets: bytes 160-175 instead of 176-191. `NVME_HEALTH_INFO_LOG` places UnsafeShutdowns at 160-175 and MediaErrors at 176-191, and the parser was rejecting every byte from 216 onward (which is also where valid sensors 7 and 8 live). Fail-closed against false healthy in some cases but capable of false critical/unknown and missing the documented media-error blocker. Not a P1 for this epic, but it is the next bead.

## Also shipped

Other repos did work today, briefly:

- **omarchy-plugins-bluegold-email-fix**: closed FAQ panels 35 and 36, the adversarial buyer FAQ set. Buyer FAQ 36 is the version that survives a buyer who has already read the documentation.
- **intent-solutions-landing-bluegold-faq**: shipped v3.2.0 with a mobile conversion baseline (PR #54). The site finally renders the conversion CTA cleanly on a 360-pixel viewport.
- **intent-demos**: launched the proof-first demos catalog (fd6198e) and fixed site previews on touch screens (6dc710d).
- **contributing-clanker**: closed regression-state isolation and review-synthetic-alert tolerance fixes (#78 and #79).
- **jeremylongshore-dot-github**: bound VPS deploys to the caller revision (#5). Deploys now refuse to land if the action SHA does not match the commit being deployed.
- **omarchy-listening-post-entry**: recorded approvals and bound deploy revisions (#19), launched the Perception product foundation (#18).
- **braves**: a beads sync remote update only.

None of those are the day's center. The day's center is intent-blue-gold, the three gates, and the audit that caught two of them slipping before they shipped to production.

## Related posts

- [Auditing Written Claims Against Their Artifacts]({{< ref "the-second-review-that-audits-the-claims.md" >}}): the second-review pattern across two unrelated domains. Today's Codex audit instantiates it on the BitLocker surface.
- [Sealing a 168-bead planning graph took three reviews and a seven-seat council]({{< ref "sealing-a-168-bead-planning-graph-took-three-reviews-and-a-seven-seat-council.md" >}}): planning under multi-review pressure, the day before.
- [Adversarial review before team rollout]({{< ref "adversarial-review-before-team-rollout.md" >}}): the adversarial pattern that the Codex audit instantiates on this surface.
