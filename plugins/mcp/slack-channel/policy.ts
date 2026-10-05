/**
 * policy.ts — Declarative policy engine for claude-code-slack-channel.
 *
 * This module provides the Zod schema for PolicyRule. The evaluate()
 * function, shadow-detection linter, monotonicity check, and path
 * canonicalization land in sibling beads (29-A.3 – 29-A.7). See
 * 000-docs/policy-evaluation-flow.md for the full design contract.
 *
 * Scope of this file for 29-A.1:
 *   - PolicyRule discriminated union (auto_approve | deny | require_approval)
 *   - MatchSpec with at-least-one-field refinement
 *   - Inferred TypeScript types
 *
 * Deliberately narrow surface: no compound combinators, no expression DSL.
 * Three effects only; more is a footgun for shadows.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

import { createHash } from 'node:crypto'
import { realpathSync } from 'node:fs'
import { resolve, sep } from 'node:path'
import { z } from 'zod'
import { canonicalJson } from './journal.ts'

// ---------------------------------------------------------------------------
// MatchSpec — which tool calls a rule applies to.
// ---------------------------------------------------------------------------

/** Fields a rule's `match` can constrain. Each field is optional; the
 *  refinement below rejects match specs that constrain zero fields (a
 *  rule that matches everything is almost always a bug).
 *
 *  - `tool`       — exact MCP tool name, e.g. "upload_file".
 *  - `pathPrefix` — canonicalized via realpath by evaluate() (29-A.4);
 *                   the value stored here is the pre-resolve literal.
 *  - `channel`    — Slack channel ID, e.g. "C0123456789".
 *  - `thread_ts`  — Slack thread timestamp, e.g. "1712345678.001100".
 *                   Scopes a rule to a single thread within a channel.
 *                   Enforced by evaluate() via matchApplies(): compared
 *                   against `call.sessionKey.thread`. (Previously schema-
 *                   only; wiring landed in Epic 29-B — before that a
 *                   thread_ts-only rule silently matched every thread.)
 *  - `actor`      — who is calling the tool. Approvers arrive on a
 *                   later turn so they are not a valid `actor` here.
 *  - `argEquals`  — subset equality on validated MCP input args. Keys
 *                   are compared against the top-level input object;
 *                   every listed key must equal the listed value.
 *  - `tier`       — provenance of the rule. Schema-only in this PR
 *                   (ccsc-4g8): the field is parsed and stored, and
 *                   `detectShadowing()` uses it for cross-tier
 *                   intersection lint. `evaluate()` does NOT yet act
 *                   on tier — that arrives in `ccsc-8pw` (combining
 *                   algorithm: strictest-tier-wins, then first-
 *                   applicable within tier). Default `'default'` keeps
 *                   existing access.json files loading unchanged.
 */
export const PolicyTier = z.enum(['default', 'workspace', 'user', 'admin'])
export type PolicyTier = z.infer<typeof PolicyTier>

export const MatchSpec = z
  .object({
    tool: z.string().min(1).optional(),
    pathPrefix: z.string().min(1).optional(),
    channel: z
      .string()
      .regex(/^[CD][A-Z0-9]+$/)
      .optional(),
    thread_ts: z
      .string()
      .regex(/^\d+\.\d+$/)
      .optional(),
    actor: z.enum(['session_owner', 'claude_process']).optional(),
    argEquals: z.record(z.string(), z.unknown()).optional(),
    tier: PolicyTier.optional(),
  })
  .refine(
    (m) =>
      m.tool !== undefined ||
      m.pathPrefix !== undefined ||
      m.channel !== undefined ||
      m.thread_ts !== undefined ||
      m.actor !== undefined ||
      (m.argEquals !== undefined && Object.keys(m.argEquals).length > 0),
    { message: 'match must constrain at least one field' },
  )

export type MatchSpec = z.infer<typeof MatchSpec>

/** Read the effective tier of a rule, defaulting to `'default'` when
 *  unset. Wrapped so callers don't repeat the fallback. */
export function effectiveTier(rule: PolicyRule): PolicyTier {
  return rule.match.tier ?? 'default'
}

// ---------------------------------------------------------------------------
// PolicyRule — discriminated union over the three effects.
// ---------------------------------------------------------------------------

/** Common fields on every rule — identity and position in the policy set. */
const RuleBase = {
  /** Stable, human-readable identifier. Shows up in audit log + error
   *  messages. Two rules with the same id is a load-time error. */
  id: z.string().min(1).max(120),

  /** Tie-breaker within effect when two rules would otherwise be
   *  equivalent. Primary ordering is authored array position (first-
   *  applicable, see 000-docs/policy-evaluation-flow.md §Combining).
   *  Lower `priority` wins the tie. */
  priority: z.number().int().default(100),

  match: MatchSpec,
} as const

/** `auto_approve`: allow the call without operator intervention. */
export const AutoApproveRule = z.object({
  ...RuleBase,
  effect: z.literal('auto_approve'),
})

/** `deny`: refuse the call. `reason` is surfaced to Claude so the model
 *  knows why the tool call was rejected — short, non-sensitive prose. */
export const DenyRule = z.object({
  ...RuleBase,
  effect: z.literal('deny'),
  reason: z.string().min(1).max(200),
})

/** `require_approval`: hold the call until human approver(s) respond on
 *  Slack. `ttlMs` is how long an approval remains valid after it
 *  arrives; future calls that match the same rule + session within the
 *  window are auto-approved. Default = 5 minutes.
 *
 *  `approvers` is the quorum threshold (NIST two-person integrity when
 *  ≥2). Same Slack `user_id` cannot double-satisfy — the server tracks
 *  approvedBy as a Set<user_id> and dedups on that. Display name is
 *  never used (spoofable). Hard ceiling of 10 is anti-footgun: no real
 *  workflow needs more than that, and an operator typo like `100`
 *  should be loud, not a deadlock. */
