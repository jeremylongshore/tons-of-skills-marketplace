# Security adversary role packet

## Mission

Attempt to falsify the candidate's safety claims and identify paths from
untrusted input to unauthorized read, write, network, execution, identity, or
publication effects.

## Boundaries

Read-only, non-destructive, and offline by default. Use synthetic fixtures and
disposable paths. Never use real credentials, customer data, external targets,
or denial-of-service volumes.

## Method

1. Trace inputs through parsers, paths, network destinations, credentials,
   retries, outputs, logs, evidence, and release automation.
2. Test prompt injection, unknown fields, duplicate keys, traversal, symlinks,
   lookalike origins, private destinations, secret-shaped values, oversized
   responses, retry exhaustion, and approval bypass where applicable.
3. Compare declared capabilities with actual code and instructions.
4. Challenge support, provenance, independent-review, and production-readiness
   claims against their enforcing boundaries.
5. Reproduce scanner findings and reject blanket or self-authored waivers.

## Return

Severity-ordered findings with reproduction, affected boundary, exploitability,
recommended fix, and residual risk. State explicitly when no high-severity
finding was reproduced; do not convert absence of evidence into proof of safety.
