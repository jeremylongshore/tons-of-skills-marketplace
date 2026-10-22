/**
 * journal.ts — Tamper-evident audit journal for the Slack↔Claude-Code bridge.
 *
 * This file is the Epic 30-A entry point. Scope of this bead (ccsc-5pi.1)
 * is narrow: the `JournalEvent` schema and its inferred type. The writer,
 * redaction module, canonical-JSON serializer, and verification command
 * land in sibling beads (ccsc-5pi.2 – ccsc-5pi.16). See
 * 000-docs/audit-journal-architecture.md for the full contract.
 *
 * Shape of a journal event (audit-journal-architecture.md §19-59):
 *
 *   {
 *     v:        1,                          // schema version; chain refuses mixed versions
 *     ts:       '2026-04-19T12:34:56.789Z', // ISO-8601 UTC with ms precision
 *     seq:      42,                         // monotonic per chain
 *     kind:     'gate.inbound.drop',        // discriminated union of 37 event kinds
 *     toolName?: 'reply',
 *     input?:   { chat_id: 'C01', text: '...' },     // post-redaction
 *     outcome?: 'allow' | 'deny' | 'require' | 'drop' | 'n/a',
 *     reason?:  'peer bot not in allowFrom',
 *     ruleId?:  'no-exfil-to-untrusted-channel',
 *     sessionKey?: { channel: 'C01', thread: '1711000000.000100' },
 *     actor?:   'session_owner' | 'claude_process' | ...,
 *     correlationId?: 'req-abc123',
 *     prevHash: 'e3b0c44...',                // sha256 hex, 64 chars
 *     hash:     'b94d27b...',                // sha256 hex, 64 chars
 *   }
 *
 * Why `strict()` on the schema: the chain property depends on every writer
 * and every verifier hashing the **same bytes**. Accepting unknown fields
 * would let callers sneak unredacted content through the writer's redactor
 * (which only walks the documented fields). Strict mode surfaces those
 * mistakes at build time or on the first `parse()` call.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

import { createHash, randomBytes } from 'node:crypto'
import { type FileHandle, open as fsOpen, readFile } from 'node:fs/promises'
import { z } from 'zod'
import { type Ed25519KeyPair, signBytes, verifySignatureBytes } from './crypto.ts'
import type { SessionKey } from './lib'

// ---------------------------------------------------------------------------
// Event kinds — discriminated union tag
// ---------------------------------------------------------------------------

/** Every security-relevant event the journal records. Pinned by
 *  000-docs/audit-journal-architecture.md §40-59; adding a new kind is an
 *  intentional schema change and should be justified in a design-doc PR
 *  before the code PR.
 *
 *  Grouping (for the reader, not enforced):
 *    - `gate.*`        inbound/outbound gate decisions (lib.ts)
 *    - `policy.*`      evaluator decisions + approval flow (policy.ts)
 *    - `exfil.block`   `assertSendable()` refusal
 *    - `session.*`     supervisor lifecycle transitions (supervisor.ts)
 *    - `pairing.*`     DM-pairing state machine (access.json)
 *    - `system.*`      boot, shutdown, rotation
 */
export const EventKind = z.enum([
  'gate.inbound.deliver',
  'gate.inbound.drop',
  'gate.outbound.allow',
  'gate.outbound.deny',
  'policy.allow',
  'policy.deny',
  // Emitted immediately after `policy.deny` (ccsc-06s) to record that the
  // dispatcher minimised the response delivered to Claude — i.e., the MCP
  // notification carried only `behavior: 'deny'` with no rule id, no
  // reason, no input echo. The full denial detail remains in the
  // preceding `policy.deny` event for forensic review; the agent context
  // sees only that the call was denied. Order-of-operations invariant:
  // `policy.deny` is fully journaled BEFORE this event is written, and
  // both are journaled BEFORE the MCP notification is sent.
  'policy.deny.context_stripped',
  'policy.require',
  'policy.approved',
  'exfil.block',
  'session.activate',
  'session.quiesce',
  'session.deactivate',
  'session.quarantine',
  // Global backpressure: a NEW activation refused because the supervisor is at
  // its maxConcurrentSessions cap (ccsc-4e9bf). Records the load-shed decision.
  'session.activate_rejected',
  // Boot-time crash recovery (ccsc-o7x.1.2). `recoverOnStartup()` emits one
  // event per session with a persisted in-flight-turn marker: `.requeued` when
  // the marker's heartbeat has lapsed (owner provably dead → the marker is
  // cleared and the session is left re-activatable); `.orphaned` when the
  // marker is still fresh (a second live owner cannot be ruled out → the key is
  // quarantined, fail closed) or the file could not be read.
  'session.recovery.requeued',
  'session.recovery.orphaned',
  'pairing.issued',
  'pairing.accepted',
  'pairing.expired',
  'system.boot',
  'system.shutdown',
  'system.reload',
  // Journal v2 (ccsc-22l). Emitted under the OLD key at the moment of
  // key rotation; body carries old_public_key + new_public_key + reason.
  // The verifier MUST use the old key to verify this event and then
  // switch to new_public_key for every subsequent event. See
  // 000-docs/key-management.md § Rotation.
  'system.key_rotation',
  // Stream finalize (ccsc-ele). Emitted exactly once per logical
  // stream after the last chat.update lands. Carries the
  // pre-committed full-text hash + chunks_sent count. The single
  // gate.outbound.allow at stream start + this finalize event are
  // the ONLY journal entries per stream — no per-chunk events
  // (would cause O(n²) canonicalize cost on the chain). See
  // 000-docs/audit-journal-architecture.md § Streaming reply.
  'system.stream_finalize',
  // Admin verbs (ccsc-3w0). Emitted on every operator-initiated
  // admin command — !clear (reversible) and !restart (destructive,
  // nonce-gated). See admin.ts dispatcher and ACCESS.md § HMAC nonce.
  // The .denied variants record refused attempts (allowlist miss,
  // nonce verification failure). The .challenge variant records that
  // a nonce was minted + DM'd to the operator — without recording the
  // nonce itself (journal-read attacker would otherwise have a free
  // replay credential).
  'admin.clear',
  'admin.clear.denied',
  'admin.restart',
  'admin.restart.denied',
  'admin.restart.challenge',
  // Mute / unmute verbs (ccsc-gjm — multi-agent epic). Operator
  // silences a specific peer bot in a channel for a TTL (default 5
  // min). The mute store is in-memory; restart clears all mutes.
  // Counterpart admin.unmute provides early release. .denied
  // variants record allowlist misses / mute-store-not-configured
  // failures.
  'admin.mute',
  'admin.mute.denied',
  'admin.unmute',
  'admin.unmute.denied',
  // Bot-manifest protocol (Epic 31-A). Emitted on every read_peer_manifests
  // call so manifest activity is forensically visible even when cached;
  // see 000-docs/bot-manifest-protocol.md §163-166.
  'manifest.read',
  'manifest.read.cached',
  // Publisher side (Epic 31-B, ccsc-0qk.1/0qk.3). Emitted after a successful
  // publish_manifest call, carrying the replaced-count so operators can see
  // how many prior manifests were unpinned during the replace sweep.
  'manifest.publish',
])

/** TypeScript string union of the 37 event kinds. */
export type EventKind = z.infer<typeof EventKind>

// ---------------------------------------------------------------------------
// Supporting enums
// ---------------------------------------------------------------------------

/** Outcome of a gated action. `n/a` is the legitimate value for events
 *  that are observational rather than decision-emitting (e.g.
 *  `system.boot`, `session.activate`). Keep this set tight so the
 *  verification tool can normalize cleanly. */
export const Outcome = z.enum(['allow', 'deny', 'require', 'drop', 'n/a'])
export type Outcome = z.infer<typeof Outcome>

/** Who initiated or owns the action being recorded. Mirrors the
 *  four-principal model in ARCHITECTURE.md; `system` is the catch-all
 *  for supervisor / reaper / boot-path entries that have no human or
 *  agent actor. */
