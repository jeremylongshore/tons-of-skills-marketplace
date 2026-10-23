<!-- doc-class: record -->

# Plane versioned surface review

Tracking: `claude-nzec`; source-watch finding: [GitHub issue 1753](https://github.com/jeremylongshore/tons-of-skills-marketplace/issues/1753).

## Finding

The original plugin did not identify an MCP package or installed version. All 13
captured names are registered in the versioned Node comparison
`@makeplane/plane-mcp-server@0.1.5`, whose npm `gitHead` is
`537d9760efb72c1fca4b5c3259aa0710bf60fefd`. The resemblance establishes a legacy
surface family, not which implementation/version any user has installed.

The watcher correctly compares that unchanged capture with the latest official
Python source. At `dc7cfd9f3c305891909e2372f0cc507291353801` (package 0.3.5), nine
names are absent and four remain declared aliases. This is a documented API-family
transition, not evidence of a deployed outage. The versioned mapping and pinned
primary links are in [the API reference](../plugins/productivity/plane/skills/plane/references/api-surface.md).

## Correction

The skill now identifies server capabilities from actual schemas and host
permissions before selecting read operations. It documents the legacy and Python
families without installing, upgrading or pinning a user's server. The transfer
operation is a mutation in both reviewed implementations and is excluded from
observation recipes. Nested agent files are reference checklists; the manifest
does not register executable agents.

The five observation purposes remain. Historical metrics now require actual dated
snapshots or structured events. Comments cannot prove assignment churn; current
priority cannot establish planned priority; current cycle end dates cannot prove
actual close time; points and logged time have different units. Partial visibility
and missing evidence remain explicit. These are prose instructions, not an MCP
proxy, permission grant, or runtime enforcement claim. The safety register records
that limitation. The historical forge proof is qualified as static evidence.

## Watch disposition

Keep the historical research capture, its SHA-256, and the source-watcher binding
unchanged. Latest official Python is useful as a migration-review signal even
when a user intentionally runs legacy Node. Preserve the finding in issue 1753
with a versioned explanation rather than recapturing a baseline to hide it. A
future change to the comparison policy needs separate review. The issue may stay
open as the acknowledged transition record; this review does not certify an
installed server or require a migration.

## Evidence and limits

A local inert source comparison found all 13 Node registrations, matched 12 Python
read capabilities and identified one excluded transfer mutation. Receipt SHA-256:
`edf5c19646a458d250950760f6c2b17111d6d1fd7b8880e4fbee94d632d74027`.
The complete mapping is reproduced in the linked versioned reference. No upstream
source was imported or executed. No authenticated workspace, provider behavior,
deployment or server configuration was exercised. Static grading and generated
projection checks cannot establish runtime compatibility.

## Manifest prescreen correction

The initial PR prescreen correctly reported the existing executable manifest's
`generated` and `author_type` keys as unrecognized fields. Remove those duplicate
keys from the manifest and retain their existing values in the editable marketplace
catalog, where provenance metadata belongs. The README now identifies that source.
No validator rule, schema, waiver or provenance capture changes for this repair.
