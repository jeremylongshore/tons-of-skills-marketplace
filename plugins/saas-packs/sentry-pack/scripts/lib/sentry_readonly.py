"""Shared read-only Sentry client stub for sentry-pack v2 scripts.

One module for stats, event JSON, and project settings. No MCP server.
No write tools. Pasted JSON when no token is present.

Used by the five parents' scripts. Revisit MCP only when this function
list is boring enough to wrap (Absorb / pressure-test change 6).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


class SentryReadOnlyError(RuntimeError):
    """Raised on config / parse problems — never on "should write"."""


class SentryReadOnlyClient:
    """Read-only access via sentry-cli / documented REST, or advisory paste."""

    def __init__(self, token: str | None = None, org: str | None = None) -> None:
        self.token = token or os.environ.get("SENTRY_AUTH_TOKEN")
        self.org = org or os.environ.get("SENTRY_ORG")
        self.advisory = not bool(self.token)

    def fetch_org_stats_usage(self, *, pasted: str | None = None) -> dict[str, Any]:
        """GET /api/0/organizations/{org}/stats/usage/ — or parse pasted JSON."""
        if pasted is not None:
            return self._parse_json(pasted, what="org stats usage")
        if self.advisory:
            raise SentryReadOnlyError("No SENTRY_AUTH_TOKEN; pass pasted stats JSON for advisory mode")
        # Live read-only fetch (sentry-cli or REST GET) is a planned follow-up. Never POST/PUT/DELETE.
        raise SentryReadOnlyError("Live read-only stats fetch is not implemented yet; pass pasted JSON (advisory mode)")

    def fetch_event_json(self, event_id: str, *, pasted: str | None = None) -> dict[str, Any]:
        if pasted is not None:
            return self._parse_json(pasted, what="event")
        if self.advisory:
            raise SentryReadOnlyError("No SENTRY_AUTH_TOKEN; pass pasted event JSON for advisory mode")
        raise SentryReadOnlyError("Live read-only event fetch is not implemented yet; pass pasted JSON (advisory mode)")

    def fetch_project_settings(self, project: str, *, pasted: str | None = None) -> dict[str, Any]:
        if pasted is not None:
            return self._parse_json(pasted, what="project settings")
        if self.advisory:
            raise SentryReadOnlyError("No SENTRY_AUTH_TOKEN; pass pasted settings JSON for advisory mode")
        raise SentryReadOnlyError(
            "Live read-only settings fetch is not implemented yet; pass pasted JSON (advisory mode)"
        )

    @staticmethod
    def _parse_json(raw: str, *, what: str) -> dict[str, Any]:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SentryReadOnlyError(f"invalid {what} JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise SentryReadOnlyError(f"{what} JSON must be an object")
        return data

    def refuse_write(self, action: str) -> None:
        """Explicit guard — skills recommend; they do not click."""
        raise SentryReadOnlyError(
            f"read-only client refuses write action: {action}. Print the request for the operator; do not send."
        )


def client_from_env() -> SentryReadOnlyClient:
    return SentryReadOnlyClient()


def _repo_scripts_lib_on_path() -> None:
    """Allow `from sentry_readonly import ...` when scripts run from skill dirs."""
    here = Path(__file__).resolve().parent
    # pack/scripts/lib
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))


if __name__ == "__main__":
    c = client_from_env()
    print(json.dumps({"advisory": c.advisory, "org": c.org or None}))
