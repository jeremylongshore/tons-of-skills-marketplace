---
title: "Secret Scanner False Positives From Whitespace Stripping"
description: "Map each whitespace-stripped secret scanner match back to its source span and join only line wraps. Split-key false positives: Task- prose read as sk- keys."
date: "2026-11-04"
tags: ["debugging", "testing", "typescript", "ai-agents", "automation"]
featured: false
canonical: "https://startaitools.com/posts/secret-scanner-false-positives-whitespace-stripping/"
---
A secret scanner has to catch keys that a line break has cut in two. The fast way to do that is to delete every whitespace character and run the key patterns on what is left. The catch is that deleting whitespace also glues the end of one word to the start of the next. A clean document can then look like it leaks a credential. This post is for anyone who maintains a secret scanner, a data loss prevention (DLP) rule set, or another detector that normalizes text before it matches.

By the end of this post you will have the rule that fixed it and the reason each piece exists. You will also have a checklist of test cases to write, and watch fail, before you trust the fix.

## Whitespace stripping creates false API key matches

The scanner in question checks text for credentials before a team knowledge base accepts it. Its main pass reads one line at a time. Split-key evasion, meaning a key broken across a line break so a per-line scan never sees all of it, needs a second pass over a flattened copy of the text.

The flattened copy that caused the trouble was the one with every whitespace character removed. One of its regex patterns covers API keys. It looks for `sk-` followed by at least twenty letters and digits. The word `Task-` ends in exactly those three characters. Strip the spaces that follow it, and the following words land right where the key pattern expects its body.

The test file for this change uses that exact shape: a sentence beginning "Task-Based Gameplay improves player feedback and progression", followed by a newline and an unrelated sentence. Before the fix, the scanner raised a false positive, a generic API key match. The same thing happens with `risk-` and `desk-` followed by ordinary words, because each one ends in the same letters.

## Map stripped matches back to source spans

The fix keeps the stripped match, but it does not trust it. Every stripped match is checked against the original text before it counts.

First, the scanner keeps a map from each character in the stripped view back to its UTF-16 offset in the source. The map is the only way to answer "what did this match look like before whitespace was removed?" The existing input cap bounds the map and each source slice:

```ts
// Preserve UTF-16 offsets into the original source. Validate the source token
// before applying the fragment-prefix guard, so a genuine line-wrapped key
// attached to an identifier remains visible. The existing input cap bounds
// the map and each source slice.
const stripped = mappedWhitespace(content, false);
const offsets = stripped.offsets;
```

Second, the scanner re-runs the canonical pattern on the original span, after joining only the whitespace runs that contain a line break or a Unicode line separator:

```ts
/** Join padded line wraps, retaining purely horizontal whitespace runs. */
function joinLineWraps(text: string): string {
  return text.replace(/\s+/g, (space) => (/[\r\n\u2028\u2029]/.test(space) ? '' : space));
}
```

Horizontal spaces survive. A word space stays a word space, so `Task-Based Gameplay` does not turn into one long token. A real line wrap, even one padded with indentation, is joined, so a key split across lines comes back together.

Third, the decision itself. The callback below runs for each candidate found in the stripped view (source comments trimmed here). Only the generic key pattern sets `requiresSourceToken`, so only its candidates reach the source check:

```ts
(pattern, match) => {
  if (!acceptedContext(pattern, match, offsets)) return false;
  if (!pattern.requiresSourceToken) return true;
  const start = offsets[match.index];
  const end = offsets[match.index + match[0].length - 1];
  if (start === undefined || end === undefined) return false;
  const source = joinLineWraps(content.slice(start, end + 1));
  if (firstCountedMatch(pattern, source)?.index === 0) return true;
  return start === 0 || !/[A-Za-z]/.test(content[start - 1]!);
}
```

The logic reads in two steps. If the joined source starts with a real key prefix, the match is accepted, even when the greedy stripped match ran on into following prose. If it does not, the candidate survives only when the character before it is not an ASCII letter. That is what stops the suffix of `task-` from becoming a key. A newline is not a letter, so a newline counts as a boundary. The scanner does not look backward through it.

The joining runs only on the slice of source that one candidate covers. The check does not rebuild the whole document, so the cost of each decision follows the length of the match, not the length of the file.

Rejected candidates also have to stop consuming the text. A rejected match can eat the first letters of a later, real prefix. So the walker resumes one character past the rejected match's start, not at its end:

```ts
if (!sourceAccepted) walker.lastIndex = match.index + 1;
```

Without that line, one false match can hide a true key that starts a few characters later. The test suite has a case for exactly that: a false `Task-` match, followed by a real split key on the next line.

