---
title: "A Sidecar Fault Should Not Block the Main Deliverable"
description: "A library or archive sidecar is best-effort, not a gate. Ship the deliverable, then file the sidecar. If filing fails, warn, never fail the deliverable."
date: "2026-10-05"
tags: ["release-engineering", "devops", "architecture", "claude-code"]
featured: false
canonical: "https://startaitools.com/posts/the-sidecar-must-never-block-the-deliverable/"
---
If you are adding an audit, library, cache, or log sidecar to a working CLI tool, this post is the design rule to install before you ship. A PDF (or a build, a report, an artifact) is the deliverable. A versioned local archive of those PDFs is a sidecar. whiteglove-pdf writes a receipt (a machine-written record proving a step really ran) alongside every PDF. The trap is bolting the sidecar onto the same code path that writes the main output, which silently turns the sidecar into a gate. A permission error on the sidecar's root, or a stray file left behind by an interrupted run, can then make the main job fail. The fix is structural: ship the deliverable first, file the sidecar in a separate phase whose failure becomes a warning rather than a non-zero exit, and regression-test the off-switch so 'no sidecar' is a real state, not a stuck-on footgun. The post walks through a specific case where that rule came out of a code review, the file paths the rule changed, the regressions that now guard the off-switch, and the three-bullet checklist a reader can apply to their own tool.

