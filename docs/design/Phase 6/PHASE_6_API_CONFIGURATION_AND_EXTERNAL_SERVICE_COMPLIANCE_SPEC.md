# Phase 6 API Configuration and External Service Compliance Specification
Date: 2026-03-13
Status: Productization planning note only; not runtime truth
Scope: API handling, configuration, attribution, and service-compliance posture for Nova as downloadable software

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

### 3. Rate-limit planning
If Nova ships to many users, some third-party services may rate limit shared credentials.

The cleanest early answer is:
- user-provided API keys where needed

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

## Logging and Privacy Rule
Nova's docs should clearly explain:
- what API-bound requests leave the device
- what stays local
- what is logged to the ledger
- where logs are stored

## Model Licensing Rule
For local models:
- verify redistribution rights
- verify commercial-use rights
- decide whether Nova ships models directly or requires user-side download

## Product Positioning Rule
Nova should not blur:
- local intelligence
- third-party API use

If a feature uses an outside service, Nova should say so plainly.

## Relationship to Architecture
Nova's NetworkMediator makes this easier because external calls are already centralized.

That means app-readiness work should focus on:
- config
- compliance review
- disclosure

not on rebuilding the API layer itself.

## Bottom Line
Turning Nova into an app should not require a major API redesign.

The important work is:
- key handling
- terms compliance
- rate-limit readiness
- attribution
- clear network disclosure
