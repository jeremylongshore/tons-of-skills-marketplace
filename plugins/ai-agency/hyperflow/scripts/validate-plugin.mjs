#!/usr/bin/env node
/**
 * Validate the portable Hyperflow package without host-specific tooling.
 * This is intentionally read-only: it parses manifests, checks the shipped
 * surface, resolves current Markdown links, and syntax-checks shell entrypoints.
 */
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, extname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const failures = [];
const CONTRACT = readJson("tests/fixtures/core-contract.json");

function pathFromRoot(path) {
  return join(ROOT, path);
}

function read(path) {
  return readFileSync(pathFromRoot(path), "utf8");
}

function readJson(path) {
  try {
    return JSON.parse(read(path));
  } catch (error) {
    failures.push(`${path}: invalid JSON (${error.message})`);
    return {};
  }
}

function filesUnder(path) {
  const absolute = pathFromRoot(path);
  if (!existsSync(absolute)) return [];
  if (!statSync(absolute).isDirectory()) return [path];

  return readdirSync(absolute, { withFileTypes: true }).flatMap((entry) => {
    if (entry.name === ".git" || entry.name === ".hyperflow" || entry.name === "node_modules") return [];
    const child = join(path, entry.name);
    if (entry.isDirectory()) return filesUnder(child);
    return entry.isFile() ? [child] : [];
  });
}

function check(condition, message) {
  if (!condition) failures.push(message);
}

function checkVersionParity() {
  const pkg = readJson("package.json");
  const claude = readJson(".claude-plugin/plugin.json");
  const codex = readJson(".codex-plugin/plugin.json");
  const marketplace = readJson(".claude-plugin/marketplace.json");
  const version = pkg.version;

  check(typeof version === "string" && /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/.test(version), "package.json: version is not strict semver");
  for (const [label, manifest] of [["Claude manifest", claude], ["Codex manifest", codex]]) {
    check(manifest.version === version, `${label}: version does not match package.json`);
  }
  check(marketplace.metadata?.version === version, "marketplace metadata: version does not match package.json");
  for (const plugin of marketplace.plugins ?? []) {
    check(plugin.version === version, `marketplace plugin ${plugin.name ?? "<unnamed>"}: version does not match package.json`);
  }
  for (const path of ["AGENTS.md", "CLAUDE.md"]) {
    check(read(path).includes(`hyperflow:doctrine:start version=${version}`), `${path}: doctrine version does not match package.json`);
  }
}

