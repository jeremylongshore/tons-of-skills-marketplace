"""Regression checks for the daily marketplace-stats publication contract.

The workflow owns four public surfaces: three generated data files and the
README ``NPM-STATS`` block. A 2026-09-02 run updated the npm JSON but caught a
missing Prettier import and silently skipped the README, producing a green
workflow and a self-contradictory PR. A 2026-09-09 run exposed that the bot's
npm-only title and body also omitted the GitHub and skills.sh outputs. These
checks pin dependency setup, fail-closed error handling, prepare-before-write
ordering, and a truthful generated PR narrative.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "update-npm-stats.yml"
GENERATOR = REPO_ROOT / "scripts" / "fetch-npm-stats.mjs"


def test_workflow_installs_generator_dependencies_before_fetching() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    corepack = workflow.index("run: corepack enable")
    install = workflow.index(
        'run: pnpm install --frozen-lockfile --filter "claude-code-plugins-monorepo" --ignore-scripts'
    )
    fetch = workflow.index("run: node scripts/fetch-npm-stats.mjs")

    assert corepack < install < fetch


def test_readme_formatting_is_required_and_precedes_artifact_writes() -> None:
    generator = GENERATOR.read_text(encoding="utf-8")

    assert "import prettier from 'prettier';" in generator
    assert "README update skipped" not in generator

    format_readme = generator.index("const readmeOutput = await formatter.format")
    write_json = generator.index("writeFileSync(OUT_JSON, jsonOutput)")
    write_readme = generator.index("writeFileSync(README, updatedReadme)")

    assert format_readme < write_json < write_readme


def assert_truthful_stats_narrative(workflow: str) -> None:
    assert workflow.startswith("name: Update marketplace stats (daily)\n")
    assert "refresh daily npm download stats" not in workflow

    commit_lines = [
        line.strip()
        for line in workflow.splitlines()
        if line.strip().startswith('git commit --no-verify -m "')
    ]
    assert commit_lines == [
        'git commit --no-verify -m "chore(marketplace-site): refresh daily marketplace stats'
    ]

    pr_block = workflow[
        workflow.index("gh pr create") : workflow.index("\n          fi", workflow.index("gh pr create"))
    ]
    title_lines = [
        line.strip() for line in pr_block.splitlines() if line.strip().startswith('--title "')
    ]
    assert title_lines == [
        '--title "chore(marketplace-site): refresh daily marketplace stats" \\'
    ]

    body_start = pr_block.index('--body "') + len('--body "')
    body_end = pr_block.rindex('"')
    body = pr_block[body_start:body_end]
    expected_body = (
        "## Daily Marketplace Stats\n"
        "\n"
        "          Refreshes the marketplace's generated npm, skills.sh, and GitHub statistics "
        "plus the README \\`NPM-STATS\\` block.\n"
        "\n"
        "          - **npm:** \\`scripts/fetch-npm-stats.mjs\\` → "
        "\\`marketplace/src/data/npm-stats.json\\` and the README block\n"
        "          - **skills.sh:** \\`scripts/fetch-skills-stats.mjs\\` → "
        "\\`marketplace/src/data/skills-stats.json\\`\n"
        "          - **GitHub:** \\`scripts/fetch-github-stats.mjs\\` → "
        "\\`marketplace/src/data/github-stats.json\\`\n"
        "          - **Cadence:** daily at 00:15 UTC\n"
        "          - **Idempotent:** re-running force-pushes \\`automation/npm-stats\\`; "
        "this PR auto-updates instead of stacking PRs.\n"
        "\n"
        "          Generated data only; merge after required checks pass."
    )
    assert body == expected_body
    assert "safe to merge" not in body.casefold()

    summary = workflow[workflow.index("      - name: Summary") :]
    summary_headings = [
        line.strip()
        for line in summary.splitlines()
        if line.strip().startswith('echo "## ') and "GITHUB_STEP_SUMMARY" in line
    ]
    assert summary_headings == [
        'echo "## 📊 Marketplace Stats Refresh" >> "$GITHUB_STEP_SUMMARY"'
    ]


def test_generated_pr_narrative_names_every_stats_source_and_output() -> None:
    assert_truthful_stats_narrative(WORKFLOW.read_text(encoding="utf-8"))


def test_each_generated_narrative_surface_fails_closed_on_drift() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    mutations = {
        "workflow-name": workflow.replace(
            "name: Update marketplace stats (daily)",
            "name: Update npm stats (daily)",
            1,
        ),
        "commit-subject-suffix": workflow.replace(
            "refresh daily marketplace stats\n\n          Auto-generated",
            "refresh daily marketplace stats for npm only\n\n          Auto-generated",
            1,
        ),
        "pr-title-suffix": workflow.replace(
            '--title "chore(marketplace-site): refresh daily marketplace stats"',
            '--title "chore(marketplace-site): refresh daily marketplace stats for npm only"',
            1,
        ),
        "body-path-suffix": workflow.replace(
            "marketplace/src/data/npm-stats.json\\` and the README block",
            "marketplace/src/data/npm-stats.json.wrong\\` and the README block",
            1,
        ),
        "premature-merge-claim": workflow.replace(
            "Generated data only; merge after required checks pass.",
            "Generated data only; merge after required checks pass. Safe to merge immediately.",
            1,
        ),
        "summary-suffix": workflow.replace(
            "## 📊 Marketplace Stats Refresh",
            "## 📊 Marketplace Stats Refresh for npm only",
            1,
        ),
    }

    for name, mutation in mutations.items():
        assert mutation != workflow, f"mutation fixture did not alter {name}"
        try:
            assert_truthful_stats_narrative(mutation)
        except (AssertionError, ValueError):
            continue
        raise AssertionError(f"narrative contract admitted the {name} mutation")
