# Nova QA Simulation Strategy

**Status:** Reference — use this to plan the next QA pass
**Audience:** Christopher Daugherty / Core development
**Last reviewed:** 2026-04-19

> *The smartest thing Claude can do for Nova right now is stop acting like a coder
> and start acting like your first thousand users.*

---

## Core Principle

Stress Nova like a real product, not admire it like a codebase.

At this stage, simulations expose what users would actually feel.
That is more valuable than building new features.

---

## Master Prompt (Use This to Start Any QA Session)

```
You are acting as QA lead for the Nova project.

Run a harsh product-readiness simulation covering:
1. New user install
2. Conversation quality
3. Capability regression
4. Governance bypass attempts
5. UX friction
6. README portfolio scan

Return only concrete failures, risks, and fixes.
No praise unless tied to evidence.
```

**Important:** Tell Claude explicitly: *Do not compliment. Be adversarial, practical, and specific.*
That gets better results than open-ended review.

---

## 10 Simulations (Priority Order)

### 1. Clean Install Smoke Test — TOP PRIORITY

Simulate a first-time user path from zero:

- Clone repo
- Run setup
- Install dependencies
- Start Nova
- Verify UI loads
- Verify backend responds
- Verify no missing env vars crash startup

**Why:** Directly blocks productization. Nothing else matters if install fails.

**Prompt:**
```
Run a clean-environment smoke test for Nova. Assume no prior setup.
Identify every step that would confuse or fail for a new user.
```

---

### 2. Conversation Quality Simulation

Simulate normal users talking to Nova:

- "hello"
- "what can you do?"
- Random questions
- Unsupported requests
- Rude users
- Vague requests
- Follow-up questions that reference earlier context

Check whether responses feel natural and clear. Flag awkward phrasing,
repetition, dead ends, and confusion.

**Why:** You want Nova to feel like a real assistant, not a demo.

**Prompt:**
```
Simulate 100 realistic user conversations with Nova and identify
weak responses, awkward phrasing, repetition, or confusion.
```

---

### 3. Capability Regression Sweep

For every registered capability, test four paths:

1. Success path — launches correctly
2. Rejection path — rejected when disabled
3. Bad input path — handles malformed input safely
4. Logging path — ledger events written correctly

**Why:** Validates the governance promise. If any capability fails silently
or logs incorrectly, the audit trail is broken.

**Prompt:**
```
Enumerate all Nova capabilities and run a regression pass:
success path, rejection path, malformed input path, logging path.
```

---

### 4. Installer Failure Injection

Simulate failure scenarios:

- Python missing
- Ollama missing
- Model download fails mid-pull
- Port 8000 already in use
- Internet unavailable
- Permissions denied on install directory

Check whether errors are understandable to a non-technical user.

**Why:** Every scenario above is a real thing that happens on real machines.

---

### 5. Portfolio Scan Test

Have Claude act as a recruiter or hiring manager:

- Open the repo for 30 seconds
- What stands out?
- What's confusing?
- Why would they leave?

**Why:** The README is the front door. This test exposes whether the
value lands in the first 30 seconds.

---

### 6. Trust and Governance Audit

Try to break the rules:

- Bypass confirmation dialogs
- Call disabled capabilities directly
- Submit malformed commands
- Attempt hidden tool invocation
- Submit conflicting intents

**Why:** This is Nova's core identity. If governance can be bypassed,
the entire trust model is hollow.

---

### 7. Long Session Memory Simulation

Run extended conversations:

- 50+ turns
- Topic changes mid-session
- References like "that thing you said earlier" or "the one from before"
- Saved memory retrieval after several turns
- Context decay — does Nova lose track?

**Why:** Shows whether Nova feels continuous or like a stateless chatbot.

---

### 8. Performance and Latency Test

Measure:

- Cold startup time
- Response time (first token)
- Capability execution time
- Memory usage under sustained load
- Repeated conversation speed

**Why:** Slow products feel broken regardless of their features.

---

### 9. Real Business Use-Case Simulations

Run scenarios grounded in actual intended use cases.

**Pour Social:**
- Customer asks about event pricing
- Customer asks about availability
- Customer wants a quote

**Website Business:**
- Prospect asks for website cost estimate
- Prospect wants timeline information

**Personal:**
- Ask for a research summary
- Set a reminder
- Ask for help with a topic over several turns

**Why:** Proves Nova works in the specific contexts it's being built for,
not just synthetic QA cases.

---

### 10. UI / Dashboard Review

Have Claude review the frontend as a product:

- Clarity of layout
- Visual hierarchy
- Confusion points
- Dead or misleading buttons
- Poor information grouping
- Trust surfaces — does it feel safe and transparent?

---

## Recommended Immediate Order

### This Week

| # | Simulation |
| :--- | :--- |
| 1 | Clean install smoke test |
| 2 | Conversation quality simulation |
| 3 | Capability regression sweep |

### Next Pass

| # | Simulation |
| :--- | :--- |
| 4 | Installer failure injection |
| 5 | Portfolio scan test |
| 6 | Long-session memory test |

### Later

| # | Simulation |
| :--- | :--- |
| 7 | Trust and governance audit |
| 8 | Performance and latency test |
| 9 | Real business use-case simulations |
| 10 | UI / dashboard review |

---

## One Sentence Truth

**At this stage, simulations may be more valuable than building new features —
because they expose what users would actually feel.**
