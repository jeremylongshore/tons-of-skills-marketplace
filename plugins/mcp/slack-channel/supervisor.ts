/**
 * supervisor.ts — Session supervisor interface for the MCP server.
 *
 * This file is the Epic 32-B entry point. It declares the shape of the
 * SessionSupervisor actor — the single component allowed to create,
 * transition, or destroy sessions — without providing a runtime. The
 * activate / quiesce / deactivate implementations land in sibling beads
 * (ccsc-xa3.2, ccsc-xa3.3, and the deactivate + reaper beads under
 * ccsc-xa3.14). See 000-docs/session-state-machine.md §221-267 for the
 * full behavioural contract this interface pins down, and Armstrong
 * (2003) for the supervisor / lifecycle pattern it borrows from.
 *
 * Design notes:
 *
 *   - **Actor, not a library.** Every mutation of a live session flows
 *     through a single SessionSupervisor owned by server.ts. lib.ts
 *     primitives (sessionPath, saveSession, loadSession) are called only
 *     from here. A session file written by any other path is a bug.
 *
 *   - **One mutex per session file.** Two Slack threads in the same
 *     channel are independent; their handles carry independent mutexes.
 *     The supervisor guarantees serialised `update()` calls per key, not
 *     per channel.
 *
 *   - **Crash is not data loss.** The on-disk file is the source of
 *     truth. In-memory handles are caches. If the process crashes mid-
 *     flight, the next inbound event for that key re-enters Activating
 *     and re-reads the file (see session-state-machine.md §239-247).
 *
 *   - **No policy, no gate, no journal.** The supervisor decides when a
 *     session is loaded, held, flushed, or quarantined — it does not
 *     decide who can speak (inbound gate), which tools run (Epic 29-B),
 *     or what gets logged (Epic 30-A). Those subsystems observe session
 *     state; they never mutate it.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

import type { JournalWriter } from './journal'
import type { DeliveryObligation, InFlightTurn, Session, SessionKey } from './lib'
import {
  classifyDeliveryError,
  computeBackoffMs,
  ExfilBlockedError,
  extractSlackErrorCode,
  listSessions,
  loadSession,
  saveSession,
  sessionPath,
} from './lib'

// ---------------------------------------------------------------------------
// Lifecycle state
// ---------------------------------------------------------------------------

/** Observable lifecycle state for one session, mirroring the five-state
 *  FSM in 000-docs/session-state-machine.md §109-155. Nonexistent is
 *  implicit (no handle) so it is not an enumerated value here.
 *
 *  Transitions are strict and are the supervisor's responsibility — the
 *  doc diagram is authoritative, this type is descriptive.
 *
 *    - `activating`   — load-or-create in progress; single-writer critical
 *                       section. Callers of activate() observe this only
 *                       through the returned Promise resolving.
 *    - `active`       — handle is live, `session` reflects the on-disk
 *                       file after the most recent `update()`.
 *    - `quiescing`    — refusing new work; pending writes still flushing.
 *                       `update()` rejects.
 *    - `deactivating` — last flush resolved; handle about to be released.
 *                       Terminal from the caller's perspective.
 *    - `quarantined`  — save or load failure; supervisor filed a beads
 *                       issue and will not auto-reload. Only a human
 *                       (SO) clears this; see session-state-machine.md
 *                       §132-137.
 */
export type SessionState = 'activating' | 'active' | 'quiescing' | 'deactivating' | 'quarantined'

// ---------------------------------------------------------------------------
// Fencing lease — crash-safe turn ownership (ccsc-o7x.1.1)
// ---------------------------------------------------------------------------

/** A fencing lease over an active session's turn. Exactly one owner holds a
 *  live lease at a time; the monotonic `token` fences writes so a resurrected
 *  old owner — one whose process hung past the heartbeat window, was presumed
 *  dead, and whose turn a new owner took over — cannot clobber the new owner's
 *  work, because its stale token no longer matches the current lease.
 *
 *  In-memory for ccsc-o7x.1.1: the lease lives on the active handle and the
 *  token comes from a process-monotonic counter. Crash-durable ownership across
 *  a process restart (so a restarted process mints a token strictly greater
 *  than any pre-crash token) is ccsc-o7x.1.2's job; routing a lapsed lease into
 *  the quarantine terminal is ccsc-o7x.1.3's. The on-disk session file stays
 *  the source of truth (session-state-machine.md invariant 5) — the lease
 *  fences writes, it does not replace the file. */
export interface Lease {
  /** Monotonic ownership token. Strictly increases on every acquisition, so a
   *  newer owner always holds a higher token than any prior owner of the key. */
  readonly token: number
  /** Identifier of the owner that acquired this lease (the supervisor process).
   *  Recorded for the recovery sweep's forensics (ccsc-o7x.1.2); fencing keys
   *  on `token`, not `owner`. */
  readonly owner: string
  /** Epoch-ms of the most recent heartbeat. A lease whose heartbeat has not
   *  been renewed within the TTL is *stale* — the signal its owner died. */
  readonly heartbeatAt: number
}

/** Default lease heartbeat-lapse window: 30s. An active turn renews its lease
 *  well within this; a gap longer than this means the owner stopped heart-
 *  beating (crash, hang, or kill). Tunable via `SLACK_SESSION_LEASE_TTL_MS`. */
export const DEFAULT_LEASE_TTL_MS = 30_000

/** Parse `SLACK_SESSION_LEASE_TTL_MS` from an env record. Falls back to
 *  `DEFAULT_LEASE_TTL_MS` when unset, empty, non-numeric, non-positive, or
 *  non-finite. Pure relative to `env` (same shape as `resolveIdleMs`). */
export function resolveLeaseTtlMs(env: Record<string, string | undefined> = process.env): number {
  const raw = env.SLACK_SESSION_LEASE_TTL_MS
  if (raw === undefined || raw === '') return DEFAULT_LEASE_TTL_MS
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) return DEFAULT_LEASE_TTL_MS
  return Math.floor(parsed)
}

/** True when `lease`'s heartbeat has lapsed past `ttlMs` as of `now`. Pure.
 *  Strict `>` so a heartbeat exactly `ttlMs` old is still live. */
export function isLeaseStale(lease: Lease, now: number, ttlMs: number): boolean {
  return now - lease.heartbeatAt > ttlMs
}

/** Default cap on send attempts per delivery obligation before the poller
 *  dead-letters it (ccsc-o7x.2.2). Bounds retries on a persistently-failing
 *  retryable error so it can never loop forever. */
export const DEFAULT_MAX_DELIVERY_ATTEMPTS = 5

/** Default inter-retry wait used by `drainOutbox` — a real timer. Tests inject
 *  a recording / no-op stub so backoff is asserted without wall-clock waits. */
const defaultDelayMs = (ms: number): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, ms))

/** Return a copy of `lease` with its heartbeat advanced to `now`. Pure — the
 *  input is never mutated; `token` and `owner` carry forward unchanged. */
export function heartbeatLease(lease: Lease, now: number): Lease {
  return { token: lease.token, owner: lease.owner, heartbeatAt: now }
}

/** A boot-time recovery decision for one persisted in-flight turn (ccsc-o7x.1.2). */
export type RecoveryDecision = 'resumable' | 'orphaned'

/** Classify a persisted in-flight turn during the startup sweep. A turn whose
 *  heartbeat has lapsed past `ttlMs` as of `now` is `resumable`: its owner is
 *  provably dead (the same lapse test the in-memory lease uses — see
 *  `isLeaseStale`), so a new owner can safely take over and the marker is
 *  cleared. A turn whose heartbeat is still fresh is `orphaned`: a second
 *  *live* owner sharing the state dir cannot be ruled out, so the session is
 *  quarantined rather than resumed — fail closed. Pure; mirrors `isLeaseStale`'s
 *  strict `>` boundary. */
export function classifyRecovery(turn: InFlightTurn, now: number, ttlMs: number): RecoveryDecision {
  return now - turn.heartbeatAt > ttlMs ? 'resumable' : 'orphaned'
}

/** Outcome of one `recoverOnStartup()` sweep (ccsc-o7x.1.2). */
export interface RecoveryReport {
  /** Number of session files scanned. */
  scanned: number
  /** Keys whose lapsed in-flight turn was requeued — marker cleared, session
   *  left clean and re-activatable by the next inbound message. */
  requeued: SessionKey[]
  /** Keys orphaned into quarantine — in-flight turn not provably abandoned, or
   *  the file could not be read during the sweep. */
  orphaned: SessionKey[]
}

/** Outcome of one `drainOutbox()` pass (ccsc-o7x.2.2). Every pending obligation
 *  examined this pass lands in exactly one of the three result lists (or is
 *  skipped). */
export interface OutboxDrainReport {
  /** Total pending obligations examined this pass. */
  scanned: number
  /** Obligation ids delivered successfully (state → `delivered`). */
  delivered: string[]
  /** Obligations dead-lettered (state → `dead`) with the recorded failure —
   *  either a non-retryable Slack error or a retryable one that exhausted the
   *  attempt cap. */
  deadLettered: { id: string; error: string }[]
  /** Obligation ids left `pending` and NOT sent this pass because the session's
   *  fencing lease was lost/superseded before the send (a newer owner exists),
   *  the session was unactivatable (quarantined), or persisting the resolved
   *  state was fenced. They are retried on a later pass by the live owner. */
  skipped: string[]
}

