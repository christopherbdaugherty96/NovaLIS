# Governed Crypto And Trading Guide
Updated: 2026-03-21
Status: Human guide

## What This Guide Is
This is the plain-language guide to how crypto support should work in Nova.

It explains:
- what Nova could safely do with Crypto.com
- what it should not do early
- what APIs would be needed
- what costs to expect
- what legal and tax issues matter

This is not legal advice and not financial advice.
It is a practical planning guide.

## Short Answer
Yes, Nova could eventually support Crypto.com.

Yes, Nova could even support auto trading in the future.

But the best and safest roadmap is:
1. market data first
2. watchlists and alerts
3. paper trading
4. approval-gated real orders
5. only much later, maybe limited auto trading

That is the right shape if you want Nova to be:
- useful
- robust
- safe

## What Nova Should Do First
The first good version is:
- show crypto prices
- show market snapshots
- answer crypto questions
- summarize crypto news with sources
- maintain watchlists
- maybe send alerts later

This version should use public market data only.

That means:
- no account access
- no wallet access
- no placing trades
- no moving money

## Which Crypto.com APIs Matter

### Public Market Data
For the safe first version, the useful Crypto.com Exchange API pieces are the public market-data endpoints:
- `public/get-tickers`
- `public/get-book`
- `public/get-candlestick`
- `public/get-trades`

And later, public WebSocket feeds for live updates.

This is enough for:
- prices
- order-book snapshots
- recent trades
- candles and charts

### Private Account APIs
Later, if you want account-aware features, Nova would need private APIs such as:
- balances
- open orders
- order details

These require:
- an API key
- a secret key
- request signing

This is already a more sensitive step.

### Trading APIs
If Nova ever places real trades, it would need private order endpoints such as:
- create order
- cancel order
- amend order

This should not be first.

## What It Costs

## API Cost
Based on the official docs reviewed:
- I did not find a separate public price for simply using the Crypto.com Exchange API
- the docs describe limits and authentication, not a separate API subscription fee

So the safest answer is:
- no separate API subscription fee was found in the official docs reviewed today
- but that could change, so it should be checked again before implementation

### Rate Limits
Crypto.com's help center says:
- hard limit: `10 calls per URL per second`
- market API limits are enforced per IP
- user API limits are enforced per account

### Real Trading Costs
If Nova ever trades live, the important costs are not just API access.

They are:
- exchange trading fees
- spread/slippage
- possible network or transfer costs
- your own infrastructure and monitoring costs

Crypto.com's official materials show:
- fees and costs may apply to Exchange use
- example spot fees in the VIP programme currently start around:
  - `0.0650%` maker
  - `0.1000%` taker

Those are not guaranteed permanent rates.
They can vary by tier and product.

## Legal And Tax Reality

## For Your Own Account
If Nova is only helping **you** with **your own** account:
- that is the lowest-risk legal version
- but it still involves taxes, exchange terms, and trading risk

Crypto.com's U.S. terms say:
- they are not your financial adviser
- you should get your own professional advice
- account use depends on available jurisdictions
- identity verification is part of the service

## Taxes
The IRS says:
- digital assets are treated as property for U.S. tax purposes
- income from digital assets is taxable
- gains and losses may need to be reported

So if Nova ever helps place real trades, you should expect:
- taxable events
- recordkeeping needs
- basis/gain/loss tracking

## If You Ever Use It For Other People
This is where legal risk jumps.

If Nova ever:
- trades for someone else
- manages someone else’s money
- offers auto trading as a service
- gives algorithmic discretionary trading to other users

then the legal picture gets much more serious.

SEC materials explain that robo-advisers are typically registered investment advisers and are subject to adviser obligations.

FinCEN guidance also shows that handling or transmitting virtual currency for others can trigger money-transmitter issues.

So:
- personal-use assistant for your own account = one category
- product/service trading for others = a much harder category

## What Nova Should Not Do Early
Nova should not start with:
- withdrawals
- wallet transfers
- leverage
- margin
- perpetuals or derivatives
- hidden trade execution
- full autonomous live trading

These add too much risk too early.

## Best Roadmap

### Stage 1
- public crypto market data
- crypto Q&A
- crypto watchlists
- crypto summaries

### Stage 2
- paper trading
- simulation
- strategy comparison

### Stage 3
- approval-gated live orders
- small caps and limits
- no withdrawals

### Stage 4
- tightly bounded semi-auto rules
- kill switch
- daily loss limits
- position limits

### Stage 5
- true auto trading only much later, maybe never

## Best Safety Rules
If Nova ever reaches live trading, it should have:
- approved asset list only
- position size caps
- daily loss caps
- full audit log
- clear reason before each order
- manual override
- emergency stop
- no withdrawals in the early live-trading phase

## Where This Belongs In Nova
- Now:
  - public market data
  - crypto summaries
  - watchlists
- Later:
  - paper trading
  - account-aware views
- Phase 8:
  - private API account access
  - live order placement with approval
- Much later:
  - any real auto trading

## Bottom Line
Nova **can** support Crypto.com in the future.

The best version is not:
- "Let Nova trade freely right away."

The best version is:
- public market data first
- paper trading second
- approval-gated real trading later
- full auto trading only if you still want it after strong safeguards, testing, tax handling, and legal review

## Official Sources
- [Crypto.com Help Center: API](https://help.crypto.com/en/articles/3511424-api)
- [Crypto.com Exchange API v1 docs](https://exchange-docs.crypto.com/exchange/v1/rest-ws/index.html)
- [Crypto.com U.S. Exchange Terms & Conditions](https://static2.crypto.com/exchange/assets/documents/us-tnc.pdf)
- [Crypto.com Exchange VIP Programme](https://help.crypto.com/en/articles/4756522-what-is-the-crypto-com-exchange-vip-programme)
- [IRS Digital Assets](https://www.irs.gov/filing/digital-assets)
- [SEC All About Auto-Trading](https://www.sec.gov/about/reports-publications/investorpubsautotradinghtm)
- [FinCEN virtual currency guidance](https://www.fincen.gov/resources/statutes-regulations/guidance/application-fincens-regulations-persons-administering)
