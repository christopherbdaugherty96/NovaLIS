# Market Sandbox Learning Loop

This document defines the governed learning model for a future NovaLIS market sandbox.

It is not current runtime behavior. It does not authorize real trading, financial advice, broker access, or autonomous money movement.

---

## Purpose

The learning loop exists so NovaLIS can improve market research, signal review, paper-trading discipline, and thesis tracking over time.

It should help NovaLIS answer questions like:

- Which signals repeatedly failed?
- Which signals produced better simulated outcomes?
- Which news events actually changed the thesis?
- Which strategy rules are too noisy?
- Which explanations helped the user make better decisions?
- Which assumptions were wrong?

It should not turn NovaLIS into a self-authorizing trader.

---

## Core Principle

> NovaLIS may learn from observations and simulated outcomes, but learning must never grant new authority.

Learning improves research quality, thesis tracking, signal review, and paper-trading discipline. It does not approve real trades, increase risk limits, or bypass governance.

Short form:

> NovaLIS may improve analysis. NovaLIS may not improve itself into permission.

---

## What Improves Over Time

NovaLIS may improve:

- explanation quality
- thesis tracking accuracy
- signal review consistency
- watchlist organization
- news relevance filtering
- paper-trade journaling
- strategy weakness detection
- user-specific preference awareness
- caution around repeated failure patterns

---

## What Never Improves Automatically

NovaLIS must not automatically improve or expand:

- trading authority
- risk limits
- account access
- credential access
- broker access
- allowed asset classes
- real-money execution
- margin, options, short selling, or leverage permissions
- ability to bypass human approval

These require separate explicit governance, implementation, testing, and user approval.

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
- strategy rules that produced too many false signals
- thesis-break conditions that were detected late

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
- silent strategy changes
- hidden autonomy

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
7. Score evidence strength
8. Draft suggested rule change
9. User approves or rejects change
10. Log decision
```

---

## Review Cadence

Learning should happen on a schedule, not constantly mutate behavior after every result.

Recommended cadence:

- Daily: summarize signals and paper trades
- Weekly: review strategy performance
- Monthly: review whether rules should change
- After major market events: review thesis breaks separately

Rule changes should normally wait for weekly or monthly review unless a hard safety issue is discovered.

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
- signal success rate
- false positive notes
- false negative notes
- news-related failures
- thesis-break failures
- market regime notes
- user feedback
- suggested change
- evidence strength
- risk of overfitting
- user decision

---

## Evidence Strength Labels

Every suggested learning should label evidence strength.

```text
LOW: small sample, anecdotal, or noisy pattern
MEDIUM: repeated pattern, but still limited evidence
HIGH: repeated pattern across enough examples and conditions
```

Low evidence should not produce automatic rule changes.

---

## Strategy Change Governance

Rule changes should follow this path:

```text
NovaLIS identifies pattern
→ drafts suggested change
→ labels evidence strength
→ explains possible downside
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
- track missed opportunities, not only bad trades
- compare performance across different market conditions
- require user approval for any rule change

---

## Kill / Pause Suggestions

NovaLIS may recommend pausing a strategy when evidence suggests risk is increasing.

Examples:

- loss streak exceeds threshold
- max drawdown exceeds threshold
- repeated thesis-break failures occur
- signals trigger during known high-risk events
- strategy performs poorly in current market regime

NovaLIS may suggest a pause. The user approves strategy disablement unless a pre-approved safety rule already requires automatic pause.

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

Evidence strength:
Low to medium. Sample size is still small.

Risk:
Do not assume this pattern will continue.

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
- user feedback
- review summaries

It should not store:

- brokerage credentials
- account passwords
- unrestricted financial instructions
- hidden authority grants
- claims that profits are guaranteed

---

## Promotion Rule

Paper-trading success should not automatically promote the system to real trading.

Promotion requires separate review, governance, tests, runtime support, and user approval.

Promotion should require evidence from multiple reviews, not one lucky run.

---

## First Implementation Target

The first implementation should be simple:

```text
paper signal → paper trade → journal entry → weekly learning summary
```

No broker API.

No real money.

No automatic rule changes.

No authority upgrades.
