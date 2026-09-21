# anima-webhooks-events — Official Contract

Checked 2026-09-12 against Anima's public SDK repository at commit
`95b66d7e56514908d2017b6d9da03699e6ee0e00` and the current public docs.

## Contract Applied

Anima does not expose a pack-specific webhook contract here; use Figma Webhooks v2 for design events. Validate the configured passcode, deduplicate event/version identities, acknowledge promptly, and queue bounded generation behind human review.

## Primary Sources

- [Anima SDK README](https://github.com/AnimaApp/anima-sdk/blob/95b66d7e56514908d2017b6d9da03699e6ee0e00/README.md)
- [Anima API documentation](https://docs.animaapp.com/docs/anima-api)
- [Anima SDK package](https://www.npmjs.com/package/@animaapp/anima-sdk)
- [Figma developer documentation](https://developers.figma.com/docs/)
