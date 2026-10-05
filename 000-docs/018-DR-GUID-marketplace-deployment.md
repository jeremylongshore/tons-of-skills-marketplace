<!-- doc-class: record -->

# Deployment Guide - Claude Code Plugins Marketplace

**Last Updated**: 2025-10-11
**Build Status**: SUCCESS
**Ready for Production**: YES

---

## Quick Deploy

```bash
# 1. Build the site
cd
npm run build

# 2. The production-ready site is in dist/
ls -lh dist/

# 3. Deploy to GitHub Pages (automatic via GitHub Actions)
git add .
git commit -m "feat: complete marketplace redesign with modern slate/green theme"
git push origin main
```

---

## Build Output Summary

```
dist/
├── _astro/
│   └── index.CN-Zjh_D.css (24KB - optimized CSS)
├── fonts/
│   ├── IBMPlexMono-Regular.otf
│   ├── IBMPlexMono-Medium.otf
│   └── IBMPlexMono-SemiBold.otf
├── favicon.svg
└── index.html (578 lines - 1.1MB with all 220 plugins)

Total Size: 2.5MB
```

---

## Deployment Options

### Option 1: GitHub Pages (Recommended)

The repository is already configured for GitHub Pages deployment.

**Automatic Deployment**:
1. Push changes to `main` branch
2. GitHub Actions will automatically build and deploy
3. Site will be live at: `[retired legacy public domain]/`

**Manual Deployment**:
```bash
# Build
npm run build

# The dist/ folder will be automatically deployed by GitHub Actions
# No manual steps required
```

### Option 2: Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd
vercel --prod
```

### Option 3: Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
cd
netlify deploy --prod --dir=dist
```

### Option 4: Custom Server

```bash
# Build the site
npm run build

# Copy dist/ to your web server
scp -r dist/* user@server:/var/www/html/

# Or use rsync
rsync -avz --delete dist/ user@server:/var/www/html/
```

---

## Pre-Deployment Checklist

- [x] All 220 plugins loading correctly
- [x] Search functionality working
- [x] Category filters working
- [x] Sort options working
- [x] Copy buttons functional
- [x] All links working (GitHub, Discord, Docs)
- [x] Mobile responsive design
- [x] Browser compatibility (Chrome, Firefox, Safari)
- [x] Build completed without errors
- [x] SEO meta tags present
- [x] Open Graph tags for social sharing
- [x] Accessibility features implemented

---

## Testing the Build

### Local Preview

```bash
# Build the site
npm run build

# Preview the production build
npm run preview

# Open browser to http://localhost:4321/claude-code-plugins/
```

### Verify Key Features

1. **Search**: Type in search bar, results filter instantly
2. **Category Filter**: Select category, plugins filter by category
3. **Sort**: Change sort order (A-Z, Z-A, Featured)
4. **Copy Buttons**: Click "Copy Install" buttons, commands copy to clipboard
5. **Links**: Click GitHub, Discord, Docs links - all open correctly
6. **Mobile**: Resize browser to mobile width, verify responsive design
7. **Performance**: Check page load time (should be < 2s)

---

## Performance Optimization

The site is already optimized:

- **Static Generation**: Pre-rendered HTML (no server-side rendering)
- **Minimal JavaScript**: Only for search/filter (client-side)
- **Optimized CSS**: Single 24KB CSS file
- **No External Dependencies**: All assets self-hosted
- **Compressed HTML**: Minified and compressed
- **Fast Font Loading**: Preloaded fonts with swap

---

## Monitoring & Analytics (Optional)

### Add Google Analytics

Edit `src/layouts/Layout.astro` and add before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Add Plausible Analytics (Privacy-Friendly)

```html
<!-- Plausible Analytics -->
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

---

## Custom Domain Setup (GitHub Pages)

### 1. Add CNAME File

Create `public/CNAME` with your domain:

```
plugins.yourdomain.com
```

### 2. Update DNS Records

Add these DNS records with your domain provider:

```
Type: CNAME
Name: plugins
Value: jeremylongshore.github.io
```

### 3. Update astro.config.mjs

```javascript
export default defineConfig({
  site: 'https://plugins.yourdomain.com',
  base: '/',
  // ... rest of config
});
```

### 4. Rebuild and Deploy

```bash
npm run build
git add .
git commit -m "feat: add custom domain"
git push origin main
```

---

## Troubleshooting

### Build Fails

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Assets Not Loading

Check `astro.config.mjs` - ensure `base` path matches your deployment:

```javascript
base: '/claude-code-plugins',  // For GitHub Pages subdirectory
// OR
base: '/',  // For root domain
```

### Search Not Working

Ensure JavaScript is enabled in browser. Check browser console for errors:

```bash
# Open browser DevTools (F12)
# Check Console tab for errors
```

### Styles Not Applied

Clear browser cache:
- Chrome: Ctrl+Shift+R (hard refresh)
- Firefox: Ctrl+Shift+Delete (clear cache)
- Safari: Cmd+Option+E (clear cache)

---

## Rollback Procedure

If deployment has issues:

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Or reset to specific commit
git reset --hard <commit-hash>
git push origin main --force
```

---

## Maintenance

### Update Plugin Count

When adding new plugins, update these files:

1. `src/components/Hero.astro` - Update stats
2. `src/pages/index.astro` - Automatically updates from content
3. `README.md` - Update plugin count

### Add New Category

1. Update `src/content/config.ts` - Add to category enum
2. Update `src/components/PluginCard.astro` - Add category icon and color
3. Update `src/pages/index.astro` - Add to categoryIcons object

---

## Support

- **GitHub Issues**: https://github.com/jeremylongshore/claude-code-plugins/issues
- **Discussions**: https://github.com/jeremylongshore/claude-code-plugins/discussions
- **Documentation**: https://docs.claude.com/en/docs/claude-code/plugins

---

## Next Steps After Deployment

1. Announce on Discord
2. Share on Twitter/X
3. Update main repository README with live site link
4. Monitor GitHub Pages deployment status
5. Test live site on multiple devices
6. Collect user feedback
7. Iterate on improvements

---

**Deployment Status**: READY
**Live URL**: `[retired legacy public domain]/`
**Last Build**: 2025-10-11
**Build Time**: ~1.6s
**Total Size**: 2.5MB