export const Actor = z.enum([
  'session_owner',
  'claude_process',
  'human_approver',
  'peer_agent',
  'system',
])
export type Actor = z.infer<typeof Actor>

// ---------------------------------------------------------------------------
// Primitive shapes
// ---------------------------------------------------------------------------

/** SHA-256 hex string: exactly 64 lowercase hex chars. Enforced at
 *  parse time so a malformed `prevHash` / `hash` is caught before it
 *  reaches the verifier. The writer produces them via `toString('hex')`
 *  on a Node crypto digest, which is guaranteed lowercase. */
const Sha256Hex = z.string().regex(/^[0-9a-f]{64}$/, {
  message: 'sha256 hex must be 64 lowercase hex chars',
})

/** Subset match of `SessionKey` from lib.ts. Duplicated here rather
 *  than reusing the lib schema because the journal must be hashable
 *  independent of whether lib.ts is loaded; keeping the structure
 *  literal keeps the JCS canonical form frozen to this file.
 *
 *  The `satisfies` assertion guarantees the shape stays in lock-step
 *  with the `SessionKey` type — a lib-side rename breaks the build
 *  here, forcing a schema bump.
 *
 *  `.strict()` for the same reason the top-level `JournalEvent` is
 *  strict: two writers that disagree on what fields live inside
 *  `sessionKey` would hash to different canonical forms and break the
 *  chain. Reject unknown fields at parse time. */
const SessionKeyShape = z
  .object({
    channel: z.string(),
    thread: z.string(),
  })
  .strict() satisfies z.ZodType<SessionKey>

// ---------------------------------------------------------------------------
// JournalEvent — the on-disk record shape
// ---------------------------------------------------------------------------

/** One line in `audit.log` after canonical serialization. Every field
 *  is either required (carried by every event) or optional with a clear
 *  meaning when absent.
 *
 *  Why `strict()`: unknown fields on a journal event mean either (a) a
 *  caller is trying to sneak unredacted data through the writer, or
 *  (b) two components disagree on the schema. Both need to be loud,
 *  not swallowed. The cost is that schema growth requires a coordinated
 *  bump of `v` — which is exactly the right friction for a forensic
 *  record.
 *
 *  Canonicalisation note: when the writer (ccsc-5pi.2) hashes an event
 *  it strips `hash` and JCS-serializes the rest. The schema therefore
 *  accepts `hash` as required — partial events without `hash` are a
 *  writer-internal intermediate, not a valid on-disk record.
 */
/** Ed25519 signature shape used by v2 events. Exactly 88 base64 chars
 *  (64-byte raw signature with `=` padding). See crypto.ts for the
 *  sign/verify primitives. */
const Ed25519SignatureB64 = z.string().regex(/^[A-Za-z0-9+/]{86}==$/, {
  message: 'signature must be base64-encoded 64-byte Ed25519 (88 chars total)',
})

/** SHA-256 hex string for the `policy_attestation.digest` field of v2
 *  events. Same shape as `prevHash` / `hash` but semantically distinct
 *  — this records the active policy rule set at the moment the event
 *  was written, computed by `policyDigest()` in policy.ts. */
const PolicyDigestHex = z.string().regex(/^[0-9a-f]{64}$/, {
  message: 'policy_attestation.digest must be 64 lowercase hex chars',
})

/** Optional attestation tying an event to the policy set in effect when
 *  it was written. Present only on v2 events emitted while the writer
 *  was holding a `currentPolicyDigest` value. Absent on v2 events that
 *  are pre-policy-load (the boot event before policy.json is read).
 *
 *  Why this exists: a signed audit log answers "did this happen?" The
 *  policy attestation answers "under what rules?" — without it, an
 *  audit reader cannot reconstruct whether a policy.allow event was
 *  legitimate at the time, only that the writer claimed it was. */
const PolicyAttestation = z
  .object({
    digest: PolicyDigestHex,
    alg: z.literal('sha256'),
  })
  .strict()

export const JournalEvent = z
  .object({
    /** Schema version. v1 is the original hash-chained shape; v2 (ccsc-
     *  22l) adds optional `signature` and `policy_attestation` fields
     *  for Ed25519-signed entries. The verifier accepts mixed v1/v2
     *  chains only in v1 → v2 contiguous order — see 000-docs/audit-
     *  journal-architecture.md § version transition. */
    v: z.union([z.literal(1), z.literal(2)]),

    /** ISO-8601 UTC timestamp with millisecond precision, e.g.
     *  `2026-04-19T12:34:56.789Z`. The writer sets this from `nowIso()`
     *  at append time; callers must not pre-populate. `z.string().datetime()`
     *  enforces the ISO form and mandates a trailing `Z` / offset. */
    ts: z.string().datetime({ offset: true, precision: 3 }),

    /** Monotonic sequence number. Starts at 1 on the first event after
     *  boot and never resets within a chain. A gap between consecutive
     *  events is a tamper signal during verification — see audit-
     *  journal-architecture.md §61-73. */
    seq: z.number().int().nonnegative(),

    /** Discriminated tag identifying what happened. See `EventKind`
     *  above for the enumerated set. */
    kind: EventKind,

    /** MCP tool name when the event involves a tool call. Absent for
     *  session / pairing / system events. */
    toolName: z.string().min(1).optional(),

    /** Redacted tool-call arguments. Every secret-shaped value has been
     *  replaced with `[REDACTED:<kind>]` before this field is hashed or
     *  written. Nested structures are walked recursively by the redactor
     *  (ccsc-5pi.4). */
    input: z.record(z.string(), z.unknown()).optional(),

    /** Outcome classifier for decision events. `n/a` is valid and
     *  required for observational events; absence is valid too (same
     *  semantic). */
    outcome: Outcome.optional(),

    /** Short, human-readable explanation. Redacted before hashing.
     *  Carries no PII or secret material by contract — if you find a
     *  counter-example, file a bead against the caller, not the schema. */
    reason: z.string().optional(),

    /** Identifier of the matched policy rule for `policy.*` events. */
    ruleId: z.string().min(1).optional(),

    /** Owning session when the event is session-scoped. Absent for
     *  `system.*` and some `pairing.*` events that predate session
     *  creation. */
    sessionKey: SessionKeyShape.optional(),

    /** Who triggered or owns the event. See `Actor` above. */
    actor: Actor.optional(),

    /** Dapper-style correlation id linking related events — a single
     *  tool call's policy-require → pairing-issued → pairing-accepted →
     *  policy-approved → gate-outbound-allow all share one
     *  `correlationId`. Absent for events that have no cross-cutting
     *  trace (boot, reload). */
    correlationId: z.string().min(1).optional(),

    /** SHA-256 hex of the preceding event. The very first event in a
     *  chain uses `sha256(TRUSTED_ANCHOR)`; see audit-journal-
     *  architecture.md §76-85 for the anchor contract. */
    prevHash: Sha256Hex,

    /** SHA-256 hex of `prevHash || canonicalJson(event sans hash and signature)`.
     *  Computed by the writer (ccsc-5pi.2) and verified bit-for-bit by
     *  the verify-journal command (ccsc-5pi.9). For v2 events, `signature`
     *  is ALSO stripped before hashing — the signature signs the SAME
     *  canonical bytes the hash covers, so signature and hash are
     *  independent attestations of the same payload, not nested. */
    hash: Sha256Hex,

    /** Ed25519 signature of the canonical bytes covered by `hash`,
     *  base64-encoded (88 chars). Present only on v2 events when the
     *  writer holds a signing keypair. Absent on v1 events and on v2
     *  events written in `--no-audit-signing` mode. The verifier
     *  refuses to verify a v2 event whose `signature` is present but
     *  doesn't match. */
    signature: Ed25519SignatureB64.optional(),

    /** Policy attestation for v2 events. Records the SHA-256 of the
     *  canonicalized active PolicyRule set at the moment the event
     *  was written. Absent on v1 events, on v2 events emitted before
     *  policy.json is loaded, and on v2 events for which no policy
     *  was in effect (boot/shutdown). */
    policy_attestation: PolicyAttestation.optional(),
  })
  .strict()

