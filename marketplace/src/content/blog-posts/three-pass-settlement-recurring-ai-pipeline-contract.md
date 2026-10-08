---
title: "Three-Pass Settlement for a Recurring AI Pipeline Contract"
description: "Three evidence passes settle a recurring pipeline contract: every audit gap becomes a file, every gate pin is walked, every rollback is a live drill."
date: "2026-10-07"
tags: ["release-engineering", "devops", "ci-cd", "architecture", "claude-code", "ai-pipelines"]
featured: false
canonical: "https://startaitools.com/posts/three-pass-settlement-recurring-ai-pipeline-contract/"
---
## The defect loops back every sprint

Three nightly runs logged `transcript corroborates` as 1/9, 4/4, 0/9 while the roles receipt (a machine-written record proving a step really ran) said every required agent had completed. The 2026-10-03 Tier-2 run logged 1/9 but had actually run 5/9; four `seo-*` agents and a `code-reviewer` were answered by the catch-all Claude type because their agent types were not registered, then were staged under the role names they were supposed to fill. The parser accepted only one completion shape, so any agent that arrived as its own turn was dropped on the floor. The role receipt said complete, the corpus said otherwise, and the daily job moved on with green CI. Sprint review found it. The fix landed. Next sprint review found another instance of the same shape. The defect looped.

The naive approach is to ship a tighter parser, run the suite, and call it done. That is what pass one did. The independent evidence auditor came back EVIDENCE_INCOMPLETE. A second pass closed most of the named gaps. The auditor came back again, with two more it had no way to know about on the first pass. The third pass closed those exactly, and the auditor returned EVIDENCE_COMPLETE.

This post is about that shape. Not the parser bug, which is local. The three-pass settlement pattern, which is reusable.

## The first pass bundles the evidence, the auditor finds the holes

Pass one (2026-10-05) shipped a settlement PR with the original failure evidence: the three nightly run logs, the parser diff, the role receipt, and a README explaining the chain. It merged. The independent auditor, run from a fresh clone of `intent-os` (the company's internal operations and documentation repo) on the exact merge commit, returned EVIDENCE_INCOMPLETE with five named gaps. Two were obvious in hindsight: no quarantine (set a failed run's files aside instead of publishing them) retention census, and the app suite log from the daily that had motivated the fix was already rotated out and not in the bundle. Three were not obvious: the auditor noticed the harness (the in-repo package of deterministic test-quality checks) hash for the gate manifest had drifted from the code, the `package.json` for the gate runner had been edited after the last pin, and the rollback plan in the settlement body referred to reverting the September fix rather than restoring the last known-good pair.

Each gap is a file the first pass did not think to produce. The first pass was scoped to the parser bug; the auditor is scoped to the evidence chain. A bug fix and an evidence chain are not the same shape, and one pass cannot satisfy both.

## Pass two closes most gaps, the auditor finds the new ones

Pass two was PR #748, "docs(blog-epic): settle the recurring blog contract repair epic (evidence passes 2-3, supersedes #738)". It rebased pass one's commits on current `main`, added a quarantine retention census covering all 13 quarantined runs, added a tarball pin, and rewrote the rollback section to point at the last known-good pair (application v1.30.3 plus skills at commit `a0bae9c`, the pair that had actually run the 2026-10-05 daily) instead of at a hypothetical September revert. It merged. The auditor returned EVIDENCE_INCOMPLETE again, with two new gaps pass two had no way to anticipate:

1. The third-pass settlement-audit itself had been performed on a `tmp/` path that the cleanup job had since purged. The receipt file was real, but the directory it lived in was gone, and the auditor had no way to verify the audit had actually been run from where the receipt said.
2. The harness re-pin for `package.json` was a single-line change but the diff between the stale pin and the new one had never been walked. The pin was a re-blessing of the file at its current state, and "current state" is what made `audit-harness verify` return `HARNESS_TAMPERED` in the first place.

Both gaps were about proof, not about work. The work was done in pass one. The proof that the work was done was not.

## Pass three closes the proof gaps exactly

Pass three is commit `322dd893`, "docs(evidence): close the third-pass settlement-audit gaps for the blog contract epic". Two files, one new content table, one new tarball pin.

The retention census: `quarantine-retention-census.txt` is a hashed census of all 13 quarantined runs, line-counted, sha256 per file, and committed to the bundle. It is the auditor's answer to "where did the third-pass audit actually run from?" It is not the audit output. It is a list of every file the audit was given, with hashes, so a later audit can verify the inputs by re-hashing. The auditor's question was about the input, not the answer, and the census is the input.

