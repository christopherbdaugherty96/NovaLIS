# Weekly Engineering Summary

This folder mirrors the active local Codex automation:
- local runtime path: `$CODEX_HOME/automations/weekly-engineering-summary/`

Purpose:
- keep the weekly engineering summary automation inside the Nova repo
- make prompt changes reviewable in GitHub
- preserve a project-owned copy of the automation memory and operating rules

Files:
- `automation.toml` — tracked automation definition and prompt
- `memory.md` — tracked notes about evidence order, uncertainty handling, and prior run learnings

Sync rule:
- if the live local automation changes, update the matching files here
- if the tracked repo copy changes, mirror it back to the local Codex automation folder
