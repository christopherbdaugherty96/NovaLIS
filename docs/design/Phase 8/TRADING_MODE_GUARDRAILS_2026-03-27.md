# Trading Mode Guardrails
Date: 2026-03-27
Status: Required guardrails before any live trading mode

## Purpose
This document defines the minimum safety and governance boundaries required before Nova or OpenClaw should be allowed to interact with markets, broker APIs, or automated buy/sell execution.

## Core Position
Nova may support market research earlier than live trading.

That means:
- analysis can come first
- paper trading can come second
- live trading must come last

The model should begin as:
- analyst
- explainer
- scenario comparer
- order-preparer

It should not begin as:
- unchecked order executor
- hidden day-trading bot
- autonomous capital allocator

## Recommended Phase Order
### Phase A — Research only
Allowed:
- summarize market data
- compare scenarios
- review strategies
- explain signals

Not allowed:
- send live orders
- modify live broker state

### Phase B — Paper trading
Allowed:
- create simulated orders
- track simulated fills
- evaluate P&L
- compare strategy outcomes

Still not allowed:
- live capital deployment

### Phase C — Approval-gated live trading
Allowed only with:
- explicit user approval
- hard risk limits
- full audit visibility

### Phase D — Narrow auto-execution
Only after:
- paper track record
- bounded strategy scope
- deterministic risk engine
- visible kill switch
- explicit operator review

## Non-Negotiable Guardrails
1. Model output is not enough to place a live trade.
2. A deterministic risk layer must validate every order.
3. Position size limits must be enforced outside the model.
4. Max loss / max drawdown rules must be enforced outside the model.
5. Symbol allowlists must be explicit.
6. Market hours rules must be explicit.
7. Every order decision must be auditable.
8. There must be an immediate kill switch.

## Required Deterministic Risk Checks
Before any live order:
- market open check
- symbol allowlist check
- max order size check
- max daily loss check
- max open positions check
- duplicate order suppression
- cooldown window check
- account connectivity check

These checks must be deterministic and non-LLM.

## Human Approval Requirements
Before any early live mode:
- show symbol
- show side
- show size
- show reason
- show stop and target if present
- show estimated risk
- require explicit approval

## OpenAI-Specific Warning
OpenAI can be useful for:
- research synthesis
- narrative market summaries
- coding trading infrastructure
- reviewing logs and failures

OpenAI should not be the first live execution authority.

Why:
- model variance
- prompt sensitivity
- external market risk
- higher-stakes failure modes

## Recommended Current Product Shape
Near term, Nova should support:
- market research
- strategy explanation
- structured paper-trade planning
- order-preview generation

Nova should defer:
- fully autonomous live buying and selling

## Logging and Visibility
If trading mode ever becomes real, Nova must log:
- trigger source
- model/provider involved
- prompt class
- final structured recommendation
- deterministic validation results
- approval state
- order payload
- broker response
- cancellation or failure reason

## What This Document Blocks Today
This document blocks:
- silent live auto-trading
- invisible order placement
- model-only risk control
- background money movement without operator visibility

## Safe Near-Term Path
1. build research mode
2. build paper trading mode
3. build deterministic risk engine
4. add approval-gated live preview
5. only then consider narrow auto-execution
