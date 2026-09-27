import { test } from 'node:test';
import { equal, ok, deepEqual } from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  analyzeConfig,
  analyzeIgnore,
  formatIssue,
  verifyFingerprintInRepository,
  validateFingerprintSourceLine,
  SUPPORTED_FINGERPRINT_RULES,
  APPROVED_PATH_PATTERNS,
  BANNED_FRAGMENTS,
} from './check-gitleaks-config.mjs';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const APPROVED_EXACT = '^scripts/validate-skills-schema\\.py$';
const APPROVED_EXACT_2 =
  '^plugins/security/penetration-tester/skills/scanning-for-hardcoded-secrets/scripts/scan_secrets\\.py$';

const governed = (pattern) =>
  `[allowlist]\npaths = [\n    # reason: because.\n    # expiry: 2999-01-01\n    '''${pattern}''',\n]\n`;

function provenanceFixture({ trusted = true } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'gitleaks-provenance-'));
  execFileSync('git', ['-C', root, 'init', '--quiet']);
  execFileSync('git', ['-C', root, 'config', 'user.name', 'Test Author']);
  execFileSync('git', ['-C', root, 'config', 'user.email', 'test@example.invalid']);
  const path = 'fixtures/source.txt';
  mkdirSync(join(root, 'fixtures'), { recursive: true });
  writeFileSync(join(root, path), 'baseline\n');
  execFileSync('git', ['-C', root, 'add', path]);
  execFileSync('git', ['-C', root, 'commit', '--quiet', '-m', 'baseline']);
  if (!trusted) {
    execFileSync('git', ['-C', root, 'tag', '-a', 'trusted-provenance', '-m', 'anchor']);
  }
  const key = ['AI', 'za', 'A'.repeat(35)].join('');
  writeFileSync(join(root, path), `fixture=${key}\n`);
  execFileSync('git', ['-C', root, 'add', path]);
  execFileSync('git', ['-C', root, 'commit', '--quiet', '-m', 'fixture']);
  const commit = execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'], {
    encoding: 'utf8',
  }).trim();
  if (trusted) {
    execFileSync('git', ['-C', root, 'tag', '-a', 'trusted-provenance', '-m', 'anchor']);
  }
  const anchor = {
    ref: 'refs/tags/trusted-provenance',
    object: execFileSync('git', ['-C', root, 'rev-parse', 'refs/tags/trusted-provenance'], {
      encoding: 'utf8',
    }).trim(),
  };
  return { root, entry: `${commit}:${path}:gcp-api-key:1`, anchor };
}

test('live config passes with zero issues', () => {
  const result = analyzeConfig(readFileSync(resolve(ROOT, '.gitleaks.toml'), 'utf8'));
  equal(result.allow, true, JSON.stringify(result.issues));
  ok(result.entries > 0);
  deepEqual(result.entries, APPROVED_PATH_PATTERNS.length);
});

test('every historical blanket fragment is banned even when documented', () => {
  for (const banned of BANNED_FRAGMENTS) {
    const result = analyzeConfig(governed(`(?i).*${banned}$`));
    equal(result.allow, false, banned);
    ok(
      result.issues.some((issue) => issue.code === 'TYPE_BLANKET'),
      banned,
    );
  }
});

test('a path entry without reason and expiry fails', () => {
  const result = analyzeConfig(`[allowlist]\npaths = [\n    '''${APPROVED_EXACT}''',\n]\n`);
  ok(result.issues.some((issue) => issue.code === 'UNDOCUMENTED_EXCEPTION'));
});

test('reason without expiry is not enough', () => {
  const result = analyzeConfig(
    `[allowlist]\npaths = [\n    # reason: because.\n    '''${APPROVED_EXACT}''',\n]\n`,
  );
  ok(result.issues.some((issue) => issue.code === 'UNDOCUMENTED_EXCEPTION'));
});

test('a shared comment block governs consecutive entries', () => {
  const result = analyzeConfig(
    `[allowlist]\npaths = [\n    # reason: generated projections.\n    # expiry: 2027-01-01\n    '''${APPROVED_EXACT}''',\n    '''${APPROVED_EXACT_2}''',\n]\n`,
  );
  equal(result.allow, true, JSON.stringify(result.issues));
  equal(result.entries, 2);
});

test('a blank line ends a governing block', () => {
  const result = analyzeConfig(
    `[allowlist]\npaths = [\n    # reason: covered.\n    # expiry: 2027-01-01\n    '''${APPROVED_EXACT}''',\n\n    '''${APPROVED_EXACT_2}''',\n]\n`,
  );
  ok(result.issues.some((issue) => issue.code === 'UNDOCUMENTED_EXCEPTION'));
});