export const RequireApprovalRule = z.object({
  ...RuleBase,
  effect: z.literal('require_approval'),
  ttlMs: z
    .number()
    .int()
    .positive()
    .max(24 * 60 * 60 * 1000) // 24h hard ceiling
    .default(5 * 60 * 1000),
  approvers: z.number().int().min(1).max(10).default(1),
})

/** Discriminated union over the three effects. evaluate() (29-A.3)
 *  walks a list of these in authored order and returns on the first
 *  rule whose `match` applies. */
export const PolicyRule = z.discriminatedUnion('effect', [
  AutoApproveRule,
  DenyRule,
  RequireApprovalRule,
])

export type PolicyRule = z.infer<typeof PolicyRule>
export type AutoApproveRule = z.infer<typeof AutoApproveRule>
export type DenyRule = z.infer<typeof DenyRule>
export type RequireApprovalRule = z.infer<typeof RequireApprovalRule>

/** Parse an unknown value as a PolicyRule. Throws on invalid input with
 *  Zod's standard error shape. The loader (29-A.5) wraps this with the
 *  shadow-detection linter; direct callers usually want that instead. */
export function parsePolicyRule(raw: unknown): PolicyRule {
  return PolicyRule.parse(raw)
}

/** Parse an unknown value as an array of PolicyRule. Zod-validates the
 *  array shape and each rule. Does NOT enforce uniqueness of `id` —
 *  call `assertUniqueRuleIds()` for that (kept separate so the loader
 *  can report parse + uniqueness errors independently and so pure
 *  parse callers aren't forced to accept the throw contract of the
 *  uniqueness check). */
export function parsePolicyRules(raw: unknown): PolicyRule[] {
  return z.array(PolicyRule).parse(raw)
}

// ---------------------------------------------------------------------------
// PolicyDecision — output of evaluate(). See 000-docs/policy-evaluation-flow.md §27-30.
// ---------------------------------------------------------------------------

/** The decision returned by `evaluate()`. Three kinds — a deliberately
 *  narrow surface. `allow` is the happy path; `deny` refuses with a
 *  reason surfaced to Claude; `require` pauses until a human approver
 *  responds on Slack within `ttlMs`.
 *
 *  Not confused with `PolicyRule.effect` (the *input* shape): rule
 *  effects are `auto_approve | deny | require_approval`; decisions are
 *  `allow | deny | require`. An `auto_approve` rule produces an `allow`
 *  decision; a `require_approval` rule produces a `require` decision
 *  unless a fresh approval is already in flight (which turns it into
 *  `allow`). See the flowchart in policy-evaluation-flow.md.
 *
 *  **No runtime validation.** Decisions are produced by `evaluate()`
 *  from validated inputs, never parsed from untrusted data, so a Zod
 *  schema here would be dead weight. The type alone is the contract.
 */
export type PolicyDecision =
  | {
      kind: 'allow'
      /** ID of the matching rule. Absent when the default branch fires
       *  (no rule matched + tool not in `requireAuthoredPolicy`). */
      rule?: string
    }
  | {
      kind: 'deny'
      rule: string
      /** Short, non-sensitive prose surfaced to Claude so the model
       *  knows why the tool call was rejected. */
      reason: string
    }
  | {
      kind: 'require'
      rule: string
      /** For now always the human approver; named so future expansion
       *  (peer-agent approvals, escalation paths) can extend the union. */
      approver: 'human_approver'
      /** How long an approval, once granted, is fresh for. Propagated
       *  from the matching `RequireApprovalRule.ttlMs`. */
      ttlMs: number
      /** Quorum threshold — how many distinct Slack `user_id`s must
       *  approve before the decision flips to allow. Propagated from
       *  `RequireApprovalRule.approvers` (default 1). */
      approvers: number
      /** Set ONLY on the input-unavailable fail-safe path (ccsc-x0t.5):
       *  a `deny`/`require_approval` rule matched every enforceable field
       *  but its `pathPrefix`/`argEquals` predicate could not be evaluated
       *  at the gate, so the call is routed to a human. Honest-journaling
       *  signal — the server writes it into the `policy.require` event so
       *  the audit chain records WHY the human was asked, never claiming
       *  the predicate was evaluated. Undefined on a genuine
       *  `require_approval` match. */
      reason?: string
    }

// Compile-time shape-drift guard. `lib.ts` deliberately duplicates the
// shape of `PolicyDecision` as `PolicyDecisionShape` (type-only, no
// runtime import) to stay decoupled from policy.ts. These bidirectional
// `satisfies` casts break the build the moment either side drifts —
// without forcing a runtime import or a third shared module.
import type { PolicyDecisionShape } from './lib.ts'

type _PolicyDecisionForward = PolicyDecision extends PolicyDecisionShape ? true : never
type _PolicyDecisionBackward = PolicyDecisionShape extends PolicyDecision ? true : never
const _decisionShapeForward: _PolicyDecisionForward = true
const _decisionShapeBackward: _PolicyDecisionBackward = true
void _decisionShapeForward
void _decisionShapeBackward

// ---------------------------------------------------------------------------
// Path canonicalization (CWE-22) — see policy-evaluation-flow.md §174-196.
// ---------------------------------------------------------------------------