// ---------------------------------------------------------------------------
// SessionHandle — in-memory wrapper around one Session file
// ---------------------------------------------------------------------------

/** Live handle to one session. Returned by `SessionSupervisor.activate()`.
 *
 *  Callers treat the handle as opaque: read `session` for the current
 *  snapshot, call `update()` to persist a change. The handle enforces
 *  serialised writes through an internal mutex keyed on this session's
 *  path — two concurrent `update()` calls on the same handle run in
 *  strict order (see session-state-machine.md §210 invariant 1).
 *
 *  A handle is valid only while `state === 'active'`. Once quiesce has
 *  started, `update()` rejects; callers must re-activate to resume.
 */
export interface SessionHandle {
  /** Identity. Immutable for the lifetime of the handle. */
  readonly key: SessionKey

  /** Lifecycle state of this handle as observed by the supervisor.
   *  Consumers may read but must not assume state is stable between
   *  awaits — the reaper or a shutdown signal can transition the
   *  handle out from under them. Always re-check after an `await`. */
  readonly state: SessionState

  /** Most recent successfully persisted snapshot of this session. The
   *  reference may point to frozen / read-only data; callers must not
   *  mutate it in place. Produce the next version inside `update()`. */
  readonly session: Session

  /** The fencing lease currently held over this session's active turn, or
   *  `null` before activation completes. Readers must not mutate it; renew it
   *  via `heartbeat()`. (ccsc-o7x.1.1) */
  readonly lease: Lease | null

  /** Renew the active turn's lease heartbeat. Returns `true` if `token` matches
   *  the current lease — the heartbeat is advanced to now; `false` if the lease
   *  was superseded by a newer owner or never acquired, meaning the caller has
   *  been fenced and should stop writing. (ccsc-o7x.1.1) */
  heartbeat(token: number): boolean

  /** Persist an in-flight-turn marker to the session file so a crash mid-turn
   *  leaves a recoverable trace for the boot-time sweep (ccsc-o7x.1.2). Fenced
   *  by `token`: rejects if it is not the current lease's. The write rides the
   *  same atomic save path as `update()`. */
  recordTurnStart(token: number): Promise<void>

  /** Clear the in-flight-turn marker on clean turn completion (ccsc-o7x.1.2).
   *  Fenced by the current lease when one is held; a no-op persist when the
   *  marker is already absent. */
  recordTurnEnd(): Promise<void>

  /** Record a durable "reply owed" obligation as the turn reaches its terminal
   *  state (ccsc-o7x.2.1) — the transactional-outbox write. In ONE atomic save
   *  it appends a fresh `pending` obligation to the session's `outbox` AND
   *  clears the in-flight-turn marker, so "turn done, reply owed" is a single
   *  durable fact. Must run BEFORE the Slack send is attempted; a crash after
   *  this write but before the send leaves a pending obligation the delivery
   *  poller (ccsc-o7x.2.2) honors. Fenced by `token` (the current lease's). The
   *  caller supplies the message identity + content; `attempts` (0), `state`
   *  (`pending`), and `createdAt` are stamped here. */
  recordTerminalDelivery(
    token: number,
    reply: {
      id: string
      channel: string
      thread: string
      payload: string
      blocks?: Array<Record<string, unknown>>
    },
  ): Promise<void>

  /** Batch sibling of `recordTerminalDelivery` for a chunked reply (ccsc-o7x.4):
   *  one logical reply that spans N Slack messages. Appends ALL `replies` as
   *  fresh `pending` obligations AND clears the in-flight-turn marker in ONE
   *  atomic save — all-or-nothing, so a crash mid-record can never leave a
   *  partially-recorded chunked reply (some chunks owed, the rest silently lost).
   *  Each caller-supplied `id` must be unique (the chunk index is folded in by
   *  the caller, e.g. `<replyId>:<i>`) so each chunk gets its own idempotency
   *  key. Order is preserved: the obligations append in `replies` order, and the
   *  poller drains a session's outbox in array order. Fenced by `token`.
   *
   *  ccsc-o7x.5 — a reply may also carry FILE-upload obligations: a reply with an
   *  `upload` descriptor becomes a durable `filesUploadV2` obligation rather than
   *  a `chat.postMessage`. Text obligations are recorded before file ones so the
   *  poller posts the message before its attachments. */
  recordTerminalDeliveries(
    token: number,
    replies: readonly {
      id: string
      channel: string
      thread: string
      payload: string
      blocks?: Array<Record<string, unknown>>
      upload?: { path: string; filename: string; comment?: string }
    }[],
  ): Promise<void>

  /** Serialise an update through the per-session mutex, persist it via
   *  the atomic writer (`saveSession()`), and refresh `this.session`.
   *
   *  Contract:
   *    - `fn` receives the current session and returns the next one.
   *      It must be pure — no I/O, no sleeps, no throwing except to
   *      signal a validation failure that should abort the update.
   *    - The supervisor persists the returned value with the atomic
   *      writer. Partial state never lands on disk.
   *    - On save failure the handle transitions to `quarantined` and
   *      the returned promise rejects. In-memory `session` reverts to
   *      the pre-update value; no consumer ever sees the failed draft.
   *    - While `state !== 'active'` the promise rejects without
   *      calling `fn`.
   *    - When `fenceToken` is supplied the write is *fenced*: it is rejected
   *      (without calling `fn` or persisting) if no live lease is held, if the
   *      token has been superseded by a newer owner, or if the lease's
   *      heartbeat has lapsed past the TTL. Omit `fenceToken` for an unfenced
   *      write (current default for callers that do not yet hold a lease).
   *      (ccsc-o7x.1.1)
   *    - A fenced rejection is treated as **lease loss**: the handle is
   *      transitioned to `quarantined` (and removed from the supervisor's
   *      active set) so the turn performs no further work, rather than retried.
   *      `fenceToken` is the owner's own held lease token, so a mismatch is a
   *      real loss, not a stray caller. (ccsc-o7x.1.3) */
  update(fn: (prev: Session) => Session, fenceToken?: number): Promise<void>
}

// ---------------------------------------------------------------------------
// SessionSupervisor — the actor contract
// ---------------------------------------------------------------------------

/** Supervisor for the per-thread session population. There is exactly one
 *  `SessionSupervisor` per MCP server process; it owns the
 *  `Map<SessionKey, SessionHandle>` named in session-state-machine.md
 *  §229 and is the only code permitted to drive state transitions on
 *  that map.
 *
 *  Armstrong-style shape: the supervisor is a long-lived actor that
 *  delegates work to short-lived per-session children (the handles).
 *  Crashes of a single session are isolated — quarantine a handle, keep
 *  serving every other key. Crashes of the supervisor itself restart
 *  the whole population from disk (see §239-247).
 *
 *  The supervisor is **not** responsible for deciding whether an inbound
 *  event reaches Claude (that is the inbound `gate()` in lib.ts), for
 *  deciding whether a tool call runs (policy evaluator, Epic 29), or
 *  for persisting the audit log (journal sink, Epic 30). It is a pure
 *  session-lifecycle authority.
 */
export interface SessionSupervisor {
  /** Activate the session for `key`: load the file if it exists, create
   *  an empty one if not, and return a live handle.
   *
   *  `initialOwnerId` is the Slack user ID to record as `ownerId` on a
   *  newly-created session file. It is consulted **only** on the create
   *  branch; if the session file already exists, the stored owner wins
   *  and the argument is ignored. A caller that knows the session
   *  already exists may omit it. A caller that cannot vouch for owner
   *  (supervisor rehydration on boot, internal bookkeeping) may omit it
   *  as well — activate() will then reject if the file is missing,
   *  rather than synthesize an owner.
   *
   *  Contract:
   *    - Idempotent per key. Two concurrent activate() calls for the
   *      same key return the same handle (single-flight, per
   *      session-state-machine.md §266).
   *    - While loading/creating the handle observes `state =
   *      'activating'`; the returned promise resolves only after the
   *      handle reaches `active`.
   *    - Load failure on an existing file transitions to `quarantined`
   *      and rejects the promise; the supervisor files a beads issue
   *      for the SO and never auto-retries.
   *    - Path-validation failure (realpath escape, bad SessionKey
   *      component) rejects before any on-disk work; no session is
   *      recorded for the key.
   *    - Does not enforce idle TTL. Reaper logic lives in the deactivate
   *      path, not here. */
  activate(key: SessionKey, initialOwnerId?: string): Promise<SessionHandle>

  /** Refuse new work on `key` and wait for pending writes to flush.
   *
   *  Contract:
   *    - After `quiesce()` begins, `update()` on the associated handle
   *      rejects. New `activate()` calls for the same key wait for
   *      quiesce to complete, then re-activate from disk.
   *    - A new inbound event may cancel the quiesce and return the
   *      handle to `active`, per session-state-machine.md §124 (the
   *      `Quiescing → Active` transition). That decision is the
   *      supervisor's; callers of `quiesce()` receive a promise that
   *      resolves in either terminal case.
   *    - Quiesce is idempotent: a second call during an in-flight
   *      quiesce joins the same promise. */
  quiesce(key: SessionKey): Promise<void>

