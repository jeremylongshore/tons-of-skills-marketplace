#!/usr/bin/env python3
"""Bind the existing sync advisory role to trusted Actions producer evidence.

Standalone stdlib only: the consumer is executed from an immutable target-base
Git blob, never from the PR checkout. Proof failures select full scanner grading;
this does not approve a CHALLENGE or change REFUSE semantics.
"""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import signal
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

REPOSITORY = "jeremylongshore/tons-of-skills-marketplace"
REPOSITORY_ID = 1073337396
WORKFLOW_ID = 220341118
WORKFLOW_PATH = ".github/workflows/sync-external.yml"
CREATORS = {213859472: "User", 41898282: "Bot"}
BRANCH = re.compile(r"automation/sync-external-([1-9][0-9]*)\Z")
SHA = re.compile(r"[0-9a-f]{40}\Z")
FIELDS = {
    "format_version",
    "repository_id",
    "workflow_id",
    "workflow_path",
    "workflow_head_sha",
    "run_id",
    "run_attempt",
    "event_name",
    "event_action",
    "pr_number",
    "pr_author_id",
    "pr_author_type",
    "head_repository_id",
    "head_ref",
    "head_sha",
}
REASONS = {
    "eligible",
    "not-sync-branch",
    "invalid-input",
    "identity-mismatch",
    "untrusted-run",
    "untrusted-source",
    "producer-incomplete",
    "missing-proof",
    "invalid-proof",
    "proof-mismatch",
    "artifact-digest",
    "artifact-size",
    "artifact-archive",
    "api-error",
    "proof-timeout",
    "internal-error",
}


class ProofFailure(Exception):
    def __init__(self, reason):
        if reason not in REASONS:
            reason = "internal-error"
        super().__init__(reason)
        self.reason = reason


def require(condition, reason="invalid-proof"):
    if not condition:
        raise ProofFailure(reason)


def positive(value):
    return type(value) is int and 0 < value <= 9007199254740991


def strict_json(data, limit):
    require(len(data) <= limit, "artifact-size")

    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result)
            result[key] = value
        return result

    def constant(value):
        raise ProofFailure("invalid-proof")

    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError):
        raise ProofFailure("invalid-proof") from None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHub:
    """Bounded GitHub-only API reads; never expose errors or signed URLs."""

    def __init__(self, token):
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect)

    def read(self, url, limit, authenticated=False, redirect=False):
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "sync-pr-provenance"}
        if authenticated:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        try:
            response = self.opener.open(request, timeout=10)
        except urllib.error.HTTPError as error:
            if redirect and error.code in (301, 302, 303, 307, 308):
                location = error.headers.get("Location", "")
                parsed = urllib.parse.urlsplit(location)
                host = parsed.hostname or ""
                require(
                    parsed.scheme == "https"
                    and not parsed.username
                    and not parsed.password
                    and parsed.port in (None, 443)
                    and any(
                        host.endswith(suffix)
                        for suffix in (
                            ".blob.core.windows.net",
                            ".githubusercontent.com",
                            ".actions.githubusercontent.com",
                        )
                    ),
                    "api-error",
                )
                # Signed archive URLs are never logged and never receive the API token.
                return self.read(location, limit, authenticated=False)
            raise ProofFailure("api-error") from None
        except (OSError, ValueError):
            raise ProofFailure("api-error") from None
        with response:
            length = response.headers.get("Content-Length")
            if length is not None:
                require(length.isdigit() and int(length) <= limit, "artifact-size")
            chunks = []
            total = 0
            while True:
                # read1 returns available data; the overall SIGALRM also bounds trickles.
                chunk = response.read1(min(4096, limit + 1 - total))
                if not chunk:
                    return b"".join(chunks)
                total += len(chunk)
                require(total <= limit, "artifact-size")
                chunks.append(chunk)

    def api(self, suffix):
        return strict_json(
            self.read(f"https://api.github.com/repos/{REPOSITORY}/{suffix}", 1024 * 1024, authenticated=True),
            1024 * 1024,
        )

    def archive(self, artifact_id):
        require(positive(artifact_id))
        return self.read(
            f"https://api.github.com/repos/{REPOSITORY}/actions/artifacts/{artifact_id}/zip",
            65536,
            authenticated=True,
            redirect=True,
        )


