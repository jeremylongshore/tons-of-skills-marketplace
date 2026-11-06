#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run


def analyze(d, r):
    world = d.get("world_size")
    workers = d.get("workers", [])
    r.require(type(world) is int and world > 0, "world-size", "World size must be a positive integer.")
    if type(world) is not int or world <= 0:
        return
    ranks = [w.get("rank") for w in workers]
    r.require(
        all(type(v) is int for v in ranks) and sorted(ranks) == list(range(world)),
        "rank-set",
        "Every rank must be unique and present exactly once.",
    )
    endpoints = {w.get("rendezvous") for w in workers}
    r.require(
        len(endpoints) == 1 and bool(next(iter(endpoints), None)),
        "rendezvous",
        "All workers must use the same nonempty rendezvous.",
    )
    r.require(
        all(type(w.get("gpu_count")) is int and w["gpu_count"] > 0 for w in workers),
        "gpu-allocation",
        "Every worker needs explicit positive GPU allocation evidence.",
    )
    transports = {w.get("transport", "unknown") for w in workers}
    r.require(
        len(transports) == 1 and transports <= {"IB", "Socket"},
        "transport-evidence",
        "Separate unknown/mixed rank transport evidence; bootstrap sockets are not data-path evidence.",
        unknown=True,
    )
    checkpoint = d.get("checkpoint", {})
    r.require(
        checkpoint.get("restore_test_passed") is True
        and checkpoint.get("world_size") == world
        and bool(checkpoint.get("model_revision"))
        and checkpoint.get("model_revision") == d.get("model_revision"),
        "checkpoint-recovery",
        "Checkpoint must have supplied compatible revision/world-size recovery evidence.",
    )
    r.observations.update(
        expected_ranks=world, supplied_ranks=len(ranks), transports=sorted(str(t) for t in transports)
    )


if __name__ == "__main__":
    raise SystemExit(run(analyze))
