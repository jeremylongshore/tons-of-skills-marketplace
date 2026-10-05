# Repository scanning runtime contract

## Current handlers

- search_issues generates one issue_match object for each of at most five supplied terms. Confidence is
  0.6, so assignEvidenceTier() returns Tier 3.
- inspect_recent_commits returns one recent_commit object with confidence 0.5 and Tier 3.
- inspect_code_paths returns one affected_path object with confidence 0.5 and Tier 3.
- check_recent_deploys returns one recent_deploy object with confidence 0.4 and Tier 3.

The descriptive strings say search, scanned, inspected, or checked, but the handlers only interpolate
inputs into those strings. They perform no fetch, GitHub CLI call, filesystem traversal, or API request.

## Evidence policy boundary

assignEvidenceTier() is real deterministic logic over an evidence type and confidence number. It grades
the shape of supplied/generated records; it does not verify their factual basis.

## Future integration

Live GitHub evidence requires new authenticated handlers plus tests that prove returned URLs, SHAs,
paths, and release identifiers came from the requested repository.