def parse_archive(data, digest):
    require(len(data) <= 65536, "artifact-size")
    require(
        isinstance(digest, str)
        and re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
        and digest == "sha256:" + hashlib.sha256(data).hexdigest(),
        "artifact-digest",
    )
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            require(len(members) == 1, "artifact-archive")
            member = members[0]
            mode = member.external_attr >> 16
            require(
                member.filename == "sync-pr-provenance.json"
                and not member.is_dir()
                and not member.flag_bits & 1
                and member.extract_version <= 20
                and member.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                and (stat.S_IFMT(mode) in (0, stat.S_IFREG)),
                "artifact-archive",
            )
            require(member.file_size <= 16384 and member.compress_size <= 65536, "artifact-size")
            with archive.open(member) as stream:
                payload = stream.read(16385)
                require(len(payload) <= 16384, "artifact-size")
            return validate_receipt(strict_json(payload, 16384))
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError, ValueError):
        raise ProofFailure("artifact-archive") from None


def validate_receipt(receipt):
    require(type(receipt) is dict and set(receipt) == FIELDS)
    for field in (
        "repository_id",
        "workflow_id",
        "run_id",
        "run_attempt",
        "pr_number",
        "pr_author_id",
        "head_repository_id",
        "format_version",
    ):
        require(positive(receipt[field]))
    require(
        receipt["format_version"] == 1
        and receipt["repository_id"] == REPOSITORY_ID
        and receipt["head_repository_id"] == REPOSITORY_ID
        and receipt["workflow_id"] == WORKFLOW_ID
        and receipt["workflow_path"] == WORKFLOW_PATH
    )
    require(
        type(receipt["head_ref"]) is str and len(receipt["head_ref"]) <= 64 and BRANCH.fullmatch(receipt["head_ref"])
    )
    for field in ("head_sha", "workflow_head_sha"):
        require(type(receipt[field]) is str and SHA.fullmatch(receipt[field]))
    require(receipt["pr_author_id"] in CREATORS and receipt["pr_author_type"] == CREATORS[receipt["pr_author_id"]])
    require(
        receipt["event_name"] in ("schedule", "workflow_dispatch", "repository_dispatch")
        and receipt["event_action"]
        == ("external-plugin-sync" if receipt["event_name"] == "repository_dispatch" else "")
    )
    return receipt


def current_pr(api, number):
    require(positive(number), "invalid-input")
    pr = api.api(f"pulls/{number}")
    require(
        pr["number"] == number
        and pr["state"] == "open"
        and pr["head"]["repo"]["id"] == REPOSITORY_ID
        and pr["base"]["repo"]["id"] == REPOSITORY_ID
        and pr["head"]["repo"]["fork"] is False
        and pr["base"]["ref"] == "main"
        and pr["base"]["repo"]["default_branch"] == "main"
        and pr["user"]["id"] in CREATORS
        and pr["user"]["type"] == CREATORS[pr["user"]["id"]],
        "identity-mismatch",
    )
    return pr


def run_binding(api, pr, base_commit_sha):
    match = BRANCH.fullmatch(pr["head"]["ref"])
    require(match is not None, "not-sync-branch")
    run_id = int(match[1])
    require(positive(run_id), "invalid-input")
    run = api.api(f"actions/runs/{run_id}")
    require(
        run["id"] == run_id
        and run["repository"]["id"] == REPOSITORY_ID
        and run["workflow_id"] == WORKFLOW_ID
        and run["path"] == WORKFLOW_PATH
        and run["head_branch"] == "main"
        and run["event"] in ("schedule", "workflow_dispatch", "repository_dispatch")
        and positive(run["run_attempt"])
        and SHA.fullmatch(run["head_sha"]),
        "untrusted-run",
    )
    require(SHA.fullmatch(base_commit_sha), "invalid-input")
    comparison = api.api(f"compare/{run['head_sha']}...{base_commit_sha}")
    require(
        comparison["status"] in ("ahead", "identical") and comparison["merge_base_commit"]["sha"] == run["head_sha"],
        "untrusted-source",
    )
    return run


def producer(api, number, base_commit_sha, event, run_id, attempt, local_head, local_ref, event_name):
    # The PAT deliberately needs only contents/PR permissions. Immutable runner
    # context supplies run identity; the consumer independently authenticates it
    # through Actions metadata and the server-associated artifact.
    pr = current_pr(api, number)
    match = BRANCH.fullmatch(local_ref)
    require(
        match is not None
        and int(match[1]) == run_id
        and positive(attempt)
        and pr["head"]["sha"] == local_head
        and pr["head"]["ref"] == local_ref,
        "proof-mismatch",
    )
    return validate_receipt(
        {
            "format_version": 1,
            "repository_id": REPOSITORY_ID,
            "workflow_id": WORKFLOW_ID,
            "workflow_path": WORKFLOW_PATH,
            "workflow_head_sha": base_commit_sha,
            "run_id": run_id,
            "run_attempt": attempt,
            "event_name": event_name,
            "event_action": event.get("action", "") if event_name == "repository_dispatch" else "",
            "pr_number": number,
            "pr_author_id": pr["user"]["id"],
            "pr_author_type": pr["user"]["type"],
            "head_repository_id": REPOSITORY_ID,
            "head_ref": local_ref,
            "head_sha": local_head,
        }
    )


