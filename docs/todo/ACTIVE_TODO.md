# Active TODO - Nova

**Updated:** 2026-05-01
**Sprint goal:** Cap 16 current-information reliability + conversation/search proof.
**Authority note:** This file is the public task snapshot. Exact runtime truth still comes from generated runtime docs and code.

## Current Priorities (ordered)

- [ ] Re-run and record the conversation + search demo flow after Search Evidence Synthesis merge
- [ ] Improve conversation follow-up/topic tracking for connector/governance topics
- [ ] Tighten uncertainty wording for health/safety/current-evidence questions
- [ ] Continue doc/status cleanup where stale "local-only" or planning-as-runtime wording remains
- [ ] Plan cost posture metadata as the next free-first implementation step
- [ ] Plan Google read-only connector foundation after connector governance and cost posture metadata are clear
- [ ] Prepare OpenClaw hardening pass: mandatory EnvelopeFactory, freeform-goal gate, real approval decisions, centralized execution guard, boundary detection, and receipts
- [ ] Fuller Trust Review Card / Trust Panel - richer blocked reasons, confirmation previews, receipt history, and proof browsing
- [ ] Windows installer VM validation - clean install + bootstrap.log fixes
- [ ] README screenshot or GIF of governed action flow
- [ ] Daily Brief MVP - schedule, priorities, reminders, recent actions
- [ ] Memory UX flows - remember / forget / review saved memory
- [ ] Dashboard home improvements - stronger daily assistant surface
- [ ] Cap 65 P5 live signoff
- [ ] Waitlist activation

## Current Proof Queue

- [ ] Re-run `docs/demo_proof/2026-04-29_conversation_search_proof/CONVERSATION_SEARCH_REPORT.md` prompts after Search Evidence Synthesis merge
- [ ] Capture a short public conversation/search demo
- [ ] Run Cap 64 live signoff only after conversation/search proof is stable
- [ ] Run Cap 65 credential-backed proof only after Shopify env vars are available

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

- Brain Planning Preview scaffold merged via PR #64
- YouTubeLIS planning-only tool folder merged via PR #65
- Search Evidence Synthesis merged as deterministic Cap 16 evidence structuring
- Free-first cost governance design docs merged as planning only
- OpenClaw robust hardening audit added as planning/recommendation doc
- Auralis Website Coworker planning docs integrated
- Cap 64 email draft authority-boundary tests
- Local-first demo proof package
- Conversation + search proof pass
- RequestUnderstanding integration
- Receipt backend groundwork
- Action Receipts / Trust Receipts API groundwork
- Governance hardening and test passes
