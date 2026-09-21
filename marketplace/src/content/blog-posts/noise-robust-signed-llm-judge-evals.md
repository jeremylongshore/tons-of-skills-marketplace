---
title: "Noise-Robust LLM-Judge Evals: Don't Sign a Coin Flip"
description: "An un-seeded LLM judge is a coin flip even at temperature 0. How we made signed eval verdicts replayable instead of attesting noise."
date: "2026-07-07"
tags: ["ai-agents", "evals", "llm-as-judge", "testing", "provenance", "ci-cd"]
featured: false
canonical: "https://startaitools.com/posts/noise-robust-signed-llm-judge-evals/"
---
An un-seeded LLM judge is nondeterministic even at temperature 0. So a single-call binary verdict is a coin flip. And when you sign that verdict into a public transparency log, you have cryptographically attested one noisy draw as if it were ground truth.

That is the integrity bug at the center of this post. It sits underneath every "LLM-as-judge" eval pipeline that gates a rollout, and it gets worse the moment you add a signature, because a [Rekor entry](https://docs.sigstore.dev/logging/overview/) is permanent. You cannot retract a coin flip once a stranger can verify it.

The fix is not "make the judge deterministic" — you can't, the API gives you no seed. The fix is to stop signing the judge's word and start signing a deterministic fold over N recorded votes. Sign the arithmetic, not the oracle. Put the votes inside the signed bytes. Decompose judge noise from execution-sampling noise so you know which layer you're fighting. Gate blockers on measured agreement instead of a single "no". And label your replay fidelity honestly, so silence doesn't imply a guarantee you don't have.

Here is the method as built, the three-arm experiment that proved each layer, and the signed, stranger-verifiable evidence — including an honest BLOCK of our own published skill.

## The problem, measured

The harness is `j-rig`. It evaluates each AI skill against roughly 10 to 20 binary criteria. Some criteria are marked *blocker*, and the rollout gate BLOCKs on any single blocker "no". Judge-method criteria called an LLM judge once per criterion, un-seeded, at temperature 0.

Three failures compound here, and they compound multiplicatively.

**A single temperature-0 API call is not a measurement.** Temperature 0 removes sampling noise from the token distribution. It does not remove serving-stack nondeterminism: batch-composition-dependent kernels and floating-point accumulation order change the logits before the argmax. Two identical requests can land in different batches and produce different tokens. Temperature 0 is a knob on one noise source, not a guarantee of determinism.

**An any-blocker AND-gate is a noise amplifier.** Take ten subjective criteria, each with a judge reliability around 85%. A truly passing skill has to survive all ten:

```
P(clean pass) = 0.85^10 ≈ 0.20
```

Roughly 80% of runs BLOCK a genuinely-good skill from judge noise alone. The gate doesn't measure the skill. It measures the judge's worst day, ten times in a row, and reports the union of every misfire.

**The signature laminated hidden state.** The signed artifact carried only the folded decision. So "we decided BLOCK" was indistinguishable from "the batch scheduler decided BLOCK." The provenance was real and the verdict was noise, which is the worst possible combination: a trustworthy wrapper around an untrustworthy number.

Then we measured it live. Seven identical re-runs of the skill `coreweave-gpu-cost-leak-hunter`, no code changes, same inputs:

**6 BLOCK / 1 SHIP.**

Same skill. Same harness. Same prompt. The verdict flip-flopped across runs. An earlier run had scored it 10/10 and shipped it. That 10/10 was a lucky draw, and we had signed nothing yet — which, in retrospect, was the only piece of good luck in the story.

## What the research settled

Before writing code we ran a 12-agent research pass (positions recorded in an internal research brief, `025-RA-ANLY`, with 16 citations). Five findings survived and became the design.

**Majority voting beats seed-determinism, definitively.** Anthropic's [Messages API](https://platform.claude.com/docs/en/api/messages) exposes no seed parameter. Where seeds exist on other providers they are best-effort and get voided by backend fingerprint drift. Repeat-and-aggregate — the self-consistency pattern — is the only approach that works on every provider, so it is the only approach worth building on.

**N = 5 samples meets the false-BLOCK budget** at a 0.8 agreement quorum. The binomial majority-error works out to ≈ 0.0022 against a 0.005 budget. For blockers we default to N = 11 — deliberate over-provisioning against vote correlation, held as a config default rather than a claim of independence.

**The agreement fraction is evidence, not confidence.** It gets labeled "agreement (votes)" with small-sample intervals. It is never presented as a calibrated probability, and it is *never* the judge's self-reported confidence, which is uncalibrated and should be treated as decoration.

**Sign the deterministic fold over the recorded votes.** A signature must attest "the majority of these N recorded votes," never "the judge said so." That means the fold inputs — the votes themselves — belong inside the signed predicate.

**Label replay fidelity honestly.** An un-seeded API judge caps the artifact below reproducible-from-scratch. So the signed statement says exactly that: `replay_fidelity_level: RF-1`. Silence would let every reader assume the strongest claim. State the weaker true one.

## The method, layer by layer

This shipped to `jeremylongshore/j-rig-skill-binary-eval` main across PRs #184 and #193 (cluster issue #183). Six layers.

### 1. N-sample majority voting per judge criterion

The verdict for a judge criterion is the majority of N independent samples. The measured agreement fraction replaces the judge's self-reported confidence. Plurality ties abstain to "unsure." An errored sample votes "unsure" too — which is the load-bearing detail.

```typescript
// One judge criterion, N independent samples.
// The verdict is the fold, not any single sample's word.
function aggregate(votes: Vote[], blocker: boolean): CriterionResult {
  const tally = { yes: 0, no: 0, unsure: 0 };
  for (const v of votes) {
    // An errored sample is NOT a missing sample. It votes "unsure",
    // so a degraded run lands in the quorum DENOMINATOR and weakens
    // agreement — a 1-of-5 run can never report false certainty.
    tally[v.error ? "unsure" : v.verdict] += 1;
  }

  const n = votes.length;
  const top = maxKey(tally);           // "yes" | "no" | "unsure"
  const agreement = tally[top] / n;    // measured, not self-reported

  // Plurality tie abstains — the judge does not get to guess under a tie.
  const tied = Object.values(tally).filter(c => c === tally[top]).length > 1;
  const verdict = tied ? "unsure" : top;

  return { verdict, agreement, samples: n, votes, blocker };
}
```

The direction of the error handling is the whole point. Missing evidence has to weaken confidence, never strengthen it. If an errored sample silently dropped out of the count, five samples with three errors would report "2/2 agreement, unanimous" — false certainty manufactured by failure. Putting errors in the denominator makes a degraded run *look* degraded.

One compatibility note that mattered for adoption: `samples = 1` stays byte-identical to the legacy path. The whole legacy behavior is just this function with N = 1, so nothing downstream had to change to keep working.

### 2. The stability gate

A multi-sampled blocker "no" that can't clear the agreement quorum is noise, not a finding. It downgrades to a warning. Never a noise-BLOCK. Never a false SHIP either.

```typescript
// A blocker "no" that can't clear the quorum is too unstable to act on.
function applyGate(c: CriterionResult, cfg: GateConfig): Decision {
  const quorum = cfg.blockerQuorum;            // default 0.8

  // One draw carries no stability evidence — the legacy rule stands.
  if (c.samples === 1) return legacyGate(c);

  if (c.blocker && c.verdict === "no") {
    return c.agreement >= quorum
      ? "block"    // stable, reproducible "no" — a real finding
      : "warn";    // too unstable to block on, and too unstable to pass
  }
  return c.verdict === "yes" ? "pass" : "warn";
}
```

The asymmetry is deliberate. A single-call or deterministic result is never downgraded, because one sample carries no stability evidence to downgrade *on*. Only a multi-sampled result has earned the right to be called unstable. A verdict too unstable to reproduce is too unstable to block on, and it is equally too unstable to pass — so it routes to "warn" and asks a human, instead of silently picking a side.

### 3. Execution pinned to greedy decoding

This is the layer we didn't know we needed until the judge stabilized and the noise didn't go away.

The judge was now steady, but re-runs still flipped. The skill-under-test was executing at the API default temperature, around 1.0. So the *output being judged* was a fresh random draw every run. The judge was reliably evaluating a different artifact each time. No amount of judge stabilization can absorb variance in the thing being judged — you have to pin the source.

```jsonc
{
  // Pin the skill-under-test to greedy decoding. Otherwise the OUTPUT
  // being judged is a fresh random draw every run — variance the judge
  // cannot absorb because it is downstream of the judge.
  "execution_temperature": 0.0,

  "judge": {
    "provider": "deepseek",
    "samples": 5,           // per non-blocker judge criterion
    "blocker_samples": 11,  // over-provisioned against vote correlation
    "blocker_quorum": 0.8
  }
}
```

Making `execution_temperature` an explicit spec field, defaulting to greedy, means sampling variance in the subject is now a deliberate decision you can point at — not an invisible inherited API default that silently randomizes your ground truth.

### 4. Vote evidence inside the signed artifact

The `gate-result/v1` predicate — an [in-toto attestation](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md) — carries, per criterion-evaluation: the blocker flag, the verdict, the sample count, the agreement fraction, and the per-sample votes in dispatch order. Plus the aggregation rule in force. A verifier re-derives the verdict from the signed bytes without trusting us.

```json
{
  "_type": "https://in-toto.io/Statement/v1",
  "predicateType": "https://evals.intentsolutions.io/gate-result/v1",
  "predicate": {
    "gate_decision": "fail",
    "rollout_decision": "block",
    "replay_fidelity_level": "RF-1",
    "metadata": {
      "aggregation": {
        "rule": "majority-vote",
        "errored_samples": "count-as-unsure",
        "blocker_quorum": 0.8
      },
      "criteria": [
        {
          "criterion_id": "produces-cfo-grokkable-report",
          "blocker": true,
          "verdict": "no",
          "samples": 5,
          "agreement": 1.0,
          "sample_verdicts": ["no", "no", "no", "no", "no"]
        },
        {
          "criterion_id": "produces-cfo-grokkable-report",
          "blocker": true,
          "verdict": "no",
          "samples": 5,
          "agreement": 1.0,
          "sample_verdicts": ["no", "no", "no", "no", "no"]
        }
      ],
      "stability": { "min_blocker_agreement": 0.8, "unstable_blocker_failures": 0 }
    }
  }
}
```

That is trimmed to the load-bearing fields — the live bundle carries more — but the shape is the real one: the fold inputs live under `metadata`, and the top-level `gate_decision`/`rollout_decision` are re-derivable from them. Two subtleties. The `stability` object is present *if and only if* multi-sampling actually ran — its absence means "no stability evidence was gathered," never a fake measured zero. And `replay_fidelity_level: RF-1` is stamped on every artifact, saying out loud that the fold is replayable from the recorded votes but the votes themselves are not reproducible from scratch. A verifier reading this predicate re-derives `block` from two blocker criterion-evaluations at agreement 1.0 ≥ the 0.8 quorum recorded in the same document. The verdict is a function of signed inputs, not an assertion.

### 5. A decoupled, priced judge

The judge model is independently swappable — `--judge-provider` accepts DeepSeek, Groq, NVIDIA NIM, Anthropic, and others. And every eval reports its real cost per phase: trigger, execution, judge, with the judge's N-multiplier visible.

```
phase      calls
judge         50   ← N=5 × 10 judge criteria; the ONLY phase that multiplies
other         12   ← trigger + execution (unmultiplied)
------------------------------------------------------------------
total         62   74,157 in / 24,695 out tokens   →   $0.017
```

Multi-sampling multiplies only the judge phase. That makes "which judge, at what N" a quality-per-dollar decision you make with a number in front of you, instead of a vibe. Judge quality stops being an article of faith and becomes a line item.

### 6. The noise is observable

Every judge sample emits an OpenTelemetry event, and every criterion event carries its sample count and agreement. That is the audit trail of the noise the majority decision absorbed — capturable to NDJSON.

```jsonc
// one line per judge sample, capturable to NDJSON
{"event":"judge.sample","criterion":"produces-cfo-grokkable-report",
 "sample":3,"of":5,"verdict":"no","dispatch_ms":812,"agreement_so_far":1.0}
```

You can watch a criterion converge, or watch it fail to. The `dispatch_ms` field also feeds the open question about vote correlation — more on that below.

## The experiment

Three arms. Seven identical re-runs each. DeepSeek judge. A frozen copy of the skill so nothing drifts between arms. Every criterion — the blocker included — ran at N = 5 here, so the arms compare apples-to-apples; the N = 11 blocker default is production over-provisioning, not exercised in this worked example.

| Arm | Judge | Execution | Distribution |
|---|---|---|---|
| **Before (legacy)** | single call, un-seeded, temp 0 | API default (~1.0) | 6 BLOCK / 1 SHIP — the flip-flop |
| **Judge fix only** | 5-sample majority, 0.8 gate | API default (~1.0) | 5 BLOCK / 2 WARN — judge stable, output not |
| **Full fix** | 5-sample majority, 0.8 gate | pinned greedy | 7/7 BLOCK — unanimous |

The middle arm is the load-bearing result. It is the proof that verdict noise decomposes into layers. With the judge stabilized but execution still sampling, the runs reported `unstable_blocker_failures: 0` with unanimous votes — the judge had stopped flip-flopping. But two runs landed WARN instead of BLOCK, because the *output* was still a fresh random draw. Stabilizing the judge didn't remove the variance; it moved the variance upstream and made it attributable. `[5/5 no]` unanimous votes on a genuinely degraded output is the fingerprint of execution sampling, cleanly separated from judging noise. You cannot see the second layer until you've killed the first.

The honest residual: one additional run outside the protocol landed WARN even under greedy decoding. Greedy decoding still carries temperature-0 API nondeterminism — the batch and kernel effects from the very first failure mode. That is structural, and it is exactly why the signed claim is RF-1. The fold is replayable from the recorded votes. The votes are not reproducible from scratch. Claiming otherwise would be the lie the whole method exists to avoid.

And the verdict itself is a real finding, not a lab artifact. The blocker `produces-cfo-grokkable-report` fails unanimously — `[5/5 votes, agreement 1.0]` — on two reporting test cases. Under reproducible conditions the skill leads with credential and PromQL requests instead of the CFO-legible dollar headline its own criterion demands. The earlier 10/10 SHIP was a favorable draw at sampling temperature. Pin the temperature and the skill genuinely fails its own bar.

## The working proof

Everything above is a claim until a stranger can check it. Here is where the strangers check it:

**https://labs.intentsolutions.io/eval-sets/iep-self-eval-dogfood/**

| Skill | Verdict | Rekor log index |
|---|---|---|
| `coreweave-gpu-node-forensics` | **SHIP** | [2085904207](https://rekor.sigstore.dev/api/v1/log/entries?logIndex=2085904207) |
| `coreweave-gpu-cost-leak-hunter` | **BLOCK (7/7 re-runs)** | [2091983416](https://rekor.sigstore.dev/api/v1/log/entries?logIndex=2091983416) |

The first row is a second dogfood skill, `coreweave-gpu-node-forensics`, that passed cleanly — a SHIP signed to the same standard — so the board carries an honest pass right next to the honest fail. Both verdicts are signed and anchored in the public Rekor transparency log. A stranger with [`cosign`](https://docs.sigstore.dev/cosign/verifying/verify/) — no account, no keys — downloads the two files from the page and runs the printed command:

```bash
# No account. No keys. Just cosign + the bundle from the page.
# (The page prints the exact --certificate-identity for each artifact.)
cosign verify-blob \
  --new-bundle-format \
  --bundle coreweave-gpu-cost-leak-hunter.bundle.sigstore.json \
  --certificate-identity-regexp '^https://github.com/jeremylongshore/.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  coreweave-gpu-cost-leak-hunter.bundle.json
# → Verified OK
```

Then they fetch the Rekor inclusion proof and re-derive the verdict from the signed bytes: two blocker criterion-evaluations, unanimous "no" at agreement 1.0 ≥ the 0.8 quorum recorded in the same predicate → block. They never trust our conclusion. They recompute it.

The signing ran under a reviewer-gated GitHub Actions identity — [keyless Fulcio](https://docs.sigstore.dev/certificate_authority/overview/), with the git ref frozen into the certificate — approved by a human at a protected environment. The one-way door to a permanent public log stays human-held. No automated job walks through it alone.

Before the page went live it was adversarially verified by a three-lens pass: stranger-cosign, claims-versus-data, and internal consistency, 30-plus checks total. That pass executed the verify commands verbatim, decoded the certificates, and checked every number against the artifact. It caught a would-be broken link and four honesty imprecisions before they shipped. The verification harness is itself part of the product — if the proof page can lie, the method is theater.

The verdict that made all of this worth doing is the second row of the table. It is a BLOCK of our own published skill. Signed, anchored, and published anyway — because a gate that only fires outward is theater. A `coreweave-gpu-cost-leak-hunter` we ship with a public failing grade is worth more to the method's credibility than a wall of green badges.

## What honesty costs

Reproducibility is not free, but at this quality it is cents.

**~$0.017 per full eval at N = 5 on DeepSeek.** That is 74,157 input and 24,695 output tokens across 62 calls, 50 of them judge samples. Multi-sampling multiplies only the judge phase. Buying a replayable verdict instead of a coin flip costs, at this judge and this N, less than two cents.

**"Free" judges carry a throughput tax.** Groq's free tier (~30 requests/minute, as observed) rate-limited a 5×10 sample burst. That failure degraded honestly — the errored samples became "unsure" votes and weakened agreement rather than manufacturing false certainty, exactly as the denominator rule intends. NVIDIA NIM hung a judge call for over an hour, which exposed that judge calls need timeouts and pacing before any free-tier judge can be fairly benchmarked. The cheap judge isn't cheap until you've built the plumbing to survive it.

## What we'd tell anyone signing eval verdicts

1. **Never sign a single draw.** Sign a deterministic fold over recorded samples, and put the samples in the signed artifact. Retrofitting provenance onto a published transparency-log corpus is the one recovery you cannot make. Get the shape right before the first `cosign` call, not after.
2. **Decompose your noise before you fix it.** Judge noise and execution sampling are different layers with different fixes. A stabilized judge is the instrument that lets you *see* the second layer. Fix them in the wrong order and you'll conclude your judge is broken when your subject is the one flipping.
3. **Any-blocker AND-gates amplify noise exponentially.** Gate blockers on measured agreement, and route unstable failures to "warn." A verdict too unstable to reproduce is too unstable to block on — and too unstable to pass.
4. **Missing evidence weakens confidence; it never strengthens it.** Errored samples belong in the denominator. Any code path where a failure quietly raises your agreement fraction is a bug that will eventually sign a lie.
5. **State the replay-fidelity level.** Silence defaults every reader to the strongest, and usually false, claim. RF-1 is not a weakness in the artifact. It is the artifact refusing to overstate itself.
6. **Publish your failing grades.** The signed BLOCK of your own skill does more for the method's credibility than another SHIP badge ever will.

## Limits and open work

This is where the method earns trust — by being explicit about what it does not yet cover.

**Vote correlation is real and unquantified.** Same-judge samples are not fully independent; burst dispatch likely increases co-batching, which correlates errors. That is why blocker N = 11 is over-provisioned rather than derived from a clean binomial. Per-sample timing (`dispatch_ms`) now lands in the evidence so effective sample size can eventually be estimated, but today it's a margin, not a measurement.

**Judge-versus-human validity is unmeasured here.** Agreement measures stability, not correctness. A judge can be perfectly stable and perfectly wrong. The next experiment is Cohen's κ against a human-anchored gold set, target ≥ 0.8. Until that runs, this method guarantees you'll get the *same* verdict twice — not that it's the *right* verdict.

**The evidence store is append-only by convention, not by invariant.** Freeze triggers and hash chaining are specified and tracked, not yet enforced. Convention is a promise; an invariant is a proof. This one is still a promise.

**Telemetry has a home only locally** — NDJSON capture. An OTLP collector on prod plus `gen_ai.*` dual-emit is recommended and tracked. The noise is observable on the dev box; making it observable in production is open work.

None of these are reasons to distrust the signed verdicts. They are the reasons the signed verdicts say RF-1 and "agreement," not "reproducible" and "confidence." The method's honesty is load-bearing precisely because the limits are stated in the artifact.

## Also shipped

Same day, a separate estate-hygiene artifact landed in intent-os: a hand-maintained **automations and notifications registry** (`mission-control/automations.md`, PRs #32/#33) — a single index of every unattended job across cloud routines, GitHub Actions crons, dev-box crons, and production VPS daemons, plus the Slack channel matrix and notification-channel reachability (cloud routines can't reach the tailnet ntfy topics; there is no Slack *read* path, so asks living only in Slack are invisible to agents). The governing rule: an automation that isn't in the registry effectively doesn't exist. Same instinct as the eval work — make the hidden machinery legible before it surprises you.

## Related posts

- [Eval-gated model swaps: shipping gpt-5.4 as a one-line config switch](/blog/eval-gated-model-swap-gpt-5-4/)
- [The moat is the trust layer: enforced egress, code-enforced citations, tamper-evident audit](/blog/the-moat-is-the-trust-layer-nexus-byok-rag/)
- [Every safety gate has a failure direction](/blog/every-safety-gate-has-a-failure-direction/)

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Noise-Robust LLM-Judge Evals: Don't Sign a Coin Flip",
  "description": "An un-seeded LLM judge is a coin flip even at temperature 0. How we made signed eval verdicts replayable instead of attesting noise.",
  "datePublished": "2026-07-07T10:00:00-05:00",
  "dateModified": "2026-07-07T10:00:00-05:00",
  "author": { "@type": "Person", "name": "Jeremy Longshore" },
  "publisher": { "@type": "Organization", "name": "Start AI Tools", "url": "https://startaitools.com" },
  "url": "https://startaitools.com/posts/noise-robust-signed-llm-judge-evals/",
  "mainEntityOfPage": "https://startaitools.com/posts/noise-robust-signed-llm-judge-evals/",
  "articleSection": "AI Engineering",
  "keywords": ["ai-agents", "evals", "llm-as-judge", "testing", "provenance", "ci-cd"]
}
</script>
