#!/usr/bin/env node
/**
 * CI GATE: skill and plugin detail-page link crawl (built site).
 *
 * Walks every built /skills/<slug>/ and /plugins/<name>/ page in dist/ and
 * fails when a same-site link on it would 404:
 *
 *   - page-relative hrefs (`references/x.md`, `../README.md`) — these resolve
 *     against the page URL, so they 404 as /skills/<slug>/references/x.md or,
 *     when the page is requested without its trailing slash, as
 *     /skills/references/x.md. Rendered repository markdown must emit an
 *     absolute target instead (see relative-link-resolver.mjs).
 *   - root-relative hrefs (`/skills/x/`) whose target is not in dist/.
 *
 * validate-internal-links.mjs covers only seven seed pages; detail pages are
 * where repository markdown is rendered, so they are crawled exhaustively.
 *
 * Usage: node validate-detail-page-links.mjs [--dist <dir>]
 * Exit:  0 clean, 1 broken links found (or dist missing).
 */

import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { extractInternalLinks, pathExistsInDist } from './internal-link-utils.mjs';

const DETAIL_SECTIONS = ['skills', 'plugins'];
const PROBE_ORIGIN = 'https://site.invalid';

function detailPages(distDirectory) {
  const pages = [];
  for (const section of DETAIL_SECTIONS) {
    const sectionDirectory = join(distDirectory, section);
    if (!existsSync(sectionDirectory)) continue;
    for (const entry of readdirSync(sectionDirectory, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const file = join(sectionDirectory, entry.name, 'index.html');
      if (existsSync(file)) pages.push({ file, route: `/${section}/${entry.name}/` });
    }
  }
  return pages.sort((left, right) => left.route.localeCompare(right.route));
}

/**
 * Crawl detail pages under distDirectory.
 * @returns {{ pages: number, links: number, broken: Array<{ route: string, href: string, reason: string, resolvesTo: string[] }> }}
 */
export function auditDetailPageLinks(distDirectory) {
  const broken = [];
  let links = 0;
  const pages = detailPages(distDirectory);
  const existence = new Map();
  const exists = (path) => {
    if (!existence.has(path)) existence.set(path, pathExistsInDist(distDirectory, path));
    return existence.get(path);
  };

  for (const { file, route } of pages) {
    const html = readFileSync(file, 'utf8');
    for (const { href } of extractInternalLinks(html, route)) {
      links += 1;
      if (!href.startsWith('/')) {
        // Both forms a browser or crawler can produce for this page.
        const resolvesTo = [route, route.replace(/\/$/, '')].map(
          (base) => new URL(href, `${PROBE_ORIGIN}${base}`).pathname,
        );
        broken.push({ route, href, reason: 'page-relative link', resolvesTo });
        continue;
      }
      if (!exists(href)) broken.push({ route, href, reason: 'target not built', resolvesTo: [href] });
    }
  }

  return { pages: pages.length, links, broken };
}

function main() {
  const flag = process.argv.indexOf('--dist');
  const distDirectory =
    flag === -1
      ? join(dirname(fileURLToPath(import.meta.url)), '..', 'dist')
      : resolve(process.argv[flag + 1]);

  if (!existsSync(distDirectory)) {
    console.error(`❌ Dist directory not found: ${distDirectory} (run \`npm run build\` first)`);
    process.exit(1);
  }

  const { pages, links, broken } = auditDetailPageLinks(distDirectory);
  console.log(`🔗 Detail-page link crawl: ${pages} pages, ${links} same-site links`);
  if (pages === 0) {
    console.error('❌ No skill or plugin detail pages found — refusing to report a vacuous pass');
    process.exit(1);
  }
  if (broken.length > 0) {
    console.error(`❌ ${broken.length} broken link(s):`);
    for (const { route, href, reason, resolvesTo } of broken.slice(0, 50)) {
      console.error(`   ${route}  ${href}  (${reason} → ${resolvesTo.join(' | ')})`);
    }
    if (broken.length > 50) console.error(`   … and ${broken.length - 50} more`);
    process.exit(1);
  }
  console.log('✅ No broken same-site links on skill or plugin detail pages');
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main();