function checkSkillSurface() {
  const skills = readdirSync(pathFromRoot("skills"), { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && existsSync(pathFromRoot(`skills/${entry.name}/SKILL.md`)))
    .map((entry) => entry.name)
    .sort();
  check(JSON.stringify(skills) === JSON.stringify([...CONTRACT.skills].sort()), `skills: expected ${CONTRACT.skills.join(", ")}; found ${skills.join(", ")}`);

  for (const skill of CONTRACT.skills) {
    const path = `skills/${skill}/SKILL.md`;
    const source = read(path);
    const frontmatter = source.match(/^---\n([\s\S]*?)\n---/);
    check(frontmatter !== null, `${path}: missing frontmatter`);
    check(/^name:\s*\S+$/m.test(frontmatter?.[1] ?? ""), `${path}: missing name`);
    check(/^description:\s*.+$/m.test(frontmatter?.[1] ?? ""), `${path}: missing description`);
    check(/^version:\s*\S+$/m.test(frontmatter?.[1] ?? ""), `${path}: missing version`);
    check(frontmatter?.[1].match(/^version:\s*(.+)$/m)?.[1].trim() === readJson("package.json").version, `${path}: version does not match package.json`);
    check(/^# .+$/m.test(source.slice(frontmatter?.[0].length ?? 0)), `${path}: missing body H1`);
    check(source.split(/\r?\n/).length <= 350, `${path}: exceeds the 350-line entrypoint budget`);
    check(source.includes("node <plugin-root>/runtime/cli.mjs"), `${path}: must delegate through the local runtime`);
  }
  for (const command of CONTRACT.skills) {
    const path = `commands/${command}.md`;
    const source = read(path);
    check(source.includes("@HYPERFLOW_PLUGIN_ROOT@/runtime/cli.mjs"), `${path}: missing local CLI entrypoint`);
    check(source.includes(`@HYPERFLOW_PLUGIN_ROOT@/skills/${command}/SKILL.md`), `${path}: missing matching skill`);
    check(!/^model:/m.test(source), `${path}: must not pin the surrounding host model`);
  }
  check(existsSync(pathFromRoot("runtime/cli.mjs")), "runtime/cli.mjs: local runner is missing");
}

function checkJsonDocuments() {
  for (const path of filesUnder(".").filter((candidate) => extname(candidate) === ".json")) readJson(path);
}

function checkMarkdownLinks() {
  const documents = ["README.md", "PRIVACY.md", "RELEASING.md", ...filesUnder("docs").filter((path) => extname(path) === ".md"), ...filesUnder("skills").filter((path) => extname(path) === ".md"), ...filesUnder("commands").filter((path) => extname(path) === ".md")];
  for (const document of documents) {
    const source = read(document);
    for (const match of source.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
      const target = match[1].split("#", 1)[0];
      if (!target || /^(?:https?:|mailto:)/.test(target)) continue;
      const resolved = resolve(dirname(pathFromRoot(document)), decodeURIComponent(target));
      check(resolved === ROOT || resolved.startsWith(`${ROOT}${relative(ROOT, resolved).startsWith("/") ? "" : "/"}`), `${document}: link escapes repository (${target})`);
      check(existsSync(resolved), `${document}: broken local link ${target}`);
    }
  }
}

function checkShellSyntax() {
  const shellFiles = ["install.sh", ...filesUnder("scripts").filter((path) => extname(path) === ".sh")];
  try {
    execFileSync("bash", ["-n", ...shellFiles], { cwd: ROOT, stdio: "pipe" });
  } catch (error) {
    failures.push(`shell syntax: ${error.stderr?.toString().trim() || error.message}`);
  }
}

function currentSurface(path) {
  const source = read(path);
  const migrationDocs = new Set(["README.md", "PRIVACY.md", "docs/installation.md", "install.sh"]);
  if (!migrationDocs.has(path)) return source;
  return source
    .replace(/<!-- hyperflow:legacy-migration:start -->[\s\S]*?<!-- hyperflow:legacy-migration:end -->/g, "")
    .replace(/# hyperflow:legacy-migration:start[\s\S]*?# hyperflow:legacy-migration:end/g, "");
}

function checkRuntimeBoundary() {
  const allFiles = filesUnder(".");
  check(allFiles.every((path) => extname(path) !== ".p" + "y"), "runtime boundary: Python files must not ship");
  const manifest = readJson(".codex-plugin/plugin.json");
  check(!Object.hasOwn(manifest, "hooks"), "Codex manifest: hooks are not allowed in the inert runtime");
  const current = [
    "AGENTS.md", "CLAUDE.md", "PRIVACY.md", "README.md", "RELEASING.md", "install.sh", "package.json",
    ...[".claude-plugin", ".codex-plugin", ".github", "agents", "config", "docs", "evals", "scripts", "skills"]
      .flatMap(filesUnder),
  ].filter((path) => existsSync(pathFromRoot(path))).map(currentSurface);
  const shipped = current.join("\n");
  const startupMarkers = [
    ["hooks", "session-start"].join("/"),
    ["hooks", "pre-compact"].join("/"),
    ["scripts", "hook-runtime"].join("/"),
    "Session" + "Start",
    "Pre" + "Compact",
  ];
  const legacyMarkers = [
    [".hyperflow", "artefacts"].join("/"),
    ["artefact", "schema"].join("."),
    "render-" + "artefact",
    "open-" + "artefact",
  ];
  check(startupMarkers.every((marker) => !shipped.includes(marker)), "runtime boundary: startup hooks must not ship");
  check(legacyMarkers.every((marker) => !shipped.includes(marker)), "runtime boundary: legacy JSON artefact machinery must not ship");
}

function main() {
  checkVersionParity();
  checkSkillSurface();
  checkJsonDocuments();
  checkMarkdownLinks();
  checkShellSyntax();
  checkRuntimeBoundary();

  if (failures.length > 0) {
    console.error(`FAIL plugin-validation (${failures.length} issue${failures.length === 1 ? "" : "s"})`);
    for (const failure of failures) console.error(`  - ${failure}`);
    return 1;
  }
  console.log("PASS plugin-validation (version, skills, JSON, links, shell, and runtime boundary)");
  return 0;
}

process.exitCode = main();
