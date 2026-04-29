# See It Work

Last reviewed: 2026-04-29

Nova is easiest to understand when you watch a request move through governance.

Latest captured proof package:

- [Conversation + Search Proof Report](../demo_proof/2026-04-29_conversation_search_proof/CONVERSATION_SEARCH_REPORT.md)
- [Conversation + Search Proof Index](../demo_proof/2026-04-29_conversation_search_proof/PROOF_INDEX.md)
- [User Test Report](../demo_proof/2026-04-28_user_test/USER_TEST_REPORT.md)
- [Proof Index](../demo_proof/2026-04-28_user_test/PROOF_INDEX.md)
- [Recorded Demo Flow](../demo_proof/2026-04-28_user_test/video/nova_user_test_demo_flow.webm)

Representative screenshots:

![Nova local-first dashboard](../demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level0_dashboard_connection_status.png)

![Nova Trust receipts](../demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level1_surface_trust.png)

![Nova memory authority boundary](../demo_proof/2026-04-28_user_test/screenshots/local_first_followup/level2_memory_authority.png)

## What To Look For

1. What you asked for
2. How Nova interpreted the request
3. Whether a real action is involved
4. Which capability is allowed to act
5. Whether approval is needed
6. Whether the action was allowed or blocked
7. The final result
8. A visible receipt or review trail

## Current Proof Verdict

The local-first demo path mostly works:

- Nova starts locally and the dashboard loads.
- Local dashboard surfaces are navigable.
- Core self-description prompts have a useful local fallback when the metered budget is exhausted.
- Memory/context are explained as continuity aids, not authority.
- Trust receipts render in both API and UI.
- Cap 64 email draft reaches the confirmation boundary and clearly states that Nova does not send email.
- Shopify missing-credentials behavior fails cleanly without write behavior.

Current sprint focus:

- Cap 16 web-search answer quality
- conversation coherence
- source citation / evidence display
- uncertainty handling
- follow-up/topic tracking

Remaining proof work:

- Fix current-search CPU-budget friction.
- Improve follow-up coherence for connector/governance topics.
- Run Cap 64 P5 live signoff with explicit approval to open a safe local mail-client draft, then close it without sending.
- Make receipt rows friendlier when the ledger payload only includes capability IDs.
- Re-record a final public demo video after Cap 64 live receipt proof is visible.
