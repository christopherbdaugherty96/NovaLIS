# Nova Release Checklist

Process document — what must happen before a release. Changes slowly. Distinct from the
Capability Inventory (Truth: what exists) and the QA Verification Report (Evidence: what was
observed this release).

```text
□ Runtime documentation clean (fingerprint regenerated; no drift)
□ Tests passing
□ Capability Inventory updated (docs/capability_verification/CAPABILITY_INVENTORY.md)
□ Live verification complete — QA Rule #1: restart to match current main FIRST, then verify
□ Documentation current (README / front-door / status docs)
□ No capability drift (capability count unchanged unless intended and reviewed)
□ QA Verification Report written (evidence for this release)
□ Release notes complete
```

## QA Rule #1 (permanent)

> Before any live verification, confirm the running process matches current `main`.
> If not, **restart before testing.**

Origin (2026-07-06): a 4-day-stale running backend produced two false negatives (news and
calendar looked broken; the code was fine). Never draw conclusions from a stale instance.

## The three verification documents

| Document | Question | Cadence |
|---|---|---|
| Capability Inventory | What exists / works / is verified? (Truth) | Updated each release |
| Release Checklist (this doc) | What must happen before shipping? (Process) | Changes slowly |
| QA Verification Report | What was observed this release? (Evidence) | Generated each release |
