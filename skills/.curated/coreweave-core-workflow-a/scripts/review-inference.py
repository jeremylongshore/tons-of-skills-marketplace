#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run


def analyze(d, r):
    m = d["manifest"]
    metadata = m["metadata"]
    spec = m["spec"]
    predictor = spec["predictor"]
    r.require(m.get("kind") == "InferenceService", "kind", "Expected a KServe InferenceService.")
    r.require(
        metadata.get("namespace") == d["expected_namespace"],
        "manifest-scope",
        "Manifest namespace differs from the intended namespace.",
    )
    crds = d.get("crds", [])
    r.require(
        isinstance(crds, list) and any(name == "inferenceservices.serving.kserve.io" for name in crds),
        "kserve-crd",
        "KServe CRD must be present in supplied discovery evidence.",
    )
    r.require(
        bool(d.get("controller_version")),
        "controller-version",
        "Supply the installed KServe controller version.",
        unknown=True,
    )
    minimum, maximum = predictor.get("minReplicas"), predictor.get("maxReplicas")
    r.require(
        type(minimum) is int and type(maximum) is int and 0 <= minimum <= maximum and maximum > 0,
        "replica-budget",
        "Explicit nonnegative minReplicas and positive bounded maxReplicas required.",
    )
    model = predictor.get("model", {})
    gpu = model.get("resources", {}).get("limits", {}).get("nvidia.com/gpu")
    r.require(type(gpu) is int and gpu > 0, "gpu-allocation", "Model requires an explicit positive GPU limit.")
    uri = model.get("storageUri", "")
    r.require(
        isinstance(uri, str) and uri.startswith("s3://") and len(uri.split("/")) > 3,
        "model-location",
        "Identify an exact owner-approved object-storage model prefix.",
    )
    provenance = d.get("model_provenance", {})
    digest = provenance.get("sha256", "")
    r.require(
        provenance.get("license_reviewed") is True
        and isinstance(digest, str)
        and len(digest) == 64
        and all(c in "0123456789abcdef" for c in digest),
        "model-provenance",
        "Model license and artifact digest evidence required.",
    )
    status = m.get("status", {})
    r.require(
        type(metadata.get("generation")) is int and status.get("observedGeneration") == metadata["generation"],
        "observed-generation",
        "Readiness must describe the current manifest generation.",
        unknown=True,
    )
    ready = any(c.get("type") == "Ready" and c.get("status") == "True" for c in status.get("conditions", []))
    r.require(ready, "service-ready", "InferenceService readiness is absent or false.", unknown=True)
    endpoint = d.get("endpoint_result", {})
    r.require(
        endpoint.get("status_code") == 200
        and endpoint.get("accepted") is True
        and bool(d.get("expected_model"))
        and endpoint.get("model") == d["expected_model"],
        "endpoint-acceptance",
        "Require a supplied successful model-specific endpoint acceptance result.",
    )
    r.observations.update(ready=ready, gpu_per_replica=gpu, maximum_replicas=maximum)


if __name__ == "__main__":
    raise SystemExit(run(analyze))