The tarball pin: the f8 tarball referenced by the third-pass audit is now pinned in the README's new "Third settlement pass" table by sha256, with independent anchors and a recorded note that the raw app-suite log was deleted by retention and is therefore not in the bundle. The auditor's question was "is the artifact you cite the artifact you mean?" The pin is the answer.

The harness re-pin in PR #755 is the same shape at a different layer. The `package.json` for the gate runner had been edited after the last `.harness-hash` entry (`d2e5060e`, 2026-09-25), and `audit-harness verify` returned `HARNESS_TAMPERED` on `main`. The fix is a one-line update of the pin from `c5d6df1b` to `e2a83601`. The interesting part is the diff walk between the stale pin and the new one. Every commit in that range, examined by hand, was additive gate wiring: `validate:legal-packet` and `validate:coastal-retention` added to the check script, three new test files added to `ci:drills` (a blog liveness row, a host-drift test, a Buzz (the self-hosted team chat relay) topic-allowlist test), and one markdownlint exclusion for unmodified Common Paper and Bonterms source forms. No gate removed. No threshold lowered. No dependency changed. The pin re-blesses a file whose only changes since the last pin are the gates themselves, and the diff walk is what proves that. Without the walk, the re-pin is a rubber stamp. With the walk, the re-pin is a verdict.

## Why not ship the parser fix and stop

The obvious move after the parser fix is to merge the parser fix and call the contract repaired. The contract is the role-counting chain, the parser is one link, the gate manifest is another, the rollback story is a third. Merging the parser and stopping leaves the other two as "we think these are fine", which the auditor cannot read. Recurrence starts the moment a sprint review finds one of the unproven links. The three-pass settlement pattern is what makes the chain auditable instead of asserted.

A second reason: the rollback story. PR #748's body says the rollback is "proven by restoring the last pair with live proof (application v1.30.3 + skills a0bae9c, which ran the 2026-10-05 daily) rather than by reverting the September fix pair." That sentence is the result of a rollback drill, not a claim. The drill checked tree identity, ran transform tests (16/16), ran pytest (1456 passed, 20 skipped), ran the six skill suites, and ran the skill-reading app tests (182 passed) against the restored skills. Every green number is a hash-bounded artifact. If the auditor asked for the rollback proof, the reply is the drill output. The drill is the file the first pass did not write, and the second pass would have been incomplete without it.

A third reason: the harness pin is a gate, not a file. Re-blessing it without walking the diff is the same shape as the original defect: a manifest that says PASS while the underlying file is not what the manifest claims it is. The diff walk is what turns the pin from a trust-me into a prove-it. It is one reviewer shape (read every diff line, classify each as additive gate wiring or not) that the original pass-one author cannot play, because they are too close to the change.

## The settlement shape, as code

The contract between a settlement PR and an auditor is small:

```text
settlement = {
    evidence_bundle:     list[file with hash],
    quarantine_census:   file with hash per quarantined run,
    gate_manifest_pins:  list[file: hash, since: old_hash, walk: diff_summary],
    rollback_proof:      file with restored-pair gate output,
    auditor_verdict:     PASS | EVIDENCE_INCOMPLETE(gaps=[...]),
}
```

Every field is a file. Every file has a hash. The auditor's job is to verify the hashes and re-run the rollback proof. The settlement author's job is to populate every field with a real file, not a description of a file. The auditor can re-run a file. The auditor cannot re-run a description.

The pass-one author populated `evidence_bundle` and stopped. The auditor returned five gaps. Pass two populated `quarantine_census` and `rollback_proof` and re-ran `gate_manifest_pins`, but the re-pin was unverified. Pass three populated the verification of the re-pin and the census of the audit input. Three passes, one PR, one verdict.

## What the three passes actually prove

Pass one proves the defect reproduces and the fix lands. Pass two proves the fix is auditable and the rollback is drillable. Pass three proves the audit's own inputs and the gate manifest's own changes. Each pass is a different reviewer shape against the same chain. The operator session wrote the parser fix and the evidence bundle. The independent evidence auditor verified the chain and named the gaps. The role-counting daily producer verified the parser against three real run fixtures. The harness diff walker verified the pin against the actual commit range. Each reviewer is a different lens. No single lens would have caught all the gaps, because each gap is invisible from the lens that produced the work.

The three-pass settlement is EVIDENCE_COMPLETE on the third pass, with the auditor returning PASS for every one of items 1-11 across the epic, the .2 sub-epic, and the .5 sub-epic. Application suite on the post-merge commit: 1543 passed, 20 skipped, 0 failed. Rollback drill: green across every gate. The defect does not loop, because the next time the auditor runs, the chain has files it can re-verify. The next time a sprint review asks "is the contract still good?", the answer is a list of file hashes, not a story.