test('missing paths section is an explicit failure', () => {
  const result = analyzeConfig('[allowlist]\nregexes = []\n');
  ok(result.issues.some((issue) => issue.code === 'NO_PATHS_SECTION'));
});

test('credential-shaped Google API keys cannot be retained as allowlist values', () => {
  const key = ['AI', 'za', 'A'.repeat(35)].join('');
  const result = analyzeConfig(`[allowlist]\npaths = []\nregexes = [\n    '''${key}''',\n]\n`);
  ok(result.issues.some((issue) => issue.code === 'CREDENTIAL_LITERAL'));
});

test('TOML escapes cannot conceal a credential-shaped Google API key', () => {
  const encodedKey = ['\\u0041', 'Iza', 'A'.repeat(35)].join('');
  const result = analyzeConfig(`${governed(APPROVED_EXACT)}regexes = ["${encodedKey}"]\n`);
  ok(result.issues.some((issue) => issue.code === 'CREDENTIAL_LITERAL'));
});

test('inline path arrays are rejected rather than silently skipped', () => {
  const result = analyzeConfig('[allowlist]\npaths = ["^specific/path$"]\n');
  ok(result.issues.some((issue) => issue.code === 'UNSUPPORTED_PATHS_SYNTAX'));
  ok(result.issues.some((issue) => issue.code === 'PATH_ENTRY_COUNT_MISMATCH'));
});

test('a decoy paths array outside allowlist cannot hide semantic allowlist paths', () => {
  const result = analyzeConfig(
    `paths = [\n    # reason: decoy.\n    # expiry: 2999-01-01\n    '''^specific/path$''',\n]\n[allowlist]\npaths = ["^.*\\\\.md$"]\n`,
  );
  ok(result.issues.some((issue) => issue.code === 'UNSUPPORTED_PATHS_SYNTAX'));
  ok(result.issues.some((issue) => issue.code === 'PATH_ENTRY_COUNT_MISMATCH'));
});

test('plural global and rule-level allowlists are rejected', () => {
  const global = analyzeConfig(
    `${governed(APPROVED_EXACT)}\n[[allowlists]]\ndescription = "bypass"\nregexes = [".*"]\n`,
  );
  ok(global.issues.some((issue) => issue.code === 'UNSUPPORTED_GLOBAL_ALLOWLISTS'));

  const rule = analyzeConfig(
    `${governed(APPROVED_EXACT)}\n[[rules]]\nid = "fixture"\ndescription = "fixture"\nregex = "fixture"\n[[rules.allowlists]]\nregexes = [".*"]\n`,
  );
  ok(rule.issues.some((issue) => issue.code === 'UNSUPPORTED_RULE_ALLOWLIST'));

  const inlineRulesObject = analyzeConfig(
    `rules = { id = "fixture", regex = "fixture", allowlist = { regexes = [".*"] } }\n${governed(APPROVED_EXACT)}`,
  );
  ok(inlineRulesObject.issues.some((issue) => issue.code === 'INVALID_RULES_SHAPE'));

  const rulesTable = analyzeConfig(
    `[rules]\nid = "fixture"\nregex = "fixture"\nallowlist = { regexes = [".*"] }\n${governed(APPROVED_EXACT)}`,
  );
  ok(rulesTable.issues.some((issue) => issue.code === 'INVALID_RULES_SHAPE'));
});

test('unknown global fields and unreviewed values are rejected', () => {
  const unknownField = analyzeConfig(
    `${governed(APPROVED_EXACT)}\ncommits = ["${'a'.repeat(40)}"]\nregexes = []\nstopwords = []\n`,
  );
  ok(unknownField.issues.some((issue) => issue.code === 'UNSUPPORTED_GLOBAL_ALLOWLIST_FIELD'));

  const unknownRegex = analyzeConfig(
    `${governed(APPROVED_EXACT)}\nregexes = [".*"]\nstopwords = []\n`,
  );
  ok(unknownRegex.issues.some((issue) => issue.code === 'UNAPPROVED_ALLOWLIST_REGEX'));

  const unknownStopword = analyzeConfig(
    `${governed(APPROVED_EXACT)}\nregexes = []\nstopwords = ["anything"]\n`,
  );
  ok(unknownStopword.issues.some((issue) => issue.code === 'UNAPPROVED_ALLOWLIST_STOPWORD'));
});

