# Known Limitations

Last reviewed: 2026-04-29

This page exists to set honest expectations about Nova today.

## Product State
- Nova is an active alpha build, not a finished mainstream release.
- Some flows are stronger than others because the project is still evolving.
- Current setup still expects a technically comfortable user.
- Product clarity is improving faster than mainstream convenience.

## Environment Dependence
- Local models must be installed and configured.
- Performance depends on your hardware.
- Some local actions vary by operating system.
- Voice features may require local speech dependencies and model paths.
- Optional connectors require additional setup, credentials, or external accounts.

## Current Gaps
- Action Receipts and the Trust Receipts API exist, and the Trust page now renders receipts in the local-first proof pass. The full Trust Review Card / Trust Panel experience is still not complete.
- Receipt rows can still be too technical when ledger payloads include capability IDs but not friendly capability names.
- Cap 64 email draft still needs human P5 live signoff before lock. The latest proof reached the confirmation boundary; Nova opens a local draft only after confirmation and does not send email autonomously.
- Cap 64 live signoff is paused while Cap 16 web-search answer quality and conversation coherence are the active sprint.
- Current web searches can still hit CPU-budget friction. One live proof run returned `Execution exceeded allowed CPU budget`.
- Follow-up coherence is improved but not finished; one Shopify follow-up drifted instead of answering the avoid/do-not-do question directly.
- Weak search results now produce a low-evidence response, but answer quality still depends on search provider relevance.
- Cap 65 Shopify intelligence still needs real credential-backed P5 live proof before lock; current Shopify support is read-only reporting.
- One-click installer is not finished.
- Optional network/connector degradation, such as weather or news source issues, can make the UI look less healthy than the local runtime actually is.
- The in-app Browser Use proof path was blocked in this environment by an invalid user-level `C:\Users\Chris\package.json`; Playwright screenshots were used as real proof captures instead.
- Some advanced workflows remain experimental.
- Broad autonomous execution is intentionally limited and not the current promise.
- Some docs may describe future direction rather than live capability state.

## Authority Boundaries
- Conversation context can help Nova understand what the user means; it does not grant permission to act.
- Memory can support continuity; it is not an execution authority.
- Ledger entries and Action Receipts record governed actions; they are not the same thing as memory.
- Scheduler or background-loop concepts, where present, must stay gated, bounded, settings-controlled, and unable to bypass governance.

## Best Fit Today
Nova is best for builders, technical early adopters, and users who value control, visibility, and local ownership more than maximum convenience.

## Not The Best Fit Yet
Nova may not be the best fit yet for users expecting:
- zero-setup onboarding
- polished mobile-first UX
- invisible automation that runs everything for you
- enterprise support guarantees
- appliance-level simplicity

## Why This Matters
Honest limits build trust better than inflated claims.
Use generated runtime truth docs for exact current capability status.
