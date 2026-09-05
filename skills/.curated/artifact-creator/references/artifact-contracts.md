# Artifact contract selector

| Artifact                 | Portable?               | Governing authority                                    | Minimum output                                                  |
| ------------------------ | ----------------------- | ------------------------------------------------------ | --------------------------------------------------------------- |
| Agent Skill              | Yes                     | Agent Skills specification plus explicit local overlay | Named directory with `SKILL.md`                                 |
| MCP server               | Protocol-portable       | MCP specification plus selected SDK                    | Server, declared transports, tool/resource contracts, tests     |
| MCP client configuration | No                      | Target host                                            | Host-native configuration with secret references                |
| Plugin                   | No                      | Target host or marketplace                             | Native manifest and only the components actually present        |
| Subagent                 | No common file contract | Target host                                            | Focused prompt and least-privilege host adapter                 |
| Hook                     | No                      | Target host                                            | Event, matcher, handler, failure behavior, test                 |
| Marketplace catalog      | No                      | Marketplace owner                                      | Catalog entry with source, identity, provenance, and validation |

## Agent Skill floor

Use lowercase kebab-case identity, a precise description containing purpose and
activation conditions, and relative links to local resources. Keep instructions
complete without host adapters. Extra frontmatter is allowed only when the
target overlay defines it.

## MCP floor

Choose a supported transport intentionally. Define closed input schemas, bounded
responses, timeouts, cancellation, and stable error classes. Credentials come
from environment variables or a host secret facility. Never place a live value
in a manifest, example, fixture, log, error, or receipt.

Separate read and mutation methods. A name such as `manage_resource` is too
broad when `get_resource` and `delete_resource` have different risk. Mutations
must expose dry-run, idempotency, or confirmation semantics when the upstream
operation supports them; otherwise keep them recommend-only.

## Host-native floor

Record the host, specification URL, verification date, supported runtime
version, and unsupported capabilities. Model selection must inherit or use an
abstract model class unless a host-specific adapter requires a native value.