  /** Release the in-memory handle. The on-disk file is left alone.
   *
   *  Contract:
   *    - Must be preceded by a completed `quiesce(key)`. Calling
   *      `deactivate` on an `active` key is a programmer error and
   *      rejects.
   *    - After deactivation, the supervisor's live map no longer
   *      contains `key`. Future inbound events for the same key
   *      re-enter `activate()` and reload the file from disk.
   *    - Quarantined handles are not deactivated through this path —
   *      they persist until a human clears the quarantine flag. */
  deactivate(key: SessionKey): Promise<void>

  /** Graceful shutdown. Quiesces every live session in parallel, awaits
   *  all flushes, then deactivates. Called from server.ts on SIGTERM /
   *  SIGINT and on stdin EOF from the Claude Code host.
   *
   *  After `shutdown()` resolves the supervisor is unusable; a second
   *  `activate()` call rejects. A new supervisor instance is required
   *  to resume, and it will rebuild state from disk. */
  shutdown(): Promise<void>

  /** Clear the quarantine flag for `key`, allowing a future `activate()`
   *  to succeed. This is the explicit operator-action path specified in
   *  session-state-machine.md §129 ("only a human (SO) clears this").
   *
   *  Contract:
   *    - If `key` is not quarantined this is a no-op; no error is thrown
   *      because the operator may have already cleared it.
   *    - After this call, a subsequent `activate()` will attempt to load
   *      the session file from disk as normal. If the file is still
   *      corrupted, the load will fail and the key will be quarantined
   *      again.
   *    - Does not perform any I/O; it only removes the in-memory
   *      quarantine entry. The audit journal event for this action lands
   *      in Epic 32-B. */
  clearQuarantine(key: SessionKey): void

  /** One pass of the idle reaper. Finds every `active` handle whose
   *  `session.lastActiveAt` is older than `idleMs` and has no in-flight
   *  work, then drives it through quiesce → deactivate.
   *
   *  Contract:
   *    - Never reaps a handle with `inFlight.size > 0` (session-state-
   *      machine.md §265 — the idle TTL check runs before quiesce and
   *      does not pre-empt in-flight work).
   *    - Never reaps a handle whose state is not `active`. Quiescing /
   *      deactivating / quarantined handles are on their own edge of
   *      the FSM; the reaper stays out of their way.
   *    - Errors on a single session do not stop the tick. The reaper
   *      logs the failure and moves on so one quarantined handle can't
   *      starve the rest of the population.
   *    - Pure relative to wall-clock — tests inject a `clock` to drive
   *      the threshold deterministically.
   *
   *  Timer wiring lives in `server.ts`: this function is the reapable
   *  unit so the server can decide tick frequency, or a test can call
   *  it directly. */
  reapIdle(): Promise<void>

  /** Boot-time crash-recovery sweep (ccsc-o7x.1.2). Reads every persisted
   *  session file; for each carrying an in-flight-turn marker, classifies it
   *  (`classifyRecovery`) and acts:
   *
   *    - **resumable** (marker heartbeat lapsed past the lease TTL — owner
   *      provably dead): clear the marker, persist the clean session so the
   *      next inbound event re-activates it normally, and journal
   *      `session.recovery.requeued`.
   *    - **orphaned** (marker still fresh, or file unreadable): record the key
   *      in the quarantine map so `activate()` rejects until a human clears it,
   *      and journal `session.recovery.orphaned`. Fail closed — a second live
   *      owner on the same state dir cannot be ruled out.
   *
   *  Also seeds the supervisor's monotonic lease-token counter above every
   *  persisted token, so a restarted process never re-issues a token a crashed
   *  owner already held (crash-durable monotonicity — the durable half of the
   *  ccsc-o7x.1.1 fence).
   *
   *  Contract:
   *    - Idempotent on a clean state dir (no markers) — a no-op that returns a
   *      zero report.
   *    - Intended to run ONCE at boot, before the socket opens, while no handle
   *      is live. Errors on a single file do not stop the sweep.
   *    - Returns a `RecoveryReport` for the caller / tests. */
  recoverOnStartup(): Promise<RecoveryReport>

  /** Read side of the transactional outbox (ccsc-o7x.2.1): scan every session
   *  file and return all `pending` delivery obligations across the population.
   *  This is the delivery poller's (ccsc-o7x.2.2) input — it consumes each
   *  obligation, sends it, and resolves it. Best-effort: a file that cannot be
   *  read is skipped (logged), never throwing. Reads from disk so a fresh
   *  process after a crash sees obligations recorded by the prior one. */
  pendingDeliveries(): Promise<DeliveryObligation[]>

  /** Delivery poller (ccsc-o7x.2.2) — the consumer side of the transactional
   *  outbox. One pass over every `pending` obligation (`pendingDeliveries()`):
   *  for each, deliver it via `send` under the session's fencing lease, then
   *  persist the resolved state in one fenced write. Replaces the old
   *  stderr-and-swallow on a failed `chat.postMessage`.
   *
   *    - **success** → obligation `delivered`, `attempts` incremented.
   *    - **retryable error** (rate limit, transient 5xx, network — see
   *      `classifyDeliveryError`) → retried in-pass with exponential backoff
   *      (`computeBackoffMs`) up to `maxAttempts`; on exhaustion it is
   *      dead-lettered (`dead`) with the last error recorded — bounded, never
   *      an infinite retry.
   *    - **non-retryable error** (channel gone, bad auth, payload malformed) →
   *      dead-lettered immediately (`dead`) with the error recorded; no retry.
   *
   *  Lease discipline: each obligation is delivered under the lease held over
   *  its session. The lease is re-checked (via `heartbeat`) immediately before
   *  every send; if it has been superseded by a newer owner the poller yields
   *  without sending and leaves the obligation `pending` — so a stale owner can
   *  never race a live one into a double-send. (The residual crash-window
   *  duplicate — sent-but-not-yet-marked — is closed by the idempotency key in
   *  ccsc-o7x.2.3; the lease covers the in-process superseded-owner race.)
   *
   *  This is a SEPARATE sink from the audit journal/projection: the outbox is
   *  authoritative for *delivery*; the obligation is never written to the audit
   *  log and the projection is never made authoritative for delivery
   *  (audit-journal-architecture.md invariants).
   *
   *  `send` performs the real Slack post (injected so this stays unit-testable
   *  and the supervisor keeps zero Slack-SDK coupling). `opts.maxAttempts`
   *  defaults to `DEFAULT_MAX_DELIVERY_ATTEMPTS`; `opts.delayMs` defaults to a
   *  real timer (tests inject a stub). Best-effort + never throws: a per-
   *  obligation failure is recorded in the report and the pass continues.
   *  Returns an `OutboxDrainReport`. */
  drainOutbox(
    send: (obligation: DeliveryObligation) => Promise<void>,
    opts?: { maxAttempts?: number; delayMs?: (ms: number) => Promise<void> },
  ): Promise<OutboxDrainReport>
}

// ---------------------------------------------------------------------------
// Factory — createSessionSupervisor
// ---------------------------------------------------------------------------

/** Structured log line emitted by the supervisor. `event` is a stable
 *  identifier (e.g. `session.activate`); `fields` carries the event's
 *  payload. Consumers are expected to inject their own writer; the
 *  default writes one newline-delimited JSON object per call to stderr
 *  (stdout is the MCP stdio protocol channel and must stay clean). */
export type SupervisorLog = (event: string, fields: Record<string, unknown>) => void

/** Injection points for a SessionSupervisor. All are optional; defaults
 *  give you a production-shaped supervisor that logs to stderr and
 *  reads real wall-clock time. Tests supply their own `log` and `clock`
 *  to keep assertions deterministic. */
export interface SupervisorOptions {
  /** State directory root, e.g. `~/.claude/channels/slack`. The same
   *  root passed to `sessionPath()` and `loadSession()` in lib.ts. */
  stateRoot: string
  /** Optional structured log sink. Defaults to a stderr JSON-line
   *  writer. */
  log?: SupervisorLog
  /** Optional wall-clock source, returning epoch-ms. Defaults to
   *  `Date.now`. Injected for deterministic tests of `createdAt` and
   *  `lastActiveAt`. */
  clock?: () => number
  /** Idle threshold for the reaper, in milliseconds. A session is
   *  eligible for reaping when `clock() - session.lastActiveAt >
   *  idleMs`. Default: 4 hours (14_400_000 ms). Matches the
   *  `SLACK_SESSION_IDLE_MS` env var documented in
   *  session-state-machine.md §119. */
  idleMs?: number
  /** Lease heartbeat-lapse window in milliseconds (ccsc-o7x.1.1). A fenced
   *  write whose lease has not been renewed within this window is rejected.
   *  Default: `DEFAULT_LEASE_TTL_MS` (30s). Tests pass a small value to drive
   *  lapse detection deterministically alongside the injected `clock`. */
  leaseTtlMs?: number
  /** Identifier recorded as the `owner` of every lease this supervisor
   *  acquires (ccsc-o7x.1.1). Defaults to a per-process id. Fencing keys on the
   *  monotonic token, not the owner; this is forensic metadata for the recovery
   *  sweep (ccsc-o7x.1.2). */
  ownerId?: string
  /** Optional audit journal writer. When provided, the supervisor emits
   *  `session.activate`, `session.quiesce`, and `session.deactivate` events
   *  at the corresponding state transitions. Journal write failures are
   *  logged and swallowed — they must never interrupt message delivery or
   *  session lifecycle (audit-journal-architecture.md invariant: broken
   *  journal MUST NOT take down the hot path). */
  journal?: JournalWriter
  /** Global backpressure cap on concurrently-live sessions (ccsc-4e9bf). When
   *  set, `activate()` REJECTS a NEW session once `live + in-flight` is at the
   *  cap, so a burst (e.g. a runaway multi-agent channel) can't exhaust file
   *  handles / memory. Reactivating an already-live session is never capped.
   *  Absent → unlimited (default; behavior unchanged). */
  maxConcurrentSessions?: number
}

