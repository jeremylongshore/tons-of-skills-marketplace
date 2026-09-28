#!/usr/bin/env node

/**
 * Enforce STANDARDS.md as the only grant of document authority.
 *
 * Usage: node scripts/check-doc-authority.mjs [repository-root]
 */
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, posix, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { safeReadFile, UnsafePathError } from './safe-fs.mjs';

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const STATUS_FIELD =
  /^\s*(?:>\s*)*(?:(?:[-+*]|\d+[.)])\s+)?(?:\*\*Status\*\*\s*:|\*\*Status:\*\*|Status\s*:)\s*(.+?)\s*$/i;
const FROZEN_BANNER = /^\s*>\s*\*\*SUPERSEDED–FROZEN\b/;
function visibleMarkdownLines(lines) {
  let fence = null;
  let htmlComment = false;
  return lines.map((rawLine) => {
    if (fence) {
      const close = rawLine.match(/^ {0,3}(`{3,}|~{3,})[ \t]*$/)?.[1] ?? null;
      if (close && close[0] === fence.character && close.length >= fence.length) fence = null;
      return null;
    }

    let line = rawLine;
    let visible = '';
    while (line.length) {
      if (htmlComment) {
        const end = line.indexOf('-->');
        if (end === -1) return visible;
        htmlComment = false;
        line = line.slice(end + 3);
        continue;
      }
      const start = line.indexOf('<!--');
      if (start === -1) {
        visible += line;
        break;
      }
      visible += line.slice(0, start);
      htmlComment = true;
      line = line.slice(start + 4);
    }

    const opening = visible.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
    if (opening && !(opening[1][0] === '`' && opening[2].includes('`'))) {
      fence = { character: opening[1][0], length: opening[1].length };
      return null;
    }
    return visible;
  });
}

function canonicalTarget(linkCell) {
  const link = linkCell.match(/^\s*\[[^\]]+\]\(([^)]+)\)\s*$/);
  if (!link) throw new Error('each Canonical documents Document cell must be one active link');
  const href = link[1].trim();
  if (
    !href ||
    href.includes('#') ||
    href.includes('?') ||
    href.includes('%') ||
    /^[a-z][a-z+.-]*:/i.test(href) ||
    href.startsWith('/')
  )
    throw new Error(`invalid canonical Document link: ${JSON.stringify(href)}`);
  const normalized = posix.normalize(href.replace(/^\.\//, ''));
  if (normalized === '..' || normalized.startsWith('../'))
    throw new Error(`canonical Document link escapes the repository: ${JSON.stringify(href)}`);
  return normalized;
}

export function canonicalDocumentLinks(standardsText, trackedPaths = null) {
  const lines = standardsText.split(/\r?\n/);
  const visible = visibleMarkdownLines(lines);
  const headings = visible
    .map((line, index) => (/^##\s+Canonical documents\s*$/i.test(line) ? index : -1))
    .filter((index) => index !== -1);
  if (headings.length !== 1)
    throw new Error(
      `STANDARDS.md must contain exactly one "## Canonical documents" section (found ${headings.length})`,
    );

  const heading = headings[0];
  let end = lines.length;
  for (let index = heading + 1; index < lines.length; index += 1) {
    if (visible[index] && /^##\s+/.test(visible[index])) {
      end = index;
      break;
    }
  }

  const sectionLines = visible.slice(heading + 1, end);
  const tableStarts = sectionLines
    .map((line, index) => {
      if (line === null) return -1;
      const cells = line
        .split('|')
        .slice(1, -1)
        .map((cell) => cell.trim().toLowerCase());
      return cells.length === 2 && cells[0] === 'topic' && cells[1] === 'document' ? index : -1;
    })
    .filter((index) => index !== -1);
  if (tableStarts.length !== 1)
    throw new Error(
      `Canonical documents section must contain exactly one Topic | Document table (found ${tableStarts.length})`,
    );

  const tableRows = [];
  for (const line of sectionLines.slice(tableStarts[0])) {
    if (line === null || !/^\s*\|/.test(line)) break;
    tableRows.push(line);
  }
  if (tableRows.length < 3)
    throw new Error('Canonical documents table is missing or has no data rows');

  const headerCells = tableRows[0]
    .split('|')
    .slice(1, -1)
    .map((cell) => cell.trim().toLowerCase());
  if (headerCells.length !== 2 || headerCells[0] !== 'topic' || headerCells[1] !== 'document')
    throw new Error('Canonical documents table must have exactly the columns Topic | Document');
  const delimiterCells = tableRows[1]
    .split('|')
    .slice(1, -1)
    .map((cell) => cell.trim());
  if (delimiterCells.length !== 2 || delimiterCells.some((cell) => !/^:?-{3,}:?$/.test(cell)))
    throw new Error('Canonical documents table is missing its delimiter row');

  const links = new Set();
  for (const row of tableRows.slice(2)) {
    const cells = row
      .split('|')
      .slice(1, -1)
      .map((cell) => cell.trim());
    if (cells.length !== 2) throw new Error(`malformed Canonical documents row: ${row.trim()}`);
    const target = canonicalTarget(cells[1]);
    if (trackedPaths && !trackedPaths.has(target))
      throw new Error(`canonical Document target is not tracked: ${target}`);
    links.add(target);
  }
  if (links.size === 0) throw new Error('Canonical documents table has no document links');
  return links;
}

function claimToken(value) {
  const normalized = value.replace(/[*_`]/g, '');
  const direct = normalized.match(/^\s*(AUTHORITATIVE|CANONICAL)\b/i);
  if (direct) return direct[1].toUpperCase();
  const activation = normalized.match(/\bbecomes\s+(AUTHORITATIVE|CANONICAL)\b/i);
  return activation?.[1].toUpperCase() ?? null;
}

function preambleLines(contents) {
  const lines = contents.split(/\r?\n/);
  const visible = visibleMarkdownLines(lines);
  const firstContentIndex = visible.findIndex((line) => line?.trim());
  if (firstContentIndex === -1) return { frozen: false, lines: [] };
  if (FROZEN_BANNER.test(visible[firstContentIndex])) return { frozen: true, lines: [] };

  const preamble = [];
  let sawH1 = false;
  for (let index = 0; index < visible.length; index += 1) {
    const line = visible[index];
    if (line === null) continue;
    if (/^#\s+/.test(line)) sawH1 = true;
    if (sawH1 && (/^##\s+/.test(line) || /^\s*(?:---+|___+|\*\*\*+)\s*$/.test(line))) break;
    preamble.push({ line: index + 1, text: line });
  }
  return { frozen: false, lines: preamble };
}

export function inspectAuthorityMetadata(contents) {
  const preamble = preambleLines(contents);
  if (preamble.frozen) return { claim: null, errors: [] };

  const statuses = [];
  for (const item of preamble.lines) {
    const match = item.text.match(STATUS_FIELD);
    if (match) statuses.push({ line: item.line, value: match[1].trim() });
  }
  if (statuses.length > 1) {
    return {
      claim: null,
      errors: [
        {
          reason: 'DOC_AUTHORITY_AMBIGUOUS_STATUS',
          line: statuses[1].line,
          value: statuses.map((status) => status.value).join(' | '),
        },
      ],
    };
  }
  if (statuses.length === 0) return { claim: null, errors: [] };

  const token = claimToken(statuses[0].value);
  return {
    claim: token
      ? { kind: `STATUS_${token}`, line: statuses[0].line, value: statuses[0].value }
      : null,
    errors: [],
  };
}

export function effectiveAuthorityClaim(contents) {
  return inspectAuthorityMetadata(contents).claim;
}

export function checkAuthorityGraph({ standardsText, documents, trackedPaths = null }) {
  const canonicalLinks = canonicalDocumentLinks(standardsText, trackedPaths);
  const claimants = [];
  const findings = [];

  for (const document of documents) {
    const inspection = inspectAuthorityMetadata(document.contents);
    for (const error of inspection.errors) findings.push({ path: document.path, ...error });
    if (!inspection.claim) continue;
    const item = { path: document.path, ...inspection.claim };
    claimants.push(item);
    if (!canonicalLinks.has(document.path))
      findings.push({ reason: 'DOC_AUTHORITY_UNLINKED', ...item });
  }

  return { canonicalLinks, claimants, findings };
}

export function scanRepository(root = repositoryRoot) {
  const tracked = execFileSync('git', ['-C', root, 'ls-files', '-z'], {
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024,
  })
    .split('\0')
    .filter(Boolean);
  if (tracked.length === 0) throw new Error('Git reported no tracked repository files');
  const trackedPaths = new Set(tracked);
  const markdownDocs = tracked.filter(
    (path) => path.startsWith('000-docs/') && path.endsWith('.md'),
  );
  if (markdownDocs.length === 0)
    throw new Error('Git reported no tracked Markdown documents in 000-docs');

  const documents = markdownDocs.map((path) => {
    try {
      return { path, contents: safeReadFile(resolve(root), path).content.toString('utf8') };
    } catch (error) {
      if (error instanceof UnsafePathError) {
        throw new Error(`tracked document is not a regular file: ${path}`);
      }
      throw error;
    }
  });
  return checkAuthorityGraph({
    standardsText: readFileSync(resolve(root, 'STANDARDS.md'), 'utf8'),
    documents,
    trackedPaths,
  });
}

export function formatAuthorityReport(result) {
  if (result.findings.length === 0)
    return `document-authority: OK (${result.claimants.length} effective claimant documents; ${result.canonicalLinks.size} canonical-table links)`;

  const lines = result.findings.map((finding) => {
    if (finding.reason === 'DOC_AUTHORITY_UNLINKED')
      return `${finding.reason} ${finding.path}:${finding.line} declares ${finding.kind} (${JSON.stringify(finding.value)}) but STANDARDS.md § Canonical documents does not link it`;
    return `${finding.reason} ${finding.path}:${finding.line} has conflicting preamble status fields (${JSON.stringify(finding.value)})`;
  });
  lines.push(
    `document-authority: ${result.findings.length} violation(s) among ${result.claimants.length} effective claimant documents`,
  );
  return lines.join('\n');
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const result = scanRepository(process.argv[2] ? resolve(process.argv[2]) : repositoryRoot);
    const report = formatAuthorityReport(result);
    if (result.findings.length) {
      console.error(report);
      process.exitCode = 1;
    } else console.log(report);
  } catch (error) {
    console.error(`DOC_AUTHORITY_CONFIG_ERROR ${error.message}`);
    process.exitCode = 1;
  }
}