test('behaviorally broad path regexes fail even without banned literal fragments', () => {
  const result = analyzeConfig(governed('^.*\\.md$'));
  ok(result.issues.some((issue) => issue.code === 'UNAPPROVED_PATH_PATTERN'));
});

test('unreviewed file-type blankets fail even when finite probes would miss them', () => {
  const result = analyzeConfig(governed('^.*\\.yaml$'));
  ok(result.issues.some((issue) => issue.code === 'UNAPPROVED_PATH_PATTERN'));
});

test('expiry metadata must be a real ISO date or an explained permanent exception', () => {
  const invalid = analyzeConfig(
    `[allowlist]\npaths = [\n    # reason: because.\n    # expiry: tomorrow\n    '''${APPROVED_EXACT}''',\n]\n`,
  );
  ok(invalid.issues.some((issue) => issue.code === 'INVALID_EXPIRY'));

  const impossible = analyzeConfig(
    `[allowlist]\npaths = [\n    # reason: because.\n    # expiry: 2027-02-30\n    '''${APPROVED_EXACT}''',\n]\n`,
  );
  ok(impossible.issues.some((issue) => issue.code === 'INVALID_EXPIRY'));

  const expired = analyzeConfig(
    `[allowlist]\npaths = [\n    # reason: because.\n    # expiry: 2000-01-01\n    '''${APPROVED_EXACT}''',\n]\n`,
  );
  ok(expired.issues.some((issue) => issue.code === 'INVALID_EXPIRY'));

  equal(analyzeConfig(governed(APPROVED_EXACT)).allow, true);
  equal(
    analyzeConfig(
      `[allowlist]\npaths = [\n    # reason: this config file itself holds detector and allowlist regexes\n    # expiry: none (self-referential by construction)\n    '''^\\.gitleaks\\.toml$''',\n]\n`,
    ).allow,
    true,
  );
  const unrelatedPermanent = analyzeConfig(
    `[allowlist]\npaths = [\n    # reason: because.\n    # expiry: none (unrelated reason)\n    '''${APPROVED_EXACT}''',\n]\n`,
  );
  ok(unrelatedPermanent.issues.some((issue) => issue.code === 'INVALID_EXPIRY'));
});

test('metadata labels must be unique and anchored', () => {
  const duplicateExpiry = analyzeConfig(
    `[allowlist]\npaths = [\n    # reason: because.\n    # expiry: 2999-01-01\n    # expiry: 2998-01-01\n    '''${APPROVED_EXACT}''',\n]\n`,
  );
  ok(duplicateExpiry.issues.some((issue) => issue.code === 'UNDOCUMENTED_EXCEPTION'));

  const prefixedLabels = analyzeConfig(
    `[allowlist]\npaths = [\n    # historical reason: because.\n    # historical expiry: 2999-01-01\n    '''${APPROVED_EXACT}''',\n]\n`,
  );
  ok(prefixedLabels.issues.some((issue) => issue.code === 'UNDOCUMENTED_EXCEPTION'));
});

test('ignore entries must bind commit, path, rule, and line', () => {
  const exact = `${'a'.repeat(40)}:path/to/file:gcp-api-key:52`;
  equal(analyzeIgnore(`# reason: fixture\n${exact}\n`, () => ({ ok: true })).allow, true);
  deepEqual(
    analyzeIgnore('path/to/file:gcp-api-key:52\n').issues.map((issue) => issue.code),
    ['NON_COMMIT_BOUND_FINGERPRINT'],
  );
});

test('duplicate ignore fingerprints fail closed', () => {
  const exact = `${'b'.repeat(40)}:path/to/file:gcp-api-key:52`;
  deepEqual(
    analyzeIgnore(`${exact}\n${exact}\n`, () => ({ ok: true })).issues.map((issue) => issue.code),
    ['DUPLICATE_FINGERPRINT'],
  );
});

test('fingerprint paths must be normalized repository-relative paths', () => {
  for (const path of ['/absolute/path', '../outside', 'a/../b', './relative', 'a\\b', 'a//b']) {
    const exact = `${'b'.repeat(40)}:${path}:gcp-api-key:52`;
    ok(
      analyzeIgnore(exact, () => ({ ok: true })).issues.some(
        (issue) => issue.code === 'INVALID_FINGERPRINT_PATH',
      ),
    );
  }
});

test('one fingerprint cannot suppress multiple same-line findings', () => {
  const first = ['AI', 'za', 'A'.repeat(35)].join('');
  const second = ['AI', 'za', 'B'.repeat(35)].join('');
  equal(validateFingerprintSourceLine(`first=${first}`).ok, true);
  deepEqual(validateFingerprintSourceLine(`first=${first} second=${second}`), {
    ok: false,
    code: 'AMBIGUOUS_FINGERPRINT_LINE',
  });
});

