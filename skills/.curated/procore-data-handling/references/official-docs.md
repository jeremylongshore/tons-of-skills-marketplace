# Official Procore sources

Consulted: 2026-09-13

## Scope

These first-party sources ground **Procore Governed File Transfer**. The target resource reference determines its accepted upload or attachment shape.

## Sources

- [Direct file uploads](https://developers.procore.com/documentation/tutorial-uploads)
- [Secure file access](https://developers.procore.com/documentation/secure-file-access-tips)
- [File attachments and image uploads](https://developers.procore.com/documentation/tutorial-attachments)
- [Working with Documents](https://developers.procore.com/documentation/tutorial-documents)

## Provider boundaries

- Upload creation, byte transfer, completion, and resource association can be separate steps.
- Secure file URLs must be treated as opaque and may require Bearer authentication.
- Legacy upload flows should migrate through documented paths.
- Resource-specific endpoint documentation controls the final association.
- Source snapshot: `procore/documentation@fd31bc4b6c3d46b72b2b570c920ae5ccb2aa4318`.
