# Nova Provider Budget And Usage Control Plan

Date: 2026-04-28

Status: Future architecture/product guide / not runtime truth until implemented

Purpose: define how Nova should control cost, quotas, and usage for cloud models, ElevenLabs, Google APIs, MCP/network tools, OpenClaw runs, browser/computer-use, and background reasoning.

---

## Core Rule

> **A provider can expand capability or quality, but it must not create hidden cost, hidden data movement, or hidden authority.**

---

## Providers / Resources To Track

```text
ElevenLabs characters / audio duration
cloud LLM calls such as OpenAI / DeepSeek / other provider lanes
Google API quota
MCP server calls
NetworkMediator outbound requests
OpenClaw run budgets
browser/computer-use time
background reasoning runs
local CPU / memory / time budgets
```

---

## Budget Types

```text
per-request limit
per-session limit
daily limit
monthly limit
provider-specific limit
role/workflow-specific limit
background-run limit
manual override limit
```

---

## Required User Visibility

Nova should eventually show:

```text
provider used
estimated or actual usage
remaining budget if available
whether cloud was used
fallback used if budget exhausted
what data was sent, summarized safely
what action authority effect occurred
```

Example:

```text
Online voice used: ElevenLabs.
Usage: short spoken response.
Authority effect: none.
Nothing was sent or changed.
```

---

## Default Behavior

```text
short low-risk responses may use enabled provider within budget
long readouts ask before spending significant budget
sensitive content uses local/redacted/ask-first routing
budget exhaustion falls back to local/text where possible
background jobs must have stricter limits than foreground user requests
```

---

## Provider-Specific Notes

### ElevenLabs

```text
track character count and audio duration where possible
ask before long document readouts
fall back to local TTS or text-only
never use online voice for sensitive content unless allowed
```

### Cloud LLMs

```text
track request count and estimated token usage where available
prefer local-first where configured
ask or disclose before cloud fallback for sensitive/high-volume tasks
```

### Google APIs

```text
track connector use and last error
separate read-only usage from draft/write proposals
quota failure should not imply user data was changed
```

### MCP / Network Tools

```text
track server/tool call count
apply risk class and network policy
unknown/blocked servers must not be called
```

### OpenClaw

```text
track run duration
track tool-call budget
track allowed/blocked actions
track approval requirements
```

---

## Failure / Exhaustion Message

```text
The provider budget for this path is exhausted or unavailable. I did not call the provider or perform the action. I can continue in local/text mode where possible.
```

---

## Guardrails

```text
No hidden provider calls.
No provider fallback for sensitive content without policy/approval.
No background provider usage without visible budget rules.
No cost-incurring long readouts without confirmation.
No raw secrets in usage logs.
```

---

## Build Order

```text
1. Define provider usage event schema.
2. Add simple provider-used trace card.
3. Add ElevenLabs character budget first when voice provider lands.
4. Add cloud model usage display later.
5. Add background reasoning budget rules before background jobs.
6. Add connector/API quota visibility later.
```

---

## Final Rule

> **Nova should be useful without surprising the user with cost, cloud use, or hidden provider calls.**
