# Market Sandbox

This folder documents a possible future NovaLIS market-research and paper-trading sandbox.

It is not current runtime behavior. It is not an active trading capability. It does not authorize NovaLIS to submit real orders, move money, trade options, use margin, operate a brokerage account, or provide financial advice.

The safest first version is a read-only intelligence, statistics, thesis-tracking, learning, and paper-trading system.

---

## Safety Position

Financial automation is critical risk.

NovaLIS may help organize information, learn from outcomes, simulate decisions, and improve research quality, but it should not become the financial authority.

Core rule:

> NovaLIS may analyze markets, track signals, learn from paper-trade results, and improve strategy reviews under strict rules, but real-money action requires separate governance, final human approval, and explicit runtime support.

Learning does not grant authority.

---

## Learning Principle

NovaLIS should be able to get better over time by remembering structured outcomes.

Allowed learning:

- which signals worked or failed in paper trading
- which news types changed a thesis
- which statistics were useful or misleading
- which watchlist rules produced better simulated outcomes
- user feedback on reasoning quality
- trade journal lessons
- market regime observations

Blocked learning:

- secretly changing risk limits
- secretly approving real trades
- hiding losses
- treating past paper success as guaranteed future profit
- overriding user constraints
- learning brokerage credentials
- expanding its own authority

> NovaLIS may improve analysis. It may not improve itself into permission.

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

> market intelligence + watchlist + thesis tracker + statistical signal review + learning loop + paper wallet + trade journal

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

> Trading automation is mostly rules, statistics, risk controls, testing, logging, and review loops.

---

## Correct NovaLIS Model

The safe model is:

