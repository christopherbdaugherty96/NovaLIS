# Nova Sensitive Data Routing Plan

Date: 2026-04-27

Status: Future architecture plan / not current runtime truth

Purpose: define how Nova should decide whether content can stay local, use cloud providers, be redacted, or require user approval before leaving the machine.

---

## Active Priority Note

This is future planning only. Do not implement broad sensitive-data routing before RequestUnderstanding trust/action visibility unless explicitly reprioritized.

---

## Executive Summary

As Nova gains Google, MCP, ElevenLabs, browser, memory, and external workflow integrations, it needs a clear sensitive-data routing policy.

Core rule:

> **Cloud providers may expand intelligence or voice quality. They must not silently receive sensitive data.**

---

## Routing Modes

```text
LOCAL_ONLY — keep content local; no cloud model/provider/voice call
LOCAL_FIRST_CLOUD_FALLBACK — try local first; ask or disclose before cloud fallback
CLOUD_ALLOWED — user/provider policy allows cloud for this content
CLOUD_REDACTED — redact sensitive parts before cloud use
ASK_FIRST — require user approval before cloud use
BLOCKED — do not process through that provider/path
```

---

## Sensitive Data Categories

```text
credentials / API keys / tokens
financial data
medical/health data
legal documents
identity documents / SSN / license/passport
private emails/messages
customer records
children/minors data
precise home/security data
business secrets / unreleased code
personal photos/audio/voice clone material
calendar/location patterns
```

---

## Provider-Specific Relevance

### ElevenLabs

```text
Use cloud voice for normal low-sensitivity responses if enabled.
Use local/private voice or text-only for sensitive content unless user approves.
Ask before long sensitive readouts.
Never send API keys/secrets to voice provider.
```

### Google / Gmail / Calendar / Drive

```text
Google tokens/scopes grant access, not permission.
Summaries may be local-first when sensitive.
Drafts should be reviewed before creation/sending.
Receipts should state what was read and what was not changed.
```

### MCP

```text
MCP outputs are untrusted input.
Remote MCP calls require connector registry and network policy.
Filesystem/Git/database contents may be sensitive by default.
```

### OpenClaw

```text
OpenClaw may receive only the minimum context required by envelope.
Worker runs should record input sources and sensitive-data policy.
```

---

## Required UX

When sensitivity matters, Nova should show or say:

```text
This may contain sensitive information.
I can keep this local, redact it, or ask before using an online provider.
```

For cloud use:

```text
Cloud provider used: <provider>
Data included: <safe summary>
Sensitive fields redacted: yes/no
Action authority effect: none unless separately approved
```

---

## Guardrails

```text
Do not put secrets in prompts.
Do not store secrets in run state or trace cards.
Use summaries/hashes for sensitive payloads.
Cloud fallback must be visible.
Sensitive-content classification should fail conservatively.
User approval for cloud use is not approval for action execution.
```

---

## Build Order

```text
1. Define sensitivity categories and routing modes.
2. Add manual user setting for local-only / balanced / cloud-allowed.
3. Add sensitive-content warning in trust/action view.
4. Add provider disclosure for ElevenLabs/cloud model use.
5. Add connector-specific redaction policies.
6. Add tests for secrets, email, calendar, customer data, and code.
```

---

## Final Rule

> **Sensitive data should move only when the user can understand why, where, and under what limits.**
