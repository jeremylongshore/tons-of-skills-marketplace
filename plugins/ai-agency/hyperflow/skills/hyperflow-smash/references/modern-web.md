# Modern web work

Load when a workflow changes web UI, browser APIs, forms, dialogs, canvas, or WebMCP. Start with the repository's supported browser/device matrix, design-system primitives, and existing test routes. Prefer Baseline Widely available behavior when no target is declared. Treat newer APIs as enhancements: feature-detect them and keep a usable fallback for supported browsers. Do not force Chrome-only features.

If the pinned Modern Web Guidance catalog is already available, look up one capability at a time with generic terms and telemetry disabled. Do not install dependencies or send private code, project names, or user data. If it is unavailable, use the [published Chrome guides](https://developer.chrome.com/docs/modern-web-guidance/guides).

## Interaction and UI

- For slow interactions, trace input delay, handler work, and presentation. Show feedback early, then split work by elapsed time. Prefer `scheduler.yield()` when available and keep a task-based fallback; consider a worker only for suitable CPU-heavy work.
- Reuse accessible dialog and popover primitives. Check keyboard opening, initial focus, dismissal, focus return, and reduced motion. For native top-layer transitions, use `@starting-style` for entry and keep `display` and `overlay` through exit where supported. Preserve function without discrete transition support.
- Treat view transitions, scroll effects, carousel controls, scroll-state queries, CSS functions, and anchor positioning as progressive enhancements when target browsers differ. Give gestures an equivalent button or keyboard action.
- Label form controls, use appropriate address `autocomplete` tokens and mobile input types, and retain manual entry. Make calendar and time-zone choices explicit. Feature-detect `Temporal` and cover supported fallback behavior, including leap-month cases where relevant.
- Keep a functional DOM fallback for HTML-in-Canvas. Check hit geometry, keyboard access, text selection, and assistive technology behavior when those features matter.

## Web tools and evidence

For browser WebMCP, define the user's goal and success condition. Keep schemas narrow, enforce authorization at the server, require explicit confirmation for consequential actions, and treat tool output as untrusted. Test successful, invalid, unauthorized, and consequential paths. Keep existing OpenCode MCP connections separate.

Verify affected journeys on the supported browser and exercise fallbacks separately. Record revision, route, viewport, browser, and action. Keep lab measures separate from field p75 Core Web Vitals. Use only existing authorized browser tools and respect their resource caps; state which checks still need a real browser or assistive technology.
