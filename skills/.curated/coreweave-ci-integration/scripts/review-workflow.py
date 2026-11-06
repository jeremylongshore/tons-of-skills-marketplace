#!/usr/bin/env python3
"""Original offline review; accepts supplied evidence and never performs platform operations."""

import json
from review_common import run


def analyze(d, r):
    workflow = d["workflow"]
    events = workflow.get("on", {})
    names = {events} if isinstance(events, str) else set(events)
    r.require(
        "pull_request_target" not in names,
        "privileged-pr-event",
        "Do not run contributor code with pull_request_target deployment privileges.",
    )
    jobs = workflow.get("jobs", {})
    r.require(bool(jobs), "jobs", "Workflow must contain jobs.")
    protected = set(d.get("protected_environments", []))
    saw_deploy = False
    for job in jobs.values():
        steps = job.get("steps", [])
        deploy = job.get("environment") is not None or any(
            "kubectl" in s.get("run", "") or "terraform apply" in s.get("run", "") for s in steps
        )
        text = json.dumps(job)
        if "pull_request" in names:
            r.require(
                "secrets." not in text and not deploy,
                "pr-trust-boundary",
                "Use a separate trusted deployment workflow; PR jobs must not receive deployment secrets.",
            )
        perms = job.get("permissions", workflow.get("permissions"))
        r.require(
            isinstance(perms, dict)
            and all(
                v in ("read", "none") or (k == "id-token" and v == "write" and deploy) for k, v in (perms or {}).items()
            ),
            "permissions",
            "Explicit minimum job permissions required; review any write access.",
        )
        for step in steps:
            uses = step.get("uses", "")
            if uses and not uses.startswith("./"):
                ref = uses.rsplit("@", 1)[-1]
                r.require(
                    len(ref) == 40 and all(c in "0123456789abcdef" for c in ref),
                    "action-pin",
                    "Pin third-party actions to full commit SHAs.",
                )
            command = step.get("run", "")
            r.require(
                not any(v in command for v in ("set -x", "printenv", "env |", "echo $", 'echo "$', 'cat "$KUBECONFIG')),
                "secret-output",
                "Do not echo environment or kubeconfig values.",
            )
        if deploy:
            saw_deploy = True
            env = job["environment"]
            env = env if isinstance(env, str) else env.get("name")
            r.require(
                env in protected,
                "environment-review",
                "Supply evidence of required reviewers for the exact deployment environment.",
            )
            r.require(
                d.get("cost_review_bound_to_revision") is True,
                "revision-cost-gate",
                "Protected review must bind the deployed revision to its resource/cost plan.",
            )
            r.require(
                d.get("credential_cleanup_test_passed") is True,
                "credential-cleanup",
                "Supply success and failure cleanup test evidence for temporary credentials.",
            )
    r.observations.update(job_count=len(jobs), deployment_workflow=saw_deploy)


if __name__ == "__main__":
    raise SystemExit(run(analyze))
