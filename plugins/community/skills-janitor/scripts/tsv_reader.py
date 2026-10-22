"""Skills Janitor - TSV interchange reader.

The scan module's bash side collects one tab-separated row per skill/agent/
command; a single python3 pass renders the JSON inventory. This reader is the
python side of that interchange, extracted from the scan module's heredoc so
tests can import it directly. The scan module's observable behavior must not
change because of this file.

Row encoding contract (written by the bash side): fields are tab-separated;
literal tabs/newlines inside a value were replaced with a space; empty values
became the sentinel "_" (bash `read` with IFS=$'\t' collapses consecutive
tabs). This reader decodes "_" back to empty.
"""

import os

S = "_"  # sentinel for empty fields


def d(v):
    return "" if v == S else v


def read_tsv(path, n_fields):
    # newline="\n": with universal newlines a stray CR inside a field ends the
    # line, splitting one record into two short ones that both fail the
    # field-count check below — a whole skill disappears with no error. Writers
    # strip CR at the source; this makes the reader safe regardless.
    rows = []
    if not path or not os.path.isfile(path):
        return rows
    with open(path, newline="\n") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != n_fields:
                continue
            rows.append([d(p) for p in parts])
    return rows


if __name__ == "__main__":
    # Standalone invocation for tests: tsv_reader.py <path> <n_fields>
    # prints the decoded rows as a JSON array.
    import json
    import sys

    print(json.dumps(read_tsv(sys.argv[1], int(sys.argv[2]))))