/** Default idle threshold: 4 hours in ms. Documented in
 *  session-state-machine.md §119. */
export const DEFAULT_IDLE_MS = 4 * 60 * 60 * 1000

/** Parse `SLACK_SESSION_IDLE_MS` from an env record and return a valid
 *  idle threshold in ms. Falls back to `DEFAULT_IDLE_MS` when the var
 *  is unset, empty, non-numeric, negative, or non-finite.
 *
 *  Pure *relative to the `env` argument*: parsing the record is
 *  deterministic and side-effect-free. The default parameter value
 *  reads `process.env` as an ergonomic fallback so the call site in
 *  server.ts boot can write `resolveIdleMs()` without repeating the
 *  env lookup. Tests pass an explicit record to keep the function
 *  deterministic at the test boundary. */
export function resolveIdleMs(env: Record<string, string | undefined> = process.env): number {
  const raw = env.SLACK_SESSION_IDLE_MS
  if (raw === undefined || raw === '') return DEFAULT_IDLE_MS
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) return DEFAULT_IDLE_MS
  return Math.floor(parsed)
}

/** Parse `SLACK_MAX_CONCURRENT_SESSIONS` (ccsc-4e9bf) → a positive integer cap,
 *  or `undefined` (= unlimited) when unset/empty/non-numeric/non-positive. Same
 *  pure-relative-to-`env` contract as `resolveIdleMs`. */
export function resolveMaxConcurrentSessions(
  env: Record<string, string | undefined> = process.env,
): number | undefined {
  const raw = env.SLACK_MAX_CONCURRENT_SESSIONS
  if (raw === undefined || raw === '') return undefined
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) return undefined
  return Math.floor(parsed)
}

/** Default structured log writer: one newline-delimited JSON object per
 *  call, written to STDERR. Keeping this internal means callers who want
 *  a different sink just pass their own `log` — no global config.
 *
 *  This must NOT write to stdout: the server speaks MCP over stdio, so
 *  stdout is the protocol channel. A structured log line there arrives
 *  at the client as an invalid JSON-RPC message (no jsonrpc/method/id
 *  keys) and Claude Code drops the whole connection — in practice every
 *  `session.activate` (one per inbound message) and every boot-time
 *  recovery-sweep line killed the transport. */
// Exported (ccsc-x0t.10) so a regression test can assert it writes to STDERR,
// never STDOUT — the stdout-is-the-MCP-protocol-channel invariant #267 fixed.
export function defaultLog(event: string, fields: Record<string, unknown>): void {
  const line = JSON.stringify({ event, ...fields })
  // process.stderr.write is sync for TTYs, async for pipes; either way
  // the supervisor does not await the flush. Structured logs are best-
  // effort; loss of a line is not a correctness issue.
  process.stderr.write(`${line}\n`)
}

/** Construct a SessionSupervisor bound to a state directory.
 *
 *  Build one of these at server boot per state root. The supervisor is
 *  long-lived; every inbound event flows through the same instance.
 *
 *  This factory currently returns a supervisor whose `activate()` is
 *  fully wired (ccsc-xa3.2) and whose `quiesce()`, `deactivate()`, and
 *  `shutdown()` throw `not yet implemented`. Those land in sibling
 *  beads (ccsc-xa3.3, ccsc-xa3.14). Handle `update()` is also staged
 *  for a later bead and currently rejects — callers of `activate()`
 *  can read state but not yet persist changes. See
 *  000-docs/session-state-machine.md §221-267 for the full target
 *  behaviour. */
