#!/usr/bin/env node

/** Validate completed supersession records without interpreting frozen documents. */
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { safeReadFile, UnsafePathError } from './safe-fs.mjs';

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DEFAULT_TEMPLATE = '000-docs/746-DR-TMPL-document-supersession.md';
const BEGIN = '<!-- BEGIN SUPERSESSION RECORD -->';
const END = '<!-- END SUPERSESSION RECORD -->';
const FROZEN_MARKER = '<!-- doc-class: frozen -->';
const EXPECTED_COLUMNS = ['superseded section', 'disposition', 'new authority'];
const ALLOWED_DISPOSITIONS = new Set([
  'CARRIED FORWARD',
  'REPLACED',
  'REVERSED',
  'SUPERSEDED WITHOUT REPLACEMENT',
]);
const RECORD_MISSING = 'SUPERSESSION_RECORD_MISSING';

function finding(code, message, line = null, record = null) {
  return {
    code,
    message,
    ...(line === null ? {} : { line }),
    ...(record === null ? {} : { record }),
  };
}

function stripComments(rawLine, state) {
  let line = rawLine;
  let visible = '';
  while (line.length) {
    if (state.htmlComment > 0) {
      const start = line.indexOf('<!--');
      const end = line.indexOf('-->');
      if (start !== -1 && (end === -1 || start < end)) {
        state.htmlComment += 1;
        line = line.slice(start + 4);
        continue;
      }
      if (end === -1) return visible;
      state.htmlComment -= 1;
      line = line.slice(end + 3);
      continue;
    }
    const start = line.indexOf('<!--');
    if (start === -1) return visible + line;
    visible += line.slice(0, start);
    state.htmlComment += 1;
    line = line.slice(start + 4);
  }
  return visible;
}

function fenceToken(line) {
  return line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
}

function hasVisibleInlineMachineMarker(rawLine, initialCommentDepth) {
  const target = `\`${FROZEN_MARKER}\``;
  let line = rawLine;
  let depth = initialCommentDepth;

  while (line.length) {
    if (depth > 0) {
      const start = line.indexOf('<!--');
      const end = line.indexOf('-->');
      if (start !== -1 && (end === -1 || start < end)) {
        depth += 1;
        line = line.slice(start + 4);
        continue;
      }
      if (end === -1) return false;
      depth -= 1;
      line = line.slice(end + 3);
      continue;
    }

    const targetIndex = line.indexOf(target);
    const commentIndex = line.indexOf('<!--');
    if (targetIndex !== -1 && (commentIndex === -1 || targetIndex < commentIndex)) return true;
    if (commentIndex === -1) return false;
    depth += 1;
    line = line.slice(commentIndex + 4);
  }

  return false;
}

