# Auralis Digital Client Intake OS — Second Pass Review

Last updated: 2026-05-06

Status: second-pass review and NovaLIS integration boundary note.

Primary document: `docs/future/AURALIS_DIGITAL_CLIENT_INTAKE_OS.md`

This note does not replace the primary future concept document. It tightens the NovaLIS boundary, clarifies what would be allowed later, and prevents this Auralis business idea from being mistaken for current runtime work.

---

## Second-Pass Verdict

The concept belongs in NovaLIS as a future product direction, but it must remain paused under the current priority lock.

The right long-term idea is:

```text
Auralis structured lead intake
→ lead record
→ Nova governed review card
→ Nova lead summary / missing-info check / draft follow-up
→ user approval
→ manual or governed send/action path
```

The right current NovaLIS status is:

```text
Future concept only.
No runtime implementation.
No new capability.
No connector expansion.
No business automation expansion.
```

---

## Why This Must Stay Future-Only Right Now

NovaLIS is under an active priority lock.

The only active sequence is:

```text
RequestUnderstanding review card
→ local capability signoff matrix
→ OpenClawMediator skeleton
→ first read-only OpenClaw workflow proof
```

Auralis intake integration is not part of that active sequence unless it is used later as a read-only proof with safe/sample/local input and no external action.

Therefore, do not use this concept to justify:

```text
Gmail runtime connector work
Google OAuth work
CRM write connectors
public chatbot integration
email sending
proposal sending
quote automation
payment automation
client-facing action automation
```

Those remain outside the current lock.

---

## Correct Nova Role

Nova should not be the public-facing Auralis website chatbot at first.

Nova’s correct role is internal, governed, and review-oriented.

Allowed future role:

```text
Read a structured lead record
Summarize the lead
Identify missing information
Recommend likely package or route
Draft a follow-up message
Create a review card
Wait for user approval before any action
Produce a receipt of what happened and what did not happen
```

Not allowed without explicit governed implementation:

```text
Send the message
Quote a binding price
Promise a timeline
Accept a job
Charge payment
Update external CRM state
Create a client folder in an external system
Schedule a call
Change project state as final truth
```

---

## Best Near-Term Use Inside NovaLIS

If this concept is used during the current OpenClaw read-only proof stage, use it only as a safe local sample workflow.

Good proof candidate:

```text
Business Follow-Up Brief
```

Input:

```text
A local sample JSON lead record
A local sample Auralis service/pricing reference
A local sample follow-up policy
```

Output:

```text
Lead summary
Fit score recommendation
Missing information list
Draft follow-up text
Non-action receipt
```

Hard constraints:

```text
No live Gmail
No live CRM
No external writes
No autonomous send
No real customer data unless explicitly provided by user for the session
No persistent business automation
```

This would support the priority lock only if framed as read-only workflow proof, not integration expansion.

---

## Future Capability Shape

If this becomes a real NovaLIS feature later, it should not be one broad “Auralis automation” capability.

It should be decomposed into explicit, bounded surfaces.

Possible future capability surfaces:

```text
read_lead_record
summarize_lead_record
draft_follow_up
prepare_quote_review
prepare_project_checklist
create_local_business_brief
```

Possible future connector surfaces, if governed:

```text
read_form_submission
read_crm_record
create_local_draft_only
read_calendar_availability
create_reviewed_task
```

Write actions must remain separate from read/reasoning actions.

Drafting must remain separate from sending.

Recommendation must remain separate from execution.

---

## Required Review Card Fields

Any Nova review card for an Auralis lead should show:

```text
Request type
Lead source
Business name
Project type
Main goal
Budget range
Timeline
Existing assets
Risk class
Authority boundary
Missing information
Recommended next action
Draft status
Execution status
Receipt / ledger reference
```

The card should explicitly say whether any external action happened.

Default should be:

```text
execution_performed = false
authorization_granted = false
```

---

## Draft Follow-Up Boundary

Nova may eventually draft this kind of message:

```text
Hi [Name], thanks for reaching out about your website project for [Business]. Based on what you shared, it sounds like you may need [recommended path]. Before giving you a clean quote, I would want to confirm [missing information].

Would you prefer to go over this by text, email, or a quick call?
```

But the draft must be clearly labeled:

```text
Draft only. Not sent.
```

If Cap 64 is used in the future, remember the current boundary:

```text
Cap 64 creates a local mailto draft only.
Nova does not autonomously transmit email.
User manually reviews and sends.
```

Do not describe Cap 64 as an inbox connector or autonomous email sender.

---

## Data and Privacy Boundaries

Lead records may contain personal data.

Potential fields:

```text
name
phone
email
business name
website URL
budget range
project notes
```

Therefore future handling must include:

```text
explicit user-provided or governed read source
source label
session visibility
no silent memory writes
no hidden background processing
no uncontrolled external transmission
receipt of any action taken
clear deletion/archive path if stored locally
```

If the data comes from a real client, it should not be used as a demo without explicit permission.

---

## Future Architecture Sketch

A safe future architecture would look like:

```text
Auralis lead source
→ governed read connector or user-provided JSON
→ Nova lead parser
→ RequestUnderstanding / review card
→ lead summary and missing-info analysis
→ draft follow-up proposal
→ user approval gate
→ local draft creation or manual copy path
→ receipt / ledger event
```

This architecture keeps the core Nova rule intact:

```text
Intelligence is not authority.
```

---

## Do Not Overstate

Do not claim any of the following unless implemented and verified:

```text
Nova is connected to Auralis live leads.
Nova reads Auralis form submissions.
Nova manages the Auralis CRM.
Nova sends follow-up emails.
Nova creates quotes automatically.
Nova updates project statuses.
Nova schedules client calls.
Nova has a public-facing website assistant.
```

The current truthful claim is:

```text
NovaLIS contains a future planning document for a governed Auralis Digital intake-review workflow.
```

---

## Acceptance Criteria Before Future Runtime Work

Before implementing this as Nova runtime work, confirm:

```text
[ ] The active priority lock no longer blocks this workstream, or the work directly supports the locked read-only proof.
[ ] A local/sample read-only proof exists first.
[ ] The lead record schema is stable.
[ ] The authority boundary is explicit.
[ ] Review card payload supports the needed fields.
[ ] The connector source is read-only or explicitly user-provided.
[ ] External write actions are separate capabilities.
[ ] Drafting and sending are separate states.
[ ] Every action has a receipt.
[ ] Generated runtime truth is updated if capabilities change.
```

---

## Final Second-Pass Position

Keep the primary future document.

Do not implement it as a Nova feature yet.

If used soon, use it only as a safe read-only workflow proof:

```text
local sample lead record
→ Nova summary
→ missing-info list
→ draft follow-up
→ non-action receipt
```

That path fits Nova’s governance-first identity and avoids turning Auralis intake into uncontrolled automation.