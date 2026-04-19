# Nova QA Simulation Strategy

**Status:** Reference — use this to plan the next QA pass
**Audience:** Christopher Daugherty / Core development
**Last reviewed:** 2026-04-19

---

## Core Principle

> Stress Nova like a real product, not admire it like a codebase.

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

---

## Important Rule

Tell Claude:

> Do not compliment. Be adversarial, practical, and specific.

That gets better results.

---

## 10 Simulations

### 1. Clean Install Smoke Test — Top Priority

Simulate a first-time user path from zero:

- Clone repo
- Run setup
- Install dependencies
- Start Nova
- Verify UI loads
- Verify backend responds
- Verify no missing env vars crash startup

**Why:** This directly helps productization.

**Prompt:**
```
Run a clean-environment smoke test for Nova. Assume no prior setup.
Identify every step that would confuse or fail for a new user.
```

---

### 2. Capability Regression Sweep

For every registered capability, test four paths:

1. Success path — launches correctly
2. Rejection path — rejected when disabled
3. Bad input path — handles malformed input safely
4. Logging path — ledger events written correctly

**Why:** This validates the governance promise.

**Prompt:**
```
Enumerate all Nova capabilities and run a regression pass:
success path, rejection path, malformed input path, logging path.
```

---

### 3. Conversation Quality Simulation

Simulate normal users talking to Nova:

- "hello"
- "what can you do?"
- Random questions
- Unsupported requests
- Rude users
- Vague requests
- Follow-up questions

Check whether responses feel natural and clear.

**Why:** You said you want Nova to feel like a real assistant.

**Prompt:**
```
Simulate 100 realistic user conversations with Nova and identify
weak responses, awkward phrasing, repetition, or confusion.
```

---

### 4. Installer Failure Injection

Simulate failure scenarios:

- Python missing
- Ollama missing
- Model download fails
- Port in use
- Internet unavailable
- Permissions denied

Check whether errors are understandable to a non-technical user.

**Why:** Huge for shipping.

---

### 5. Performance and Latency Test

Measure:

- Cold startup time
- Response time
- Capability execution time
- Memory usage
- Repeated conversation speed

**Why:** Slow products feel broken.

---

### 6. Trust and Governance Audit

Try to break the rules:

- Bypass confirmation dialogs
- Call disabled capabilities directly
- Submit malformed commands
- Attempt hidden tool invocation
- Submit conflicting intents

**Why:** This validates Nova's core identity.

---

### 7. UI / Dashboard Review

Have Claude review the frontend as a product:

- Clarity of layout
- Visual hierarchy
- Confusion points
- Dead or misleading buttons
- Poor information grouping
- Trust surfaces — does it feel safe and transparent?

---

### 8. Long Session Memory Simulation

Run extended conversations:

- 50+ turns
- Topic changes mid-session
- References like "that one" or "what you said earlier"
- Saved memory retrieval
- Context decay — does Nova lose track?

**Why:** Shows whether Nova feels continuous or like a stateless chatbot.

---

### 9. Real User Use-Case Simulations

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

---

### 10. Portfolio Scan Test

Have Claude act as a recruiter or hiring manager:

- Open the repo for 30 seconds
- What stands out?
- What's confusing?
- Why would they leave?

**Why:** This can massively help the README.

---

## Recommended Immediate Order

### This Week

1. Clean install smoke test
2. Conversation quality simulation
3. Capability regression sweep

### Next

4. Installer failure injection
5. Portfolio scan test
6. Long-session memory test

---

## My Honest View

At this stage, simulations may be **more valuable than building new features**,
because they expose what users would actually feel.

---

## One Sentence Truth

**The smartest thing Claude can do for Nova right now is stop acting like a coder
and start acting like your first thousand users.**
