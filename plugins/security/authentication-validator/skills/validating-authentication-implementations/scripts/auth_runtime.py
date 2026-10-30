"""Bounded local input and private report output; no network or installation."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import tempfile

MAX_INPUT = 1024 * 1024


class InputError(ValueError):
    """A deliberately non-sensitive diagnostic."""


def read_bytes(path, limit=MAX_INPUT):
    try:
        with Path(path).open("rb") as stream:
            data = stream.read(limit + 1)
    except OSError as error:
        raise InputError("cannot read selected input") from error
    if len(data) > limit:
        raise InputError("input exceeds size limit")
    return data


def _pairs(items):
    result = {}
    for name, value in items:
        if name in result:
            raise InputError("duplicate JSON member")
        result[name] = value
    return result


def _constant(_value):
    raise InputError("non-finite JSON number")


def _float(value):
    result = float(value)
    if not math.isfinite(result):
        raise InputError("non-finite JSON number")
    return result


def parse_object(data):
    try:
        result = json.loads(data, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise InputError("invalid JSON object") from error
    if not isinstance(result, dict):
        raise InputError("expected JSON object")
    return result


def load_object(path):
    return parse_object(read_bytes(path))


def write_report(report, destination=None, *, protected_inputs=()):
    text = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if destination is None:
        print(text, end="")
        return
    path = Path(destination)
    if path.is_symlink():
        raise InputError("report destination must not be a symbolic link")
    try:
        for selected in protected_inputs:
            if selected is None:
                continue
            source = Path(selected)
            if path.resolve() == source.resolve() or (path.exists() and source.exists() and path.samefile(source)):
                raise InputError("report destination aliases a selected input")
    except (OSError, RuntimeError) as error:
        raise InputError("cannot establish a separate report destination") from error
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".auth-report-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        os.replace(temporary, path)
        temporary = None
    except OSError as error:
        raise InputError("cannot write selected report") from error
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
