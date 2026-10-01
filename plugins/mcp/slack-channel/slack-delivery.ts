/**
 * slack-delivery.ts — Slack-facing glue for the reply-delivery outbox poller
 * (ccsc-o7x.3).
 *
 * The crash-safety epic (ccsc-o7x) makes a terminal turn's reply loss-proof:
 * the reply is recorded as a durable obligation (ccsc-o7x.2.1), drained by a
 * leased, retrying poller (ccsc-o7x.2.2), and made idempotent so a redelivery
 * after a lost ack never double-posts (ccsc-o7x.2.3). All of THAT logic lives
 * in the vendored `lib.ts` kernel (`makeIdempotentSend`,
 * `deliveryIdempotencyKey`) and `supervisor.ts` (`drainOutbox`).
 *
 * This module is the thin I/O adapter that binds that logic to a real Slack
 * `WebClient` — `findDelivered` (look up our own prior post by its stamped
 * idempotency key) and `post` (send with the key stamped into message
 * metadata). It is deliberately a sibling module, not inline in `server.ts`,
 * so it can be unit-tested against a faked `WebClient` without triggering
 * `server.ts`'s module-load side effects (token load, Socket Mode, `main()`).
 *
 * No Slack-SDK code crosses into `lib.ts`: the kernel stays vendorable by AGP;
 * this Slack glue stays in CCSC.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

import type { WebClient } from '@slack/web-api'
import {
  classifyDeliveryError,
  DELIVERY_METADATA_EVENT_TYPE,
  type DeliveryObligation,
  deliveryIdempotencyKey,
  ExfilBlockedError,
  extractSlackErrorCode,
  type IdempotentSendDeps,
} from './lib.ts'
import type { SessionHandle, SessionSupervisor } from './supervisor.ts'

/** Shape of a `conversations.replies` message we care about — just the `ts` and
 *  the message `metadata` (returned when the request sets
 *  `include_all_metadata`). Narrowed locally because the Slack SDK types the
 *  reply union loosely. */
interface ReplyMessage {
  ts?: string
  metadata?: { event_type?: string; event_payload?: Record<string, unknown> }
}

/** Build the production `IdempotentSendDeps` the outbox poller consumes, bound
 *  to a Slack `WebClient`.
 *
 *  - `findDelivered` scans the destination thread (`conversations.replies` with
 *    `include_all_metadata`) for a message we previously posted carrying our
 *    delivery `event_type` and a matching idempotency key. A hit means the reply
 *    already landed (e.g. a prior attempt posted but its ack was lost), so the
 *    redelivery must be a no-op — it returns the existing `ts`. No thread parent
 *    ⇒ `null` (a non-threaded post can't be looked up this way; the in-process
 *    lease still guards the live race, and CCSC sessions are thread-keyed so
 *    obligations carry a thread in practice).
 *  - `post` sends the reply with the idempotency key stamped into Slack message
 *    `metadata`, so a later `findDelivered` can recognise it.
 *
 *  The idempotency *decision* lives in `makeIdempotentSend` (lib.ts); this only
 *  supplies the two Slack calls it composes. */
export function createDeliverySendDeps(client: WebClient): IdempotentSendDeps {
  const replyPoster = createReplyPoster(client)
  return {
    async findDelivered(channel: string, thread: string, key: string): Promise<string | null> {
      if (!thread) return null
      const res = await client.conversations.replies({
        channel,
        ts: thread,
        limit: 200,
        include_all_metadata: true,
      })
      const messages = (res.messages ?? []) as ReplyMessage[]
      for (const m of messages) {
        if (
          m.metadata?.event_type === DELIVERY_METADATA_EVENT_TYPE &&
          m.metadata.event_payload?.idempotency_key === key
        ) {
          return (m.ts as string) || 'delivered'
        }
      }
      return null
    },
    // The poller discards the ts; the inline durable send wants it. Both share
    // one metadata-stamping site (`createReplyPoster`) so the delivery key is
    // written identically on every path.
    async post(obligation, key): Promise<void> {
      await replyPoster(obligation, key)
    },
  }
}

