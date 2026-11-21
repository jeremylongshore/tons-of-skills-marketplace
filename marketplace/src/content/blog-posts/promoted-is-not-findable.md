---
title: "Promoted Is Not Findable: Sensitivity Hides It From Export"
description: "A sensitivity classifier label hid two released knowledge base notes from search and export. The write receipt said promoted. Verify the read path."
date: "2026-11-17"
tags: ["ai-agents", "architecture", "automation", "debugging"]
featured: false
canonical: "https://startaitools.com/posts/promoted-is-not-findable/"
---
If you run a knowledge base or RAG store where new entries pass a policy check before an indexer picks them up, a "success" from the write step does not prove anyone can find the entry. This post shows one case where two notes were saved and released but never reached search or export, and the check that catches it. Read the record back through the same path a user would.

The system here is a team knowledge base that holds risky new notes for human review. Releasing a held note sets only the audience, meaning who may read it. A person picks it, such as the whole team. Separately, an automatic classifier reads the text and assigns a sensitivity label (for example public or confidential). The search index and the exporter both skip anything labelled confidential or above. Only the audience is a human choice.

## What broke

Two notes sat in the review queue while a nightly summary recommended releasing them, 13 nights in a row. On night 14 they were released to the whole team, under the owner's standing delegation (a prior instruction to act without asking each time). The release step returned success and wrote its audit records. The review queue was empty afterward. One note was released about 46 hours before its hold would have expired.

The release worked. What broke was the promise the nightly summaries had been making. For 13 nights they said a note released to the team would be searchable. For any note whose body held a literal email address, that was false.

## The label that hid them

Both notes were promoted at sensitivity confidential. The classifier flags a literal email address as a PII pattern, and the git exporter never exports anything at confidential or above. The export check is one function. Its second clause, on audience, did not apply here, because both notes were released to the whole team:

```ts
export function isExportRestricted(memory) {
  return isSensitivityRestricted(memory.sensitivity) || !isExportableAudience(memory.metadata?.audience);
}
```

Search has its own filter. A constant named SEARCH_HIDDEN_SENSITIVITY hides these notes from search results. So each note was durable and reachable by id or list, but it was not exported, and search would not cite it.

The write side looked clean. The same night's compile captured six other memories, moved the store from 18,577 to 18,583, and verified the audit chain over 34,310 events. All of that is true. None of those audit records would have told you if any of the six could not be found. The receipts are good at recording what happened. They were never built to tell you what happens next.

## Where the gate was right

The approve verb refused both held items with a 422. The refusal named its trigger: on hold for human review, sensitivity_gate_flag. That was the correct behavior. An approval cannot release a hold, so the release had to go through the release command.

A dry run of each release returned rc=0 and reported that it would be released for audience tenant (the whole team). The dry run also flagged that this audience was wider than the recommended audience, which required an explicit wider-audience acknowledgement. Then the release ran.

The gap is structural. The release decides who may read a note. Nothing in that step decides whether the exporter may see it, and the classifier decides that alone.

## Where the verification broke

The review ran under MiniMax M3 in a Claude Code session. Its most useful step was the end-state check. It did not stop at the promoted receipt. It went looking for the export, found the confidential label, and reported it.

Its own verification then failed three times. A pre-check scanned only the first paragraph, though capture bodies contain newlines. It scanned the checkout while the live API ran from a release directory. A ps check returned nothing and raised no error, because ps is aliased to procs on this box.

Each one is a small slip. Together they are one mistake. Each check looked at a stand-in for the path that matters, not the path a reader takes. I would not trust any verification that does not touch the read path directly.

## Durable fixes, none built yet

The open task record lists two options, and neither is built. The first is to let a human release also set a published sensitivity. That would be a reviewed downgrade, hash-chained and kept separate from the audience. The second is an allowlist for company role mailboxes on the company's own domain.

The session also found that a re-proposal with the mailbox abstracted classified public, with zero matched patterns. Removing the address clears the label. It is a way around the classifier, not a decision about the note, so I would not count it as a fix. The session ended with that re-proposal unresolved.

The registrar that holds the exporter and its sensitivity check is at https://github.com/jeremylongshore/bobs-big-brain-registrar. Start with apps/git-exporter/src/sensitivity.ts.

## Use this

- After any governed write, export the record and search for its exact text. Treat "promoted" as unverified until both return it.
- Compare each released item's sensitivity label against your export threshold before a digest calls it citable. Report mismatches as findings, not as counts.
- Keep audience and sensitivity as separate decisions in your pipeline. Make any change to the published sensitivity a reviewed, logged step, never a side effect of a classifier.

## Related Posts

- [Reachability and freshness need separate checks](https://startaitools.com/posts/reachability-is-not-freshness/)
- [A fail-closed disclosure gate that rejects PII at intake](https://startaitools.com/posts/disclosure-gate-reject-pii-at-source/)
- [A cron job's process grep matches itself](https://startaitools.com/posts/cron-job-check-matches-your-own-job/)
