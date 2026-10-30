# Local report persistence

Each local audit attempts to file its report in the caller's Intent OS checkout. The
audited project remains read-only. Only the supplied report and its index entry
are written, after the destination's existing disclosure adapter accepts them.
The bundled writer makes no provider or network calls and performs no repairs,
registry changes, brain ingestion or scheduled jobs. The destination-owned adapter
is trusted local policy code; its behavior remains subject to that checkout's review.

## Invocation

The helper requires a POSIX environment with Python 3.10+, Bash and file-locking
support. It uses the existing local policy, not a downloaded service.

Resolve Intent OS from the caller's path, otherwise `~/000-projects/intent-os`.
The checkout must already have `.git`, `000-docs/000-INDEX.md`, and the canonical
`ops/disclosure-policy/{policy.py,adapters/enforce.sh}`. Missing prerequisites
hold the write; do not synthesize a replacement policy.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/persist-report.py" \
  --intent-os "$intent_os" --audited-root "$audited_project" < "$payload_json"
```

Input is UTF-8 JSON on standard input, at most 1 MiB:

```json
{
  "report": "The complete Markdown audit report, including the two exact Part A and Part B headings from Step 4",
  "repairs": [
    {
      "summary": "A separately performed repair, supplied by the caller",
      "evidence": "The review or commit receipt supporting that claim"
    }
  ]
}
```

`repairs` is optional; an omitted or empty list records **report-only**, with no
repairs claimed. A repair needs both a summary and evidence. These remain
caller-reported claims, not independent adjudication by the writer. The report
already records the declared authority and drifted values; unowned facts still
name no winner. Do not add confidential source excerpts merely to improve a log.

Keep report data out of executable shell text. Prefer an existing JSON artifact
or structured stdin. If a tool requires a here-document, use a quoted, newly
generated delimiter that does not appear as a complete line in the payload;
never use command substitution or interpolate report content into Python code.
No intermediate report file in Intent OS is needed before screening.

`--at` accepts an explicit UTC ISO timestamp for deterministic rehearsals; normal
runs use the current UTC time. It does not select arbitrary output paths.

Pass the actual audited directory as `--audited-root`. The writer refuses a
report/index destination inside that tree. Auditing Intent OS itself can therefore
hold persistence; retain the conversation report rather than overriding this guard.

## Disclosure boundary

The helper invokes the destination's canonical C8 adapter for `evidence-ingest`.
It screens both raw caller text and the rendered report body, without redaction.
It requires exact accepted payloads, two passing content-free receipts, matching
content digests and a matching run receipt. A zero exit alone is insufficient:
the policy can reject a document while exiting successfully.

Receipt scratch files live in a private process temporary directory. If its
configured parent lies inside Intent OS or the declared audited tree, the writer
holds before creating scratch files or invoking the adapter.
Only after acceptance does the helper file the report. Errors return a generic
code without echoing rejected text or raw subprocess errors. The saved record
includes content-free policy/body/receipt digests. These prove the local filter
boundary; they do not certify the report's substantive correctness, make facts
canonical, or introduce the deferred hash-chain record substrate.

The filter remains the existing Intent OS policy and retains its limitations.
Keep the repository's normal disclosure gate and human review before committing
records. Do not weaken the filter when it rejects a report.

## Filing and results

The helper follows Intent OS content schema `003`: it scans the full numbered
tree, including cluster folders, and creates the next flat
`NNN-AA-AUDR-consistency-<UTC timestamp>-<input digest>.md` artifact. It appends one
entry to the existing index without rewriting unrelated edits. Report creation
is exclusive; identical input retries are checked across the numbered tree, symlink entries
in that tree and required paths are refused, and a busy
index is held immediately. No old report is replaced or deleted.

Success exits zero with JSON containing `status: saved`, the relative record
path, its SHA-256 and disclosure digests. A held operation exits nonzero with a
content-free code. Report and index writes are not a two-file transaction:
`report-saved-index-incomplete` means the accepted report exists but indexing
failed. Retain that evidence, inspect the destination and repair its index in a
normal reviewed change; do not claim a complete filing or retry blindly.

There is no automatic commit, push, notification or brain promotion. Follow the
destination repository's existing review, disclosure and Git rules.

## Validation

Portable filesystem and adapter-transport tests use stdlib unittest. They do
not substitute a test policy for a real privacy result:

```bash
python3 -m unittest discover -s tests -p test_consistency_report_persistence.py -v
```

For the actual C8 boundary, explicitly point the integration suite at an existing
Intent OS checkout. It copies only the adapter and policy into owned scratch
destinations; it never writes to that checkout. The private policy is not
vendored into this plugin or public tests.

```bash
INTENT_OS_DISCLOSURE_ROOT="$intent_os" \
  python3 -m unittest discover -s tests -p test_consistency_report_persistence.py -v
```

Without that variable the canonical-policy integration cases are explicitly
skipped. Do not report them as passed. The existing clean/seeded-drift fixture
gate remains a separate prerequisite and is unchanged.
