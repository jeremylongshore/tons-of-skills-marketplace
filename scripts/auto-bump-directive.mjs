#!/usr/bin/env node
import { appendFileSync, readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

// A body directive is a standalone Markdown paragraph, not an example in
// prose, a quote, an HTML comment, or an indented/fenced code block.
export function hasSkipDirective(body) {
  if (typeof body !== 'string') return false;
  let fence = null;
  for (const line of body.replace(/<!--[\s\S]*?(?:-->|$)/g, '').split(/\r?\n/)) {
    if (fence) {
      const close = line.match(/^ {0,3}(`{3,}|~{3,})[ \t]*$/);
      if (close && close[1][0] === fence[0] && close[1].length >= fence.length) fence = null;
      continue;
    }
    const open = line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
    if (open && (open[1][0] !== '`' || !open[2].includes('`'))) {
      fence = open[1];
      continue;
    }
    if (/^ {0,3}\[skip auto-bump\][ \t]*$/.test(line)) return true;
  }
  return false;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const event = JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8'));
  if (!event.pull_request) throw new Error('Expected a pull_request event');
  appendFileSync(process.env.GITHUB_OUTPUT, `skip=${hasSkipDirective(event.pull_request.body)}\n`);
}