/** Canonicalize a `match.pathPrefix` at load time.
 *
 *  The policy loader calls this once per rule and caches the result.
 *  `realpathSync.native` resolves every symlink in the configured
 *  prefix, so the comparison at evaluate time is a prefix-check on
 *  two canonical paths — no TOCTOU, no smuggling.
 *
 *  Throws if the prefix does not exist on disk. That's intentional:
 *  a rule pointing at a nonexistent path can never match anything, so
 *  it's almost certainly a typo that the operator should fix at load
 *  time, not a mystery-miss at evaluation time. Fail loud.
 *
 *  See policy-evaluation-flow.md §174-196 for the full design rationale
 *  and CWE-22 mitigation story.
 */
export function canonicalizeRulePathPrefix(raw: string): string {
  return realpathSync.native(resolve(raw))
}

/** Canonicalize a per-call request path.
 *
 *  Unlike the prefix (canonicalized once at load), the input path is
 *  canonicalized on every tool call — fresh `realpath` each time so a
 *  newly-created symlink between calls is caught on the next match.
 *
 *  Throws if the path does not exist. That's the desired fail-closed
 *  posture: a tool call referencing a nonexistent path gets a policy
 *  error (loud) rather than matching a rule against an unresolvable
 *  lexical string (quiet).
 */
export function canonicalizeRequestPath(raw: string, cwd: string = process.cwd()): string {
  return realpathSync.native(resolve(cwd, raw))
}

/** Prefix-matches a canonicalized request path against a canonicalized
 *  rule prefix. Both args MUST already be realpath-resolved via the
 *  helpers above — this function does no I/O, just a string compare.
 *
 *  The `+ sep` guard prevents `/etc/passwd` from matching prefix
 *  `/etc/pass` while still allowing an exact-equality match (the common
 *  case of a rule targeting a file, not a directory).
 */
export function pathMatchesPrefix(resolvedPath: string, resolvedPrefix: string): boolean {
  return resolvedPath === resolvedPrefix || resolvedPath.startsWith(resolvedPrefix + sep)
}

// ---------------------------------------------------------------------------
// 31-A.4 Invariant — manifest data NEVER passed to evaluate()
//
// Design: 000-docs/bot-manifest-protocol.md §91-109 ("The binding invariant").
//
// Peer-bot manifests are advertisements, not grants (Miller 2006). Policy
// decisions MUST use only verified signals carried on ToolCall (tool,
// sessionKey.channel, actor) — never content a peer advertised about itself.
// A peer claiming "I am an approver" in its manifest does not make it one;
// allowBotIds and access.json are the only sources of role truth.
//
// Enforcement here is structural + contractual:
//
//   1. policy.ts imports NO manifest-module path, direct or re-exported.
//      Enforced by the "31-A.4 invariant" test in server.test.ts, which
//      parses this file's import specifiers on every CI run. A violation
//      is a merge block, not a warning.
//
//   2. When the (future, conditionally-shipped) manifest consumer lands in
//      Epic 31-A, its output flows to Claude only as MCP tool-call text —
//      the same trust surface as a chat message. It does NOT flow into
//      ToolCall.input, PolicyRule[], or EvaluateOptions. Reviewers of any
//      31-A PR must confirm this before merge.
//
//   3. access.json mutation from manifest reads is forbidden (see the
//      manifest protocol doc §190-203). That rule is enforced in the
//      manifest-consumer module itself, not here — policy.ts's job is
//      to stay unreachable from manifest content, full stop.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// evaluate() — first-applicable combining (XACML) per policy-evaluation-flow.md
// ---------------------------------------------------------------------------

/** Surface of a tool call as the evaluator sees it.
 *
 *  Path-bearing tools put the caller-supplied path in `input.path`;
 *  evaluate() canonicalizes it when a rule constrains `pathPrefix`.
 *  `actor` is the direct caller — human approvers arrive as later turns,
 *  never as the `actor` on the original call. */
export interface ToolCall {
  tool: string
  input: Record<string, unknown>
  sessionKey: { channel: string; thread: string }
  actor: 'session_owner' | 'claude_process'
  /** Whether `input` carries the structured tool args. Defaults to `true`.
   *
   *  The sole production caller — the MCP `permission_request` notification
   *  handler — sets this `false`: that notification carries only an
   *  `input_preview` string, never the structured args, so it builds the
   *  call with `input: {}`. When `false`, `matchApplies` cannot evaluate the
   *  `pathPrefix`/`argEquals` predicates and returns `'indeterminate'`
   *  instead of the old fail-open `false`; `evaluate()` then fails a
   *  `deny`/`require_approval` rule SAFE to `require` (routes to a human)
   *  rather than letting a later broad `auto_approve` swallow the call.
   *  See 000-docs/policy-evaluation-flow.md § Input-unavailable fail-safe
   *  (ccsc-x0t.5). Defaulting to `true` keeps every existing call site and
   *  test byte-for-byte unchanged. */
  inputAvailable?: boolean
}

/** Key into the approvals map: `${ruleId}:${channel}:${thread}`. Scoped
 *  to (rule, session) per policy-evaluation-flow.md §285-287 so a
 *  different session in the same channel never inherits the approval. */
export type ApprovalKey = string

/** Build the approval-map key for a (rule, sessionKey) pair. */
export function approvalKey(
  ruleId: string,
  sessionKey: { channel: string; thread: string },
): ApprovalKey {
  return `${ruleId}:${sessionKey.channel}:${sessionKey.thread}`
}

/** Set of tools for which an unmatched call defaults to deny-by-omission
 *  (rather than the blanket allow for everything else). Mutation of
 *  external state goes here; read-only tools do not — see
 *  policy-evaluation-flow.md §107-117. */
export const DEFAULT_REQUIRE_AUTHORED_POLICY: ReadonlySet<string> = new Set(['upload_file'])

