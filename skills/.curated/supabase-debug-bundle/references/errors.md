# Collection failure handling

| Observation | Response |
| --- | --- |
| CLI is missing or a command exits nonzero | Keep the nonzero receipt; do not install a replacement or reinterpret captured error output as a successful observation. |
| Temporary directory creation fails | Stop before collection; choose an approved writable location without weakening permissions. |
| Platform status fetch fails | Record unavailable status; do not infer the project's health. |
| Candidate contains SQL values, opaque tokens or personal data | Keep it private and prepare a separately reviewed minimized export. Regex masking is not a clearance. |
| Archive creation fails | Keep private evidence for review, report failure, and do not claim a complete or shareable bundle. |
| File permissions or filesystem ACLs expose the candidate | Stop sharing and correct the approved storage boundary before collecting further evidence. |

See the [main collector](../SKILL.md). Diagnostics do not authorize remediation,
privilege escalation, credential rotation or automatic support upload.