/** Cross-field validator: v1 events MUST NOT carry v2-only fields.
 *  Applied at parse boundaries where the full event is available
 *  (writer post-hash sanity check, verifier per-line parse) — kept
 *  separate from the base schema so `.omit()` calls still work for
 *  the writer's caller-input shape derivation. */
export function validateVersionFieldExclusivity(event: z.infer<typeof JournalEvent>): void {
  if (event.v === 1 && (event.signature !== undefined || event.policy_attestation !== undefined)) {
    throw new Error(
      `journal event v=1 MUST NOT carry signature or policy_attestation (got seq=${event.seq})`,
    )
  }
}

/** Inferred TypeScript shape of `JournalEvent`. Prefer this over the
 *  Zod type when writing application code — the Zod object is the
 *  parser, the TS type is the data. */
export type JournalEvent = z.infer<typeof JournalEvent>

/** Narrower type for the writer's pre-hash intermediate form: all the
 *  fields that go into the hash, without `hash` itself. The writer
 *  computes `sha256(prevHash || jcs(PartialEvent))` and then attaches
 *  `hash` to produce a full `JournalEvent`. Not exported as a Zod
 *  schema — it is a writer-internal shape, not a valid on-disk record. */
export type PartialJournalEvent = Omit<JournalEvent, 'hash'>

// ---------------------------------------------------------------------------
// JournalWriter — SHA-256 hash-chained append-only writer (ccsc-5pi.2)
// ---------------------------------------------------------------------------

/** Everything a caller supplies for a new event. The writer fills in the
 *  framing fields (`v`, `ts`, `seq`, `prevHash`, `hash`) so callers cannot
 *  drift the hash-determining fields by accident.
 *
 *  Note the Omit excludes `v` even though it is a literal — the writer
 *  always sets it to 1. When the schema version bumps, callers do not
 *  need to update. */
export type WriteInput = Omit<JournalEvent, 'v' | 'ts' | 'seq' | 'prevHash' | 'hash'>

/** Construction options for `JournalWriter.open()`.
 *
 *  Defaults give you a production-shaped writer. Tests override `now` and
 *  `initialPrevHash` to keep hash assertions deterministic.
 */
export interface WriterOptions {
  /** Absolute path to the audit log file. Created with mode `0o600` if
   *  it doesn't exist. */
  path: string

  /** Genesis `prevHash` for an empty file. Default is a fresh random
   *  32-byte sha256, matching the "TRUSTED_ANCHOR" concept in
   *  audit-journal-architecture.md §76-85. Callers that want the anchor
   *  recorded in the first event's body pre-compute it and pass it here.
   *  Ignored when the file is non-empty — existing chains dictate their
   *  own lastHash. */
  initialPrevHash?: string

  /** Clock source for `ts`. Injected in tests so assertions can fix the
   *  timestamp. Default: real wall clock. */
  now?: () => Date

  /** Ed25519 keypair used to sign events (ccsc-22l). When present, the
   *  writer emits v2 events with `signature` populated. When absent
   *  (e.g., `--no-audit-signing` mode or pre-v2 boot), the writer emits
   *  v1 events — backward-compatible with every existing reader.
   *
   *  The keypair itself is opaque to the writer; key loading (SOPS
   *  decrypt, /dev/shm tmpfs) lives in the server boot path. */
  signingKey?: Ed25519KeyPair

  /** Initial policy digest (SHA-256 of canonical JCS of the active
   *  PolicyRule[]). Carried on every v2 event written while the writer
   *  is signing. May be updated later via `setPolicyDigest()` when the
   *  operator hot-reloads the policy. Absent → no `policy_attestation`
   *  is attached (legal for pre-policy events and for unsigned mode). */
  policyDigest?: string
}

/** Module-level registry of open audit-log paths. Enforces the
 *  "single JournalWriter per process" invariant (audit-journal-
 *  architecture.md §148-151, invariant §312-326 #1). A second `open()`
 *  on the same path while the first writer is still live rejects rather
 *  than allowing two writers to interleave their hash chains silently. */
const ACTIVE_PATHS = new Set<string>()

/** Chunk size for the reverse-chunk tail read in `readLastLine`. 64 KiB is
 *  large enough that realistic audit lines (~300-2000 bytes) fit in a
 *  single chunk, small enough that the buffer cost stays negligible even
 *  if recovery runs on a tiny-memory machine. Lines larger than the chunk
 *  are handled correctly by the loop — it just reads another chunk. */
const READ_LAST_LINE_CHUNK_SIZE = 64 * 1024

/** Read the last non-empty newline-delimited line from an open file
 *  handle without loading the whole file into memory. Returns null if
 *  the file is empty (or contains only trailing newlines). Used by
 *  `JournalWriter.open` to recover chain state in O(last-line-size)
 *  memory instead of O(file-size) — the original full-`readFileSync`
 *  path stopped scaling past the low-MB range per ccsc-otd.
 *
 *  Reads with explicit `position` so it doesn't disturb the append
 *  pointer of an `a+`-opened handle (writes still land at EOF via
 *  O_APPEND).
 */
async function readLastLine(fh: FileHandle): Promise<string | null> {
  const { size } = await fh.stat()
  if (size === 0) return null

  // Walk backwards from EOF in chunks, accumulating into `tail`. Stop
  // when we find a newline that precedes non-empty content (i.e., the
  // newline before the last line) or when we reach the start of file.
  let tail = Buffer.alloc(0)
  let pos = size
  while (pos > 0) {
    const readSize = Math.min(READ_LAST_LINE_CHUNK_SIZE, pos)
    pos -= readSize
    const buf = Buffer.alloc(readSize)
    const { bytesRead } = await fh.read(buf, 0, readSize, pos)
    if (bytesRead === 0) break // unexpected but defensive
    tail = Buffer.concat([buf.subarray(0, bytesRead), tail])

    // Trim trailing newlines (one or more) before scanning for the
    // boundary newline so an empty last line (file ends with "\n\n")
    // is treated as "no content on that line".
    let end = tail.length
    while (end > 0 && tail[end - 1] === 0x0a /* '\n' */) end--
    if (end === 0) {
      // Chunk(s) so far are all newlines. Keep reading earlier bytes.
      continue
    }
    // Look for the nearest newline strictly before `end`. If found,
    // the last line is the slice after it (up to `end`).
    const nl = tail.subarray(0, end).lastIndexOf(0x0a)
    if (nl !== -1) {
      return tail.subarray(nl + 1, end).toString('utf8')
    }
    // No newline yet and we've reached start-of-file — whole file is
    // one line. Return it (minus any trailing newlines).
    if (pos === 0) return tail.subarray(0, end).toString('utf8')
    // Else: line is longer than what we've read; loop and pull another
    // chunk.
  }
  // Got here only if the whole file was newlines.
  return null
}

/** Tamper-evident append-only writer. See audit-journal-architecture.md
 *  §76-161 for the full contract. One writer per process per path.
 *
 *  Lifecycle:
 *    1. `JournalWriter.open({ path })` — opens the file in append mode,
 *       reads any existing content to recover `lastHash` + `seq`, and
 *       registers the path.
 *    2. `.writeEvent(input)` — serializes through an internal queue so
 *       concurrent callers cannot interleave increments. Computes
 *       `hash = sha256(lastHash || jcs(event sans hash))`, appends a
 *       newline-delimited JSON line, and returns the full event.
 *    3. `.close()` — flushes, closes the file descriptor, frees the
 *       path registration.
 *
 *  Fail-loud posture: any write failure puts the writer into a broken
 *  state and subsequent `writeEvent` calls reject. Recovery is an
 *  operator concern — inspect and restart. Silent recovery would
 *  violate the forensic-record invariant.
 */
export class JournalWriter {
  private fh: FileHandle | null
  private lastHash: string
  private nextSeq: number
  private readonly now: () => Date
  private readonly path: string

  /** Serialization queue. Every `writeEvent` chains onto this promise so
   *  that increment → hash → append runs as a single critical section
   *  per call, regardless of how many callers await concurrently. */
  private queue: Promise<unknown> = Promise.resolve()