export interface EvaluateOptions {
  /** (rule, session) → approval window. An entry with `ttlExpires > now`
   *  flips a `require_approval` rule into an `allow` decision. Written
   *  by the permission-reply handler, not by `evaluate()`. */
  approvals?: ReadonlyMap<ApprovalKey, { ttlExpires: number }>
  /** Tools that require an authored rule; unmatched calls return deny. */
  requireAuthoredPolicy?: ReadonlySet<string>
}

/** Pure evaluator. Walks `rules` in authored order and returns on the
 *  first match (XACML first-applicable, see policy-evaluation-flow.md
 *  §89-93). Side-effect-free: journal emission, approval recording,
 *  and Slack posts happen outside, after evaluate() returns.
 *
 *  Path matching canonicalizes both sides via `realpath` on every call
 *  (see canonicalizeRequestPath + canonicalizeRulePathPrefix). If
 *  either path does not exist, the `pathPrefix` constraint is treated
 *  as "not matching" — fail-closed: a rule can't match a path that
 *  doesn't resolve.
 *
 *  Returns the default decision when no rule matches:
 *    - `deny` (rule = 'default') if `call.tool` is in requireAuthoredPolicy
 *    - `allow` (rule undefined) otherwise
 */
/** Tier evaluation order, strictest first (ccsc-8pw). Admin wins over
 *  User wins over Workspace wins over Default. When at least one rule
 *  in a higher tier matches, that tier's decision is the result; lower
 *  tiers are not consulted. */
const TIER_PRIORITY: readonly PolicyTier[] = ['admin', 'user', 'workspace', 'default']

// ---------------------------------------------------------------------------
// Input-unavailable fail-safe constants (ccsc-x0t.5)
// ---------------------------------------------------------------------------

/** Reason stamped on a `require` decision produced by the input-unavailable
 *  fail-safe. Exported so tests and the server assert against one string,
 *  not a copy. The server writes this into the `policy.require` journal
 *  event so the audit chain records WHY the human was asked. */
export const INDETERMINATE_PREDICATE_REASON = 'predicate unevaluable at gate → routed to human'

/** Approval-window TTL applied when a `deny` rule is fail-safed to `require`
 *  (a `deny` has no `ttlMs` of its own). Mirrors the `require_approval`
 *  schema default (5 min) so the hold clears promptly and doesn't linger. */
export const FAILSAFE_APPROVAL_TTL_MS = 5 * 60 * 1000

/** Quorum applied when a `deny` rule is fail-safed to `require` (a `deny`
 *  has no `approvers` of its own). One operator can clear the hold —
 *  matches the `require_approval` schema default and avoids a surprise
 *  deadlock when no second approver is configured. */
export const FAILSAFE_APPROVAL_QUORUM = 1

export function evaluate(
  call: ToolCall,
  rules: readonly PolicyRule[],
  now: number,
  opts: EvaluateOptions = {},
): PolicyDecision {
  const approvals = opts.approvals ?? new Map<ApprovalKey, { ttlExpires: number }>()
  const requireAuthored = opts.requireAuthoredPolicy ?? DEFAULT_REQUIRE_AUTHORED_POLICY

  // Tier-aware combining algorithm (ccsc-8pw): strictest-tier-wins,
  // then first-applicable within tier.
  //
  // Backward compatibility: when no rule declares a tier, every rule
  // lives in the 'default' tier. The for-loop below walks admin → user
  // → workspace → default; with no rules in admin/user/workspace, only
  // default runs, and `default` walks every rule in the order the
  // operator authored them — exactly the v0.5.x behavior. Existing
  // tests and existing access.json files continue to behave identically.
  //
  // When tiers ARE used, every rule in a higher tier is considered before
  // any rule in a lower tier. A `deny` in Admin always beats an
  // `auto_approve` in Workspace AND an `auto_approve` in Admin always
  // beats a `deny` in Workspace (the intentional "Admin overrides" path).
  for (const tier of TIER_PRIORITY) {
    for (const rule of rules) {
      if (effectiveTier(rule) !== tier) continue

      const outcome = matchApplies(rule.match, call)
      if (outcome === 'no_match') continue

      if (outcome === 'indeterminate') {
        // Input-unavailable fail-safe (ccsc-x0t.5). Every enforceable field
        // (tool/channel/thread_ts/actor) matched, but an input-dependent
        // predicate (pathPrefix/argEquals) could not be evaluated because the
        // call carries no structured input (inputAvailable === false). NEVER
        // fail-open here:
        //   - auto_approve → skip (never auto-approve on an unconfirmable
        //     predicate); fall through to later rules / the default branch,
        //     exactly the pre-x0t.5 no-match net effect, now made explicit.
        //   - deny / require_approval → route to a human (require), which
        //     PREEMPTS any later broad auto_approve that would otherwise
        //     swallow the call. This is the whole fix: an operator's
        //     `{deny, pathPrefix:/etc}` no longer silently loses to a later
        //     `{auto_approve, tool:Bash}`.
        // See 000-docs/policy-evaluation-flow.md § Input-unavailable fail-safe.
        if (rule.effect === 'auto_approve') continue
        // Honor a fresh (rule, session) approval — an indeterminate
        // require_approval then behaves identically to a matched one, and a
        // human who already cleared an indeterminate deny isn't re-prompted.
        const approval = approvals.get(approvalKey(rule.id, call.sessionKey))
        if (approval && approval.ttlExpires > now) {
          return { kind: 'allow', rule: rule.id }
        }
        return {
          kind: 'require',
          rule: rule.id,
          approver: 'human_approver',
          // require_approval carries its own window; a deny has none, so
          // fall back to the conservative fail-safe defaults.
          ttlMs: rule.effect === 'require_approval' ? rule.ttlMs : FAILSAFE_APPROVAL_TTL_MS,
          approvers: rule.effect === 'require_approval' ? rule.approvers : FAILSAFE_APPROVAL_QUORUM,
          reason: INDETERMINATE_PREDICATE_REASON,
        }
      }

      // outcome === 'match' — every field evaluated; original semantics.
      switch (rule.effect) {
        case 'auto_approve':
          return { kind: 'allow', rule: rule.id }
        case 'deny':
          return { kind: 'deny', rule: rule.id, reason: rule.reason }
        case 'require_approval': {
          const approval = approvals.get(approvalKey(rule.id, call.sessionKey))
          if (approval && approval.ttlExpires > now) {
            return { kind: 'allow', rule: rule.id }
          }
          return {
            kind: 'require',
            rule: rule.id,
            approver: 'human_approver',
            ttlMs: rule.ttlMs,
            approvers: rule.approvers,
          }
        }
      }
    }
  }

  // No rule in any tier matched — default branch.
  if (requireAuthored.has(call.tool)) {
    return {
      kind: 'deny',
      rule: 'default',
      reason: `no policy authored for tool '${call.tool}'`,
    }
  }
  return { kind: 'allow' }
}

