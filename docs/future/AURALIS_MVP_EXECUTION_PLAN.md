# Auralis MVP Execution Plan

Date: 2026-04-26

Status: Skeleton / future planning

Related docs:

- `AURALIS_NOVALIS_INTEGRATION_GOALS.md`
- `AURALIS_TECHNICAL_INTEGRATION_SPEC.md`

---

## Purpose

Define the first narrow Auralis + NovaLIS overlap that can be built, tested, and sold without overpromising Nova as a full autonomous business agent.

Working MVP:

> Nova Lead Console v1 — structured website inquiries become lead summaries, missing-info checks, draft replies, and follow-up suggestions.

---

## MVP Boundary

### In Scope

- Structured website inquiry intake
- Business profile context
- Lead summary
- Intent and urgency classification
- Missing information detection
- Draft reply generation
- Follow-up suggestion
- Visible action/history record

### Out of Scope

- Autonomous email sending
- Autonomous booking
- Autonomous website publishing
- Payment processing
- Full CRM
- Multi-tenant SaaS billing
- Regulated industry workflows

---

## User Story

A small business owner receives a website inquiry. Nova summarizes what the customer wants, identifies missing information, drafts a response, and suggests the next step. The owner reviews and sends manually.

---

## MVP Flow

1. Customer submits website form.
2. Form creates structured lead payload.
3. Lead payload enters Auralis/Nova intake path.
4. Nova reads the business profile.
5. Nova produces lead summary and draft response.
6. Owner reviews the draft.
7. Owner sends manually or saves for later.
8. Nova records what it did and what it did not do.

---

## Data Inputs

- Customer name
- Customer phone/email
- Service requested
- Location/service area
- Timeline
- Notes/photos if applicable
- Preferred contact method
- Business profile
- Owner approval rules

---

## Outputs

- Lead summary
- Urgency level
- Missing fields
- Suggested next step
- Draft response
- Follow-up reminder suggestion
- Action/trust record

---

## Success Criteria

- Lead is summarized accurately
- Draft reply is useful and editable
- Missing information is clearly identified
- No customer-facing action happens without owner review
- Failure mode does not lose the inquiry
- Workflow is understandable to a nontechnical small business owner

---

## Build Phases

### Phase 1: Static Prototype

- Use sample lead JSON
- Use sample business profile
- Generate summary and draft reply
- No live website integration

### Phase 2: Form Integration Prototype

- Connect one demo website form
- Store or forward structured lead payload
- Generate lead summary

### Phase 3: Owner Review Surface

- Display lead card
- Display draft reply
- Add edit/copy/save behavior

### Phase 4: Trust Record

- Record what Nova read
- Record what Nova drafted
- Record what Nova did not send

### Phase 5: Demo Client Test

- Test with RobsLawnCare or another low-risk demo
- Collect failure cases
- Update schema and prompts

---

## Open Questions

Three of these questions overlap with Open Technical Decisions in `AURALIS_TECHNICAL_INTEGRATION_SPEC.md`. Resolve shared questions there first; answers apply here.

Shared with tech spec (resolve there):
- Storage model: local-first only or hosted components?
- First connector type: local-only, email-forwarded, or form-webhook?
- Lead card UI surface (what UI displays trust records?)

MVP-specific questions:
- What is the minimum business profile schema?
- What logging/trust receipt format is needed for v1?

---

## Next Actions

Shared with tech spec (resolve there first):
- Define lead payload schema
- Define business profile schema

MVP-specific:
- Create 3 sample demo leads
- Create first static lead summary test
- Choose one demo website for first integration
