# Nova — Trading Connector Design
Status: PLANNED — not yet started
Updated: 2026-04-02

---

## Goal

Allow Nova to automatically buy and sell assets on behalf of the user using a pre-paid card
or funded brokerage account, governed by user-defined rules, with hard capital limits and
a full audit trail.

The user controls the total capital at risk by how much they deposit into the brokerage account.
Nova can only trade what is in that account. Once the funds are gone, trading stops.

---

## Capital Flow

```
Pre-paid card / bank card
        ↓
Brokerage or exchange account  ←── hard capital ceiling set by user deposit
        ↓
Nova trading API connector     ←── only talks to the account, never the card directly
        ↓
Governor rules gate            ←── checks every trade against user guidelines before execution
        ↓
Trade executed
        ↓
Audit ledger + widget delivery
```

Nova never has access to the card itself — only to the brokerage API key for the funded account.

---

## Supported Platforms (Phase 1)

### Stocks & ETFs — Alpaca Markets
- Commission-free brokerage with a REST API built for automation
- Paper trading mode: fake money, real market data — test Nova's strategy with zero risk
- Free real-time and historical market data via the same API
- Fractional shares: trade with as little as $1
- API key is scoped to the account — no access beyond what is in the account
- Signup: alpaca.markets

### Crypto — Coinbase Advanced Trade API
- Supports BTC, ETH, and major altcoins
- Card funding available in most regions
- Sandbox mode for testing
- API key scoped to trade permissions only (no withdrawal access)

### Future Platforms (not in Phase 1)
- Interactive Brokers (professional-grade, higher complexity)
- Kraken (crypto alternative to Coinbase)
- Binance (global crypto, higher volume)

---

## Paper Trading Mode

**Always start here.** Never go live until Nova's strategy has run in paper mode for at least
2–4 weeks and the results are reviewed.

```
.env setting:
  TRADING_PAPER_MODE=true      ← routes all trades to paper/sandbox account
  TRADING_PAPER_MODE=false     ← live trading (requires explicit opt-in)
```

Paper mode is enforced in the connector — the API endpoint used changes, not the logic.
All rules, logging, and delivery work identically in paper mode so the transition to live
trading changes nothing except the endpoint.

---

## User Guidelines System

The user writes trading rules in plain language. These are stored as a permanent governed
memory record (`user_trading_rules`) and enforced by the Governor before every trade.

### Example User Guidelines

```
- Never spend more than $50 on a single trade
- Only buy BTC and ETH — no altcoins
- Never hold a position overnight — sell before 4:00 PM
- Stop all trading if account balance drops below $200
- Only buy if the signal confidence score is 7 or above
- Maximum 3 trades per day
- Never buy during the first 30 minutes of market open (9:30–10:00 AM)
- If I am in a losing position for more than 2 days, sell regardless of signal
```

### How Guidelines Are Enforced

Before every trade the Governor runs a rules check:

```
Pre-trade checklist (all must pass):
  ✓ Asset is on the allowed list
  ✓ Trade size is within single-trade limit
  ✓ Account balance is above the floor
  ✓ Daily trade count is within limit
  ✓ Signal confidence meets minimum threshold
  ✓ Time of day is within allowed window
  ✓ Position age is within hold limit (if selling)

If any check fails:
  → Trade is refused
  → Refusal logged to audit ledger with reason
  → Widget delivery: "Trade blocked — [reason]"
```

Rules are user-owned and stored as `protected: true` permanent memory.
Nova cannot override them through normal conversation.

---

## Dollar Budget Gate

Mirrors the Phase 9 token budget gate — same architecture, different units.

| State | Condition | Nova Behavior |
|---|---|---|
| Normal | Balance above floor + daily spend within limit | Trade as normal |
| Warning | Balance within 20% of floor OR daily spend at 80% of limit | Trade proceeds, widget shows amber warning |
| Limit | Balance at or below floor OR daily spend limit hit | All trades blocked, widget shows red alert |

```
.env settings:
  TRADING_ACCOUNT_FLOOR=200        ← stop trading if balance drops to this
  TRADING_DAILY_SPEND_LIMIT=150    ← max total spend per calendar day
  TRADING_SINGLE_TRADE_MAX=50      ← max spend per individual trade
```

