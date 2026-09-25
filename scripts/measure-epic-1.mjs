#!/usr/bin/env node

/**
 * Deterministic measurement harness for blueprint 727, Epic 1.
 *
 * The package-level `measure:e1:check` command runs the resolver and harness
 * fixture suites before invoking this module's artifact drift check.
 *
 * ORDERING MATTERS, and getting it wrong looks like a broken generator.
 * `--check` builds its report from the GIT INDEX, not from the worktree, while
 * generation WRITES to the worktree. So this sequence never converges:
 *
 *     edit inputs -> generate -> stage everything -> --check      (DRIFT)
 *
 * because the report was measured against an index that did not yet contain the
 * edits. The correct order stages the inputs first:
 *
 *     edit inputs -> stage inputs -> generate -> stage artifact -> --check  (OK)
 *
 * A regeneration run before the inputs are staged measures one state and
 * verifies another, which reads as non-determinism and is not.
 */

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, extname, isAbsolute, join, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

import { buildExtendedScorecardRows } from './measure-epic-1-scorecard.mjs';

export const ARTIFACT_PATH = '000-docs/742-RA-DATA-epic-1-scorecard.json';
export const REQUIRED_README_METRIC_WRITER = 'scripts/generate-readme-toc.mjs';
const SCRIPT_PATH = 'scripts/measure-epic-1.mjs';
export const MEASUREMENT_INPUT_PATHS = [
  SCRIPT_PATH,
  'scripts/measure-epic-1-scorecard.mjs',
  'scripts/dead-domain-policy.mjs',
  'scripts/generated-artifact-registry.mjs',
  'scripts/corpus-resolver.mjs',
  'scripts/plugin-provenance.mjs',
  'scripts/check-doc-authority.mjs',
];
const SCRIPT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const GRADES = new Set(['A', 'B', 'C', 'D', 'F']);
const CATALOGS = new Set([
  '.claude-plugin/marketplace.extended.json',
  '.claude-plugin/marketplace.json',
]);
const SIGNATURES = {
  '.pdf': [Buffer.from('%PDF-')],
  '.png': [Buffer.from('89504e470d0a1a0a', 'hex')],
  '.ttf': [Buffer.from('00010000', 'hex'), Buffer.from('true')],
  '.zip': [
    Buffer.from('504b0304', 'hex'),
    Buffer.from('504b0506', 'hex'),
    Buffer.from('504b0708', 'hex'),
  ],
};

function fail(message) {
  throw new Error(`epic-1-measurement: ${message}`);
}

function posix(path) {
  return path.split(sep).join('/');
}

function file(root, path) {
  const target = resolve(root, path);
  const rel = relative(root, target);
  if (rel.startsWith('..') || isAbsolute(rel)) fail(`path escapes repository: ${path}`);
  return target;
}

function text(root, path) {
  try {
    return readFileSync(file(root, path), 'utf8');
  } catch (error) {
    fail(`cannot read ${path}: ${error.message}`);
  }
}

function json(root, path) {
  try {
    return JSON.parse(text(root, path));
  } catch (error) {
    if (error.message.startsWith('epic-1-measurement:')) throw error;
    fail(`malformed JSON in ${path}: ${error.message}`);
  }
}

function run(root, command, args) {
  const result = spawnSync(command, args, {
    cwd: root,
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
  });
  if (result.error) fail(`${command} failed to start: ${result.error.message}`);
  return result;
}

const HERMETIC_CONTRACT_CACHE = new Map();

