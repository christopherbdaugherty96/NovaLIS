# What Nova Can Do
Updated: 2026-03-13

## Overview
Nova's active capability surface now covers five big areas:
- research and information work
- computer help and local control
- voice and screen understanding
- continuity across ongoing work
- governed memory and persistence
- manual response-style control
- user-directed scheduled updates and reminders
- opt-in pattern review for ongoing work

## 1. Research and Information Work
Nova can:
- search the web through its governed search path
- open source pages in the browser
- summarize headlines
- give more detail on a selected story
- summarize the page behind a story link when available
- create multi-source reports
- build intelligence briefs
- show topic maps across the news cycle
- verify a statement or prior response
- create session analysis documents
- track stories over time

Examples:
- `search for local AI sovereignty tools`
- `open source 2`
- `summarize headline 3`
- `more on story 1`
- `daily brief`
- `verify this`
- `create analysis report on robotics startups`
- `track story EU AI Act`

## 2. Computer Help and Local Control
Nova can:
- open websites
- open approved files and folders
- speak text aloud
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

These are meant to make the dashboard and daily workflow easier to use.

Examples:
- `weather`
- `news`
- `calendar`
- `system status`

## 4. Voice, Screen, and Explain Mode
Nova can:
- transcribe speech into text
- speak text back aloud
- capture a screenshot region on request
- analyze the visible screen
- explain what you are looking at
- route explain requests to the right source, such as screen or file

Examples:
- `take a screenshot`
- `analyze this screen`
- `explain this`
- `what is this?`
- `which one should I download?`

Important note:
- screenshot and screen analysis are live
- wake word is still planned, not live runtime
- the next product-quality evolution is a cursor-first `what is this?` flow that expands to section or full page only when needed

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

Examples:
- `create thread deployment issue`
- `continue my deployment issue`
- `project status deployment issue`
- `biggest blocker in deployment issue`
- `which project is most blocked right now`
- `thread detail deployment issue`

## 6. Governed Memory
Nova now has active governed memory, which means it can preserve things across time under explicit user control.

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

Examples:
- `memory save deployment fix: confirm PYTHONPATH in container`
- `memory list`
- `memory show mem_...`
- `memory lock mem_...`
- `memory save thread deployment issue`
- `memory save decision for deployment issue: inspect path before rebuild`
- `memory list thread deployment issue`

## 7. What Is Planned But Not Fully Live Yet
Some important ideas are documented and partly scaffolded, but are not fully active runtime features today.

The biggest example is wake word.

Wake word is planned as a natural entrypoint like:
- `Hey Nova...`

But in the current runtime, Nova supports voice transcription and speech output without a live always-listening wake-word module.

## 8. Response Style Control
Nova can now expose and adjust its manual presentation tone without changing what it is allowed to do.

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

## 9. Scheduled Updates and Reminders
Nova can now support calm, user-directed scheduling without turning into a background actor.

It can:
- create a daily brief schedule
- create one-time reminders
- create recurring daily reminders
- show due and upcoming schedules
- show notification policy settings
- let the user set quiet hours
- let the user set a delivery rate limit
- let the user reschedule an existing item
- let the user cancel or dismiss schedule items
- surface scheduled items quietly in the dashboard

Examples:
- `show schedules`
- `notification status`
- `notification settings`
- `schedule daily brief at 8:00 am`
- `remind me at 2:00 pm to review deployment issue`
- `remind me daily at 9:00 am to review project threads`
- `reschedule schedule SCH-123 to 3:00 pm`
- `set quiet hours from 10:00 pm to 7:00 am`
- `clear quiet hours`
- `set notification rate limit 2 per hour`
- `cancel schedule SCH-123`
- `dismiss schedule SCH-123`

Important boundary:
- schedules are created only when the user asks
- scheduled items do not auto-run actions
- delivery is meant to stay calm, visible, cancellable, and policy-bound

## 10. Pattern Review
Nova can now help you review repeated patterns across threads and durable memory, but only if you explicitly opt in first.

It can:
- let you opt in or opt out of pattern review
- generate an advisory review queue on request
- show repeated blocker themes
- highlight blocked work that has no next step recorded
- highlight durable context that may still need a saved decision
- let you accept or dismiss proposals explicitly

Examples:
- `pattern opt in`
- `pattern status`
- `review patterns`
- `review patterns for deployment issue`
- `accept pattern PAT-...`
- `dismiss pattern PAT-...`

Important boundary:
- pattern review is opt-in only
- proposals are advisory only
- no proposal is auto-applied
- review does not run in the background

## Short Summary
Today Nova can already:
- research
- explain
- summarize
- inspect
- guide
- continue project work
- preserve governed memory
- expose manual response-style controls
- support explicit scheduled updates and reminders
- support opt-in pattern review for ongoing work
- help with the current screen
- help with the local computer in bounded ways

That is enough for Nova to behave more like a personal intelligence workspace than a simple assistant.