/** Tri-state result of `matchApplies` (ccsc-x0t.5).
 *
 *  - `'match'`         — the rule applies to the call.
 *  - `'no_match'`      — the rule genuinely does not apply.
 *  - `'indeterminate'` — every ENFORCEABLE field matched, but an
 *    input-dependent predicate (`pathPrefix`/`argEquals`) could not be
 *    evaluated because the call carries no structured input
 *    (`inputAvailable === false`). `evaluate()` fails a
 *    `deny`/`require_approval` rule SAFE to `require` on this signal, and
 *    skips an `auto_approve`. */
type MatchOutcome = 'match' | 'no_match' | 'indeterminate'

/** Does `match` apply to `call`? Every undefined field is a wildcard.
 *
 *  Enforceable fields (`tool`/`channel`/`thread_ts`/`actor`) are evaluable
 *  regardless of input availability, so they are checked FIRST and any
 *  mismatch short-circuits to `'no_match'` — a rule that mismatches one of
 *  them genuinely does not apply and never reaches the fail-safe path. Only
 *  when every enforceable field matches do the input-dependent predicates
 *  run; under `inputAvailable === false` an unevaluable `pathPrefix`/
 *  `argEquals` yields `'indeterminate'` instead of the pre-x0t.5 fail-open
 *  `false`. When input IS available (the default), the tri-state collapses
 *  to the original boolean and behavior is byte-for-byte unchanged. */
function matchApplies(match: MatchSpec, call: ToolCall): MatchOutcome {
  if (match.tool !== undefined && match.tool !== call.tool) return 'no_match'
  if (match.channel !== undefined && match.channel !== call.sessionKey.channel) return 'no_match'
  if (match.thread_ts !== undefined && match.thread_ts !== call.sessionKey.thread) return 'no_match'
  if (match.actor !== undefined && match.actor !== call.actor) return 'no_match'

  // Enforceable fields all matched. Input-dependent predicates come next;
  // they are unevaluable at a call site that carries no structured input.
  const inputAvailable = call.inputAvailable ?? true

  if (match.pathPrefix !== undefined) {
    if (!inputAvailable) return 'indeterminate'
    const raw = call.input.path
    if (typeof raw !== 'string') return 'no_match'
    try {
      const resolvedPrefix = canonicalizeRulePathPrefix(match.pathPrefix)
      const resolvedInput = canonicalizeRequestPath(raw)
      if (!pathMatchesPrefix(resolvedInput, resolvedPrefix)) return 'no_match'
    } catch {
      // Either side failed to resolve: treat as non-match. Fail-closed.
      return 'no_match'
    }
  }

  if (match.argEquals !== undefined) {
    if (!inputAvailable) return 'indeterminate'
    for (const [k, v] of Object.entries(match.argEquals)) {
      if (!jsonEqual(call.input[k], v)) return 'no_match'
    }
  }

  return 'match'
}

/** Structural equality via JSON round-trip. Good enough for validated
 *  MCP input (plain JSON, no functions/cycles/dates); if perf becomes
 *  an issue, swap in a real deep-eq. Returns false on non-serializable
 *  inputs rather than throwing. */
function jsonEqual(a: unknown, b: unknown): boolean {
  try {
    return JSON.stringify(a) === JSON.stringify(b)
  } catch {
    return false
  }
}

// ---------------------------------------------------------------------------
// assertUniqueRuleIds() — load-time hard invariant per ACCESS.md §"Safety
// checks the loader runs" and policy-evaluation-flow.md. Duplicate `id`s
// are fatal because the evaluator walks in authored order and returns on
// the first match, so a second rule with the same id is silently
// unreachable — a subtle footgun the operator should see at boot, not in
// a post-incident audit trail review.
// ---------------------------------------------------------------------------

/** Throws if two or more rules share an `id`. Error message enumerates
 *  every duplicated id so an operator fixing a large policy sees the
 *  full set at once. Called AFTER `parsePolicyRules()` because it
 *  assumes the input is already schema-valid (so `rule.id` is a
 *  non-empty string). Sibling to `detectShadowing()` and
 *  `detectBroadAutoApprove()` — but unlike those, throws rather than
 *  returning warnings, matching the documented "fatal at boot"
 *  contract in ACCESS.md.
 */
