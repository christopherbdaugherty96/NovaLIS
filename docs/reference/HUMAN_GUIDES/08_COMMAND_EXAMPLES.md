# Command Examples
Updated: 2026-03-26

## Purpose
This guide shows natural ways to talk to Nova.

It is written for normal use, not for code review.
The goal is to make it obvious what kinds of requests Nova handles well today.

## Important Note About Voice
Current runtime truth:
- typed commands are active
- push-to-talk speech transcription is active
- voice-origin replies now auto-speak through the runtime speech helper more reliably
- text-to-speech is still subject to local device/output validation for final confidence
- wake word is still planned, not active runtime truth yet

So when you see examples below, read them as:
- something you can type now
- or something you can say through the active voice input path

## 1. Research and Search
Examples:
- `search for local AI sovereignty tools`
- `look up the latest OpenAI API pricing`
- `research robotics startups in warehouse automation`
- `search for weather in Detroit`

Good follow-ups:
- `open source 1`
- `summarize these search results`
- `compare the top 3 search results`
- `which result is the most reliable source and why`

## 2. News and Daily Briefing
Examples:
- `news`
- `latest news`
- `headlines`
- `daily brief`
- `intelligence brief`
- `today's news`

Good follow-ups:
- `summarize headline 1`
- `summary of article 1`
- `more on story 2`
- `compare headlines 1 and 2`
- `summarize politics news`
- `summarize global news`
- `summarize local news`
- `summarize tech news`
- `summarize crypto news`

## 3. Weather, Calendar, and System Snapshots
Examples:
- `weather`
- `forecast`
- `calendar`
- `today's schedule`
- `system status`
- `morning brief`
- `intro`
- `settings`

## 4. Screen and Explain Mode
Examples:
- `take a screenshot`
- `capture the screen`
- `analyze this screen`
- `explain this screen`
- `explain this`
- `what is this?`
- `what am I looking at?`
- `which one should I download?`

## 5. Websites, Files, and Local Computer Help
Examples:
- `open github`
- `open downloads`
- `open file C:\Users\Chris\Downloads\notes.txt`
- `volume up`
- `mute`
- `pause`
- `brightness down`
- `set brightness to 65`

## 6. Voice Output
Examples:
- `speak that`
- `read that`
- `say it`

There is also a governed same-thread second-opinion lane:
- click `Second opinion`
- or type `second opinion`
- or type `review this answer`
- Nova will request a bounded external second opinion on the recent exchange
- this stays advisory only

Useful voice confidence commands:
- `voice status`
- `voice check`

## 7. Project Continuity And Workspace
Examples:
- `create thread deployment issue`
- `show threads`
- `continue my deployment issue`
- `project status deployment issue`
- `thread detail deployment issue`
- `workspace home`
- `workspace board`
- `project home`

## 8. Trust Review
Examples:
- `trust center`
- `trust review`
- `trust status`
- `system status`

Use these when you want to understand:
- what Nova did recently
- what is currently blocked
- what mode Nova is in
- whether anything external happened recently
- which reasoning provider and route were used for a second opinion
- what the current voice runtime looks like

## 9. Policy Review
Examples:
- `policy center`
- `policy overview`
- `policy create weekday system status at 8:00 am`
- `policy create daily weather snapshot at 7:30 am`
- `policy show POL-...`
- `policy simulate POL-...`
- `policy run POL-... once`
- `policy delete POL-... confirm`

Use these when you want to:
- prepare a safe delegated policy draft
- inspect what the policy would do
- review the Governor verdict before any run
- run a safe draft once without enabling background automation

## 10. Governed Memory
Examples:
- `save this`
- `remember this: client supplies alcohol`
- `memory overview`
- `list memories`
- `show that memory`
- `memory show mem_123`
- `edit that memory: updated text`
- `delete that memory`

Dashboard note:
- Nova now exposes a dedicated Memory page for reviewing durable memory, linked threads, and recent items.

## 11. Local Project Understanding
Examples:
- `audit this repo`
- `summarize this repo`
- `create analysis report on this repo architecture`
- `visualize this repo`
- `show structure map`

## 12. Response Style and Tone
Examples:
- `tone status`
- `tone set concise`
- `tone set detailed`
- `tone set research detailed`
- `tone reset all`

## 13. Scheduled Updates and Reminders
Examples:
- `show schedules`
- `schedule daily brief at 8:00 am`
- `remind me at 2:00 pm to review deployment issue`
- `set quiet hours from 10:00 pm to 7:00 am`
- `cancel schedule SCH-123`

## 14. Pattern Review
Examples:
- `pattern opt in`
- `pattern status`
- `review patterns`
- `accept pattern PAT-123`
- `dismiss pattern PAT-123`

## Short Version
If you are not sure what to say, start with one of these:
- `news`
- `weather`
- `system status`
- `trust center`
- `workspace board`
- `explain this`
- `continue my <project>`
- `list memories`
- `visualize this repo`