/** Post a reply with the idempotency key stamped into Slack message `metadata`,
 *  returning the resulting `ts`. The single place the delivery metadata is
 *  written — shared by the poller's `post` (which discards the ts) and the
 *  inline durable send via `deliverReplyDurably` (which needs the ts for the
 *  tool result). Bound to a `WebClient`. (ccsc-o7x.3) */
export function createReplyPoster(client: WebClient): ReplyPoster {
  return async (obligation, key) => {
    const res = await client.chat.postMessage({
      channel: obligation.channel,
      text: obligation.payload,
      ...(obligation.blocks !== undefined ? { blocks: obligation.blocks as any } : {}),
      thread_ts: obligation.thread || undefined,
      unfurl_links: false,
      unfurl_media: false,
      metadata: {
        event_type: DELIVERY_METADATA_EVENT_TYPE,
        event_payload: { idempotency_key: key },
      },
    })
    return (res.ts as string) || undefined
  }
}

// ---------------------------------------------------------------------------
// Durable single-message reply delivery (ccsc-o7x.3 pt2 — ADR-002 addendum)
// ---------------------------------------------------------------------------

/** Raised when durable delivery cannot even begin — the session can't be
 *  activated, or it holds no lease — *before* any obligation is recorded or any
 *  send attempted. The caller catches this and falls back to a best-effort
 *  direct send; nothing was persisted, so there is no obligation to redeliver. */
export class DurableUnavailableError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'DurableUnavailableError'
  }
}

/** One logical reply to deliver durably. `id` is the caller-supplied stable
 *  unique key (a fresh UUID per reply call) — it becomes the obligation id and
 *  thus the idempotency key, so a poller redelivery of THIS obligation dedups
 *  exactly. */
export interface DurableReply {
  id: string
  channel: string
  thread: string
  text: string
  /** Block Kit blocks for a rich-layout reply; `text` is the notification
   *  fallback. Recorded on the obligation so poller redelivery re-sends the
   *  same rich message. */
  blocks?: Array<Record<string, unknown>>
}

export type DurableDeliveryResult =
  | { status: 'delivered'; ts: string | undefined }
  | { status: 'queued' }

/** Post one reply, stamping the idempotency key into Slack message metadata,
 *  and return the resulting `ts` (the inline attempt wants it for the tool
 *  result). Distinct from `IdempotentSendDeps.post` (which returns `void` for
 *  the poller). The production impl wraps `web.chat.postMessage`. */
export type ReplyPoster = (
  obligation: DeliveryObligation,
  idempotencyKey: string,
) => Promise<string | undefined>

/** Durable single-message reply delivery (ADR-002 addendum, Option A). Records
 *  a `pending` obligation BEFORE the send — so a crash before/at the send leaves
 *  a recoverable record the boot-drain redelivers — then attempts exactly ONE
 *  inline send and resolves:
 *
 *    - **success**        → mark `delivered`, return the Slack `ts`;
 *    - **transient error**→ bump `attempts`, leave `pending`, return `queued`
 *      (the poller redelivers idempotently — the caller must NOT retry, or it
 *      would double-post);
 *    - **non-retryable**  → mark `dead` (error recorded) and rethrow the Slack
 *      error so the caller surfaces the real failure to the agent.
 *
 *  Throws `DurableUnavailableError` *before recording* if the session can't be
 *  activated or holds no lease — the caller falls back to a direct send.
 *
 *  Marking the obligation state is best-effort: if the fenced mark write fails
 *  (lease lost mid-flight), the obligation simply stays as the prior process saw
 *  it and the poller reconciles from disk (a delivered-but-unmarked message is
 *  deduped by `findDelivered`, a still-pending one is redelivered). So a mark
 *  failure never fails the reply. (ccsc-o7x.3) */
