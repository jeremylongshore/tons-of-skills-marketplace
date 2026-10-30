# Primary contracts

Reviewed 2026-10-25. These support limited local review and verification; they do
not authorize account/provider operations or certify a deployment.

- [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.html) defines JWT claims and
  NumericDate semantics. The supported local profile requires expiration and
  explicit expected issuer/audience; other applications may use other profiles.
- [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html) addresses algorithm,
  cryptographic-input and claim verification. Received headers never select this
  tool's trusted key or allowed algorithm. Inspection does not authenticate.
- [PyJWT API](https://pyjwt.readthedocs.io/en/stable/api.html) and
  [security changelog](https://pyjwt.readthedocs.io/en/stable/changelog.html)
  document the maintained verification boundary. The tested pin is 2.15.1;
  verification rejects older/unsupported major versions instead of silently
  trusting them. Cryptography 50.0.2 is the pinned optional asymmetric backend.
- [OAuth security BCP, RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html)
  distinguishes client roles and PKCE requirements. The configuration helper
  reviews declared public/shared-secret-confidential HTTPS web clients and S256
  PKCE; it does not test registration, redirect matching or flow binding.
- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html) distinguishes
  single-factor and MFA password length, discourages mandatory composition and
  arbitrary periodic changes, and requires comparison of entire candidate values
  against a blocklist. Local checks use declared context and exact supplied
  values; they do not prove MFA, blocklist adequacy or deployed enforcement.
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
  provides KDF review profiles. The helper supports the listed Argon2id memory/time
  combinations with p=1, PBKDF2-HMAC-SHA256/SHA512 and a limited legacy bcrypt
  review. It does not execute hashing, validate FIPS modules or infer salt/key
  entropy. Unsupported variants/parameters remain review items.
- [OWASP Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
  and [Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
  support the broader manual review. Record the actual framework/context and
  independent evidence before mapping a control; these references are not
  bundled automated application scanners.
