// Externalized from src/layouts/BaseLayout.astro so script-src can drop 'unsafe-inline' (bead claude-i076).
(function() {
    var nav = document.querySelector('nav');
    if (!nav) return;
    function onScroll() {
        if (window.scrollY > 20) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
})();
