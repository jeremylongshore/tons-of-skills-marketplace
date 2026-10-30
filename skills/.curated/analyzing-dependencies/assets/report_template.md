# Dependency Check Report

## Scope and evidence

- Project/root and source revision: [record exact selected target]
- Timestamp: [UTC observation time]
- Mode: [live scan / supplied report / installed license inventory]
- Inputs and hashes: [manifest/lock/report paths and hashes, or unavailable]
- Commands, tool versions and advisory database age: [observed values; unavailable where not captured]
- Process status and retained JSON: [exit code and private evidence location]
- Coverage: [complete / incomplete / unsupported; specify selected roots]

## Outcome

[State findings, review-required or incomplete. A clean selected scope is not a
whole-project security claim. Include partial findings despite tool failures.]

| Count                    | Observed value  |
| ------------------------ | --------------- |
| Unfiltered findings      | [count]         |
| Displayed findings       | [count]         |
| Hidden by display filter | [count]         |
| Unknown severity         | [count]         |
| Failed/unassessed routes | [names/reasons] |

## Findings

| Package          | Observed version/range    | Advisory identifier        | Severity                     | Fix evidence                     |
| ---------------- | ------------------------- | -------------------------- | ---------------------------- | -------------------------------- |
| [actual package] | [native value or unknown] | [actual ID or unavailable] | [native severity or UNKNOWN] | [verified source or unavailable] |

Do not fill identifiers, CVSS scores, patched releases or transitive paths from
assumptions. Outdated-version analysis requires separately retained evidence.

## License metadata review

Scope: [installed npm tree / explicitly selected Python environment / not assessed].

| Package          | Exact declared metadata  | Automated category    | Review needed                                     |
| ---------------- | ------------------------ | --------------------- | ------------------------------------------------- |
| [actual package] | [declaration or unknown] | [category or unknown] | [unresolved expression or contextual obligations] |

This inventory does not establish legal compatibility. Preserve unknown IDs,
LicenseRef declarations and compound expressions for contextual review.

## Errors, unknowns and next actions

[Record missing tools/locks, skipped private packages, unavailable advisory
sources, stale database evidence and unsupported ecosystems. Do not coerce
unknowns to zero.]

[Propose evidence-backed remediation and a verification plan. Installation,
upgrades, lock changes, fixes and live requests require their own authorized
execution scope. No security or DoD/STIG certification is asserted.]
