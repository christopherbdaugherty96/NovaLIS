# Public Source Boundary

NovaLIS is a deliberately inspectable source repository. Public visibility does not make
runtime data, private business material, credentials, or release artifacts repository
content.

## Allowed

- Nova source code and public-safe architecture documentation.
- Tests that use clearly synthetic fixtures and non-working example credentials.
- Public-safe threat models and sanitized proof artifacts.
- Example configuration containing placeholders only.
- Contribution and security-reporting documentation.

## Prohibited

- Runtime ledgers, memory contents, user profiles, prompts, histories, receipts, or state.
- `.env` files, OAuth client files, provider tokens, access tokens, private keys, or
  credential exports.
- Browser/session/account exports, HAR files, cookies, local authentication material, or
  machine-bound encrypted blobs.
- Personal exports, real user identifiers, machine-specific paths, or developer-local state.
- Client data or private Auralis pricing, funnels, sales strategy, operations, and future
  commercial planning.
- Installer or release binaries that have not passed an explicitly approved provenance,
  privacy, secrets, dependency, and distribution review.

## Required handling

Use disposable runtime roots and synthetic fixtures in tests. Store private commercial work
outside this repository. Before publishing a release, record the source revision and artifact
SHA-256 and complete the accepted release review. Report suspected exposure privately through
`SECURITY.md`.

Run this check before proposing a change:

```text
python scripts/check_public_source_hygiene.py
```

The check is intentionally narrow. It catches forbidden tracked paths, obvious private file
types, and known personal markers. It complements rather than replaces Gitleaks, TruffleHog,
GitHub secret scanning, review, and release inspection.
