# Safety and Trust
Updated: 2026-05-03

## Why Nova Talks About Safety So Much
Nova is not trying to be a reckless action agent.

A lot of AI systems become dangerous or confusing because they blur these things together:
- reasoning
- intention
- authority
- execution

Nova is built to separate them.

That separation is part of why the project can support real capabilities without becoming chaotic.

## The Core Rule
The easiest way to understand Nova's safety model is this:

`Intelligence may expand. Authority may not expand without explicit unlock.`

In plain language, that means:
- Nova can become better at understanding, summarizing, comparing, and helping
- but it does not automatically gain more power to act just because it became smarter

## What Nova Is Supposed To Do
Nova is supposed to:
- explain
- summarize
- guide
- inspect
- preserve context when asked
- execute allowed actions only through a governed path

## What Nova Is Not Supposed To Do
Nova is not supposed to:
- start acting on its own
- run hidden background task loops
- silently monitor the screen
- silently save long-term memory
- bypass the governed action path
- let presentation or personality become authority

## Why The Governor Matters
The Governor is the part of Nova that stands between a request and a real action.

In normal language, its job is to make sure that:
- the requested capability is allowed
- the action is bounded
- the action passes through the expected path
- the result is logged

That helps keep the system inspectable.

## Why Screen Features Still Fit This Model
Screen capture and explain-anything can sound powerful, so it is important to describe them clearly.

Nova's perception features are meant to be:
- request-time only
- read-only unless a separate explicit action is requested
- bounded to the visible context relevant to the request

That is very different from a system that quietly watches the computer all day.

## Why Memory Still Fits This Model
Memory is also intentionally explicit.

Nova's governed memory is not meant to work like a hidden always-learning profile.
Instead, it is supposed to work more like:
- an explicit filing system
- a preserved project record
- a durable decision history under user control

## Trust Comes From Legibility
A big theme in Nova is that trust should come from legibility.
That means users should be able to understand:
- what Nova can do
- what Nova is doing
- why it recommended something
- what it saved
- what it did not do

Nova is strongest when it feels clear, calm, and inspectable rather than mysterious.
