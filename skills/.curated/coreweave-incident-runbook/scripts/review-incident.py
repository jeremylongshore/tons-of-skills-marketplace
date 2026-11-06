#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

from review_common import run, instant


def analyze(d, r):
    events = d.get("timeline", [])
    r.require(bool(events), "timeline-empty", "Supply an ordered incident timeline.", unknown=True)
    times = [instant(e["at"]) for e in events]
    r.require(times == sorted(times), "timeline-order", "Timeline events must be chronological.")
    r.require(
        bool(d.get("affected_resources")) and bool(d.get("incident_owner")),
        "incident-scope",
        "Identify affected resources and the incident owner.",
    )
    r.require(
        d.get("containment_authorized") is not True or bool(d.get("approval_reference")),
        "containment-authority",
        "Urgency alone does not authorize containment.",
    )
    recovery = d.get("recovery", {})
    if d.get("state") == "resolved":
        r.require(
            recovery.get("acceptance_passed") is True and recovery.get("resource_scope") == d.get("affected_resources"),
            "recovery-proof",
            "Resolved state requires matching resource-scope acceptance evidence.",
        )
        if times and recovery.get("at"):
            r.require(
                instant(recovery["at"]) >= times[-1],
                "recovery-age",
                "Recovery evidence predates the incident timeline.",
            )
        else:
            r.require(False, "recovery-age", "Recovery timestamp missing.", unknown=True)
    else:
        r.require(
            False,
            "incident-unresolved",
            "Incident remains open; report safe next collection and escalation.",
            unknown=True,
        )
    r.require(
        bool(d.get("escalation_route")),
        "escalation-owner",
        "Identify the support/platform escalation route.",
        unknown=True,
    )
    r.observations.update(timeline_events=len(events), recovery_claim=d.get("state") == "resolved")


if __name__ == "__main__":
    raise SystemExit(run(analyze))
