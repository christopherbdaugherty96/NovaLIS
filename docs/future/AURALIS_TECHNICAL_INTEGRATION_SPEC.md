# Auralis Technical Integration Spec

Date: 2026-04-26

Status: Skeleton / future planning

Related docs:

- `AURALIS_NOVALIS_INTEGRATION_GOALS.md`
- `AURALIS_MVP_EXECUTION_PLAN.md`
- `AURALIS_RISK_AND_POLICY.md`

---

## Purpose

Define how Auralis websites may connect to NovaLIS safely over time.

---

## Design Principles

- Intelligence does not equal authority
- Read-only before write access
- Approval before sensitive actions
- Visible logs / trust receipts
- Smallest useful integration first
- Fail safely

---

## Core Components

### Frontend Surface
- Auralis client websites
- Forms
- Customer-facing pages

### Connector Layer
- Form webhook or payload bridge
- Email forwarding / parsing path
- Analytics input path
- Future calendar path

### Nova Context Layer
- Business profile
- Service catalog
- Approval rules
- Memory / notes if enabled

### Nova Governance Layer
- GovernorMediator
- CapabilityRegistry
- ExecuteBoundary
- NetworkMediator
- Ledger

### Output Layer
- Lead summaries
- Draft replies
- Reports
- Suggestions
- Approved actions

---

## Initial Data Flows

### Flow A: Website Lead
Website form -> structured payload -> Nova analysis -> summary + draft

### Flow B: Email Inquiry
Email text -> read path -> summary + draft

### Flow C: Metrics Review
Analytics data -> reporting path -> insight summary

---

## Security / Governance Questions

- Where is client data stored?
- How long is it retained?
- Who can access it?
- What is logged?
- What requires approval?
- How are failures surfaced?

---

## Future Integrations

- Calendar
- CRM
- CMS publish path
- SMS
- Voice intake
- Multi-location support

---

## Open Technical Decisions

- Local-first only or hosted components?
- Shared tenant model or isolated client profiles?
- What auth model is needed?
- What connector should be first?
- What UI displays trust records?

---

## Next Actions

- Define lead payload schema
- Define business profile schema
- Map first MVP to current runtime surfaces
- Identify missing capabilities
