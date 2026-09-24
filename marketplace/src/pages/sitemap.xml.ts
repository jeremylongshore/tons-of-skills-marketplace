import type { APIRoute } from 'astro';
import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import { buildSitemap } from '../lib/sitemap-xml.mjs';

// Generate sitemap.xml from marketplace catalog
export const GET: APIRoute = async () => {
  const siteUrl = 'https://tonsofskills.com';

  // Load marketplace catalog
  const catalogPath = join(process.cwd(), '../.claude-plugin/marketplace.json');
  const catalog = JSON.parse(readFileSync(catalogPath, 'utf-8')) as {
    plugins: Array<{ name: string }>;
  };

  // Load skills catalog
  const skillsCatalogPath = join(process.cwd(), 'src/data/skills-catalog.json');
  const skillsCatalog = JSON.parse(readFileSync(skillsCatalogPath, 'utf-8')) as {
    skills: Array<{ slug: string }>;
  };

  // Discover docs pages from content directory
  const docsDir = join(process.cwd(), 'src/content/docs');
  const docsSections = ['getting-started', 'concepts', 'guides', 'reference', 'ecosystem'];
  const docsPages: { url: string; priority: string; changefreq: string }[] = [
    { url: '/docs', priority: '0.9', changefreq: 'weekly' },
  ];
  for (const section of docsSections) {
    try {
      const files = readdirSync(join(docsDir, section));
      for (const file of files) {
        if (file.endsWith('.md')) {
          const slug = encodeURIComponent(file.replace(/\.md$/, ''));
          docsPages.push({ url: `/docs/${section}/${slug}`, priority: '0.7', changefreq: 'weekly' });
        }
      }
    } catch { /* section dir may not exist yet */ }
  }

  // Static pages
  const staticPages = [
    { url: '/', priority: '1.0', changefreq: 'daily' },
    { url: '/about', priority: '0.8', changefreq: 'monthly' },
    { url: '/explore', priority: '0.9', changefreq: 'daily' },
    { url: '/skills', priority: '0.9', changefreq: 'daily' },
    { url: '/cowork', priority: '0.8', changefreq: 'weekly' },
    { url: '/collections', priority: '0.8', changefreq: 'weekly' },
    { url: '/compare', priority: '0.8', changefreq: 'weekly' },
    { url: '/tools', priority: '0.9', changefreq: 'weekly' },
    { url: '/sponsor', priority: '0.7', changefreq: 'weekly' },
    { url: '/privacy', priority: '0.5', changefreq: 'monthly' },
    { url: '/terms', priority: '0.5', changefreq: 'monthly' },
    { url: '/acceptable-use', priority: '0.5', changefreq: 'monthly' },
    { url: '/skill-enhancers', priority: '0.8', changefreq: 'weekly' },
    { url: '/community', priority: '0.8', changefreq: 'weekly' },
    { url: '/compare-marketplaces', priority: '0.8', changefreq: 'weekly' },
    { url: '/blog', priority: '0.9', changefreq: 'weekly' },
    { url: '/verification', priority: '0.7', changefreq: 'monthly' },
  ];

  const sitemap = buildSitemap({
    siteUrl,
    staticPages,
    docsPages,
    pluginNames: catalog.plugins.map((plugin) => plugin.name),
    skillSlugs: skillsCatalog.skills.map((skill) => skill.slug),
  });

  return new Response(sitemap, {
    headers: {
      'Content-Type': 'application/xml',
      'Cache-Control': 'public, max-age=3600',
    },
  });
};