export function createSessionSupervisor(opts: SupervisorOptions): SessionSupervisor {
  const log = opts.log ?? defaultLog
  const clock = opts.clock ?? Date.now
  const idleMs = opts.idleMs ?? DEFAULT_IDLE_MS
  const leaseTtlMs = opts.leaseTtlMs ?? DEFAULT_LEASE_TTL_MS
  const ownerId =
    opts.ownerId ?? `slack-supervisor-${typeof process !== 'undefined' ? process.pid : 0}`
  const { stateRoot, journal, maxConcurrentSessions } = opts

  // Process-monotonic lease token source (ccsc-o7x.1.1). Every acquisition gets
  // a strictly higher token than any prior one across all keys, so a superseded
  // owner is always fenced out by token comparison. Crash-durable monotonicity
  // across a process restart is ccsc-o7x.1.2's concern.
  let nextLeaseToken = 0
  const mintLeaseToken = (): number => ++nextLeaseToken
  // Lift the counter so the next mint is strictly above `token` (ccsc-o7x.1.2).
  // Called by the recovery sweep for every persisted token so a restarted
  // process never re-issues a token a crashed owner already held.
  const seedLeaseToken = (token: number): void => {
    if (token > nextLeaseToken) nextLeaseToken = token
  }

  /** Awaitable journal write for session lifecycle transitions. Never throws —
   *  a broken journal MUST NOT take down the session lifecycle path. Errors are
   *  forwarded to `log`. Returns a promise so callers in non-hot paths (quiesce,
   *  deactivate) can await completion before they return — this ensures that
   *  the journal file is durable before the supervisor's own state changes. */
  async function journalWrite(input: Parameters<JournalWriter['writeEvent']>[0]): Promise<void> {
    if (journal === undefined) return
    try {
      await journal.writeEvent(input)
    } catch (err: unknown) {
      log('journal.write_error', {
        kind: input.kind,
        error: err instanceof Error ? err.message : String(err),
      })
    }
  }

  // Live handles, keyed by the stringified SessionKey. Use a composite
  // string because `Map<object, ...>` keys by reference and two equal-
  // valued SessionKey literals would not collide.
  const live = new Map<string, ConcreteHandle>()

  // Quarantined keys: maps keyId → the Error that caused the quarantine.
  // Preserving the original failure reason allows activate() to surface
  // the first-failure context when it rejects. Quarantined is a sticky
  // terminal state per session-state-machine.md §129 — only an explicit
  // clearQuarantine() call removes an entry. A key in this map MUST NOT
  // also be in `live`; the two maps are disjoint by invariant.
  const quarantined = new Map<string, Error>()

  // Single-flight: concurrent activate() calls for the same key share
  // one load/create promise. Cleared after the promise settles so a
  // post-deactivate re-activation is not served a stale entry.
  const activating = new Map<string, Promise<SessionHandle>>()

  function keyId(k: SessionKey): string {
    // `\0` is not a legal character in a Slack channel/ts/user string, so it
    // is safe as a separator. Avoids the `"C1:T1" vs "C:1T1"` collision you
    // would get with a single-colon join. The trailing userId segment (empty
    // when absent) keeps a per-user key (ccsc-kl410) from ever colliding with
    // the shared (channel, thread) key.
    return `${k.channel}\0${k.thread}\0${k.userId ?? ''}`
  }

  async function doActivate(
    key: SessionKey,
    initialOwnerId: string | undefined,
  ): Promise<SessionHandle> {
    // Path validation runs first — a malformed key never touches disk.
    // Any throw here propagates; no handle is recorded.
    const path = sessionPath(stateRoot, key)

    let session: Session
    try {
      session = await loadSession(stateRoot, path)
    } catch (err) {
      if (!isNotFound(err)) {
        // Real read failure: permissions, I/O, corrupt JSON, realpath
        // escape. Per session-state-machine.md §259-267 this is a
        // Quarantined transition — record in the quarantined map so
        // subsequent activate() calls reject rather than re-attempting
        // a load that is likely still broken. Bead-filing lands in
        // ccsc-xa3.8; the map entry is the in-process forensic trail.
        const errObj = err instanceof Error ? err : new Error(String(err))
        const id = keyId(key)
        quarantined.set(id, errObj)
        log('session.activate_error', {
          channel: key.channel,
          thread: key.thread,
          error: errorMessage(err),
        })
        throw err
      }
      // ENOENT branch: this key has never been activated. Require the
      // caller to name the initial owner; otherwise refuse rather than
      // synthesize identity. Aligned with session-state-machine.md §39
      // ("the identity primitive does not accept user-authored values").
      if (initialOwnerId === undefined) {
        throw new Error(
          `activate: session file missing and no initialOwnerId provided for ${JSON.stringify(
            key,
          )}`,
        )
      }
      const now = clock()
      session = {
        v: 1,
        key,
        createdAt: now,
        lastActiveAt: now,
        ownerId: initialOwnerId,
        data: {},
      }
      await saveSession(path, session)
    }

    const handle = new ConcreteHandle(key, session, path, clock, leaseTtlMs)
    // Wire the quarantine callback so update()'s failure arm can record
    // the error in the supervisor's quarantined map AND remove the handle
    // from live. Without this the supervisor's two maps would be out of
    // sync: live still carrying a quarantined handle that activate()
    // would return instead of rejecting.
    const id = keyId(key)
    handle.onQuarantine = (err: Error) => {
      quarantined.set(id, err)
      live.delete(id)
      log('session.update_error', {
        channel: key.channel,
        thread: key.thread,
        error: errorMessage(err),
      })
    }
    handle.markActive()
    // Acquire the initial fencing lease for this active turn-owner (ccsc-o7x.1.1).
    // Every active handle holds a lease; a future re-activation by a new owner
    // mints a higher token, fencing the prior owner's late writes.
    handle.acquireLease(ownerId, mintLeaseToken())
    live.set(id, handle)

    log('session.activate', {
      channel: key.channel,
      thread: key.thread,
      ownerId: session.ownerId,
    })
    await journalWrite({
      kind: 'session.activate',
      outcome: 'n/a',
      actor: 'system',
      sessionKey: key,
    })

    return handle
  }

  return {
    activate(key: SessionKey, initialOwnerId?: string): Promise<SessionHandle> {
      const id = keyId(key)

      // Quarantined keys are a sticky terminal state per session-state-
      // machine.md §129. Reject immediately with the original failure
      // reason so the caller surfaces the first-failure context rather
      // than silently re-loading a potentially-corrupted file from disk.
      // Only a human (SO) calling clearQuarantine() unblocks this key.
      const priorErr = quarantined.get(id)
      if (priorErr !== undefined) {
        return Promise.reject(
          new Error(`SessionSupervisor.activate: key is quarantined`, { cause: priorErr }),
        )
      }

      // Cached handle wins: subsequent activate() on a live key returns
      // the same handle without re-reading the file (session-state-
      // machine.md §266 invariant).
      const existing = live.get(id)
      if (existing !== undefined) {
        return Promise.resolve(existing)
      }

      // Single-flight: if a concurrent activation is already in
      // progress, join it. The initialOwnerId from the second caller is
      // discarded — the first caller won the race and their owner
      // (if any) is the authoritative first owner.
      const inflight = activating.get(id)
      if (inflight !== undefined) {
        return inflight
      }

      // ccsc-4e9bf — global backpressure. A genuinely NEW session is refused
      // once live + in-flight activations are at the cap, so a runaway burst
      // can't exhaust resources. The load-shed decision is BOTH logged (operator
      // stderr) and journaled (audit record of the refusal, per the ccsc-4e9bf
      // acceptance criteria). The caller (deliverEvent) logs + drops the message.
      if (maxConcurrentSessions !== undefined) {
        // Count DISTINCT in-progress sessions. A key whose doActivate has
        // already resolved is briefly in BOTH `live` and `activating` (the
        // .finally cleanup runs a microtask later), so `live.size +
        // activating.size` would double-count it and could reject spuriously
        // near the cap (Gemini, PR #250). Count in-flight keys not yet in
        // `live`, plus live. `activating` is small (concurrent activations).
        let inFlightNew = 0
        for (const k of activating.keys()) if (!live.has(k)) inFlightNew++
        const active = live.size + inFlightNew
        if (active >= maxConcurrentSessions) {
          log('session.activate_rejected', {
            channel: key.channel,
            thread: key.thread,
            reason: 'max_concurrent_sessions',
            active,
            cap: maxConcurrentSessions,
          })
          // Fire-and-forget: the journal must never block the hot path (audit-
          // journal-architecture.md invariant); journalWrite is internally
          // resilient and swallows its own failures.
          void journalWrite({
            kind: 'session.activate_rejected',
            outcome: 'deny',
            actor: 'system',
            sessionKey: key,
            reason: `maxConcurrentSessions cap (${maxConcurrentSessions}) reached; active=${active}`,
          })
          return Promise.reject(
            new Error(
              `SessionSupervisor.activate: at maxConcurrentSessions cap (${maxConcurrentSessions})`,
            ),
          )
        }
      }

      const promise = doActivate(key, initialOwnerId).finally(() => {
        activating.delete(id)
      })
      activating.set(id, promise)
      return promise
    },

    async quiesce(key: SessionKey): Promise<void> {
      const id = keyId(key)
      const handle = live.get(id)
      if (handle === undefined) {
        // Nothing to drain. Per session-state-machine.md §124 a
        // quiesce() on a Nonexistent key is a no-op — there is no
        // handle to transition and no work to flush. Do not emit a
        // log line for the empty case; it adds no information and
        // would confuse the journal sink's per-session correlation.
        return
      }

      log('session.quiesce', {
        channel: key.channel,
        thread: key.thread,
        inflight: handle.inFlight.size,
      })

      // beginQuiesce() transitions the state active → quiescing synchronously.
      // The journal write follows so the state is already visible to concurrent
      // callers when the event is persisted. Journal errors never abort the
      // quiesce path — beginQuiesce already began.
      const drainPromise = handle.beginQuiesce()
      await journalWrite({
        kind: 'session.quiesce',
        outcome: 'n/a',
        actor: 'system',
        sessionKey: key,
      })

      return drainPromise
    },

    async deactivate(key: SessionKey): Promise<void> {
      const id = keyId(key)
      const handle = live.get(id)
      if (handle === undefined) {
        // No live handle — nothing to release. Matches quiesce()'s
        // Nonexistent-key no-op per session-state-machine.md §124.
        // Do not log an empty-case line; a deactivate on an already-
        // dropped key is a recovery idempotency guarantee, not an
        // event worth correlating.
        return
      }

      // Quarantined handles are out of scope per the interface contract
      // (§197-198): only a human clears the quarantine flag. Fail loudly
      // rather than silently release a handle that the supervisor has
      // marked as needing SO attention.
      if (handle.state === 'quarantined') {
        throw new Error(
          `deactivate: handle for ${JSON.stringify(key)} is quarantined; human action required`,
        )
      }

      // Deactivation is only legal after a completed quiesce. Refusing
      // the active path is how the supervisor enforces the "work has
      // drained before release" invariant — session-state-machine.md
      // §210 invariant 2. An active-state deactivate would race with
      // in-flight update()/tool calls and violate the at-most-one-
      // writer rule.
      if (handle.state !== 'quiescing') {
        throw new Error(
          `deactivate: handle for ${JSON.stringify(key)} is in state '${handle.state}'; must be quiesced first`,
        )
      }

      handle.markDeactivating()

      // Defensive final persist. `saveSession` is atomic (tmp + rename
      // under `wx`). In the current supervisor shape `session` never
      // drifts from disk between update() calls (update() is still
      // unwired and the one field mutated by the supervisor itself is
      // `_state`, which is not persisted). Still, writing here makes
      // deactivate the single "this file is now stable on disk" fence
      // so future beads that add in-memory fields (e.g. lastActiveAt
      // refresh in the reaper) don't leak drift at shutdown.
      try {
        await saveSession(handle.path, handle.session)
      } catch (err) {
        // A write failure at the deactivation boundary is not something
        // we can recover from on this handle — the on-disk copy may or
        // may not be the last-known-good. Transition to quarantine so
        // that the NEXT activate() rejects instead of silently re-
        // loading a potentially-corrupted file. Recording the error in
        // the quarantined map BEFORE removing from live ensures the
        // signal is never lost between the two maps. Bead-filing for
        // quarantine lands with the reaper work (ccsc-xa3.8); for now
        // the quarantined map entry is the forensic trail.
        handle.markQuarantined()
        quarantined.set(id, err instanceof Error ? err : new Error(String(err)))
        live.delete(id)
        log('session.deactivate_error', {
          channel: key.channel,
          thread: key.thread,
          error: errorMessage(err),
        })
        throw err
      }

      live.delete(id)

      log('session.deactivate', {
        channel: key.channel,
        thread: key.thread,
      })
      await journalWrite({
        kind: 'session.deactivate',
        outcome: 'n/a',
        actor: 'system',
        sessionKey: key,
      })
    },

    clearQuarantine(key: SessionKey): void {
      const id = keyId(key)
      // No-op if not quarantined — idempotent so repeat operator calls
      // (e.g. a script that bulk-clears) do not error.
      quarantined.delete(id)
    },

    shutdown(): Promise<void> {
      // Under ccsc-xa3.14 (deactivate + reaper sub-epic).
      return Promise.reject(
        new Error('SessionSupervisor.shutdown: not yet implemented (ccsc-xa3.14)'),
      )
    },

    async reapIdle(): Promise<void> {
      const now = clock()
      const threshold = now - idleMs

      // Snapshot candidate keys first so we don't iterate the live map
      // while mutating it through deactivate(). Capture only what the
      // filter allows; the quiesce/deactivate pair per candidate runs
      // on the snapshot list.
      const candidates: SessionKey[] = []
      for (const handle of live.values()) {
        if (handle.state !== 'active') continue
        if (handle.inFlight.size > 0) continue
        if (handle.session.lastActiveAt > threshold) continue
        candidates.push(handle.key)
      }

      if (candidates.length === 0) return

      log('session.reap_tick', {
        idleMs,
        threshold,
        candidates: candidates.length,
      })

      // Sequential rather than parallel: keeps log ordering predictable
      // and keeps contention on the filesystem (one atomic rename at a
      // time) down on reapers that drain dozens of sessions at once.
      // For a developer install the population is small; the parallel
      // win is not worth the log-interleaving loss.
      for (const key of candidates) {
        try {
          await this.quiesce(key)
          await this.deactivate(key)
        } catch (err) {
          // One quarantined or racing handle must not starve the rest
          // of the tick. Log and continue.
          log('session.reap_error', {
            channel: key.channel,
            thread: key.thread,
            error: errorMessage(err),
          })
        }
      }
    },

    async recoverOnStartup(): Promise<RecoveryReport> {
      const report: RecoveryReport = { scanned: 0, requeued: [], orphaned: [] }
      const now = clock()

      let summaries: ReturnType<typeof listSessions>
      try {
        summaries = listSessions(stateRoot)
      } catch (err) {
        // A missing/empty sessions dir is normal on first boot (listSessions
        // returns []). A real read error is logged; the sweep is best-effort
        // and must never block boot.
        log('session.recovery_scan_error', { error: errorMessage(err) })
        return report
      }

      for (const summary of summaries) {
        const key: SessionKey = { channel: summary.channel, thread: summary.thread }
        const id = keyId(key)
        const path = sessionPath(stateRoot, key)
        report.scanned++

        let session: Session
        try {
          session = await loadSession(stateRoot, path)
        } catch (err) {
          // Unreadable / corrupt during the sweep ⇒ orphan into quarantine.
          quarantined.set(id, err instanceof Error ? err : new Error(String(err)))
          report.orphaned.push(key)
          log('session.recovery', {
            channel: key.channel,
            thread: key.thread,
            decision: 'orphaned',
            reason: `unreadable: ${errorMessage(err)}`,
          })
          await journalWrite({
            kind: 'session.recovery.orphaned',
            outcome: 'n/a',
            actor: 'system',
            sessionKey: key,
          })
          continue
        }

        const turn = session.inFlightTurn
        if (turn === undefined) continue // clean session — nothing was in flight

        // Crash-durable monotonicity (ccsc-o7x.1.2): lift the token counter
        // above the persisted token regardless of the decision below, so the
        // next minted token can never collide with a crashed owner's.
        seedLeaseToken(turn.token)

        if (classifyRecovery(turn, now, leaseTtlMs) === 'resumable') {
          const { inFlightTurn: _cleared, ...clean } = session
          try {
            await saveSession(path, clean as Session)
          } catch (err) {
            // Could not clear the marker ⇒ fall back to quarantine so we never
            // leave a half-recovered session behind.
            quarantined.set(id, err instanceof Error ? err : new Error(String(err)))
            report.orphaned.push(key)
            log('session.recovery', {
              channel: key.channel,
              thread: key.thread,
              decision: 'orphaned',
              reason: `requeue-write-failed: ${errorMessage(err)}`,
            })
            await journalWrite({
              kind: 'session.recovery.orphaned',
              outcome: 'n/a',
              actor: 'system',
              sessionKey: key,
            })
            continue
          }
          report.requeued.push(key)
          log('session.recovery', {
            channel: key.channel,
            thread: key.thread,
            decision: 'requeued',
            staleMs: now - turn.heartbeatAt,
          })
          await journalWrite({
            kind: 'session.recovery.requeued',
            outcome: 'n/a',
            actor: 'system',
            sessionKey: key,
          })
        } else {
          quarantined.set(
            id,
            new Error('recovery: in-flight turn not provably abandoned (heartbeat still fresh)'),
          )
          report.orphaned.push(key)
          log('session.recovery', {
            channel: key.channel,
            thread: key.thread,
            decision: 'orphaned',
            reason: 'heartbeat-fresh',
          })
          await journalWrite({
            kind: 'session.recovery.orphaned',
            outcome: 'n/a',
            actor: 'system',
            sessionKey: key,
          })
        }
      }

      return report
    },

    async pendingDeliveries(): Promise<DeliveryObligation[]> {
      const out: DeliveryObligation[] = []
      let summaries: ReturnType<typeof listSessions>
      try {
        summaries = listSessions(stateRoot)
      } catch (err) {
        log('outbox.scan_error', { error: errorMessage(err) })
        return out
      }
      for (const summary of summaries) {
        const key: SessionKey = { channel: summary.channel, thread: summary.thread }
        let session: Session
        try {
          session = await loadSession(stateRoot, sessionPath(stateRoot, key))
        } catch (err) {
          // Best-effort: an unreadable file is skipped (the recovery sweep is
          // the path that quarantines it), never throwing here.
          log('outbox.read_error', {
            channel: key.channel,
            thread: key.thread,
            error: errorMessage(err),
          })
          continue
        }
        for (const ob of session.outbox ?? []) {
          if (ob.state === 'pending') out.push(ob)
        }
      }
      return out
    },

    async drainOutbox(
      send: (obligation: DeliveryObligation) => Promise<void>,
      opts?: { maxAttempts?: number; delayMs?: (ms: number) => Promise<void> },
    ): Promise<OutboxDrainReport> {
      const maxAttempts = opts?.maxAttempts ?? DEFAULT_MAX_DELIVERY_ATTEMPTS
      const delayMs = opts?.delayMs ?? defaultDelayMs
      const report: OutboxDrainReport = {
        scanned: 0,
        delivered: [],
        deadLettered: [],
        skipped: [],
      }

      const pending = await this.pendingDeliveries()
      for (const ob of pending) {
        report.scanned++
        const key: SessionKey = { channel: ob.channel, thread: ob.thread }

        // Activate to obtain the session's live handle + its fencing lease. A
        // quarantined / unloadable session is skipped (recovery owns it); the
        // obligation stays pending for a later pass.
        let handle: SessionHandle
        try {
          handle = await this.activate(key)
        } catch (err) {
          log('outbox.activate_error', {
            channel: key.channel,
            thread: key.thread,
            id: ob.id,
            error: errorMessage(err),
          })
          report.skipped.push(ob.id)
          continue
        }
        const lease = handle.lease
        if (lease === null) {
          report.skipped.push(ob.id)
          continue
        }
        const token = lease.token

        // In-pass retry loop with exponential backoff, bounded by maxAttempts.
        // `attempts` starts from the obligation's persisted count so retries
        // accumulate across passes too. `finalState === null` means we yielded
        // on lease loss without sending — leave the obligation pending.
        let attempts = ob.attempts
        let finalState: 'delivered' | 'dead' | null = null
        let lastError: string | undefined
        for (;;) {
          // Re-check the lease immediately before each send. `heartbeat` returns
          // false if a newer owner superseded the token (or the handle was
          // quarantined) — yield without sending so a stale owner never races a
          // live one into a double-send. On success it also renews the lease,
          // keeping it live across legitimate backoff waits.
          if (!handle.heartbeat(token)) {
            log('outbox.lease_lost', { channel: key.channel, thread: key.thread, id: ob.id })
            break
          }
          try {
            await send(ob)
            attempts++
            finalState = 'delivered'
            break
          } catch (err) {
            attempts++
            const code = extractSlackErrorCode(err)
            lastError = code ?? errorMessage(err)
            // ccsc-o7x.5 — an exfil-guard block on a file (re)upload is permanent:
            // the bytes won't pass on a retry, so dead-letter immediately rather
            // than burn maxAttempts. ExfilBlockedError carries no Slack code, so
            // classifyDeliveryError would otherwise treat it as retryable.
            if (
              err instanceof ExfilBlockedError ||
              classifyDeliveryError(code) === 'non-retryable'
            ) {
              finalState = 'dead'
              break
            }
            if (attempts >= maxAttempts) {
              // Retryable but persistently failing — dead-letter rather than
              // loop forever.
              finalState = 'dead'
              break
            }
            await delayMs(computeBackoffMs(attempts))
          }
        }

        if (finalState === null) {
          report.skipped.push(ob.id)
          continue
        }

        // Re-check the lease before committing. If it was superseded between the
        // send and now (a newer owner exists), do NOT persist — leave the
        // obligation pending for that owner. Crucially we skip *without* calling
        // the fenced `update()`, because a fenced rejection would quarantine the
        // session (the 1.3 lease-loss contract) and lock out the legitimate new
        // owner. Benign lease loss in the poller is a yield, not a quarantine.
        // (Any sent-but-not-committed duplicate is the idempotency key's job in
        // ccsc-o7x.2.3.)
        if (!handle.heartbeat(token)) {
          log('outbox.lease_lost_pre_persist', {
            channel: key.channel,
            thread: key.thread,
            id: ob.id,
          })
          report.skipped.push(ob.id)
          continue
        }

        // Persist the resolved obligation state in one fenced write. The fence
        // (same held token, just re-validated above) is belt-and-suspenders for
        // the microtask-window race; a save failure self-quarantines the handle.
        // Either way: record + skip, never throw.
        const resolved = finalState
        const resolvedAttempts = attempts
        const resolvedError = lastError
        try {
          await handle.update(
            (prev) => ({
              ...prev,
              outbox: (prev.outbox ?? []).map((o) =>
                o.id === ob.id
                  ? {
                      ...o,
                      attempts: resolvedAttempts,
                      state: resolved,
                      // Record WHY only on dead-letter — a `delivered` record needs
                      // no outstanding error (the attempt count still signals any
                      // transient retries it survived).
                      ...(resolved === 'dead' && resolvedError !== undefined
                        ? { lastError: resolvedError }
                        : {}),
                    }
                  : o,
              ),
            }),
            token,
          )
        } catch (err) {
          log('outbox.persist_error', {
            channel: key.channel,
            thread: key.thread,
            id: ob.id,
            error: errorMessage(err),
          })
          report.skipped.push(ob.id)
          continue
        }

        if (resolved === 'delivered') {
          report.delivered.push(ob.id)
        } else {
          report.deadLettered.push({ id: ob.id, error: resolvedError ?? 'unknown' })
        }
      }

      return report
    },
  }
}