export async function deliverReplyDurably(
  deps: { supervisor: SessionSupervisor; post: ReplyPoster },
  reply: DurableReply,
): Promise<DurableDeliveryResult> {
  let handle: SessionHandle
  try {
    handle = await deps.supervisor.activate({ channel: reply.channel, thread: reply.thread })
  } catch (err) {
    throw new DurableUnavailableError(
      `cannot activate session: ${err instanceof Error ? err.message : String(err)}`,
    )
  }
  const lease = handle.lease
  if (lease === null) throw new DurableUnavailableError('session holds no lease')
  const token = lease.token

  // Record the durable obligation BEFORE the send (crash-before-send safe).
  await handle.recordTerminalDelivery(token, {
    id: reply.id,
    channel: reply.channel,
    thread: reply.thread,
    payload: reply.text,
    ...(reply.blocks !== undefined ? { blocks: reply.blocks } : {}),
  })
  const obligation: DeliveryObligation = {
    id: reply.id,
    channel: reply.channel,
    thread: reply.thread,
    payload: reply.text,
    ...(reply.blocks !== undefined ? { blocks: reply.blocks } : {}),
    attempts: 0,
    state: 'pending',
    createdAt: 0,
  }
  const idemKey = deliveryIdempotencyKey(obligation)

  try {
    const ts = await deps.post(obligation, idemKey)
    await markObligation(handle, token, reply.id, { state: 'delivered', attempts: 1 })
    return { status: 'delivered', ts }
  } catch (err) {
    const code = extractSlackErrorCode(err)
    const lastError = code ?? (err instanceof Error ? err.message : String(err))
    if (classifyDeliveryError(code) === 'non-retryable') {
      await markObligation(handle, token, reply.id, { state: 'dead', attempts: 1, lastError })
      throw err
    }
    // Transient: leave pending (attempts bumped so the poller dedups) + queued.
    await markObligation(handle, token, reply.id, { state: 'pending', attempts: 1, lastError })
    return { status: 'queued' }
  }
}

// ---------------------------------------------------------------------------
// Durable chunked (multi-message) reply delivery (ccsc-o7x.4)
// ---------------------------------------------------------------------------

/** One logical reply that spans multiple Slack messages. `chunks` is the
 *  pre-split payload (the caller runs `chunkText`); each chunk becomes its own
 *  obligation with id `<id>:<i>`, so it carries a distinct idempotency key and a
 *  crash mid-way redelivers only the chunks that did not land. `chunks` must be
 *  non-empty; a single-element array is valid, but the single-message
 *  `deliverReplyDurably` is the lighter path for that case. */
export interface DurableChunkedReply {
  id: string
  channel: string
  thread: string
  chunks: string[]
}

export type DurableChunkedDeliveryResult =
  | { status: 'delivered'; ts: string | undefined; sent: number }
  | { status: 'queued'; delivered: number; pending: number }

/** Durable multi-message reply delivery (ccsc-o7x.4) — the chunked sibling of
 *  `deliverReplyDurably`. One reply → N chunks → N obligations, each with id
 *  `<reply.id>:<i>` (a distinct idempotency key per chunk).
 *
 *  Records ALL N obligations in ONE atomic write BEFORE any send
 *  (`recordTerminalDeliveries`) — so a crash before/at any send leaves a
 *  recoverable, all-or-nothing record the boot-drain redelivers. Then posts the
 *  chunks IN ORDER, each under its own idempotency key:
 *
 *    - every chunk posts            → all `delivered`, return the FIRST chunk's
 *      `ts`;
 *    - a transient error on chunk i → mark i `pending` and STOP (do NOT post
 *      i+1…): the poller redelivers i…N-1 in order, so chunks never land out of
 *      order. Return `queued` (the caller must NOT retry — that would double-post
 *      the already-sent prefix);
 *    - a non-retryable error on chunk i → mark i `dead` and rethrow so the agent
 *      sees the real failure. Chunks 0…i-1 already landed (a partial reply — the
 *      honest outcome); i+1…N stay pending and the poller attempts/dead-letters
 *      them (a channel-wide non-retryable error dead-letters them the same way).
 *
 *  Throws `DurableUnavailableError` BEFORE recording if the session can't be
 *  activated or holds no lease — the caller falls back to a direct send.
 *
 *  Order guarantee: per-chunk obligations append in order and the poller drains a
 *  session's outbox in array order (`pendingDeliveries` + `drainOutbox`); the
 *  inline path posts in order and stops at the first transient gap. So a chunk
 *  never lands ahead of an earlier one — inline or via the poller. (ccsc-o7x.4) */
