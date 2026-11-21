import { describe, expect, test } from 'bun:test'
import { AcpSessionCancelRequestSchema } from './acp-adapter.ts'
import { canonicalJson, JournalEvent } from './journal.ts'
import { SessionSchema } from './lib.ts'
import { ManifestV1 } from './manifest.ts'
import { parsePolicyRule } from './policy.ts'

// claude-4l09.11: exercise application contracts across the Zod major upgrade.
// These are synthetic inputs; no Slack credentials or provider calls are used.
describe('patched validation compatibility', () => {
  const session = {
    v: 1 as const,
    key: { channel: 'C_TEST', thread: '1700000000.000001' },
    createdAt: 1700000000000,
    lastActiveAt: 1700000001000,
    ownerId: 'U_TEST',
    data: { nested: { flags: [true, null, 4], text: 'Unicode: café' } },
  }

  test('retains nonempty arbitrary session data and additive outbox fields', () => {
    const input = {
      ...session,
      outbox: [
        {
          id: 'delivery-1',
          channel: 'C_TEST',
          thread: '1700000000.000001',
          payload: 'synthetic',
          attempts: 0,
          state: 'pending' as const,
          createdAt: 1700000000000,
          futureField: { retained: ['after', 'save'] },
        },
      ],
    }
    const parsed = SessionSchema.parse(input)
    expect(parsed).toEqual(input)
    expect(SessionSchema.parse(JSON.parse(JSON.stringify(parsed)))).toEqual(input)
  })

  test('keeps the session and nested identity strict', () => {
    expect(SessionSchema.safeParse({ ...session, unexpected: true }).success).toBe(false)
    expect(
      SessionSchema.safeParse({ ...session, key: { ...session.key, unexpected: true } }).success,
    ).toBe(false)
    expect(SessionSchema.safeParse({ ...session, ownerId: 42 }).success).toBe(false)
  })

  test('preserves policy defaults and refuses an unconstrained match', () => {
    expect(
      parsePolicyRule({ id: 'approval', effect: 'require_approval', match: { tool: 'reply' } }),
    ).toEqual({
      id: 'approval',
      effect: 'require_approval',
      match: { tool: 'reply' },
      priority: 100,
      ttlMs: 300000,
      approvers: 1,
    })
    expect(() => parsePolicyRule({ id: 'invalid', effect: 'auto_approve', match: {} })).toThrow()
  })

  test('preserves journal payload and canonical bytes, with strict fields', () => {
    const event = {
      v: 1 as const,
      ts: '2026-10-25T00:00:00.000Z',
      seq: 1,
      kind: 'policy.allow' as const,
      input: { nested: ['synthetic', 2, false, null] },
      prevHash: '0'.repeat(64),
      hash: '1'.repeat(64),
    }
    const parsed = JournalEvent.parse(event)
    expect(parsed).toEqual(event)
    expect(canonicalJson(parsed)).toBe(canonicalJson(event))
    expect(JournalEvent.safeParse({ ...event, unexpected: true }).success).toBe(false)
  })

  test('preserves the ACP envelope and rejects an empty session identity', () => {
    const input = {
      jsonrpc: '2.0' as const,
      id: 1,
      method: 'session/cancel' as const,
      params: { sessionId: 'C:T' },
    }
    expect(AcpSessionCancelRequestSchema.parse(input)).toEqual(input)
    expect(
      AcpSessionCancelRequestSchema.safeParse({ ...input, params: { sessionId: '' } }).success,
    ).toBe(false)
  })

  test('keeps legacy integer acceptance without adding a safe-integer ceiling', () => {
    const priority = 2 ** 53
    expect(
      parsePolicyRule({ id: 'legacy', effect: 'auto_approve', priority, match: { tool: 'reply' } })
        .priority,
    ).toBe(priority)
    expect(() =>
      parsePolicyRule({
        id: 'fraction',
        effect: 'auto_approve',
        priority: 1.5,
        match: { tool: 'reply' },
      }),
    ).toThrow()
    const event = {
      v: 1,
      ts: '2026-10-25T00:00:00.000Z',
      seq: priority,
      kind: 'policy.allow',
      prevHash: '0'.repeat(64),
      hash: '1'.repeat(64),
    }
    expect(JournalEvent.parse(event).seq).toBe(priority)
    expect(JournalEvent.safeParse({ ...event, seq: -1 }).success).toBe(false)
    expect(JournalEvent.safeParse({ ...event, seq: 1.5 }).success).toBe(false)
  })

  test('rejects an oversized manifest tool collection before per-item issue accumulation', () => {
    // Bounded 64-element control: no memory-exhaustion payload is constructed.
    // The old validator accumulated per-element errors despite the max(50).
    const result = ManifestV1.safeParse({
      __claude_bot_manifest_v1__: true,
      name: 'synthetic',
      vendor: 'test',
      version: '1.0.0',
      description: '',
      publishedAt: '2026-10-25T00:00:00.000Z',
      tools: Array.from({ length: 64 }, () => ({ name: 7, description: 7 })),
    })
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.error.issues).toHaveLength(1)
      expect(result.error.issues[0].path).toEqual(['tools'])
      expect(result.error.issues[0].code).toBe('too_big')
    }
  })
})