## Use this

- When a recurring defect survives a sprint review, write a three-pass settlement PR whose body is a contract with an auditor: every field is a file, every file has a hash, and the auditor's job is to re-run, not to re-derive.
- Walk the diff for every changed gate manifest, not just for source code. A pin re-blesses the file at its current state, and the current state is exactly what made the gate complain. Prove the changes between the stale pin and the new one are additive.
- Prove rollback live by restoring the last known-good pair and re-running the full gate suite against it. The proof is the drill output, not a description of a drill.

## Related Posts

- [name-the-single-authority-in-a-daily-pipeline](https://startaitools.com/posts/name-the-single-authority-in-a-daily-pipeline/): names one authority per concern in a daily pipeline and makes every other source refuse. The settlement pins exactly the manifests that prose-only authority cannot, and the pin is the proof.
- [exit-zero-is-not-push-ok](https://startaitools.com/posts/exit-zero-is-not-push-ok/): a daily job exit-0 does not prove the deliverable was published. The settlement here proves the converse, that a gate that says PASS can still be tampered, and the pin is what makes PASS mean PASS.
- [rank-current-truth-with-the-rerank-not-the-clock](https://startaitools.com/posts/rank-current-truth-with-the-rerank-not-the-clock/): rerank mixes lifecycle into finalScore so chronology cannot beat a current decision. The settlement mixes the auditor verdict into the gate manifest so recurrence cannot beat a completed epic.

## Frequently asked questions

### What is a three-pass settlement for a recurring AI pipeline contract?

A three-pass settlement is a closure pattern for a defect that has already survived one sprint review: pass one ships the fix and the evidence bundle behind it, pass two adds the rollback proof and the gate manifest pins the auditor requires, and pass three closes the auditor's own gaps about proof provenance. Each pass is a different reviewer shape against the same chain. One pass cannot satisfy all three, because each gap is invisible from the lens that produced the work.

### Why does a green CI log say PASS while the auditor returns EVIDENCE_INCOMPLETE?

A green CI exit proves the deliverable was published; it does not prove the evidence chain behind a recurring contract defect is auditable. The auditor looks for files it can re-run: a quarantine census, a tarball pin, a rollback drill, a manifest diff walk. CI does not produce those files. Settlement does.

### How do I prove a rollback when settling a recurring pipeline defect?

Restore the last known-good pair (the application version plus the skills commit that actually ran the daily) into a working tree, run the full gate suite against that tree, and commit the drill output as a file. The proof is the drill output, not a sentence claiming the drill happened. Every green number is a hash-bounded artifact the auditor can re-run.

## Also shipped

- `startaitools` PR #153, the underlying role-counting fix, merged with parser diff, three real-run fixtures, and a sanity test that fails on the pre-fix shape and passes on the post-fix shape.
- `intent-os` PR #755, the single-line `.harness-hash` re-pin, with the diff walk that proves every change between the stale pin and the new one is additive gate wiring.
- `intent-os` commit `2e11e375`, the earlier merge of the original blog contract repair, the merger the settlement supersedes.
- A cross-session log entry at 2026-10-07 23:44 recording the settlement as done, with PR numbers and the dependent `claude-skills-private#10` closure.
- A quarantine retention census, hashed, for all 13 quarantined runs from the contract-repair era, kept as evidence and kept out of the daily run path.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is a three-pass settlement for a recurring AI pipeline contract?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A three-pass settlement is a closure pattern for a defect that has already survived one sprint review: pass one ships the fix and the evidence bundle behind it, pass two adds the rollback proof and the gate manifest pins the auditor requires, and pass three closes the auditor's own gaps about proof provenance. Each pass is a different reviewer shape against the same chain. One pass cannot satisfy all three, because each gap is invisible from the lens that produced the work."
      }
    },
    {
      "@type": "Question",
      "name": "Why does a green CI log say PASS while the auditor returns EVIDENCE_INCOMPLETE?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A green CI exit proves the deliverable was published; it does not prove the evidence chain behind a recurring contract defect is auditable. The auditor looks for files it can re-run: a quarantine census, a tarball pin, a rollback drill, a manifest diff walk. CI does not produce those files. Settlement does."
      }
    },
    {
      "@type": "Question",
      "name": "How do I prove a rollback when settling a recurring pipeline defect?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Restore the last known-good pair (the application version plus the skills commit that actually ran the daily) into a working tree, run the full gate suite against that tree, and commit the drill output as a file. The proof is the drill output, not a sentence claiming the drill happened. Every green number is a hash-bounded artifact the auditor can re-run."
      }
    }
  ]
}
</script>
