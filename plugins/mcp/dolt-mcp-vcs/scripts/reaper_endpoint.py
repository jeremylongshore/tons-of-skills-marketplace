#!/usr/bin/env python3
"""Read-only Linux process/loopback identity check for the idle reaper."""
import os
import re
import sys
from pathlib import Path


def identity(pid, proc=Path("/proc")):
    """Return '<start ticks> <port>'; refuse unknown or ambiguous ownership.

    proc is injectable only for tests; the command line always uses /proc.
    IPv6-only and non-loopback listeners conservatively remain unreaped.
    """
    if not re.fullmatch(r"[1-9][0-9]*", str(pid)):
        raise ValueError("invalid pid")
    process = proc / str(pid)
    if os.readlink(process / "ns/net") != os.readlink(proc / "self/ns/net"):
        raise ValueError("different network namespace")
    argv = (process / "cmdline").read_bytes().split(b"\0")
    if len(argv) < 2 or Path(os.fsdecode(argv[0])).name != "dolt" or argv[1] != b"sql-server":
        raise ValueError("not a direct dolt sql-server process")
    # comm (field 2) can contain spaces and parentheses. Fields after the final
    # ')' begin at state (field 3); starttime is field 22, index 19 in this tail.
    start = (process / "stat").read_text().rsplit(")", 1)[1].split()[19]
    if not start.isdecimal():
        raise ValueError("unknown process start")
    inodes = set()
    for fd in (process / "fd").iterdir():
        try:
            target = os.readlink(fd)
        except FileNotFoundError:
            continue  # descriptor closed during the observation
        match = re.fullmatch(r"socket:\[([0-9]+)\]", target)
        if match:
            inodes.add(match[1])
    ports = set()
    for line in (process / "net/tcp").read_text().splitlines()[1:]:
        fields = line.split()
        if len(fields) < 10:
            raise ValueError("malformed TCP table")
        if fields[3] != "0A" or fields[9] not in inodes:
            continue
        address, port = fields[1].split(":")
        if address not in ("0100007F", "00000000"):
            raise ValueError("listener is not reachable through loopback")
        ports.add(int(port, 16))
    if len(ports) != 1 or not 1 <= next(iter(ports)) <= 65535:
        raise ValueError("no unique owned loopback listener")
    return f"{start} {ports.pop()}"


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("one pid required")
        print(identity(sys.argv[1]))
    except (OSError, ValueError, IndexError):
        sys.exit(1)
