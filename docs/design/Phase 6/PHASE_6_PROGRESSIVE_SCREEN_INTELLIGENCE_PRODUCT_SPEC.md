# Phase-6 Progressive Screen Intelligence Product Spec
Date: 2026-03-13
Status: Planning spec only; not fully implemented in runtime
Scope: Signature product-direction spec for Nova's "what is this?" interaction

## Purpose
This document defines the product shape for Nova's most intuitive everyday question:

`Nova, what is this?`

The goal is to make that question a fast, privacy-respecting, invocation-bound interaction that feels magical without violating Nova's governance model.

## Core Product Principle
Nova should start small and expand context only if needed.

That means the default interaction is not:
- capture everything immediately
- analyze the whole page first
- read more than the user likely intended

It is:
- analyze the thing under or near the user's cursor first
- expand to the local section if needed
- expand to the full page only when local context is not enough

## Why This Matters
This interaction removes the biggest friction that weakens everyday AI usage:
- no copy/paste
- no manual screenshot upload
- no long context setup

The user simply points and asks.

## Default User Question
The canonical form is:
- `Nova what is this?`

Equivalent follow-ups may include:
- `Nova explain this`
- `Nova what am I looking at?`
- `Nova what does this mean?`

Nova should assume the user means the object under the cursor unless a later context expansion is required.

## Progressive Context Model

### Level 1 - Cursor Context
Default behavior:
- capture a small region around the cursor
- approximately button / paragraph / error-message / field scale
- run OCR, element recognition, and lightweight reasoning

This level should solve most real questions:
- buttons
- errors
- labels
- fields
- small chart areas
- paragraphs
- code snippets

### Level 2 - Local Section Context
If cursor context is insufficient, Nova expands to the surrounding section.

Examples:
- a table region
- a grouped settings panel
- a chart plus its legend
- a grouped form area
- a DOM section when available

At this level Nova should answer questions like:
- what this table is comparing
- what this chart section means
- what this panel controls

### Level 3 - Full Page Context
If the local section is still ambiguous, Nova expands to full page or full document context.

This may include:
- page title
- headings
- surrounding sections
- structural metadata
- visible document hierarchy

This level should be used only when narrower context is not enough.

## Interaction Flow
```text
User: "Nova what is this?"
    ->
Governor authorizes read-only screen analysis
    ->
Level 1: cursor region capture and analysis
    ->
if sufficient: respond
else Level 2: local section analysis
    ->
if sufficient: respond
else Level 3: full page understanding
    ->
respond
```

## Follow-Up Expansion
After the initial answer, Nova may support explicit follow-ups such as:
- `Nova explain more`
- `Nova summarize this page`
- `Nova analyze this document`

Those follow-ups should be treated as fresh explicit requests to widen scope.

## Why This Fits Nova
Nova already has the right safety shape:
- invocation-bound screen capture
- Governor mediation
- read-only analysis
- ledger logging
- no background monitoring

This makes progressive screen intelligence a strong product track without creating a second authority path.

## High-Value Use Cases
This interaction should work well on:
- webpages
- PDFs
- spreadsheets
- contracts
- software UI
- error messages
- charts
- code

## Signature Demo Examples

### Error message
User:
- `Nova what is this?`

Nova:
- `This error means Python cannot find the module 'requests'.`

### Contract clause
User:
- `Nova what does this paragraph mean?`

Nova:
- `This clause allows termination with 30 days notice.`

### Scam detection
User:
- `Nova what is this?`

Nova:
- `This appears to be a phishing attempt. Do not click this link.`

## Relationship to Existing Runtime
The current runtime already has:
- screenshot capture
- screen analysis
- explain-anything routing

This spec describes the next product-quality evolution of those surfaces:
- cursor-first
- progressively expanding
- optimized for the question "what is this?"

## Product Importance
This should be treated as one of Nova's highest-value sellability surfaces because:
- users understand it immediately
- it works across many real computer confusion moments
- it demonstrates Nova's privacy-first differentiator clearly

## Non-Goals
This spec does not authorize:
- background watching
- always-on interpretation of screen content
- autonomous action from screen understanding
- full-page capture by default

## Interpretation Rule
This is a product-direction spec for the Phase-6 era.

It is a high-value adjacent track, not the constitutional core delegated-policy substrate.
