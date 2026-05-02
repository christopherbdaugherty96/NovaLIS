# Active TODO - Nova

**Updated:** 2026-05-02
**Sprint goal:** Memory loop implementation — Stage 3 now active.
**Authority note:** This file is the public task snapshot. Exact runtime truth still comes from generated runtime docs and code.

## Stepwise Execution Order

### Step 1 - Active proof closeout — DONE

- [x] Re-run Daily Brief + continuity proof — PASS (2026-05-02, all 4 proof docs updated)
- [x] Re-run Search Evidence Synthesis functional proof — PASS (source_backed/weak/snippet cases)
- [x] Conversation continuity fields proof — PASS (412 conversation tests, roundtrip verified)
- [x] Full suite — PASS (1877 passed, 4 skipped, exit 0)
- [ ] Capture a short public conversation/search demo (optional, not blocking memory loop)

### Step 2 - Update status after proof — DONE

- [x] Proof results recorded in `docs/demo_proof/daily_operating_baseline/`
- [x] TODO and status docs updated with proof outcome

### Step 3 - Memory loop implementation — ACTIVE SPRINT

### Step 3 - Memory loop implementation

- [ ] Memory full loop - remember / review-list / update / forget / why-used, without silent autosave
- [ ] Add memory receipts for create / update / forget / use
- [ ] Prove memory is not used before confirmation
- [ ] Prove forgotten memory is not reused
- [ ] Prove memory never authorizes action
- [ ] Add Memory UX flows - remember / forget / review saved memory

### Step 4 - Context Pack implementation

- [ ] Implement Context Pack object with source labels, authority labels, budget limits, why-selected metadata, and stale/conflict warnings
- [ ] Prove candidate items are not treated as confirmed
- [ ] Prove runtime truth outranks memory
- [ ] Prove Context Pack budgets are enforced

### Step 5 - Brain discipline and trace

- [ ] Add mode contracts for brainstorm, repo-review, implementation, merge, planning, and action-review
- [ ] Add safe BrainTrace fields without exposing private chain-of-thought
- [ ] Improve conversation follow-up/topic tracking for connector/governance topics
- [ ] Tighten uncertainty wording for health/safety/current-evidence questions

### Step 6 - Routine and workflow surfaces

- [ ] Convert Daily Brief into RoutineGraph v0 only after memory/context foundations exist
- [ ] Capture one everyday workflow demo: plan my week from tasks, notes, calendar context, and priorities, with approval boundary and receipt
- [ ] Capture one business workflow demo: find 5 local businesses that need better websites, draft improvement notes, and create reviewable outreach drafts
- [ ] Define governed workflow workspace shell for everyday workflows, independent automation, and business-owner use cases
- [ ] Draft workflow object model and workflow template schema

## Current Priorities (ordered)

- [ ] Re-run Daily Brief + continuity proof manually in the local UI/API
- [ ] Re-run and record the conversation + search demo flow with Search Evidence Synthesis active
- [ ] Memory full loop - remember / review-list / update / forget / why-used, without silent autosave
- [ ] Context Pack implementation planning after memory loop proof
- [ ] Brain mode contracts and safe trace after memory/context foundations
- [ ] Continue doc/status cleanup where stale "local-only" or planning-as-runtime wording remains
- [ ] Plan cost posture metadata as the next free-first implementation step
- [ ] Plan Google read-only connector foundation after connector governance and cost posture metadata are clear
- [ ] Prepare OpenClaw hardening pass: mandatory EnvelopeFactory, freeform-goal gate, real approval decisions,
      centralized execution guard, boundary detection, and receipts
- [ ] Fuller Trust Review Card / Trust Panel - richer blocked reasons, confirmation previews, receipt history,
      and proof browsing
- [ ] Windows installer VM validation - clean install + bootstrap.log fixes
- [ ] README screenshot or GIF of governed action flow
- [ ] Dashboard home improvements - stronger daily assistant surface
- [ ] Cap 65 P5 live signoff
- [ ] Waitlist activation

## Current Proof Queue

- [ ] Re-run `docs/demo_proof/2026-04-29_conversation_search_proof/CONVERSATION_SEARCH_REPORT.md` prompts after Search Evidence Synthesis merge
- [ ] Capture a short public conversation/search demo
- [ ] Capture one everyday workflow demo: plan my week from tasks, notes, calendar context, and priorities, with approval boundary and receipt
- [ ] Capture one business workflow demo: find 5 local businesses that need better websites, draft improvement notes, and create reviewable outreach drafts
- [ ] Run Cap 64 live signoff only after conversation/search proof is stable
- [ ] Run Cap 65 credential-backed proof only after Shopify env vars are available

