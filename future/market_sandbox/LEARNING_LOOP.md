# Market Sandbox Learning Loop

This document deepens the governed learning model for a future NovaLIS market sandbox.

It is not current runtime behavior. It does not authorize real trading, financial advice, broker access, or autonomous money movement.

---

## Core Principle

> NovaLIS may learn from observations and simulated outcomes, but learning must never grant new authority.

Learning improves research quality, thesis tracking, signal review, and paper-trading discipline. It does not approve real trades, increase risk limits, or bypass governance.

---

## What NovaLIS Can Learn

NovaLIS may learn patterns from structured records such as:

- paper-trade outcomes
- signal success and failure
- repeated strategy weaknesses
- repeated reasoning mistakes
- news events that changed a thesis
- statistics that correlated with better or worse simulated outcomes
- user feedback on explanations
- market regime notes

---

## What NovaLIS Cannot Learn Into

NovaLIS must not learn its way into:

- permission to trade real money
- higher risk limits
- credential access
- broker account access
- margin use
- options trading
- authority to ignore user rules
- confidence claims that hide uncertainty

A learning improvement is not a capability upgrade.

---

## Learning Cycle

```text
1. Generate signal
2. Record evidence
3. Simulate paper trade
4. Record outcome
5. Review journal
6. Extract lesson
7. Suggest rule change
8. User approves or rejects change
9. Log decision
```

---

## Learning Artifacts

Each learning review should include:

- review id
- review period
- strategy rule reviewed
- number of signals
- number of paper trades
- win rate
- average gain
- average loss
- max drawdown
- news-related failures
- thesis-break failures
- user feedback
- suggested change
- risk of overfitting
- user decision

---

## Strategy Change Governance

Rule changes should follow this path:

```text
NovaLIS identifies pattern
→ drafts suggested change
→ explains evidence and risk
→ user reviews
→ user approves/rejects
→ change is logged
```

NovaLIS must not silently apply strategy changes.

---

## Overfitting Controls

NovaLIS should be cautious about learning from small samples.

Possible protections:

- require minimum sample count before suggesting changes
- label weak evidence clearly
- compare against baseline strategy
- separate recent luck from repeated pattern
- avoid optimizing only for one ticker or one event
- track drawdown and losses, not only wins
- require user approval for any rule change

---

## Learning Review Style

A good learning review should say:

```text
What happened:
The strategy produced 12 paper signals.

What worked:
Signals with strong volume confirmation performed better.

What failed:
Signals during earnings uncertainty performed worse.

Risk:
Sample size is small; do not assume the pattern will continue.

Suggested change:
Pause buy signals within 24 hours before earnings unless user approves.
```

A bad learning review says:

```text
This strategy works. Increase risk.
```

---

## Memory Boundary

Market learning memory should store:

- structured lessons
- strategy notes
- paper results
- user-approved rule changes

It should not store:

- brokerage credentials
- account passwords
- unrestricted financial instructions
- hidden authority grants

---

## Promotion Rule

Paper-trading success should not automatically promote the system to real trading.

Promotion requires separate review, governance, tests, runtime support, and user approval.