  /** Non-null when the writer has encountered a fatal write error. All
   *  subsequent `writeEvent` calls reject with this error. */
  private broken: Error | null = null

  /** Signing key (ccsc-22l). Present iff the writer should emit v2
   *  signed events; absent iff the writer emits v1 (backward-compatible
   *  legacy mode or `--no-audit-signing` opt-out). */
  private readonly signingKey: Ed25519KeyPair | undefined

  /** Current policy attestation digest (ccsc-22l). Mutable via
   *  `setPolicyDigest()` so the operator can hot-reload policy and
   *  have subsequent events attest the new digest. */
  private policyDigest: string | undefined

  private constructor(
    fh: FileHandle,
    lastHash: string,
    nextSeq: number,
    now: () => Date,
    path: string,
    signingKey: Ed25519KeyPair | undefined,
    policyDigest: string | undefined,
  ) {
    this.fh = fh
    this.lastHash = lastHash
    this.nextSeq = nextSeq
    this.now = now
    this.path = path
    this.signingKey = signingKey
    this.policyDigest = policyDigest
  }

  /** Update the policy-attestation digest carried on subsequent v2
   *  events. Called by the server when `policy.json` is hot-reloaded.
   *  No-op when the writer is not signing — v1 events don't carry
   *  policy_attestation at all. */
  setPolicyDigest(digest: string | undefined): void {
    this.policyDigest = digest
  }

  /** Open (or create) an audit log at `opts.path` and return a ready-
   *  to-write JournalWriter.
   *
   *  Recovers chain state from the existing file: reads the last
   *  newline-delimited JSON line, parses it through the `JournalEvent`
   *  schema, and uses its `hash` and `seq + 1` as the seeds for new
   *  writes. If the file is empty or absent, seeds from
   *  `opts.initialPrevHash` (or a fresh random sha256 if unset) and
   *  seq 1.
   *
   *  Throws if:
   *    - Another `JournalWriter` is already open on the same path in
   *      this process (single-writer invariant).
   *    - The existing file's last line is not valid `JournalEvent`
   *      JSON — fail loudly rather than silently start a new chain
   *      that the verifier would reject anyway.
   */
  static async open(opts: WriterOptions): Promise<JournalWriter> {
    if (ACTIVE_PATHS.has(opts.path)) {
      throw new Error(
        `JournalWriter.open: path already has an active writer in this process: ${opts.path}`,
      )
    }

    // Mode 0o600 on creation; 'a+' flag sets O_RDWR|O_APPEND|O_CREAT.
    // One FileHandle for both the tail read (to recover chain state) and
    // every subsequent append — closes the stat-then-open TOCTOU window
    // that a separate read-then-open pair exposes (per CodeQL
    // js/file-system-race). O_APPEND still guarantees writes land
    // atomically at EOF per audit-journal-architecture.md §155-160;
    // reads use explicit `position` and don't move the append pointer.
    //
    // FileHandle (fs.open) rather than fs.createWriteStream because
    // we need explicit `fh.sync()` after every write for durability;
    // streams buffer and make that awkward. One event = one write =
    // one fsync for this bead (ccsc-5pi.7). A higher-volume operator
    // can relax to batch fsync in a future bead.
    const fh = await fsOpen(opts.path, 'a+', 0o600)

    let lastHash: string
    let nextSeq: number
    try {
      const lastLine = await readLastLine(fh)
      if (lastLine === null) {
        // File is empty (fresh or operator-created with `touch`) —
        // start a new chain. Not an error.
        lastHash = opts.initialPrevHash ?? sha256Hex(randomBytes(32))
        nextSeq = 1
      } else {
        let parsed: JournalEvent
        try {
          parsed = JournalEvent.parse(JSON.parse(lastLine))
        } catch (err) {
          throw new Error(
            `JournalWriter.open: last line of ${opts.path} is not a valid JournalEvent — refusing to start a new chain that would be unverifiable. Underlying error: ${
              err instanceof Error ? err.message : String(err)
            }`,
          )
        }
        lastHash = parsed.hash
        nextSeq = parsed.seq + 1
      }
    } catch (err) {
      // Don't leak the file descriptor if anything in the recovery path
      // throws. ACTIVE_PATHS hasn't been registered yet so we just close.
      // If close itself fails, surface it to stderr (it may indicate a
      // deeper fs problem) but still throw the original recovery error —
      // that's the one the operator needs to fix.
      try {
        await fh.close()
      } catch (closeErr) {
        console.error(
          `[journal] fh.close failed during open() recovery cleanup for ${opts.path}: ${closeErr instanceof Error ? closeErr.message : String(closeErr)}`,
        )
      }
      throw err
    }

    ACTIVE_PATHS.add(opts.path)
    return new JournalWriter(
      fh,
      lastHash,
      nextSeq,
      opts.now ?? ((): Date => new Date()),
      opts.path,
      opts.signingKey,
      opts.policyDigest,
    )
  }

  /** Append a new event. Returns the fully-framed `JournalEvent` that
   *  was persisted, including the writer-assigned `v`, `ts`, `seq`,
   *  `prevHash`, and `hash`.
   *
   *  Concurrent calls are serialized: if caller A and caller B both
   *  `writeEvent()` without awaiting, the promises resolve in call
   *  order and each sees a contiguous seq/hash chain.
   */
  async writeEvent(input: WriteInput): Promise<JournalEvent> {
    if (this.broken) {
      return Promise.reject(
        new Error(`JournalWriter is broken after a prior write failure: ${this.broken.message}`),
      )
    }
    if (this.fh === null) {
      return Promise.reject(new Error('JournalWriter.writeEvent: writer is closed'))
    }
    // Chain onto the existing queue so increments are serialized. Using
    // .then (not await) captures the write call's position in line
    // immediately; callers observe monotonic order regardless of
    // microtask scheduling.
    const p = this.queue.then(() => this._doWrite(input))
    // Swallow rejections on the queue itself so one failed write does
    // not poison the queue chain. The caller still sees the rejection
    // from `p`. The writer's `broken` field guards future calls.
    this.queue = p.then(
      () => undefined,
      () => undefined,
    )
    return p
  }

