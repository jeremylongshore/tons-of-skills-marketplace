"""Select changed Markdown from an exact integration tree; uncertainty keeps full scans."""

import argparse
from pathlib import Path
import re
import subprocess


def select(root, base, scan):
    if not re.fullmatch(r"[0-9a-f]{40}", base):
        raise ValueError("invalid base identity")
    result = subprocess.run(
        ["git", "--no-replace-objects", "diff", "--name-status", "-z", "--no-renames", base, "HEAD"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    fields = result.stdout.decode("utf-8").split("\0")
    if fields.pop() != "" or len(fields) % 2:
        raise ValueError("incomplete diff")
    inputs = []
    for status, name in zip(fields[::2], fields[1::2]):
        if name in {".lychee.toml", ".github/workflows/check-links.yml", "scripts/ci/link_scope.py"}:
            return None
        if not name.endswith((".md", ".mdx")):
            continue
        if (
            status not in {"A", "M"}
            or not re.fullmatch(r"[A-Za-z0-9_./-]+", name)
            or name.startswith("/")
            or ".." in name.split("/")
        ):
            return None
        path = root / name
        if path.is_symlink() or not path.is_file():
            return None
        marketplace = name.startswith("marketplace/src/content/")
        if marketplace == (scan == "marketplace"):
            inputs.append("./" + name)
    return sorted(set(inputs))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--scan", choices=["repo", "marketplace"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        selected = select(Path.cwd(), args.base, args.scan)
    except (ValueError, UnicodeError, OSError, subprocess.SubprocessError):
        selected = None
    # Only a complete trusted comparison may narrow the default scan.
    if selected is None:
        output = "full=true\nrun=true\ninputs=\n"
    else:
        output = f"full=false\nrun={'true' if selected else 'false'}\ninputs={' '.join(selected)}\n"
    with args.output.open("a") as handle:
        handle.write(output)


if __name__ == "__main__":
    main()