// ---------------------------------------------------------------------------
// Internal — ConcreteHandle
// ---------------------------------------------------------------------------

/** In-process implementation of SessionHandle.
 *
 *  Not exported: callers consume the `SessionHandle` interface. Keeping
 *  the class private lets later beads (update(), deactivate()) grow its
 *  internals without widening the public surface.
 *
 *  Current scope:
 *    - ccsc-xa3.2 — identity, state, snapshot, in-flight map allocation,
 *      markActive() transition.
 *    - ccsc-xa3.3 — beginQuiesce()/beginWork()/endWork() drain mechanics
 *      and the active → quiescing transition.
 *    - update() body and Quiescing → Deactivating / cancellation edges
 *      land in later beads. */
class ConcreteHandle implements SessionHandle {
  readonly key: SessionKey
  session: Session

  // Backing field for the public `state` accessor. Starts in
  // 'activating' so a consumer who somehow observes the handle before
  // markActive() runs sees the honest transient state rather than a
  // false 'active'.
  private _state: SessionState = 'activating'

  /** Per-request AbortControllers for tool calls dispatched against
   *  this session. Populated by `beginWork()` (called from server.ts's
   *  tool-call path in ccsc-xa3.15); cleared by `endWork()` when the
   *  call settles. Quiesce waits for this map to drain; shutdown will
   *  abort every entry before deactivating (ccsc-xa3.14). */
  readonly inFlight: Map<string, AbortController> = new Map()

