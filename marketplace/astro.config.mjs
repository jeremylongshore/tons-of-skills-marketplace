// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

import { securityHeadersForPath } from './scripts/security-policy.mjs';

function marketplaceSecurityHeaders() {
  const installMiddleware = (server) => {
    server.middlewares.use((request, response, next) => {
      for (const [name, value] of Object.entries(securityHeadersForPath(request.url ?? '/'))) {
        response.setHeader(name, value);
      }
      next();
    });
  };

  return {
    name: 'marketplace-security-headers',
    configureServer: installMiddleware,
  };
}

// https://astro.build/config
export default defineConfig({
  site: 'https://tonsofskills.com',
  base: '/',
  // NO Astro `redirects` here — deliberately. See /etc/caddy/tonsofskills-redirects.caddy
  // on the VPS, which serves the generated redirect inventory as real HTTP 301s.
  //
  // Astro's redirects config emits one thin HTML page per entry containing
  // <meta http-equiv="refresh" content="0;url=...">. Adding 81 of them on
  // 2026-08-03 took the site from 3 to 85 instant-redirect pages in a single
  // deploy, and a consumer network-security filter began blocking
  // tonsofskills.com hours later. A mass of instant meta-refresh pages is the
  // classic doorway-page / cloaking signature those heuristics look for.
  //
  // Causation was never proven — Google Safe Browsing reported the domain clean
  // throughout — but meta-refresh is the wrong mechanism regardless: a permanent
  // redirect belongs in the HTTP status line, not in markup a crawler has to
  // execute. Real 301s are faster, keep those thin pages out of the crawl surface,
  // and pass link equity correctly.
  //
  // If you need a new redirect, add it to the Caddy file — NOT here.

  // EXCEPTION — these three predate the 2026-08-03 404-repair work and stay in
  // Astro. scripts/check-routes.mjs treats them as real routes and asserts the
  // built files exist, so moving them to Caddy breaks that gate. Three redirect
  // pages is also not the doorway-page pattern the move was about; eighty-one
  // was. Keeping them here means one source of truth per redirect.
  redirects: {
    '/learning/built-system-summary': '/learning/',
    '/learning/getting-started': '/learning/overview/',
    '/spotlight': '/community#hall-of-fame',
  },
  build: {
    assets: '_astro',
    inlineStylesheets: 'auto',
  },
  output: 'static',
  compressHTML: false, // Disabled: iOS Safari fails with lines > 5000 chars
  vite: {
    // Route-aware middleware keeps the development server strict while
    // allowing user-supplied WebSocket endpoints only on /chats. The static
    // preview server and production Caddy use the same policy module.
    plugins: [tailwindcss(), marketplaceSecurityHeaders()],
    build: {
      cssCodeSplit: true,
      // Never inline processed scripts into the HTML: an inline <script> needs
      // script-src 'unsafe-inline' (bead claude-i076). Returning undefined
      // keeps Vite's default 4 KB limit for every other asset type.
      assetsInlineLimit: (filePath) => (filePath.endsWith('.js') ? false : undefined),
      rollupOptions: {
        output: {
          assetFileNames: '_astro/[name].[hash][extname]',
        },
      },
    },
  },
});
