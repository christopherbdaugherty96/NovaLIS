# Paper Wallet

Defines simulated trading behavior for the future Market Sandbox.

This is not current runtime behavior. It does not authorize real trading, broker access, account access, money movement, or financial advice.

---

## Purpose

The Paper Wallet gives NovaLIS a safe learning environment with no real money.

It exists to test:

- strategy rules
- signal quality
- risk limits
- journal discipline
- learning reviews

It must not be treated as proof that a strategy will work with real money.

---

## Core Rule

> Paper trading may train discipline and review quality. It does not grant trading authority.

---

## Hard Boundaries

The Paper Wallet must not:

- submit real orders
- connect to a live broker
- move money
- use margin
- trade options
- short sell
- change account settings
- store brokerage credentials
- claim simulated returns are guaranteed real returns

---

## Wallet Parameters

A paper wallet should define:

```text
PaperWallet
- wallet_id
- starting_balance
- current_cash
- realized_pnl
- unrealized_pnl
- max_trade_size
- max_open_positions
- daily_loss_limit
- weekly_loss_limit
- allowed_assets
- blocked_assets
- created_at
```

Example starter settings:

```text
starting_balance: 50.00
max_trade_size: 5.00
max_open_positions: 3
daily_loss_limit: 2.50
weekly_loss_limit: 7.50
allowed_assets: approved watchlist only
blocked_assets: options, margin, shorts, leverage
```

---

## Position Model

Each open simulated position should track:

```text
PaperPosition
- position_id
- symbol
- side
- simulated_entry_price
- simulated_quantity
- entry_time
- entry_signal_id
- thesis_status_at_entry
- stop_loss
- target_price
- max_holding_period
- current_status
```

---

## Trade Record

Each simulated trade should record:

```text
PaperTrade
- trade_id
- wallet_id
- symbol
- side
- simulated_order_type
- requested_price
- simulated_fill_price
- quantity
- size
- signal_id
- strategy_rule
- market_snapshot_id
- news_context_id
- thesis_status
- fees_assumed
- slippage_assumed
- outcome
- lesson
```

---

## Fill Model

The first version should use a simple conservative fill model.

Suggested defaults:

- market orders are simulated with small slippage
- limit orders only fill if price reaches the limit
- failed fills are logged
- no perfect fills unless explicitly configured

This prevents the paper wallet from pretending execution is easier than reality.

---

## Slippage / Spread Assumptions

Every simulated trade should include assumptions.

Example:

```text
slippage_assumed: 0.10 percent
spread_assumed: basic estimate or unknown
fees_assumed: 0 unless configured
```

If assumptions are unknown, the result should be labeled approximate.

---

## Risk Controls

The Paper Wallet should block or pause simulated trades when:

- max trade size is exceeded
- daily loss limit is reached
- weekly loss limit is reached
- max open positions is reached
- ticker is not on approved watchlist
- thesis status is BROKEN or UNKNOWN
- strategy is paused
- market data is stale
- signal confidence is too low

---

## Lifecycle

```text
Signal generated
→ risk filter checks
→ paper order created
→ simulated fill evaluated
→ position opened or rejected
→ position monitored
→ exit condition triggered
→ trade closed
→ journal entry created
→ learning review can use outcome
```

---

## Exit Conditions

A paper position may close when:

- target price reached
- stop loss reached
- thesis breaks
- max holding period reached
- user closes simulated position
- strategy pause rule triggers

---

## Metrics

Paper wallet should calculate:

- win rate
- average gain
- average loss
- realized PnL
- unrealized PnL
- max drawdown
- profit factor
- open exposure
- loss streak
- signal success rate

---

## Journal Integration

Every simulated trade should produce a journal entry.

The journal should include:

- why the trade was simulated
- what data supported it
- what news modified it
- what risk existed
- what happened
- what should be learned

---

## Learning Integration

The paper wallet feeds the learning loop only through structured records.

It may support:

- strategy review
- signal quality analysis
- thesis-break review
- overfitting warnings

It must not:

- silently change strategy rules
- increase risk limits
- enable real trading

---

## First Implementation Target

Start simple:

```text
approved ticker
→ generated signal
→ simulated limit order
→ paper trade record
→ journal entry
→ weekly learning summary
```

No broker API.

No real money.

No automatic strategy changes.

---

## Current Status

Planning only.

Do not claim NovaLIS supports paper trading until code, tests, and runtime truth support it.
