#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run


def analyze(d, r):
    roles = d.get("roles", [])
    bindings = d.get("bindings", [])
    intended = d.get("subject", {})
    index = {}
    for role in roles:
        key = (role["kind"], role.get("metadata", {}).get("namespace", ""), role["metadata"]["name"])
        r.require(key not in index, "duplicate-role", "Ambiguous duplicate role definition.")
        index[key] = role
    matched = 0
    for binding in bindings:
        subjects = binding.get("subjects", [])
        if not any(
            s.get("kind") == intended.get("kind")
            and s.get("name") == intended.get("name")
            and s.get("namespace", "") == intended.get("namespace", "")
            for s in subjects
        ):
            continue
        matched += 1
        namespace = binding.get("metadata", {}).get("namespace", "")
        ref = binding["roleRef"]
        kind = ref["kind"]
        r.require(
            binding.get("kind") == "RoleBinding" and namespace == d["expected_namespace"],
            "binding-scope",
            "Cluster-wide or different-namespace binding requires separate privilege review.",
        )
        role = index.get((kind, namespace if kind == "Role" else "", ref["name"]))
        r.require(role is not None, "missing-role", "Binding references a role absent from the snapshot.", unknown=True)
        if role is None:
            continue
        for rule in role.get("rules", []):
            verbs = set(rule.get("verbs", []))
            resources = set(rule.get("resources", []))
            groups = set(rule.get("apiGroups", []))
            r.require(
                not ("*" in verbs or "*" in resources or "*" in groups),
                "wildcard-access",
                "Wildcard permission requires narrowing.",
            )
            r.require(
                not verbs.intersection({"bind", "escalate", "impersonate"}),
                "privilege-escalation",
                "Binding/escalation/impersonation is a privileged path.",
            )
            r.require(
                not (
                    resources.intersection({"secrets", "serviceaccounts/token"})
                    and verbs.intersection({"get", "list", "watch", "create", "*"})
                ),
                "credential-access",
                "Credential or service-account token access is sensitive.",
            )
            r.require(
                not (
                    resources.intersection({"pods", "pods/exec", "deployments", "daemonsets", "jobs", "cronjobs"})
                    and verbs.intersection({"create", "patch", "update", "*"})
                ),
                "workload-escalation",
                "Workload creation/exec can expose mounted identities and secrets.",
            )
    r.require(
        matched > 0,
        "subject-bindings",
        "No matching subject binding supplied; cannot establish effective permissions.",
        unknown=True,
    )
    r.require(
        d.get("snapshot_complete") is True,
        "snapshot-completeness",
        "Incomplete role/binding inventory cannot establish effective access.",
        unknown=True,
    )
    r.observations["matching_bindings"] = matched


if __name__ == "__main__":
    raise SystemExit(run(analyze))