  /** Resolved path this session's file lives at. Kept on the handle so
   *  later beads' `update()` and deactivate paths do not re-run
   *  `sessionPath()` (which would re-mkdir the parent). */
  readonly path: string

  /** Mutex tail for serialised `update()` calls. Each call chains its
   *  work onto this promise so concurrent updates run in strict call
   *  order without interleaving. Initialized to a resolved promise so
   *  the first update starts immediately. The chain carries
   *  `Promise<void>` throughout; individual links catch their own errors
   *  to prevent a rejected link from collapsing the whole chain. */
  private writeQueue: Promise<void> = Promise.resolve()

  /** In-flight drain promise allocated by `beginQuiesce()`. Null when
   *  the handle is Active (nothing to drain). Callers of quiesce share
   *  this promise so concurrent quiesce() requests do not allocate
   *  multiple drains. */
  private quiescePromise: Promise<void> | null = null

  /** Resolver for `quiescePromise`. Called by `endWork()` when the
   *  last in-flight entry drains, or directly by `beginQuiesce()` when
   *  the map is already empty at quiesce time. */
  private resolveQuiesce: (() => void) | null = null

  /** Callback invoked when `update()` transitions the handle to
   *  `quarantined`. The supervisor injects this so its `quarantined` map
   *  stays consistent: a quarantine triggered inside the write queue
   *  must be recorded in the same map that `activate()` checks, or a
   *  subsequent activate() would silently reload a potentially-corrupt
   *  file instead of rejecting. Set once by the supervisor after
   *  construction; never null after `markActive()`. */
  onQuarantine: ((err: Error) => void) | null = null

  /** The fencing lease over this handle's active turn (ccsc-o7x.1.1). Null
   *  until the supervisor calls `acquireLease()` right after `markActive()`.
   *  Renewed in place by `heartbeat()`; read via the public `lease` getter. */
  private _lease: Lease | null = null

  /** Wall-clock source (epoch-ms), injected by the supervisor for deterministic
   *  lease heartbeat/lapse tests. */
  private readonly clock: () => number

  /** Lease heartbeat-lapse window (ms). A fenced write whose lease is older
   *  than this is rejected. */
  private readonly leaseTtlMs: number

  constructor(
    key: SessionKey,
    session: Session,
    path: string,
    clock: () => number,
    leaseTtlMs: number,
  ) {
    this.key = key
    this.session = session
    this.path = path
    this.clock = clock
    this.leaseTtlMs = leaseTtlMs
  }

  get state(): SessionState {
    return this._state
  }

  get lease(): Lease | null {
    return this._lease
  }

  /** Acquire a fresh fencing lease for `owner` with the supervisor-minted
   *  monotonic `token`, heartbeat-stamped at the current clock. Supersedes any
   *  prior lease on this handle (a higher token fences the old owner out).
   *  Called by the supervisor immediately after `markActive()`. (ccsc-o7x.1.1) */
  acquireLease(owner: string, token: number): Lease {
    const lease: Lease = { token, owner, heartbeatAt: this.clock() }
    this._lease = lease
    return lease
  }

  /** Renew the lease heartbeat if `token` is the current owner's. Returns
   *  `false` (no renewal) when no lease is held or the token has been
   *  superseded — the caller has been fenced. (ccsc-o7x.1.1) */
  heartbeat(token: number): boolean {
    const lease = this._lease
    if (lease === null || lease.token !== token) return false
    this._lease = heartbeatLease(lease, this.clock())
    return true
  }

  /** Persist an in-flight-turn marker so a crash mid-turn leaves a recoverable
   *  trace for `recoverOnStartup` (ccsc-o7x.1.2). Fenced by `token` (must be the
   *  current lease's) and persisted via the same atomic `update()` path. */
  recordTurnStart(token: number): Promise<void> {
    const lease = this._lease
    if (lease === null || lease.token !== token) {
      return Promise.reject(
        new Error(`recordTurnStart: token does not match the current lease (presented ${token})`),
      )
    }
    const now = this.clock()
    const marker: InFlightTurn = { owner: lease.owner, token, startedAt: now, heartbeatAt: now }
    return this.update((prev) => ({ ...prev, inFlightTurn: marker }), token)
  }

  /** Clear the in-flight-turn marker on clean turn completion (ccsc-o7x.1.2).
   *  Fenced by the current lease token when one is held. A no-op persist when
   *  the marker is already absent. */
  recordTurnEnd(): Promise<void> {
    const token = this._lease?.token
    return this.update((prev) => {
      if (prev.inFlightTurn === undefined) return prev
      const { inFlightTurn: _cleared, ...rest } = prev
      return rest as Session
    }, token)
  }

  recordTerminalDelivery(
    token: number,
    reply: {
      id: string
      channel: string
      thread: string
      payload: string
      blocks?: Array<Record<string, unknown>>
    },
  ): Promise<void> {
    const obligation: DeliveryObligation = {
      id: reply.id,
      channel: reply.channel,
      thread: reply.thread,
      payload: reply.payload,
      ...(reply.blocks !== undefined ? { blocks: reply.blocks } : {}),
      attempts: 0,
      state: 'pending',
      createdAt: this.clock(),
    }
    // One atomic save: append the obligation AND clear the in-flight marker, so
    // "turn done, reply owed" is a single durable fact. Fenced by the lease
    // token — a turn that lost its lease must not enqueue a delivery.
    return this.update((prev) => {
      const { inFlightTurn: _cleared, ...rest } = prev
      return { ...rest, outbox: [...(prev.outbox ?? []), obligation] }
    }, token)
  }

  recordTerminalDeliveries(
    token: number,
    replies: readonly {
      id: string
      channel: string
      thread: string
      payload: string
      blocks?: Array<Record<string, unknown>>
      // ccsc-o7x.5 — when present, this is a durable FILE-upload obligation.
      upload?: { path: string; filename: string; comment?: string }
    }[],
  ): Promise<void> {
    const now = this.clock()
    const obligations: DeliveryObligation[] = replies.map((reply) => ({
      id: reply.id,
      channel: reply.channel,
      thread: reply.thread,
      payload: reply.payload,
      attempts: 0,
      state: 'pending',
      createdAt: now,
      ...(reply.blocks !== undefined ? { blocks: reply.blocks } : {}),
      ...(reply.upload !== undefined ? { upload: reply.upload } : {}),
    }))
    // One atomic save appends ALL obligations AND clears the in-flight marker:
    // a chunked reply's "turn done, N replies owed" is a single durable fact.
    // All-or-nothing — a crash during this write leaves either zero or all N
    // obligations, never a partial set (which would deliver some chunks and
    // silently drop the rest). Fenced by the lease token. The obligations append
    // in `replies` order so the poller drains them into the thread in order.
    return this.update((prev) => {
      const { inFlightTurn: _cleared, ...rest } = prev
      return { ...rest, outbox: [...(prev.outbox ?? []), ...obligations] }
    }, token)
  }

  /** Transition from `activating` → `active`. Called by the supervisor
   *  once the handle is fully wired and live in the map. Package-
   *  private by convention; callers outside this file must not invoke
   *  it. Later beads replace this with a proper state-transition method
   *  that accepts the full FSM. */
  markActive(): void {
    this._state = 'active'
  }

  /** Transition from `quiescing` → `deactivating`. Only the supervisor
   *  invokes this, and only after the drain promise has resolved.
   *  Package-private by convention; external callers must go through
   *  `SessionSupervisor.deactivate()`. */
  markDeactivating(): void {
    this._state = 'deactivating'
  }

