# Nova Failure Mode Playbook

Date: 2026-04-28

Status: Future execution-control guide / not runtime truth until implemented

Purpose: define how Nova should explain and handle common failures without overclaiming, crashing, or hiding what happened.

---

## Core Rule

> **When Nova cannot do something, it should explain clearly, fail safely, and state what did not happen.**

---

## Standard Failure Response Shape

Every user-facing failure should include:

```text
what failed
why it failed in plain language
what Nova did not do
safe next step
whether anything needs user action
receipt/log reference where available
```

Avoid:

```text
raw stack traces
scary policy jargon
claiming success after partial failure
silent failures
hidden retries that perform real actions
```

---

## Common Failure Modes

### Model unavailable / slow local model

User-facing message:

```text
I could not get a reliable response from the local model right now. Nothing was executed or changed.
```

Safe fallback:

```text
retry later
use shorter prompt
use configured fallback provider only if allowed
show local model health diagnostic
```

### ElevenLabs key missing or budget exhausted

User-facing message:

```text
Online voice is not available right now, so I will stay in text/local mode. Nothing was sent or changed.
```

Safe fallback:

```text
local TTS if available
text-only response
voice setup diagnostic
```

### Google token expired / connector unavailable

User-facing message:

```text
I cannot read Google data right now because the connector needs attention. I did not read, send, create, or change anything.
```

Safe fallback:

```text
ask user to reconnect later
show connector status
continue with non-Google context
```

### MCP server unavailable or blocked

User-facing message:

```text
That connector is unavailable or blocked by policy. I did not call the tool or change anything.
```

Safe fallback:

```text
show connector status
use local docs if available
ask user to enable only after review
```

### OpenClaw run failed

User-facing message:

```text
The OpenClaw run did not complete. No approved external action was performed unless listed in the receipt.
```

Safe fallback:

```text
show run checkpoint
show last completed step
produce handoff summary
```

### Capability requires confirmation

User-facing message:

```text
This needs confirmation before anything happens. Nothing has been executed yet.
```

Safe fallback:

```text
show exactly what will happen
allow yes/no/edit/cancel
expire stale confirmation
```

### Connector paused

User-facing message:

```text
That work is currently paused by your direction. I can summarize the status, but I will not resume it unless you explicitly unpause it.
```

Safe fallback:

```text
show paused reason
show unpause criteria
recommend current active task
```

### Budget exhausted

User-facing message:

```text
The provider budget for this action is exhausted. I did not call the provider or perform the action.
```

Safe fallback:

```text
local/text fallback
shorter output
manual user approval for extra spend later
```

### Sensitive data blocked cloud path

User-facing message:

```text
This may contain sensitive information, so I kept it out of the cloud path. Nothing was sent to the online provider.
```

Safe fallback:

```text
local processing
redacted cloud request with approval
ask-first mode
```

---

## Receipt / Non-Action Statements

Use clear statements:

```text
Nothing was sent.
No calendar event was created.
No file was changed.
No connector was called.
No external system was updated.
The draft was prepared but not sent.
```

---

## Final Rule

> **A failure is safe only if the user can understand what happened, what did not happen, and what to do next.**
