---
title: "Bind a Sidecar to Its Data Store with a Generation Marker"
description: "A generation marker binds a metadata sidecar to the load that wrote its Oxigraph store. Row counts miss a re-export that keeps its totals."
date: "2026-11-11"
tags: ["architecture", "debugging", "python", "testing", "ai-agents"]
featured: false
canonical: "https://startaitools.com/posts/bind-metadata-sidecar-to-store-generation-marker/"
---
A server that answers queries from a data store often stamps each answer with an id read from a sidecar (a small metadata file published beside the store), so callers know which version of the data they got. If you publish the store and the sidecar with two separate file renames, a server that starts between them pairs the new data with stale metadata, the old id, and every answer it gives names the wrong version. A row count check does not close that gap: an updated store whose totals did not change passes it.

This post covers why counts are the wrong proof, how a generation marker (the version id written inside the store itself) makes a server that starts in that gap refuse instead of serve, and how to run a drill that proves the refusal. The example is a read-only query server over a graph store, written in Python with pyoxigraph (the Python binding for the Oxigraph database). The code reaches the store through the Semantica library's OxigraphStore wrapper, so its calls are that wrapper's, not raw pyoxigraph.

## Why can't a row count prove a sidecar matches its store?

A row count cannot prove a sidecar matches its store. Suppose a re-export edits one decision title and the server starts before the new sidecar lands: no count changes, so the check passes while the server stamps new text with the old snapshot id. A generation marker makes that window fail closed. The loader writes the snapshot id into the store, and the server refuses to start on a mismatch.

## What the MCP server queries: an Oxigraph store and its sidecar

The server is a Model Context Protocol (MCP) server, which lets an AI client call tools over a plain stdio pipe. It exposes six fixed SPARQL query tools. SPARQL is the standard query language for triple stores, and the store here is Oxigraph, a graph database that holds triples (each one a subject, predicate and object statement).

The data is a projection of the estate (every repo, server and service the company runs). When this shipped it held 366 nodes, 413 relationships, 11,732 triples and 81 decision records.

Every answer carries `projection_of`, the snapshot id that says which export the answer came from. The id comes from a sidecar, a small JSON file published beside the store. Its value is `sha256:` followed by the hash of the export bytes. The sidecar also records the node, relationship and triple counts.

That only works if the sidecar really describes the store next to it.

## The race window between the store rename and the sidecar rename

The loader publishes in two steps. It writes the sidecar to a sibling temp file, renames the store into place, and then renames the sidecar into place. The two renames are not one atomic operation.

For a short time, a new store sits beside the previous sidecar. A server started in that window stamps the new graph with the old `projection_of`. That inversion is the exact failure the sidecar exists to prevent, so the window is the bug, not an edge case. The same class of bug, a path that names something that has since changed, is the subject of [A Path Is Not Proof of Identity](https://startaitools.com/posts/a-path-is-not-proof-of-identity/).

## Why a startup row count check misses an equal-count re-export

The first version of the fix, in a follow-up pull request, was a startup count check. The server opened the store read-only, ran three counts, and compared them with the sidecar. Any mismatch exited with code 3.

The case for it was cost. Three counts over about 11.7k triples are cheap, and the check also catches a sidecar whose counts were hand-edited. The alternative was to move the sidecar inside the store's RocksDB directory (Oxigraph's on-disk storage engine), which I rejected because foreign files in a RocksDB directory are undocumented behaviour.