```ts
const key = 'sk-' + 'TESTONLY'.repeat(5);
const hasApiKey = (text: string) =>
  scanForSecrets(text).some((match) => match.patternId === 'generic-api-key');

it('finds a later real prefix even when an earlier rejected match consumes its first letters', () => {
  const prose = 'Task-Based Gameplay improves player feedback and progression';
  expect(hasApiKey(`${prose}\nThe credential is ${key.slice(0, 12)}\n${key.slice(12)}`)).toBe(true);
});
```

The controls (test cases with a known right answer) are the part I would copy first. Each boundary case became a failing test before the next change was written. Two of the four prose cases are shown:

```ts
it.each([
  'Task-Based Gameplay improves player feedback and progression',
  'risk-level classification needs careful handling',
])('does not manufacture a key inside prose: %s', (prose) => {
  expect(scanForSecrets(`${prose}\nNext section covers evaluation.`)).toEqual([]);
});
```

Pair that with positive controls, because a rule that only rejects is easy to write. The suite splits a real test key across a newline and expects a finding after an empty prefix, after `key: `, after a tab, and after an opening parenthesis. It does the same with an indented continuation line. The hardest positive case puts the split key directly against an identifier:

```ts
it('detects a real split key directly adjacent to an identifier', () => {
  expect(hasApiKey(`identifier${key.slice(0, 12)}\n${key.slice(12)}`)).toBe(true);
});
```

Each of those cases is a guard against a specific way the fix could go wrong. The prose controls catch over-matching. The split-key controls catch over-rejecting. The identifier control catches a rule that is too strict about what may sit before a prefix.

## Why not the obvious approaches

**Drop the stripped view.** The view exists to catch split keys, and the positive controls depend on it. Removing it would make the prose false positives disappear by also removing the detection the scanner exists for.

**Require a word boundary before `sk-`.** This was the first real attempt: a predecessor-character check. It rejected the prose, but it missed a real split key sitting directly against an identifier, and it still accepted wrapped prose that should have been rejected. The boundary rule alone was not enough. The source-span check is what handles the identifier case.

**Look backward through the newline.** A prose line could end with a word that looks like it might continue onto the next line. Looking back through the line break would let that unrelated text hide a credential on the next line. The fix treats newlines as hard boundaries and does not try to guess soft-wrapped words.

**Apply the same rule to every pattern.** Most patterns do not need the source check. Only the generic API key pattern opts into the source-token check. The env and Slack patterns got a separate line-wrap-only view, because the fully stripped view let short fragments after an assignment join into secret-shaped values. That split was its own change.

## What the verification showed

The main change landed as one squash commit. Its final local gates recorded 4,457 tests passing with five optional skips, and 38 added controls: 33 for the scanner and five for the policy code that consumes its results. Hosted CI passed on the exact head of that change.

The companion change for the env and Slack patterns added the line-wrap-only view. Whitespace runs containing a line feed, a carriage return, or a Unicode line separator are joined, including wrap padding. Horizontal-only runs stay intact. That change added 34 new scanner cases, and 18 of them failed on the prior implementation. After repair, all 34 passed, along with four policy-consumer controls.

The local totals come from the agent that ran them. The pull request body labels them an unreviewed Codex execution attestation, and says plainly that they are not a human-owner signoff. Merges waited for hosted CI on the exact head.

## Four attempts, each forced by a failing control

The rule above was the fourth version. A Codex agent wrote the changes, and a configured automated review on the pull request pushed back three times. Each pushback named a concrete case, and each case became failing controls before the next attempt. The squash commit message records all four.

**Attempt one: guard the prefix.** Four prose regressions failed before this fix. It rejected a match whose prefix followed a letter, and it resumed rejected candidates one character past their start. The `Task-` and `risk-` sentences went quiet.

**Attempt two: validate at the source span.** Review showed the predecessor-character check missed a real split key attached to an identifier, and still accepted wrapped prose. Both review cases failed against attempt one. The design changed here: the scanner began re-running the pattern on the original span. Four more padding cases failed until the wrap joining treated both sides of a line break the same way.

**Attempt three: keep horizontal fragments.** The source check was now too strict. A key broken up with spaces or tabs on one line no longer matched. Six horizontal controls failed. The fix accepts a valid line-wrapped source token first, then falls back to the letter guard for standalone fragments.

**Attempt four: stop looking backward through newlines.** The letter guard scanned backward past a line break, so unrelated prose on the previous line could hide a fragmented key at the start of the next one. Two line-start key controls failed. Newlines became hard boundaries.