test('ignore analysis verifies provenance by default', () => {
  const nonexistent = `${'d'.repeat(40)}:path/to/file:gcp-api-key:52`;
  const result = analyzeIgnore(nonexistent);
  equal(result.allow, false);
  ok(result.issues.some((issue) => issue.code === 'FINGERPRINT_SOURCE_UNREACHABLE'));
});

test('ignore analysis rejects an explicitly missing verifier', () => {
  const exact = `${'e'.repeat(40)}:path/to/file:gcp-api-key:52`;
  const result = analyzeIgnore(exact, null);
  equal(result.allow, false);
  ok(result.issues.some((issue) => issue.code === 'MISSING_FINGERPRINT_VERIFIER'));
});

test('diagnostics never render source patterns or possible credentials', () => {
  const key = ['AI', 'za', 'A'.repeat(35)].join('');
  const message = formatIssue({ code: 'UNAPPROVED_PATH_PATTERN', line: 7, pattern: key });
  equal(message, 'gitleaks-config: UNAPPROVED_PATH_PATTERN at line 7');
  equal(message.includes(key), false);
});

test('fingerprint provenance is verified against a pinned annotated release anchor', () => {
  const fixture = provenanceFixture();
  try {
    deepEqual(verifyFingerprintInRepository(fixture.entry, fixture.root, fixture.anchor), {
      ok: true,
    });
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
});

test('an untrusted local branch cannot establish fingerprint provenance', () => {
  const fixture = provenanceFixture({ trusted: false });
  try {
    deepEqual(verifyFingerprintInRepository(fixture.entry, fixture.root, fixture.anchor), {
      ok: false,
      code: 'FINGERPRINT_SOURCE_UNREACHABLE',
    });
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
});

test('fingerprint provenance failures fail closed', () => {
  const exact = `${'c'.repeat(40)}:path/to/file:gcp-api-key:52`;
  const result = analyzeIgnore(exact, () => ({ ok: false, code: 'FINGERPRINT_SOURCE_MISSING' }));
  deepEqual(
    result.issues.map((issue) => issue.code),
    ['FINGERPRINT_SOURCE_MISSING'],
  );
});

// ---- generic-api-key fingerprints and the main-branch provenance anchor

const NO_RELEASE_ANCHOR = { ref: 'refs/tags/does-not-exist', object: '0'.repeat(40) };

function git(root, args) {
  return execFileSync('git', ['-C', root, ...args], { encoding: 'utf8' }).trim();
}

// A repo whose `main` branch plays protected main. `fingerprintAfterAnchor`
// lands the fingerprinted commit after the pinned anchor; `anchorOffMain`
// pins an anchor that only exists on a side branch (a PR's own commit).
function mainAnchorFixture({ fingerprintAfterAnchor = false, anchorOffMain = false, line } = {}) {
  const root = mkdtempSync(join(tmpdir(), 'gitleaks-main-anchor-'));
  git(root, ['init', '--quiet', '-b', 'main']);
  git(root, ['config', 'user.name', 'Test Author']);
  git(root, ['config', 'user.email', 'test@example.invalid']);
  const path = 'fixtures/example.md';
  mkdirSync(join(root, 'fixtures'), { recursive: true });
  const commitFile = (text, message) => {
    writeFileSync(join(root, path), text);
    git(root, ['add', path]);
    git(root, ['commit', '--quiet', '-m', message]);
    return git(root, ['rev-parse', 'HEAD']);
  };
  commitFile('baseline\n', 'baseline');
  // Built at runtime (like the Google-key fixture above) so the scanner does
  // not flag this test file's own source.
  const exampleLine =
    line ??
    `${['EXAMPLE', 'API', 'KEY', 'PROD'].join('_')}=${['vendor', 'prod', 'xyz789'].join('-')}`;
  let fingerprinted;
  let anchor;
  if (fingerprintAfterAnchor) {
    anchor = git(root, ['rev-parse', 'HEAD']);
    fingerprinted = commitFile(`${exampleLine}\n`, 'example');
  } else {
    fingerprinted = commitFile(`${exampleLine}\n`, 'example');
    anchor = commitFile(`${exampleLine}\nmore\n`, 'later');
  }
  if (anchorOffMain) {
    git(root, ['checkout', '--quiet', '-b', 'pr-branch']);
    anchor = commitFile(`${exampleLine}\npr\n`, 'pr-only');
    git(root, ['checkout', '--quiet', 'main']);
  }
  return {
    root,
    entry: `${fingerprinted}:${path}:generic-api-key:1`,
    mainAnchor: { commit: anchor, branch: 'refs/heads/main' },
  };
}

function withFixture(options, fn) {
  const fixture = mainAnchorFixture(options);
  try {
    return fn(fixture);
  } finally {
    rmSync(fixture.root, { recursive: true, force: true });
  }
}

test('only gcp-api-key and generic-api-key may be fingerprint-suppressed', () => {
  deepEqual([...SUPPORTED_FINGERPRINT_RULES], ['gcp-api-key', 'generic-api-key']);
  withFixture({}, (fixture) => {
    const other = fixture.entry.replace(':generic-api-key:', ':aws-access-token:');
    deepEqual(
      verifyFingerprintInRepository(other, fixture.root, NO_RELEASE_ANCHOR, fixture.mainAnchor),
      {
        ok: false,
        code: 'UNSUPPORTED_FINGERPRINT_RULE',
      },
    );
  });
});

test('a generic fingerprint verifies when its commit is in the history of a main anchor', () => {
  withFixture({}, (fixture) => {
    deepEqual(
      verifyFingerprintInRepository(
        fixture.entry,
        fixture.root,
        NO_RELEASE_ANCHOR,
        fixture.mainAnchor,
      ),
      { ok: true },
    );
  });
});

test('a commit newer than the main anchor cannot establish provenance', () => {
  withFixture({ fingerprintAfterAnchor: true }, (fixture) => {
    deepEqual(
      verifyFingerprintInRepository(
        fixture.entry,
        fixture.root,
        NO_RELEASE_ANCHOR,
        fixture.mainAnchor,
      ),
      { ok: false, code: 'FINGERPRINT_SOURCE_UNREACHABLE' },
    );
  });
});

test('an anchor that is not on main (a PR-only commit) cannot establish provenance', () => {
  withFixture({ anchorOffMain: true }, (fixture) => {
    deepEqual(
      verifyFingerprintInRepository(
        fixture.entry,
        fixture.root,
        NO_RELEASE_ANCHOR,
        fixture.mainAnchor,
      ),
      { ok: false, code: 'FINGERPRINT_SOURCE_UNREACHABLE' },
    );
  });
});

test('a missing main anchor fails closed', () => {
  withFixture({}, (fixture) => {
    const missing = { commit: 'f'.repeat(40), branch: 'refs/heads/main' };
    deepEqual(
      verifyFingerprintInRepository(fixture.entry, fixture.root, NO_RELEASE_ANCHOR, missing),
      {
        ok: false,
        code: 'FINGERPRINT_SOURCE_UNREACHABLE',
      },
    );
    deepEqual(verifyFingerprintInRepository(fixture.entry, fixture.root, NO_RELEASE_ANCHOR, null), {
      ok: false,
      code: 'FINGERPRINT_SOURCE_UNREACHABLE',
    });
  });
});

test('a generic fingerprint must point at a line the rule could match', () => {
  equal(validateFingerprintSourceLine('EXAMPLE_API_KEY=placeholder', 'generic-api-key').ok, true);
  equal(
    validateFingerprintSourceLine('Domain authenticated, bounce handling', 'generic-api-key').ok,
    true,
  );
  deepEqual(validateFingerprintSourceLine('## Overview', 'generic-api-key'), {
    ok: false,
    code: 'FINGERPRINT_FINDING_MISMATCH',
  });
  deepEqual(validateFingerprintSourceLine(undefined, 'generic-api-key'), {
    ok: false,
    code: 'FINGERPRINT_FINDING_MISMATCH',
  });
  withFixture({ line: 'plain prose with no trigger words' }, (fixture) => {
    deepEqual(
      verifyFingerprintInRepository(
        fixture.entry,
        fixture.root,
        NO_RELEASE_ANCHOR,
        fixture.mainAnchor,
      ),
      { ok: false, code: 'FINGERPRINT_FINDING_MISMATCH' },
    );
  });
});

test('the Google-key line check is unchanged for gcp-api-key entries', () => {
  const key = ['AI', 'za', 'A'.repeat(35)].join('');
  equal(validateFingerprintSourceLine(`k=${key}`).ok, true);
  equal(validateFingerprintSourceLine(`k=${key}`, 'gcp-api-key').ok, true);
  deepEqual(validateFingerprintSourceLine('EXAMPLE_API_KEY=x', 'gcp-api-key'), {
    ok: false,
    code: 'FINGERPRINT_FINDING_MISMATCH',
  });
});
