# Web Analytics Operating Contract

Use this checklist for every run. The goal is a reproducible decision aid, not a persuasive story
built around incomplete telemetry.

## Access Boundary

- Default to read-only analytics endpoints.
- Restrict collection to the sites and period requested by the user.
- Load credentials from the operator-approved secret store at execution time.
- Send a credential only to its configured analytics host over HTTPS.
- Never include passwords, bearer tokens, cookies, or raw environment output in prompts, logs,
  reports, email, Slack, or saved state.
- Do not alter trackers, goals, events, users, or site configuration from this skill.
- Treat email, Slack, and baseline-state writes as separate side effects. Require explicit user
  intent or confirmation when that intent is not already clear.

## Collection Receipt

Capture these fields before analysis:

| Field | Required evidence |
|---|---|
| Backend | Umami, GA4, or another named source |
| Site | Registry name and stable property ID |
| Window | Exact start, end, and timezone |
| Comparison | Exact prior window or `none` |
| Endpoints | Successful operations and status |
| Coverage | Missing, delayed, sampled, or partial data |
| Volume | Visitor and event counts used for conclusions |

An empty response is not automatically a zero. Check the status, site ID, window, and tracker
health before describing it as no traffic.

## Evidence Labels

- **Observation:** A value directly present in the collected response.
- **Comparison:** A reproduced calculation between aligned windows.
- **Hypothesis:** A plausible explanation that requires another check.
- **Recommendation:** An action tied to an observation and a measurable follow-up.

Never convert correlation into causation. For a percentage change, retain both absolute values;
large percentages on tiny baselines must be described as low-volume movement.

## Verification Gate

Before issuing a report:

1. Recalculate headline deltas independently.
2. Confirm numerator, denominator, timezone, and comparison-window alignment.
3. Compare anomaly thresholds with the site registry.
4. Look for tracker outages, deploys, redirects, bots, internal traffic, and campaign changes.
5. Verify that recommendations address the observed metric rather than a guessed cause.
6. Record disagreements between specialists instead of averaging them away.

If verification cannot support a headline, downgrade it to a hypothesis or omit it.

## Failure Behavior

- **One endpoint fails:** Continue with unaffected metrics and name the gap.
- **One site fails:** Continue with other requested sites; do not publish a portfolio total as complete.
- **Authentication fails:** Stop collection, reveal no credential material, and report the failing host.
- **Comparison is unavailable:** Report the current period without a trend claim.
- **Specialist fails:** Preserve its input and error receipt; continue only if the remaining analysis
  satisfies the selected tier.
- **Delivery fails:** Keep the verified report in the current response and identify the unsent channel.

## Delivery Gate

Show the destination, subject or channel, and final report before an external send unless the user
explicitly requested immediate delivery. Respect channel length and formatting limits. Report each
channel as sent, failed, or not attempted; never imply delivery from draft generation alone.

## Full-Tier Memory

Write baseline state only with authorization. Store the source, site, exact window, calculation,
and run date. Do not store credentials or unredacted user-level analytics. A future run must be able
to distinguish a historical baseline from a live query.
