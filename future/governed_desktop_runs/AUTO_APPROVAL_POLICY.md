# Auto Approval Policy

Defines when NovaLIS may act without explicit user approval.

---

## Core Rule

> No action should be auto-approved unless explicitly categorized and bounded.

---

## Levels

Level 0 — No Auto Approval
- everything requires user approval

Level 1 — Read-Only
- checking data
- reading pages
- no state changes

Level 2 — Preparation
- drafts
- plan generation
- no execution

Level 3 — Limited Execution
- only pre-approved low-risk actions
- strict scope
- rate limited

Level 4 — Trusted Flow (rare)
- narrow workflows
- pre-approved paths
- strong stop conditions

---

## Always Blocked

- purchases
- publishing
- credential entry
- money movement
- account changes

---

## Requirements

Auto-approved actions must:

- stay within envelope
- produce receipts
- stop on uncertainty
- be interruptible

---

## Current Status

Planning only