export function assertUniqueRuleIds(rules: readonly PolicyRule[]): void {
  const seen = new Set<string>()
  const dupes = new Set<string>()
  for (const rule of rules) {
    if (seen.has(rule.id)) dupes.add(rule.id)
    seen.add(rule.id)
  }
  if (dupes.size > 0) {
    const sorted = [...dupes].sort()
    throw new Error(
      `duplicate rule id(s): ${sorted.join(', ')}. Every rule must have a unique id — the evaluator uses first-applicable, so a second rule with the same id is unreachable.`,
    )
  }
}

// ---------------------------------------------------------------------------
// policyDigest() — SHA-256 attestation hash for journal v2 (ccsc-22l)
// ---------------------------------------------------------------------------

/** Compute a deterministic SHA-256 hash over the canonical JCS form
 *  of the active PolicyRule[]. Used by the journal writer to populate
 *  `policy_attestation.digest` on every v2 event.
 *
 *  Determinism contract: the same rule set (regardless of input array
 *  order) produces the same digest. We sort by `id` before
 *  canonicalizing so the digest depends on the rule SET, not the
 *  AUTHORING ORDER. This matters because `evaluate()` is order-
 *  sensitive (first-applicable) but the digest is a content fingerprint
 *  — two operators who arrive at the same set of rules via different
 *  edit paths should land on the same digest.
 *
 *  Why this lives in policy.ts rather than journal.ts: the digest is
 *  derived from PolicyRule shapes, which are policy's domain. journal.ts
 *  treats the digest as an opaque 64-char hex string — see the
 *  `no-journal-imports-policy` invariant. The digest crosses the
 *  module boundary as a primitive, not as a structured policy object. */
export function policyDigest(rules: readonly PolicyRule[]): string {
  const sorted = [...rules].sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0))
  return createHash('sha256').update(canonicalJson(sorted)).digest('hex')
}

// ---------------------------------------------------------------------------
// detectShadowing() — load-time linter per policy-evaluation-flow.md §199-230
// ---------------------------------------------------------------------------

export interface ShadowWarning {
  /** The rule that never gets reached. */
  later: string
  /** The earlier rule that swallows every call the later rule would match. */
  earlier: string
  message: string
  /** True when the two rules live in different tiers and their matches
   *  intersect (but neither is a strict subset of the other). False or
   *  absent for the classic within-tier subset shadow — the existing
   *  warning shape is preserved for backward compatibility. Added in
   *  ccsc-4g8 to surface the Workspace-`auto_approve`-overrides-Admin-
   *  `deny` silent-footgun class that pure subset detection misses. */
  crossTier?: boolean
}

/** Static check for two kinds of shadow:
 *
 *   1. **Within-tier subset shadow** (existing v0.5.x behavior): a
 *      later rule's match is fully covered by an earlier rule's match.
 *      The later rule is never reached.
 *
 *   2. **Cross-tier intersection shadow** (ccsc-4g8): a non-Admin
 *      `auto_approve` rule shares any concrete tool call with an
 *      Admin `deny` rule. Once `ccsc-8pw` lands and `evaluate()`
 *      acts on tier precedence, the Admin deny will win — but right
 *      now (and in any audit that compares the published policy
 *      surface against what users see), the cross-tier intersection
 *      is itself ambiguous: which way does the operator intend it to
 *      resolve? Surfacing as a warning forces the question.
 *
 *  Warn-not-block: the warnings go to stderr at load time so the
 *  operator can reorder or narrow. Never fail-closed — an operator
 *  who intentionally wrote an unreachable rule (e.g., as a placeholder
 *  during a refactor) shouldn't be forced to delete it just to boot.
 */
export function detectShadowing(rules: readonly PolicyRule[]): ShadowWarning[] {
  const warnings: ShadowWarning[] = []

  // Pass 1: within-tier subset shadowing (existing behavior, unchanged).
  // We compare against earlier rules in the same tier — different tiers
  // resolve via strictest-tier-wins (once ccsc-8pw lands) so they cannot
  // shadow each other in the classic first-applicable sense.
  for (let j = 1; j < rules.length; j++) {
    const later = rules[j]!
    const laterTier = effectiveTier(later)
    for (let i = 0; i < j; i++) {
      const earlier = rules[i]!
      if (effectiveTier(earlier) !== laterTier) continue
      if (matchSubsetOrEqual(earlier.match, later.match)) {
        warnings.push({
          later: later.id,
          earlier: earlier.id,
          message: `rule '${later.id}' is shadowed by earlier rule '${earlier.id}' — every call the later rule would match is already caught by the earlier one`,
          crossTier: false,
        })
        break // first shadow is sufficient; don't double-report
      }
    }
  }

  // Pass 2: cross-tier intersection — every non-Admin `auto_approve`
  // checked against every Admin `deny`. Direction matters: we only
  // surface the dangerous direction (auto_approve from a lower tier
  // touching the same call space as a higher-tier deny). The reverse
  // direction (an Admin auto_approve intersecting a User deny) is
  // intended — it's the Admin tier saying "I override this deny."
  for (const lowerRule of rules) {
    if (lowerRule.effect !== 'auto_approve') continue
    if (effectiveTier(lowerRule) === 'admin') continue
    for (const adminRule of rules) {
      if (adminRule.effect !== 'deny') continue
      if (effectiveTier(adminRule) !== 'admin') continue
      if (matchesIntersect(lowerRule.match, adminRule.match)) {
        warnings.push({
          later: lowerRule.id,
          earlier: adminRule.id,
          message: `cross-tier shadow: '${effectiveTier(lowerRule)}'-tier auto_approve rule '${lowerRule.id}' intersects 'admin'-tier deny rule '${adminRule.id}' — operator intent is ambiguous; resolve by narrowing match, retiering, or removing one rule`,
          crossTier: true,
        })
      }
    }
  }

  return warnings
}