export function inspectFreshieHermeticTest(root) {
  const testPath = file(resolve(root), 'tests/test_freshie_hermetic_cycle.py');
  if (!existsSync(testPath)) {
    return {
      isolated_dolt_identity: false,
      no_dead_code: false,
      parsed: false,
      reachable_fake_remote_push: false,
      reachable_full_cycle: false,
      reachable_server_refusal: false,
      runner_fail_closed: false,
    };
  }
  const source = readFileSync(testPath, 'utf8');
  const digest = createHash('sha256').update(source).digest('hex');
  if (HERMETIC_CONTRACT_CACHE.has(digest)) return HERMETIC_CONTRACT_CACHE.get(digest);
  const probe = String.raw`
import ast
import json
import sys

result = {
    "parsed": False,
    "no_dead_code": False,
    "reachable_full_cycle": False,
    "reachable_fake_remote_push": False,
    "reachable_server_refusal": False,
    "runner_fail_closed": False,
    "isolated_dolt_identity": False,
}

def call_name(call):
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    return func.id if isinstance(func, ast.Name) else ""

def text_tokens(node):
    values = []
    for item in ast.walk(node):
        if isinstance(item, ast.Constant) and isinstance(item.value, str):
            values.append(item.value)
        elif isinstance(item, ast.Name):
            values.append(item.id)
    return values

def required_name(call, name):
    return any(
        isinstance(item, ast.Call)
        and isinstance(item.func, ast.Name)
        and item.func.id == "str"
        and item.args
        and isinstance(item.args[0], ast.Name)
        and item.args[0].id == name
        for item in ast.walk(call)
    )

try:
    tree = ast.parse(sys.stdin.read())
    result["parsed"] = True
    klass = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "HermeticFreshieCycleTests"
    )
    methods = {
        node.name: node for node in klass.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    test = methods["test_full_cycle_uses_only_scratch_state_and_refuses_live_server"]
    runner = methods["_run"]
    setup = methods["setUp"]
    synchronous_methods = all(
        isinstance(method, ast.FunctionDef) for method in (test, runner, setup)
    )

    conditional = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Match, ast.comprehension)
    def parent_map(method):
        parents = {}
        for parent in ast.walk(method):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent
        return parents

    def reachable(method, node, parents):
        current = node
        while current is not method:
            current = parents.get(current)
            if current is None:
                return False
            if isinstance(current, conditional):
                return False
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and current is not method:
                return False
        return True

    test_parents = parent_map(test)
    calls = [
        node for node in ast.walk(test)
        if isinstance(node, ast.Call) and reachable(test, node, test_parents)
    ]
    stages = {name: [] for name in ("REBUILD", "VALIDATE", "SYNC", "PROMOTE")}
    for call in calls:
        if call_name(call) == "_run":
            for name in stages:
                if required_name(call, name):
                    stages[name].append(call)

    ordered = all(stages[name] for name in stages)
    if ordered:
        ordered = (
            stages["REBUILD"][0].lineno
            < stages["VALIDATE"][0].lineno
            < stages["SYNC"][0].lineno
            < stages["PROMOTE"][0].lineno
        )
    forbidden = any(
        isinstance(node, (ast.Pass, ast.Return, ast.Raise, ast.Yield, ast.YieldFrom, ast.Await))
        for node in ast.walk(test)
    ) or any(
        (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Constant)
            and not bool(node.test.value)
        )
        for method in (test, setup, runner) for node in ast.walk(method)
    )
    skipped = bool(test.decorator_list) or any(
        isinstance(node, ast.Call) and call_name(node).lower().startswith("skip")
        for node in ast.walk(test)
    )
    lifecycle_skip = any(
        (
            isinstance(node, ast.Call)
            and call_name(node).lower().startswith("skip")
        )
        or (
            isinstance(node, (ast.Name, ast.Attribute))
            and (
                (node.id if isinstance(node, ast.Name) else node.attr).lower()
                in {"skiptest", "__unittest_skip__"}
            )
        )
        or (
            isinstance(node, ast.Constant)
            and node.value == "__unittest_skip__"
        )
        for node in ast.walk(tree)
    )
    governed_methods = {
        "setUpClass",
        "setUp",
        "_run",
        "test_full_cycle_uses_only_scratch_state_and_refuses_live_server",
        "tearDown",
        "tearDownClass",
    }
    mutation_nodes = (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)
    def references_governed_method(node):
        return any(
            (
                isinstance(item, ast.Attribute)
                and item.attr in governed_methods
            )
            or (
                isinstance(item, ast.Name)
                and item.id in governed_methods
            )
            or (
                isinstance(item, ast.Constant)
                and item.value in governed_methods
            )
            for item in ast.walk(node)
        )

    def assignment_targets(node):
        if isinstance(node, ast.Assign):
            return node.targets
        if isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            return [node.target]
        if isinstance(node, ast.Delete):
            return node.targets
        return []

    lifecycle_mutation = any(
        isinstance(node, mutation_nodes)
        and any(references_governed_method(target) for target in assignment_targets(node))
        for node in ast.walk(tree)
    ) or any(
        isinstance(node, ast.Call)
        and call_name(node).lower()
        in {"setattr", "__setattr__", "delattr", "__delattr__", "patch", "object"}
        and (
            references_governed_method(node)
            or call_name(node).lower() in {"setattr", "__setattr__", "delattr", "__delattr__"}
        )
        for node in ast.walk(tree)
    ) or any(
        isinstance(node, ast.Call)
        and any(
            isinstance(item, ast.Constant) and item.value in governed_methods
            for item in ast.walk(node)
        )
        for node in ast.walk(tree)
    )
    result["no_dead_code"] = (
        synchronous_methods
        and not forbidden
        and not skipped
        and not lifecycle_skip
        and not lifecycle_mutation
    )
    result["reachable_full_cycle"] = ordered and len(stages["SYNC"]) >= 2

    result["reachable_fake_remote_push"] = any(
        call_name(call) == "_run"
        and {"dolt", "push"}.issubset(set(text_tokens(call)))
        for call in calls
    ) and any("file://" in token for call in calls for token in text_tokens(call))

    refusal_calls = [
        call for call in stages["SYNC"]
        if any(
            keyword.arg == "expected"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value == 1
            for keyword in call.keywords
        )
    ]
    server_calls = [
        call for call in calls
        if call_name(call) == "Popen"
        and {"dolt", "sql-server"}.issubset(set(text_tokens(call)))
    ]
    blocked_assertions = [
        call for call in calls
        if call_name(call) == "assertFalse"
        and "blocked-grades.csv" in text_tokens(call)
    ]
    result["reachable_server_refusal"] = bool(
        refusal_calls and server_calls and blocked_assertions
        and server_calls[0].lineno < refusal_calls[0].lineno < blocked_assertions[0].lineno
    )

    result["runner_fail_closed"] = any(
        isinstance(node, ast.If)
        and any(
            isinstance(part, ast.Attribute) and part.attr == "returncode"
            for part in ast.walk(node.test)
        )
        and any(
            isinstance(part, ast.Call) and call_name(part) == "fail"
            for statement in node.body for part in ast.walk(statement)
        )
        for node in runner.body
    )

    setup_parents = parent_map(setup)
    setup_calls = [
        node for node in ast.walk(setup)
        if isinstance(node, ast.Call) and reachable(setup, node, setup_parents)
    ]
    setup_nodes = [
        node for node in ast.walk(setup)
        if reachable(setup, node, setup_parents)
    ]
    setup_tokens = [token for node in setup_nodes for token in text_tokens(node)]
    result["isolated_dolt_identity"] = (
        "HOME" in setup_tokens
        and "dolt-home" in setup_tokens
        and sum(
            1 for call in setup_calls
            if {"dolt", "config", "--global", "--add"}.issubset(set(text_tokens(call)))
        ) >= 2
    )
except (SyntaxError, StopIteration, KeyError):
    pass

print(json.dumps(result, sort_keys=True))
`;
  const observed = spawnSync('python3', ['-c', probe], {
    cwd: resolve(root),
    encoding: 'utf8',
    input: source,
    maxBuffer: 1024 * 1024,
  });
  if (observed.error || observed.status !== 0) {
    fail(`Freshie hermetic contract probe failed: ${observed.error?.message ?? observed.stderr}`);
  }
  let result;
  try {
    result = JSON.parse(observed.stdout);
  } catch (error) {
    fail(`Freshie hermetic contract probe returned malformed JSON: ${error.message}`);
  }
  HERMETIC_CONTRACT_CACHE.set(digest, result);
  return result;
}

