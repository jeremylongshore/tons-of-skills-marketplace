// Externalized from src/layouts/BaseLayout.astro so script-src can drop 'unsafe-inline' (bead claude-i076).
(() => {
  const flash = (btn, msg, ok = true, restoreMs = 3000) => {
    const orig = btn.dataset.origText ?? btn.textContent;
    if (!btn.dataset.origText) btn.dataset.origText = orig;
    btn.textContent = msg;
    btn.style.opacity = ok ? '0.85' : '1';
    btn.disabled = ok;
    if (!ok) setTimeout(() => {
      btn.textContent = orig;
      btn.style.opacity = '';
      btn.disabled = false;
    }, restoreMs);
  };

  const wireSignup = (form) => form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const emailInput = form.querySelector('input[type="email"]');
    const honey = form.querySelector('input[name="website"]');
    const email = (emailInput?.value || '').trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      flash(btn, 'Invalid email', false);
      return;
    }
    flash(btn, 'Subscribing…', true, 0);
    try {
      const r = await fetch('/api/forms/signup', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          email,
          source: form.dataset.signupForm || 'unknown',
          website: honey?.value || ''
        })
      });
      if (r.ok) {
        flash(btn, "You're in!", true, 0);
        if (emailInput) emailInput.value = '';
      } else if (r.status === 429) {
        flash(btn, 'Slow down', false);
      } else {
        const j = await r.json().catch(() => ({}));
        flash(btn, j.error || 'Something went wrong', false);
      }
    } catch {
      flash(btn, 'Network error', false);
    }
  });

  const wireNomination = (form) => form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const repoInput = form.querySelector('input[name="repo"]');
    const honey = form.querySelector('input[name="website"]');
    const repoUrl = (repoInput?.value || '').trim();
    if (!/^https:\/\/github\.com\/[^/\s]+\/[^/\s]+/.test(repoUrl)) {
      flash(btn, 'GitHub URL only', false);
      return;
    }
    flash(btn, 'Submitting…', true, 0);
    try {
      const r = await fetch('/api/forms/nominate', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          repoUrl,
          source: form.dataset.nominationForm || 'unknown',
          website: honey?.value || ''
        })
      });
      if (r.ok) {
        flash(btn, 'Submitted!', true, 0);
        if (repoInput) repoInput.value = '';
      } else if (r.status === 429) {
        flash(btn, 'Slow down', false);
      } else {
        const j = await r.json().catch(() => ({}));
        flash(btn, j.error || 'Something went wrong', false);
      }
    } catch {
      flash(btn, 'Network error', false);
    }
  });

  const wireContact = (form) => form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const nameInput = form.querySelector('input[name="name"]');
    const emailInput = form.querySelector('input[type="email"]');
    const messageInput = form.querySelector('textarea[name="message"]');
    const honey = form.querySelector('input[name="website"]');
    const name = (nameInput?.value || '').trim();
    const email = (emailInput?.value || '').trim();
    const message = (messageInput?.value || '').trim();
    if (name.length < 2) { flash(btn, 'Name required', false); return; }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { flash(btn, 'Invalid email', false); return; }
    if (message.length < 10) { flash(btn, 'Tell me more', false); return; }
    flash(btn, 'Sending…', true, 0);
    try {
      const r = await fetch('/api/forms/contact', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          name,
          email,
          message,
          source: form.dataset.contactForm || 'unknown',
          website: honey?.value || ''
        })
      });
      if (r.ok) {
        flash(btn, "Got it — back within 24h!", true, 0);
        if (nameInput) nameInput.value = '';
        if (emailInput) emailInput.value = '';
        if (messageInput) messageInput.value = '';
      } else if (r.status === 429) {
        flash(btn, 'Slow down', false);
      } else {
        const j = await r.json().catch(() => ({}));
        flash(btn, j.error || 'Something went wrong', false);
      }
    } catch {
      flash(btn, 'Network error', false);
    }
  });

  const init = () => {
    document.querySelectorAll('[data-signup-form]').forEach(wireSignup);
    document.querySelectorAll('[data-nomination-form]').forEach(wireNomination);
    document.querySelectorAll('[data-contact-form]').forEach(wireContact);
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else { init(); }
})();
