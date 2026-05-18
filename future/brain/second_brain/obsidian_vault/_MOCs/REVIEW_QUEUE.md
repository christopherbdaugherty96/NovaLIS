# Review Queue

Status: future review map / not runtime truth.

Review order:

```text
candidate notes
-> source checks
-> relationship checks
-> authority boundary check
-> stale/conflict check
-> promote / reject / supersede
```

## Candidate Sources

- `raw/inbox/`
- `synthesis/`
- `proposals/`

## Review Gates

- `non_authorizing: true` is present.
- Promoted notes have `review_state: approved`.
- Promoted notes have `reviewed_by` and `reviewed_at`.
- Promoted notes have at least one `source_refs` or `ledger_refs` item.
- Capability logs never imply permission.
- Runtime claims cite generated runtime docs.
- Receipt claims cite ledger refs but do not replace the ledger.
