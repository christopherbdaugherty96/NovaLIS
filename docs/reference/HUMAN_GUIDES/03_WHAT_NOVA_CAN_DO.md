# What Nova Can Do
Updated: 2026-03-26

## Overview
Nova's active capability surface now covers these big areas:
- research and information work
- computer help and local control
- voice and screen understanding
- continuity across ongoing work
- governed memory and persistence
- manual response-style control
- user-directed scheduled updates and reminders
- opt-in pattern review for ongoing work
- visible workspace and trust review surfaces
- visible policy review surfaces for disabled delegated drafts
- token-gated remote bridge access for read/reasoning requests

## 1. Research and Information Work
Nova can:
- search the web through its governed search path
- answer first and show sources on demand
- open source pages in the browser
- summarize headlines
- give more detail on a selected story
- summarize the page behind a story link when available
- search for a news topic and route that into research
- summarize cleaner news channels such as politics, global, local, tech, and crypto
- create multi-source reports
- build intelligence briefs
- verify a statement or prior response
- request a governed external second opinion from the chat bar or with `second opinion`
- create session analysis documents
- track stories over time

Examples:
- `search for local AI sovereignty tools`
- `open source 2`
- `summarize headline 3`
- `summary of article 1`
- `today's news`
- `summarize politics news`
- `summarize global news`
- `summarize local news`
- `summarize tech news`
- `summarize crypto news`
- `more on story 1`
- `daily brief`
- `verify this`
- `second opinion`
- `review this answer`
- `create analysis report on robotics startups`
- `track story EU AI Act`

## 2. Computer Help and Local Control
Nova can:
- open websites
- open approved files and folders
- speak text aloud through the local speech path
- change volume
- control media playback
- change brightness
- report system status and model readiness

Examples:
- `open github`
- `open downloads`
- `speak that`
- `mute`
- `pause`
- `set brightness to 70`
- `system status`

## 3. Snapshots and Daily Surfaces
Nova can load quick information views for:
- weather
- news
- calendar
- system state
- memory
- workspace continuity
- trust review
- introduction and settings guidance

Examples:
- `weather`
- `news`
- `calendar`
- `system status`
- `intro`
- `settings`
- `workspace home`
- `workspace board`
- `trust center`

## 4. Voice, Screen, and Explain Mode
Nova can:
- transcribe speech into text
- speak text back aloud
- capture a screenshot region on request
- analyze the visible screen
- explain what you are looking at
- route explain requests to the right source, such as screen or file
- auto-speak voice-origin answers through the runtime speech helper

Examples:
- `take a screenshot`
- `analyze this screen`
- `explain this`
- `what is this?`
- `which one should I download?`

Important note:
- screenshot and screen analysis are live
- wake word is still planned, not live runtime
- voice output is improved in code and still depends on final local device/audio validation for full confidence

## 5. Continuity and Ongoing Work
Nova can now help with ongoing work rather than only one-off prompts.

It can:
- create and continue project threads
- show thread health and blockers
- show what changed since last view
- show latest decision and memory depth
- identify the most blocked project
- explain why it is recommending a next step
- open a thread detail panel with the current project snapshot
- show a broader Workspace page for project continuity

Examples:
- `create thread deployment issue`
- `show threads`
- `continue my deployment issue`
- `project status deployment issue`
- `biggest blocker in deployment issue`
- `which project is most blocked right now`
- `thread detail deployment issue`
- `workspace board`

## 6. Governed Memory
Nova has active governed memory, which means it can preserve things across time under explicit user control.

It can:
- save a memory item
- list memory items
- show a memory item
- lock or defer a memory item
- unlock or delete a memory item with confirmation
- supersede an older memory item with a newer one
- save thread snapshots into memory
- save thread decisions into memory
- list memory linked to a specific thread
- expose a dedicated Memory page for reviewing durable memory, scope distribution, linked threads, and recent items

Examples:
- `save this`
- `remember this: the client supplies alcohol`
- `memory overview`
- `memory list`
- `memory show mem_...`
- `memory lock mem_...`
- `memory save thread deployment issue`
- `memory save decision for deployment issue: inspect path before rebuild`
- `memory list thread deployment issue`

## 7. Trust And Workspace Visibility
Nova now has clearer product surfaces for understanding what it is doing and where current work lives.

It can:
- show a Trust page
- show a Policies page
- show a Settings page
- show an Introduction page
- show remote bridge status
- show provider and connection status
- summarize recent governed actions
- show blocked conditions
- let you drill into why a recent action happened
- show current operating mode and failure state
- show a Workspace page
- show a local-project Structure Map
- inspect disabled policy drafts
- simulate a policy draft
- run a safe draft once manually
- show voice runtime status and a voice-check path
- show reasoning provider, route, and authority truth when a second opinion is used

Examples:
- `intro`
- `settings`
- `trust center`
- `policy center`
- `policy overview`
- `policy create weekday system status at 8:00 am`
- `trust status`
- `bridge status`
- `connection status`
- `voice status`
- `voice check`
- `second opinion`
- `workspace board`
- `visualize this repo`
- `show structure map`

## 8. Local Project Understanding
Nova can locally:
- summarize a repo
- give a local project overview
- create a local architecture report
- show a human-facing Structure Map for the repo

Examples:
- `audit this repo`
- `summarize this repo`
- `create analysis report on this repo architecture`
- `visualize this repo`

## 9. What Is Planned But Not Fully Live Yet
Some important ideas are documented and partly scaffolded, but are not fully active runtime features today.

The biggest examples are:
- wake word
- richer connectors
- actionable provider/connector setup instead of visibility-first status only
- deeper project/workspace system work
- richer visualizer stages beyond the current structured graph view
- delegated trigger runtime for policies

## 10. Response Style Control
Nova can expose and adjust its manual presentation tone without changing what it is allowed to do.

It can:
- show the current global tone profile
- show active per-domain overrides
- let the user set manual tone profiles
- let the user reset one domain or all tone settings
- show recent tone changes in an inspectable way

Examples:
- `tone status`
- `tone set concise`
- `tone set research detailed`
- `tone reset all`

## 11. Scheduled Updates and Reminders
Nova can support calm, user-directed scheduling without turning into a background actor.

Examples:
- `show schedules`
- `schedule daily brief at 8:00 am`
- `remind me at 2:00 pm to review deployment issue`
- `set quiet hours from 10:00 pm to 7:00 am`
- `cancel schedule SCH-123`

Important boundary:
- schedules are created only when the user asks
- scheduled items do not auto-run actions

## 12. Pattern Review
Nova can help review repeated patterns across threads and durable memory, but only if you explicitly opt in first.

Examples:
- `pattern opt in`
- `pattern status`
- `review patterns`
- `accept pattern PAT-...`
- `dismiss pattern PAT-...`

## Short Summary
Today Nova can already:
- research
- explain
- summarize
- inspect
- continue project work
- preserve governed memory
- expose trust and workspace state more clearly
- help with the current screen
- help with the local computer in bounded ways

That is enough for Nova to behave more like a personal intelligence workspace than a simple assistant.