export async function deliverChunkedReplyDurably(
  deps: { supervisor: SessionSupervisor; post: ReplyPoster },
  reply: DurableChunkedReply,
): Promise<DurableChunkedDeliveryResult> {
  let handle: SessionHandle
  try {
    handle = await deps.supervisor.activate({ channel: reply.channel, thread: reply.thread })
  } catch (err) {
    throw new DurableUnavailableError(
      `cannot activate session: ${err instanceof Error ? err.message : String(err)}`,
    )
  }
  const lease = handle.lease
  if (lease === null) throw new DurableUnavailableError('session holds no lease')
  const token = lease.token

  // One obligation per chunk; the id folds in the chunk index so each carries a
  // distinct idempotency key (`ccsc-reply:<reply.id>:<i>`).
  const records = reply.chunks.map((payload, i) => ({
    id: `${reply.id}:${i}`,
    channel: reply.channel,
    thread: reply.thread,
    payload,
  }))

  // Record ALL N before ANY send (crash-before-send safe, all-or-nothing).
  await handle.recordTerminalDeliveries(token, records)

  let firstTs: string | undefined
  let delivered = 0
  for (const record of records) {
    const obligation: DeliveryObligation = { ...record, attempts: 0, state: 'pending', createdAt: 0 }
    const idemKey = deliveryIdempotencyKey(obligation)
    try {
      const ts = await deps.post(obligation, idemKey)
      if (delivered === 0) firstTs = ts
      await markObligation(handle, token, obligation.id, { state: 'delivered', attempts: 1 })
      delivered++
    } catch (err) {
      const code = extractSlackErrorCode(err)
      const lastError = code ?? (err instanceof Error ? err.message : String(err))
      if (classifyDeliveryError(code) === 'non-retryable') {
        await markObligation(handle, token, obligation.id, { state: 'dead', attempts: 1, lastError })
        throw err
      }
      // Transient: leave this chunk (and every later one) pending and STOP — the
      // poller redelivers the tail in order. Posting later chunks inline now
      // would land them ahead of this one once it retries.
      await markObligation(handle, token, obligation.id, {
        state: 'pending',
        attempts: 1,
        lastError,
      })
      return { status: 'queued', delivered, pending: records.length - delivered }
    }
  }
  return { status: 'delivered', ts: firstTs, sent: delivered }
}

// ---------------------------------------------------------------------------
// Durable streaming reply finalize (ccsc-o7x.6 — ADR-002 addendum)
// ---------------------------------------------------------------------------

/** A streaming reply to make crash-durable. `id` is a fresh per-reply UUID (the
 *  obligation id and thus idempotency key); `text` is the COMPLETE reply text —
 *  the stream-finalize payload the poller redelivers on a crash, NOT a chunk. */
export interface DurableStream {
  id: string
  channel: string
  thread: string
  text: string
}

/** Handle returned by `beginDurableStream` so the caller can resolve the
 *  stream-finalize obligation once `streamReply` returns. Call EXACTLY ONE of
 *  `markDelivered` (stream completed) / `markDead` (stream failed in-process).
 *  Calling neither — the process crashed mid-stream — is the whole point: the
 *  obligation stays `pending` and the poller redelivers. Both marks are
 *  best-effort (a fenced mark failure leaves the poller to reconcile from disk)
 *  and never throw. */
export interface DurableStreamHandle {
  markDelivered(): Promise<void>
  markDead(reason: string): Promise<void>
}

