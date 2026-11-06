#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run


def unknown(value):
    if isinstance(value, dict):
        return any(unknown(v) for v in value.values())
    if isinstance(value, list):
        return any(unknown(v) for v in value)
    return value is True


def analyze(d, r):
    plan = d["plan"]
    changes = plan.get("resource_changes", [])
    r.require(
        plan.get("format_version") == "1.2", "plan-format", "Review a supported Terraform JSON plan format (1.2)."
    )
    r.require(bool(changes), "empty-plan", "No resource changes supplied.", unknown=True)
    allowed = {"coreweave_networking_vpc", "coreweave_cks_cluster", "kubernetes_manifest"}
    inventory = []
    for change in changes:
        c = change["change"]
        actions = c["actions"]
        kind = change["type"]
        inventory.append({"address": change["address"], "type": kind, "actions": actions})
        r.require(kind in allowed, "resource-type", "Unexpected resource type requires explicit design review.")
        r.require(
            actions in (["create"], ["no-op"]),
            "destructive-change",
            "Updates, replacements and deletes require a separate ownership and rollback review.",
        )
        # Computed IDs are expected on a create; unknown user-controlled configuration is not.
        pending = {
            k: v
            for k, v in c.get("after_unknown", {}).items()
            if k
            not in ("id", "api_server_endpoint", "service_account_oidc_issuer_url", "kube_api_access_status", "object")
        }
        r.require(
            not unknown(pending), "unknown-configuration", "Unresolved desired settings prevent a concrete approval."
        )
        after = c.get("after") or {}
        if kind in ("coreweave_networking_vpc", "coreweave_cks_cluster"):
            r.require(
                bool(after.get("name")) and bool(after.get("zone")),
                "resource-identity",
                "Exact resource name and zone are required.",
            )
        if kind == "coreweave_cks_cluster":
            r.require(
                all(after.get(k) for k in ("version", "pod_cidr_name", "service_cidr_name", "internal_lb_cidr_names")),
                "cluster-configuration",
                "Explicit Kubernetes version and all named network ranges required.",
            )
        if kind == "kubernetes_manifest":
            manifest = after.get("manifest", {})
            spec = manifest.get("spec", {})
            r.require(
                manifest.get("kind") == "NodePool" and manifest.get("apiVersion") == "compute.coreweave.com/v1alpha1",
                "nodepool-kind",
                "Only the reviewed NodePool API is accepted.",
            )
            r.require(
                type(spec.get("targetNodes")) is int and spec["targetNodes"] > 0 and "targetRacks" not in spec,
                "node-count",
                "Explicit positive targetNodes required; rack-based capacity needs a separate design.",
            )
            r.require(
                spec.get("autoscaling") is False and bool(spec.get("instanceType")),
                "node-capacity",
                "Pin instance type and disable unbudgeted autoscaling.",
            )
    for change in changes:
        if change["type"] == "kubernetes_manifest":
            spec = (change["change"].get("after") or {}).get("manifest", {}).get("spec", {})
            r.require(
                spec.get("prefill", {}).get("enabled") is False,
                "prefill-budget",
                "Prefill capacity must be disabled or reviewed under a separate cost plan.",
            )
    r.observations["resource_changes"] = inventory
    r.require(
        d.get("owned_state") is True and d.get("cost_gate_reviewed") is True,
        "plan-ownership-cost",
        "State ownership and exact resource cost review are required; this does not grant apply authority.",
    )


if __name__ == "__main__":
    raise SystemExit(run(analyze))