/** Extract exact, visible completed-record blocks and delimiter errors. */
export function parseSupersessionRecords(markdown) {
  if (typeof markdown !== 'string') throw new TypeError('markdown must be a string');

  const records = [];
  const findings = [];
  const state = { fence: null, htmlComment: 0 };
  let current = null;
  const lines = markdown.split(/\r?\n/);

  for (let index = 0; index < lines.length; index += 1) {
    const raw = lines[index];
    const lineNumber = index + 1;

    if (state.fence) {
      const close = raw.match(/^ {0,3}(`{3,}|~{3,})[ \t]*$/)?.[1] ?? null;
      if (close && close[0] === state.fence.character && close.length >= state.fence.length)
        state.fence = null;
      if (current) current.lines.push({ line: lineNumber, raw, visible: '' });
      continue;
    }

    const trimmed = raw.trim();
    if (!state.htmlComment && (trimmed === BEGIN || trimmed === END)) {
      if (trimmed === BEGIN) {
        if (current) {
          findings.push(
            finding(
              'SUPERSESSION_RECORD_NESTED_BEGIN',
              'a completed record cannot contain another begin marker',
              lineNumber,
              current.index,
            ),
          );
        } else {
          current = { index: records.length + 1, startLine: lineNumber, endLine: null, lines: [] };
        }
      } else if (!current) {
        findings.push(
          finding(
            'SUPERSESSION_RECORD_UNEXPECTED_END',
            'end marker has no matching visible begin marker',
            lineNumber,
          ),
        );
      } else {
        current.endLine = lineNumber;
        records.push(current);
        current = null;
      }
      continue;
    }

    if (!state.htmlComment && current && trimmed === FROZEN_MARKER) {
      current.lines.push({ line: lineNumber, raw, visible: '', machineMarker: true });
      continue;
    }

    const inlineMachineMarker = current && hasVisibleInlineMachineMarker(raw, state.htmlComment);
    const visible = stripComments(raw, state);
    const opening = !state.htmlComment && fenceToken(visible);
    if (opening && !(opening[1][0] === '`' && opening[2].includes('`'))) {
      state.fence = { character: opening[1][0], length: opening[1].length };
      if (current) current.lines.push({ line: lineNumber, raw, visible: '' });
      continue;
    }
    if (current)
      current.lines.push({ line: lineNumber, raw, visible, machineMarker: inlineMachineMarker });
  }

  if (current)
    findings.push(
      finding(
        'SUPERSESSION_RECORD_UNCLOSED',
        'completed record is missing its exact end marker',
        current.startLine,
        current.index,
      ),
    );
  if (records.length === 0)
    findings.push(
      finding(
        'SUPERSESSION_RECORD_MISSING',
        'no visible completed supersession record block was found',
      ),
    );

  return { records, findings };
}

function tableCells(line) {
  if (!/^\s*\|.*\|\s*$/.test(line)) return null;
  return line
    .trim()
    .slice(1, -1)
    .split('|')
    .map((cell) => cell.trim());
}

function normalizedHeader(cell) {
  return cell.replace(/[*_`]/g, '').trim().toLowerCase().replace(/\s+/g, ' ');
}

function normalizedDisposition(cell) {
  return cell.replace(/[*_`]/g, '').trim().toUpperCase().replace(/\s+/g, ' ');
}

function isNegated(text) {
  const normalized = text
    .replace(/\bdo(?:\s+not|n['’]t)\s+forget\s+to\b/gi, 'must')
    .replace(/\bnot\s+only\b/gi, '')
    .replace(/\bunchanged\s+from\b/gi, 'consistent with');
  return /\b(?:(?:is|are|was|were|do|does|did|has|have|had|could|should|would|must)n['’]t|can['’]t|won['’]t|do\s+not|does\s+not|did\s+not|fail(?:s|ed)?\s+to|cannot|not|never|without|avoid(?:s|ed|ing)?|refus(?:e|es|ed|ing)|prohibit(?:s|ed|ing)?|forbid(?:s|den|ding)?|omit(?:s|ted|ting)?|skip(?:s|ped|ping)?|unchanged)\b/i.test(
    normalized,
  );
}

function isDirectBannerEvidence(text) {
  // A title-only controlled blockquote is the evidence. Prose belongs in the
  // structured record fields; accepting it here would require interpreting an
  // unbounded set of contradictory or obfuscated natural-language claims.
  return /^ {0,3}>[ \t]+\*\*SUPERSEDED–FROZEN(?: \([A-Za-z0-9][A-Za-z0-9 .;:/#-]*\))?\.\*\*[ \t]*$/.test(
    text,
  );
}

function directBannerBlockText(lines, startIndex) {
  const parts = [];
  for (let index = startIndex - 1; index >= 0; index -= 1) {
    const item = lines[index];
    const visible = item.visible.trim();
    const raw = item.raw.trim();
    if (/^(?:#{1,6}\s|[-+*]\s|\d+[.)]\s|\|)/.test(visible)) break;
    if (raw && !item.machineMarker) parts.unshift(item.raw.trimEnd());
  }
  parts.push(lines[startIndex].raw.trimEnd());
  for (const item of lines.slice(startIndex + 1)) {
    const visible = item.visible.trim();
    const raw = item.raw.trim();
    if (!visible) {
      if (raw && !item.machineMarker) parts.push(raw);
      continue;
    }
    // Markdown permits lazy continuations and separate blockquote paragraphs.
    // Inspect everything until the next record structure so neither can append
    // a contradictory claim to an otherwise valid title.
    if (/^(?:#{1,6}\s|[-+*]\s|\d+[.)]\s|\|)/.test(visible)) break;
    parts.push(item.raw.trimEnd());
  }
  return parts.join('\n');
}

function isPlaceholder(text) {
  return (
    /\b(?:TODO|TBD|TBC|FIXME|CHANGEME|PLACEHOLDER|REPLACE\s+ME|NNN)\b/i.test(text) ||
    /\bYYYY-MM-DD\b/i.test(text) ||
    /<(?:insert|replace|old|new|path|table|document|section|authority|date|value)[^>]*>/i.test(
      text,
    ) ||
    /\[(?:insert|placeholder|section|new authority|document|path|date)[^\]]*\]/i.test(text)
  );
}

function checkedItems(record) {
  return record.lines
    .map((item) => ({ line: item.line, match: item.visible.match(/^\s*[-+*]\s+\[[xX]\]\s+(.+)$/) }))
    .filter((item) => item.match)
    .map((item) => ({ line: item.line, text: item.match[1].trim() }));
}

function continuedListItemText(lines, startIndex) {
  const parts = [lines[startIndex].visible.trim()];
  for (const item of lines.slice(startIndex + 1)) {
    const text = item.visible.trim();
    if (!text || /^(?:[-+*]\s|>|#|\|)/.test(text)) break;
    parts.push(text);
  }
  return parts.join(' ');
}

function inspectRecord(record) {
  const findings = [];
  const markerLines = record.lines.filter((item) => item.machineMarker);
  if (markerLines.length === 0)
    findings.push(
      finding(
        'SUPERSESSION_FROZEN_MARKER_MISSING',
        `record must contain the exact marker ${FROZEN_MARKER}`,
        record.startLine,
        record.index,
      ),
    );

  const bannerLines = record.lines.filter((item, index) => {
    if (/^\s*>\s+\*\*SUPERSEDED–FROZEN\b/.test(item.visible))
      return isDirectBannerEvidence(directBannerBlockText(record.lines, index));
    if (!/^\s*[-+*]\s+\*\*Frozen header:\*\*/i.test(item.visible)) return false;
    const field = continuedListItemText(record.lines, index);
    return /\bSUPERSEDED–FROZEN\b/.test(field) && !isNegated(field);
  });
  if (bannerLines.length === 0)
    findings.push(
      finding(
        'SUPERSESSION_FROZEN_BANNER_MISSING',
        'record must contain a visible SUPERSEDED–FROZEN banner',
        record.startLine,
        record.index,
      ),
    );

  const visibleText = record.lines.map((item) => item.visible).join('\n');
  const placeholderLine = record.lines.find((item) => isPlaceholder(item.visible));
  if (placeholderLine)
    findings.push(
      finding(
        'SUPERSESSION_PLACEHOLDER_PRESENT',
        'completed records cannot contain placeholder tokens',
        placeholderLine.line,
        record.index,
      ),
    );

  const headers = record.lines.filter((item) => {
    const cells = tableCells(item.visible);
    return cells && cells.map(normalizedHeader).join('\0') === EXPECTED_COLUMNS.join('\0');
  });
  let dispositionRows = [];
  if (headers.length === 0) {
    findings.push(
      finding(
        'SUPERSESSION_DISPOSITION_TABLE_MISSING',
        `record must contain the columns ${EXPECTED_COLUMNS.join(' | ')}`,
        record.startLine,
        record.index,
      ),
    );
  } else if (headers.length > 1) {
    findings.push(
      finding(
        'SUPERSESSION_DISPOSITION_TABLE_AMBIGUOUS',
        'record must contain exactly one disposition table',
        headers[1].line,
        record.index,
      ),
    );
  } else {
    const headerIndex = record.lines.indexOf(headers[0]);
    const delimiter = record.lines[headerIndex + 1];
    const delimiterCells = delimiter ? tableCells(delimiter.visible) : null;
    if (
      !delimiterCells ||
      delimiterCells.length !== EXPECTED_COLUMNS.length ||
      delimiterCells.some((cell) => !/^:?-{3,}:?$/.test(cell))
    ) {
      findings.push(
        finding(
          'SUPERSESSION_DISPOSITION_TABLE_MALFORMED',
          'disposition table requires a three-column Markdown delimiter row',
          delimiter?.line ?? headers[0].line,
          record.index,
        ),
      );
    } else {
      for (const item of record.lines.slice(headerIndex + 2)) {
        if (!item.visible.trim()) break;
        const cells = tableCells(item.visible);
        if (!cells) break;
        if (cells.length !== EXPECTED_COLUMNS.length || cells.some((cell) => !cell)) {
          findings.push(
            finding(
              'SUPERSESSION_DISPOSITION_TABLE_MALFORMED',
              'each disposition row must contain exactly three nonempty cells',
              item.line,
              record.index,
            ),
          );
          continue;
        }
        const disposition = normalizedDisposition(cells[1]);
        if (!ALLOWED_DISPOSITIONS.has(disposition)) {
          findings.push(
            finding(
              'SUPERSESSION_DISPOSITION_INVALID',
              `disposition must be one of ${[...ALLOWED_DISPOSITIONS].join(', ')}`,
              item.line,
              record.index,
            ),
          );
        }
        dispositionRows.push({ line: item.line, cells, disposition });
      }
      if (dispositionRows.length === 0)
        findings.push(
          finding(
            'SUPERSESSION_DISPOSITION_ROW_MISSING',
            'disposition table must contain at least one completed data row',
            headers[0].line,
            record.index,
          ),
        );
      else if (dispositionRows.every((row) => row.cells.some(isPlaceholder)))
        findings.push(
          finding(
            'SUPERSESSION_DISPOSITION_ROW_MISSING',
            'disposition table must contain at least one non-placeholder data row',
            dispositionRows[0].line,
            record.index,
          ),
        );
    }
  }

  const checklist = checkedItems(record);
  const pointer = checklist.find(
    (item) =>
      /\bSTANDARDS\.md\b/i.test(item.text) &&
      /\bCanonical documents\b/i.test(item.text) &&
      /\b(?:pointer|link(?:s|ed|ing)?|update[sd]?)\b/i.test(item.text) &&
      !isNegated(item.text),
  );
  if (!pointer)
    findings.push(
      finding(
        'SUPERSESSION_CANONICAL_POINTER_TASK_MISSING',
        'record requires a checked STANDARDS.md Canonical documents pointer task',
        record.startLine,
        record.index,
      ),
    );

  const atomicity = record.lines.find(
    (item) =>
      /\batomic(?:\s+PR|ity|ally)?\b/i.test(item.visible) &&
      /\b(?:one|same|single)\s+(?:pull request|PR)\b/i.test(item.visible) &&
      !isNegated(item.visible),
  );
  if (!atomicity)
    findings.push(
      finding(
        'SUPERSESSION_ONE_PR_ATOMICITY_MISSING',
        'record requires a checked atomicity statement naming one PR',
        record.startLine,
        record.index,
      ),
    );

  return {
    index: record.index,
    startLine: record.startLine,
    endLine: record.endLine,
    elements: {
      frozenMarker: markerLines.length > 0,
      frozenBanner: bannerLines.length > 0,
      dispositionRows: dispositionRows.length,
      canonicalPointerTask: pointer?.line ?? null,
      onePrAtomicity: atomicity?.line ?? null,
    },
    findings,
    text: visibleText,
  };
}

/** Check all visible completed record blocks in a Markdown document. */
export function checkSupersessionTemplate(markdown) {
  const parsed = parseSupersessionRecords(markdown);
  const records = parsed.records.map(inspectRecord);
  const findings = [...parsed.findings, ...records.flatMap((record) => record.findings)];
  return { ok: findings.length === 0, records, findings };
}

/** Check only documents that contain or attempt a visible completed-record block. */
export function checkSupersessionCorpus(documents) {
  if (!Array.isArray(documents)) throw new TypeError('documents must be an array');
  const checked = [];
  for (const document of documents) {
    if (!document || typeof document.path !== 'string' || typeof document.markdown !== 'string')
      throw new TypeError('each document requires string path and markdown fields');
    const result = checkSupersessionTemplate(document.markdown);
    const applicable =
      result.records.length > 0 || result.findings.some((item) => item.code !== RECORD_MISSING);
    if (applicable) checked.push({ path: document.path, ...result });
  }
  return {
    ok: checked.length > 0 && checked.every((document) => document.ok),
    documents: checked,
    recordCount: checked.reduce((sum, document) => sum + document.records.length, 0),
  };
}

export function trackedDocumentationPaths(root = repositoryRoot) {
  const listed = spawnSync('git', ['ls-files', '-z', '--', '000-docs'], {
    cwd: root,
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024,
  });
  if (listed.error || listed.status !== 0)
    throw new Error(`cannot list tracked documentation: ${listed.error?.message ?? listed.stderr}`);
  return listed.stdout
    .split('\0')
    .filter((path) => path.endsWith('.md'))
    .sort();
}

export function readTrackedDocumentation(root = repositoryRoot) {
  const lexicalRoot = resolve(root);
  return trackedDocumentationPaths(root).map((path) => {
    const absolute = resolve(lexicalRoot, path);
    if (!absolute.startsWith(`${lexicalRoot}${sep}`))
      throw new Error(`tracked documentation path escapes repository: ${path}`);
    // safe-fs refuses links anywhere under the root, special files, and a path
    // swapped between check and open, in one verified read.
    try {
      return { path, markdown: safeReadFile(lexicalRoot, path).content.toString('utf8') };
    } catch (error) {
      if (error instanceof UnsafePathError) {
        throw new Error(`tracked documentation path is not a regular file: ${path}`);
      }
      throw error;
    }
  });
}

export function formatSupersessionReport(result, path = DEFAULT_TEMPLATE) {
  if (result.ok)
    return `supersession-template: OK (${result.records.length} completed record(s)) ${path}`;
  const lines = result.findings.map((item) => {
    const location = item.line ? `:${item.line}` : '';
    const record = item.record ? ` record=${item.record}` : '';
    return `${item.code} ${path}${location}${record} ${item.message}`;
  });
  lines.push(`supersession-template: ${result.findings.length} violation(s) ${path}`);
  return lines.join('\n');
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const args = process.argv.slice(2);
    if (args.length > 1 || (args.length === 1 && args[0].startsWith('--') && args[0] !== '--all'))
      throw new Error('usage: check-supersession-template.mjs [--all | <document>]');
    if (args[0] === '--all') {
      const corpus = checkSupersessionCorpus(readTrackedDocumentation());
      for (const document of corpus.documents) {
        if (!document.ok) console.error(formatSupersessionReport(document, document.path));
      }
      if (!corpus.ok) {
        if (corpus.documents.length === 0)
          console.error('SUPERSESSION_CORPUS_RECORD_MISSING no tracked completed record was found');
        process.exitCode = 1;
      } else {
        console.log(
          `supersession-corpus: OK (${corpus.recordCount} completed record(s) in ${corpus.documents.length} tracked document(s))`,
        );
      }
    } else {
      const suppliedPath = args[0] ?? DEFAULT_TEMPLATE;
      const templatePath = args[0]
        ? resolve(process.cwd(), suppliedPath)
        : resolve(repositoryRoot, DEFAULT_TEMPLATE);
      const result = checkSupersessionTemplate(readFileSync(templatePath, 'utf8'));
      const report = formatSupersessionReport(result, suppliedPath);
      if (result.ok) console.log(report);
      else {
        console.error(report);
        process.exitCode = 1;
      }
    }
  } catch (error) {
    console.error(`SUPERSESSION_TEMPLATE_IO_ERROR ${error.message}`);
    process.exitCode = 1;
  }
}
