# anima-rate-limits — Official Contract

Checked 2026-09-12 against Anima's public SDK repository at commit
`95b66d7e56514908d2017b6d9da03699e6ee0e00` and the current public docs.

## Contract Applied

Figma limits vary by plan and endpoint. `FigmaRestApi.onRateLimited` exposes `retryAfter`, plan tier, and rate-limit type; callers decide whether a bounded retry is safe. `figmaRateLimitMaxWait` accepts 1–180 seconds and defaults to 60.

## Primary Sources

- [Anima SDK README](https://github.com/AnimaApp/anima-sdk/blob/95b66d7e56514908d2017b6d9da03699e6ee0e00/README.md)
- [Anima API documentation](https://docs.animaapp.com/docs/anima-api)
- [Anima SDK package](https://www.npmjs.com/package/@animaapp/anima-sdk)
- [Figma developer documentation](https://developers.figma.com/docs/)
