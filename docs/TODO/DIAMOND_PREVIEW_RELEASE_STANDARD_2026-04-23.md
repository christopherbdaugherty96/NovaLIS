# Diamond Preview Release Standard (2026-04-23)

## Purpose
Nova should not feel merely functional. It should feel premium, stable, clear, and intentionally designed.

This document defines the release bar for any dashboard or public-facing preview before it is considered showcase-ready.

## Diamond Standard
A preview is ready when it meets all four layers:

1. Reliable
- no blocking errors
- core flows complete successfully
- user actions produce expected responses
- recoverable failure states

2. Coherent
- responses attach to the correct turn
- no duplicate or ghost messages
- visible state matches real state
- navigation feels understandable

3. Polished
- spacing, labels, and hierarchy feel deliberate
- loading states are calm and clear
- transitions feel smooth
- no obvious rough edges in first-use paths

4. Valuable
- a first-time user quickly understands what Nova is for
- at least one meaningful task feels easier with Nova than without it
- trust and capability are visible without reading documentation

## First Impression Paths
The following flows should always feel strong:
- first launch
- open chat
- ask a basic question
- discover capabilities
- complete one practical action
- recover from one small mistake

## Release Gate Questions
Before shipping a preview, ask:
- Would a normal user understand this in under two minutes?
- Would the experience feel stable enough to trust?
- Would someone want to show another person?
- Is there any obvious friction we already know about?

If any answer is no, the preview is not yet diamond-ready.

## Philosophy
Functional is not enough.
Premium trust is part of the product.
