# Email Coordination Board

Status: future workflow design / not implemented

This document defines a core Nova workflow: turning email into a structured action board.

---

## Core Idea

Nova should not treat email as individual messages only.

Nova should convert batches of emails into:

```text
An actionable coordination board.
```

---

## Workflow

Input:

- inbox snapshot
- selected threads
- filtered domain (Auralis, personal, etc.)

Processing:

- group by sender / client / project
- summarize each thread
- classify urgency
- detect requested actions
- detect missing information
- detect follow-ups owed
- detect scheduling needs

Output:

- structured action board

---

## Action Board Sections

- Needs reply
- Needs scheduling
- Needs decision
- Waiting on someone else
- Business / client related
- Personal / admin
- No action

---

## Per-Thread Object

Example:

```json
{
  "thread_id": "gmail_thread_123",
  "domain": "business/auralis",
  "classification": "new_lead",
  "summary": "Prospect wants a one-page lawn care website.",
  "urgency": "high",
  "detected_actions": [
    "draft_reply",
    "suggest_call"
  ],
  "missing_info": [
    "budget",
    "photos"
  ],
  "recommended_next_step": "Draft intake reply and propose call."
}
```

---

## Batch Action Envelope

Multiple actions must be grouped into a single review flow.

Example:

```json
{
  "envelope_id": "email_board_001",
  "actions": [
    {
      "label": "Draft reply to GreenEdge",
      "capability": "gmail_draft_reply",
      "risk_tier": 2
    },
    {
      "label": "Create calendar hold",
      "capability": "google_calendar_event_create_confirmed",
      "risk_tier": 3
    }
  ]
}
```

---

## Approval UX

User should be able to:

- approve all drafts
- approve selected domains
- reject high-risk actions
- defer actions

---

## Voice + Dashboard Flow

Voice:

"Nova, clean up my inbox."

Response:

"I found 6 emails needing action. I prepared drafts and scheduling suggestions. Open the review board?"

Dashboard:

- thread summaries
- draft replies
- calendar suggestions
- approve/reject controls

---

## Goal

```text
Turn email into a daily command surface instead of a passive inbox.
```

This is a core Nova differentiator.