## Auralis Manual Validation Queue

Auralis Social Content Workflow Pack is planning-only until manually validated.

- [ ] Pick first niche: restaurants/bars/mobile bartending or lawn care/contractors
- [ ] Create 3 mock client packs
- [ ] Create 30 reusable post templates
- [ ] Create 1 content calendar
- [ ] Create 1 outreach package using the best samples
- [ ] Do not integrate this into Nova runtime until memory loop, Context Pack, and Routine Layer foundations are ready

## Important Principle

Current priorities favor:
- coherent everyday assistant behavior
- visible trust
- onboarding quality
- proof of value
- usability
- truthful readiness

Not raw feature count.

## Paused (do not start)

- Cap 64 P5 live signoff + lock
- Solo Business Assistant shell (Tier 2)
- Google OAuth connector runtime work
- Gmail/Calendar/Drive write or send capabilities
- OpenClaw broad automation
- OpenClaw browser/computer-use expansion until mandatory envelope issuance, real approval decisions, execution guard, boundary detection, and receipts exist
- Voice / ElevenLabs expansion
- Auralis social content runtime integration before manual validation and Nova memory/context/routine foundations

## Governed Workflow Workspace Queue

Canonical product planning note: `docs/product/GOVERNED_WORKFLOW_WORKSPACE_ARCHITECTURE.md`

- [ ] Define everyday workspace shell: Today, Tasks, Projects, People/Contacts, Files/Notes, Messages/Drafts, Content, Research, Automations, Proof/Receipts, Settings/Permissions
- [ ] Define workflow object model: WorkspaceProfile, Workflow, Project, Task, Person, Contact, Conversation, ContentAsset, FileReference, ResearchNote, Approval, Receipt, Automation, Connector
- [ ] Define optional business object extensions: BusinessProfile, Lead, Client, Campaign, Invoice, PaymentStatus, Estimate, Contract, Event, Product, Service, Vendor, AssetLibrary
- [ ] Define permission profiles in user language: Observer, Draft, Assistant, Operator, Admin
- [ ] Define workflow template schema: inputs, objects touched, tools/connectors, permissions, cost posture, approval points, blocked actions, outputs, receipts
- [ ] Define first-run workspace profile onboarding questions and output objects
- [ ] Keep independent business owners as a major use case, not the only use case

## OpenClaw Hardening Queue

Canonical audit: `docs/future/OPENCLAW_ROBUST_HARDENING_AUDIT_2026-05-01.md`

- [ ] Make EnvelopeFactory mandatory for all OpenClaw runs
- [ ] Block legacy direct-run paths when envelope issuance is unavailable
- [ ] Disable or preview-gate freeform goal execution until envelope-issued
- [ ] Replace `/api/openclaw/approve-action` auto-allow with allow / pause / block decisions
- [ ] Add centralized OpenClaw execution guard for tools, network, files, actions, and budgets
- [ ] Add boundary detector for login, submit, payment, upload/download, delete/archive, off-domain, personal data, and personal browser cases
- [ ] Add run, step, action, boundary, failure, cancel, completion, and cleanup receipts
- [ ] Add visible active-run approval UI before browser/computer-use expansion

## Recently Completed

- Agent stack future architecture docs, future backlog, and Auralis social content workflow pack merged and linked
- Daily Brief continuity hardening branch - malformed input degradation, continuity fields in brief,
  deterministic next-action recommendations, proof docs, 114 brief tests
- Conversation continuity fields merged into `SessionConversationContext`: `mode`, `last_decision`,
  `open_loops`, `recent_recommendations`
- Daily Brief MVP merged via PR #68 - deterministic on-demand session brief, 11 sections, live weather +
  calendar, 76 tests
- Brain Planning Preview scaffold merged via PR #64
- YouTubeLIS planning-only tool folder merged via PR #65
- Search Evidence Synthesis merged as deterministic Cap 16 evidence structuring via PR #66
- Free-first cost governance design docs merged as planning only
- OpenClaw robust hardening audit added as planning/recommendation doc
- Governed Workflow Workspace Architecture added as product/architecture planning for everyday workflows, independent automation, and business-owner use cases
- Auralis Website Coworker planning docs integrated
- Cap 64 email draft authority-boundary tests
- Local-first demo proof package
- Conversation + search proof pass
- RequestUnderstanding integration
- Receipt backend groundwork
- Action Receipts / Trust Receipts API groundwork
- Governance hardening and test passes
