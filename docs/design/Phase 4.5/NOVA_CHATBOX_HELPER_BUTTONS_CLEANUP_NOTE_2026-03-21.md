# Nova Chatbox Helper Buttons Cleanup Note
Date: 2026-03-21
Status: Product note only
Scope: Simplify the helper buttons near the chat box so they expose only a short, basic everyday command set

## Purpose
This note captures a simple UI/product preference:

The helper buttons near the chat box currently feel too crowded.

They should be cleaned up so the visible quick actions stay basic, familiar, and easy to scan.

This is not runtime truth.
It is a product note for a future UI cleanup pass.

## Recommended Direction
The bottom helper area near the chat box should only show a small set of basic commands.

The recommended visible helper buttons are:
- Documents
- Volume 50%
- Brightness 50%
- Facebook
- Pandora
- GitHub
- Today's brief
- System status
- Schedules

## Product Rule
The helper row should feel like:
- quick everyday actions
- low-friction shortcuts
- easy-to-understand commands

It should not feel like:
- a crowded capability wall
- a diagnostic panel
- a long list of mixed intents

## UX Recommendation

### Keep The Row Short And Recognizable
The visible button set should stay small enough that a user can understand it at a glance.

The intent is:
- fewer buttons
- more obvious buttons
- stronger everyday usefulness

### Prefer Familiar Commands
The helper row should emphasize commands a normal user immediately understands, such as:
- opening a familiar place
- setting a common device level
- opening common destinations
- getting a brief or status snapshot

### Avoid Overloading The Row
If additional shortcuts exist later, they should be:
- hidden behind a separate expansion affordance
- grouped somewhere else
- or kept out of the default helper row entirely

The default helper row should stay basic.

## Placement
This belongs in the current product/UI cleanup track.

It is not a Phase 7 or Phase 8 autonomy item.
It is a straightforward interface simplification pass.

## Suggested Future Branch
- `codex/chatbox-helper-buttons-stage1-cleanup`

## Success Condition
The helper row near the chat box feels:
- simpler
- easier to scan
- more user-friendly
- more focused on basic actions

And the default visible buttons are limited to:
- Documents
- Volume 50%
- Brightness 50%
- Facebook
- Pandora
- GitHub
- Today's brief
- System status
- Schedules
