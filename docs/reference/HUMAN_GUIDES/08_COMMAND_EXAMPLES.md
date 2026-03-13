# Command Examples
Updated: 2026-03-13

## Purpose
This guide shows natural ways to talk to Nova.

It is written for normal use, not for code review.
The goal is to make it obvious what kinds of requests Nova handles well today.

## Important Note About Voice
Current runtime truth:
- typed commands are active
- push-to-talk speech transcription is active
- text-to-speech is active
- wake word is still planned, not active runtime truth yet

So when you see examples below, read them as:
- something you can type now
- or something you can say through the active voice input path

## 1. Research and Search

Use these when you want current information or a quick lookup.

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

Use these when you want current headlines, summaries, or a more detailed story explanation.

Examples:
- `news`
- `latest news`
- `headlines`
- `daily brief`
- `intelligence brief`

Good follow-ups:
- `summarize headline 1`
- `more on story 2`
- `summary of story #3`
- `compare headlines 1 and 2`
- `track story EU AI Act`

Important note:
- `more on story 2` is meant to summarize the linked article page when Nova has the URL, not just repeat the headline.

## 3. Weather, Calendar, and System Snapshots

Use these when you want quick daily situational context.

Examples:
- `weather`
- `forecast`
- `calendar`
- `today's schedule`
- `system status`
- `system check`

Good follow-ups:
- `morning brief`
- `show my calendar`
- `what is the system status`

## 4. Screen and Explain Mode

Use these when you want Nova to help with what is currently on your screen.

Examples:
- `take a screenshot`
- `capture the screen`
- `analyze this screen`
- `explain this screen`
- `explain this`
- `what is this?`
- `what am I looking at?`
- `which one should I download?`

Good follow-ups:
- `help me do this`
- `what should I click next`
- `explain this in more detail`

Use cases:
- software download pages
- errors on screen
- settings panels
- charts
- code snippets
- technical pages

## 5. File and Document Help

Use these when you want Nova to explain or organize document-like material.

Examples:
- `create analysis report on the EU AI Act`
- `list analysis docs`
- `summarize doc 1`
- `explain section 2 of doc 1`
- `verify this`

If a file is selected or already part of the current context, these also fit naturally:
- `explain this`
- `summarize this file`

## 6. Websites, Files, and Local Computer Help

Use these when you want a local action or quick computer control.

Examples:
- `open github`
- `open source 2`
- `preview source 1`
- `open downloads`
- `open desktop`
- `open file C:\\Users\\Chris\\Downloads\\notes.txt`

Local control examples:
- `volume up`
- `mute`
- `unmute`
- `set volume to 40`
- `play`
- `pause`
- `resume`
- `brightness up`
- `brightness down`
- `set brightness to 65`

## 7. Voice Output

Use these when you want Nova to read something aloud.

Examples:
- `speak that`
- `read that`
- `say it`

These work best after Nova has already produced some text worth hearing.

## 8. Project Continuity

Use these when you are working on something over time and do not want to restate everything.

Examples:
- `create thread deployment issue`
- `show threads`
- `continue my deployment issue`
- `project status deployment issue`
- `biggest blocker in deployment issue`
- `which project is most blocked right now`
- `thread detail deployment issue`
- `why this recommendation`

These are especially useful for:
- debugging efforts
- research projects
- design work
- long-running implementation tasks

## 9. Governed Memory

Use these when you want to preserve something across time on purpose.

Examples:
- `memory save deployment fix: confirm PYTHONPATH in container`
- `memory list`
- `memory show mem_123`
- `memory lock mem_123`
- `memory defer mem_123`
- `memory unlock mem_123 confirm`
- `memory delete mem_123 confirm`
- `memory supersede mem_123 with deployment fix v2: use explicit path validation confirm`

Thread-linked memory examples:
- `memory save thread deployment issue`
- `memory save decision for deployment issue: inspect path before rebuild`
- `memory list thread deployment issue`

## 10. Natural Follow-Up Examples

Nova works best when follow-ups stay close to the current task.

Examples:
- `shorter`
- `compare those`
- `open the first one`
- `more on story 1`
- `help me do that`
- `what should I do next`
- `save this`
- `save this as part of deployment issue`

## 11. Best Practices

If you want the smoothest experience:
- be direct
- mention the thing you want if the context is ambiguous
- use thread names consistently for long-running work
- use explicit memory commands when something matters enough to preserve

## 12. Examples of Good Everyday Flows

### News flow
- `news`
- `more on story 2`
- `open source 2`

### Screen help flow
- `explain this`
- `what should I click next`

### Project continuity flow
- `continue my deployment issue`
- `biggest blocker in deployment issue`
- `memory save decision for deployment issue: inspect path before rebuild`

### System help flow
- `system status`
- `open downloads`
- `set brightness to 60`

## Short Version
If you are not sure what to say, start with one of these:

- `news`
- `weather`
- `system status`
- `explain this`
- `continue my <project>`
- `memory list`
