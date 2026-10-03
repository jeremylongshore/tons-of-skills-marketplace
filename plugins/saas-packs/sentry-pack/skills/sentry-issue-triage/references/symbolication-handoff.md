# OP01 — minified frames (handoff)

When frames are minified (`app.min.js`, column-only locations, titles like `a is not a function`) grouping is unstable because stack-trace grouping uses in-app frames and minified frames move every build.

This skill says that, then stops.

**Owner of the matcher:** `sentry-event-forensics` agent `sourcemap-debugger`.

Do not interpret `debug_meta.images[].debug_id` or `data.resolved_with` here. Do not claim that uploading maps rewrites events already stored. Merging already-split issues is a manual, imprecise lever the operator performs. This skill does not call merge.

Release-medic owns the upload pipeline. Triage does not grow a second upload procedure.
