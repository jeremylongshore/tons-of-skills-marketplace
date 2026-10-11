/**
 * Analytics helper — sends custom events to Umami, the site's only analytics
 * (self-hosted at analytics.intentsolutions.io). Loaded by BaseLayout.astro.
 */
window.trackEvent = function trackEvent(eventName, params) {
  try {
    // Umami script is defer-loaded so window.umami may not exist on very early events
    if (window.umami && typeof window.umami.track === 'function') {
      window.umami.track(eventName, params);
    }
  } catch (e) {
    // Silently ignore analytics errors
  }
};