This post is about a specific case. whiteglove-pdf is a CLI tool (command-line tool) that renders a markdown or HTML source to PDF and audits the rendered output against a mechanical QA (quality-assurance) checklist. The 1.1.0 release added a local library that files every deliverable under a versioned folder. The first wiring put the library on the main path. An independent code review, run from intent-os (the company's internal operations and documentation repo), found the design problem. The fix reorganized the rule: ship the deliverable, then file the sidecar, and if filing reports failure, warn rather than fail.

The rule that came out of it is the subject of this post. A sidecar (library, archive, cache, log) must never be allowed to fail the main deliverable. Ship the main output first. File the sidecar with a warning rather than an error if filing fails. Regression-test the off-switch so "no sidecar" is a real state, not a stuck-on footgun.

## The library path ran on the main flow, so a sidecar fault blocked the PDF

The library was added under `whiteglove/library.py`. The filing function ran on the same render pipeline as the PDF write, and it called `ensure_root(root)` before any later step could continue. If `ensure_root` raised, the render pipeline aborted with a non-zero exit. The user got an empty path: the PDF was never written and the receipt was never written, so the failure was indistinguishable from a clean run that produced no file at all. This is the same failure class the [three-classes-of-self-healing post](https://startaitools.com/posts/three-classes-of-self-healing-and-slow-is-not-failed/) names as the slow-is-not-failed family: a crash-orphan and a permissions flip from a sync client are exactly the read-only-root cases the whiteglove v1.1.0 library gate now covers. The pre-fix code looked like this:

```python
# library.py:191 (the original, pre-fix wiring)
def file_render(pdf_path, source, receipt, root):
    ensure_root(root)                                  # PermissionError here aborts everything
    doc_dir = allocate_doc_dir(root, source)
    write_versioned(doc_dir, pdf_path, source)
    update_manifest(doc_dir)
    return doc_dir
```

Two failure paths lived inside that single call. First, an unwritable root raised an uncaught `PermissionError`, and the render pipeline aborted with a non-zero exit. The user got the same error message whether the PDF was already on disk or not. Second, a stray `vNNN.md` left behind by a crashed run made every later render of that document refuse: the version allocator saw a directory that was not in the manifest and refused to proceed, again with a non-zero exit.

Both failures share the same root cause: the sidecar raised into the main flow, and there was no user-visible distinction between "deliverable written, sidecar failed" and "deliverable never written."

## Why not the obvious approach

The obvious approach to adding a sidecar is to put it on the main flow. The sidecar pattern is the discipline that says the sidecar sits beside the main path, not on it; bolting it onto the same function call as the deliverable is the common shortcut. The deliverable and the sidecar are written in the same order, and if the sidecar throws, the caller gets a non-zero exit code. That feels safer: it documents what was written, surfaces every issue, and produces a clear error log. The same instinct drove the original wiring.

The instinct is wrong when the sidecar can fail in ways the user cannot fix. A read-only filesystem, a cloud drive without hard-link support, an interrupted run that produced an orphan, or a permissions flip from a sync client: any one of these makes the sidecar unusable in a way that has nothing to do with whether the deliverable was rendered correctly. When the sidecar becomes a gate, the user gets neither a PDF nor a catalog. The catalog is the sidecar. The PDF is the deliverable. The PDF wins.

## The fix: deliver first, file best-effort

The fix in v1.1.0 moved the library off the main path. The render now produces the PDF and the receipt first, writes them to the user's destination, then runs the library file step as a separate phase whose failure is captured and surfaced as a warning:

```python
# render.py (post-fix): two phases, one receipt
def render(source, out_path, library_root, library_mode):
    pdf, receipt = render_pdf(source, out_path)         # always runs
    write_pdf(out_path, pdf)                           # always writes
    write_receipt(out_path, receipt)                    # always writes

    if library_mode == "strict":
        file_path_to_library_strict(library_root, pdf, receipt)
    elif library_mode == "on":
        result = file_library(library_root, pdf, receipt)
        if not result.ok:
            receipt["library"] = {"status": "warning", **result.dict()}
            stderr.write(f"library warning: {result.file_path}\n")
            rewrite_receipt(out_path, receipt)
    return 0                                            # exit code unchanged on warning
```

The two phases are explicit. The deliverable phase returns the PDF and the receipt. The library phase files them. If the library phase returns a `Result` with `ok=False`, the warning is written to the receipt under `"status": "warning"`, the user gets a one-line note on stderr, and the exit code is unchanged.

The strict mode is the inverse, for callers who want the library to be a gate. `whiteglove render --library=strict` writes the PDF and the receipt first, then runs the strict filing; if the filing fails, the run exits non-zero. That mode exists because some callers do want the sidecar to be a precondition (for example, a publishing pipeline that audits the manifest against the next day's run). The default mode does not require it.

## Why the off-switch is regression-tested

A sidecar feature without a tested off-switch is a footgun. The first time a user disables it, the test must catch whether the disabling actually disabled it. The v1.1.0 release landed with three regression tests on the off-switch:

```bash
# off-switch regressions (all must pass on every release)
render --no-library ...                               # no library I/O at all
render --library off ...                              # same as --no-library
render --config library.enabled=false ...             # same as --no-library
```

The three off-switch paths produce the same module-level fingerprint: zero library calls. The tests run with strace'd I/O and assert no `mkdir` and no `open` against `~/Documents/Whiteglove`. A regression here means the off-switch is decorative. The user's `library.enabled: false` would silently produce a library folder. That would be the same bug: the user opted out, the tool ignored them, the sidecar won.

The fix lands the library under three observable signals: a one-time NOTE on first use, a `library.status` block in the receipt, and a `--library` flag in the CLI. The user knows the feature is on. The user knows how to turn it off.

## Independent code review caught the sidecar-as-gate design flaw

The 1.1.0 PR was built by an agent, reported green on the head commit, and merged after the CI checks passed. The intent-os wrapper, steered by Claude Opus 5.5, ran a fresh review on the head commit through a general-purpose subagent acting as code-reviewer. That [review](https://startaitools.com/posts/when-green-ci-proves-nothing/) returned the design rule in plain words: a library fault could block delivery of the main PDF, and the fix is to ship the PDF first, file the library, warn rather than fail.

The fixes went back. The PR was remerged at a head commit locked by `safe-merge`. The library gate landed 57 tests covering the failure paths: read-only root, unusable root, colliding doc_id, crash-orphan, missing manifest entry. The coverage report on the new tests says the user gets a PDF and a warning, not a `PermissionError` and a missing file.

The collaboration beat is a clean review, fix, ship arc. The reviewer caught a real design flaw. The flaw was that the sidecar was on the main path. The fix was to take it off.

## Three sidecar rules to apply to your own tool

Three rules a reader can act on tomorrow, in the same order the design rule applies (apply this to your own [rehearse-before-production](https://startaitools.com/posts/rehearse-before-production-catches-what-tests-cant/) drill so the off-switch gets tested before a real user finds out it is decorative):

- The deliverable ships first. The sidecar (library, cache, log, archive) files after, in its own phase, and a failure there is a warning rather than a non-zero exit. The user gets the main output even if the sidecar reports failure.
- The strict mode is for callers, not users. A sidecar that is opt-out by design cannot also be a precondition. If a caller wants the sidecar to be a gate, give them a flag (for example `--library=strict`) and keep the default loose.
- The off-switch is regression-tested. Three paths (private, `--library off`, config flag) all run the same code path and all produce the same fingerprint: no library I/O at all. A regression here is the same bug, with one difference: the user opted out and the tool ignored them.

## FAQ

### How do I add a sidecar (library, archive, cache, log) to a CLI tool without breaking the main output?

Ship the deliverable first, then file the sidecar in its own separate phase. If the sidecar reports failure (a returned status, not an exception), capture it, write a warning onto the receipt, and surface one line on stderr; the exit code stays zero. The user gets the main output even when the sidecar fails, and the three off-switch paths (private flag, `--library off`, config flag) all run the same code path that produces zero library I/O.

### Why does my build or PDF tool fail when the sidecar (library, cache) fails?

Because the sidecar sat on the same function call as the deliverable write. A permission error on the sidecar's root, or a stray versioned directory left by an interrupted run, could raise an uncaught exception that aborted the function before the PDF was written to the user's destination. When the sidecar becomes a gate, the user gets neither the deliverable nor the catalog.

### What is the difference between best-effort and strict mode for a sidecar?

Best-effort (the default) ships the deliverable first and files the sidecar after; a sidecar failure becomes a warning on the receipt and a one-line note on stderr, and the exit code is unchanged. Strict mode (`--library=strict`) writes the deliverable first and then runs strict filing; if the filing fails, the run exits non-zero even though the deliverable is on disk. Strict is for callers who want the sidecar to be a precondition, not for end users.

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"How do I add a sidecar (library, archive, cache, log) to a CLI tool without breaking the main output?","acceptedAnswer":{"@type":"Answer","text":"Ship the deliverable first, then file the sidecar in its own separate phase. If the sidecar reports failure (a returned status, not an exception), capture it, write a warning onto the receipt, and surface one line on stderr; the exit code stays zero. The user gets the main output even when the sidecar fails, and the three off-switch paths (private flag, --library off, config flag) all run the same code path that produces zero library I/O."}},{"@type":"Question","name":"Why does my build or PDF tool fail when the sidecar (library, cache) fails?","acceptedAnswer":{"@type":"Answer","text":"Because the sidecar sat on the same render pipeline as the deliverable write. A permission error on the sidecar's root, or a stray versioned directory left by an interrupted run, could raise an uncaught exception that aborted the function before the PDF was written to the user's destination. When the sidecar becomes a gate, the user gets neither the deliverable nor the catalog."}},{"@type":"Question","name":"What is the difference between best-effort and strict mode for a sidecar?","acceptedAnswer":{"@type":"Answer","text":"Best-effort (the default) ships the deliverable first and files the sidecar after; a sidecar failure becomes a warning on the receipt and a one-line note on stderr, and the exit code is unchanged. Strict mode (--library=strict) writes the deliverable first and then runs strict filing; if the filing fails, the run exits non-zero even though the deliverable is on disk. Strict is for callers who want the sidecar to be a precondition, not for end users."}}]}
</script>

## Also shipped

- `catalyst-onboarding` shipped an applicant file CRM (customer-relationship-management) with a Tier-1 GitHub lookup and a Tier-2 web search behind an off flag.
- `comehomealabama` shipped one non-technical journal post.

## Related Posts

- [Exit Zero Is Not Push OK](https://startaitools.com/posts/exit-zero-is-not-push-ok/) (a cron that reports OK on a wedged tree)
- [When Green CI Proves Nothing](https://startaitools.com/posts/when-green-ci-proves-nothing/) (green checks can outlive the thing they check)