export function trackedPaths(root) {
  const treeResult = run(root, 'git', ['write-tree']);
  if (treeResult.status !== 0) fail(`git write-tree failed: ${treeResult.stderr.trim()}`);
  const tree = treeResult.stdout.trim();
  if (!/^[0-9a-f]{40,64}$/.test(tree)) fail('git write-tree returned an invalid object id');
  const result = run(root, 'git', ['ls-tree', '-r', '-z', '--name-only', tree]);
  if (result.status !== 0) fail(`git tree inventory failed: ${result.stderr.trim()}`);
  const paths = result.stdout.split('\0').filter(Boolean).map(posix).sort();
  if (paths.length === 0) fail('git inventory is empty');
  return paths;
}

export function matchesSignature(extension, bytes) {
  const signatures = SIGNATURES[extension.toLowerCase()];
  if (!signatures) fail(`unknown governed binary extension: ${extension}`);
  return signatures.some((signature) => bytes.subarray(0, signature.length).equals(signature));
}

export function parseSkillRows(value, options = {}) {
  if (!Array.isArray(value)) fail('validator JSON must be an array');
  const rows = value.filter((entry) => entry && typeof entry.path === 'string');
  const advisories = value.filter((entry) => !entry || typeof entry.path !== 'string');
  if (options.requireKernelShadow) {
    if (
      advisories.length !== 1 ||
      !advisories[0]?.kernel_shadow ||
      typeof advisories[0].kernel_shadow !== 'object'
    ) {
      fail('validator JSON must end with exactly one kernel_shadow advisory');
    }
  } else if (advisories.some((entry) => !entry?.kernel_shadow)) {
    fail('validator JSON contains an unknown non-row record');
  }
  if (rows.length === 0) fail('validator JSON contains no SKILL.md rows');
  const seen = new Set();
  const grades = Object.fromEntries([...GRADES].map((grade) => [grade, 0]));
  let errors = 0;
  let errorFiles = 0;
  let abFailing = 0;
  let aFailing = 0;
  let bFailing = 0;
  let aErrors = 0;
  let abErrors = 0;
  for (const row of rows) {
    if (
      !row.path.endsWith('/SKILL.md') ||
      seen.has(row.path) ||
      !GRADES.has(row.grade) ||
      !Number.isSafeInteger(row.errors) ||
      row.errors < 0
    ) {
      fail(`invalid validator row: ${row.path}`);
    }
    seen.add(row.path);
    grades[row.grade] += 1;
    errors += row.errors;
    if (row.errors > 0) errorFiles += 1;
    if ((row.grade === 'A' || row.grade === 'B') && row.errors > 0) {
      abFailing += 1;
      abErrors += row.errors;
      if (row.grade === 'A') {
        aFailing += 1;
        aErrors += row.errors;
      } else {
        bFailing += 1;
      }
    }
  }
  if (Object.values(grades).reduce((sum, count) => sum + count, 0) !== rows.length) {
    fail('grade totals do not equal graded rows');
  }
  return {
    ab_error_total: abErrors,
    ab_failing: abFailing,
    a_error_total: aErrors,
    a_failing: aFailing,
    b_failing: bFailing,
    error_files: errorFiles,
    error_total: errors,
    grade_distribution: grades,
    rows: rows.length,
  };
}