  private async _doWrite(input: WriteInput): Promise<JournalEvent> {
    // S2: guard broken state at the top of _doWrite so calls that were
    // already enqueued before the break are also rejected. The enqueue-time
    // check in writeEvent() catches fresh calls; this check catches calls
    // that raced in before broken was set and are now draining the queue.
    if (this.broken) {
      throw new Error(`JournalWriter is broken after a prior write failure: ${this.broken.message}`)
    }
    if (this.fh === null) {
      throw new Error('JournalWriter._doWrite: writer closed mid-queue')
    }

    // S3: validate caller-supplied fields BEFORE redaction/truncation and
    // BEFORE hash computation. A ZodError on bad input must propagate
    // without advancing seq/lastHash and without touching this.broken —
    // bad input is a caller bug, not a writer failure; the writer remains
    // usable for the next call. Ordering invariant: validate → redact →
    // truncate → build partial → hash → post-hash sanity parse → write.
    //
    // We validate only the caller-supplied fields (WriteInput) here.
    // The writer-assigned framing fields (v, ts, seq, prevHash, hash) are
    // not yet available, so we cannot parse the full JournalEvent shape.
    // The post-hash JournalEvent.parse below remains as a cheap sanity
    // check that the writer assembled the full event correctly.
    const WriteInputShape = JournalEvent.omit({
      v: true,
      ts: true,
      seq: true,
      prevHash: true,
      hash: true,
    })
    WriteInputShape.parse(input)

    // Redact token-shaped values BEFORE hashing so the on-disk bytes,
    // the hash chain, and the journal the operator inspects all agree.
    // Surgical per audit-journal-architecture.md §183-184: only `input`
    // and `reason` are redacted; other top-level fields are
    // `ruleId`/`correlationId`/`toolName`-style identifiers that never
    // carry secrets by contract. An operator who mistakenly stuffs a
    // token into one of those is a caller bug, not a redactor gap.
    const redactedInput = redactEventFields(input)

    // Truncate AFTER redaction so a half-truncated token never appears
    // on disk (audit-journal-architecture.md §206). Hard-cap per field
    // at TRUNCATION_LIMIT_DEFAULT; an over-limit string becomes a
    // marker + gets a sibling `<field>.len` entry so forensics can see
    // the original size without reading the raw payload.
    const truncatedInput = truncateEventFields(redactedInput)

    // Schema version selection (ccsc-22l):
    //   - signingKey present → v2 events with signature + policy_attestation
    //   - signingKey absent → v1 events (backward-compatible legacy)
    // Once cutover lands, callers that want unsigned mode pass
    // `signingKey: undefined` explicitly. The writer never silently
    // downgrades — operating mode is a boot-time configuration choice.
    const isV2 = this.signingKey !== undefined
    const policyAttestation =
      isV2 && this.policyDigest !== undefined
        ? { digest: this.policyDigest, alg: 'sha256' as const }
        : undefined

    const partial: PartialJournalEvent = {
      v: isV2 ? 2 : 1,
      ts: this.now().toISOString(),
      seq: this.nextSeq,
      prevHash: this.lastHash,
      ...truncatedInput,
      ...(policyAttestation !== undefined ? { policy_attestation: policyAttestation } : {}),
    }
    // canonicalJson(partial) excludes both `hash` (not in partial yet) and
    // `signature` (added post-hash below). The signature signs the same
    // canonical bytes the hash covers — they are independent attestations
    // of the same payload, not nested.
    const canonicalPayload = canonicalJson(partial)
    const hash = sha256Hex(this.lastHash + canonicalPayload)
    let event: JournalEvent = { ...partial, hash }
    if (isV2 && this.signingKey !== undefined) {
      // Sign the exact canonical bytes the hash covers. Deterministic per
      // Ed25519 (RFC 8032 §5.1.6) — same input + key → same signature.
      const signature = signBytes(Buffer.from(canonicalPayload, 'utf8'), this.signingKey)
      event = { ...event, signature }
    }

    // Post-hash sanity check: the full assembled event must pass the strict
    // JournalEvent schema. This is a belt-and-suspenders check after the
    // pre-hash WriteInput validation above — it catches writer-side bugs
    // (e.g. a framing field assembled incorrectly) rather than caller bugs.
    JournalEvent.parse(event)
    validateVersionFieldExclusivity(event)

    const line = `${JSON.stringify(event)}\n`
    try {
      await this.fh.write(line)
      // fsync after every successful write (ccsc-5pi.7). Durability
      // discipline for an audit journal: a crash between `write()`
      // buffering the line and the kernel flushing it would leave
      // the chain apparently intact in memory but missing tail
      // events on disk. For a per-developer journal the per-write
      // fsync cost is imperceptible; for a higher-volume operator a
      // sibling bead can relax this to batch fsync.
      await this.fh.sync()
    } catch (err) {
      this.broken = err instanceof Error ? err : new Error(String(err))
      throw this.broken
    }

    // Advance chain state only after the write succeeds. A crash mid-
    // write leaves `lastHash` and `nextSeq` at the pre-write values,
    // so a restart-then-write resumes at the same point rather than
    // gapping the seq or duplicating the hash.
    this.nextSeq += 1
    this.lastHash = hash

    return event
  }

  /** The current chain-head hash. Exposed so callers that need the
   *  "latest known good" pointer (e.g. the tail-anchor publisher in
   *  Epic 30-B) can read it without parsing the last line of disk. */
  get headHash(): string {
    return this.lastHash
  }

  /** The seq the next successful write will carry. Useful for tests
   *  and for operator diagnostics. */
  get nextSequenceNumber(): number {
    return this.nextSeq
  }

  /** Release the file descriptor. No separate flush is required:
   *  every successful `writeEvent()` has already `fh.sync()`'d the
   *  line to stable storage per ccsc-5pi.7, so there is no
   *  buffered-but-unsynced tail to lose. Idempotent — calling
   *  `close()` on an already-closed writer is a no-op. After close,
   *  `writeEvent()` rejects. */
  async close(): Promise<void> {
    if (this.fh === null) return
    try {
      await this.fh.close()
    } finally {
      this.fh = null
      ACTIVE_PATHS.delete(this.path)
    }
  }
}

// ---------------------------------------------------------------------------
// Canonical JSON (RFC 8785 subset for integer-only event shapes)
// ---------------------------------------------------------------------------

/** Canonicalise `value` for hashing. Two independent encoders must
 *  produce identical byte output so the verifier can recompute the
 *  chain bit-for-bit.
 *
 *  RFC 8785 compliance notes:
 *    - Strings: `JSON.stringify` matches the RFC 8785 escape rules for
 *      all inputs that avoid non-BMP Unicode. Our event schema never
 *      has strings chosen from outside the BMP (hashes are hex; ts is
 *      ISO-8601; Slack IDs are ASCII; policy reason strings are
 *      operator-authored ASCII).
 *    - Numbers: the RFC mandates shortest IEEE-754 double form. Our
 *      schema permits only integers (`seq`); other number forms throw.
 *    - Objects: keys sorted by UTF-16 code-unit order (the RFC form),
 *      which `Array.prototype.sort` delivers for the ASCII key names
 *      the schema uses.
 *    - Arrays: order-preserving.
 *    - No whitespace.
 *
 *  Throws on `undefined`, functions, symbols, bigints — none are valid
 *  `JournalEvent` content; the throw turns a schema-validation miss
 *  into a loud failure at hash time.
 */
export function canonicalJson(value: unknown): string {
  if (value === null) return 'null'
  if (typeof value === 'boolean') return value ? 'true' : 'false'
  if (typeof value === 'number') {
    if (!Number.isFinite(value) || !Number.isInteger(value)) {
      throw new Error(`canonicalJson: only finite integer numbers supported (got ${String(value)})`)
    }
    return String(value)
  }
  if (typeof value === 'string') return JSON.stringify(value)
  if (Array.isArray(value)) {
    return `[${value.map(canonicalJson).join(',')}]`
  }
  if (isRecord(value)) {
    const keys = Object.keys(value).sort()
    const pairs = keys.map((k) => `${JSON.stringify(k)}:${canonicalJson(value[k])}`)
    return `{${pairs.join(',')}}`
  }
  throw new Error(`canonicalJson: unsupported value type: ${typeof value}`)
}

// ---------------------------------------------------------------------------
// sha256 helper
// ---------------------------------------------------------------------------

/** Compute SHA-256 over `input` and return 64-char lowercase hex. Used
 *  by the writer for the hash chain and re-used by the verifier
 *  (ccsc-5pi.9). Kept close to the type + writer so all hash producers
 *  in this module share one implementation. */
export function sha256Hex(input: string | Uint8Array): string {
  return createHash('sha256').update(input).digest('hex')
}

/** Generate a fresh per-chain `TRUSTED_ANCHOR` per audit-journal-
 *  architecture.md §76-85. The returned string is a 64-char lowercase
 *  hex digest of 32 random bytes — matches `Sha256Hex` so it can be
 *  passed directly as `initialPrevHash` to `JournalWriter.open()`
 *  AND recorded in the first `system.boot` event's body.
 *
 *  Callers must do both: pass it to the writer (so the first event's
 *  `prevHash` pins it) and include it in the event body (so a reader
 *  can recover the anchor from the file alone). The chain then
 *  commits to the anchor in two places, meaning an attacker who
 *  edits the anchor in either location breaks the first event's hash
 *  verification. */
export function createBootAnchor(): string {
  return sha256Hex(randomBytes(32))
}

/** Narrow `value` to a plain object shape. Rejects arrays, null, and
 *  primitives. Used by `canonicalJson`, `redact`, and `truncate` so
 *  the `value as Record<string, unknown>` casts that previously
 *  followed `typeof value === 'object' && value !== null` become
 *  compiler-checked narrowings instead of trust-me-bro assertions.
 *  Not exported — these helpers are the only callers. */
function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

// ---------------------------------------------------------------------------
// Redaction — token-shaped secret scrubbing (ccsc-5pi.4)
// ---------------------------------------------------------------------------

