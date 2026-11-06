#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run


REVIEWED_PROVIDERS = {
    "coreweave_networking_vpc": ("registry.terraform.io/coreweave/coreweave", "0.26.0"),
    "coreweave_cks_cluster": ("registry.terraform.io/coreweave/coreweave", "0.26.0"),
    "kubernetes_manifest": ("registry.terraform.io/hashicorp/kubernetes", "2.38.0"),
}


def unknown(value):
    if isinstance(value, dict):
        return any(unknown(v) for v in value.values())
    if isinstance(value, list):
        return any(unknown(v) for v in value)
    return value is True


def planned_vpc_reference(plan, change):
    """Resolve only a direct root-module VPC ID reference, never arbitrary unknowns."""
    if change["change"].get("after_unknown", {}).get("vpc_id") is not True:
        return False
    resources = plan.get("configuration", {}).get("root_module", {}).get("resources", [])
    configs = [item for item in resources if item.get("address") == change["address"]]
    if len(configs) != 1:
        return False
    refs = configs[0].get("expressions", {}).get("vpc_id", {}).get("references", [])
    candidates = [
        item
        for item in plan.get("resource_changes", [])
        if item.get("type") == "coreweave_networking_vpc"
        and item.get("mode", "managed") == "managed"
        and item["change"].get("actions") in (["create"], ["no-op"])
        and refs
        and set(refs) <= {item["address"], item["address"] + ".id"}
        and item["address"] + ".id" in refs
    ]
    return len(candidates) == 1


def analyze(d, r):
    plan = d["plan"]
    changes = plan.get("resource_changes", [])
    r.require(
        plan.get("format_version") == "1.2", "plan-format", "Review a supported Terraform JSON plan format (1.2)."
    )
    r.require(bool(changes), "empty-plan", "No resource changes supplied.", unknown=True)
    allowed = {"coreweave_networking_vpc", "coreweave_cks_cluster", "kubernetes_manifest"}
    selections = d.get("provider_selections")
    r.require(
        isinstance(selections, dict) and bool(selections),
        "provider-evidence",
        "Supply provider selections from the same reviewed Terraform working directory.",
    )
    if not isinstance(selections, dict):
        selections = {}
    inventory = []
    for change in changes:
        c = change["change"]
        actions = c["actions"]
        kind = change["type"]
        inventory.append({"address": change["address"], "type": kind, "actions": actions})
        r.require(kind in allowed, "resource-type", "Unexpected resource type requires explicit design review.")
        if kind in REVIEWED_PROVIDERS:
            source, version = REVIEWED_PROVIDERS[kind]
            r.require(
                change.get("provider_name") == source,
                "provider-source",
                "Plan resource provider must match the reviewed provider source.",
            )
            r.require(
                selections.get(source) == version,
                "provider-version",
                "Provider version must match the packaged reviewed pin; missing or other versions require review.",
            )
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
        linked_vpc = kind == "coreweave_cks_cluster" and planned_vpc_reference(plan, change)
        if linked_vpc:
            pending.pop("vpc_id", None)
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
                bool(after.get("vpc_id")) or linked_vpc,
                "cluster-vpc",
                "Require an explicit VPC ID or a direct ID reference to one reviewed root-module VPC.",
            )
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
