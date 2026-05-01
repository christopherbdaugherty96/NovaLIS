# Phase 6 API Configuration and External Service Compliance Specification
Date: 2026-03-13
Status: Productization planning note only; not runtime truth
Scope: API handling, configuration, attribution, cost posture, and service-compliance posture for Nova as downloadable software

## Purpose
This document explains what changes when Nova becomes an app with respect to APIs and external services.

## Core Recommendation
Nova does not need a large API rewrite just to become a desktop app.

The current architecture already fits app packaging:
- UI
- local FastAPI backend
- Governor
- NetworkMediator
- executors

The main changes are operational, not architectural.

## Free-First API Rule
Nova should default to free, open-source, local-first, or user-owned API paths before paid, metered, or vendor-locking services.

This rule applies to:
- Google integrations
- external AI providers
- search providers
- commerce providers
- hosting and storage providers
- maps, location, and analytics providers
- any service that may require billing setup, credits, quota, or paid plans

Every external service should be classified before it is recommended or implemented:
- `free`: no payment method or billing exposure required for intended use
- `free_tier`: free within quotas, credits, billing setup, or rate limits
- `paid`: requires payment, paid plan, credits, or metered billing for intended use
- `unknown_cost`: cost posture has not been verified yet

Design rules:
- Recommend the `free` or local-first path first.
- Treat `free_tier` as usable but visibly flagged.
- Treat `paid` as non-default and requiring explicit user awareness before recommendation.
- Treat `unknown_cost` as blocked from being presented as the preferred path until verified.
- Do not silently replace a free/local path with a paid/cloud path because it is easier to implement.

## What Should Stay the Same
Nova should keep:
- FastAPI routes
- websocket flow
- Governor mediation
- executor structure
- capability registry
- NetworkMediator as the single network-control layer

This is one of Nova's structural advantages.

## What Should Change

### 1. API key handling
Do not ship private keys inside the app.

Instead use:
- user config
- secure local storage where appropriate
- explicit settings fields for user-provided keys

### 2. Network visibility
Nova should disclose:
- which features contact third-party services
- which requests stay local
- which APIs require user-supplied credentials
- which APIs have free-tier, paid, credit-based, or unknown cost posture

### 3. Rate-limit and cost-limit planning
If Nova ships to many users, some third-party services may rate limit shared credentials or introduce billing risk.

The cleanest early answer is:
- user-provided API keys where needed
- visible cost posture before setup
- no bundled paid-provider dependency unless it is explicitly approved

### 4. Attribution handling
If an external service requires attribution, Nova should surface it in:
- settings
- docs
- relevant UI surfaces when appropriate

## Compliance Rules
For every third-party service Nova uses:
- review the service terms
- check whether redistribution is allowed
- check whether reselling is restricted
- check attribution requirements
- check whether local caching or summarization is permitted
- verify whether payment, credits, billing setup, or free-tier quotas apply
- classify the service cost posture as `free`, `free_tier`, `paid`, or `unknown_cost`

## Logging and Privacy Rule
Nova's docs should clearly explain:
- what API-bound requests leave the device
- what stays local
- what is logged to the ledger
- where logs are stored
- whether the action used a free, free-tier, paid, or unknown-cost provider

## Model Licensing Rule
For local models:
- verify redistribution rights
- verify commercial-use rights
- decide whether Nova ships models directly or requires user-side download

## Product Positioning Rule
Nova should not blur:
- local intelligence
- third-party API use
- free execution
- free-tier or paid execution

If a feature uses an outside service, Nova should say so plainly.
If a feature may create billing or quota risk, Nova should say so before positioning it as the preferred path.

## Relationship to Architecture
Nova's NetworkMediator makes this easier because external calls are already centralized.

That means app-readiness work should focus on:
- config
- compliance review
- disclosure
- cost posture classification

not on rebuilding the API layer itself.

Future runtime implementation should route cost posture through:
- capability metadata
- Governor-visible action review
- trust-review UI surfaces
- ledger-visible audit events where appropriate

## Bottom Line
Turning Nova into an app should not require a major API redesign.

The important work is:
- key handling
- terms compliance
- rate-limit readiness
- attribution
- clear network disclosure
- free-first cost posture enforcement before paid-provider expansion
