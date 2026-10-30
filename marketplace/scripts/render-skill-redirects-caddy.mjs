import { readFileSync } from 'node:fs';

export function renderSkillRedirects(redirects, start = 84) {
  const lines = [
    '# Retired-skill redirects — generated from skill-redirects.json.',
    '# Import this fragment from the tonsofskills.com Caddy site block.',
    '# Each matcher covers both slash forms and `permanent` emits HTTP 301.',
    '',
  ];
  redirects.forEach((redirect, index) => {
    const id = String(start + index).padStart(3, '0');
    lines.push(
      `@redir${id} path /skills/${redirect.from} /skills/${redirect.from}/`,
      `redir @redir${id} /skills/${redirect.to}/ permanent`,
    );
  });
  return `${lines.join('\n')}\n`;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const redirects = JSON.parse(
    readFileSync(new URL('../src/data/skill-redirects.json', import.meta.url), 'utf8'),
  ).redirects;
  process.stdout.write(renderSkillRedirects(redirects));
}