/** Is `outer.match` less-specific-or-equal to `inner.match` on every
 *  field? Used by both shadow detection and monotonicity — if yes,
 *  `outer` matches a superset of what `inner` matches. */
function matchSubsetOrEqual(outer: MatchSpec, inner: MatchSpec): boolean {
  if (outer.tool !== undefined && outer.tool !== inner.tool) return false
  if (outer.channel !== undefined && outer.channel !== inner.channel) return false
  // thread_ts (ccsc-x0t.1): mirror matchesIntersect, which already honors it.
  // Without this, a thread-scoped `outer` was treated as covering EVERY thread,
  // so detectShadowing / checkMonotonicity false-flagged thread-disjoint rules
  // (e.g. warned that a rule scoped to thread B is shadowed by one scoped to
  // thread A, or refused a reload adding a thread-B auto_approve alongside a
  // thread-A deny). A thread-scoped outer only subsets an inner in the SAME
  // thread. Enforcement in evaluate() (matchApplies) already compared thread_ts;
  // this closes the same gap in the subset/monotonicity linters.
  if (outer.thread_ts !== undefined && outer.thread_ts !== inner.thread_ts) return false
  if (outer.actor !== undefined && outer.actor !== inner.actor) return false

  if (outer.pathPrefix !== undefined) {
    if (inner.pathPrefix === undefined) return false
    // Lexical prefix check (both would be canonicalized in practice).
    if (
      inner.pathPrefix !== outer.pathPrefix &&
      !inner.pathPrefix.startsWith(outer.pathPrefix + sep)
    ) {
      return false
    }
  }

  if (outer.argEquals !== undefined) {
    if (inner.argEquals === undefined) return false
    for (const [k, v] of Object.entries(outer.argEquals)) {
      if (!jsonEqual(inner.argEquals[k], v)) return false
    }
  }

  return true
}

/** Do `a` and `b` describe overlapping call spaces? Returns true iff
 *  there exists at least one concrete tool call that both matches
 *  accept. Used by `detectShadowing()` for the cross-tier intersection
 *  pass — a strict subset is one form of intersection, but two specs
 *  can intersect without either being a subset (e.g., one constrains
 *  tool+channel, the other constrains tool+actor).
 *
 *  Field-by-field logic:
 *    - Exact-match fields (`tool`, `channel`, `thread_ts`, `actor`):
 *      if both sides constrain the field, the values must be equal.
 *      Either side leaving the field unconstrained is compatible with
 *      anything the other side asks.
 *    - `pathPrefix`: both unconstrained → overlap. One side
 *      constrains, other doesn't → overlap. Both constrain → one must
 *      be a prefix of the other (or equal).
 *    - `argEquals`: the conjunction is the union of both keys with the
 *      union of the value constraints. They overlap unless they
 *      disagree on a shared key (same key, different required value).
 *    - `tier`: intentionally excluded from intersection (tier is
 *      provenance, not call-space identity — two rules in different
 *      tiers CAN match the same call, that's the whole point of the
 *      check).
 */
export function matchesIntersect(a: MatchSpec, b: MatchSpec): boolean {
  if (a.tool !== undefined && b.tool !== undefined && a.tool !== b.tool) return false
  if (a.channel !== undefined && b.channel !== undefined && a.channel !== b.channel) return false
  if (a.thread_ts !== undefined && b.thread_ts !== undefined && a.thread_ts !== b.thread_ts) {
    return false
  }
  if (a.actor !== undefined && b.actor !== undefined && a.actor !== b.actor) return false

  if (a.pathPrefix !== undefined && b.pathPrefix !== undefined) {
    if (
      a.pathPrefix !== b.pathPrefix &&
      !a.pathPrefix.startsWith(b.pathPrefix + sep) &&
      !b.pathPrefix.startsWith(a.pathPrefix + sep)
    ) {
      return false
    }
  }

  if (a.argEquals !== undefined && b.argEquals !== undefined) {
    for (const [k, v] of Object.entries(a.argEquals)) {
      if (k in b.argEquals && !jsonEqual(b.argEquals[k], v)) return false
    }
  }

  return true
}

// ---------------------------------------------------------------------------
// checkMonotonicity() — hot-reload invariant per policy-evaluation-flow.md §234-244
// ---------------------------------------------------------------------------

export interface MonotonicityViolation {
  /** The newly-added auto_approve rule that would weaken policy. */
  newRule: string
  /** The existing deny rule whose match the new rule supersets. */
  existingDeny: string
  message: string
}

/** Detects whether adopting `next` as the active policy set would
 *  weaken policy compared to `prev`. A violation is:
 *
 *    A newly-added rule R with effect 'auto_approve' whose `match` is
 *    a subset of an existing 'deny' rule's match — i.e., the deny
 *    would have covered R's calls, so adding R silently opens a hole.
 *
 *  Caller's responsibility: if this returns a non-empty array, refuse
 *  to adopt `next` and keep `prev` active. The server logs the
 *  violation, surfaces a beads issue, and requires operator action
 *  (doc §237-249). Removed rules don't trigger — removing a deny
 *  obviously weakens policy, and the operator signed off by removing.
 */