---

## Trading Template

New OpenClaw template: `market_trader`

### Schedule Options
- Every 15 minutes during market hours (stocks: 9:30 AM – 4:00 PM ET weekdays)
- Every 30 minutes (lower frequency, less noise)
- Manual only (user triggers from dashboard)
- On news event (future: triggered by incoming headline on watched assets)

### Template Steps

```
Step 1: fetch_price_data
  - Pull current price + 1h/4h/1d price history for watched assets
  - Source: Alpaca market data API or Coinbase ticker

Step 2: fetch_news_signal
  - Pull recent headlines for watched assets (Nova cap 48/49 — news)
  - LLM scores sentiment: bullish / neutral / bearish + confidence 1–10

Step 3: generate_signal
  - LLM combines price momentum + news sentiment
  - Output: action (buy / hold / sell), asset, size suggestion, confidence score, reasoning

Step 4: governor_rules_check  [Governor enforces all user guidelines here]
  - If any rule violated: refuse + log + deliver blocked notification
  - If all pass: proceed to execution

Step 5: execute_trade
  - Call brokerage API: place market order for the approved asset/size
  - Record: order ID, filled price, quantity, timestamp

Step 6: log_to_ledger
  - Append full trade record to audit ledger:
    signal, reasoning, rules checked, outcome, filled price, account balance after

Step 7: deliver_summary
  - Widget card: asset, action, price, reasoning summary, account balance
  - Chat (optional): "Bought 0.001 BTC at $82,450. Reason: positive momentum + bullish news on ETF approval."
```

---

## New Capability: execute_trade (Cap ~64)

```json
{
  "id": 64,
  "name": "execute_trade",
  "status": "active",
  "phase_introduced": "10",
  "authority_class": "financial_action",
  "reversible": false,
  "external_effect": true,
  "description": "Places a governed buy or sell order via a connected brokerage or exchange API. Enforces user trading rules and dollar budget gate before every execution.",
  "budget_gated": true,
  "requires_connector": "trading_connector"
}
```

`reversible: false` and `external_effect: true` mean this is one of the most consequential
capability classes in Nova. The Governor treats it accordingly — the rules gate is not
bypassable through chat commands.

---

## New Files Required

### Backend

| File | Purpose |
|---|---|
| `src/connectors/trading_connector.py` | Abstract base class (mirrors email_connector.py pattern) |
| `src/connectors/alpaca_trading_connector.py` | Concrete Alpaca Markets implementation |
| `src/connectors/coinbase_trading_connector.py` | Concrete Coinbase Advanced Trade implementation |
| `src/executors/trade_executor.py` | Cap 64 executor — rules check + API call + ledger write |
| `src/tasks/trading_rules_store.py` | Persistent store for user trading rules and dollar limits |
| `src/usage/trading_budget_store.py` | Dollar budget gate (daily spend, floor check) — mirrors provider_usage_store |

### Config

New `.env` variables:
```
# Trading — Platform
TRADING_PLATFORM=alpaca          # "alpaca" | "coinbase"
TRADING_PAPER_MODE=true          # always start true

# Alpaca
ALPACA_API_KEY=...
ALPACA_API_SECRET=...

# Coinbase
COINBASE_API_KEY=...
COINBASE_API_SECRET=...

# Safety limits (user sets these)
TRADING_ACCOUNT_FLOOR=200
TRADING_DAILY_SPEND_LIMIT=150
TRADING_SINGLE_TRADE_MAX=50
TRADING_MAX_TRADES_PER_DAY=3
TRADING_ALLOWED_ASSETS=BTC,ETH   # comma-separated whitelist
```

---

## Audit Ledger — Trade Record Format

Every trade (executed or blocked) writes a ledger entry:

```json
{
  "event": "TRADE_EXECUTED" | "TRADE_BLOCKED" | "TRADE_FAILED",
  "timestamp": "2026-04-02T09:45:00Z",
  "cap_id": 64,
  "data": {
    "asset": "BTC",
    "action": "buy",
    "size_usd": 45.00,
    "filled_price": 82450.00,
    "quantity": 0.000546,
    "order_id": "abc123",
    "signal_score": 8,
    "signal_reasoning": "Strong upward momentum on 4h chart. 3 bullish headlines in last 2h.",
    "rules_checked": ["asset_whitelist", "single_trade_max", "account_floor", "daily_count"],
    "rules_passed": true,
    "account_balance_after": 455.00,
    "paper_mode": true,
    "block_reason": null
  }
}
```