```text
Market data
→ news / filings / earnings context
→ approved watchlist
→ statistical feature review
→ strategy rules
→ signal engine
→ risk filter
→ paper wallet
→ trade journal
→ learning review
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
- explaining what statistics mean
- detecting repeated reasoning mistakes
- suggesting strategy rule refinements for user review

The LLM should not be the direct trading authority.

---

## Knowledge Boundaries

NovaLIS can maintain market knowledge in a controlled way:

Allowed knowledge:

- user-approved watchlists
- ticker theses
- known risk notes
- earnings dates
- simulated trade history
- strategy rule descriptions
- lessons from paper trades
- source summaries
- recurring market observations
- user feedback on reasoning quality

Blocked or restricted knowledge:

- brokerage credentials
- account passwords
- hidden/private financial data unless explicitly approved
- any claim that a strategy is guaranteed profitable
- any instruction to bypass risk rules
- any self-granted trading permission

Knowledge should be used to improve explanations, reminders, and analysis consistency — not to grant execution authority.

---

## Market Data vs News vs Opinion

Market sandbox should separate inputs into different categories.

### Market Data

Examples:

- current price
- historical price
- volume
- volatility
- moving averages
- relative strength
- drawdown
- support/resistance estimates

Market data can trigger statistical signals.

### News / Events

Examples:

- earnings
- guidance changes
- SEC filings
- lawsuits
- product launches
- layoffs
- macroeconomic news
- analyst upgrades/downgrades

News should modify confidence or risk, not directly submit trades.

### Opinion / Sentiment

Examples:

- social media hype
- analyst commentary
- influencer claims
- forum discussions

Opinion should be treated as weak evidence unless supported by stronger data.

---

## How News Affects Signals

News should not be treated as a simple buy/sell trigger.

Instead, news should affect:

- confidence
- risk level
- thesis status
- whether a signal is paused
- whether more research is needed

Example:

```text
Price drops 7 percent.
Rule says possible buy.
News shows normal market-wide pullback.
Signal may stay active.
```

Different example:

```text
Price drops 7 percent.
Rule says possible buy.
News shows accounting fraud investigation.
Signal should pause or be blocked as thesis-breaking.
```

---

## Thesis Status

Each watched ticker should have a thesis state:

```text
ACTIVE
WATCHING
WARNING
BROKEN
UNKNOWN
```

Suggested meanings:

- ACTIVE: thesis still supported
- WATCHING: not enough evidence for action
- WARNING: material risk appeared
- BROKEN: original reason no longer holds
- UNKNOWN: insufficient reliable information

No paper or real trade should proceed when thesis status is BROKEN or UNKNOWN unless the strategy explicitly allows that condition and the user approves it.

---

## Statistical Layer

The statistical layer should be simple at first.

Possible first metrics:

- percent change from recent high
- percent change from recent low
- moving average comparison
- volume relative to average
- volatility estimate
- win/loss rate in paper wallet
- average gain
- average loss
- max drawdown
- profit factor
- signal success rate

Important rule:

> Statistics describe past behavior and current conditions. They do not guarantee future returns.

---

## Strategy Rules

Signals should come from explicit strategy rules, not model vibes.

Example buy signal:

```text
Ticker is on approved watchlist.
Price drops at least 5 percent from recent high.
Volume is above average.
Thesis status is ACTIVE or WATCHING.
No thesis-breaking news is detected.
Paper wallet risk limit allows the position.
```

Example sell signal:

```text
Target gain reached.
Stop-loss reached.
Thesis status becomes BROKEN.
Max holding period reached.
Risk limit requires exit.
```

Signals are not orders.

---

## Learning Loop

NovaLIS should improve through a visible review loop:

```text
Signal generated
→ paper trade simulated
→ outcome recorded
→ journal reviewed
→ lesson extracted
→ strategy suggestion drafted
→ user approves or rejects change
```

Learning artifacts should include:

- signal id
- strategy rule used
- market data at signal time
- news context at signal time
- thesis status
- paper result
- what worked
- what failed
- suggested rule change
- user decision

Rule changes should not auto-apply silently.

Recommended rule:

> NovaLIS may suggest strategy changes. The user approves strategy changes.

---

## Signal Confidence

Each signal should include a confidence and risk explanation.

Example fields:

- signal type: buy / sell / hold / watch
- evidence strength
- statistical support
- news risk
- thesis status
- risk limit status
- uncertainty notes

Do not collapse everything into a single magic score unless the components remain visible.

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
- thesis status

### Stage 3 — Statistical Signal Engine

NovaLIS generates signals only from explicit rules and visible data.

Signals should include:

- data trigger
- news modifier
- thesis status
- risk filter
- confidence explanation

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
- statistics used
- news context
- risk notes
- outcome
- lesson learned

### Stage 6 — Learning Review

NovaLIS reviews paper-trading results and suggests improvements.

Allowed:

- identify repeated mistakes
- compare signal types
- suggest rule changes
- mark weak strategies
- recommend more research

Blocked:

- silently changing rules
- silently increasing risk
- enabling real trades

### Stage 7 — Human-Approved Real Trade Draft

Only after paper-trading evidence exists, NovaLIS may prepare a trade draft.

Allowed:

- prepare order details
- explain rationale
- show risk
- request user review

Blocked:

- submitting the order automatically

### Stage 8 — Limited Real-Money Sandbox (Optional, Later)

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
- statistical support
- news context
- thesis status
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
- present simulated returns as guaranteed future returns
- hide risk or uncertainty
- silently modify strategy rules
- self-approve increased authority

---

## Safety Style

Market Sandbox responses should be direct, cautious, and evidence-separated.

Use this style:

```text
Signal: Watch / Possible Buy / Possible Sell / Hold
Evidence: price/statistics/news/thesis
Risk: what could be wrong
Confidence: low/medium/high with explanation
Action: paper trade / journal / wait / ask user
```

Avoid this style:

```text
This will go up.
Guaranteed profit.
The bot knows.
Buy now.
```

---

## Relationship To Governed Desktop Runs

Market Sandbox should not bypass governed desktop runs.

If a future broker or market interface is used, it must operate through task-scoped envelopes, policy evaluation, receipts, and explicit approvals.

The first implementation should not use real broker execution at all.

---

## Best First Build

The first practical build should be:

> Read-only market intelligence + watchlist + thesis tracker + paper wallet + trade journal + learning review.

No real money.

No broker API.

No automated execution.

---

## First Data Model Ideas

A first implementation could include:

```text
TickerProfile
- symbol
- company name
- thesis
- thesis_status
- risk_notes
- approved_watchlist_status

MarketSnapshot
- symbol
- price
- percent_change
- volume
- moving_average_notes
- volatility_notes

NewsEvent
- symbol
- headline
- source
- event_type
- impact: positive / negative / mixed / unknown
- thesis_effect: supports / weakens / breaks / unrelated / unknown

PaperTrade
- symbol
- side
- simulated_entry
- simulated_exit
- size
- reason
- evidence
- outcome
- lesson

LearningReview
- period
- strategy_rule
- total_signals
- paper_outcomes
- observed_pattern
- suggested_change
- user_decision
```

---

## Current Status

Planning only.

Not implemented.

No runtime claim should say NovaLIS can trade, paper trade, manage money, learn trading strategies, or give financial advice until code, tests, and runtime truth support the specific implemented behavior.
