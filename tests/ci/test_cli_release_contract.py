"""Regression checks for the ccpi CLI test and release workflows.

Two defects shaped these checks. The CLI's filtered install also installs the
repository root's devDependencies, so every CLI job natively built
better-sqlite3 for @intentsolutions/jrig-cli, which the CLI never loads; on
Windows that needed a pinned node-gyp while the runner used Node 20. And the
publish job ran a bare ``npm publish``, so a pre-release tag such as
cli-v3.1.0-beta.1 would have become the ``latest`` dist-tag for every user.
"""

import re
import subprocess
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_TEST = REPO_ROOT / ".github" / "workflows" / "cli-test.yml"
CLI_PUBLISH = REPO_ROOT / ".github" / "workflows" / "cli-publish.yml"
CLI_INSTALL = re.compile(r"pnpm install [^\n]*--filter '@intentsolutionsio/ccpi\.\.\.'")


def _steps(path: Path):
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    for job in workflow["jobs"].values():
        yield from job.get("steps", [])


def test_every_cli_install_skips_dependency_install_scripts() -> None:
    installs = []
    for path in (CLI_TEST, CLI_PUBLISH):
        for step in _steps(path):
            for match in CLI_INSTALL.finditer(step.get("run", "")):
                installs.append((path.name, match.group(0)))
    # cli-test: matrix + Deno; cli-publish: quality gate + publish.
    assert len(installs) == 4, installs
    for name, command in installs:
        assert "--ignore-scripts" in command, f"{name}: {command}"
        assert "--frozen-lockfile" in command, f"{name}: {command}"


def test_cli_tests_no_longer_pin_node_gyp() -> None:
    assert "node-gyp@" not in CLI_TEST.read_text(encoding="utf-8")


def _publish_run() -> str:
    step = next(s for s in _steps(CLI_PUBLISH) if s.get("name") == "Publish to npm (with provenance)")
    return step["run"]


def _dist_tag_for(version: str) -> str:
    """Execute the workflow's own dist-tag selection for one version."""
    run = _publish_run()
    selection = run[run.index("case") : run.index("esac") + len("esac")]
    script = f'VERSION="{version}"\n{selection}\nprintf "%s" "$DIST_TAG"'
    return subprocess.run(
        ["bash", "-euo", "pipefail", "-c", script], check=True, capture_output=True, text=True
    ).stdout


def test_publish_passes_an_explicit_dist_tag() -> None:
    assert 'npm publish --provenance --access public --tag "$DIST_TAG"' in _publish_run()


def test_prereleases_publish_to_next_and_stable_versions_to_latest() -> None:
    assert _dist_tag_for("3.0.0") == "latest"
    assert _dist_tag_for("3.0.1") == "latest"
    assert _dist_tag_for("3.1.0-beta.1") == "next"
    assert _dist_tag_for("4.0.0-rc.2") == "next"


def test_prerelease_github_releases_are_marked_prerelease() -> None:
    step = next(s for s in _steps(CLI_PUBLISH) if s.get("name") == "Create GitHub Release")
    assert "PRERELEASE_ARGS=(--prerelease)" in step["run"]
    assert '"${PRERELEASE_ARGS[@]}"' in step["run"]
