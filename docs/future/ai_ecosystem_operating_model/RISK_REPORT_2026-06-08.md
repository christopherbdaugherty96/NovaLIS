# Risk Report - 2026-06-08

Status: Draft risk report
Date: 2026-06-08
Source: Local repo inspection and operating-model package creation
Reason: Identify risks before promoting the package into active practice

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Obsidian notes treated as permission | Unauthorized action planning or execution | Repeat that Obsidian is context-only in every operating document |
| Draft AI output treated as accepted truth | Stale or speculative plans may guide work | Require status, source, date, reason, and review |
| Multiple active priorities | Scope drift and oversized PRs | Use one active priority and defer to `.agent_context/current_priority.md` for Nova |
| Business needs bleed into Nova runtime | Commerce or automation pressure may widen authority | Use bridge rule: need -> proposal -> review -> approved scope |
| GitHub merge mistaken for execution authority | Implemented code may be treated as permission to act | Preserve Governor/capability/receipt path |
| Live proof invented from docs validation | False certification | Separate docs validation, runtime validation, and live proof |
| Stale docs revive old work | Agents may follow superseded plans | Mark stale docs and record supersession |

## Current Risk Posture

Low for this PR/package if it remains docs-only.

High if these files are later copied into an active agent prompt without the
authority notices and review gates.