/** Record a stream-finalize obligation BEFORE a streaming reply begins
 *  (ccsc-o7x.6, ADR-002 addendum). Activates the `(channel, thread)` session and
 *  appends ONE `pending` `DeliveryObligation` carrying the FULL reply text, then
 *  returns a handle to resolve it once the stream ends:
 *
 *    - stream COMPLETES        → `markDelivered()` — the streamed message holds
 *      the full content; nothing is owed;
 *    - stream FAILS in-process → `markDead(reason)` — NOT left pending: the
 *      poller's send does not re-run the outbound gate, and `streamReply` cannot
 *      distinguish a gate rejection from a transient Slack error, so a
 *      gate-rejected stream must never be auto-redelivered. The partial message
 *      that landed is the same best-effort outcome as before;
 *    - process CRASHES mid-stream → neither mark runs, the obligation stays
 *      `pending`, and the boot-drain / poller redelivers the full text as a fresh
 *      `chat.postMessage` (the partial streamed message is orphaned).
 *
 *  Throws `DurableUnavailableError` BEFORE recording if the session can't be
 *  activated or holds no lease — the caller then streams best-effort, no net
 *  (prior behavior). Mirrors `deliverReplyDurably`'s activate→lease→record
 *  prologue; the difference is the send is the caller's progressive stream, not
 *  an inline post, so this only records + hands back the resolve hooks. */
export async function beginDurableStream(
  deps: { supervisor: SessionSupervisor },
  reply: DurableStream,
): Promise<DurableStreamHandle> {
  let handle: SessionHandle
  try {
    handle = await deps.supervisor.activate({ channel: reply.channel, thread: reply.thread })
  } catch (err) {
    throw new DurableUnavailableError(
      `cannot activate session: ${err instanceof Error ? err.message : String(err)}`,
    )
  }
  const lease = handle.lease
  if (lease === null) throw new DurableUnavailableError('session holds no lease')
  const token = lease.token

  // Record the full-text obligation BEFORE the stream starts (crash-before /
  // crash-during-stream safe).
  await handle.recordTerminalDelivery(token, {
    id: reply.id,
    channel: reply.channel,
    thread: reply.thread,
    payload: reply.text,
  })

  return {
    markDelivered(): Promise<void> {
      return markObligation(handle, token, reply.id, { state: 'delivered', attempts: 1 })
    },
    markDead(reason: string): Promise<void> {
      return markObligation(handle, token, reply.id, { state: 'dead', attempts: 1, lastError: reason })
    },
  }
}

// ---------------------------------------------------------------------------
// Durable file-upload reply delivery (ccsc-o7x.5 — ADR-002 addendum)
// ---------------------------------------------------------------------------

/** Injected Slack + guard I/O for durable file uploads (ccsc-o7x.5). Kept as an
 *  interface so `slack-delivery.ts` imports no Slack SDK and the read/guard/upload
 *  wiring lives in `server.ts`. Consumed by BOTH the inline path and the poller,
 *  so a file's exfil guards re-run on every (re)upload.
 *
 *  **Read-once contract (closes a TOCTOU gap).** `readAndGuard` reads the file
 *  ONCE, runs the exfil guards on those exact bytes, and RETURNS them; `upload`
 *  sends that same buffer and never re-reads the path. So the bytes guarded are
 *  provably the bytes sent — a file that changes on disk a microsecond after the
 *  guard cannot slip past it for that delivery. (`ExfilBlockedError` lives in
 *  `lib.ts` so the poller can classify it too.) */
export interface FileUploadDeps {
  /** Read `upload.path` ONCE, run the outbound file exfil guards on those bytes —
   *  `assertSendable(path)` + secret-value scan of content + filename — and
   *  return the bytes. THROWS `ExfilBlockedError` on a block (the impl journals
   *  `exfil.block` first). The returned buffer is exactly what `upload` sends. */
  readAndGuard(upload: { path: string; filename: string }): Promise<Uint8Array>
  /** Dedup: the Slack file id if this upload already landed in the thread — a
   *  recorded `uploadedFileId` still shared there, or a `(filename, size)` scan
   *  match — else `null`. File shares carry no app metadata, so this is a thread
   *  scan, not a metadata key. */
  findUploaded(obligation: DeliveryObligation): Promise<string | null>
  /** Upload the ALREADY-READ, ALREADY-GUARDED `bytes` for `obligation.upload` via
   *  `filesUploadV2`; resolve the Slack file id. Never re-reads the path — the
   *  guarded bytes are sent verbatim. Throws on Slack failure (the caller
   *  classifies for retry / dead-letter). */
  upload(obligation: DeliveryObligation, bytes: Uint8Array): Promise<string>
}

