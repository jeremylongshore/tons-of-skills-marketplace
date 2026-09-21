# anima-reference-architecture — Official Contract

Checked 2026-09-12 against Anima's public SDK repository at commit
`95b66d7e56514908d2017b6d9da03699e6ee0e00` and the current public docs.

## Contract Applied

Separate source authorization, backend generation, optional SSE delivery, deterministic output validation, reviewed promotion, and rollback. Figma webhooks use their configured passcode and must not deploy generated code directly.

## Primary Sources

- [Anima SDK README](https://github.com/AnimaApp/anima-sdk/blob/95b66d7e56514908d2017b6d9da03699e6ee0e00/README.md)
- [Anima API documentation](https://docs.animaapp.com/docs/anima-api)
- [Anima SDK package](https://www.npmjs.com/package/@animaapp/anima-sdk)
- [Figma developer documentation](https://developers.figma.com/docs/)
