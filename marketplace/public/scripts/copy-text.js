// Copy buttons: <button data-copy-text="..."> copies its text and shows
// "copied" for two seconds. Replaces an inline onclick so script-src can
// drop 'unsafe-inline' (bead claude-i076).
document.addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-copy-text]');
  if (!btn) return;
  // Remember the original label once, so a second click inside the two
  // seconds doesn't capture "copied" as the label to restore.
  if (btn.dataset.copyLabel === undefined) btn.dataset.copyLabel = btn.textContent;
  const label = btn.dataset.copyLabel;
  navigator.clipboard.writeText(btn.dataset.copyText).then(() => {
    btn.textContent = 'copied';
    setTimeout(() => (btn.textContent = label), 2000);
  });
});
