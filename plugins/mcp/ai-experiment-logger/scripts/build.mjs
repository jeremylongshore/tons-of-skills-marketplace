import { chmod, readFile, readdir, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath, URL } from 'node:url';
import { build } from 'esbuild';

const outfile = fileURLToPath(new URL('../dist/index.js', import.meta.url));

const result = await build({
  entryPoints: [fileURLToPath(new URL('../src/index.ts', import.meta.url))],
  bundle: true,
  metafile: true,
  platform: 'node',
  format: 'esm',
  target: 'node20',
  minify: true,
  legalComments: 'eof',
  outfile,
  banner: {
    js: "import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);",
  },
});

// Preserve complete license notices for every bundled dependency, including
// packages whose source files carry no esbuild-recognized legal comment.
const notices = new Map();
for (const input of Object.keys(result.metafile.inputs)) {
  if (!input.includes('node_modules/')) continue;
  let directory = dirname(input);
  while (true) {
    try {
      const manifest = JSON.parse(await readFile(join(directory, 'package.json'), 'utf8'));
      if (!manifest.name || !manifest.version) { directory = dirname(directory); continue; }
      const names = (await readdir(directory)).filter((name) => /^licen[cs]e(?:[.-]|$)/i.test(name)).sort();
      if (names.length === 0) throw new Error(`Missing bundled license: ${manifest.name}`);
      const texts = await Promise.all(names.map((name) => readFile(join(directory, name), 'utf8')));
      notices.set(`${manifest.name}@${manifest.version}`, texts.join('\n'));
      break;
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      const parent = dirname(directory);
      if (parent === directory) throw new Error(`Missing package manifest: ${input}`);
      directory = parent;
    }
  }
}
const licenses = [...notices].sort(([a], [b]) => a.localeCompare(b, 'en')).map(
  ([name, text]) => `/*! Bundled dependency: ${name}\n${text.replaceAll('*/', '* /').trim()}\n*/`,
).join('\n\n');

// Third-party bundled source can contain whitespace-only lines. Normalize the
// deterministic publication artifact so the repository's diff gate stays clean.
const bundled = await readFile(outfile, 'utf8');
await writeFile(outfile, `${bundled.trimEnd()}\n\n${licenses}\n`.replace(/[\t ]+$/gm, ''));
await chmod(outfile, 0o755);