/** Known secret patterns. Each entry's `re` is a global regex; `kind`
 *  becomes the `[REDACTED:<kind>]` placeholder. Patterns taken directly
 *  from 000-docs/audit-journal-architecture.md §168-181 — changes to
 *  this list require a design-doc update, not a code-side tweak.
 *
 *  Defense-in-depth, not compliance: the redactor catches the
 *  well-known token shapes that leak most often through error messages
 *  and logs. Bespoke secrets (project-internal tokens, operator-chosen
 *  passwords pasted as message text) still require operator-side
 *  hygiene. The journal is `0o600` for a reason. */
const TOKEN_PATTERNS: ReadonlyArray<{ kind: string; re: RegExp }> = [
  { kind: 'anthropic', re: /sk-[a-zA-Z0-9-]{20,}/g },
  { kind: 'slack_bot', re: /xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+/g },
  { kind: 'slack_app', re: /xapp-[0-9]+-[A-Z0-9]+-[0-9]+-[a-f0-9]+/g },
  { kind: 'github', re: /\bghp_[A-Za-z0-9]{36}\b/g },
  { kind: 'aws_access', re: /\bAKIA[0-9A-Z]{16}\b/g },
  { kind: 'jwt', re: /\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g },
]

/** Return the pattern list for tests and the verifier. Read-only; the
 *  patterns are frozen to match the design doc. */
export function tokenPatterns(): ReadonlyArray<{ kind: string; re: RegExp }> {
  return TOKEN_PATTERNS
}

/** Replace every occurrence of a known secret pattern in `s` with
 *  `[REDACTED:<kind>]`. Pure over the input string. */
function redactString(s: string): string {
  let out = s
  for (const { kind, re } of TOKEN_PATTERNS) {
    out = out.replace(re, `[REDACTED:${kind}]`)
  }
  return out
}

/** Deep-walk `value`, redacting every string encountered and
 *  recursively walking arrays and plain objects. Non-string primitives
 *  (numbers, booleans, null) pass through unchanged; unsupported
 *  container types (Maps, Sets, class instances) pass through by
 *  reference — callers that need to redact those must pre-flatten them
 *  into plain JSON shapes.
 *
 *  Pure: never mutates its argument. Always returns a new object /
 *  array when the container has any redactable content. Returns the
 *  same reference when nothing changed (microoptimisation — saves
 *  allocations in the common case where events carry no tokens). */
export function redact(value: unknown): unknown {
  if (typeof value === 'string') {
    const out = redactString(value)
    return out === value ? value : out
  }
  if (Array.isArray(value)) {
    let changed = false
    const out: unknown[] = new Array(value.length)
    for (let i = 0; i < value.length; i++) {
      const next = redact(value[i])
      if (next !== value[i]) changed = true
      out[i] = next
    }
    return changed ? out : value
  }
  if (isRecord(value)) {
    // Plain object fast-path. We do not try to detect class instances
    // here because the journal event shape is JSON — class instances
    // round-tripping through JSON.stringify would have lost their
    // prototype anyway.
    let changed = false
    const out: Record<string, unknown> = {}
    for (const [k, v] of Object.entries(value)) {
      const next = redact(v)
      if (next !== v) changed = true
      out[k] = next
    }
    return changed ? out : value
  }
  return value
}

/** Writer-integration helper. Redacts only the two fields the design
 *  doc lists (`input`, `reason`) and leaves everything else untouched.
 *  Returns a new object when redaction changed anything; same
 *  reference otherwise. Exported for the writer's own use; not part of
 *  the public caller API.
 *
 *  Why restrict the scope? `toolName`, `ruleId`, `correlationId` and
 *  friends are short identifiers that the caller authored. Redacting
 *  them would mask real operator mistakes behind `[REDACTED:...]` and
 *  make forensic review harder. If a caller does stuff a token into
 *  one of those fields the journal will surface it loud — exactly the
 *  forensic signal an operator wants. */
export function redactEventFields(input: WriteInput): WriteInput {
  const hasReason = typeof input.reason === 'string'
  const hasInput = input.input !== undefined

  if (!hasReason && !hasInput) return input

  const out: WriteInput = { ...input }
  if (hasReason) {
    out.reason = redactString(input.reason as string)
  }
  if (hasInput) {
    out.input = redact(input.input) as Record<string, unknown>
  }
  return out
}

// ---------------------------------------------------------------------------
// Truncation — bound journal record size (ccsc-5pi.5)
// ---------------------------------------------------------------------------

/** Per-field character cap for journal records. Strings longer than
 *  this get replaced with the truncation marker form:
 *
 *    `<first TRUNCATION_LIMIT_DEFAULT chars>[... truncated N chars]`
 *
 *  2048 chars is the doc-specified default (audit-journal-architecture.md
 *  §200-210). Large enough to capture structured JSON error bodies and
 *  typical tool-call args; small enough to keep the journal bounded
 *  even under a burst of oversized payloads. */
export const TRUNCATION_LIMIT_DEFAULT = 2048

/** Truncate a single string to `max` characters, returning it unchanged
 *  if already short enough. The marker preserves the original length
 *  inline so a reader can tell the payload was oversized without
 *  needing the sibling-field bookkeeping. */
function truncateString(s: string, max: number): string {
  if (s.length <= max) return s
  const omitted = s.length - max
  return `${s.slice(0, max)}[... truncated ${omitted} chars]`
}

/** Deep-walk `value`, bounding every string to `max` characters. For
 *  object keys whose value was truncated, a sibling `<key>.len` entry
 *  is added at the same object level recording the original character
 *  count. The sibling key pattern matches audit-journal-architecture.md
 *  §208-210. Arrays are walked but do not get sibling length entries
 *  (arrays don't have named keys — the truncation marker itself
 *  carries the size signal in that case).
 *
 *  Pure: returns the same reference when nothing was truncated.
 *
 *  Edge cases:
 *    - If a sibling `<key>.len` key already exists on the object, it
 *      is overwritten. Collisions with real data are not expected —
 *      callers don't put dotted keys in event payloads — and silent
 *      overwrite is preferable to a throw in the hot path.
 *    - Non-string primitives (numbers, booleans, null) pass through.
 *    - Unsupported container types (Maps, Sets, class instances) pass
 *      through by reference. Pre-flatten those at the caller. */
export function truncate(value: unknown, max: number = TRUNCATION_LIMIT_DEFAULT): unknown {
  if (typeof value === 'string') {
    const t = truncateString(value, max)
    return t === value ? value : t
  }
  if (Array.isArray(value)) {
    let changed = false
    const out: unknown[] = new Array(value.length)
    for (let i = 0; i < value.length; i++) {
      const next = truncate(value[i], max)
      if (next !== value[i]) changed = true
      out[i] = next
    }
    return changed ? out : value
  }
  if (isRecord(value)) {
    const entries = Object.entries(value)
    let changed = false
    const out: Record<string, unknown> = {}
    for (const [k, v] of entries) {
      if (typeof v === 'string' && v.length > max) {
        out[k] = truncateString(v, max)
        out[`${k}.len`] = v.length
        changed = true
      } else {
        const next = truncate(v, max)
        if (next !== v) changed = true
        out[k] = next
      }
    }
    return changed ? out : value
  }
  return value
}

/** Writer-integration helper. Mirrors `redactEventFields`: truncates
 *  only `input` and `reason`, leaves everything else untouched. Called
 *  by the writer after redaction so the hash is computed over the
 *  bounded form.
 *
 *  Why scope it? `reason` and `input` are the realistic oversized-
 *  payload surfaces; other fields are short identifiers. Truncating
 *  `toolName` or `ruleId` would be more confusing than helpful. A
 *  pathological caller who stuffs 100 KiB into `correlationId` will
 *  surface that loudly rather than being quietly truncated — which
 *  matches the redaction policy on the same fields. */
