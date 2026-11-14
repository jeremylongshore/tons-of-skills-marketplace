import { createHash } from 'node:crypto';
import { cpSync, existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readlinkSync, readdirSync, realpathSync, renameSync, rmSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';

const CORE = ['hyperflow-plan', 'hyperflow-smash', 'hyperflow-crash', 'hyperflow-agents-skill'];
const LEGACY = ['hyperflow', 'plan', 'dispatch', 'trace', 'audit', 'deploy', 'handoff'];
const MARKER = '.hyperflow-source.json';
const PROTECTED_PATH = /(^|\/)(?:\.env(?:\..*)?|credentials?(?:\..*)?|secrets?(?:\..*)?|\.ssh|\.aws|\.kube|[^/]+\.(?:pem|key|crt))($|\/)|(^|\/)\.config\/(?:gcloud|aws)(\/|$)/i;
const command = process.argv[2];
const sourceInputRoot = process.argv[3] ? resolve(process.argv[3]) : '';
const sourceRoot = sourceInputRoot ? realpathSync(sourceInputRoot) : '';
const skillsRoot = process.argv[4] ? resolve(process.argv[4]) : '';

function fail(message) { throw new Error(message); }

function hasPath(path) { try { lstatSync(path); return true; } catch (error) { if (error.code === 'ENOENT') return false; throw error; } }

function pathIsProtected(path) {
  let current = resolve(path);
  const suffix = [];
  while (!hasPath(current)) {
    suffix.unshift(basename(current));
    current = dirname(current);
  }
  const canonical = resolve(realpathSync(current), ...suffix);
  return PROTECTED_PATH.test(path) || PROTECTED_PATH.test(canonical);
}

function treeDigest(directory) {
  const directoryInfo = lstatSync(directory);
  if (!directoryInfo.isDirectory() || directoryInfo.isSymbolicLink() || pathIsProtected(directory) ||
      pathIsProtected(realpathSync(directory))) fail('Skill copy root is not a safe real directory');
  const hash = createHash('sha256');
  function visit(current, relative = '') {
    for (const entry of readdirSync(current, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      if (!relative && entry.name === MARKER) continue;
      const path = join(current, entry.name);
      const name = relative ? `${relative}/${entry.name}` : entry.name;
      if (PROTECTED_PATH.test(name) || (!relative && name === MARKER)) fail(`Protected or reserved skill copy path: ${name}`);
      const info = lstatSync(path);
      if (info.isSymbolicLink()) fail(`Skill copies cannot contain symbolic links: ${name}`);
      hash.update(`${info.isDirectory() ? 'd' : 'f'}\0${name}\0${info.mode & 0o777}\0`);
      if (info.isDirectory()) visit(path, name);
      else if (info.isFile() && info.nlink === 1) hash.update(readFileSync(path));
      else if (info.isFile()) fail(`Skill copies cannot contain hard-linked files: ${name}`);
      else fail(`Unsupported skill copy entry: ${name}`);
    }
  }
  visit(directory);
  return hash.digest('hex');
}

function copyMarker(directory, skill) {
  try {
    if (!hasPath(directory)) return false;
    const directoryInfo = lstatSync(directory);
    if (!directoryInfo.isDirectory() || directoryInfo.isSymbolicLink() || pathIsProtected(directory) ||
        pathIsProtected(realpathSync(directory))) return false;
    const path = join(directory, MARKER);
    const info = lstatSync(path);
    if (!info.isFile() || info.isSymbolicLink() || info.nlink !== 1) return false;
    const marker = JSON.parse(readFileSync(path, 'utf8'));
    return marker.schema === 'hyperflow-source-copy.v1' && marker.sourceRoot === sourceRoot &&
      marker.skill === skill && marker.digest === treeDigest(directory);
  } catch { return false; }
}

function ownedLink(path, skill) {
  if (!hasPath(path) || !lstatSync(path).isSymbolicLink()) return false;
  const target = resolve(dirname(path), readlinkSync(path));
  const expected = join(sourceInputRoot, 'skills', skill);
  if (target === expected || target === join(sourceRoot, 'skills', skill)) return true;
  try { return realpathSync(target) === join(sourceRoot, 'skills', skill); }
  catch { return false; }
}

function state() {
  if (pathIsProtected(sourceRoot) || pathIsProtected(join(sourceRoot, 'skills')) || pathIsProtected(skillsRoot)) return 'conflict';
  if (hasPath(skillsRoot) && (!lstatSync(skillsRoot).isDirectory() || lstatSync(skillsRoot).isSymbolicLink())) return 'conflict';
  let copies = 0;
  let links = 0;
  let conflicts = 0;
  for (const skill of CORE) {
    const path = join(skillsRoot, skill);
    if (copyMarker(path, skill)) copies += 1;
    else if (ownedLink(path, skill)) links += 1;
    else if (hasPath(path)) conflicts += 1;
  }
  for (const skill of LEGACY) {
    const path = join(skillsRoot, skill);
    if (!hasPath(path)) continue;
    if (ownedLink(path, skill)) links += 1;
    else conflicts += 1;
  }
  if (conflicts) return 'conflict';
  if (copies === CORE.length && !links) return 'complete';
  if (!copies && !links) return 'none';
  return 'partial';
}

function renderCopy(staging, skill) {
  const source = join(sourceRoot, 'skills', skill);
  const target = join(staging, skill);
  if (!existsSync(join(source, 'SKILL.md'))) fail(`Missing source skill ${skill}`);
  validateSourceTree(source);
  cpSync(source, target, { recursive: true, preserveTimestamps: true, verbatimSymlinks: true });
  const skillFile = join(target, 'SKILL.md');
  const content = readFileSync(skillFile, 'utf8');
  writeFileSync(skillFile, content.replaceAll('<plugin-root>', `'${sourceRoot.replaceAll("'", "'\\''")}'`));
  const digest = treeDigest(target);
  writeFileSync(join(target, MARKER), `${JSON.stringify({ schema: 'hyperflow-source-copy.v1', sourceRoot, skill, digest })}\n`, { mode: 0o600 });
}

function validateSourceTree(directory) {
  if (pathIsProtected(directory) || pathIsProtected(realpathSync(directory))) fail('Source skill root is protected');
  function visit(current, relative = '') {
    for (const entry of readdirSync(current, { withFileTypes: true })) {
      const name = relative ? `${relative}/${entry.name}` : entry.name;
      if (PROTECTED_PATH.test(name) || (!relative && name === MARKER)) fail(`Protected or reserved source skill path: ${name}`);
      const info = lstatSync(join(current, entry.name));
      if (info.isSymbolicLink()) fail(`Source skills cannot contain symbolic links: ${name}`);
      if (info.isDirectory()) visit(join(current, entry.name), name);
      else if (!info.isFile() || info.nlink !== 1) fail(`Source skills cannot contain non-regular or hard-linked files: ${name}`);
    }
  }
  visit(directory);
}

function prepare() {
  if (!sourceRoot || !skillsRoot) fail('Source and Codex skills roots are required');
  if (pathIsProtected(sourceRoot) || pathIsProtected(join(sourceRoot, 'skills')) || pathIsProtected(skillsRoot)) {
    fail('Source or Codex skills root resolves inside a protected path');
  }
  const info = existsSync(skillsRoot) ? lstatSync(skillsRoot) : null;
  if (info?.isSymbolicLink() || (info && !info.isDirectory())) fail(`Codex skills root is not a real directory: ${skillsRoot}`);
  mkdirSync(skillsRoot, { recursive: true, mode: 0o700 });
  const rootInfo = lstatSync(skillsRoot);
  if (!rootInfo.isDirectory() || rootInfo.isSymbolicLink()) fail(`Codex skills root is not a real directory: ${skillsRoot}`);
}

function install() {
  prepare();
  const current = state();
  if (current === 'conflict') fail('Codex skill paths include foreign or modified content; provider was not changed');
  const stage = mkdtempSync(join(skillsRoot, '.hyperflow-stage-'));
  const moved = [];
  const installed = [];
  try {
    for (const skill of CORE) renderCopy(stage, skill);
    for (const skill of CORE) {
      const path = join(skillsRoot, skill);
      if (hasPath(path)) {
        const original = join(stage, `backup-${skill}`);
        renameSync(path, original);
        moved.push([original, path]);
      }
    }
    for (const skill of LEGACY) {
      const path = join(skillsRoot, skill);
      if (ownedLink(path, skill)) {
        const original = join(stage, `legacy-${skill}`);
        renameSync(path, original);
        moved.push([original, path]);
      }
    }
    for (const skill of CORE) {
      const path = join(skillsRoot, skill);
      renameSync(join(stage, skill), path);
      installed.push(path);
    }
    rmSync(stage, { recursive: true, force: true });
    return { state: 'complete', skills: CORE.length };
  } catch (error) {
    for (const path of installed.reverse()) rmSync(path, { recursive: true, force: true });
    for (const [backup, path] of moved.reverse()) if (hasPath(backup)) renameSync(backup, path);
    rmSync(stage, { recursive: true, force: true });
    throw error;
  }
}

function uninstall() {
  if (!hasPath(skillsRoot) || lstatSync(skillsRoot).isSymbolicLink()) return { removed: 0, state: 'none' };
  let removed = 0;
  for (const skill of CORE) {
    const path = join(skillsRoot, skill);
    if (copyMarker(path, skill)) { rmSync(path, { recursive: true }); removed += 1; }
  }
  for (const skill of [...CORE, ...LEGACY]) {
    const path = join(skillsRoot, skill);
    if (ownedLink(path, skill)) { rmSync(path); removed += 1; }
  }
  return { removed, state: state() };
}

try {
  if (process.versions.node.split('.')[0] < 24) fail('Node.js 24 or newer is required for Codex skill copies');
  if (command === 'status') process.stdout.write(`${state()}\n`);
  else if (command === 'install') process.stdout.write(`${JSON.stringify(install())}\n`);
  else if (command === 'uninstall') process.stdout.write(`${JSON.stringify(uninstall())}\n`);
  else fail('Usage: codex-skills.mjs status|install|uninstall <source-root> <skills-root>');
} catch (error) {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 1;
}
