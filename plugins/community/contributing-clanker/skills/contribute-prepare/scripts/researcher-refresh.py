#!/usr/bin/env python3
"""Preserve dossier manual sections and publish a complete refresh."""

import argparse
import os
from pathlib import Path
import re
import stat
import sys
import tempfile


HEADINGS = (b"Pet peeves & known triggers", b"Failure log", b"Notes")
H2 = re.compile(rb" {0,3}##(?:[ \t]+(.*?))?[ \t]*$")
FENCE = re.compile(rb" {0,3}(`{3,}|~{3,})(.*)$")


def sections(data):
    """Return byte spans of the three bodies; refuse unclear boundaries."""
    data.decode("utf-8")  # Invalid text must never be silently replaced.
    found = {}
    active = None
    fence = None
    offset = 0
    for line in data.splitlines(keepends=True):
        text = line.rstrip(b"\r\n")
        marker = FENCE.fullmatch(text)
        if fence is not None:
            if marker and marker[1][:1] == fence[:1] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            if marker[1].startswith(b"`") and b"`" in marker[2]:
                raise ValueError("ambiguous backtick fence")
            fence = marker[1]
        else:
            heading = H2.fullmatch(text)
            if heading:
                if active is not None:
                    found[active][1] = offset
                    active = None
                name = heading[1]
                if name in HEADINGS:
                    if name in found:
                        raise ValueError("duplicate manual heading: " + name.decode())
                    found[name] = [offset + len(line), len(data)]
                    active = name
        offset += len(line)
    if fence is not None:
        raise ValueError("unclosed fenced block")
    if set(found) != set(HEADINGS):
        raise ValueError("expected exactly one of each manual heading")
    return found


def merge(generated, existing):
    placeholders = sections(generated)
    if existing is None:
        return generated
    preserved = sections(existing)
    result = generated
    for name, (start, end) in sorted(placeholders.items(), key=lambda item: item[1][0], reverse=True):
        old_start, old_end = preserved[name]
        result = result[:start] + existing[old_start:old_end] + result[end:]
    # For example, a manual body without a final newline could swallow a heading.
    sections(result)
    return result


def snapshot(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("dossier must be a regular file, not a symlink or directory")
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as stream:
        opened = os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode):
            raise ValueError("dossier changed to a nonregular file")
        if (info.st_dev, info.st_ino) != (opened.st_dev, opened.st_ino):
            raise ValueError("dossier changed while opening")
        data = stream.read()
    return data, opened


def identity(saved):
    if saved is None:
        return None
    data, info = saved
    return data, info.st_dev, info.st_ino, info.st_mode, info.st_mtime_ns, info.st_ctime_ns


def refresh(generated, destination, stdout=False):
    original = snapshot(destination)
    result = merge(generated, None if original is None else original[0])
    if stdout:
        sys.stdout.buffer.write(result)
        sys.stdout.buffer.flush()
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".researcher-", dir=destination.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            if original is not None:
                os.fchmod(stream.fileno(), stat.S_IMODE(original[1].st_mode))
            stream.write(result)
            stream.flush()
            os.fsync(stream.fileno())
        if identity(snapshot(destination)) != identity(original):
            raise ValueError("dossier changed during refresh; retry after edits finish")
        if original is None:
            # Creation cannot overwrite a file that appeared after the check.
            os.link(temporary, destination)
        else:
            # Atomic publication; an uncooperative editor can still race this
            # final check-to-replace window. Coordinate simultaneous writers.
            os.replace(temporary, destination)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    try:
        refresh(args.generated.read_bytes(), args.destination, args.stdout)
    except (OSError, ValueError) as error:
        print(f"researcher-refresh: refused refresh: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
