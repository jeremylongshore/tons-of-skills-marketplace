#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run


def analyze(d, r):
    from pathlib import PurePosixPath

    # This adapter supports exactly the documented public TLS endpoint.
    # No generic URL parser or network-capable module is required.
    endpoint = d.get("endpoint", "")
    r.require(
        endpoint in ("https://cwobject.com", "https://cwobject.com/"),
        "storage-endpoint",
        "Use the documented TLS cwobject.com endpoint without URL credentials.",
    )
    prefix = d.get("prefix", "")
    r.require(
        isinstance(prefix, str)
        and bool(prefix.strip("/"))
        and ".." not in PurePosixPath(prefix).parts
        and not prefix.startswith("/"),
        "prefix-scope",
        "Exact non-root owned model prefix required.",
    )
    r.require(
        d.get("prefix_owned") is True and d.get("license_reviewed") is True,
        "artifact-authority",
        "Destination ownership and model license/provenance review required.",
    )
    r.require(d.get("public_access") is False, "public-access", "Do not enable public access for model staging.")
    objects = d.get("objects", [])
    seen = set()
    total = 0
    r.require(bool(objects), "object-manifest", "Supply exact object keys, sizes and content digests.")
    for obj in objects:
        key = obj.get("key", "")
        r.require(
            isinstance(key, str)
            and key.startswith(prefix.rstrip("/") + "/")
            and ".." not in PurePosixPath(key).parts
            and key not in seen,
            "object-scope",
            "Object key escapes the prefix or is duplicated.",
        )
        seen.add(key)
        size = obj.get("size_bytes")
        r.require(type(size) is int and size >= 0, "object-size", "Explicit nonnegative object size required.")
        if type(size) is int:
            total += size
        digest = obj.get("sha256", "")
        r.require(
            len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
            "artifact-digest",
            "Supply a source SHA-256; ETag is not a portable content checksum.",
        )
        r.require(
            obj.get("uploaded_size_bytes") == size
            and obj.get("downloaded_sha256") == digest
            and obj.get("upload_complete") is True,
            "transfer-integrity",
            "A completed upload and read-back size/content digest must match; missing evidence is incomplete.",
            unknown=True,
        )
    r.require(
        d.get("cost_gate_reviewed") is True,
        "storage-cost",
        "Review storage, transfer and retention charges before upload.",
    )
    r.observations.update(object_count=len(objects), total_bytes=total)


if __name__ == "__main__":
    raise SystemExit(run(analyze))
