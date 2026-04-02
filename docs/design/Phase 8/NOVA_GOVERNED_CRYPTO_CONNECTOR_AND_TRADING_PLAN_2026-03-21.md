# Nova Governed Crypto Connector And Trading Plan
Date: 2026-03-21
Status: Planning packet only; current product roadmap plus later governed trading phases
Scope: Define the safest way to add Crypto.com support to Nova, including public market data, paper trading, approval-gated live orders, and much-later autonomous trading boundaries

## Purpose
This packet answers a practical product question:

Can Nova eventually support Crypto.com and even auto trade in the future?

The honest answer is:
- yes, technically it could
- but the safe and responsible roadmap is layered
- the first version should be read-only market data, not autonomous live trading

This is not runtime truth.
It is a design and phase-placement roadmap for crypto market data and any future trading-related features.

## Plain-English Recommendation
The best safe roadmap is:

1. public market data
2. watchlists and alerts
3. paper trading and simulation
4. approval-gated live orders
5. tightly bounded semi-automatic rules
6. fully autonomous trading only much later, if ever

That preserves usefulness without turning Nova into an unsafe trading bot too early.

## Best First Version
If you want Crypto.com specifically, the best first slice is:
- read-only public market data only
- no account access
- no wallet actions
- no deposits
- no withdrawals
- no trading

That first slice is useful for:
- crypto price lookups
- market snapshots
- watchlists
- crypto-related brief/news context
- chart and trend summaries

## APIs You Would Need

### Stage 1 - Public Market Data
For a safe first version, the main Crypto.com Exchange API v1 endpoints would be the public market data endpoints:
- `public/get-tickers`
- `public/get-book`
- `public/get-candlestick`
- `public/get-trades`
- relevant public WebSocket subscriptions such as:
  - `ticker.{instrument_name}`
  - `book.{instrument_name}.{depth}`
  - `trade.{instrument_name}`
  - `candlestick.{time_frame}.{instrument_name}`

Why these are the right first APIs:
- they are read-only
- they support price and market views
- they do not require Nova to act on funds

### Stage 2 - Private Read-Only Account Context
Only later, and only if you want account-aware features, consider private read-only endpoints such as:
- `private/user-balance`
- `private/get-accounts`
- `private/get-open-orders`
- `private/get-order-detail`
- user WebSocket channels for balances or orders

This would require:
- API key
- secret key
- signature generation
- stronger permission handling

This is already more sensitive than public market data, even if no order is placed.

### Stage 3 - Trading Endpoints
If Nova ever progresses to approval-gated live trading, the relevant endpoints would be:
- `private/create-order`
- `private/amend-order`
- `private/cancel-order`
- `private/cancel-all-orders`
- advanced order endpoints if ever needed later

These should not be part of the first version.

### Endpoints To Avoid Early
Do not start with:
- withdrawals
- deposit address generation
- fiat withdrawal endpoints
- leverage/margin/derivatives controls
- staking conversions

These dramatically increase risk and complexity.

## What It Would Cost

## API Access Cost
Based on the official Crypto.com Exchange docs and help center:
- I did not find a published separate subscription fee for using the Exchange API itself
- the help center article documents limits and key management, not API subscription pricing
- the public market data endpoints appear intended for normal Exchange API access

The safest wording is:
- no separate API subscription fee was found in the official docs reviewed today
- but this is an inference from the documentation, not a guaranteed pricing commitment

### Official Limits Found
Crypto.com's help center says:
- hard limit: `10 calls per URL per second`
- market API limits are enforced per IP address
- user API limits are enforced per account

### Trading Costs
Even if API access itself has no separate subscription fee, live trading is not free.

Real live-trading costs would include:
- maker/taker exchange fees
- spread/slippage
- possible network or blockchain costs depending on transfers
- operational costs on your side:
  - monitoring
  - logging
  - hosting
  - secret management

Crypto.com's U.S. Exchange Terms say fees and costs may apply to use of the Exchange.
The Crypto.com VIP Programme article currently lists example spot fees such as:
- VIP 1 maker fee: `0.0650%`
- VIP 1 taker fee: `0.1000%`

Those are not universal forever rates.
They can vary by tier, product, and time, so any live trading design should re-check the official current fee schedule before implementation.

## Legal And Compliance Considerations

## Important Note
This section is not legal advice.

It is a practical product/legal-awareness note based on official sources reviewed today.
If Nova ever moves beyond read-only market data into live trading, especially anything automated, you should get professional legal and tax advice.

### 1. Exchange Terms And Jurisdiction Matter
Crypto.com's U.S. Exchange Terms say:
- you must read and accept the terms
- disputes may be subject to arbitration
- Crypto.com is not acting as your financial adviser
- you should consult your own professional advisers before entering transactions
- the Exchange is only available in "Available Jurisdictions"
- the U.S. terms define available jurisdictions as eligible U.S. jurisdictions, excluding New York

That means:
- availability depends on where you are
- your account jurisdiction matters
- terms and restrictions are part of the real design boundary

### 2. Identity Verification / KYC
The official terms and help materials show that:
- Crypto.com performs identity verification
- you may be asked to provide updated information
- private API use requires account-level setup
- trading/withdrawal permissions are more sensitive than read-only access

So any private API roadmap assumes:
- verified account
- stable jurisdiction eligibility
- secure key handling

### 3. Taxes
For a U.S. user, crypto tax reporting is a major real-world requirement.

The IRS says:
- digital assets are treated as property for U.S. tax purposes
- income from digital assets is taxable
- you may have to report transactions on your tax return
- brokers are rolling into newer reporting forms such as Form 1099-DA

That means even a well-governed trading system still creates:
- taxable events
- basis tracking needs
- gain/loss reporting responsibilities