Here is the case it misses, as an illustration. Counts that pass while the data is wrong are the failure in [Passing Is Not Validating](https://startaitools.com/posts/passing-is-not-validating/). Suppose a re-export edits one decision title and changes no count. The totals match the old sidecar, the check passes, and the server serves the new text while `projection_of` names the previous snapshot id.

The MiniMax Adversarial Review (an advisory bot that tries to refute a pull request's own claims) made the same argument with three cases: editing a decision title, swapping a relationship target, and a hand-edit that changes only `snapshot_id`. Each passes a count check. The review asked for a drill that publishes a store with identical counts and a changed id, plus a store-derived digest or an equivalent check.

## A generation marker written into the store

The fix is one triple. The loader writes the snapshot id into the store itself.

```python
store.add_triplets([Triplet(core.SNAPSHOT_SUBJECT, core.SNAPSHOT_PREDICATE, snapshot_id, 1.0,
                            {"datatype": core.XSD_STRING})])
store.flush()
```

The write happens after the count gate, so the gate still compares input to store exactly. The marker is excluded from every count and from the canonical hashes, which means it does not move any number the server checks.

The server reads the marker before it looks at any count:

```python
marker = self.store.execute_sparql(
    f"SELECT ?id WHERE {{ <{core.SNAPSHOT_SUBJECT}> <{core.SNAPSHOT_PREDICATE}> ?id }}")["bindings"]
in_store = marker[0]["id"]["value"] if marker else None
if in_store != self.snapshot.get("snapshot_id"):
    raise RuntimeError(f"snapshot sidecar does not describe this store: sidecar id "
                       f"{self.snapshot.get('snapshot_id')}, store marker {in_store}")
```

The count comparison runs after that and raises on mismatch too. A `RuntimeError` at startup makes the server exit 3 with nothing on stdout. So there are two refusal reasons and one exit code.

The marker check is what refuses when the counts agree, which is the case counts cannot see. The order only decides which message prints when both checks fail.

What the marker proves is narrower than it sounds. The snapshot id is a hash of the export bytes, so a re-export with changed content gets a new id and writes a new marker. The check binds the sidecar to the load that wrote the store. It does not hash the store. If someone edited triples inside the store, left the marker alone and kept every count, this check would pass. The drill does not cover that case.

## A drill that proves the server refuses a mismatched sidecar

Two legs were added to the read-only drill. Each plants a stale sidecar, starts the server, and passes only if the exit code is 3 and stdout is empty.

```bash
echo "-- 7a. stale sidecar: equal counts, different snapshot_id -> exit 3 --"
stale_leg "stale sidecar (equal counts, id differs)" \
  's["snapshot_id"] = "sha256:" + "0" * 64' "$EVIDENCE/stale-sidecar-id.err"
echo "-- 7b. stale sidecar: counts differ -> exit 3 --"
stale_leg "stale sidecar (counts differ)" 's["nodes"] = s["nodes"] + 1' "$EVIDENCE/stale-sidecar-counts.err"
```

Leg 7a is the one that matters. Its sidecar matches every count, and only the id is wrong. A count-only check would serve it. The captured stderr from 7a:

```text
cannot open the store read-only: RuntimeError: snapshot sidecar does not describe this store: sidecar id sha256:0000000000000000000000000000000000000000000000000000000000000000, store marker sha256:5ca94f4f6a77adc7f0ea52cccd4ba4860af530d86a55cc4a9e2883d28c11bcbb
```

Leg 7b exercises the count path. Its sidecar claims 367 nodes, and the store holds 366. Relationships and triples match. The drill's sections are numbered up to 7b, and five of them are pass/fail legs in its result file. All five passed, 7a and 7b included, over the real state directory.

## Why not the obvious approach? Stronger counts, a co-located sidecar, a content digest

The obvious repair is a stronger count. Hypothetically, you could add a fourth count. You would still compare counts, so a stale sidecar whose counts happen to match still passes. The marker does not depend on counts. Any re-export that changes content changes the export bytes, so the snapshot id and the marker change. A hand-edited sidecar id is caught too. The marker does not catch an edit made inside the store after the load, and a stronger count would not either. Hashing store content at startup would, which is the digest option below.

The second obvious repair is to put the sidecar inside the store directory so the two cannot separate. That is the alternative I rejected above, for the undocumented-behaviour reason.

The third is the review's suggestion, a digest of the store contents. A digest binds the sidecar to content rather than to an id. The merged check does not compute one. The marker was chosen because it closed the specific gap the review demonstrated, an equal-count stale sidecar, with one extra triple. I have not measured what a full content digest would cost at startup.

## What it cost

After the first server pull request merged, an automated code reviewer (OpenCodeReview, a different bot from the adversarial one) posted 17 inline comments. Seven were real and went into a follow-up pull request. That follow-up's first push carried the count-only check. The MiniMax Adversarial Review rated the equal-count gap high confidence, and the marker and leg 7a landed in the same follow-up before it merged.

The check also has a deployment cost. It refuses any store that an older loader wrote without a marker. The current state directory was reloaded. Any other state directory needs one loader run before the server will start.

The build ran as a long Claude Code session in the operations repo, with Claude Opus 5.5 doing most of it and Claude Fable 5.1 handling a small share of the session's turns. The count-only first fix came out of that session. A reviewer built to argue against the pull request is what caught it.

## Also shipped

- The installer rewrite stages a launcher, health-checks it, and only then swaps it live, keeping the prior copy in `previous/`. Its first run failed on a parser defect and left the live install untouched.
- A kill drill removed every server container and moved the state directory aside. Eight estate checks answered identically before and after. Two were already red at baseline, so each check was compared with its own baseline rather than required to be green.

## Use this

- Write a generation marker into the store in the same load as the data, after your count gate, and exclude it from every count and hash. It binds the sidecar to the load, not to the store's content.
- At startup, compare the marker to the sidecar's id before comparing any counts (so the more specific message prints), and exit nonzero on either mismatch.
- Add a drill that plants a sidecar with identical counts and a different snapshot id, and assert the server refuses it with empty stdout. For read-only opening in raw pyoxigraph (not through a wrapper), see the Store API docs at https://pyoxigraph.readthedocs.io/.

## Frequently asked questions

### Can row counts prove a sidecar matches its data store?

No. A re-export can edit a decision title or swap a relationship target and leave the node, relationship and triple totals unchanged, so a count check passes it. The fix here writes the snapshot id into the store as a marker and compares it with the sidecar id before any count runs.

### What is a generation marker?

A generation marker is the version id written inside the store itself, in the same load as the data. It is one triple holding the snapshot id, excluded from every count and canonical hash. At startup the server reads it and exits with code 3 if it differs from the sidecar's snapshot_id. The marker binds the sidecar to the load that wrote the store; it does not hash the store contents, so an edit inside the store that keeps the marker and every count would still pass.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Can row counts prove a sidecar matches its data store?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. A re-export can edit a decision title or swap a relationship target and leave the node, relationship and triple totals unchanged, so a count check passes it. The fix here writes the snapshot id into the store as a marker and compares it with the sidecar id before any count runs."
      }
    },
    {
      "@type": "Question",
      "name": "What is a generation marker?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A generation marker is the version id written inside the store itself, in the same load as the data. It is one triple holding the snapshot id, excluded from every count and canonical hash. At startup the server reads it and exits with code 3 if it differs from the sidecar's snapshot_id. The marker binds the sidecar to the load that wrote the store; it does not hash the store contents, so an edit inside the store that keeps the marker and every count would still pass."
      }
    }
  ]
}
</script>

## Related Posts

- [Carrying the installed commit hash into an end-to-end test result makes provenance checkable](https://startaitools.com/posts/the-commit-the-test-actually-installed/)
- [A guard with no reachable red path is not a guard](https://startaitools.com/posts/the-gate-that-could-not-fail/)
- [A green recovery drill can still be lying](https://startaitools.com/posts/a-green-recovery-drill-can-still-be-lying/)
