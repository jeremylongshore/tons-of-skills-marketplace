#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run, instant, finite


def gpu_count(value):
    """Accept whole units from normalized inputs or plain-decimal Kubernetes JSON."""
    if isinstance(value, str) and 0 < len(value) <= 19 and value.isascii() and value.isdecimal():
        value = int(value)
    return value if type(value) is int and 0 <= value <= 2**63 - 1 else None


def analyze(d, r):
    pod = d["pod"]
    meta = pod["metadata"]
    status = pod.get("status", {})
    r.require(
        meta.get("namespace") == d["expected_namespace"] and isinstance(meta.get("uid"), str) and bool(meta["uid"]),
        "pod-identity",
        "Pod UID and intended namespace required.",
    )
    node = pod.get("spec", {}).get("nodeName")
    scheduled = isinstance(node, str) and bool(node)
    terminating = meta.get("deletionTimestamp") is not None
    ready_condition = any(c.get("type") == "Ready" and c.get("status") == "True" for c in status.get("conditions", []))
    ready = status.get("phase") == "Running" and ready_condition and not terminating
    r.require(
        not terminating,
        "pod-terminating",
        "Deletion is requested; retained readiness/activity cannot establish a continuing ready workload.",
        unknown=True,
    )
    r.require(scheduled, "pod-scheduled", "Pod is not assigned to a Node.", unknown=True)
    r.require(ready, "pod-ready", "Pod is not observed Ready and Running.", unknown=True)
    containers = pod.get("spec", {}).get("containers", [])
    counts = [gpu_count(c.get("resources", {}).get("limits", {}).get("nvidia.com/gpu", 0)) for c in containers]
    r.require(
        all(c is not None for c in counts),
        "gpu-limits",
        "GPU limits must be nonnegative whole units as integers or plain decimal strings; normalize other forms first.",
    )
    count = sum(counts) if all(c is not None for c in counts) else None
    r.require(
        count is not None and count > 0,
        "gpu-request",
        "No valid positive GPU count supplied; cannot claim GPU activity.",
        unknown=True,
    )
    allocations = d.get("gpu_allocations", [])
    uuids = [a.get("uuid") for a in allocations if a.get("pod_uid") == meta.get("uid")]
    allocation_complete = (
        count is not None
        and count > 0
        and len(uuids) == count
        and len(set(uuids)) == count
        and all(isinstance(u, str) and bool(u) for u in uuids)
    )
    r.require(
        allocation_complete,
        "gpu-attribution",
        "Unique device-to-Pod attribution must cover all requested GPUs.",
        unknown=True,
    )
    samples = d.get("gpu_samples", [])
    active = 0
    devices = []
    for uuid in uuids:
        matches = [s for s in samples if s.get("uuid") == uuid and s.get("pod_uid") == meta.get("uid")]
        valid = []
        ages = []
        for s in matches:
            sampled_at = instant(s["at"])
            age = (r.evaluation_time - sampled_at).total_seconds()
            captured_age = (instant(d["captured_at"]) - sampled_at).total_seconds()
            ages.append(age)
            v = s.get("utilization_percent")
            if finite(v) and 0 <= v <= 100 and 0 <= age <= 300 and captured_age >= 0:
                valid.append(v)
        r.require(
            bool(valid),
            "gpu-sample-missing",
            "Missing/stale/mismatched device sample; activity is unknown.",
            unknown=True,
        )
        activity = bool(valid) and max(valid) > 0
        if activity:
            active += 1
        devices.append(
            {"uuid": uuid, "sample_ages_seconds": ages, "valid_samples": len(valid), "activity_observed": activity}
        )
    r.require(
        active == count and count > 0,
        "gpu-activity",
        "Positive activity on every attributed GPU has not been demonstrated.",
        unknown=True,
    )
    r.observations.update(
        pod_uid=meta.get("uid"),
        node_name=node,
        captured_at=d["captured_at"],
        capture_age_seconds=(r.evaluation_time - instant(d["captured_at"])).total_seconds(),
        scheduled=scheduled,
        ready_condition=ready_condition,
        ready=ready,
        terminating=terminating,
        requested_gpus=count,
        attributed_gpus=len(uuids),
        allocation_complete=allocation_complete,
        gpus_with_activity=active,
        devices=devices,
    )


if __name__ == "__main__":
    raise SystemExit(run(analyze))
