# Dashboard Stale / Degraded Rendering Proof - 2026-05-07

Status: pass / screenshot proof still blocked

## Request Coverage

- visible `provider_status` rendering
- visible `freshness_status` rendering
- visible `source_credibility` rendering
- empty malformed/degraded search widget rendering

## What Happened

The dashboard search widget now renders a read-only `Evidence state` panel when search evidence contains visible truth metadata.

Visible behavior:

- `provider_status` appears as `Provider: <status>` when not `ok`
- `freshness_status` appears as `Freshness: <status>` when not `unknown`
- `source_credibility` appears as source signal count plus conservative credibility rows
- empty degraded/malformed search widgets remain visible as `Search state` instead of disappearing

This makes stale/degraded search behavior inspectable in the UI without implying success.

## Verification

```text
6 passed
24 passed
node --check passed
```

## What Did Not Happen

- No browser/computer-use capability was added.
- No external write occurred.
- No OpenClaw execution or expansion occurred.
- No autonomous workflow was added.
- No direct Cap 63 shortcut was used.
- No definitive source truth score was claimed.

## Governance Boundary

The panel renders existing evidence metadata. It does not authorize action, execute search, open sources, or convert source credibility signals into authority.

## Evidence

- `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/dashboard_stale_degraded_rendering_contract.json`
- `docs/PROOFS/UI-Commands/evidence/2026-05-07/raw/dashboard_stale_degraded_rendering_pytest_results.txt`
- `nova_backend/tests/phase45/test_dashboard_search_widget_followups.py`
- `nova_backend/static/dashboard-chat-news.js`
- `nova_backend/static/dashboard-surfaces.css`

## Screenshot Status

No screenshot was captured in this pass. Browser Use screenshot/click-path proof remains blocked by the existing runtime asset setup issue and should not be substituted with a fake screenshot claim.
