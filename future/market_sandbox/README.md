# Market Sandbox

This folder documents a possible future NovaLIS market-research and paper-trading sandbox.

It is not current runtime behavior. It is not an active trading capability. It does not authorize NovaLIS to submit real orders, move money, trade options, use margin, or operate a brokerage account.

---

## Why This Belongs In Future

A market sandbox fits NovaLIS as a research, analysis, journaling, and governed decision-support system.

It does not fit as unrestricted autonomous trading.

NovaLIS' current architecture is strongest when intelligence proposes and governance controls. Financial execution must remain one of the strictest categories because mistakes can lose real money.

---

## Current NovaLIS Architecture Fit

Current NovaLIS already supports several relevant patterns:

- governed research and reporting
- external reasoning review
- memory and continuity
- scheduled/read-only checking surfaces
- ledgered execution
- capability-gated action paths
- no broad autonomy invariant
- no hidden execution outside explicit scheduler carve-out

This means a market sandbox should begin as:

> market intelligence + watchlist + thesis tracker + paper wallet + trade journal

not as:

> NovaLIS directly trades real money.

---

## Lessons From Existing Trading Bot Patterns

Open-source trading bots commonly include:

- data ingestion
- strategy rules
- indicator calculations
- backtesting
- paper trading / dry-run mode
- exchange or broker connectors
- configuration
- risk limits
- logging
- dashboards or reports

The useful lesson for NovaLIS is not "let AI guess trades."

The useful lesson is:

> Trading automation is mostly rules, risk controls, testing, logging, and review loops.

---

## Correct NovaLIS Model

The safe model is:

```text
Market data
→ news / filings / earnings context
→ approved watchlist
→ strategy rules
→ signal engine
→ paper wallet
→ trade journal
→ performance review
→ optional human-approved real trade draft later
```

The LLM may help with:

- summarizing news
- explaining earnings
- identifying risks
- comparing thesis changes
- generating plain-English trade rationale
- reviewing journal entries

The LLM should not be the direct trading authority.

---

## Stage Plan

### Stage 1 — Market Research Assistant

NovaLIS reads and summarizes market news, ticker context, earnings, and user-defined interests.

Allowed:

- research
- summarize
- explain risks
- build watchlists

Blocked:

- real orders
- account access
- money movement

### Stage 2 — Watchlist + Thesis Tracker

NovaLIS tracks why a ticker is being watched.

For each ticker:

- thesis
- risk
- trigger conditions
- relevant news
- earnings dates
- user notes

### Stage 3 — Rule-Based Signal Engine

NovaLIS generates signals only from explicit rules.

Example:

```text
If approved ticker drops 5 percent from recent high
and no thesis-breaking news is detected
and volume confirms movement
then mark as possible buy signal.
```

Signals are not orders.

### Stage 4 — Paper Wallet

NovaLIS simulates trades with fake money.

Example:

- starting paper wallet: $50
- max simulated trade: $5
- no options
- no margin
- no shorts
- approved watchlist only

### Stage 5 — Trade Journal / Review

Every simulated trade records:

- ticker
- signal
- entry price
- exit price
- reason
- evidence
- risk notes
- outcome
- lesson learned

### Stage 6 — Human-Approved Real Trade Draft

Only after paper-trading evidence exists, NovaLIS may prepare a trade draft.

Allowed:

- prepare order details
- explain rationale
- show risk
- request user review

Blocked:

- submitting the order automatically

### Stage 7 — Limited Real-Money Sandbox (Optional, Later)

Only after strong testing, NovaLIS could possibly support a very small real-money sandbox.

Required restrictions:

- max account exposure: user-defined, e.g. $50
- max trade size: small, e.g. $5–$10
- max trades per day
- approved watchlist only
- limit orders only
- no margin
- no options
- no shorts
- no account changes
- no deposits or withdrawals
- daily and weekly loss stops
- full receipt every trade
- human final approval unless a separate tested policy exists

---

## Governance Category

Financial actions should be treated as critical risk.

A future financial envelope should include:

- ticker
- side
- quantity or dollar amount
- order type
- limit price
- account label
- max loss
- reason
- evidence
- approval status
- stop condition
- receipt requirement

---

## Hard Blocks

By default, NovaLIS must not:

- submit real orders
- trade options
- use margin
- short sell
- move money
- change brokerage settings
- enter credentials
- bypass user approval
- trade unapproved assets
- continue after risk limit is hit

---

## Relationship To Governed Desktop Runs

Market Sandbox should not bypass governed desktop runs.

If a future broker or market interface is used, it must operate through task-scoped envelopes, policy evaluation, receipts, and explicit approvals.

The first implementation should not use real broker execution at all.

---

## Best First Build

The first practical build should be:

> Read-only market intelligence + paper wallet + trade journal.

No real money.

No broker API.

No automated execution.

---

## Current Status

Planning only.

Not implemented.

No runtime claim should say NovaLIS can trade, paper trade, or manage money until code, tests, and runtime truth support it.
