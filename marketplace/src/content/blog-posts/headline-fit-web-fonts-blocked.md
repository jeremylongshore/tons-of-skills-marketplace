---
title: "Your Headline Fit Does Not Run When Web Fonts Are Blocked"
description: "The Font Loading API is optional, so a headline fit that waits for it never runs at all. Fit on mount, on load and on resize, then measure the rendered line until it fits."
date: "2026-11-24"
tags: ["react", "web-development", "debugging", "typescript"]
featured: false
canonical: "https://startaitools.com/posts/headline-fit-web-fonts-blocked/"
---
If you ship a text-led hero headline that scales itself to fit the viewport, the routine doing that scaling can stop running on a phone with web fonts blocked, and the clipped text reaches real users while your page looks fine on every machine you own. This post covers what broke, why the CSS Font Loading API was the wrong thing to depend on, and how to make the fit self-sufficient so it runs whether or not that API exists.

The symptom is easy to miss because nothing throws on your end. The page renders. The headline is present. It is just missing its last few words.

## What broke

On the owner's iPhone the homepage headline read "I MAKE TEA" in portrait and in landscape. The designed headline is longer than that. With web fonts blocked, and iOS Lockdown Mode the likely cause, the headline rendered in a full-size system face instead of the face it was designed around.

The line kept its designed size and `.fit-block`, the container that clips overflow, cut the rest off. The failure was invisible to a reader and to the team. The page still rendered, the headline was still there, and only its last words were cut off. On a desktop with the fonts loaded, the same code path fit the line perfectly.

## The dependency that was optional all along

The fit lived in `components/FitLines.tsx` and it did all of its work inside a promise on the CSS Font Loading API. That API is optional. On the phone it was not there, and the access threw before any fitting happened.

```tsx
// Before: the whole fit hangs off an optional API.
useEffect(() => {
  let cancelled = false;
  document.fonts.ready.then(() => {
    if (!cancelled) fitAll();
  });
  return () => { cancelled = true; };
}, []);
```

A `.then` on a property that throws is not a no-op. The exception propagated out of the effect, so the fit never ran at all. The design was also backwards in a second way. Waiting for fonts to settle is the right idea only if the fit is the thing that has to wait. Here the fit was the only thing that could happen, so making it depend on an event that may never arrive left the page with no fitting path whatsoever.

## What the fix does

The fit no longer depends on the Font Loading API. `fitAll` fits every `.fit` line on mount, on the window load event, again when fonts settle only if `document.fonts` exists, and on resize and rotation. A thrown feature test is treated as a feature that is absent, not as a failure. The whole thing is wrapped in `safeFit`, which swallows a fitting failure instead of letting it take the page down, and a failed pass leaves the designed size on the line.

```tsx
export function FitLines() {
  useEffect(() => {
    let cancelled = false;
    let frame = 0;
    const run = () => {
      if (cancelled) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(safeFit);
    };
    run();
    try {
      const fonts = (document as Document & { fonts?: FontFaceSet }).fonts;
      fonts?.ready?.then(run, () => {});
    } catch {
      // No Font Loading API: the mount and resize passes still fit the lines.
    }
    window.addEventListener('load', run);
    window.addEventListener('resize', run);
    window.addEventListener('orientationchange', run);
    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
      window.removeEventListener('load', run);
      window.removeEventListener('resize', run);
      window.removeEventListener('orientationchange', run);
    };
  }, []);
  return null;
}
```

The mount pass is the one that matters most. It runs before any font question is asked, so it fits the line against whatever face is actually rendering right now. If the real face arrives later, the fonts-settled pass refits it.

## Restart from the designed size

The old pass could only shrink. It carried a guard, `if (next < current * 0.995)`, so it never let a line grow back. That `0.995` was a shrink threshold: a new size had to land below 99.5% of the current size, so a larger size was refused. That guard is wrong for a fallback face. On a page where the fit ran, a fallback face is wider than the face the line was designed around, so the line gets shrunk to fit it, and when the real font arrives the line stays small because growing back was never allowed.

The new pass restarts from the designed `--fit` value every time. A line shrunk for a fallback face grows back when the real face arrives, and a line set smaller on purpose stays put. The designed size is cached on the element so it survives across passes.

## Measure the width, do not infer it

The other change is in how the size is computed. Text width is not exactly linear in font size, because glyph advances round per size. One proportional step can land a few pixels wide, which is enough to clip the tail of a line.

So each pass measures the rendered line and corrects against the measurement, over up to four measured passes. The `0.995` in the snippet below is a room factor, the share of the block width the line has to fit inside, not a shrink threshold.

```tsx
// excerpt from fitAll(), where range is a document.createRange() result
const base = parseFloat(line.dataset.fitBase);
const room = block.clientWidth * 0.995;
let size = base;
line.style.setProperty('--fit', String(size));
for (let pass = 0; pass < 4; pass += 1) {
  range.selectNodeContents(line);
  const width = range.getBoundingClientRect().width;
  if (!width || width <= room) break;
  size = Math.floor(((size * room) / width) * 100) / 100;
  line.style.setProperty('--fit', String(size));
}
```

Measurement also means the routine never has to know which font won. A font-detection class would have to guess at every case, including zoom, other fallbacks, and rounding. Measuring covers all of them, because the question that matters is not which face rendered but whether the line fits the room it has.

## Verification

`pnpm typecheck` and `pnpm build` both pass. A WebKit Playwright probe ran at 440x956 and 956x440, which is the portrait and landscape phone pair the headline broke on.

| Scenario | Live site | This change |
|---|---|---|
| No Font Loading API plus system face, the iPhone case | page error, never fitted | fits, right edge 422/424 and 927/932 |
| Fonts OK | font sizes 38.5 / 48.5 | unchanged, font sizes 38.5 / 48.5 |
| Font files blocked, next/font Arial fallback | fits | fits |
| Chromium, fonts OK | not measured | unchanged |

The right edge numbers are the proof. The room is 424 at 440 and 932 at 956, which is the block width times the 0.995 room factor, and the fitted line ends at 422 and 927, so it sits inside the room in both orientations.

The risk is bounded. It is a client-only effect, and the server HTML and the designed sizes are unchanged. Rollback is a revert of the one commit.

## Also shipped

- Fitting logic in `components/FitLines.tsx` was rewritten in place, 73 lines changed, 58 added and 15 removed.
- Shrink-only guard is gone, replaced by a restart from the designed size on every pass.
- Font-loading access now sits inside a try block, so a missing API is a missing feature rather than a thrown exception.
- A `safeFit` wrapper swallows any fitting failure and leaves the designed size in place.

## Use this

- Feature-detect the CSS Font Loading API and treat a thrown access as the feature being absent, then make your layout correction run on mount and on resize regardless, so it does not depend on an event that may never arrive.
- Restart every fit pass from the designed size rather than the current size, so a line that was shrunk for a fallback face can grow back when the real font loads.
- Measure the rendered line and correct against the measurement instead of taking one proportional step, because glyph advances round per size and a few pixels is the difference between a full headline and a clipped one.

## Related Posts

- [GitHub Webhook IP Allowlist: Add the New Hook Ranges](https://startaitools.com/posts/github-webhook-ip-allowlist-new-hook-ranges/): Another optional dependency that fails silently. A static source allowlist on a webhook receiver drops deliveries from ranges you never added, and no health check sees the drop.
- [What a Skipped Check Is Worth in CI](https://startaitools.com/posts/the-skip-that-counted-as-a-pass/): A gate that counts SKIP as pass prints green for work that never ran, so the receipt (a machine-written record proving a step really ran) has to prove the run.
