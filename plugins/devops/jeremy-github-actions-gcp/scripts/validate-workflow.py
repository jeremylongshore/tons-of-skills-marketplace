#!/usr/bin/env python3
"""Apply the existing lexical GCP checks to the proposed native tool content.

This is not a YAML parser, secret detector, or guarantee of GCP deployment safety.
"""

import json
import os
from pathlib import Path
import re
import sys


def proposed_content(event):
    if not isinstance(event, dict):
        raise ValueError("Expected a hook event object")
    if event.get("hook_event_name") != "PreToolUse":
        return None
    tool = event.get("tool_name")
    if tool not in ("Write", "Edit"):
        return None
    data = event.get("tool_input")
    if not isinstance(data, dict):
        raise ValueError("Missing tool input")
    name, cwd = data.get("file_path"), event.get("cwd")
    if not isinstance(name, str) or not name or not isinstance(cwd, str) or not os.path.isabs(cwd):
        raise ValueError("Missing file path or absolute event cwd")
    # Use lexical paths: a symlink inside workflows must not evade its guard.
    target = Path(os.path.abspath(os.path.join(cwd, name)))
    directory = Path(os.path.abspath(cwd)) / ".github" / "workflows"
    if target.parent != directory or target.suffix not in (".yml", ".yaml"):
        return None
    if tool == "Write":
        content = data.get("content")
        if not isinstance(content, str):
            raise ValueError("Write requires string content")
        return content
    old, new = data.get("old_string"), data.get("new_string")
    replace_all = data.get("replace_all", False)
    if not isinstance(old, str) or not old or not isinstance(new, str) or type(replace_all) is not bool:
        raise ValueError("Edit requires old/new strings and a boolean replace_all")
    content = target.read_text(encoding="utf-8")
    matches = content.count(old)
    if not matches or (matches != 1 and not replace_all):
        raise ValueError("Cannot establish the proposed Edit result")
    return content.replace(old, new) if replace_all else content.replace(old, new, 1)


def findings(content):
    errors, warnings = [], []
    if "credentials_json" in content:
        errors.append("JSON service account keys detected; use Workload Identity Federation")
    if "workload_identity_provider" in content and "id-token: write" not in content:
        errors.append("Workload Identity Federation requires id-token: write")
    if re.search(r"roles/owner|roles/editor", content):
        errors.append("Overly permissive IAM role detected; use least privilege")
    if re.search(r"GOOGLE_APPLICATION_CREDENTIALS.*=|GCP_SA_KEY.*=", content):
        errors.append("Hardcoded credential assignment detected; use managed secrets")
    if ("vertex" in content or "aiplatform" in content) and not re.search(
        r"validate-deployment|validate-agent", content
    ):
        warnings.append("Vertex AI deployment has no post-deployment validation step")
    if "deploy" in content and not re.search(r"trivy|trufflehog", content):
        warnings.append("Consider security scanning before deployment")
    return errors, warnings


def main():
    manual = len(sys.argv) > 1
    denied = 1 if manual else 2
    try:
        if manual:
            if len(sys.argv) != 2:
                raise ValueError("Usage: validate-workflow.sh <workflow-file>, or native JSON on stdin")
            content = Path(sys.argv[1]).read_text(encoding="utf-8")
        else:
            content = proposed_content(json.load(sys.stdin))
        if content is None:
            return 0
        errors, warnings = findings(content)
        for warning in warnings:
            print("Workflow warning: " + warning, file=sys.stderr)
        for error in errors:
            print("Workflow policy: " + error, file=sys.stderr)
        if errors:
            return denied
        if manual:
            print("GitHub Actions workflow lexical checks passed")
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        # Do not echo event bodies, workflow contents, or credential matches.
        print("Cannot validate proposed workflow: " + type(error).__name__, file=sys.stderr)
        return denied


if __name__ == "__main__":
    sys.exit(main())