function summaryValue(output, label, valuePattern = '(\\d+)') {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const matches = [
    ...output.matchAll(new RegExp(`^[^\\n]*${escaped}:\\s*${valuePattern}\\s*$`, 'gm')),
  ];
  if (matches.length !== 1) fail(`validator summary requires exactly one ${label}`);
  return Number(matches[0][1]);
}

export function parseTerminalSummary(evidence, lane) {
  const output = typeof evidence === 'string' ? evidence : evidence?.output;
  const status = typeof evidence === 'string' ? undefined : evidence?.status;
  if (typeof output !== 'string') fail(`missing ${lane} terminal summary`);
  const totalFiles = summaryValue(output, 'Total files');
  const verdicts = [
    ...output.matchAll(/^.*Validation FAILED with\s+(\d+) errors .*$/gm),
    ...output.matchAll(/^.*Validation PASSED with\s+(\d+) warnings .*$/gm),
    ...output.matchAll(/^.*All skills fully compliant! .*$/gm),
  ];
  if (verdicts.length !== 1) fail('validator summary requires exactly one terminal result');
  const failure = output.match(/^.*Validation FAILED with\s+(\d+) errors .*$/m);
  const errors = failure ? Number(failure[1]) : 0;
  if (failure && errors === 0) fail('validator cannot fail with zero errors');
  const expectedStatus = failure ? 1 : 0;
  if (status !== undefined && status !== expectedStatus) {
    fail(`validator ${lane} exit ${status} contradicts its terminal result`);
  }
  if (lane === 'marketplace') {
    const skills = summaryValue(output, 'Skills validated');
    const commands = summaryValue(output, 'Commands validated');
    const agents = summaryValue(output, 'Agents validated');
    // 4.0.2 (blueprint E4.12): the validator's denominator now includes the
    // plugin-manifest lane, printed as its own summary line. Optional so the
    // harness also parses pre-4.0.2 output shapes in fixtures.
    const manifests = /Plugin manifests validated:/.test(output)
      ? summaryValue(output, 'Plugin manifests validated')
      : 0;
    if (skills + commands + agents + manifests !== totalFiles) {
      fail('marketplace terminal denominator arithmetic is inconsistent');
    }
    return {
      error_total_all_validated_surfaces: errors,
      fully_compliant_surfaces: summaryValue(output, 'Fully compliant'),
      terminal_denominator: {
        agents,
        commands,
        files: totalFiles,
        label: 'skills_plus_commands_plus_agents_plus_plugin_manifests',
        plugin_manifests: manifests,
        skills,
      },
      validator_reported_mixed_denominator_percent: summaryValue(
        output,
        'Compliance rate',
        '([\\d.]+)%',
      ),
    };
  }
  if (lane !== 'agents') fail(`unknown terminal lane: ${lane}`);
  const agents = summaryValue(output, 'Agents validated');
  // 4.0.2 (E4.12): the plugin-manifest lane joins the denominator in every
  // invocation that validates manifests, including --agents-only runs.
  const agentLaneManifests = /Plugin manifests validated:/.test(output)
    ? summaryValue(output, 'Plugin manifests validated')
    : 0;
  if (agents + agentLaneManifests !== totalFiles)
    fail('agent terminal denominator arithmetic is inconsistent');
  return {
    error_total_all_validated_surfaces: errors,
    fully_compliant_surfaces: summaryValue(output, 'Fully compliant'),
    terminal_denominator: {
      agents,
      files: totalFiles,
      label: 'agents_plus_plugin_manifests',
      plugin_manifests: agentLaneManifests,
    },
    validator_reported_mixed_denominator_percent: summaryValue(
      output,
      'Compliance rate',
      '([\\d.]+)%',
    ),
  };
}

function validatorEvidence(root) {
  const invocations = [
    ['skills', ['scripts/validate-skills-schema.py', '--marketplace', '--skills-only', '--json']],
    ['marketplace', ['scripts/validate-skills-schema.py', '--marketplace']],
    ['agents', ['scripts/validate-skills-schema.py', '--standard', '--agents-only']],
  ];
  const evidence = {};
  for (const [name, args] of invocations) {
    const result = run(root, 'python3', args);
    if (![0, 1].includes(result.status)) fail(`validator ${name} exited ${result.status}`);
    if (/VALIDATION SUMMARY|Validation (?:FAILED|PASSED)/.test(result.stderr)) {
      fail(`validator ${name} emitted protocol text on stderr`);
    }
    if (name === 'skills') {
      try {
        evidence.skills = JSON.parse(result.stdout);
        evidence.skillsStatus = result.status;
        evidence.requireKernelShadow = true;
      } catch (error) {
        fail(`malformed validator JSON: ${error.message}`);
      }
    } else {
      evidence[name] = { output: result.stdout, status: result.status };
    }
  }
  return evidence;
}