### 4. If You Ever Trade For Others, The Legal Risk Changes A Lot
If Nova is only helping you trade your own account, that is one thing.

If you ever move toward:
- trading for other people
- taking discretion over other people's money
- offering auto-trading as a service
- selling algorithmic signals tied to auto execution

then the legal picture changes materially.

SEC materials on robo-advisers explain that robo-advisers are typically registered investment advisers and are subject to substantive and fiduciary obligations under the Advisers Act.

That means:
- "my own account" is very different from
- "a product or service that trades or advises for others"

### 5. Money Transmission / Custody Risk
FinCEN guidance makes clear that accepting and transmitting convertible virtual currency on behalf of others can trigger money transmitter issues.

That is another major reason not to blur:
- personal-use tooling
with
- handling or moving value for other people

### 6. Derivatives / Leverage Need Extra Caution
The CFTC treats virtual currencies as commodities and has separate concerns around derivatives and leveraged trading.

So if Nova ever expands into:
- leverage
- margin
- perpetuals
- derivatives

that should be treated as a much higher-risk legal and product step than simple spot trading.

## Best Safe Product Shape

### Stage 1 - Crypto Read-Only Assistant
Nova can:
- show prices
- summarize market moves
- maintain a watchlist
- create crypto brief summaries
- answer questions about tickers using public data plus source-grounded reasoning

Nova cannot:
- trade
- move money
- access wallet funds

### Stage 2 - Paper Trading / Simulation
Nova can:
- simulate trades
- log hypothetical entries/exits
- show P/L
- compare strategies

Nova still cannot:
- place real orders

This is the best place to test whether Nova's market logic is actually useful.

### Stage 3 - Approval-Gated Live Trading
Only after simulation and careful testing:
- Nova may prepare an order
- Nova explains why
- you approve each order

Strong limits should include:
- no withdrawals
- no leverage at first
- no margin at first
- approved asset list only
- position size caps
- daily loss caps
- full audit log
- kill switch

### Stage 4 - Semi-Automatic Rules
Only later:
- user-defined rules
- explicit order caps
- emergency stop
- visible logs
- approval of the rule set before activation

### Stage 5 - Fully Autonomous Live Trading
This should be the last step, if it happens at all.

And if it ever happens, it should require:
- strong evals and backtesting
- live paper-to-real validation
- strict position and risk controls
- immediate stop controls
- highly reviewable traces
- likely legal review

## Phase Placement Map

### Current Product Track
These belong in the current product lane:
- public Crypto.com market data
- crypto price lookups
- crypto watchlists
- crypto alerts
- crypto news/research grounded in public data
- paper-trading design and simulation planning

These are the useful low-risk steps.

### Phase 7 - Governed External Reasoning
These belong in Phase 7:
- stronger crypto market synthesis
- second-opinion review of crypto research
- deeper cross-source market/news reasoning

Why:
- this is reasoning quality
- still text-first
- no trading authority added

### Phase 8 - Governed Execution
These belong in Phase 8:
- any private account API use
- approval-gated live order placement
- any order amendment/cancel flows
- action-capable crypto automations
- any app or connector actions that affect real funds

Important boundary:
- no withdrawals in the early trading lane
- no leverage or derivatives in the early trading lane
- no silent order placement

### Phase 9 - Node / Cross-Client Coherence
These belong in Phase 9:
- shared watchlists across devices
- consistent crypto task/alert visibility across clients
- portfolio context coherence across Nova surfaces

### Phase 10 And Later
Only much later should Nova even consider:
- adaptive strategy tuning
- learned trade preferences
- self-adjusting strategy behavior
- autonomous live trading with reduced per-trade approval

This should happen only with:
- auditability
- rollback
- strict risk controls
- explicit user opt-in
- serious legal and tax review

## Best APIs By Stage

### Best First API Set
- Crypto.com Exchange API v1 public REST + WebSocket market data

### Best Second API Set
- private read-only balance and order-state endpoints

### Best Third API Set
- private order placement/cancel endpoints under manual approval

### APIs To Leave Out Early
- withdrawal APIs
- deposit-address APIs
- staking conversion APIs
- fiat withdrawal APIs
- margin/leverage controls

## Best Product Rule
The anchor rule for crypto support should be:

Read market data first, simulate second, require approval for real orders, and treat true auto trading as a much-later high-risk feature.

## Official Sources Reviewed
- [Crypto.com Help Center: API](https://help.crypto.com/en/articles/3511424-api)
- [Crypto.com Exchange API v1 docs](https://exchange-docs.crypto.com/exchange/v1/rest-ws/index.html)
- [Crypto.com U.S. Exchange Terms & Conditions](https://static2.crypto.com/exchange/assets/documents/us-tnc.pdf)
- [Crypto.com Exchange VIP Programme](https://help.crypto.com/en/articles/4756522-what-is-the-crypto-com-exchange-vip-programme)
- [IRS Digital Assets](https://www.irs.gov/filing/digital-assets)
- [IRS FAQs on virtual currency transactions](https://www.irs.gov/individuals/international-taxpayers/frequently-asked-questions-on-virtual-currency-transactions)
- [SEC All About Auto-Trading](https://www.sec.gov/about/reports-publications/investorpubsautotradinghtm)
- [SEC robo-adviser guidance release](https://www.sec.gov/newsroom/press-releases/2017-52)
- [SEC robo-adviser guidance update PDF](https://www.sec.gov/investment/im-guidance-2017-02.pdf)
- [FinCEN virtual currency guidance](https://www.fincen.gov/resources/statutes-regulations/guidance/application-fincens-regulations-persons-administering)
- [CFTC customer advisory on virtual currency trading risk](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/understand_risks_of_virtual_currency.html)
