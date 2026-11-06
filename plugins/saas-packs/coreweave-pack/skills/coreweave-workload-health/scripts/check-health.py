#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run, instant, finite


def analyze(d, r):
    pod = d["pod"]
    meta = pod["metadata"]
    status = pod.get("status", {})
    r.require(
        meta.get("namespace") == d["expected_namespace"] and bool(meta.get("uid")),
        "pod-identity",
        "Pod UID and intended namespace required.",
    )
    scheduled = bool(pod.get("spec", {}).get("nodeName"))
    ready = status.get("phase") == "Running" and any(
        c.get("type") == "Ready" and c.get("status") == "True" for c in status.get("conditions", [])
    )
    r.require(scheduled, "pod-scheduled", "Pod is not assigned to a Node.", unknown=True)
    r.require(ready, "pod-ready", "Pod is not observed Ready and Running.", unknown=True)
    containers = pod.get("spec", {}).get("containers", [])
    counts = [c.get("resources", {}).get("limits", {}).get("nvidia.com/gpu", 0) for c in containers]
    r.require(
        all(type(c) is int and c >= 0 for c in counts),
        "gpu-limits",
        "GPU allocation must be explicit nonnegative integer limits.",
    )
    count = sum(c for c in counts if type(c) is int)
    r.require(count > 0, "gpu-request", "No GPU allocation requested; cannot claim GPU activity.", unknown=True)
    allocations = d.get("gpu_allocations", [])
    uuids = [a.get("uuid") for a in allocations if a.get("pod_uid") == meta.get("uid")]
    r.require(
        len(uuids) == count and len(set(uuids)) == count and all(uuids),
        "gpu-attribution",
        "Unique device-to-Pod attribution must cover all requested GPUs.",
        unknown=True,
    )
    samples = d.get("gpu_samples", [])
    active = 0
    for uuid in uuids:
        matches = [s for s in samples if s.get("uuid") == uuid and s.get("pod_uid") == meta.get("uid")]
        valid = []
        for s in matches:
            age = (instant(d["captured_at"]) - instant(s["at"])).total_seconds()
            v = s.get("utilization_percent")
            if finite(v) and 0 <= v <= 100 and 0 <= age <= 300:
                valid.append(v)
        r.require(
            bool(valid),
            "gpu-sample-missing",
            "Missing/stale/mismatched device sample; activity is unknown.",
            unknown=True,
        )
        if valid and max(valid) > 0:
            active += 1
    r.require(
        active == count and count > 0,
        "gpu-activity",
        "Positive activity on every attributed GPU has not been demonstrated.",
        unknown=True,
    )
    r.observations.update(scheduled=scheduled, ready=ready, requested_gpus=count, gpus_with_activity=active)


if __name__ == "__main__":
    raise SystemExit(run(analyze))
