import { chmod, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath, URL } from 'node:url';
import { build } from 'esbuild';

// The marketplace installs this plugin by copying the directory, with no
// `npm install`, so .mcp.json must launch a self-contained file. Bundle the
// server and its dependencies into the committed dist/ path it launches.
const outfile = fileURLToPath(new URL('../dist/servers/workflow-engine.js', import.meta.url));

await build({
  entryPoints: [fileURLToPath(new URL('../servers/workflow-engine.ts', import.meta.url))],
  bundle: true,
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

// Bundled third-party source can contain whitespace-only lines; normalize so
// the committed artifact stays byte-stable for the CI drift check.
const bundled = await readFile(outfile, 'utf8');
await writeFile(outfile, bundled.replace(/[\t ]+$/gm, ''));
await chmod(outfile, 0o755);