export function checkMonotonicity(
  prev: readonly PolicyRule[],
  next: readonly PolicyRule[],
): MonotonicityViolation[] {
  const violations: MonotonicityViolation[] = []
  const prevIds = new Set(prev.map((r) => r.id))
  const prevDenies = prev.filter(
    (r): r is Extract<PolicyRule, { effect: 'deny' }> => r.effect === 'deny',
  )

  for (const newRule of next) {
    if (prevIds.has(newRule.id)) continue // unchanged or modified, not added
    if (newRule.effect !== 'auto_approve') continue

    for (const existingDeny of prevDenies) {
      if (matchSubsetOrEqual(existingDeny.match, newRule.match)) {
        violations.push({
          newRule: newRule.id,
          existingDeny: existingDeny.id,
          message: `new auto_approve rule '${newRule.id}' weakens existing deny '${existingDeny.id}' — reload refused`,
        })
      }
    }
  }

  return violations
}

// ---------------------------------------------------------------------------
// detectBroadAutoApprove() — boot-time footgun warning for auto_approve
// rules with overly broad match (no `tool` and no `pathPrefix`).
// ---------------------------------------------------------------------------

export interface BroadMatchWarning {
  ruleId: string
  message: string
}

/** Flag `auto_approve` rules whose `match` is too broad to be intentional.
 *  The heuristic: a narrow auto_approve must scope itself with at least
 *  one of `tool` or `pathPrefix`. Without either, the rule auto-approves
 *  based on `channel` / `actor` / `thread_ts` / `argEquals` alone — which
 *  means any tool, on any path, in that scope gets a green light.
 *
 *  That's almost always a misconfiguration: the operator meant to bound
 *  the rule to a specific safe operation and forgot. Warn loud at boot
 *  so the operator catches it before a silent over-grant lands in prod.
 *  Warn-not-block (same posture as `detectShadowing`) — an operator who
 *  intentionally wants "trust claude_process fully in this channel" can
 *  still boot; they just see the warning in logs.
 *
 *  Not shadow-detection (which flags unreachable rules) and not
 *  monotonicity (which flags weakening reloads). This is a separate
 *  axis: "this rule IS reachable and would be monotone, but its shape
 *  means it probably matches far more than you think."
 */
export function detectBroadAutoApprove(rules: readonly PolicyRule[]): BroadMatchWarning[] {
  const warnings: BroadMatchWarning[] = []
  for (const rule of rules) {
    if (rule.effect !== 'auto_approve') continue
    const hasNarrow = rule.match.tool !== undefined || rule.match.pathPrefix !== undefined
    if (!hasNarrow) {
      warnings.push({
        ruleId: rule.id,
        message:
          `auto_approve rule '${rule.id}' has no 'tool' or 'pathPrefix' in its match — ` +
          `this rule auto-approves ANY tool call within its scope, which is almost always ` +
          `a misconfiguration. Narrow the rule or convert to require_approval.`,
      })
    }
  }
  return warnings
}

// ---------------------------------------------------------------------------
// detectUnenforceablePredicates() — boot-time honesty warning for rules whose
// pathPrefix/argEquals predicate the production MCP permission gate cannot
// evaluate (ccsc-x0t.5). Sibling of detectShadowing / detectBroadAutoApprove.
// ---------------------------------------------------------------------------

export interface UnenforceablePredicateWarning {
  ruleId: string
  /** Which input-dependent predicate(s) the gate cannot evaluate. */
  predicates: ('pathPrefix' | 'argEquals')[]
  message: string
}

/** Flag every rule whose `match` constrains `pathPrefix` or `argEquals`.
 *
 *  The sole production caller of `evaluate()` is the MCP `permission_request`
 *  handler, whose notification carries only an `input_preview` string — no
 *  structured args. So at that gate these predicates are unevaluable and the
 *  input-unavailable fail-safe kicks in: a `deny`/`require_approval` rule is
 *  routed to a human (never silently skipped), and an `auto_approve` rule is
 *  skipped (never auto-approved on an unconfirmable predicate). Either way the
 *  rule does NOT behave the way its JSON literally reads against structured
 *  input.
 *
 *  This warning states that plainly at boot so an operator authoring a
 *  `pathPrefix`/`argEquals` rule is never surprised that it behaves more
 *  coarsely than written. It names the effective behavior per effect.
 *
 *  Warn-not-block (same posture as `detectShadowing` / `detectBroadAutoApprove`):
 *  the predicate IS enforceable in a test harness or a future MCP surface that
 *  carries structured args, so an operator shouldn't be blocked from booting.
 *  Not shadow-detection (unreachable rules), not monotonicity (weakening
 *  reloads), not broad-auto-approve (over-scoped grants) — a distinct axis:
 *  "this predicate can't be checked at the live gate, here's what happens
 *  instead."
 */
export function detectUnenforceablePredicates(
  rules: readonly PolicyRule[],
): UnenforceablePredicateWarning[] {
  const warnings: UnenforceablePredicateWarning[] = []
  for (const rule of rules) {
    const predicates: ('pathPrefix' | 'argEquals')[] = []
    if (rule.match.pathPrefix !== undefined) predicates.push('pathPrefix')
    if (rule.match.argEquals !== undefined) predicates.push('argEquals')
    if (predicates.length === 0) continue

    const behavior =
      rule.effect === 'auto_approve'
        ? 'is SKIPPED (never auto-approved on an unconfirmable predicate)'
        : 'FAILS SAFE to human approval'
    warnings.push({
      ruleId: rule.id,
      predicates,
      message:
        `rule '${rule.id}' constrains ${predicates.join(' + ')}, which the MCP ` +
        `permission_request gate cannot evaluate (it carries only a preview string, ` +
        `not structured args). At that gate this ${rule.effect} rule ${behavior}. ` +
        `See 000-docs/policy-evaluation-flow.md § Input-unavailable fail-safe.`,
    })
  }
  return warnings
}