Blocked trade example:
```json
{
  "event": "TRADE_BLOCKED",
  "data": {
    "asset": "BTC",
    "action": "buy",
    "size_usd": 60.00,
    "rules_passed": false,
    "block_reason": "Single trade size $60 exceeds limit of $50"
  }
}
```

---

## Dashboard Widget

New widget card: `trading_status`

```
┌──────────────────────────────────────────────────┐
│  Trading                          🟢 Paper mode  │
│                                                  │
│  Account balance    $455.00                      │
│  Today's P&L        +$3.20  (+0.7%)              │
│  Trades today       2 / 3                        │
│  Last trade         BTC buy @ $82,450  9:45 AM   │
│                                                  │
│  Last signal        BTC — Bullish (8/10)         │
│  Next check         in 12 min                    │
│                                                  │
│  [View trade history]   [Pause trading]          │
└──────────────────────────────────────────────────┘
```

- Green badge: paper mode. Yellow badge: live mode.
- `Pause trading` button immediately suspends the scheduler without clearing rules.
- `View trade history` opens the full ledger filtered to cap 64 events.

---

## Safety Design Decisions

| Decision | Rationale |
|---|---|
| Paper mode on by default | No live money at risk until user explicitly opts in |
| API key scoped to trade only | Brokerage API keys should have no withdrawal permissions |
| Rules stored as protected memory | Nova cannot talk itself out of enforcing the rules |
| Every trade logged — including blocked ones | Full audit trail of what Nova considered and refused |
| Account floor is a hard stop | When balance hits floor, trading stops entirely until user reviews |
| No leveraged products in Phase 1 | Stocks and spot crypto only — no margin, no options, no futures |
| User must explicitly set TRADING_PAPER_MODE=false | Cannot accidentally go live |

---

## What Nova Is Good At (and Not)

### Good at
- Following rules consistently — never forgets a guideline, never gets emotional
- News sentiment classification — reading headlines and scoring bullish/bearish
- Combining multiple signals into a structured decision with explicit reasoning
- Logging everything — full transparency on why each trade was or wasn't made
- Staying within defined limits — the Governor enforces this at every step

### Not good at
- Predicting markets — no LLM has a genuine price prediction edge
- High-frequency trading — the 15-minute polling loop is the floor, not milliseconds
- Technical analysis at scale — basic momentum is feasible, complex indicators require dedicated quant tools
- Guaranteeing profit — trading involves real risk regardless of automation

The right mental model: **Nova is a disciplined rule follower, not a market oracle.**
It enforces your strategy consistently. The quality of the outcome depends on the quality
of your guidelines.

---

## Build Order

1. `trading_connector.py` abstract base + `alpaca_trading_connector.py` (paper mode first)
2. `trading_rules_store.py` + `trading_budget_store.py`
3. Cap 64 `trade_executor.py` with full rules gate
4. `market_trader` OpenClaw template
5. Dashboard trading widget
6. `.env` variables + `.env.example` update
7. Test suite: paper mode execution, rules gate blocking, dollar budget gate, ledger writes
8. Coinbase connector (Phase 2)
9. Live mode opt-in flow (Phase 2 — requires user to explicitly flip paper mode off in UI)

---

## Open Questions / Things to Add

- [ ] Should the signal step use local model (fast, private) or cloud model (better reasoning)?
- [ ] Should there be a "explain your last trade" chat command that pulls from the ledger?
- [ ] Should the asset watchlist (BTC, ETH, etc.) be editable in the UI separately from the rules?
- [ ] Should Nova send a daily P&L summary as part of the evening digest template?
- [ ] What happens if the brokerage API is unreachable — fail open (skip trade) or fail closed (pause trading)?
- [ ] Should there be a max drawdown rule — "if account drops X% from peak, pause all trading"?
- [ ] Should live mode require a second confirmation step in the UI (not just an .env change)?
- [ ] Tax/reporting: should Nova track cost basis per trade for year-end reporting?

---