export function truncateEventFields(
  input: WriteInput,
  max: number = TRUNCATION_LIMIT_DEFAULT,
): WriteInput {
  const hasReason = typeof input.reason === 'string'
  const hasInput = input.input !== undefined

  if (!hasReason && !hasInput) return input

  const out: WriteInput = { ...input }
  if (hasReason) {
    const original = input.reason as string
    // `reason` is a top-level string field governed by the strict
    // JournalEvent schema; we cannot add a sibling `reason.len` key
    // there (the schema would reject it). For this field the marker
    // itself carries the original-length signal inline.
    out.reason = truncateString(original, max)
  }
  if (hasInput) {
    out.input = truncate(input.input, max) as Record<string, unknown>
  }
  return out
}

// ---------------------------------------------------------------------------
// Verifier — Schneier-Kelsey chain integrity check (ccsc-5pi.10)
// ---------------------------------------------------------------------------

/** Shape of a verification failure. All fields aside from `reason`
 *  are best-effort — a parse error on the first line, for example,
 *  has no `seq` or `ts` to surface. The operator reads `reason` for
 *  the human explanation and uses `lineNumber` to locate the
 *  offending entry. */
export interface VerifyBreak {
  /** 1-indexed line number where the break was detected. The first
   *  real JSON line is line 1. */
  lineNumber: number
  /** Parsed `seq` of the offending event if it passed schema
   *  validation, else null. */
  seq: number | null
  /** Parsed `ts` of the offending event if it passed schema
   *  validation, else null. */
  ts: string | null
  /** One-line human summary: `"hash mismatch"`, `"version skew"`,
   *  `"seq gap"`, `"prevHash mismatch"`, `"parse error: ..."`, etc. */
  reason: string
  /** Expected hash (or prevHash) when applicable. */
  expected?: string
  /** Actual hash (or prevHash) when applicable. */
  actual?: string
}

/** Result of a full-file verification pass. `eventsVerified` counts
 *  events that matched expectations strictly before a break — useful
 *  for a truncation-tolerance story in follow-up tooling. */
export type VerifyResult =
  | { ok: true; eventsVerified: number }
  | { ok: false; eventsVerified: number; break: VerifyBreak }

// Compile-time shape-drift guard. `lib.ts` duplicates the shape of
// `VerifyResult` as `VerifyResultShape` (type-only, no runtime import)
// to stay decoupled from journal.ts. These bidirectional checks break
// the build the moment either side drifts.
import type { VerifyResultShape } from './lib.ts'

type _VerifyForward = VerifyResult extends VerifyResultShape ? true : never
type _VerifyBackward = VerifyResultShape extends VerifyResult ? true : never
const _verifyShapeForward: _VerifyForward = true
const _verifyShapeBackward: _VerifyBackward = true
void _verifyShapeForward
void _verifyShapeBackward

/** Options accepted by `verifyJournal()`. All optional — a v1-only
 *  chain verifies without any options. v2 chains require
 *  `initialPublicKey` to check signatures. */
export interface VerifyOptions {
  /** Initial Ed25519 public key for v2 signature verification. Base64-
   *   encoded 32-byte raw key (44 chars). When the chain begins with v2
   *   events, this is required — verification fails at the first v2
   *   event without a key. Switches automatically on `system.key_rotation`
   *   events: that event itself verifies under the CURRENT key, then
   *   `input.new_public_key` becomes the active key for subsequent
   *   events. (ccsc-22l) */
  initialPublicKey?: string
  /** Pinned genesis anchor (ccsc-x0t.7). When set, the FIRST accepted event's
   *  `prevHash` must equal this exact value, instead of being trusted as an
   *  opaque per-file random anchor. Defeats head-shear + rechain (v1 and v2): a
   *  sheared file's new first event carries a different `prevHash`. The value is
   *  the writer's `initialPrevHash`, captured out-of-band at journal creation.
   *  Absent → the first `prevHash` is trusted (prior behavior). */
  pinnedGenesisHash?: string
  /** v2 signing-floor anchor (ccsc-x0t.7). When set, every event with
   *  `seq >= v2FloorSeq` MUST be a v2 event — a v1 event at or after the floor
   *  is a downgrade tamper signal. Defeats a uniform rewrite of a signed chain
   *  to unsigned v1 (which the in-file v2→v1 rollback check cannot catch,
   *  because a uniformly-v1 file never trips it). The value is the `seq` at
   *  which the operator turned signing on. Absent → no floor (prior behavior). */
  v2FloorSeq?: number
}

/** Verification anchors (ccsc-x0t.7), factored out of verifyJournal to keep its
 *  CRAP score under the Wall-5 gate (mirrors checkSeqContinuity). Returns a
 *  break descriptor or null.
 *   - v2 floor: a v1 event at `seq >= v2FloorSeq` is a downgrade tamper signal.
 *   - pinned genesis: the FIRST accepted event's prevHash must equal the
 *     operator's out-of-band anchor (defeats head-shear + rechain).
 *  Both anchors are optional; absent → no check (prior behavior). */
function checkVerifyAnchors(
  event: { v: number; seq: number; prevHash: string },
  isGenesis: boolean,
  opts: { pinnedGenesisHash?: string; v2FloorSeq?: number },
): { reason: string; expected?: string; actual?: string } | null {
  const { pinnedGenesisHash, v2FloorSeq } = opts
  if (v2FloorSeq !== undefined && event.v === 1 && event.seq >= v2FloorSeq) {
    return {
      reason: `downgrade below v2 floor — v1 event at seq ${event.seq} (signing floor is seq ${v2FloorSeq})`,
    }
  }
  if (isGenesis && pinnedGenesisHash !== undefined && event.prevHash !== pinnedGenesisHash) {
    return {
      reason: 'genesis prevHash does not match the pinned anchor — head may be truncated',
      expected: pinnedGenesisHash,
      actual: event.prevHash,
    }
  }
  return null
}

/** Sequence-continuity check, factored out of verifyJournal to keep its
 *  cyclomatic complexity under the Wall-5 gate. Enforces two rules:
 *   - genesis: the first accepted event (prevAcceptedSeq === null) must
 *     carry seq 1, else the journal head was truncated;
 *   - continuity: every later event increments seq by exactly 1.
 *  Returns a break descriptor (reason + expected/actual) or null when the
 *  seq is valid. */
function checkSeqContinuity(
  seq: number,
  prevAcceptedSeq: number | null,
): { reason: string; expected: string; actual: string } | null {
  if (prevAcceptedSeq === null) {
    if (seq !== 1) {
      return {
        reason: `first event has seq ${seq}, expected 1 — journal head truncated`,
        expected: '1',
        actual: String(seq),
      }
    }
    return null
  }
  if (seq !== prevAcceptedSeq + 1) {
    return {
      reason: `seq gap — expected ${prevAcceptedSeq + 1}, got ${seq}`,
      expected: String(prevAcceptedSeq + 1),
      actual: String(seq),
    }
  }
  return null
}

/** Verify a journal file end-to-end per audit-journal-architecture.md
 *  §237-261. Reads the file line-by-line, schema-validates each
 *  record, and recomputes `sha256(prevHash || canonicalJson(event
 *  sans hash, sans signature))` for every event. Any mismatch is
 *  reported as a `VerifyBreak`.
 *
 *  Invariants checked (in line order):
 *    - Strict `JournalEvent` shape (v1 OR v2).
 *    - Version transition: v1 → v2 is permitted contiguously; v2 → v1
 *      after a v2 event has been accepted is a tamper signal (rollback
 *      attack). ccsc-22l adds this gate.
 *    - `hash` matches the recomputed value bit-for-bit. The recompute
 *      strips BOTH `hash` and `signature` so the v2 hash covers the
 *      same canonical bytes the signature signs.
 *    - On v2 events: `signature` (when present) verifies under the
 *      currently-active public key. `system.key_rotation` events
 *      verify under the OLD key, then switch the key for subsequent
 *      events.
 *    - `prevHash` matches the previous accepted event's `hash`
 *      (first event's `prevHash` is trusted as the genesis value —
 *      that's the `TRUSTED_ANCHOR` contract from §76-85; validating
 *      the anchor is a caller concern for now).
 *    - `seq` is strictly monotonic by +1 with no gaps, AND the first
 *      accepted event has `seq === 1`. The genesis-seq pin defeats
 *      head-truncation (shearing lines off the top) **only for signed,
 *      key-verified (v2) chains**: the surviving prefix would otherwise
 *      verify cleanly because its new first event's `prevHash` is trusted
 *      as genesis, but on a v2 chain the attacker cannot renumber the
 *      survivors' `seq` and recompute the chain without also reforging
 *      every Ed25519 signature (checked against `opts.initialPublicKey`),
 *      which requires the signing key. **On an unsigned v1 chain the pin
 *      adds nothing**: the hash chain is a bare keyless SHA-256, so a
 *      writer-capable attacker renumbers survivors to `seq === 1` and
 *      recomputes `hash = sha256(prevHash + canonicalJson(event))` with no
 *      secret — the sheared file verifies clean (encoded as a
 *      known-limitation test in server.test.ts, ccsc-x0t.2). Tail-
 *      truncation and a uniform full-file downgrade of a signed chain to
 *      unsigned v1 (stripping every Ed25519 signature) likewise remain
 *      residual — defeating them needs a pinned "signing began at seq N"
 *      v2-floor anchor (deferred; tracked as ccsc-x0t.7 under epic #269).
 *
 *  The function never modifies the file (read-only contract).
 *  Returns on the first break; a second broken event after a fixed
 *  first break is outside the verify-and-report-one-location
 *  semantic the doc describes. */
