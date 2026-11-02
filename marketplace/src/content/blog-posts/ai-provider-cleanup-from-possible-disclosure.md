---
title: "Erasure Requests: Model Provider Cleanup From Reservations"
description: "Derive a model provider cleanup set from reservations and confirmed calls. An erasure request that skips a reserved call may leave personal data at the vendor."
date: "2026-11-01"
tags: ["python", "architecture", "testing", "debugging", "ai-agents"]
featured: false
canonical: "https://startaitools.com/posts/ai-provider-cleanup-from-possible-disclosure/"
---
When a product has to honor an erasure request, the cleanup obligation owed to a hosted model provider has to come from what was possibly sent, not from what we can prove was sent. We had it derived from the wrong signal, and the two directions of that failure were not equally bad: one asks a vendor for a cleanup of data it never received, the other can leave personal data sitting at a vendor outside our control.

What follows is the rule that replaced it, the SQL condition that implements it, a reversible migration (a database change you can roll back) that installs it, and a regression module that reproduces both defects.

The product here is an onboarding system. Its assessment path sends applicant data to a hosted model provider to score assessments, and its reply interpreter uses the same provider. When a person asks to be erased, the system computes a handoff list: the external parties that now owe a cleanup because they may hold that person's data. The model provider is one entry on that list, written as `model_provider`.

Our own database holds narrower evidence about a provider call than it does about a row. We record that we reserved a request before sending it, and we record that a provider call consumed requests. Between those two records sits the part we cannot resolve: whether a reserved request that never completed actually crossed to the vendor. Any obligation we owe that vendor has to be derived from the wider of the two records, the reservation rather than the consumption count, because the two ways of getting it wrong cost very different amounts.

## The old rule asked only whether a run row existed