export function withIndexSnapshot(root, callback) {
  const repository = resolve(root);
  const snapshot = mkdtempSync(join(tmpdir(), 'epic-1-measurement-index-'));
  const archive = `${snapshot}.tar`;
  try {
    const treeResult = run(repository, 'git', ['write-tree']);
    if (treeResult.status !== 0) fail(`git write-tree failed: ${treeResult.stderr.trim()}`);
    const tree = treeResult.stdout.trim();
    if (!/^[0-9a-f]{40,64}$/.test(tree)) fail('git write-tree returned an invalid object id');

    const inventoryResult = run(repository, 'git', ['ls-tree', '-r', '-z', '--name-only', tree]);
    if (inventoryResult.status !== 0) {
      fail(`git tree inventory failed: ${inventoryResult.stderr.trim()}`);
    }
    const paths = inventoryResult.stdout.split('\0').filter(Boolean).map(posix).sort();
    if (paths.length === 0) fail('git tree inventory is empty');

    const archiveResult = run(repository, 'git', [
      'archive',
      '--format=tar',
      `--output=${archive}`,
      tree,
    ]);
    if (archiveResult.status !== 0) fail(`cannot archive Git tree: ${archiveResult.stderr.trim()}`);
    const extractResult = run(repository, 'tar', ['-xf', archive, '-C', snapshot]);
    if (extractResult.status !== 0) fail(`cannot extract Git tree: ${extractResult.stderr.trim()}`);
    return callback({ paths, root: snapshot, tree });
  } finally {
    rmSync(archive, { force: true });
    rmSync(snapshot, { force: true, recursive: true });
  }
}

function binaryAssets(root, paths) {
  const candidates = paths.filter((path) => Object.hasOwn(SIGNATURES, extname(path).toLowerCase()));
  const mismatches = [];
  for (const path of candidates) {
    let bytes;
    try {
      bytes = readFileSync(file(root, path));
    } catch (error) {
      fail(`cannot read binary candidate ${path}: ${error.message}`);
    }
    if (!matchesSignature(extname(path), bytes)) mismatches.push(path);
  }
  return { candidates, mismatches };
}