/** Idempotent, guarded durable file upload (ccsc-o7x.5). Order is **dedup →
 *  read+guard → upload**: skip if already delivered, otherwise read the file once
 *  and re-validate those exact bytes, then upload the SAME bytes. Returns the
 *  Slack file id (existing on a dedup hit, fresh otherwise). The read+guard runs
 *  on every call that reaches the upload — inline AND poller — so a file whose
 *  content changed to a secret since record-time is blocked at redelivery, not
 *  merely at record-time, and the guarded bytes are provably the sent bytes (no
 *  second read). Throws `ExfilBlockedError` on a guard block and the Slack error
 *  on an upload failure; the caller marks the obligation accordingly. */
export async function sendFileObligation(
  deps: FileUploadDeps,
  obligation: DeliveryObligation,
): Promise<string> {
  if (obligation.upload === undefined) {
    throw new Error('sendFileObligation: obligation has no upload descriptor')
  }
  const existing = await deps.findUploaded(obligation)
  if (existing) return existing
  // Read once + re-validate the exact bytes that will be sent, then send THEM.
  const bytes = await deps.readAndGuard({
    path: obligation.upload.path,
    filename: obligation.upload.filename,
  })
  return deps.upload(obligation, bytes)
}

/** One logical reply with file attachments (ccsc-o7x.5). `chunks` is the
 *  pre-split text (may be empty — a files-only reply); `files` are the
 *  attachments. Each text chunk becomes obligation id `<id>:<i>` and each file
 *  `<id>:file:<j>`, recorded all-or-nothing before any send and delivered in
 *  order (text first so the message lands before its attachments). */
export interface DurableFileReply {
  id: string
  channel: string
  thread: string
  chunks: string[]
  files: { path: string; filename: string; comment?: string }[]
  /** Block Kit blocks, attached to the first text chunk's obligation. */
  blocks?: Array<Record<string, unknown>>
}

export type DurableFileDeliveryResult =
  | { status: 'delivered'; ts: string | undefined; messagesSent: number; filesSent: number }
  | { status: 'queued'; delivered: number; pending: number }

/** Durable delivery of a reply with file attachments (ccsc-o7x.5) — the
 *  files-bearing sibling of `deliverChunkedReplyDurably`. Records all text-chunk
 *  AND file obligations in ONE atomic write before any send, then delivers them
 *  in order: text chunks via `deps.post` (idempotency-keyed `chat.postMessage`),
 *  files via `sendFileObligation` (dedup → guard → upload). On a successful file
 *  upload the Slack file id is recorded (`uploadedFileId`) so a later redelivery
 *  dedups.
 *
 *    - every item posts/uploads → all `delivered`, return the first message ts;
 *    - a TRANSIENT error on item i → mark i `pending` and STOP (poller redelivers
 *      i…N in order) → `queued`;
 *    - a NON-RETRYABLE error or an `ExfilBlockedError` on item i → mark i `dead`
 *      and rethrow so the agent sees the failure (a blocked file is never
 *      uploaded; earlier items already landed).
 *
 *  Throws `DurableUnavailableError` BEFORE recording if the session can't be
 *  activated or holds no lease — the caller falls back to the best-effort direct
 *  path. */
