# AI Ecosystem Operating Model

Status: Draft operating package
Date: 2026-06-08
Source: User-directed build prompt
Scope: Docs-only context and coordination model

This package defines a governed operating model for coordinating ChatGPT, Codex,
Claude, OpenClaw, NovaLIS, Obsidian, GitHub, and business planning work without
turning context into execution authority.

Core invariant:

```text
Obsidian coordinates context; it does not authorize execution.
```

This package does not implement Nova runtime behavior, does not add capabilities,
does not change capability locks, does not add scheduler/background execution,
does not add Shopify writes, and does not implement Second Brain Slice 1.

## Required Reading Order

1. [AI_ECOSYSTEM_OPERATING_RULES.md](AI_ECOSYSTEM_OPERATING_RULES.md)
2. [ACTIVE_PRIORITY.md](ACTIVE_PRIORITY.md)
3. [CURRENT_TRUTH.md](CURRENT_TRUTH.md)
4. [VAULT_STRUCTURE.md](VAULT_STRUCTURE.md)
5. [VALIDATION_PROCEDURES.md](VALIDATION_PROCEDURES.md)
6. [VALIDATION_REPORT_2026-06-08.md](VALIDATION_REPORT_2026-06-08.md)
7. [FINDINGS_REPORT_2026-06-08.md](FINDINGS_REPORT_2026-06-08.md)
8. [RISK_REPORT_2026-06-08.md](RISK_REPORT_2026-06-08.md)
9. [IMPROVEMENT_RECOMMENDATIONS.md](IMPROVEMENT_RECOMMENDATIONS.md)
10. [FINAL_IMPLEMENTATION_SUMMARY_2026-06-08.md](FINAL_IMPLEMENTATION_SUMMARY_2026-06-08.md)

## Authority Notice

These files are proposed coordination documents. They are not Nova runtime truth
unless later reviewed and promoted through the repo's accepted governance process.

For exact Nova runtime truth, use:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- actual code
- receipts and logs

For active implementation scope, use:

- `.agent_context/current_priority.md`
- `docs/status/CURRENT_WORK_STATUS.md`
- accepted priority locks