def consumer(api, number, base_commit_sha, expected_head):
    require(type(expected_head) is str and SHA.fullmatch(expected_head), "invalid-input")
    pr = current_pr(api, number)
    require(pr["head"]["sha"] == expected_head, "proof-mismatch")
    run = run_binding(api, pr, base_commit_sha)
    rid, attempt = run["id"], run["run_attempt"]
    jobs = api.api(f"actions/runs/{rid}/attempts/{attempt}/jobs?per_page=100")
    require(jobs["total_count"] <= 100, "producer-incomplete")
    matching = [job for job in jobs["jobs"] if job["name"] == "Sync from external repos"]
    require(len(matching) == 1, "producer-incomplete")
    for name in ("Run sync script", "Scan synced content for injected payloads", "Create Pull Request"):
        steps = [step for step in matching[0]["steps"] if step["name"] == name]
        require(
            len(steps) == 1 and steps[0]["status"] == "completed" and steps[0]["conclusion"] == "success",
            "producer-incomplete",
        )
    artifacts = api.api(f"actions/runs/{rid}/artifacts?per_page=100")
    require(artifacts["total_count"] <= 100, "missing-proof")
    matching = [a for a in artifacts["artifacts"] if a["name"] == f"sync-pr-provenance-{rid}-{attempt}"]
    require(len(matching) == 1, "missing-proof")
    artifact = matching[0]
    require(
        artifact["expired"] is False
        and artifact["size_in_bytes"] <= 65536
        and artifact["workflow_run"]["id"] == rid
        and artifact["workflow_run"]["head_sha"] == run["head_sha"],
        "missing-proof",
    )
    receipt = parse_archive(api.archive(artifact["id"]), artifact.get("digest"))
    expected = {
        "repository_id": REPOSITORY_ID,
        "workflow_id": WORKFLOW_ID,
        "workflow_head_sha": run["head_sha"],
        "run_id": rid,
        "run_attempt": attempt,
        "event_name": run["event"],
        "pr_number": number,
        "pr_author_id": pr["user"]["id"],
        "pr_author_type": pr["user"]["type"],
        "head_repository_id": pr["head"]["repo"]["id"],
        "head_ref": pr["head"]["ref"],
        "head_sha": pr["head"]["sha"],
    }
    require(all(receipt[key] == value for key, value in expected.items()), "proof-mismatch")
    return "advisory"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("consume", "produce"))
    args = parser.parse_args()
    try:
        # Linux Actions runner: bounds the entire proof, including slow byte trickles.
        def timeout_handler(signum, frame):
            raise ProofFailure("proof-timeout")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, 30)
        api = GitHub(os.environ.get("GH_TOKEN", ""))
        number = int(os.environ.get("SYNC_PR_NUMBER", "0"))
        base = os.environ.get("SYNC_BASE_COMMIT_SHA", "")
        if args.mode == "consume":
            print(consumer(api, number, base, os.environ.get("SYNC_EXPECTED_HEAD", "")))
        else:
            with Path(os.environ["GITHUB_EVENT_PATH"]).open("rb") as event_file:
                event = strict_json(event_file.read(1024 * 1024 + 1), 1024 * 1024)
            receipt = producer(
                api,
                number,
                base,
                event,
                int(os.environ["GITHUB_RUN_ID"]),
                int(os.environ["GITHUB_RUN_ATTEMPT"]),
                os.environ["SYNC_HEAD_SHA"],
                os.environ["SYNC_HEAD_REF"],
                os.environ["GITHUB_EVENT_NAME"],
            )
            Path(os.environ["SYNC_RECEIPT_PATH"]).write_text(json.dumps(receipt, sort_keys=True) + "\n")
        reason = "eligible"
    except ProofFailure as error:
        reason = error.reason
    except Exception:
        # Never print raw urllib/ZIP/JSON errors, signed URLs, tokens or payloads.
        reason = "internal-error"
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(f"sync provenance: {reason}", file=sys.stderr)
    if reason != "eligible":
        if args.mode == "consume":
            print("full")
        else:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