export async function deliverFileReplyDurably(
  deps: { supervisor: SessionSupervisor; post: ReplyPoster; files: FileUploadDeps },
  reply: DurableFileReply,
): Promise<DurableFileDeliveryResult> {
  let handle: SessionHandle
  try {
    handle = await deps.supervisor.activate({ channel: reply.channel, thread: reply.thread })
  } catch (err) {
    throw new DurableUnavailableError(
      `cannot activate session: ${err instanceof Error ? err.message : String(err)}`,
    )
  }
  const lease = handle.lease
  if (lease === null) throw new DurableUnavailableError('session holds no lease')
  const token = lease.token

  // Text obligations first, then file obligations — recorded (and delivered) in
  // that order so the message lands before its attachments.
  const textRecords = reply.chunks.map((payload, i) => ({
    id: `${reply.id}:${i}`,
    channel: reply.channel,
    thread: reply.thread,
    payload,
    // Blocks ride on the FIRST text message only (a blocks reply is one
    // message; trailing chunks, if any, are plain-text continuation).
    ...(i === 0 && reply.blocks !== undefined ? { blocks: reply.blocks } : {}),
  }))
  const fileRecords = reply.files.map((upload, j) => ({
    id: `${reply.id}:file:${j}`,
    channel: reply.channel,
    thread: reply.thread,
    payload: '',
    upload,
  }))
  const records = [...textRecords, ...fileRecords]
  await handle.recordTerminalDeliveries(token, records)

  const total = records.length
  let firstTs: string | undefined
  let messagesSent = 0
  let filesSent = 0
  let delivered = 0
  for (const record of records) {
    const obligation: DeliveryObligation = {
      ...record,
      attempts: 0,
      state: 'pending',
      createdAt: 0,
    }
    try {
      if (obligation.upload !== undefined) {
        const fileId = await sendFileObligation(deps.files, obligation)
        await markObligation(handle, token, obligation.id, {
          state: 'delivered',
          attempts: 1,
          uploadedFileId: fileId,
        })
        filesSent++
      } else {
        const ts = await deps.post(obligation, deliveryIdempotencyKey(obligation))
        if (messagesSent === 0) firstTs = ts
        await markObligation(handle, token, obligation.id, { state: 'delivered', attempts: 1 })
        messagesSent++
      }
      delivered++
    } catch (err) {
      const code = extractSlackErrorCode(err)
      const lastError = code ?? (err instanceof Error ? err.message : String(err))
      const nonRetryable =
        err instanceof ExfilBlockedError || classifyDeliveryError(code) === 'non-retryable'
      if (nonRetryable) {
        await markObligation(handle, token, obligation.id, { state: 'dead', attempts: 1, lastError })
        throw err
      }
      // Transient: leave this item (and every later one) pending and STOP — the
      // poller redelivers the tail in order.
      await markObligation(handle, token, obligation.id, { state: 'pending', attempts: 1, lastError })
      return { status: 'queued', delivered, pending: total - delivered }
    }
  }
  return { status: 'delivered', ts: firstTs, messagesSent, filesSent }
}

/** Pull the uploaded Slack file id out of a `filesUploadV2` response, tolerant of
 *  the SDK's nested/loose shape. Returns `''` if none is extractable — callers
 *  treat that as "no recorded id" and fall back to the `(filename, size)` scan. */
function extractUploadedFileId(res: unknown): string {
  const r = res as { files?: Array<{ id?: string; files?: Array<{ id?: string }> }> }
  const first = r.files?.[0]
  return first?.id ?? first?.files?.[0]?.id ?? ''
}

/** Build the production `FileUploadDeps` (ccsc-o7x.5 part 2) bound to a Slack
 *  `WebClient` + the outbound exfil guards + injected fs reads. Kept here (not
 *  `server.ts`) so it is unit-testable against a fake client — fs is INJECTED
 *  (`readFile` / `fileSize`) so tests need no real files and this module stays
 *  fs-free.
 *
 *  - `readAndGuard` reads the file ONCE via `readFile`, runs `assertSendable`
 *    (path denylist) + `assertNoSecretValues` on the latin1 content AND the
 *    filename, and returns the bytes. A guard hit journals `exfil.block` then
 *    throws `ExfilBlockedError` (non-retryable everywhere). The returned buffer
 *    is exactly what `upload` sends — no second read (TOCTOU-safe).
 *  - `findUploaded` dedups: a recorded `uploadedFileId` still shared in the
 *    thread, else a `(filename, size)` scan of `conversations.replies`. Returns
 *    `null` (never `''`) on no match.
 *  - `upload` sends the already-guarded bytes via `filesUploadV2` and returns the
 *    new file id. */