  /** Transition to `quarantined`. Terminal from the supervisor's
   *  perspective — only a human clears it. Called on save-path
   *  failures that leave the on-disk state uncertain. */
  markQuarantined(): void {
    this._state = 'quarantined'
  }

  /** Drive this handle into the quarantine terminal AND notify the supervisor
   *  so its live + quarantined maps stay in sync — without that, a subsequent
   *  `activate()` would hand back this now-quarantined handle from the live map
   *  instead of rejecting (sticky-quarantine invariant). Idempotent: a no-op
   *  once already quarantined, so it never double-fires `onQuarantine`. Shared
   *  by the save-failure path and the lease-loss fence in `update()`
   *  (ccsc-o7x.1.3). */
  private quarantineSelf(err: Error): void {
    if (this._state === 'quarantined') return
    this._state = 'quarantined'
    this.onQuarantine?.(err)
  }

  /** Begin a graceful drain. Transitions state `active` → `quiescing`
   *  and returns a promise that resolves when the in-flight map reaches
   *  zero entries. Contract:
   *
   *    - Idempotent when already quiescing: returns the existing drain
   *      promise so two concurrent callers share one drain.
   *    - Idempotent no-op when the in-flight map is already empty:
   *      resolves on the next microtask to preserve the promise
   *      ordering callers expect.
   *    - Rejects if called from any state other than `active` or
   *      `quiescing` — the FSM has no edge there.
   *
   *  Called by `SessionSupervisor.quiesce()`. Not a SessionHandle
   *  interface method; consumers use the supervisor's quiesce() entry
   *  point which emits the `session.quiesce` log line. */
  beginQuiesce(): Promise<void> {
    if (this._state === 'quiescing') {
      // Join the already-running drain (session-state-machine.md §266
      // documents quiesce() as idempotent — a second call receives the
      // first's promise).
      if (this.quiescePromise === null) {
        // Defensive: state is quiescing but no promise was recorded.
        // That's a programmer error (markActive / beginQuiesce sequence
        // violated). Fail loudly rather than silently synthesize. The
        // key is included so the journal sink can correlate the bug
        // back to the offending session without grepping the running
        // process.
        return Promise.reject(
          new Error(
            `beginQuiesce: quiescing state without drain promise for ${JSON.stringify(this.key)}`,
          ),
        )
      }
      return this.quiescePromise
    }

    if (this._state !== 'active') {
      return Promise.reject(new Error(`beginQuiesce: cannot quiesce from state '${this._state}'`))
    }

    this._state = 'quiescing'

    this.quiescePromise = new Promise<void>((resolve) => {
      this.resolveQuiesce = resolve
    })

    // If nothing is in flight at quiesce time, resolve on the next
    // microtask. Queueing (rather than resolving inline) keeps the
    // promise-returns-before-handler semantic consistent with the
    // drain-via-endWork() path, so callers cannot accidentally depend
    // on synchronous resolution.
    if (this.inFlight.size === 0) {
      queueMicrotask(() => {
        this.resolveQuiesce?.()
      })
    }

    return this.quiescePromise
  }

  /** Register an AbortController for an in-flight tool call and return
   *  it to the caller. The caller's responsibility is to invoke
   *  `endWork(requestId)` when the call settles. On shutdown (ccsc-
   *  xa3.14) the supervisor will call `.abort()` on every entry still
   *  in the map.
   *
   *  Not used in this bead — xa3.15 wires it into the tool-call path.
   *  Published here so `beginQuiesce()` has a real drain contract to
   *  honour and tests can exercise the drain path. */
  beginWork(requestId: string): AbortController {
    if (this.inFlight.has(requestId)) {
      throw new Error(`beginWork: requestId already in flight: '${requestId}'`)
    }
    const ctrl = new AbortController()
    this.inFlight.set(requestId, ctrl)
    return ctrl
  }

  /** Mark a tool call complete. Removes the controller from the in-
   *  flight map and, if the handle is quiescing and the map is now
   *  empty, resolves the drain promise. Safe to call with an unknown
   *  requestId — treated as a no-op so crash-recovery bookkeeping
   *  that double-ends is not a fatal error. */
  endWork(requestId: string): void {
    const had = this.inFlight.delete(requestId)
    if (!had) return

    if (this._state === 'quiescing' && this.inFlight.size === 0) {
      this.resolveQuiesce?.()
    }
  }

  /** Serialise a state mutation through the per-session write mutex,
   *  persist it atomically, and refresh `this.session` on success.
   *
   *  The write queue is a promise chain: each call appends a new link
   *  and returns a promise that resolves only after the previous link
   *  settles. Links catch their own errors so a failed update does not
   *  prevent subsequent calls from running — the handle quarantines
   *  itself and further calls will immediately reject at the state check.
   *
   *  Implementation mirrors the `deactivate()` save path: both use
   *  `saveSession()` (tmp + chmod + rename from lib.ts) and both
   *  transition to `quarantined` on save failure. */
  update(fn: (prev: Session) => Session, fenceToken?: number): Promise<void> {
    // Capture state at enqueue time for the early-exit checks below.
    // We re-check after acquiring the mutex because state can change
    // while waiting in the queue (a concurrent quiesce, for example).
    const enqueueTimeState = this._state

    if (enqueueTimeState === 'quarantined') {
      return Promise.reject(new Error(`SessionHandle.update: handle is quarantined`))
    }
    if (enqueueTimeState !== 'active') {
      // Covers 'quiescing', 'deactivating', and 'activating'. Include the
      // actual state so callers can distinguish the cases without inspecting
      // `handle.state` separately.
      return Promise.reject(
        new Error(`SessionHandle.update: handle is not active (state: ${enqueueTimeState})`),
      )
    }

    // Expose a stable Promise<void> to the caller that resolves/rejects
    // based solely on this link's outcome.
    let resolve!: () => void
    let reject!: (err: unknown) => void
    const callerPromise = new Promise<void>((res, rej) => {
      resolve = res
      reject = rej
    })

    // Chain the work unit onto the write queue. The link must catch all
    // errors to avoid collapsing the chain — the original rejection is
    // forwarded to the caller via `callerPromise`.
    this.writeQueue = this.writeQueue.then(async () => {
      // Re-check state now that we hold the mutex. A concurrent quiesce
      // or a previous update's quarantine may have changed things.
      if (this._state === 'quarantined') {
        reject(new Error(`SessionHandle.update: handle is quarantined`))
        return
      }
      if (this._state !== 'active') {
        reject(new Error(`SessionHandle.update: handle is not active (state: ${this._state})`))
        return
      }

      // Fenced write (ccsc-o7x.1.1): evaluate the lease at write time, inside
      // the mutex, because a newer owner could have superseded the token (or it
      // could have lapsed) while this write waited in the queue. `fn` is not
      // called and nothing is persisted on a fenced rejection.
      // A fenced write means the owner has LOST its lease — either a newer
      // owner superseded its token or its heartbeat lapsed. Per ccsc-o7x.1.3
      // this is not a transient retry: route the session through the existing
      // quarantine terminal so it performs no further tool calls or sends and
      // is excluded from the active set, rather than letting a possibly-
      // split-brained turn keep acting. (The fenceToken is the owner's own
      // held lease token, so a mismatch is a real loss, not a stray caller.)
      if (fenceToken !== undefined) {
        const lease = this._lease
        if (lease === null || lease.token !== fenceToken) {
          const err = new Error(
            `SessionHandle.update: write fenced — lease lost (no live lease or token superseded; presented ${fenceToken}); handle quarantined`,
          )
          this.quarantineSelf(err)
          reject(err)
          return
        }
        if (isLeaseStale(lease, this.clock(), this.leaseTtlMs)) {
          const err = new Error(
            `SessionHandle.update: write fenced — lease heartbeat lapsed; handle quarantined`,
          )
          this.quarantineSelf(err)
          reject(err)
          return
        }
      }

      const prev = this.session
      const next = fn(prev)

      try {
        await saveSession(this.path, next)
        this.session = next
        resolve()
      } catch (err) {
        // Save failure: quarantine the handle so future update() and
        // activate() calls fail fast. In-memory session reverts to
        // `prev` (it was never reassigned). This mirrors the deactivate()
        // failure arm exactly (session-state-machine.md §132-137).
        const errObj = err instanceof Error ? err : new Error(String(err))
        this.quarantineSelf(errObj)
        reject(
          new Error(`SessionHandle.update: save failed; handle quarantined`, {
            cause: errObj,
          }),
        )
      }
    })

    return callerPromise
  }
}

// ---------------------------------------------------------------------------
// Internal — error helpers
// ---------------------------------------------------------------------------

/** True for errors thrown by `loadSession` when the session file does
 *  not exist yet. `realpathSync.native` surfaces a NodeJS.ErrnoException
 *  with `code === 'ENOENT'`; we check `code` defensively in case the
 *  error was wrapped. */
function isNotFound(err: unknown): boolean {
  if (typeof err !== 'object' || err === null) return false
  const e = err as { code?: unknown }
  return e.code === 'ENOENT'
}

/** Best-effort error message extractor for structured logs. Uses
 *  `Error.message` when available; falls back to the stringified value
 *  so non-Error throws (string, number) still log something. */
function errorMessage(err: unknown): string {
  if (err instanceof Error) return err.message
  return String(err)
}
