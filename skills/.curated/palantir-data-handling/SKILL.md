---
name: palantir-data-handling
description: >-
  Design and verify Foundry data handling across projects, roles, mandatory controls, Ontology security, logs, exports, and retention. Use when processing sensitive or regulated data. Trigger with "Foundry data handling" or "Palantir markings".
allowed-tools: Read,Glob,Grep,Write,Edit
version: 2.0.0
argument-hint: "[dataset-object-type-or-workflow]"
model: inherit
effort: high
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
compatibility: Requires current Palantir Foundry documentation and approved access for any live resource, permission, data, build, application, or deployment change
tags: [saas, palantir, foundry, data-governance, security]
---
# Palantir Data Governance and Handling

## Overview

Map the full data path before editing a permission or transform. Foundry discretionary roles, mandatory controls, Ontology row/property policies, and downstream exports protect different boundaries and must be reviewed separately.

## Prerequisites

- Identify data owner, purpose, classifications, source datasets, derived resources, Ontology objects and properties, logs, exports, and retention obligations.
- Record the projects, organizations, markings, CBAC policies, groups, and roles governing each stage.
- Read `references/official-docs.md` and involve the information-security or privacy owner for regulated data.
- Use synthetic data for policy tests unless a protected test environment is approved.

## Current Contract

- Projects and roles provide discretionary access, while organizations, markings, and CBAC remain mandatory and propagate according to their own rules.
- Ontology object and property policies can implement row- and column-level read controls; granular controls do not automatically protect downstream exports.
- Mandatory controls within security policies continue to protect derived data where the documented propagation rules apply.
- Logs and audit exports may contain sensitive or personal data and require explicit access, marking, retention, and audience decisions.

## Instructions

1. Draw the data-flow and authority map from ingestion through transforms, Ontology, applications, logs, and exports.

2. Classify each resource and define the minimum project roles, groups, mandatory controls, and application restrictions.

3. Configure Ontology object/property policies for read-time needs and pair them with mandatory controls when downstream propagation is required.

4. Define retention, deletion, export, and audit evidence procedures with accountable owners.

5. Test authorized, unauthorized, downstream-derived, log-viewing, and export cases before production.

## Tool Discipline

- Use **Glob** to locate candidate repositories, manifests, configurations, and evidence without widening scope.
- Use **Grep** to find relevant identifiers, declarations, permissions, errors, and stale claims.
- Use **Read** to inspect the smallest required files and authoritative evidence.
- Use **Write** only for a new approved local draft, test, manifest, or evidence artifact.
- Use **Edit** only for a bounded approved change whose rollback is known.
- Do not use file tools as a substitute for authenticated Foundry operations or owner approval.

## Approval Boundaries

The data owner approves purpose and access; the security owner approves markings or CBAC; the privacy owner approves retention and deletion; the platform owner approves exports. Do not unmark, broaden roles, or export protected data without those approvals.

## Output

A data-flow map, classification inventory, control matrix, lineage/propagation analysis, retention and deletion procedure, test evidence, exceptions, and owner attestations.

## Error Handling

| Condition | Response |
|---|---|
| A user has a role but still lacks access | Check organizations, markings, CBAC, resource dependencies, and application restrictions rather than broadening the role. |
| A property policy protects reads but not an export | Add an appropriate mandatory control or redesign the export boundary. |
| Logs expose sensitive values | Stop export or viewing, apply the required markings and audience controls, then review retention. |
| Deletion cannot be proven downstream | Block closure and trace every derived dataset, Ontology resource, export, cache, and audit exception. |

## Examples

### Example 1

Protect customer contact fields with Ontology property policies while using mandatory markings for derived datasets and exports that must retain the same access requirement.

### Example 2

Design a deletion request workflow that resolves the subject, identifies every governed resource and lawful exception, executes approved deletion or retention actions, and records non-sensitive evidence.

## Validation

- Authorized and unauthorized personas behave as the policy specifies.
- Lineage demonstrates where mandatory controls propagate and where granular controls stop.
- Logs and exports have explicit markings, audiences, and retention.
- Deletion and retention evidence names every in-scope resource and exception.
- No credential, PII sample, or protected payload appears in the deliverable.

## Resources

- [Official documentation and contract notes](references/official-docs.md)
- Re-check the dated contract before any live operation.
- Treat unresolved or changed vendor behavior as a stop condition.
