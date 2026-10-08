#!/usr/bin/env node

import { URL } from 'node:url';

/**
 * Shared markdown-to-HTML converter for marketplace build scripts.
 *
 * Used by:
 *   - discover-skills.mjs   (skill SKILL.md body content)
 *   - extract-readme-sections.mjs  (plugin README sections)
 *
 * Handles: fenced code blocks (with lang attribute), tables, headings h1-h6,
 * horizontal rules, ordered/unordered lists, bold, italic, inline code, links.
 * Zero runtime dependencies.
 */

export function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

const HTML_CHARACTER_REFERENCES = Object.freeze({
  amp: '&',
  apos: "'",
  colon: ':',
  gt: '>',
  lt: '<',
  newline: '\n',
  quot: '"',
  tab: '\t',
});

function decodeHtmlCharacterReferences(value) {
  return value.replace(
    /&(?:#(\d+)|#x([\da-f]+)|(amp|apos|colon|gt|lt|newline|quot|tab));?/gi,
    (match, decimal, hexadecimal, named) => {
      if (named) return HTML_CHARACTER_REFERENCES[named.toLowerCase()];

      const codePoint = Number.parseInt(decimal ?? hexadecimal, decimal ? 10 : 16);
      if (codePoint > 0x10ffff || (codePoint >= 0xd800 && codePoint <= 0xdfff)) return match;
      return String.fromCodePoint(codePoint);
    },
  );
}

function decodeLinkProbe(target) {
  let probe = target;

  // Multiple passes catch mixed or nested percent/entity encoding without ever
  // using the decoded value as the emitted href.
  for (let pass = 0; pass < 8; pass++) {
    let decoded;
    try {
      decoded = decodeURIComponent(probe);
    } catch {
      return null;
    }
    decoded = decodeHtmlCharacterReferences(decoded);
    if (decoded === probe) return decoded;
    probe = decoded;
  }

  // Extremely deep or deliberately cycling encodings fail closed rather than
  // being mistaken for a relative path after an arbitrary pass limit.
  return null;
}

function hasControlCharacter(value) {
  return [...value].some((character) => {
    const codePoint = character.codePointAt(0);
    return codePoint <= 0x1f || (codePoint >= 0x7f && codePoint <= 0x9f);
  });
}

function hasUnsafeRawLinkCharacters(value) {
  return hasControlCharacter(value) || [...'"\'<>`'].some((character) => value.includes(character));
}

/**
 * Links are an allowlist, not a best-effort scheme blacklist. The original
 * target must use an explicit supported form; the decoded probe is only used
 * to detect browser-relevant obfuscation.
 */
export function isSafeLinkTarget(target) {
  if (!target || target !== target.trim() || /\s/u.test(target)) return false;

  const probe = decodeLinkProbe(target);
  if (
    !probe ||
    hasUnsafeRawLinkCharacters(target) ||
    hasControlCharacter(probe)
  ) {
    return false;
  }

  const compactProbe = probe.replace(/\s/gu, '');
  if (/^(?:data|javascript|vbscript):/i.test(compactProbe)) return false;

  if (/^https:\/\//i.test(target)) {
    try {
      const parsed = new URL(target);
      return parsed.protocol === 'https:' && Boolean(parsed.hostname);
    } catch {
      return false;
    }
  }

  if (/^mailto:/i.test(target)) {
    return target.length > 'mailto:'.length;
  }

  if (target.startsWith('#')) return true;

  // Same-origin absolute paths, dot-relative paths, query references, and
  // ordinary relative paths are safe. Protocol-relative URLs, backslashes,
  // and any decoded first-segment scheme are deliberately excluded.
  if (target.includes('\\') || probe.includes('\\')) return false;
  if (target.startsWith('//') || probe.startsWith('//')) return false;
  if (/^[^/?#]*:/u.test(probe)) return false;

  return /^(?:\/(?!\/)|\.\.?\/|\?|[\p{L}\p{N}_~.%+-])/u.test(target);
}

function countRun(text, start, marker) {
  let end = start;
  while (text[end] === marker) end++;
  return end - start;
}

function isEscaped(text, index) {
  let backslashes = 0;
  for (let cursor = index - 1; cursor >= 0 && text[cursor] === '\\'; cursor--) backslashes++;
  return backslashes % 2 === 1;
}

function findCodeSpanEnd(text, start, delimiterLength) {
  for (let cursor = start; cursor < text.length; ) {
    if (text[cursor] !== '`' || isEscaped(text, cursor)) {
      cursor++;
      continue;
    }

    const runLength = countRun(text, cursor, '`');
    if (runLength === delimiterLength) return cursor;
    cursor += runLength;
  }
  return -1;
}

function findClosingBracket(text, start) {
  let depth = 1;

  for (let cursor = start; cursor < text.length; cursor++) {
    if (isEscaped(text, cursor)) continue;

    if (text[cursor] === '`') {
      const delimiterLength = countRun(text, cursor, '`');
      const end = findCodeSpanEnd(text, cursor + delimiterLength, delimiterLength);
      if (end !== -1) cursor = end + delimiterLength - 1;
      continue;
    }

    if (text[cursor] === '[') depth++;
    if (text[cursor] === ']' && --depth === 0) return cursor;
  }

  return -1;
}

function findClosingParenthesis(text, start) {
  let depth = 1;

  for (let cursor = start; cursor < text.length; cursor++) {
    if (isEscaped(text, cursor)) continue;
    if (text[cursor] === '(') depth++;
    if (text[cursor] === ')' && --depth === 0) return cursor;
  }

  return -1;
}

function isWordCharacter(character) {
  return Boolean(character && /[\p{L}\p{N}]/u.test(character));
}

function canOpenDelimiter(text, start, length, marker) {
  const before = text[start - 1];
  const after = text[start + length];
  if (!after || /\s/u.test(after)) return false;
  return marker !== '_' || !(isWordCharacter(before) && isWordCharacter(after));
}

function canCloseDelimiter(text, runStart, runLength, marker) {
  const before = text[runStart - 1];
  const after = text[runStart + runLength];
  if (!before || /\s/u.test(before)) return false;
  return marker !== '_' || !(isWordCharacter(before) && isWordCharacter(after));
}

function findClosingDelimiter(text, start, length, marker) {
  for (let cursor = start; cursor < text.length; ) {
    if (text[cursor] !== marker || isEscaped(text, cursor)) {
      cursor++;
      continue;
    }

    const runLength = countRun(text, cursor, marker);
    if (runLength >= length && canCloseDelimiter(text, cursor, runLength, marker)) {
      // Taking the end of a longer run makes ***nested emphasis*** resolve
      // into properly nested tags rather than crossing tag boundaries.
      return cursor + runLength - length;
    }
    cursor += runLength;
  }
  return -1;
}

/**
 * @param {string} text
 * @param {{ resolveLink?: (target: string) => string | null }} [options]
 *   resolveLink rewrites a link target before the safety allowlist runs; a
 *   null result renders the label as plain text (see relative-link-resolver).
 */
export function inlineFormat(text, options = {}) {
  const { resolveLink } = options;
  let html = '';
  let literal = '';

  const flushLiteral = () => {
    html += escapeHtml(literal);
    literal = '';
  };

  for (let cursor = 0; cursor < text.length; ) {
    const character = text[cursor];

    if (character === '`' && !isEscaped(text, cursor)) {
      const delimiterLength = countRun(text, cursor, '`');
      const end = findCodeSpanEnd(text, cursor + delimiterLength, delimiterLength);
      if (end !== -1) {
        flushLiteral();
        html += `<code>${escapeHtml(text.slice(cursor + delimiterLength, end))}</code>`;
        cursor = end + delimiterLength;
        continue;
      }

      // An unmatched run is literal as a whole. Reconsidering its second
      // character as a shorter opener would make malformed input ambiguous.
      literal += text.slice(cursor, cursor + delimiterLength);
      cursor += delimiterLength;
      continue;
    }

    if (character === '[' && !isEscaped(text, cursor)) {
      const labelEnd = findClosingBracket(text, cursor + 1);
      if (labelEnd !== -1 && text[labelEnd + 1] === '(') {
        const targetEnd = findClosingParenthesis(text, labelEnd + 2);
        if (targetEnd !== -1) {
          flushLiteral();
          const label = inlineFormat(text.slice(cursor + 1, labelEnd), options);
          const rawTarget = text.slice(labelEnd + 2, targetEnd);
          const target = resolveLink ? resolveLink(rawTarget) : rawTarget;
          html += target !== null && isSafeLinkTarget(target)
            ? `<a href="${escapeHtml(target)}">${label}</a>`
            : label;
          cursor = targetEnd + 1;
          continue;
        }
      }
    }

    if ((character === '*' || character === '_') && !isEscaped(text, cursor)) {
      const delimiterLength = Math.min(countRun(text, cursor, character), 2);
      if (canOpenDelimiter(text, cursor, delimiterLength, character)) {
        const end = findClosingDelimiter(
          text,
          cursor + delimiterLength,
          delimiterLength,
          character,
        );
        if (end !== -1) {
          flushLiteral();
          const tag = delimiterLength === 2 ? 'strong' : 'em';
          html += `<${tag}>${inlineFormat(text.slice(cursor + delimiterLength, end), options)}</${tag}>`;
          cursor = end + delimiterLength;
          continue;
        }
      }
    }

    literal += character;
    cursor++;
  }

  flushLiteral();
  return html;
}

/**
 * Convert a markdown string to HTML.
 *
 * Supports fenced code blocks (with optional language tag rendered as
 * `data-lang`), GFM-style pipe tables, headings (h1–h6), horizontal rules,
 * ordered and unordered lists, and inline formatting (bold, italic, code,
 * links).
 *
 * `options.resolveLink` (optional) rewrites link targets; callers rendering
 * repository markdown pass a relative-link resolver so links relative to the
 * source file do not become dead links relative to the page URL.
 */
export function mdToHtml(md, options = {}) {
  const format = (value) => inlineFormat(value, options);
  const lines = md.split('\n');
  const out = [];
  let inCodeBlock = false;
  let inList = false;
  let listType = null;
  let inTable = false;
  let paragraphLines = [];
  let listItemLines = [];

  const flushParagraph = () => {
    if (paragraphLines.length === 0) return;
    out.push(`<p>${format(paragraphLines.join(' '))}</p>`);
    paragraphLines = [];
  };

  const flushListItem = () => {
    if (listItemLines.length === 0) return;
    out.push(`<li>${format(listItemLines.join(' '))}</li>`);
    listItemLines = [];
  };

  const closeList = () => {
    if (!inList) return;
    flushListItem();
    out.push(`</${listType}>`);
    inList = false;
    listType = null;
  };

  const closeTable = () => {
    if (!inTable) return;
    out.push('</tbody></table>');
    inTable = false;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Fenced code blocks
    if (line.trimStart().startsWith('```')) {
      if (inCodeBlock) {
        out.push('</code></pre>');
        inCodeBlock = false;
      } else {
        flushParagraph();
        closeList();
        closeTable();
        const lang = line.trim().slice(3).trim();
        out.push(`<pre${lang ? ` data-lang="${escapeHtml(lang)}"` : ''}><code>`);
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      out.push(escapeHtml(line));
      continue;
    }

    const trimmed = line.trim();

    // Table rows (detect by pipe characters)
    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      flushParagraph();
      closeList();
      const cells = trimmed.slice(1, -1).split('|').map(c => c.trim());

      // Separator row (|---|---|)
      if (cells.every(c => /^[-:]+$/.test(c))) {
        continue;
      }

      if (!inTable) {
        out.push('<table><thead><tr>');
        cells.forEach(c => out.push(`<th>${format(c)}</th>`));
        out.push('</tr></thead><tbody>');
        inTable = true;
        continue;
      }

      out.push('<tr>');
      cells.forEach(c => out.push(`<td>${format(c)}</td>`));
      out.push('</tr>');
      continue;
    }

    // Close table if we hit a non-table line
    closeTable();

    // Empty line
    if (!trimmed) {
      flushParagraph();
      closeList();
      continue;
    }

    // Headings (h1-h6)
    const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      flushParagraph();
      closeList();
      const level = headingMatch[1].length;
      out.push(`<h${level}>${format(headingMatch[2])}</h${level}>`);
      continue;
    }

    // Horizontal rule
    if (/^[-*_]{3,}$/.test(trimmed)) {
      flushParagraph();
      closeList();
      out.push('<hr>');
      continue;
    }

    // Unordered list
    if (/^[-*+]\s/.test(trimmed)) {
      flushParagraph();
      if (!inList || listType !== 'ul') {
        closeList();
        out.push('<ul>');
        inList = true;
        listType = 'ul';
      } else {
        flushListItem();
      }
      listItemLines.push(trimmed.replace(/^[-*+]\s+/, ''));
      continue;
    }

    // Ordered list
    if (/^\d+[.)]\s/.test(trimmed)) {
      flushParagraph();
      if (!inList || listType !== 'ol') {
        closeList();
        out.push('<ol>');
        inList = true;
        listType = 'ol';
      } else {
        flushListItem();
      }
      listItemLines.push(trimmed.replace(/^\d+[.)]\s+/, ''));
      continue;
    }

    // Soft-wrapped paragraph and lazy list-item continuation lines are joined
    // before inline parsing so code/link/emphasis delimiters may span them.
    if (inList) listItemLines.push(trimmed);
    else paragraphLines.push(trimmed);
  }

  flushParagraph();
  closeList();
  if (inCodeBlock) out.push('</code></pre>');
  closeTable();

  return out.join('\n');
}