The human role in that loop was owning the boundary rule (a letter immediately before a fragment excludes it, and a newline is a boundary) and merging only on hosted CI. The controls are the record of what each attempt got wrong. They are also what let the final rule be checked without trusting the agent's own summary.

## Source-span checks for Heroku UUID context

A third change that day applied the source-first rule to a different failure. The Heroku pattern matches a UUID only when credential words such as key or token appear nearby. After whitespace collapsing or decoding, a UUID could borrow those words from an unrelated line. Detection now evaluates context at the original source occurrence: the lines the match spans, or an immediately preceding credential label or assignment. Only the Heroku pattern opts into this context check. Its new controls cover unrelated lines in either direction, explicit preceding labels, and an earlier unrelated UUID followed by a later associated one.

## Limits

The limits are stated in the change. Line-wrap joining is a heuristic. A fragmented key attached directly to a letter on the same line can go unrecognized unless its line-wrapped source token matches. In the other direction, ambiguous soft-wrapped prose such as `ta` followed by a new line starting `sk-` stays flagged on purpose, because prose on the previous line must never suppress a credential. Arbitrary horizontal obfuscation of env and Slack tokens is outside what this view promises. The Heroku context association shipped separately, and it is a deterministic association rule, not semantic verification of a credential. The scanner also decodes base64 and hex blobs, and it stops after 64 unique decodes. That budget caps recall: a blob seen without context, followed by 63 other accepted unique decodes, can go unreported when it reappears later under a label. No per-occurrence recall is claimed beyond that budget.

The change is in [PR #447 in bobs-big-brain-registrar](https://github.com/jeremylongshore/bobs-big-brain-registrar/pull/447).

## FAQ

### Why does my secret scanner flag prose like "Task-Based Gameplay" as an API key?

Deleting all whitespace joins the end of "Task-" to the next word, and the generic API key pattern matches "sk-" followed by at least twenty letters and digits. The same thing happens with "risk-" and "desk-". Checking each match against the original text rejects these false positives.

### How do I detect an API key split across lines without flagging ordinary prose?

Keep an offset map from the stripped text back to the source, and join only whitespace runs that contain a line break or a Unicode line separator. Re-run the key pattern on that original span and accept it when the joined text starts with a key prefix. Otherwise, accept it only when the character before it is not an ASCII letter. This is a heuristic, so a fragmented key attached to a letter on the same line can go unrecognized unless its line-wrapped source token matches.

### Why must a rejected match restart the search one character later?

A rejected match can consume the first letters of a real key prefix that starts a few characters later. Resuming the search from the rejected match's start plus one keeps that key visible. The post's test suite covers a false "Task-" match followed by a split key on the next line.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Why does my secret scanner flag prose like \"Task-Based Gameplay\" as an API key?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Deleting all whitespace joins the end of \"Task-\" to the next word, and the generic API key pattern matches \"sk-\" followed by at least twenty letters and digits. The same thing happens with \"risk-\" and \"desk-\". Checking each match against the original text rejects these false positives."
      }
    },
    {
      "@type": "Question",
      "name": "How do I detect an API key split across lines without flagging ordinary prose?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Keep an offset map from the stripped text back to the source, and join only whitespace runs that contain a line break or a Unicode line separator. Re-run the key pattern on that original span and accept it when the joined text starts with a key prefix. Otherwise, accept it only when the character before it is not an ASCII letter. This is a heuristic, so a fragmented key attached to a letter on the same line can go unrecognized unless its line-wrapped source token matches."
      }
    },
    {
      "@type": "Question",
      "name": "Why must a rejected match restart the search one character later?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A rejected match can consume the first letters of a real key prefix that starts a few characters later. Resuming the search from the rejected match's start plus one keeps that key visible. The post's test suite covers a false \"Task-\" match followed by a split key on the next line."
      }
    }
  ]
}
</script>

## Use this

- Before you trust a normalizing detector, write one failing control per boundary: a match after a letter, a match after a newline, and an identifier sitting directly before a split key.
- When a match comes from a stripped view, map its offsets back to the source, join only line-wrap whitespace, and re-run the canonical pattern there. Accept it when the joined source starts with a key prefix. Otherwise accept it only when the character before it is not an ASCII letter.
- When a candidate is rejected, resume the search at the candidate's start plus one, so an overlapping real prefix is not hidden by the false one.

## Related Posts

- [gitleaks: Allowlist the Squash Commit in .gitleaksignore](https://startaitools.com/posts/squash-merge-breaks-gitleaksignore-fingerprint/)
- [Reject PII at the Source: A Disclosure Gate at Intake](https://startaitools.com/posts/disclosure-gate-reject-pii-at-source/)
