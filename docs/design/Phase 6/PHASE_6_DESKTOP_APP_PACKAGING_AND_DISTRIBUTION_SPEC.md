# Phase 6 Desktop App Packaging and Distribution Specification
Date: 2026-03-13
Status: Productization planning note only; not runtime truth
Scope: Recommended packaging and first-distribution path for Nova as local desktop software

## Purpose
This document explains how Nova should be packaged and distributed once the product surfaces and delegated-policy foundations are mature enough for early launch.

## Core Recommendation
Recommended first shipping model:
- local desktop app

Why this fits Nova:
- Nova is already architected as a local runtime
- FastAPI + websocket + Governor is already app-friendly
- local deployment preserves Nova's privacy-first story
- it avoids forcing Nova into a cloud-first identity too early

## Current Architecture Fit
Nova already behaves like many modern desktop apps:

UI
-> local FastAPI backend
-> Governor
-> executors / capabilities
-> external APIs and local models

That means turning Nova into an app is mainly:
- packaging work
- launcher work
- installability work

not a rewrite of the backend architecture

## Packaging Options

### Option A - Desktop shell around the current local backend
Examples:
- Tauri
- Electron

Recommended use:
- primary end-of-Phase-6 packaging path

Why:
- keeps the current backend intact
- gives Nova a real app window
- makes updates and settings easier later

### Option B - Python desktop packaging
Examples:
- PyInstaller
- Briefcase

Recommended use:
- early alpha packaging or fallback packaging path

Why:
- simple path to an executable
- useful for early adopters

Tradeoff:
- less elegant UI shell and product feel

### Option C - Docker for developer users
Example:
- `docker run ...`

Recommended use:
- technical early adopters only

Tradeoff:
- too technical for mainstream users

## Recommended Packaging Order
1. keep the existing backend runtime intact
2. add a launcher that starts the backend automatically
3. load the dashboard in a desktop window
4. move config and user-data paths into stable app locations
5. add installer and first-run checks

## Expected App Structure
Recommended high-level structure:

Nova/
  app/
  config/
  user_data/
  models/
  logs/

Updates should primarily replace:
- `app/`

Updates should avoid wiping:
- `config/`
- `user_data/`
- `models/`
- `logs/`

## First Distribution Channels
Recommended first channels:
- GitHub Releases
- direct download website
- technical early-adopter communities

Examples of release assets:
- Windows installer
- macOS installer or bundle
- Linux AppImage or package

## Website Role
Once Nova is packaged, the product should also have a simple website with:
- homepage
- download
- features
- docs
- privacy
- terms
- security contact

## Early Launch Audience
Start with:
- developers
- local-AI enthusiasts
- people who already understand installing technical tools

This avoids overselling Nova before installability and onboarding are mature.

## Non-Goals
This packaging path is not:
- a requirement to move Nova into SaaS
- a reason to replace the current backend
- a justification for weakening local governance or privacy boundaries

## Bottom Line
Nova's first credible product form is:
- a local desktop app with the current backend architecture preserved

That is the shortest route from:
- developer runtime

to:
- real installable software