function promotionDetector(root, mismatches) {
  const sourcePath = 'freshie/scripts/promote-to-curated.py';
  const source = text(root, sourcePath);
  const declaredMagic = /CONTENT_TYPE_STRATEGY\s*=\s*["']magic_bytes["']/.test(source);
  const legacyNul = /b["']\\0["']\s+in\s+fh\.read\(8192\)/.test(source);
  if (!declaredMagic && !legacyNul) fail('unknown promotion binary-detector shape');

  // Execute the indexed detector rather than inferring enforcement from source
  // tokens. The fixed probes catch dead-code markers and the original prefix-only
  // failure mode even when the live corpus has already been corrected to zero
  // extension mismatches.
  const probe = String.raw`
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

module_path = Path(sys.argv[1])
repository = Path(sys.argv[2])
mismatches = json.loads(sys.argv[3])
spec = importlib.util.spec_from_file_location("curated_promotion_probe", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
content_error = getattr(module, "ContentInspectionError", None)
content_errors = (content_error,) if isinstance(content_error, type) else ()

def outcome(path):
    try:
        value = module._is_binary(path)
    except content_errors:
        return "refused"
    except Exception as exc:
        return "error:" + type(exc).__name__
    return "excluded" if value else "mirrorable"

observed = {"excluded": [], "missed": [], "refused": []}
for relative_path in mismatches:
    result = outcome(repository / relative_path)
    if result == "excluded":
        observed["excluded"].append(relative_path)
    elif result == "refused":
        observed["refused"].append(relative_path)
    else:
        observed["missed"].append(relative_path)

with tempfile.TemporaryDirectory(prefix="epic-1-content-probe-") as directory:
    root = Path(directory)
    def fixture(name, data):
        target = root / name
        target.write_bytes(data)
        return target

    checks = {
        "genuine_png": outcome(fixture("genuine.png", bytes.fromhex("89504e470d0a1a0a") + b"fixture")),
        "counterfeit_png": outcome(fixture("counterfeit.png", b"plain text placeholder\n")),
        "invalid_utf8": outcome(fixture("invalid.dat", b"plain-prefix\xff\xfe")),
        "late_nul": outcome(fixture("late.dat", b"a" * (64 * 1024) + b"\x00")),
        "wrong_extension": outcome(fixture("image.bin", bytes.fromhex("89504e470d0a1a0a") + b"fixture")),
        "extensionless_elf": outcome(fixture("tool", bytes.fromhex("7f454c46") + b"fixture")),
        "utf8_text": outcome(fixture("notes.md", "# héllo — ✅\n".encode("utf-8"))),
    }

payload = {
    **observed,
    "fixture_checks": checks,
    "prefix_bytes": module._INSPECTION_CHUNK_BYTES,
    "strategy": getattr(module, "CONTENT_TYPE_STRATEGY", "nul_prefix"),
}
print(json.dumps(payload, sort_keys=True))
`;
  const result = run(root, 'python3', [
    '-c',
    probe,
    file(root, sourcePath),
    root,
    JSON.stringify(mismatches),
  ]);
  if (result.status !== 0) {
    fail(`promotion detector probe failed: ${(result.stderr || result.stdout).trim()}`);
  }
  let observed;
  try {
    observed = JSON.parse(result.stdout);
  } catch (error) {
    fail(`promotion detector emitted malformed JSON: ${error.message}`);
  }
  const expectedChecks = {
    counterfeit_png: 'refused',
    extensionless_elf: 'excluded',
    genuine_png: 'excluded',
    invalid_utf8: 'refused',
    late_nul: 'refused',
    utf8_text: 'mirrorable',
    wrong_extension: 'refused',
  };
  return {
    ...observed,
    fixture_passed:
      stableJson(observed.fixture_checks) === stableJson(expectedChecks) &&
      observed.strategy === (declaredMagic ? 'magic_bytes' : 'nul_prefix'),
  };
}

function catalogMeasurement(root, paths) {
  const catalog = json(root, '.claude-plugin/marketplace.extended.json');
  if (!Array.isArray(catalog.plugins)) fail('catalog plugins must be an array');
  const names = catalog.plugins.map((plugin, index) => {
    if (!plugin || typeof plugin.name !== 'string' || !plugin.name)
      fail(`catalog plugin ${index} lacks name`);
    return plugin.name;
  });
  const counts = new Map();
  for (const name of names) counts.set(name, (counts.get(name) ?? 0) + 1);
  const duplicateNames = [...counts]
    .filter(([, count]) => count > 1)
    .map(([name, count]) => ({ count, name }))
    .sort((a, b) => a.name.localeCompare(b.name));
  const shadows = paths.filter(
    (path) =>
      path.startsWith('.claude-plugin/marketplace') &&
      path.includes('.json') &&
      !CATALOGS.has(path),
  );
  return { duplicateNames, entries: names.length, names: counts.size, shadows };
}

const ROW_SOURCES = {
  1: 'git write-tree + git ls-tree over the exact index tree',
  2: '.claude-plugin/marketplace.extended.json',
  3: 'git tree inventory under .claude-plugin/',
  4: 'scripts/validate-skills-schema.py JSON and terminal protocols',
  11: 'Git tree bytes matched against the per-extension signature registry',
  12: 'executed freshie/scripts/promote-to-curated.py predicate over row 11 and fixed red probes',
};

function row(dimension, cohort, values, id, targetStatus = 'informational') {
  const source = ROW_SOURCES[id];
  if (!source) fail(`row ${id} lacks a source identifier`);
  return {
    cohort,
    dimension,
    reproduce: `pnpm run measure:e1 --row=${id} --stdout`,
    source,
    status: 'measured',
    target_status: targetStatus,
    values,
  };
}

export function assertReadmeMetricWriterContract(readmeWriterRow) {
  const writers = readmeWriterRow?.values?.writers;
  if (
    !Array.isArray(writers) ||
    writers.length !== 1 ||
    writers[0] !== REQUIRED_README_METRIC_WRITER
  ) {
    const observed = Array.isArray(writers) ? writers.join(', ') || '(none)' : '(malformed)';
    fail(
      `README metric writer contract requires only ${REQUIRED_README_METRIC_WRITER}; observed ${observed}`,
    );
  }
}

export function buildReport(root, suppliedEvidence, suppliedPaths) {
  const repository = resolve(root);
  const paths = suppliedPaths ?? trackedPaths(repository);
  const evidence = suppliedEvidence ?? validatorEvidence(repository);
  const skills = parseSkillRows(evidence.skills, {
    requireKernelShadow: evidence.requireKernelShadow === true,
  });
  if (evidence.skillsStatus !== undefined && evidence.skillsStatus !== 0) {
    fail(`validator skills JSON exited ${evidence.skillsStatus}`);
  }
  const marketplace = parseTerminalSummary(evidence.marketplace, 'marketplace');
  const agents = parseTerminalSummary(evidence.agents, 'agents');
  if (marketplace.terminal_denominator.skills !== skills.rows) {
    fail('marketplace and SKILL-row counts disagree');
  }
  marketplace.validated_plugin_manifests = paths.filter((path) =>
    /\/\.claude-plugin\/plugin\.json$/.test(path),
  ).length;

  const pluginSkills = paths.filter((path) => /^plugins\/.+\/SKILL\.md$/.test(path)).length;
  const pluginAgents = paths.filter((path) => /^plugins\/.+\/agents\/[^/]+\.md$/.test(path)).length;
  const catalog = catalogMeasurement(repository, paths);
  const assets = binaryAssets(repository, paths);
  const detector = promotionDetector(repository, assets.mismatches);
  const hermeticTestContract = inspectFreshieHermeticTest(repository);
  const extendedRows = buildExtendedScorecardRows({
    agentSummary: {
      agents: agents.terminal_denominator.agents,
      compliance_percent: agents.validator_reported_mixed_denominator_percent,
      errors: agents.error_total_all_validated_surfaces,
    },
    marketplaceSummary: {
      errors: marketplace.error_total_all_validated_surfaces,
    },
    paths,
    root: repository,
    hermeticTestContract,
    skillRows: evidence.skills.filter((entry) => entry && typeof entry.path === 'string'),
    skillSummary: skills,
  });
  assertReadmeMetricWriterContract(extendedRows[25]);

  return {
    blueprint: '727',
    cohorts: {
      agent_files_plugin_surface: 'tracked Markdown files directly beneath plugins/**/agents/',
      agent_lane_validator: 'files reported by validate-skills-schema.py --standard --agents-only',
      graded_artifacts:
        'unique SKILL.md rows from --marketplace --skills-only --json in the exact Git index tree',
      marketplace_terminal:
        'errors and fully-compliant counts may include plugin manifests; Total files excludes them and equals skills + commands + agents',
      plugin_skills: 'tracked plugins/**/SKILL.md files',
      tracked_tree: 'git ls-tree over one immutable git write-tree object',
    },
    graded_artifact_cohort: {
      cohort: 'graded_artifacts',
      reproduce: 'pnpm run measure:e1 --row=graded_artifact_cohort --stdout',
      source: 'scripts/validate-skills-schema.py --marketplace --skills-only --json',
      status: 'measured',
      values: skills,
    },
    rows: {
      1: row(
        'Tracked files, plugin SKILL.md, and plugin agent files',
        'tracked_tree',
        {
          plugin_agent_files: pluginAgents,
          raw_tracked_plugin_skill_files: pluginSkills,
          tracked_files: paths.length,
        },
        1,
      ),
      2: row(
        'Catalog entries versus distinct names',
        'canonical extended catalog',
        {
          duplicate_names: catalog.duplicateNames,
          entries: catalog.entries,
          distinct_names: catalog.names,
        },
        2,
        catalog.entries === catalog.names ? 'pass' : 'fail',
      ),
      3: row(
        'Tracked stale catalog shadows',
        'tracked .claude-plugin catalog-shaped files',
        {
          count: catalog.shadows.length,
          paths: catalog.shadows,
        },
        3,
        catalog.shadows.length === 0 ? 'pass' : 'fail',
      ),
      4: row(
        'Marketplace-tier errors and compliance',
        'three named validator cohorts; never interchangeable',
        {
          agent_lane: agents,
          marketplace_terminal: marketplace,
          skill_rows: skills,
        },
        4,
      ),
      11: row(
        'Binary-extension assets versus magic bytes',
        'tracked .png/.pdf/.zip/.ttf files',
        {
          candidate_count: assets.candidates.length,
          mismatch_count: assets.mismatches.length,
          mismatch_paths: assets.mismatches,
        },
        11,
        assets.mismatches.length === 0 ? 'pass' : 'fail',
      ),
      12: row(
        'Binary detector in the promotion path',
        'row 11 mismatches plus fixed genuine, counterfeit, late-NUL, and invalid-UTF-8 probes',
        {
          detector: detector.strategy,
          excluded_count: detector.excluded.length,
          fixture_checks: detector.fixture_checks,
          fixture_passed: detector.fixture_passed,
          missed_count: detector.missed.length,
          missed_paths: detector.missed,
          prefix_bytes: detector.prefix_bytes,
          refused_count: detector.refused.length,
          refused_paths: detector.refused,
        },
        12,
        detector.strategy === 'magic_bytes' &&
          detector.fixture_passed &&
          detector.missed.length === 0 &&
          detector.refused.length === assets.mismatches.length
          ? 'pass'
          : 'fail',
      ),
      ...extendedRows,
    },
    schema_version: 2,
  };
}

export function stableJson(value) {
  const seen = new WeakSet();
  function sort(item) {
    if (typeof item === 'number' && !Number.isFinite(item)) fail('non-finite number in output');
    if (['undefined', 'function', 'symbol', 'bigint'].includes(typeof item)) {
      fail(`unsupported ${typeof item} in output`);
    }
    if (Array.isArray(item)) {
      if (Object.keys(item).length !== item.length) fail('sparse array in output');
      if (seen.has(item)) fail('cycle in output');
      seen.add(item);
      const result = item.map(sort);
      seen.delete(item);
      return result;
    }
    if (item && typeof item === 'object') {
      if (
        Object.getPrototypeOf(item) !== Object.prototype &&
        Object.getPrototypeOf(item) !== null
      ) {
        fail('non-plain object in output');
      }
      if (seen.has(item)) fail('cycle in output');
      seen.add(item);
      const result = Object.fromEntries(
        Object.keys(item)
          .sort((a, b) => (a < b ? -1 : a > b ? 1 : 0))
          .map((key) => [key, sort(item[key])]),
      );
      seen.delete(item);
      return result;
    }
    return item;
  }
  const raw = `${JSON.stringify(sort(value), null, 2)}\n`;
  const formatted = spawnSync(
    join(SCRIPT_ROOT, 'node_modules/.bin/prettier'),
    ['--parser', 'json'],
    {
      cwd: SCRIPT_ROOT,
      encoding: 'utf8',
      input: raw,
      maxBuffer: 64 * 1024 * 1024,
    },
  );
  if (formatted.error || formatted.status !== 0) {
    fail(`Prettier JSON formatting failed: ${formatted.error?.message ?? formatted.stderr.trim()}`);
  }
  const rendered = formatted.stdout;
  if (/"(?:captured_at|generated_at|hostname|cwd|head)"\s*:/.test(rendered)) {
    fail('nondeterministic metadata entered output');
  }
  return rendered;
}

/**
 * Row values that are measured and reproducible but are not written to the
 * committed scorecard. Each one is a pure function of the commit that would
 * contain it, so storing it records nothing Git cannot already answer, and it
 * changes with every added or deleted file anywhere in the repository. Kept in
 * the file, it made every pair of file-adding pull requests conflict on the
 * same line. `--stdout` still reports the full live row; the committed row
 * names what it omits under `unpersisted_values`.
 */
export const UNPERSISTED_VALUES = Object.freeze({
  1: Object.freeze(['tracked_files']),
  46: Object.freeze(['tracked_files']),
});

/** Project a full measurement report into the form persisted in the scorecard. */
export function persistedReport(report) {
  const rows = { ...report.rows };
  for (const [id, keys] of Object.entries(UNPERSISTED_VALUES)) {
    const measured = rows[id];
    // A row that was not measured in this tree (values null) has nothing to omit.
    if (!measured || measured.values === null) continue;
    if (typeof measured.values !== 'object') fail(`row ${id} has no values to omit`);
    const values = { ...measured.values };
    for (const key of keys) {
      if (!Object.hasOwn(values, key)) fail(`row ${id} no longer measures ${key}`);
      delete values[key];
    }
    rows[id] = { ...measured, unpersisted_values: [...keys], values };
  }
  return { ...report, rows };
}

export function artifactMatches(actual, expected) {
  return actual === expected;
}

export function assertMeasurementInputsIndexed(
  worktreeRoot,
  snapshotRoot,
  paths = MEASUREMENT_INPUT_PATHS,
) {
  for (const path of paths) {
    if (text(snapshotRoot, path) !== text(worktreeRoot, path)) {
      fail(`${path} differs from the Git index; stage or restore it before measuring`);
    }
  }
}

function parseArgs(argv) {
  const options = { check: false, root: SCRIPT_ROOT, row: null, stdout: false };
  for (const arg of argv) {
    if (arg === '--check') options.check = true;
    else if (arg === '--stdout') options.stdout = true;
    else if (arg.startsWith('--row=')) {
      const value = arg.slice(6);
      if (value !== 'graded_artifact_cohort' && !/^(?:[1-9]|[1-5]\d|6[0-2])$/.test(value)) {
        fail(`unknown row: ${value || '(empty)'}`);
      }
      options.row = value;
    } else if (arg.startsWith('--root=')) {
      const value = arg.slice(7);
      if (!value) fail('--root requires a path');
      options.root = resolve(value);
    } else fail(`unknown argument: ${arg}`);
  }
  if (options.row && !options.stdout) fail('--row requires --stdout');
  if (options.check && options.stdout) fail('--check and --stdout are mutually exclusive');
  return options;
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  const indexed = withIndexSnapshot(options.root, (snapshot) => {
    assertMeasurementInputsIndexed(options.root, snapshot.root);
    return {
      artifact: existsSync(file(snapshot.root, ARTIFACT_PATH))
        ? readFileSync(file(snapshot.root, ARTIFACT_PATH), 'utf8')
        : null,
      report: buildReport(snapshot.root, undefined, snapshot.paths),
    };
  });
  const report = indexed.report;
  let selected = report;
  if (options.row) {
    selected =
      options.row === 'graded_artifact_cohort'
        ? report.graded_artifact_cohort
        : report.rows[options.row];
    if (!selected) fail(`unknown row: ${options.row}`);
  }
  if (options.stdout) {
    process.stdout.write(stableJson(selected));
    return;
  }
  const rendered = stableJson(persistedReport(report));
  const artifact = file(options.root, ARTIFACT_PATH);
  if (options.check) {
    if (indexed.artifact === null || !artifactMatches(indexed.artifact, rendered)) {
      console.error(`epic-1-measurement: DRIFT (${ARTIFACT_PATH})`);
      process.exitCode = 1;
      return;
    }
    console.log(`epic-1-measurement: OK (${ARTIFACT_PATH})`);
    return;
  }
  writeFileSync(artifact, rendered);
  console.log(`epic-1-measurement: generated (${ARTIFACT_PATH})`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    main();
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
