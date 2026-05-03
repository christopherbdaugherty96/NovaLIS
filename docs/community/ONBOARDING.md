# Nova Contributor Onboarding

NovaLIS is a governance-first local AI system.

The core principle is simple:

> Intelligence is not authority.

Nova may reason, summarize, search, draft, explain, and recommend. Real actions must stay bounded by capability checks, execution boundaries, confirmation where required, and visible receipts.

This guide is for people who want to understand the project, run it, or contribute without weakening the governance model.

---

## 1. Start Here

Read these first:

1. `README.md` — project overview and entry links
2. `docs/current_runtime/CURRENT_RUNTIME_STATE.md` — generated runtime truth
3. `docs/status/CURRENT_WORK_STATUS.md` — human-maintained current work state
4. `CONTRIBUTING.md` — governance rules for contributions

Runtime truth comes from code and generated artifacts. If documents disagree, `docs/current_runtime/CURRENT_RUNTIME_STATE.md` wins for runtime behavior.

---

## 2. What Nova Is

Nova is not a general chatbot and not an uncontrolled agent.

Nova is a local AI runtime/workspace that separates reasoning from authority. The system is designed so that intelligence can expand while execution remains visible, bounded, and reviewable.

The execution model is governed through the runtime authority spine:

```text
User -> GovernorMediator -> Governor -> CapabilityRegistry -> SingleActionQueue -> LedgerWriter -> ExecuteBoundary -> Executor
```

Do not bypass this path when adding or changing runtime behavior.

---

## 3. What Works Today

Use `docs/current_runtime/CURRENT_RUNTIME_STATE.md` for the exact current capability list.

At a high level, Nova currently includes governed surfaces for:

- web/current-information search
- local website opening
- local text-to-speech
- system media and brightness controls
- approved file/folder opening
- response verification
- OS diagnostics
- news and intelligence brief surfaces
- calendar/weather/news snapshots
- screen capture and screen analysis
- explain-anything routing
- explicit memory governance
- external reasoning review
- bounded OpenClaw execution surface
- local email draft creation through `mailto:`
- read-only Shopify intelligence reporting

Do not claim broader functionality unless generated runtime truth and code prove it.

---

## 4. What Is Not Done Yet

Do not overstate these areas:

- broad autonomous execution
- full Trust Panel system
- full Phase-8 governed envelope execution
- one-click consumer installer
- full first-run onboarding wizard
- Google OAuth/Gmail/Calendar/Drive runtime connector
- Gmail send/write authority
- Shopify write authority
- complete workflow workspace runtime shell
- full background daily operating system
- unconstrained OpenClaw/browser/computer-use execution

Planning docs may describe these directions, but planning is not runtime truth.

---

## 5. Safe Ways to Help

Good contribution areas:

- tests that enforce existing boundaries
- bug fixes that preserve governed behavior
- docs that clarify current truth without overstating runtime status
- UI/UX improvements that make governance more visible
- installer and setup validation
- proof/demo capture
- runtime-doc drift checks
- Trust Review Card / Trust Panel design work
- connector research that stays read-only until governance is proven
- workflow templates that remain draft/review-first

Risky contribution areas that require extra review:

- new capabilities
- executor changes
- network access
- file write/delete behavior
- background/scheduled execution
- OpenClaw expansion
- connector writes
- email/account actions
- anything that touches credentials or external systems

Forbidden contribution patterns:

- direct executor bypasses
- direct network bypasses around `NetworkMediator`
- hidden background loops
- autonomous sending, purchasing, posting, deploying, or destructive action
- capability changes without runtime/governance updates and tests

---

## 6. First Local Run

Use the current README/Quickstart if these steps drift.

Typical development flow:

```bash
cd nova_backend
python -m uvicorn src.brain_server:app --host 127.0.0.1 --port 8000
```

Then open the local dashboard in your browser.

Some surfaces require local dependencies, API keys, model files, or OS-specific setup. If a feature does not work locally, check the relevant docs before assuming it is broken.

---

## 7. First Things to Try

After starting Nova, try low-risk flows first:

1. Ask Nova what it can do right now.
2. Run a current-information/search request.
3. Save an explicit memory item.
4. Review or forget that memory item.
5. Ask for an explanation or verification.
6. Check runtime/status surfaces.

Avoid testing destructive, external, or account-touching workflows until you understand the governance path.

---

## 8. Contribution Checklist

Before opening a PR, answer:

- Does this change runtime behavior?
- Which runtime surfaces are impacted?
- Does it add, remove, or change a capability?
- Does it touch network, filesystem, email, account, browser, connector, or OS execution?
- Does it preserve GovernorMediator / CapabilityRegistry / ExecuteBoundary / NetworkMediator / Ledger boundaries?
- Are tests updated?
- Are runtime docs generated, not hand-edited?
- Are human-facing docs careful about what is implemented vs planned?

Every PR should clearly state:

```text
Behavior change: yes/no
Impacted runtime surfaces: ...
Tests run: ...
Runtime docs changed: yes/no
Governance risk: low/medium/high
```

---

## 9. Current Project Direction

Nova is moving toward a governed AI workspace for everyday workflows and independent automation.

That direction includes personal workflows, local-first assistant workflows, creator/business workflows, research workflows, connector-backed read surfaces, and approved automation routines.

The important constraint remains:

> Workflows may become more capable, but authority must remain bounded, visible, and reviewable.

---

## 10. Where To Start Helping

Recommended first contribution tracks:

1. Documentation cleanup: remove stale claims and link to generated runtime truth.
2. Tests: add boundary tests for governance, memory, context, and connector behavior.
3. UI: make trust, receipts, and approval state easier to see.
4. Setup: validate install/run steps on a clean machine.
5. Proof: capture short demos that show what works today.
6. Workflow planning: define draft-first workflows that do not publish, send, buy, deploy, or mutate external systems without approval.

When unsure, choose the safer contribution: tests, docs, proof, setup, or UI clarity.

---

## 11. Contributor Rule of Thumb

A change is probably aligned with Nova if it makes the system:

- safer
- clearer
- easier to verify
- easier to install
- easier to explain
- more honest about current truth
- more visible in its approvals and receipts

A change is probably misaligned if it makes Nova:

- more autonomous without governance
- harder to audit
- easier to bypass
- less clear about what is real vs planned
- dependent on hidden background behavior
- capable of external action without explicit boundaries