export async function verifyJournal(path: string, opts: VerifyOptions = {}): Promise<VerifyResult> {
  let raw: string
  try {
    raw = await readFile(path, 'utf8')
  } catch (err) {
    return {
      ok: false,
      eventsVerified: 0,
      break: {
        lineNumber: 0,
        seq: null,
        ts: null,
        reason: `read failed: ${err instanceof Error ? err.message : String(err)}`,
      },
    }
  }

  const lines = raw.split('\n')
  let prevAcceptedHash: string | null = null
  let prevAcceptedSeq: number | null = null
  let eventsVerified = 0
  let seenV2 = false // ccsc-22l — once true, v2 → v1 is a rollback signal
  let activePublicKey: string | undefined = opts.initialPublicKey
  const { pinnedGenesisHash, v2FloorSeq } = opts // ccsc-x0t.7 anchors

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!
    // Tolerate a trailing empty line (from the writer's final
    // newline). Empty lines mid-file would indicate structural
    // damage; those are flagged.
    if (line.length === 0) {
      if (i === lines.length - 1) continue
      return {
        ok: false,
        eventsVerified,
        break: {
          lineNumber: i + 1,
          seq: prevAcceptedSeq,
          ts: null,
          reason: 'empty line in middle of journal (structural damage)',
        },
      }
    }

    const lineNumber = i + 1

    let event: JournalEvent
    try {
      event = JournalEvent.parse(JSON.parse(line))
      validateVersionFieldExclusivity(event)
    } catch (err) {
      return {
        ok: false,
        eventsVerified,
        break: {
          lineNumber,
          seq: null,
          ts: null,
          reason: `parse/schema error: ${err instanceof Error ? err.message : String(err)}`,
        },
      }
    }

    // Version-transition gate (ccsc-22l):
    //   - v1 events are always permitted (legacy).
    //   - v2 events are permitted; once seen, the chain has crossed
    //     the cutover and any subsequent v1 event is a rollback
    //     (downgrade tamper).
    if (event.v === 1 && seenV2) {
      return {
        ok: false,
        eventsVerified,
        break: {
          lineNumber,
          seq: event.seq,
          ts: event.ts,
          reason: 'version rollback — v1 event appears after v2 was accepted',
        },
      }
    }
    if (event.v === 2) {
      seenV2 = true
    }

    // Verification anchors (ccsc-x0t.7) — factored into checkVerifyAnchors to
    // keep verifyJournal under the Wall-5 CRAP gate (mirrors checkSeqContinuity).
    const anchorBreak = checkVerifyAnchors(event, prevAcceptedHash === null, {
      pinnedGenesisHash,
      v2FloorSeq,
    })
    if (anchorBreak !== null) {
      return {
        ok: false,
        eventsVerified,
        break: { lineNumber, seq: event.seq, ts: event.ts, ...anchorBreak },
      }
    }

    if (prevAcceptedHash !== null && event.prevHash !== prevAcceptedHash) {
      return {
        ok: false,
        eventsVerified,
        break: {
          lineNumber,
          seq: event.seq,
          ts: event.ts,
          reason: 'prevHash mismatch — chain break',
          expected: prevAcceptedHash,
          actual: event.prevHash,
        },
      }
    }

    const seqBreak = checkSeqContinuity(event.seq, prevAcceptedSeq)
    if (seqBreak !== null) {
      return {
        ok: false,
        eventsVerified,
        break: { lineNumber, seq: event.seq, ts: event.ts, ...seqBreak },
      }
    }

    // Recompute the hash. This is the primary tamper check: any edit
    // to the event body (kind, input, reason, anything) will change
    // the canonical serialization and so the computed hash. Strip
    // BOTH `hash` and `signature` (signature is added post-hash by the
    // v2 writer, so the canonical bytes the hash covers exclude it).
    const { hash: stored, signature: storedSignature, ...rest } = event
    const canonicalPayload = canonicalJson(rest)
    const recomputed = sha256Hex(event.prevHash + canonicalPayload)
    if (recomputed !== stored) {
      return {
        ok: false,
        eventsVerified,
        break: {
          lineNumber,
          seq: event.seq,
          ts: event.ts,
          reason: 'hash mismatch — event body or prevHash was tampered',
          expected: recomputed,
          actual: stored,
        },
      }
    }

    // v2 signature verification. Signatures are verified against the
    // CURRENTLY active public key (which may change after a
    // `system.key_rotation` event). A v2 event without a `signature`
    // field is permitted ONLY when no public key was supplied — this
    // is the unsigned-relaxed mode (`--no-audit-signing`). When a key
    // IS supplied, every v2 event must carry a verifiable signature.
    if (event.v === 2 && storedSignature !== undefined) {
      if (activePublicKey === undefined) {
        return {
          ok: false,
          eventsVerified,
          break: {
            lineNumber,
            seq: event.seq,
            ts: event.ts,
            reason: 'v2 event has signature but no public key was provided to the verifier',
          },
        }
      }
      try {
        if (
          !verifySignatureBytes(
            Buffer.from(canonicalPayload, 'utf8'),
            storedSignature,
            activePublicKey,
          )
        ) {
          return {
            ok: false,
            eventsVerified,
            break: {
              lineNumber,
              seq: event.seq,
              ts: event.ts,
              reason: 'signature verification failed under active public key',
            },
          }
        }
      } catch (err) {
        return {
          ok: false,
          eventsVerified,
          break: {
            lineNumber,
            seq: event.seq,
            ts: event.ts,
            reason: `signature verification threw: ${err instanceof Error ? err.message : String(err)}`,
          },
        }
      }
    } else if (event.v === 2 && storedSignature === undefined && activePublicKey !== undefined) {
      return {
        ok: false,
        eventsVerified,
        break: {
          lineNumber,
          seq: event.seq,
          ts: event.ts,
          reason:
            'v2 event missing signature while verifier holds a public key (unsigned event in signed chain)',
        },
      }
    }

    // After a successful key_rotation event verifies under the OLD
    // key, switch to the new key for subsequent events. The new key
    // is carried in input.new_public_key per the rotation contract
    // documented in 000-docs/key-management.md § Rotation.
    if (event.v === 2 && event.kind === 'system.key_rotation') {
      const inputRecord = (event.input ?? {}) as Record<string, unknown>
      const newKey = inputRecord.new_public_key
      if (typeof newKey !== 'string') {
        return {
          ok: false,
          eventsVerified,
          break: {
            lineNumber,
            seq: event.seq,
            ts: event.ts,
            reason: 'system.key_rotation event missing input.new_public_key',
          },
        }
      }
      activePublicKey = newKey
    }

    prevAcceptedHash = event.hash
    prevAcceptedSeq = event.seq
    eventsVerified += 1
  }

  return { ok: true, eventsVerified }
}
