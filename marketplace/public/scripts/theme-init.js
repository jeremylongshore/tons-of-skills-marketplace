// Externalized from src/layouts/BaseLayout.astro so script-src can drop 'unsafe-inline' (bead claude-i076).
(function(){var t=localStorage.getItem('theme');if(!t){t=window.matchMedia('(prefers-color-scheme:light)').matches?'light':'dark'}document.documentElement.setAttribute('data-theme',t)})();
