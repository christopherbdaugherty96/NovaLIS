# UI Simplification Audit — 2026-05-26

Audit of Nova dashboard before the product clarity slice.

---

## Navigation

11 primary nav items with no grouping:
Chat, Home, Goals, Agent, News, Workspace, Memory, Rules,
Trust, Settings, Intro.

Issues:

```text
- Too many top-level items for a new user to scan
- No visual grouping between "use Nova" pages (Chat, Home,
  Goals, News) and "inspect/configure" pages (Trust, Settings,
  Rules, Memory, Agent, Workspace)
- Intro is last in the list but is the first thing a new user
  needs
```

Classification:

```text
must fix: Regroup nav into primary (use) and secondary
  (inspect/configure) tiers using existing menu strip
optional polish: Reorder to put most-used pages first
defer: Full nav redesign
```

## Home page clarity

Home page has a "What Nova Can Do Right Now" capability panel.
Good, but the summary text ("Loading live capabilities...") is
generic. The kicker says "Today With Nova" which is vague.

Issues:

```text
- "Start Here" title is good but "Today With Nova" kicker
  is vague
- "Open Nova and move" badge is motivational but not
  informative
- Capability panel exists but is buried below fold
```

Classification:

```text
optional polish: Improve home summary wording
defer: Move capability panel higher
```

## Chat page clarity

Chat page is functional. The Workflow Focus widget says
"What are we getting done?" which is good. The input
placeholder is outcome-first. The hints panel is toggleable.

Issues:

```text
- "Workflow Focus" kicker is internal jargon
- "Ready for review" badge on Workflow Focus is confusing
  when nothing is in progress
```

Classification:

```text
optional polish: Rename "Workflow Focus" to simpler label
defer: Dynamic badge states
```

## Goals page clarity

Goals page has good structure: hero with DISPLAY ONLY badge,
status legend, sort controls, cards container.

Issues:

```text
- "Your Workflows" kicker above "Goals" title is redundant
  and slightly misleading (workflows implies execution)
- Subtitle "Visible, bounded, proof-tracked" is internal
  jargon
- No short helper text saying goals do not execute
- Goal page intro says "Planning is not authority" which is
  correct but jargon-heavy for users
```

Classification:

```text
must fix: Replace "Visible, bounded, proof-tracked" with
  user-facing language
must fix: Add helper text: "Goals track visible work. They
  do not run tasks."
must fix: Replace "Your Workflows" kicker with something
  clearer
optional polish: Simplify "Planning is not authority" to
  user language
```

## DISPLAY ONLY badge visibility

Present and visible in Goals page hero. Good placement.

Classification:

```text
no change needed
```

## Fallback state clarity

Fallback notice ("Showing demo goals because local goal
storage is unavailable.") exists in dashboard.js and has
CSS styling. Tested and working.

Classification:

```text
no change needed
```

## Empty state clarity

Empty state ("No goals yet") exists with helpful copy about
visible, governed cards. The language is slightly jargon-heavy
("governed card").

Classification:

```text
optional polish: Simplify "governed card" language
```

## Trust / receipt discoverability

Trust page exists at nav item "Trust" with title "Activity
Log." Contains: Operating State, Action Receipts, Recent
Governed Actions, Blocked Conditions, Runtime Health,
Operational Context, Assistive Notices, Voice Runtime,
Reasoning Transparency, Remote Bridge, Rules And Limits,
Live Capability Surface.

Issues:

```text
- Trust page has many sections — hard to scan
- Action Receipts exist but are not linked from Goal Cards
  or Home
- "Recent Governed Actions" uses "governed" jargon
- No quick link to Trust from Goals page
```

Classification:

```text
must fix: Add "View activity log" link on Goals page
  so users can find receipts from Goal Cards context
optional polish: Rename "Recent Governed Actions" to
  "Recent Actions"
defer: Simplify Trust page section count
```

## Confusing internal jargon

Found across multiple pages:

```text
"governed" — used in Goals, Trust, Memory, Agent, Settings
"bounded" — used in Goals, Agent, Intro
"proof-tracked" — used in Goals subtitle
"metered" — used in Settings
"governed permissions" — Settings section title
"governed memory action" — Memory confirmation
"assistive noticing" — Settings section title
"operational context" — Trust/Home section title
```

Classification:

```text
must fix: Replace "proof-tracked" in Goals subtitle
must fix: Replace "governed" in most user-facing labels
  with simpler words ("reviewed", "inspectable", or just
  remove the adjective)
optional polish: Address remaining jargon in secondary pages
defer: Comprehensive jargon sweep across all pages
```

## UI copy that implies authority that does not exist

```text
- "Home Agent helps Nova run manual tasks" (Agent page) —
  implies execution authority that is limited
- "Choose what can run" (Agent delivery section) — implies
  broader execution than exists
- "Try Once With Review" (Rules page) — implies execution
  capability
- Workflow Focus "Refine goal" / "Show steps" / "Reset focus"
  buttons — these are chat commands, not execution, so OK
```

Classification:

```text
optional polish: Soften Agent page language about "running"
defer: Rules page execution language (separate concern)
```

---

## Summary of must-fix items

```text
1. Goals page: replace "Your Workflows" kicker
2. Goals page: replace "Visible, bounded, proof-tracked"
3. Goals page: add helper text about no execution
4. Goals page: add link to Trust / Activity Log
5. Replace "governed" jargon in key user-facing labels
6. Nav grouping: separate use-pages from inspect-pages
```

## Summary of optional-polish items

```text
1. Simplify "Planning is not authority" to user language
2. Improve home summary wording
3. Rename "Workflow Focus" kicker
4. Simplify empty state "governed card" language
5. Rename "Recent Governed Actions" in Trust page
6. Soften Agent page execution language
```

## Deferred items

```text
1. Full nav redesign
2. Move capability panel higher on Home
3. Dynamic workflow focus badge states
4. Trust page section count reduction
5. Comprehensive jargon sweep
6. Rules page execution language
```
