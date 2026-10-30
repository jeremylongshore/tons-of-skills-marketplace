#!/usr/bin/env python3
"""Opt-in native hook probe, using only Docker loopback and canned model replies.

Requires Linux, Docker, Python 3.12+, jq, a cached Python image, and the standalone
Claude binary. No host credentials or Docker socket are mounted in the container.
The formatter dependency is a local marker executable, not a Prettier integration.

Example:
    python3 tests/run_native_hook_events.py --image python:3.14.8-slim \
        --baseline-ref 7409ebbfdb302045c4f7d523d834e74209ed0fef

The optional baseline demonstrates the historical GCP bypass. Artifacts stay in a
new private temporary directory; only this runner's stopped container is removed.
"""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = {
    "gcp": "plugins/devops/jeremy-github-actions-gcp",
    "formatter": "plugins/examples/formatter",
}


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="already cached Python image")
    parser.add_argument("--claude-binary", default=shutil.which("claude"))
    parser.add_argument("--baseline-ref")
    args = parser.parse_args()
    if platform.system() != "Linux" or sys.version_info < (3, 12):
        parser.error("This opt-in runner requires Linux and Python 3.12+")
    if not args.claude_binary or not shutil.which("jq"):
        parser.error("A standalone Claude binary and jq are required")
    binary = Path(args.claude_binary).resolve(strict=True)
    jq = Path(shutil.which("jq")).resolve(strict=True)
    image = output("docker", "image", "inspect", args.image, "--format", "{{.Id}}")
    folder = Path(tempfile.mkdtemp(prefix="native-hook-events-runtime-"))
    hashes = {}
    for alias, plugin in PLUGINS.items():
        paths = subprocess.check_output(["git", "ls-files", "-z", "--", plugin], cwd=ROOT).decode().split("\0")
        for relative in filter(None, paths):
            source = ROOT / relative
            if source.is_symlink() or not source.is_file():
                raise RuntimeError("Expected a tracked regular source file: " + relative)
            destination = folder / "sources/candidate" / alias / source.relative_to(ROOT / plugin)
            destination.parent.mkdir(parents=True, exist_ok=True)
            before = sha(source)
            shutil.copy2(source, destination)
            assert sha(destination) == before
            hashes[relative] = before
    if args.baseline_ref:
        archive = subprocess.check_output(["git", "archive", args.baseline_ref, "--", *PLUGINS.values()], cwd=ROOT)
        baseline = folder / "historical-source"
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(baseline, filter="data")
        for alias, plugin in PLUGINS.items():
            shutil.copytree(baseline / plugin, folder / "sources/baseline" / alias)
    controller = ROOT / "tests/fixtures/native_hook_events/runtime.py"
    shutil.copy2(controller, folder / "run.py")
    tools = folder / "bin"
    tools.mkdir()
    (tools / "prettier").write_text(
        "#!/usr/local/bin/python3\nimport os,sys,json,pathlib\n"
        "with open(os.environ['HOOK_RUNTIME_MARKER'],'a') as f: "
        "f.write(json.dumps(sys.argv[1:])+'\\n')\n"
        "if '--write' in sys.argv: pathlib.Path(sys.argv[-1]).write_text('const fixture = 2;\\n')\n"
    )
    (tools / "npx").write_text("#!/bin/sh\necho 'Unexpected npx invocation' >&2\nexit 99\n")
    for tool in tools.iterdir():
        tool.chmod(0o755)
    command = [
        "docker",
        "create",
        "--pull=never",
        "--network",
        "none",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "--workdir",
        "/work",
        "--env",
        "LD_LIBRARY_PATH=/opt/jiglib",
    ]
    mounts = [(folder, "/work", False), (binary, "/usr/local/bin/claude", True), (jq, "/usr/local/bin/jq", True)]
    for line in output("ldd", str(jq)).splitlines():
        match = re.search(r"(libjq\.so\S*|libonig\.so\S*) => (\S+)", line)
        if match:
            mounts.append((Path(match[2]), "/opt/jiglib/" + match[1], True))
    for source, destination, readonly in mounts:
        if "," in str(source):
            raise RuntimeError("Docker mount source cannot contain a comma")
        command += ["--mount", f"type=bind,src={source},dst={destination}" + (",readonly" if readonly else "")]
    command += [image, "python3", "/work/run.py"]
    cid = output(*command)
    (folder / "container-id.txt").write_text(cid + "\n")
    config = json.loads(output("docker", "inspect", cid))[0]
    isolation = {
        "id": cid,
        "image": image,
        "network_mode": config["HostConfig"]["NetworkMode"],
        "cap_drop": config["HostConfig"]["CapDrop"],
        "security_opt": config["HostConfig"]["SecurityOpt"],
        "user": config["Config"]["User"],
    }
    assert isolation["network_mode"] == "none" and isolation["user"] != "0:0"
    (folder / "isolation.json").write_text(json.dumps(isolation, indent=2) + "\n")
    print("Native fixture artifacts:", folder, flush=True)
    # An observation timeout must not restart or forcibly remove a live container.
    result = subprocess.run(["docker", "start", "--attach", cid], cwd=ROOT)
    final = json.loads(output("docker", "inspect", cid))[0]["State"]
    assert not final["Running"]
    results = json.loads((folder / "results.json").read_text())
    receipt = {
        "base_revision": output("git", "rev-parse", "HEAD"),
        "baseline_ref": args.baseline_ref,
        "source_sha256": hashes,
        "controller_sha256": sha(controller),
        "runner_sha256": sha(__file__),
        "claude_sha256": sha(binary),
        "isolation": isolation,
        "native_version": results["native_version"],
        "cases": results["cases"],
        "passed": result.returncode == 0 and final["ExitCode"] == 0 and results["passed"],
        "scope": "Native hook contract; canned loopback API and marker Prettier; no live provider",
    }
    (folder / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    subprocess.run(["docker", "rm", cid], check=True, stdout=subprocess.DEVNULL)
    if not receipt["passed"]:
        raise SystemExit("Native hook probe failed; inspect " + str(folder))
    print("Native hook probe PASS:", len(results["cases"]), "cases", flush=True)


if __name__ == "__main__":
    main()
