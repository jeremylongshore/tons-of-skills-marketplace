// Externalized from src/layouts/BaseLayout.astro so script-src can drop 'unsafe-inline' (bead claude-i076).
document.addEventListener('DOMContentLoaded', function() {
    var menuToggle = document.querySelector('.mobile-menu-toggle');
    var navLinks = document.querySelector('.nav-links');
    var menuIcon = document.querySelector('.menu-icon');
    var closeIcon = document.querySelector('.close-icon');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            document.body.classList.toggle('menu-open');

            if (navLinks.classList.contains('active')) {
                menuIcon.style.display = 'none';
                closeIcon.style.display = 'block';
            } else {
                menuIcon.style.display = 'block';
                closeIcon.style.display = 'none';
            }
        });

        navLinks.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                navLinks.classList.remove('active');
                document.body.classList.remove('menu-open');
                menuIcon.style.display = 'block';
                closeIcon.style.display = 'none';
            });
        });

        document.addEventListener('click', function(e) {
            if (navLinks.classList.contains('active') &&
                !navLinks.contains(e.target) &&
                !menuToggle.contains(e.target)) {
                navLinks.classList.remove('active');
                document.body.classList.remove('menu-open');
                menuIcon.style.display = 'block';
                closeIcon.style.display = 'none';
            }
        });
    }

    // Track outbound link clicks (nav + footer)
    document.querySelectorAll('nav a[target="_blank"], footer a[target="_blank"]').forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.trackEvent) {
                window.trackEvent('outbound_click', {
                    url: link.href,
                    link_text: link.textContent.trim()
                });
            }
        });
    });
});
