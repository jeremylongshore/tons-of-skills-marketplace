# HTTP method policy remediation

## Establish expected behavior

Ask the route and proxy owners which principals and methods are intended.
Record expected methods by route and environment. Allow-header advertisement
alone is insufficient to demand removal of a legitimate API or WebDAV feature.
Separate the discovery result, bounded capability evidence and owner-policy
verdict in the change record. Do not claim exploitation or DoD/STIG compliance.

## Make an owned configuration change

For a confirmed policy violation, review the actual reverse proxy, application
routing and authoring configuration with its maintainer. Restrict unneeded
methods at the appropriate layer while preserving required API operations,
CORS preflight and approved proxy destinations. Enforce authentication and
resource authorization for the methods that remain. A blanket GET/POST-only
rule can break legitimate behavior; do not apply one without a route policy.

Use the deployed server version's official configuration documentation and
normal review/deploy/rollback procedure. This skill does not edit server
configuration, deploy WAF rules, restart services or install/remove modules.
Retain the prior configuration and an owner-approved rollback before rollout.

## Reconcile incomplete experiments

1. Keep the private ledger and identify generated fixture URLs from request
   intents and ownership receipts. A lost acknowledgement means state is unknown.
2. Have the resource owner inspect those exact URLs and compare current state
   with synthetic payload hashes/ETags. Do not expand into a directory crawl.
3. Do not automatically delete a changed file or recursively delete a collection
   with unexpected members. Escalate these to the owner for manual reconciliation.
4. Short collection locks may persist after failure. Do not reuse tokens or
   blindly resume the ledger. Let the bounded lease expire or have the owner
   reconcile through their normal administrative process.
5. Preserve the inconclusive result even if later remediation succeeds. Record
   reconciliation separately; do not rewrite a failed run as historical success.

## Verify after remediation

Repeat bounded OPTIONS discovery with the approved exact URL. Compare its
advertisement with policy, then conduct only separately approved active
experiments if capability verification is required. Use a new ledger and new
fixtures. A denied anonymous request does not prove denial for every principal.
Check the relevant legitimate application behavior before accepting the change.

## CI integration

A scheduled OPTIONS-only check can detect advertisement drift. Keep the process
exit code as the gate; do not infer success from an empty severity-filtered
report. Treat exit 2 as missing evidence, not a pass. Active write/proxy
experiments require per-run permission and a disposable environment; never
introduce them into an ordinary deployment check merely by adding --authorized.

The deterministic regression suite uses in-memory peers only and does not
establish live server compatibility or authorize an external test.

## References

- [Evidence semantics and primary standards](THEORY.md)
- [Operator instructions](../SKILL.md)
