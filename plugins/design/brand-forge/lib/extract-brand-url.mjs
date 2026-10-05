// extract-brand-url.mjs — the ONE networked path used by /brand-new: fetch a
// website and propose a palette + fonts from its CSS. Opt-in: only runs when
// the user passes a URL. Isolated here so the vector core stays network-free
// (the only other networked module is genimage.mjs).
//
// Guards: http(s) only; DNS-resolved private/loopback/reserved addresses are
// refused (SSRF); redirects are re-validated hop by hop; the body is size- and
// time-capped. `fetch` and `resolve` are injectable so tests never hit the network.

import { lookup } from 'node:dns/promises';
import { isIP } from 'node:net';
import { collectColors, rankPalette, collectFonts } from './extract-brand.mjs';

function ipv4Private(ip) {
  const p = ip.split('.').map(Number);
  if (p.length !== 4 || p.some((n) => !Number.isInteger(n) || n < 0 || n > 255)) return true; // malformed → refuse
  const [a, b] = p;
  return (
    a === 0 || a === 10 || a === 127 || a >= 224 ||   // this-net, private, loopback, multicast/reserved
    (a === 169 && b === 254) ||                        // link-local
    (a === 172 && b >= 16 && b <= 31) ||               // private
    (a === 192 && b === 168) ||                        // private
    (a === 100 && b >= 64 && b <= 127)                 // CGNAT
  );
}

function ipv6Private(ip) {
  const s = ip.toLowerCase();
  if (s === '::1' || s === '::') return true;                       // loopback / unspecified
  const mapped = s.match(/::ffff:(\d+\.\d+\.\d+\.\d+)$/);           // IPv4-mapped
  if (mapped) return ipv4Private(mapped[1]);
  const head = s.split(':')[0];
  return /^f[cd]/.test(head) || /^fe[89ab]/.test(head);             // ULA fc00::/7, link-local fe80::/10
}

// Refuse anything that isn't a public routable address.
export function isPrivateAddress(ip) {
  const v = isIP(ip);
  if (v === 4) return ipv4Private(ip);
  if (v === 6) return ipv6Private(ip);
  return true; // not an IP we understand → refuse
}

// Validate scheme, then resolve the host and refuse private/loopback targets.
export async function assertSafeUrl(rawUrl, { resolve = lookup } = {}) {
  let u;
  try { u = new URL(rawUrl); } catch { throw new Error(`extract-brand: invalid URL "${rawUrl}"`); }
  if (u.protocol !== 'http:' && u.protocol !== 'https:')
    throw new Error(`extract-brand: only http(s) URLs are allowed (got "${u.protocol}")`);
  const records = isIP(u.hostname) ? [{ address: u.hostname }] : await resolve(u.hostname, { all: true });
  for (const { address } of [].concat(records))
    if (isPrivateAddress(address))
      throw new Error(`extract-brand: refusing to fetch a private/loopback address (${address})`);
  return u;
}

// Fetch text with manual redirect re-validation, a byte cap, and a timeout.
export async function fetchText(rawUrl, {
  fetch: f = globalThis.fetch, resolve = lookup,
  timeoutMs = 8000, maxBytes = 2_000_000, maxRedirects = 3,
} = {}) {
  let url = (await assertSafeUrl(rawUrl, { resolve })).href;
  for (let hop = 0; hop <= maxRedirects; hop++) {
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), timeoutMs);
    try {
      const res = await f(url, { redirect: 'manual', signal: ctl.signal, headers: { 'user-agent': 'brand-forge-extract' } });
      const loc = res.status >= 300 && res.status < 400 ? res.headers.get('location') : null;
      if (loc) {
        if (hop === maxRedirects) throw new Error('extract-brand: too many redirects');
        url = (await assertSafeUrl(new URL(loc, url).href, { resolve })).href;
        continue;
      }
      const reader = res.body?.getReader?.();
      if (!reader) return (await res.text()).slice(0, maxBytes);
      const chunks = [];
      let total = 0;
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        total += value.length;
        chunks.push(Buffer.from(value));
        if (total >= maxBytes) { await reader.cancel(); break; }
      }
      return Buffer.concat(chunks).toString('utf8').slice(0, maxBytes);
    } finally {
      clearTimeout(timer);
    }
  }
  throw new Error('extract-brand: too many redirects');
}

// Fetch a site and propose { palette, fonts } from its inline/embedded CSS.
export async function extractFromUrl(rawUrl, opts = {}) {
  const text = await fetchText(rawUrl, opts);
  return { palette: rankPalette(collectColors(text)), fonts: collectFonts(text) };
}