export function createFileSendDeps(deps: {
  client: WebClient
  assertSendable: (path: string) => void
  assertNoSecretValues: (text: string) => void
  journalExfilBlock: (reason: string) => void
  readFile: (path: string) => Uint8Array
  fileSize: (path: string) => number
}): FileUploadDeps {
  const blocked = (err: unknown): never => {
    const reason = err instanceof Error ? err.message : String(err)
    deps.journalExfilBlock(reason)
    throw new ExfilBlockedError(reason)
  }
  return {
    async readAndGuard(upload): Promise<Uint8Array> {
      try {
        deps.assertSendable(upload.path)
      } catch (err) {
        blocked(err)
      }
      // One read — its bytes are guarded AND sent (no second read).
      const bytes = deps.readFile(upload.path)
      // latin1 maps every byte 1:1 to a char, so no decode can split/drop a token.
      try {
        deps.assertNoSecretValues(Buffer.from(bytes).toString('latin1'))
        deps.assertNoSecretValues(upload.filename)
      } catch (err) {
        blocked(err)
      }
      return bytes
    },
    async findUploaded(obligation): Promise<string | null> {
      if (obligation.upload === undefined || !obligation.thread) return null
      const { filename, path } = obligation.upload
      const recordedId = obligation.uploadedFileId
      let size = -1
      try {
        size = deps.fileSize(path)
      } catch {
        size = -1
      }
      const res = await deps.client.conversations.replies({
        channel: obligation.channel,
        ts: obligation.thread,
        limit: 200,
      })
      const messages = (res.messages ?? []) as Array<{
        ts?: string
        files?: Array<{ id?: string; name?: string; size?: number }>
      }>
      for (const m of messages) {
        // Only a file shared as part of THIS obligation's delivery window counts
        // for the (filename, size) scan: a multi-turn thread can hold an OLDER
        // file with the same name + size, and matching it would falsely dedup and
        // DROP this upload (a loss, not a dup). Slack `ts` is epoch seconds; the
        // obligation's `createdAt` is epoch ms. The recorded-id match is exact, so
        // it is NOT time-scoped.
        const msgMs = m.ts ? Math.round(Number.parseFloat(m.ts) * 1000) : 0
        const fromThisDelivery = msgMs >= obligation.createdAt
        for (const f of m.files ?? []) {
          if (recordedId && f.id === recordedId) return f.id ?? 'delivered'
          if (fromThisDelivery && size >= 0 && f.name === filename && f.size === size) {
            return f.id ?? 'delivered'
          }
        }
      }
      return null
    },
    async upload(obligation, bytes): Promise<string> {
      if (obligation.upload === undefined) {
        throw new Error('createFileSendDeps.upload: obligation has no upload descriptor')
      }
      const res = await deps.client.filesUploadV2({
        channel_id: obligation.channel,
        file: Buffer.from(bytes),
        filename: obligation.upload.filename,
        ...(obligation.thread ? { thread_ts: obligation.thread } : {}),
        ...(obligation.upload.comment ? { initial_comment: obligation.upload.comment } : {}),
        // filesUploadV2's argument type is a strict union (channel-vs-thread
        // destination); the reply tool casts the same way (executeReplyFileUploads).
      } as Parameters<typeof deps.client.filesUploadV2>[0])
      return extractUploadedFileId(res)
    },
  }
}

/** Best-effort fenced patch of one obligation's state. Never throws: a fenced /
 *  save failure leaves the obligation as-is for the poller to reconcile (see
 *  `deliverReplyDurably`). */
async function markObligation(
  handle: SessionHandle,
  token: number,
  id: string,
  patch: {
    state: DeliveryObligation['state']
    attempts: number
    lastError?: string
    // ccsc-o7x.5 — recorded after a successful file upload, so a later redelivery
    // dedups by checking the file is still shared in the thread.
    uploadedFileId?: string
  },
): Promise<void> {
  try {
    await handle.update(
      (prev) => ({
        ...prev,
        outbox: (prev.outbox ?? []).map((o) =>
          o.id === id
            ? {
                ...o,
                state: patch.state,
                attempts: patch.attempts,
                ...(patch.lastError !== undefined ? { lastError: patch.lastError } : {}),
                ...(patch.uploadedFileId !== undefined
                  ? { uploadedFileId: patch.uploadedFileId }
                  : {}),
              }
            : o,
        ),
      }),
      token,
    )
  } catch {
    // Swallow — the poller reconciles obligation state from disk.
  }
}
