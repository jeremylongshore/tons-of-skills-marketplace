"""Executable workflow contract for the conservative CI fast lane."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/validate-plugins.yml"
SPEC = importlib.util.spec_from_file_location("fastlane_workflow_under_test", ROOT / "scripts/ci/fastlane.py")
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)
REQUIRED, SKIPPABLE = POLICY.REQUIRED, POLICY.SKIPPABLE


def workflow(name: str = "validate-plugins.yml") -> dict:
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text())


def triggers(document: dict) -> dict:
    # PyYAML's YAML 1.1 resolver interprets the Actions key `on` as True.
    return document.get("on", document.get(True))


class WorkflowRoutingContractTests(unittest.TestCase):
    def setUp(self):
        self.document = workflow()
        self.jobs = self.document["jobs"]

    def test_exact_seven_jobs_can_skip_for_the_lightweight_lane(self):
        self.assertEqual(
            SKIPPABLE,
            {
                "cli-smoke-tests",
                "shellcheck-skills",
                "skill-codeblock-syntax",
                "typescript-coverage-audit",
                "eslint-check",
                "ruff-check",
                "ruff-format-check",
            },
        )
        routed = set()
        for name, job in self.jobs.items():
            if name in SKIPPABLE:
                self.assertEqual(job["if"], "needs.classify-changes.outputs.lane != 'lightweight'")
                expected = (
                    ["classify-changes", "marketplace-validation"] if name == "cli-smoke-tests" else "classify-changes"
                )
                self.assertEqual(job["needs"], expected)
                routed.add(name)
            elif name != "ci-required":
                self.assertNotIn("if", job, name)
        self.assertEqual(routed, SKIPPABLE)

    def test_aggregate_requires_the_complete_job_set_and_runs_after_failure(self):
        aggregate = self.jobs["ci-required"]
        self.assertEqual(aggregate["if"], "always()")
        self.assertEqual(set(aggregate["needs"]), REQUIRED)
        self.assertEqual(len(aggregate["needs"]), len(REQUIRED))
        self.assertEqual(set(self.jobs), REQUIRED | {"ci-required"})
        self.assertEqual(aggregate["steps"][0]["uses"], "actions/checkout@v7")
        gate = aggregate["steps"][1]
        self.assertEqual(gate["env"], {"NEEDS_JSON": "${{ toJSON(needs) }}"})
        self.assertEqual(gate["run"], "python3 scripts/ci/fastlane.py gate")

    def test_required_contexts_are_unfiltered_and_remain_independent(self):
        events = triggers(self.document)
        self.assertEqual(set(events), {"pull_request", "push", "workflow_dispatch"})
        self.assertIsNone(events["pull_request"])
        self.assertIsNone(events["workflow_dispatch"])
        self.assertEqual(events["push"], {"branches": ["main"]})
        for filename, name in (
            ("secret-scan.yml", "gitleaks"),
            ("skill-conform.yml", "skill-conform"),
        ):
            with self.subTest(context=name):
                document = workflow(filename)
                self.assertNotIn(name, self.jobs)
                self.assertNotIn(name, self.jobs["ci-required"]["needs"])
                self.assertNotIn("if", document["jobs"][name])
                self.assertEqual(document["jobs"][name]["name"], name)
                for event in ("pull_request", "push"):
                    config = triggers(document)[event] or {}
                    self.assertNotIn("paths", config)
                    self.assertNotIn("paths-ignore", config)

    def test_classifier_uses_full_history_and_immutable_base_identity(self):
        classifier = self.jobs["classify-changes"]
        self.assertEqual(
            classifier["outputs"],
            {
                "schema": "${{ steps.classify.outputs.schema }}",
                "lane": "${{ steps.classify.outputs.lane }}",
            },
        )
        self.assertEqual(classifier["steps"][0]["with"], {"fetch-depth": 0, "persist-credentials": False})
        step = next(step for step in classifier["steps"] if step.get("id") == "classify")
        self.assertEqual(step["env"], {"PR_BASE_SHA": "${{ github.event.pull_request.base.sha }}"})
        upload = classifier["steps"][-1]
        self.assertEqual(upload["if"], "always()")
        self.assertEqual(upload["with"]["path"], "${{ runner.temp }}/ci-routing.json")

    def test_security_and_schema_test_matrix_is_preserved(self):
        matrix = self.jobs["test"]
        self.assertEqual(matrix["needs"], "classify-changes")
        self.assertEqual(
            matrix["strategy"]["matrix"]["test-type"], ["mcp-plugins", "python-tests", "validation-scripts"]
        )
        steps = {step.get("name"): step for step in matrix["steps"]}
        protected = {
            "Test signed evidence payload binding": ("mcp-plugins", "ci/emit-evidence/*.test.mjs"),
            "Verify Snowflake collector bundle integrity": ("python-tests", "sync_bundled_collectors.py --check"),
            "Run Freshie hermetic publication cycle": ("python-tests", "not result.skipped"),
            "Run validation with universal validator": (
                "validation-scripts",
                "scripts/validate-skills-schema.py --standard",
            ),
        }
        for name, (lane, command) in protected.items():
            with self.subTest(step=name):
                self.assertEqual(steps[name]["if"], f"matrix.test-type == '{lane}'")
                self.assertIn(command, steps[name]["run"])

    def test_mcp_build_routes_only_the_exact_lightweight_lane_and_propagates_failure(self):
        step = next(s for s in self.jobs["test"]["steps"] if s.get("name") == "Build MCP plugins")
        self.assertEqual(step["env"], {"CI_LANE": "${{ needs.classify-changes.outputs.lane }}"})
        with tempfile.TemporaryDirectory(prefix="ci-build-routing-") as directory:
            root = Path(directory)
            trace = root / "trace"
            command = root / "pnpm"
            command.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$TRACE"\nexit "${BUILD_EXIT:-0}"\n')
            command.chmod(0o755)
            for lane in ("lightweight", "full", "", "unknown", None):
                for code in (0, 23):
                    with self.subTest(lane=lane, exit_code=code):
                        env = {
                            **os.environ,
                            "PATH": f"{root}:{os.environ['PATH']}",
                            "TRACE": str(trace),
                            "BUILD_EXIT": str(code),
                        }
                        env.pop("CI_LANE", None)
                        if lane is not None:
                            env["CI_LANE"] = lane
                        result = subprocess.run(["bash", "-c", step["run"]], env=env, text=True, capture_output=True)
                        self.assertEqual(result.returncode, code, result.stderr)
                        expected = ["--filter", "./plugins/mcp/*...", "build"] if lane == "lightweight" else ["build"]
                        self.assertEqual(trace.read_text().splitlines(), expected)

    def test_security_and_funding_steps_remain_unconditional(self):
        protected = {
            "marketplace-validation": {
                "Check CSP inline-script inventory (dist)",
                "Validate Cowork Security",
                "Validate Cowork Manifest Drift",
            },
            "validate": {
                "Enforce the safety ratchet",
                "Verify audit-harness integrity",
                "Test CI routing policy",
                "Validate funding metadata",
            },
        }
        for job, names in protected.items():
            steps = {step.get("name"): step for step in self.jobs[job]["steps"]}
            for name in names:
                with self.subTest(job=job, step=name):
                    self.assertIn(name, steps)
                    self.assertNotIn("if", steps[name])
        names = [step.get("name") for step in self.jobs["validate"]["steps"]]
        self.assertLess(names.index("Enforce the safety ratchet"), names.index("Test CI routing policy"))
        self.assertLess(names.index("Enforce the safety ratchet"), names.index("Validate funding metadata"))

    def test_python_provisioning_preserves_full_fallback_and_fails_on_missing_fixture_dependencies(self):
        step = next(s for s in self.jobs["test"]["steps"] if s.get("name") == "Install Python test dependencies")
        self.assertEqual(step["env"], {"CI_LANE": "${{ needs.classify-changes.outputs.lane }}"})
        with tempfile.TemporaryDirectory(prefix="ci-python-routing-") as directory:
            root = Path(directory)
            trace = root / "trace"
            (root / "requirements.txt").touch()
            scripts = {
                "python": "#!/bin/bash\nexit 0\n",
                "find": '#!/bin/bash\nprintf "%s\\n" plugins/full-runtime/requirements.txt plugins/optional-runtime/requirements.txt\n',
                "pip": '#!/bin/bash\nprintf "%s\\n" "$@" >> "$TRACE"\nif [ -n "${FAIL_FIXTURE:-}" ] && [[ "$*" == *"$FAIL_FIXTURE"* ]]; then exit 23; fi\nif [[ "$*" == *optional-runtime* ]]; then exit 24; fi\n',
            }
            for name, content in scripts.items():
                command = root / name
                command.write_text(content)
                command.chmod(0o755)
            for lane in ("lightweight", "full", "", "unknown", None):
                with self.subTest(lane=lane):
                    trace.write_text("")
                    env = {**os.environ, "PATH": f"{root}:{os.environ['PATH']}", "TRACE": str(trace)}
                    env.pop("CI_LANE", None)
                    if lane is not None:
                        env["CI_LANE"] = lane
                    result = subprocess.run(
                        ["bash", "-c", step["run"]], cwd=root, env=env, text=True, capture_output=True
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    installed = trace.read_text().splitlines()
                    self.assertIn("requirements.txt", installed)
                    for tool in ("pytest", "pytest-cov", "pytest-asyncio", "pyyaml", "jsonschema"):
                        self.assertIn(tool, installed)
                    fixtures = {
                        "plugins/mcp/lumera-agent-memory/requirements.txt",
                        "plugins/security/penetration-tester/skills/performing-penetration-testing/scripts/requirements.txt",
                        "plugins/crypto/trading-strategy-backtester/requirements.txt",
                        "plugins/crypto/crypto-news-aggregator/requirements.txt",
                    }
                    actual = {arg for arg in installed if arg.startswith("plugins/")}
                    self.assertEqual(
                        actual,
                        fixtures
                        if lane == "lightweight"
                        else fixtures
                        | {"plugins/full-runtime/requirements.txt", "plugins/optional-runtime/requirements.txt"},
                    )
                    if lane != "lightweight":
                        self.assertLess(
                            installed.index("plugins/optional-runtime/requirements.txt"),
                            installed.index("plugins/mcp/lumera-agent-memory/requirements.txt"),
                        )
            for lane, fixture in ((lane, fixture) for lane in ("lightweight", "full") for fixture in sorted(fixtures)):
                with self.subTest(failed_fixture_lane=lane, fixture=fixture):
                    trace.write_text("")
                    env.update(CI_LANE=lane, FAIL_FIXTURE=fixture)
                    result = subprocess.run(
                        ["bash", "-c", step["run"]], cwd=root, env=env, text=True, capture_output=True
                    )
                    self.assertEqual(result.returncode, 23, result.stderr)
                    self.assertNotIn("pyyaml", trace.read_text().splitlines())


class TrustedClassifierExecutionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ci-routing-workflow-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.runtime = self.root / "runner"
        self.runtime.mkdir()
        self.policy = self.repo / "scripts/ci/fastlane.py"
        self.policy.parent.mkdir(parents=True)
        self.output = self.root / "outputs"
        self.event = self.root / "event.json"
        self.event.write_text("{}")
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "CI routing fixture")
        self.git("config", "user.email", "ci-routing@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.shell = next(
            step["run"] for step in workflow()["jobs"]["classify-changes"]["steps"] if step.get("id") == "classify"
        )

    def git(self, *args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=self.repo, text=True, stderr=subprocess.PIPE).strip()

    def commit(self, message: str) -> str:
        self.git("add", ".")
        self.git("commit", "-qm", message)
        return self.git("rev-parse", "HEAD")

    def prepare(self, *, base_policy: bool = True, malicious_head: bool = True) -> str:
        (self.repo / "CODE_OF_CONDUCT.md").write_text("# Community\n")
        if base_policy:
            self.policy.write_text((ROOT / "scripts/ci/fastlane.py").read_text())
        base = self.commit("base")
        self.git("checkout", "-qb", "candidate")
        if malicious_head:
            self.policy.write_text(
                "from pathlib import Path\nimport os\n"
                "Path('head-policy-executed').touch()\n"
                "Path(os.environ['GITHUB_OUTPUT']).write_text('schema=1\\nlane=lightweight\\n')\n"
            )
        (self.repo / "CODE_OF_CONDUCT.md").write_text("# Community\nBe kind.\n")
        head = self.commit("candidate")
        self.git("checkout", "-q", "main")
        self.git("merge", "--no-ff", "-qm", "integration", "candidate")
        self.event.write_text(json.dumps({"pull_request": {"base": {"sha": base}, "head": {"sha": head}}}))
        return base

    def execute(self, base: str, *, event_name: str = "pull_request") -> subprocess.CompletedProcess:
        env = {
            **os.environ,
            "PR_BASE_SHA": base,
            "GITHUB_EVENT_NAME": event_name,
            "GITHUB_EVENT_PATH": str(self.event),
            "GITHUB_SHA": self.git("rev-parse", "HEAD"),
            "GITHUB_OUTPUT": str(self.output),
            "RUNNER_TEMP": str(self.runtime),
        }
        return subprocess.run(
            ["bash", "-c", self.shell], cwd=self.repo, env=env, text=True, capture_output=True, timeout=30
        )

    def assert_full(self, result: subprocess.CompletedProcess):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.output.read_text(), "schema=1\nlane=full\n")
        receipt = json.loads((self.runtime / "ci-routing.json").read_text())
        self.assertEqual(receipt["lane"], "full")
        self.assertFalse((self.repo / "head-policy-executed").exists())
        return receipt

    def test_real_base_policy_overrules_malicious_head_policy(self):
        base = self.prepare()
        receipt = self.assert_full(self.execute(base))
        self.assertEqual(receipt["reason"], "non-allowlisted-change-or-empty-diff")
        self.assertEqual(
            (self.runtime / "trusted-fastlane.py").read_text(),
            self.git("show", f"{base}:scripts/ci/fastlane.py") + "\n",
        )

    def test_trusted_policy_can_route_a_proven_safe_merge(self):
        base = self.prepare(malicious_head=False)
        result = self.execute(base)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.output.read_text(), "schema=1\nlane=lightweight\n")
        receipt = json.loads((self.runtime / "ci-routing.json").read_text())
        self.assertEqual(receipt["reason"], "reviewed-paths-only")
        self.assertEqual([change["path"] for change in receipt["authored"]], ["CODE_OF_CONDUCT.md"])

    def test_first_install_bootstraps_full_without_executing_head(self):
        base = self.prepare(base_policy=False)
        receipt = self.assert_full(self.execute(base))
        self.assertEqual(receipt["reason"], "trusted-base-policy-not-installed")

    def test_invalid_or_unavailable_base_fails_without_outputs(self):
        self.prepare()
        for base in ("", "main", "f" * 40, "$(touch injected)"):
            with self.subTest(base=base):
                result = self.execute(base)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.output.exists())
                self.assertFalse((self.repo / "injected").exists())
                self.assertFalse((self.repo / "head-policy-executed").exists())

    def test_malformed_event_cannot_select_lightweight(self):
        base = self.prepare(malicious_head=False)
        self.event.write_text("not JSON")
        receipt = self.assert_full(self.execute(base))
        self.assertEqual(receipt["reason"], "unproven-comparison")

    def test_push_and_manual_runs_use_full_lane(self):
        base = self.prepare(malicious_head=False)
        for event in ("push", "workflow_dispatch"):
            with self.subTest(event=event):
                self.output.unlink(missing_ok=True)
                receipt = self.assert_full(self.execute(base, event_name=event))
                self.assertEqual(receipt["reason"], "non-pr-event")


if __name__ == "__main__":
    unittest.main()
