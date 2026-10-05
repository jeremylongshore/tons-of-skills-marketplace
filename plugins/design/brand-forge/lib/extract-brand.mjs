// extract-brand.mjs — propose a starter palette + fonts from an existing asset,
// so /brand-new can pre-fill its Q&A instead of asking for everything by hand.
//
// The local extractors (SVG, CSS/HTML, PDF) are pure Node: no network, no
// dependencies. The URL importer lives in a separate, opt-in module and is the
// ONLY part that touches the network.
//
// Everything returned here is a *proposal*. /brand-new shows it to the user to
// confirm or edit; nothing is silently trusted.

import { readFileSync } from 'node:fs';
import { extname } from 'node:path';

const GENERIC_FONTS = new Set([
  'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui',
  'ui-serif', 'ui-sans-serif', 'ui-monospace', 'inherit', 'initial', 'unset',
  '-apple-system', 'blinkmacsystemfont',
]);

// --- color collection -------------------------------------------------------

const clamp = (n) => Math.max(0, Math.min(255, n | 0));
const toHex = (r, g, b) =>
  '#' + [r, g, b].map((n) => clamp(n).toString(16).padStart(2, '0')).join('');

// Expand #abc -> #aabbcc, lowercase.
function normHex(h) {
  h = h.toLowerCase();
  if (h.length === 4) h = '#' + [...h.slice(1)].map((c) => c + c).join('');
  return h;
}

// Map<hex, count> for hex, rgb(), and rgba() colors found in `text`.
export function collectColors(text) {
  const counts = new Map();
  const bump = (hex) => counts.set(hex, (counts.get(hex) ?? 0) + 1);
  for (const m of text.matchAll(/#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b/g)) bump(normHex(m[0]));
  for (const m of text.matchAll(/rgba?\(\s*(\d{1,3})[,\s]+(\d{1,3})[,\s]+(\d{1,3})/gi))
    bump(toHex(+m[1], +m[2], +m[3]));
  return counts;
}

// Top-N most frequent colors (frequency desc).
export function rankPalette(counts, n = 6) {
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, n).map(([hex]) => hex);
}

// --- font collection --------------------------------------------------------

// Candidate families from CSS `font-family:` and SVG `font-family="..."`,
// skipping generic keywords, in first-seen order.
export function collectFonts(text) {
  const seen = new Set();
  const out = [];
  for (const m of text.matchAll(/font-family\s*[:=]\s*["']?([^"';{}<>]+)/gi)) {
    const first = m[1].split(',')[0].trim().replace(/^["']|["']$/g, '');
    const key = first.toLowerCase();
    if (!first || GENERIC_FONTS.has(key) || seen.has(key)) continue;
    seen.add(key);
    out.push(first);
  }
  return out;
}

// --- extractors -------------------------------------------------------------

// SVG, CSS, and HTML are all text: one color+font scan covers them.
export function extractFromText(text) {
  return { palette: rankPalette(collectColors(text)), fonts: collectFonts(text) };
}

// PDF: embedded font names (/BaseFont) + best-effort fill colors (rg operator,
// 0..1 floats). Read as latin1 so binary streams never throw.
export function extractFromPdf(buf) {
  const s = Buffer.isBuffer(buf) ? buf.toString('latin1') : String(buf);
  const seen = new Set();
  const fonts = [];
  for (const m of s.matchAll(/\/BaseFont\s*\/([A-Za-z0-9.+_-]+)/g)) {
    const name = m[1]
      .replace(/^[A-Z]{6}\+/, '')                                        // subset prefix
      .replace(/[-,](Bold|Italic|Regular|Light|Medium|SemiBold|Oblique)+$/i, ''); // weight
    const key = name.toLowerCase();
    if (name && !seen.has(key)) { seen.add(key); fonts.push(name); }
  }
  const counts = new Map();
  for (const m of s.matchAll(/(\d?\.\d+|[01])\s+(\d?\.\d+|[01])\s+(\d?\.\d+|[01])\s+rg\b/gi))
    counts.set(toHex(Math.round(+m[1] * 255), Math.round(+m[2] * 255), Math.round(+m[3] * 255)),
      (counts.get(toHex(Math.round(+m[1] * 255), Math.round(+m[2] * 255), Math.round(+m[3] * 255))) ?? 0) + 1);
  return { palette: rankPalette(counts), fonts };
}

// Dispatch a local file by extension. Raster images (PNG/JPEG) need a decoder
// and are intentionally out of scope for the dependency-free local path — use
// an SVG, a PDF, a CSS/HTML file, or a URL instead.
export function extractFromFile(path) {
  const ext = extname(path).toLowerCase();
  if (ext === '.svg' || ext === '.css' || ext === '.html' || ext === '.htm')
    return extractFromText(readFileSync(path, 'utf8'));
  if (ext === '.pdf') return extractFromPdf(readFileSync(path));
  throw new Error(
    `extract-brand: unsupported local type "${ext || 'unknown'}". ` +
    `Use .svg, .pdf, .css, .html, or pass a URL.`,
  );
}
