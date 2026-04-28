# Nova Task / Run-State Plan

Date: 2026-04-27

Status: Future architecture plan / not current runtime truth

Purpose: define a durable task/run-state layer for Nova so long work can pause, resume, recover, and hand off cleanly without granting authority.

---

## Active Priority Note

This is future planning only. Do not implement before the current RequestUnderstanding trust/action-history priority unless explicitly reprioritized.

---

## Executive Summary

Nova needs a run-state system because the owner frequently works across Claude, Codex, GitHub, OpenClaw, and local repo sessions where tokens or time run out.

Core rule:

> **Run state is evidence and continuity, not permission.**

---

## Problems This Solves

```text
Claude ran out of tokens
Codex stopped mid-task
OpenClaw run paused or failed
repo work continued across branches
unclear what changed
unclear what tests ran
unclear what should happen next
paused work accidentally resumes
```

---

## Suggested Run Record Fields

```text
run_id
user_goal
active_priority_snapshot
status: active / paused / blocked / complete / failed / cancelled
actor: user / Claude / Codex / Nova / OpenClaw / connector
started_at
updated_at
ended_at
files_read
files_changed
commands_run
tests_run
commits_created
branches_touched
external_systems_touched
receipts_created
blockers
next_recommended_step
do_not_touch
handoff_summary
```

---

## Recommended Workflows

```text
Token Recovery / Session Continuity Brief
Project Foreman Brief
repo audit progress tracker
capability signoff session recorder
OpenClaw run handoff
background project status review
Claude/Codex next-prompt builder
```

---

## State Rules

```text
A resumed task must re-check the current priority override.
A stale run cannot override newer owner direction.
Paused scopes remain paused unless explicitly unpaused.
A run checkpoint cannot approve actions.
A completed run should produce a summary and receipts/non-action statements.
```

---

## Handoff Output

Every long run should be able to produce:

```text
what was requested
what was completed
what files changed
what tests ran
what commits landed
what was blocked
what remains uncertain
what should happen next
what should not be touched
```

---

## Guardrails

```text
Do not store secrets in run state.
Use summaries/hashes for sensitive content.
Do not treat run state as proof of live capability signoff unless signoff criteria are met.
Do not auto-resume actions that require approval.
```

---

## Build Order

```text
1. Define run-state schema.
2. Add read-only run-state/handoff record model.
3. Add manual run summary generator.
4. Connect to trust/action-history view.
5. Add OpenClaw run integration later.
6. Add background reasoning status only after background plan is ready.
```

---

## Final Rule

> **Nova should remember where work stopped without pretending that memory gives it permission to continue acting.**
