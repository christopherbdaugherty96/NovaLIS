# Personality Layer Design — Session Prompt

Status: prompt template for future design session
Date: 2026-06-04
Context: to be used in a fresh session after the DeepSeek governance
hardening session (commits 7b5091d–de8c3da)

---

## Prompt

Ground yourself in the current NovaLIS repository truth.

Context:

Nova is a governance-first personal operating layer.

Core principle:

Intelligence proposes. Nova governs. User decides.

Current architecture:

```text
Personality Layer
    ↑
User Experience Layer
    ↑
Governance Layer
    ↑
Intelligence Layer
    ↑
Data / Capability Layer
```

Current state:

- DeepSeek is the external reasoning layer (Cap 62)
- Shopify Intelligence exists as read-only Cap 65
- Governance boundaries are hardened
- Approval gates are certified
- Simulations completed successfully
- Personality layer does not yet exist

Task:

Design a personality layer for Nova.

Important:

The personality layer must NEVER:

- Grant authority
- Bypass approval gates
- Execute actions
- Override governance
- Act as an autonomous agent
- Change capability permissions
- Modify confirmation requirements

The personality layer MUST:

- Improve user experience
- Make governance feel natural
- Explain decisions clearly
- Provide proactive suggestions
- Help prioritize tasks
- Help manage business workflows
- Help manage personal workflows
- Maintain user trust

Design Goals:

Nova should feel like:

- A trusted butler
- A knowledgeable chief of staff
- A personal operations coordinator

Nova should NOT feel like:

- A chatbot
- A corporate help desk
- An autonomous AI agent
- A system administrator acting without permission

Deliver:

1. Personality Principles
2. Behavioral Rules
3. Tone Guidelines
4. Proactive Suggestion Framework
5. Reminder Framework
6. Business Workflow Behavior
7. Auralis Digital Support Behavior
8. Home/Desktop Assistant Behavior
9. Memory Interaction Rules
10. Approval Gate Interaction Rules
11. Trust UI Interaction Rules
12. Failure Handling Personality
13. Examples of Good Behavior
14. Examples of Forbidden Behavior
15. Governance Risk Review
16. Recommended Implementation Architecture

Specific Question:

How can Nova feel highly proactive and intelligent while
preserving the rule:

"Intelligence proposes. Nova governs. User decides."

Output:

```text
CURRENT TRUTH
PERSONALITY DESIGN
GOVERNANCE SAFETY REVIEW
IMPLEMENTATION RECOMMENDATION
RISKS
NEXT ACTION
```

---

## Notes

This prompt should produce a governed personality architecture,
not a list of traits. Nova's personality should be treated as a
system layer with its own governance review, not merely a writing
style applied to responses.

The personality layer sits on top of governance. It never sits
beside or beneath it. The personality makes gates feel natural
to the user while they remain fully visible in the ledger.

Reference docs:
- docs/status/SESSION_SUMMARY_2026-06-04_DEEPSEEK_GOVERNANCE.md
- docs/status/SIMULATION_RESULTS_2026-06-04.md
- docs/future/RJ_PRINT_GOVERNED_PRODUCTION_TICKET_PLAN.md
