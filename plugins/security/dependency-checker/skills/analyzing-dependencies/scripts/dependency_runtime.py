"""Shared bounded I/O for the bundled dependency reports; standard library only."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time


MAX_REPORT_BYTES = 32 * 1024 * 1024
MAX_ERROR_BYTES = 1024 * 1024


class CheckError(ValueError):
    """A failed or unsupported observation, never evidence of absence."""


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise CheckError("duplicate JSON key")
        result[key] = value
    return result


def _constant(_value):
    raise CheckError("non-finite JSON number")


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        raise CheckError("non-finite JSON number")
    return result


def parse_json(raw):
    if len(raw) > MAX_REPORT_BYTES:
        raise CheckError("report exceeds the input limit")
    try:
        return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)
    except (ValueError, UnicodeError, RecursionError) as error:
        # Native error bodies and parse excerpts can contain registry credentials.
        raise CheckError("invalid or unsupported JSON report") from error


def load_json(path):
    try:
        with Path(path).open("rb") as stream:
            return parse_json(stream.read(MAX_REPORT_BYTES + 1))
    except OSError as error:
        raise CheckError("cannot read the selected JSON file") from error


def object_value(value, label="object"):
    if not isinstance(value, dict):
        raise CheckError(f"expected {label} object")
    return value


def array_value(value, label="array"):
    if not isinstance(value, list):
        raise CheckError(f"expected {label} array")
    return value


def string_value(value, label="string"):
    if not isinstance(value, str) or not value.strip():
        raise CheckError(f"expected nonempty {label}")
    return value


def visible(value):
    """Escape terminal control bytes; this is not general secret redaction."""
    return "".join(
        char if ord(char) >= 32 and not 127 <= ord(char) <= 159 else f"\\u{ord(char):04x}" for char in str(value)
    )


def run_tool(arguments, *, timeout=30, cwd=None):
    """Capture private temporary output with a deadline and size checks.

    This does not sandbox an executable. Operators must trust the selected
    installed tools; neither their stderr nor malformed stdout is echoed.
    """
    if not 0 < timeout <= 300:
        raise CheckError("timeout must be greater than zero and at most 300 seconds")
    process = None
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        try:
            process = subprocess.Popen(
                arguments,
                cwd=cwd,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=errors,
                start_new_session=True,
            )
            deadline = time.monotonic() + timeout
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    raise CheckError("audit tool timed out")
                if (
                    os.fstat(output.fileno()).st_size > MAX_REPORT_BYTES
                    or os.fstat(errors.fileno()).st_size > MAX_ERROR_BYTES
                ):
                    raise CheckError("audit tool output exceeded its limit")
                time.sleep(0.01)
            if (
                os.fstat(output.fileno()).st_size > MAX_REPORT_BYTES
                or os.fstat(errors.fileno()).st_size > MAX_ERROR_BYTES
            ):
                raise CheckError("audit tool output exceeded its limit")
            output.seek(0)
            return process.returncode, output.read(MAX_REPORT_BYTES + 1)
        except OSError as error:
            raise CheckError("required audit tool is unavailable") from error
        finally:
            if process is not None and process.poll() is None:
                # Only the process group created by this invocation is owned.
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.wait()


def write_report(text, destination=None):
    """Stdout is a single document; explicit files are replaced atomically, 0600."""
    if destination is None:
        print(text)
        return
    path = Path(destination)
    if path.is_symlink():
        raise CheckError("report destination must not be a symbolic link")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=".dependency-report-",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.write("\n")
        os.replace(temporary, path)
        temporary = None
    except OSError as error:
        raise CheckError("cannot write the selected report destination") from error
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
