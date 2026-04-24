# OpenClaw Setup and Runtime Guide
Updated: 2026-04-23
Status: Plain-language OpenClaw guide

## Purpose
This guide explains how OpenClaw is used inside Nova today.

## Simple Mental Model
- Nova is the user-facing system
- OpenClaw is a worker layer used inside Nova
- Governance rules still decide what may run

## Current Scope
OpenClaw surfaces may support research, summaries, project analysis, and narrow operator flows.

Important safety clarification:
Even where newer runtime phases mention chaining, recovery, or goal-based task flows, those features remain bounded by capability checks, approvals, routing rules, and visible controls. They should not be understood as unrestricted autonomy.

## What Is Live Today
- governed remote bridge for approved read/reasoning tasks
- local agent surfaces for briefings and narrow scheduled flows
- read-focused project analysis lanes
- local-first operation with optional metered fallback paths where configured

## What Is Not Live
- unrestricted autonomous execution
n- silent background authority expansion
- broad local mutation without approvals
- hidden operator behavior

## Runtime Truth First
For exact live state, use generated runtime docs in `docs/current_runtime/`.
