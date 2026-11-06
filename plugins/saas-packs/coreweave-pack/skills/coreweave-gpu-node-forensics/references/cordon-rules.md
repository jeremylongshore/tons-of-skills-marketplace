# Managed cordon ownership

Never manually uncordon a controller-owned health cordon. Identify the actual owner rather than assuming every cordon has the same source. Current CKS lifecycle documentation describes state/pending-state labels, pending conditions and the `node.coreweave.cloud/cordonReason` annotation; record them when authorized. Do not claim these fields are universally unpublished.

A lifecycle transition may lead to reboot or other remediation, not necessarily replacement. Coordinate workload/checkpoint handling and follow the owner-approved path. This offline tool never performs it.

Source checked 2026-11-05: [CKS lifecycle transitions](https://docs.coreweave.com/platform/fleet-management/node-lifecycle/state-transitions).