The old rule lived in a catalog module (the Python file that generates the erasure function's SQL), inside the SQL body of the function that builds the handoff list. It looked like this:

```sql
  IF EXISTS (SELECT 1 FROM public.assessments_assessmentrun r WHERE r.application_id = ANY(v_apps)) THEN
    v_handoffs := v_handoffs || 'model_provider'::text;  -- what the model provider kept of a request, if anything
  END IF;
```

Any assessment run row at all for the erased person's applications was enough. No column was compared. The query could not tell a run that consumed a provider call from a run that was created and then refused before a call was ever made.

Both defects came out of that one line, and they point in opposite directions.

**False positive.** An assessment refused on suspension produced a run row and no provider call. The old rule still reported `model_provider`. The vendor owed nothing, and it would have been asked to clean up data it never received.

**False negative.** A person's inbound reply can be reserved for interpretation by the provider while no assessment run exists for them. The legacy predicate found no run row, so the entry was omitted. The provider might have received the reply, and nobody would have asked it to drop anything.

Neither defect is something you find by reading the SQL twice. The condition looks conservative, and conservative is the right instinct here. It is just conservative in the wrong place: careful about the row's existence, careless about the request's fate.

## How do I derive a model provider cleanup obligation?

We derive it from what was possibly sent, not from what we can prove was sent. A reserved provider call counts as evidence of disclosure even when the call never completed, because an unfinished run is not evidence of absence. An abandoned call is the harder case, because there the run exists and did not finish, and the reason is that the provider's side of the call is not something our database can resolve. When a run is refused before anything is reserved, no handoff is owed.

The new predicate lives in `erasure/catalog.py` as `MODEL_PROVIDER_HANDOFF`:

```python
MODEL_PROVIDER_HANDOFF = """EXISTS (SELECT 1 FROM public.assessments_assessmentinvocation i
             WHERE i.application_id = ANY(v_apps) AND i.reserved_requests > 0)
     OR EXISTS (SELECT 1 FROM public.assessments_assessmentrun r
                WHERE r.application_id = ANY(v_apps) AND r.requests_used > 0)
     OR EXISTS (SELECT 1 FROM public.correspondence_replyinterpretation i
                WHERE i.application_id = ANY(v_apps) AND i.reserved_requests > 0)"""
```

Three signal sources and two different columns:

| Signal | Column | What it establishes |
|---|---|---|
| Assessment invocation (assessment and clarification rounds) | `reserved_requests > 0` | A provider call was reserved. A possible disclosure, even if the call never completed. |
| Assessment run | `requests_used > 0` | A provider call consumed requests. A confirmed disclosure. |
| Reply interpretation | `reserved_requests > 0` | Reply-interpretation provider work was reserved. A possible disclosure. |

The rule now reads, as recorded in the internal launch plan: a queued or suspension-refused run that reserved nothing and recorded nothing owes no model provider handoff. Positive assessment and clarification reservations, recorded assessment requests and reply interpretation reservations keep the handoff, including abandoned calls whose provider outcome is uncertain. Reply-only calls count even without an assessment run.

The inversion that matters is that a reservation became a first-class signal instead of an implementation detail. Previously a provider call surfaced only as an assessment run row. The reservation was always recorded and the old rule never looked at it. Now the rule reads that column, so the ambiguous middle (reserved, then interrupted, then abandoned) is answered from a recorded number instead of inferred from the mere existence of a run row.

## Why not count only confirmed calls, or ask the provider?

The obvious fix is to count only confirmed calls: drop the reservation checks, keep `requests_used > 0`, and let the ambiguous cases fall on the floor. It removes the false positive entirely and the query gets shorter.

It also creates a silent false negative, and that is the bad trade. A call that was reserved and then interrupted leaves no confirmed record, but the provider may have received it. The absence of a finished run is not evidence of absence of disclosure. When the evidence is missing rather than negative, the only safe reading is that a disclosure is possible, and a possible disclosure still creates a cleanup obligation.

The other obvious approach is to ask the provider. Read the vendor's logs for the person's identifiers and use the answer. That makes the vendor a runtime dependency of an erasure request, it assumes the vendor can match our identifiers to what it received, and it assumes the vendor keeps logs long enough to answer. None of those hold in general, and the cost when they do not hold is the person's data still sitting there.

So the obligation is deliberately a superset of confirmed disclosures, and we accept the false positive the new rule keeps. That false positive costs a message to a vendor and some noise in our own logs. The false negative can cost a person their right to be forgotten.

One more reason the set has to lean wide: we do not get to know what the provider does with a request after we send it. Retention, training and logging on their side, if they happen at all, happen outside our database. Our own records tell us a request was reserved for sending, and a confirmed call (`requests_used > 0`) tells us the provider consumed it. Neither tells us it kept anything. The reservation is our evidence that it might have gone out.

## Installing it without rewriting history

The change ships as a reversible migration, `erasure/migrations/0008_model_handoff_evidence.py`:

```python
"""9kg.73: queued or refused model work alone creates no provider cleanup obligation.

Reservations remain conservative evidence of possible disclosure, including abandoned calls
and reply interpretation without an assessment run. Reinstall both erasure functions without
rewriting rows, signed records, function ownership or grants.
"""

# imports elided

LEGACY = "EXISTS (SELECT 1 FROM public.assessments_assessmentrun r WHERE r.application_id = ANY(v_apps))"


def install(schema_editor, *, reverse):
    ...  # retention and existing lookups elided
    for replay in (False, True):
        statement = catalog.erase_sql(retention, existing, replay=replay)
        if statement.count(catalog.MODEL_PROVIDER_HANDOFF) != 1:
            raise RuntimeError("unexpected model handoff definition")
        if reverse:
            statement = statement.replace(catalog.MODEL_PROVIDER_HANDOFF, LEGACY, 1)
        schema_editor.execute(statement, params=None)


# forwards, backwards and the Migration class elided
```

Three things are worth pulling out of that file.

The loop runs over both function variants, the normal erasure and the restore replay. The two have to carry the same rule, because a restored database can bring back rows for a person erased after the backup, and the replay re-runs the erasure against those rows. What a restore leaves behind is covered in [A Database Restore Does Not Undo Sent Email or Envelopes](https://startaitools.com/posts/database-restore-does-not-undo-outward-effects/). If replay derived the entry differently, the replay would answer a different question than the erasure it replays.

The count check keeps the installed SQL and the catalog in agreement. The function body is generated from the catalog, so the migration asserts that the new predicate appears exactly once in the generated statement. A later edit that drops the clause or duplicates it fails the migration instead of shipping a function that quietly disagrees with the source it came from.

The reverse path swaps the new predicate back to the legacy one, which is what makes the migration reversible. The old rule is carried in the file as a constant, so reversing is a substitution instead of a guess. Ownership, grants, historical rows and signed erasure records survive the reinstall, so no signed record is rewritten.

Nothing else moved. Provider activation, rate limits and token policy are untouched.

## The regression that reproduces both defects

`tests/test_erasure_model_handoffs.py` landed at 150 lines with four test functions in it. The first of them covers the asymmetry in a single body:

```python
@pytest.mark.parametrize("replay", [False, True], ids=["erase", "replay"])
@pytest.mark.parametrize("called", [False, True], ids=["refused", "provider-called"])
def test_9kg_73_a_suspended_assessment_owes_no_provider_handoff_but_a_real_call_does(
    a, monkeypatch, settings, decided, replay, called
):
    if called:
        app, run, seen = assessed(a, monkeypatch, valid())
        assert run.status == "succeeded" and seen["calls"] == 1
        assert AssessmentInvocation.objects.filter(run=run).exists()
    else:
        app, run, seen = queued(a, monkeypatch, settings, valid())
        settings.CATALYST_ASSESSMENT_MODEL = "none"
        run_worker()
        run.refresh_from_db()
        assert run.status == "refused" and seen["calls"] == 0
        assert not AssessmentInvocation.objects.filter(run=run).exists()
    closer = grant(a, staff(a, "model-erasure-closer"), "close_application")
    closure.close_application(app.pk, closer, "closed", "Synthetic erasure regression")
    assert ("model_provider" in handoffs(a.committed, app, replay)) is called
```

The `called` parameter doubles as the expected answer, which is why the last line can assert `is called` instead of branching on it. The `refused` branch builds the case that used to produce the false positive. Setting the model to `none` is the suspension condition, so the worker runs, the run is refused and the fake provider records zero calls. The `provider-called` branch is the control, where a real call happened and the handoff is owed. The `closure.close_application` call closes the application through the staff closure helper before the erasure runs. The second function, `test_9kg_73_reply_only_model_reservations_keep_the_provider_handoff`, covers the false negative. It builds a reply interpretation that reserved provider work, in an application with no assessment run, and asserts across both erasure paths that the handoff appears when something was reserved and stays absent when the reservation count is zero.

The third test covers the ambiguous middle, the case the old predicate could not tell apart from a run that reserved nothing:

```python
@pytest.mark.parametrize("status", ["started", "abandoned"])
def test_9kg_73_an_uncertain_reserved_call_still_owes_provider_cleanup(
    privileged_reset, decided, status
):
    app = subject()
    reserved_run(app, status)
    assert "model_provider" in handoffs(privileged_reset, app, False)
```

A call that was reserved and then started or abandoned still owes a model provider cleanup, because the provider's side of that call is not something our database can resolve.

The fourth function, `test_9kg_73_both_functions_reverse_and_reapply_without_changing_rows_or_grants`, reverses the migration and reapplies it, then checks that the rows, the function ownership and the grants survive the reinstall.

The helper three of the four tests call is what ties the two paths together. It runs the installed `catalyst_erase` function for the normal path and the installed `catalyst_erase_replay` function for the restore path, so whichever path is under test is held to the same rule.

## Result

The eight-case regression, the module's first eight cases, four from the suspended-assessment matrix and four from the reply-only matrix, reproduced both defects before the change: 4 expected failures and 4 passing controls, in 30.32 seconds. Making the guard prove it can fail before trusting that it passed is the same rule as in [Make the Guard Prove It Can Fail](https://startaitools.com/posts/the-gate-that-could-not-fail/). After the fix, all 15 focused checks passed in 102.60 seconds. The coverage included actual worker and fake-provider cases, both erasure paths, uncertain calls, reversal and reapplication with exact row, function and grant preservation, the installed SQL checked against the catalog, schema inventory and model synchronization, and the existing complete erasure-reversal check.

Ruff, formatting, Markdown, document index and diff checks pass. Neither a live provider nor a production database took part in this change or in its tests, and nothing is deployed yet, so no vendor ever received one of these cleanup requests. Full CI was the merge gate, and the change is merged.

Deployment and the live handover to the new version remain separate open work. The internal launch plan and the approved migration set in `tests/test_database.py` were updated with the change, so the next person reads the rule instead of rediscovering which signal was wrong.

## Also shipped

- A sibling fix from the same day ([PR #178](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/178)) requires restore-recovery evidence to be timestamped at or after the current transaction's start, not just to carry a matching transaction ID, so a rebuilt cluster cannot reuse an old transaction ID as fresh authorization.
- Restore replay now matches normalized inbound senders against the signed erasure record ([PR #177](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/177)), so restoring a backup cannot resurrect inbound mail and intake counters for a person erased after that backup was taken.

## Use this

- Derive any obligation to ask an external party to delete data from what was possibly sent, not from the existence of a row. A reservation you wrote before the call is the evidence that a request might have reached the vendor, and a refusal that reserved nothing is evidence that nothing did.
- Give the delete path and the restore path the same predicate, then test both against the installed functions. A restore that replays an erasure with a different rule answers a different question than the erasure it replays.
- Carry the old predicate in the migration as a constant, assert the new one appears exactly once in the generated SQL, and reverse by substitution. A signed erasure record is never rewritten, and a catalog edit cannot ship a function that disagrees with its own source.

The change is in [catalyst-onboarding-v2 PR #179](https://github.com/intent-solutions-io/catalyst-onboarding-v2/pull/179).

## Frequently asked questions

### What is the difference between a reserved provider call and a confirmed one?

A reservation is the record your system writes before it sends the request, so the request may have reached the provider. A confirmed disclosure is the record that requests were consumed. A call that was reserved and then started or abandoned still owes a cleanup, because the provider's side of that call is not something your database can resolve.

### Why not count only confirmed provider calls?

Counting only confirmed calls removes the false positive and shortens the query, but it creates a silent false negative: an interrupted call leaves no confirmed record while the provider may have received it. Asking the provider instead makes the vendor a runtime dependency of an erasure request, and none of those assumptions hold in general. So the obligation is deliberately a superset of confirmed disclosures.

### How do I test that an erasure derives the right cleanup set?

Parametrize the case over both erasure paths and over whether the provider was actually called, so the parameter doubles as the expected answer. Cover the false negative with a reply interpretation that reserved provider work, and the ambiguous middle with a call reserved and then started or abandoned. Assert against the installed functions, so the path under test and the restore path are held to the same rule.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is the difference between a reserved provider call and a confirmed one?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A reservation is the record your system writes before it sends the request, so the request may have reached the provider. A confirmed disclosure is the record that requests were consumed. A call that was reserved and then started or abandoned still owes a cleanup, because the provider's side of that call is not something your database can resolve."
      }
    },
    {
      "@type": "Question",
      "name": "Why not count only confirmed provider calls?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Counting only confirmed calls removes the false positive and shortens the query, but it creates a silent false negative: an interrupted call leaves no confirmed record while the provider may have received it. Asking the provider instead makes the vendor a runtime dependency of an erasure request, and none of those assumptions hold in general. So the obligation is deliberately a superset of confirmed disclosures."
      }
    },
    {
      "@type": "Question",
      "name": "How do I test that an erasure derives the right cleanup set?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Parametrize the case over both erasure paths and over whether the provider was actually called, so the parameter doubles as the expected answer. Cover the false negative with a reply interpretation that reserved provider work, and the ambiguous middle with a call reserved and then started or abandoned. Assert against the installed functions, so the path under test and the restore path are held to the same rule."
      }
    }
  ]
}
</script>

## Related Posts

- [A Database Restore Does Not Undo Sent Email or Envelopes](https://startaitools.com/posts/database-restore-does-not-undo-outward-effects/)
- [A Green Recovery Drill Can Still Be Lying](https://startaitools.com/posts/a-green-recovery-drill-can-still-be-lying/)
- [Every Claim Needs a Shipped Source and an Executable Proof](https://startaitools.com/posts/working-is-not-proven/)
