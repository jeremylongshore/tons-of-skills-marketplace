#!/usr/bin/env python3
"""Validate the deliberately small funding schema admitted by the CI fast lane.

Adding platforms or accepting richer YAML requires a reviewed code change and
the full CI lane. These handle patterns intentionally accept a conservative
subset of platform usernames, never arbitrary payment URLs.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import stat
import sys

import yaml
from yaml.tokens import AliasToken, AnchorToken, DirectiveToken, TagToken

MAX_BYTES = 16 * 1024
SUPPORTED_KEYS = frozenset({"github", "buy_me_a_coffee", "ko_fi"})
GITHUB_HANDLE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}")
SUPPORT_HANDLE = re.compile(r"[A-Za-z0-9]{1,39}")


class FundingError(ValueError):
    """A funding manifest is outside the reviewed schema."""


class FundingLoader(yaml.SafeLoader):
    """Safe YAML with no duplicate, merged, or non-string mapping keys."""

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            if key_node.tag != "tag:yaml.org,2002:str" or key_node.value == "<<":
                raise FundingError("mapping keys must be plain platform names; merge keys are forbidden")
            key = self.construct_object(key_node, deep=deep)
            if key in result:
                raise FundingError("duplicate platform key")
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def read_manifest(path: Path) -> str:
    """Read one bounded regular file without following a final-component symlink."""
    if not hasattr(os, "O_NOFOLLOW"):
        raise FundingError("this validator requires no-follow file opening")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise FundingError("manifest must be an existing regular file, not a link or special file")
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise FundingError("manifest exceeds the 16 KiB limit")
    return raw.decode("utf-8")


def validate_manifest(text: str) -> None:
    # Reject advanced YAML before construction, including harmless explicit
    # tags: aliases/anchors must not hide duplicate or merged platform values.
    for token in yaml.scan(text):
        if isinstance(token, (AliasToken, AnchorToken, DirectiveToken, TagToken)):
            raise FundingError("YAML anchors, aliases, directives, and explicit tags are forbidden")
    data = yaml.load(text, Loader=FundingLoader)
    if not isinstance(data, dict) or not data:
        raise FundingError("manifest must be a nonempty platform mapping")
    if not set(data).issubset(SUPPORTED_KEYS):
        raise FundingError("supported platforms are github, buy_me_a_coffee, and ko_fi")
    for platform, value in data.items():
        if platform == "github":
            if not isinstance(value, list) or not 1 <= len(value) <= 4:
                raise FundingError("github must be a list of one to four handles")
            if any(not isinstance(handle, str) or not GITHUB_HANDLE.fullmatch(handle) for handle in value):
                raise FundingError("github handles must be 1–39 letters/digits with single internal hyphens")
            if len({handle.casefold() for handle in value}) != len(value):
                raise FundingError("github handles must be distinct, ignoring case")
        elif not isinstance(value, str) or not SUPPORT_HANDLE.fullmatch(value):
            raise FundingError("support handles must be scalar strings of 1–39 ASCII letters/digits")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=Path(".github/FUNDING.yml"))
    args = parser.parse_args()
    try:
        validate_manifest(read_manifest(args.path))
    except (FundingError, OSError, UnicodeError, yaml.YAMLError) as error:
        # YAML parser diagnostics can echo credential-shaped input. Keep the
        # failure useful without repeating manifest contents into CI logs.
        detail = str(error) if isinstance(error, FundingError) else type(error).__name__
        print(f"funding schema: FAIL ({detail})", file=sys.stderr)
        return 1
    print("funding schema: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
