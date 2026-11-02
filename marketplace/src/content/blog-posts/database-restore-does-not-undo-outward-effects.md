---
title: "A Database Restore Does Not Undo Sent Email or Envelopes"
description: "An AST-scanned registry makes a restore effect journal's coverage testable. Building it exposed a path that would mail a signer a second contract."
date: "2026-10-26"
tags: ["testing", "python", "architecture", "devops", "debugging"]
featured: false
canonical: "https://startaitools.com/posts/database-restore-does-not-undo-outward-effects/"
---
Restore a database to last night's backup and the rows go back in time. The email your app sent at 2 a.m. does not. Neither does the e-signature envelope it created, the mailbox password it rotated or the message it appended to a Sent folder. The restored app has no memory of any of them, so it can do them again: a second contract envelope to the same signer, a duplicate confirmation email to the same applicant.

This post covers a three-part pattern for that problem. First, a registry: every function that calls an outside service, tagged with how a restore recovers it. Second, a test that reads the source code and fails the build when that registry and the code disagree. Third, for an effect nothing reads back and the review does not close, a check after the restore that asks the outside service what it created since the backup.

The app here is an onboarding system. It sends mail over SMTP and through Django's mailer, creates and distributes agreements through Documenso (a self-hosted e-signature service), writes to a mailbox host, appends to IMAP folders and calls LLM agents. It also keeps an effect journal (an append-only log of outward actions, the side effects a rollback cannot reach, kept outside the database). After a restore, a post-restore review reads that journal and the providers, then decides whether to lift the restore hold (release the restored system for normal use).

## What a restore forgets

The journal only helps if it covers every effect. Before this work, that coverage was a hand-written claim in a design document, written after a code review. Nothing checked it.

