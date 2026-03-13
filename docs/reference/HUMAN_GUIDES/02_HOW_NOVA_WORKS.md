# How Nova Works
Updated: 2026-03-13

## The Simple Model
Nova has three big layers:
- experience
- intelligence
- governed action

### 1. Experience layer
This is the part you see and interact with.
It includes:
- the dashboard
- the orb
- chat responses
- voice input and voice output
- thread views and widgets

This layer is about interaction and presentation.
It is not supposed to hold authority by itself.

### 2. Intelligence layer
This is the part that analyzes, compares, summarizes, and explains.
It includes:
- research and reporting
- verification
- screen analysis
- explain-anything routing
- analysis documents
- thread reasoning

This layer is where Nova "thinks," but that does not mean it gets to act freely.

### 3. Governed action layer
This is the part that handles any real execution.
It includes things like:
- opening a website
- changing volume
- changing brightness
- opening a file or folder
- saving governed memory

The key rule is that real actions do not come directly from the intelligence layer.
They go through a governance path first.

## Why That Matters
Nova is built on a very important idea:
- intelligence and authority are not the same thing

That means Nova can become better at:
- reasoning
- summarizing
- comparing
- understanding context
- helping with projects

without automatically becoming more powerful in what it is allowed to do.

## What Happens When You Ask Nova For Something
At a human level, a Nova request usually goes one of three ways.

### Path A: explanation only
Example:
- `Nova, explain this page.`

Nova will:
- gather request-time context
- analyze the current screen or page
- return an explanation

No real-world action is needed.

### Path B: governed action
Example:
- `Nova, open source 2.`
- `Nova, set brightness to 65.`

Nova will:
- interpret the request
- route it into the governed action path
- check whether the capability is enabled and allowed
- execute inside the boundary
- log the result

### Path C: continuity or memory
Example:
- `Nova, continue my deployment issue.`
- `Nova, memory list thread deployment issue.`

Nova will:
- retrieve current thread context or governed memory
- explain where the work stands
- show blocker, status, decisions, or saved memory

## The Dashboard's Role
The dashboard is where Nova starts to feel like a workspace rather than a simple chat window.

It can show:
- weather, news, calendar, and system snapshots
- thread map and thread detail
- memory counts and linked history
- system status and model readiness
- follow-up actions

The dashboard should make Nova easier to understand, not more autonomous.

## The Orb's Role
The orb is meant to provide calm presence.
It is not meant to secretly signal hidden reasoning state, execution readiness, or system authority.

## The Most Important High-Level Truth
Nova is designed so that deeper intelligence does not automatically become deeper authority.

That separation is one of the most important things about the whole project.
