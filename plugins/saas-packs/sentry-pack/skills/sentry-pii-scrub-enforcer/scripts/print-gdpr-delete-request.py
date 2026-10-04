#!/usr/bin/env python3
"""Print a GDPR erasure plan for an end-user id. Do not send it.

There is no auto-delete. Help Center (2026-08-03): DELETE
/api/0/projects/{org}/{project}/users/{id}/ does not exist and does not erase
data. GET on the project users collection is read-only.

This script prints the plan, then calls SentryReadOnlyClient.refuse_write.
It never attaches a real token.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if _LIB.is_dir() and str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))
from sentry_readonly import SentryReadOnlyError, client_from_env  # noqa: E402


def build_plan(org: str, user_id: str, project: str | None, issue_ids: list[str]) -> dict:
    lookup = None
    if project:
        lookup = {
            "method": "GET",
            "url": f"https://sentry.io/api/0/projects/{org}/{project}/users/",
            "authorization": "Bearer <REDACTED>",
            "scope": "project:read",
            "note": "GET only. Lists users observed on events. This is not an erasure.",
        }
    issue_deletes = []
    for issue_id in issue_ids:
        issue_deletes.append(
            {
                "method": "DELETE",
                "url": f"https://sentry.io/api/0/organizations/{org}/issues/{issue_id}/",
                "authorization": "Bearer <REDACTED>",
                "scope": "event:admin",
                "effect": "Deletes the issue and every event in it. Not a single-event scrub.",
                "sent": False,
            }
        )
    return {
        "mode": "print-only",
        "auto_delete": False,
        "applied": False,
        "recommends_not_applies": True,
        "org": org,
        "user_id": user_id,
        "user_id_note": "Identifier the operator named (user.id or user.email). Not verified by a write.",
        "false_endpoint": {
            "method": "DELETE",
            "url": f"https://sentry.io/api/0/projects/{org}/{project or '{project}'}/users/{user_id}/",
            "erases_data": False,
            "citation": "Sentry Help Center, 2026-08-03: no such DELETE; a 404 confirms nothing.",
        },
        "lookup_read_only": lookup,
        "search_hint": f'user.id:"{user_id}" OR user.email:"{user_id}"',
        "issue_deletes_not_sent": issue_deletes,
        "issue_ids_omitted": not issue_ids,
        "not_individually_deletable": ["spans", "transactions", "logs", "profiles", "feedback"],
        "project_delete": "not printed — deleting the project is a human decision, not this script",
        "retention": "Ingested data expires on the plan retention window (30–90 days by type). Not a substitute for erasure you still owe.",
        "writes": "none",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Print GDPR delete plan; do not send")
    parser.add_argument("--org", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--project", default=None)
    parser.add_argument("--issue-id", action="append", default=[])
    parser.add_argument(
        "--send",
        action="store_true",
        help="Always refused. Kept so a caller cannot grow a send path quietly.",
    )
    args = parser.parse_args()
    if not args.user_id.strip():
        raise SystemExit("user id is required; refusing to invent one")
    client = client_from_env()
    plan = build_plan(args.org.strip(), args.user_id.strip(), args.project, args.issue_id)
    # Token must not appear even if the environment has one.
    blob = json.dumps(plan)
    token = client.token or ""
    if token and token in blob:
        raise SystemExit("refusing to print: plan contained the auth token")
    try:
        client.refuse_write("GDPR delete / issue delete / user data delete")
    except SentryReadOnlyError as exc:
        plan["refused_write"] = str(exc)
    json.dump(plan, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if args.send:
        raise SystemExit(3)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