A hand-written list of covered effects drifts in one direction. Code adds a new provider call. Nobody updates the list. The list still reads as complete, and the next restore drill passes because the drill never exercises the new call. [A Green Recovery Drill Can Still Be Lying](https://startaitools.com/posts/a-green-recovery-drill-can-still-be-lying/) covers other ways a restore check reports green.

That is the failure mode to design against. The restore itself is fine. The claim about what the restore can recover is the part that rots.

## The registry: one recovery class per function and family

The fix starts with a data file, `workflow/effects.py`. It registers 40 functions, two of them markers rather than effects, grouped in seven families: journal writes, SMTP, Django mail, Documenso writes, mailbox host writes, IMAP appends and model runs.

Each function gets one class for each family it touches, plus a reason. Six classes make up the recovery vocabulary:

- **journaled_before:** a journal entry is written and fsynced before the effect becomes a fact. Restrictive effects (such as a staff deactivation or an access revocation) are prepared this way. If that write fails, only the erasure and custody records refuse the effect; see below.
- **journaled_after:** the entry is written on commit, once the effect is a fact. A crash can lose it, but it can never invent an effect.
- **provider_read:** no entry. A named post-restore function reads the effect back at the provider.
- **checked_before:** no entry. The action reads the provider before it writes, so a repeated run is idempotent: it finds the effect and skips it.
- **covered_by_review:** nothing reads it back. The post-restore review closes what the effect handed out, such as every live confirmation, password-setup and withdrawal link.
- **marker:** an entry about the journal itself, such as the restore point. Not an effect.

Three entries copied from the registry as the first PR shipped it show the shape. The `gap` on the first one comes back below.

```python
"agreements.handlers:CreateAgreement.call": {"documenso": Site(PROVIDER_READ,
    "a restored instance's envelope is read by id, or found by its external key",
    by=READ_ENVELOPES, gap="9kg.76")},
"agreements.handlers:DistributeAgreement.call": {"documenso": Site(CHECKED_BEFORE,
    "re-reads the envelope and skips one already PENDING",
    by="agreements.handlers:DistributeAgreement.call")},
"agreements.keystore:destroy": {"journal": Site(JOURNALED_BEFORE,
    "custody key destruction, appended before the unlink",
    ("custody_key_destroyed",))},
```

The key is the module plus the function's qualified name. The value maps a family to a `Site`. The `by` field names the function responsible for recovery, so a reviewer can follow the claim to code instead of trusting a sentence.

`Site` is a frozen dataclass, copied from the registry with its comments:

```python
@dataclass(frozen=True)
class Site:
    cls: str
    why: str
    kinds: tuple = ()  # journal kinds written (the journal family only)
    via: str = ""  # the registered function whose journal entry covers a provider or model call
    by: str = ""  # the function that reads the effect back, checks it first, or closes it in the review
    gap: str = ""  # the bead for a known uncovered part
    after: tuple = ()  # kinds of a journaled-before site written after the effect
```

The `gap` field matters more than it looks. It lets the registry admit an uncovered effect without lying about it, and it must carry a tracked-task ID. The `after` field lists kinds a journaled_before site writes once the effect is done, such as an outcome record, and the test checks it names some but not all of that site's kinds.

## Why not a runtime decorator?

The obvious design is a decorator: mark each effectful function `@effect("smtp")` and check coverage at runtime. The PR chose call-site discovery instead, for two reasons.

First, discovery needs no change to application code. The registry is data and the test is static.

Second, a decorator only knows about functions somebody remembered to decorate. That is the same failure as the hand-written list, moved into the source. Discovery reads the code and finds the provider call whether or not anyone thought to mark it. A new `send_mail` with no registry entry fails the build.

## The test: find every outward call with `ast`

`tests/test_effect_registry.py` parses every source file into an abstract syntax tree with [Python's `ast` module](https://docs.python.org/3/library/ast.html) and builds a map of `{function: {family: calls}}`. Its import resolver handles module imports, aliases, relative imports and by-name imports, because `from django.core.mail import send_mail as sm` is still a mail call.

It has nine test functions. The first three check the registry against the source, and the fourth checks that the scanner knows every provider write method:

```text
test_9kg62_every_function_with_an_effect_is_registered_and_no_registration_is_stale(sites)
test_9kg62_each_class_matches_what_the_function_does(sites)
test_9kg62_every_journal_kind_has_a_writer_and_each_restrictive_kind_is_prepared(sites)
test_9kg62_the_scanner_knows_every_write_method_of_each_provider_client()
```

Of the other five, four test the scanner on synthetic source (import spellings, kind resolution, lookalike calls, an unreviewed outward module). One checks the real code against the outward-module allow-list.

Between them, the tests fail when:

- a function with an effect is unregistered, an entry is stale, or the family is wrong;
- the class does not match the calls the function makes;
- a journaled_before entry is written after the provider call it precedes in the same function;
- a checked_before action writes before it reads;
- `by` or `via` is missing, or `gap` is not a tracked-task ID;
- a journal kind does not resolve to a literal, a constant or a literal caller argument;
- the provider client has a write method the scanner does not know;
- any module outside a reviewed allow-list of twelve imports a network or process module, or writes, moves or removes a file.

The last two are the drift guards for the scanner itself. If someone adds a new write method to the Documenso client, the scanner has no rule for it, and the fourth test fails until a human teaches it. If a thirteenth module starts opening sockets or deleting files, the allow-list test fails.

The ordering rule is the least obvious one. "Journaled before" is only true if the journal write precedes the provider call in source order. Here is the idea, reduced to a hypothetical sketch (not the shipped code):

```python
# Hypothetical reduction of the ordering check.
def first_call_line(fn, matches):
    lines = [n.lineno for n in ast.walk(fn)
             if isinstance(n, ast.Call) and matches(n)]
    return min(lines, default=None)

journal_at = first_call_line(fn, is_journal_write)
provider_at = first_call_line(fn, is_provider_call)
if journal_at is not None and provider_at is not None:
    assert journal_at < provider_at
```

This only decides order inside one function. Order across functions is not checked.

## Verifying the AST test with hand mutations

A static test that passes on day one proves nothing about whether it can fail. The same rule for a CI gate is in [Make the Guard Prove It Can Fail](https://startaitools.com/posts/the-gate-that-could-not-fail/). So the verification was mutation by hand: break the code or the registry on purpose, one change at a time, and confirm the intended test catches it.

The registry test and the repository's test-selection test together ran 28 passed, 0 failed. Then 21 hand mutations, each caught by the test meant to catch it. The first round of twelve covered a dropped site, a stale entry, the wrong class, the wrong kind, a bad `via`, a missing `via`, a dropped family, a marker that was really a record, an undeclared kind, a restrictive kind never prepared, an empty reason and an injected unregistered send.

The second round of nine: a dropped Django mail site, a missing reader, an absent `by`, a non-task `gap`, a removed erasure completion caller, `FileCopy` writing before it reads, the `send_begun` journal write moved after SMTP, a dynamic journal kind and a removed staff-role prepare. Separately from the 21, an injected module with outward calls was also caught.

## What writing the registry and its QA pass found

The first version of the registry was incomplete, and a separate QA agent pass (static reading only) showed it. That pass returned seven findings. Five were fixed in the PR. One was filed as a tracked task and one was partly fixed. The PR's own list of five findings, below, draws on both the writing and the QA pass and only partly overlaps the QA agent's seven. Each one says what happened to it.

**Three applicant mails were missing (fixed).** The contact confirmation, the password setup and the withdrawal link go through [Django's mailer](https://docs.djangoproject.com/en/stable/topics/email/), not the app's correspondence transport. The first version of the registry missed all three. Django mail is its own family in the registry. The post-restore review covers them by superseding every live link they carry.

**`FileCopy` was misclassified (fixed).** It was registered as read back by the Sent-folder reader. That reader skips filed copies. What `FileCopy` actually does is search the Sent folder before it files, so it is now checked_before, with an order check behind it.

**The revocation's host calls are outside the journal (registered as covered_by_review).** Password rotation and forwarder removal run before the transaction that prepares the revocation entry. The review's revocation round covers them, so they are registered covered_by_review.

**A failed restrictive prepare does not stop its effect (recorded, not changed).** The failure is logged, counted and refused at readiness. Only the erasure and custody records refuse their effect outright. This was recorded, not changed.

**A second envelope after a restore had no coverage at all (filed, then closed by a follow-up PR).** An agreement created and distributed after the backup has no row once you restore. Nothing read its envelope. The external key is random, so the restored system would create a new agreement and distribute a second envelope to the same signer. The registry could only mark this as a gap, because a runtime fix did not belong in a test-only PR.

That last one was the main finding. Writing and reviewing the registry forced every function through the question "who reads this back?", and for envelopes created after the backup the honest answer was "nobody". The test could not fail on this. It could only carry the gap.

## Closing the gap with a bounded Documenso envelope listing

The [follow-up PR](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/119) added an unknown-envelope scan to the post-restore Documenso read, `agreements.restore.read_envelopes`.

It lists the Documenso team's envelopes from every template, newest first, back to one hour before the backup's start, so a template the restored tables do not know is covered too. Any envelope with the app's key shape (`ag_` plus 32 hex characters) that no restored agreement or envelope attempt names, by envelope id or external key, opens one review item. The item is keyed by a digest of the envelope id, and the raw id is stored in neither the item nor its audit event. It carries the application only when exactly one verified applicant is a signer.

The listing is bounded by a configured page limit (the PR's risk note puts it at 20 pages of 100). If it hits that limit before reaching the backup's start, it reports `incomplete:listing_limit`, and any status other than `ok` refuses to lift the restore hold. A truncated listing is treated as incomplete, never as clean. The registry entry's `gap` was then removed, as the task's acceptance required. That PR's targeted run was 82 passed. The gap is closed in code, pending the provider check described below.

## Why not journal every create instead?

The alternative was a journal entry per envelope create. The listing won for two reasons. It already existed for reconciliation, so no new write path. And it finds a create whose journal append was lost, which a journal entry cannot do by definition.

Envelopes without the app's key shape belong to another writer on the same Documenso team and are ignored. The cost of that team-wide listing is volume: another writer's envelopes count toward the page limit. Hitting it fails closed until the system's operator raises the limit or resolves the items by hand.

## Known blind spots

The test's docstring lists its own blind spots:

- receivers held in attributes or reached through `getattr`;
- a database write that should be journaled and is not;
- whether a named reader actually reads what the entry says.

The ordering check also works only inside one function, as noted above.

Documenso's real behaviour is also unverified. Its list ordering, default status filter and field names are not confirmed against the installed version, so the scan checks order itself and never trusts a page count. A canary against the real provider is where that gets settled. Resolving an unknown envelope is currently by the operator's note alone, and whether a note is enough is the operator's call.

The test is brittle by design. Rename an effectful function, add a provider write method or add a file-writing module and the build fails until someone reviews the change. That is intended: a failing build is the moment the hand-written list used to go stale silently.

## Also shipped

- A `journal-ship` service copies the effect journal off the production host, so the journal survives the host it describes. It runs with `network_mode: none` because it only reads and writes files ([PR #123](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/123), 239 passed in its targeted run).

## Use this

- List every function in your app that calls a provider (mail, e-signature, payments, mailbox APIs) and give it a recovery class for each provider it touches, plus the name of the function that recovers it.
- Write a static test that discovers those calls from source, including aliased and relative imports, and fails on any call it can resolve that the registry has not classified; then mutate it by hand until each failure mode has been caught once.
- For an effect that nothing reads back and the review does not close, add a post-restore provider listing with a time floor just before the backup's start and a page limit, make a truncated listing keep the restore hold in place, and confirm the provider's list behaviour against the real service.

The registry and its AST test are in [catalyst-onboarding-v2 PR #117](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/117).

## Frequently asked questions

### What is an effect journal?

An effect journal is an append-only log of outward actions, kept outside the database. After a restore, a post-restore review reads that journal and the providers, then decides whether to lift the restore hold.

### How do you stop a restored app from repeating an email or envelope?

Give every function that calls an outside service one recovery class per provider family in a registry, and name the function that recovers it. A checked_before action reads the provider before it writes, so a repeated run finds the effect and skips it. Where nothing reads an effect back and the review does not close it, a bounded provider listing looks for envelopes the restored database does not name.

### How can a test catch an effect nobody registered?

An AST test parses every source file, follows aliased and relative imports, and fails the build when a function with an effect is unregistered, stale or in the wrong class. It was checked with 21 hand mutations, each caught by the test meant to catch it. It still cannot see receivers held in attributes or reached through getattr.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is an effect journal?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "An effect journal is an append-only log of outward actions, kept outside the database. After a restore, a post-restore review reads that journal and the providers, then decides whether to lift the restore hold."
      }
    },
    {
      "@type": "Question",
      "name": "How do you stop a restored app from repeating an email or envelope?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Give every function that calls an outside service one recovery class per provider family in a registry, and name the function that recovers it. A checked_before action reads the provider before it writes, so a repeated run finds the effect and skips it. Where nothing reads an effect back and the review does not close it, a bounded provider listing looks for envelopes the restored database does not name."
      }
    },
    {
      "@type": "Question",
      "name": "How can a test catch an effect nobody registered?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "An AST test parses every source file, follows aliased and relative imports, and fails the build when a function with an effect is unregistered, stale or in the wrong class. It was checked with 21 hand mutations, each caught by the test meant to catch it. It still cannot see receivers held in attributes or reached through getattr."
      }
    }
  ]
}
</script>

## Related Posts

- [Every Claim Needs a Shipped Source and an Executable Proof](https://startaitools.com/posts/working-is-not-proven/)
- [The Drills Passed. Reality Did Not.](https://startaitools.com/posts/the-drills-passed-reality-did-not/)
- [Rehearse the deploy, not the test suite](https://startaitools.com/posts/rehearse-before-production-catches-what-tests-cant/)
