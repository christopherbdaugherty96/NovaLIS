# Local Capability Signoff Matrix - 2026-05-06

Status: draft / review required

## Purpose

This document records current evidence for local, device, and runtime surfaces that OpenClaw may later want to rely on.

It is a read-only evidence document for the active priority-lock sequence:

```text
RequestUnderstanding trust/action-history review card
-> local capability signoff matrix
-> OpenClawMediator skeleton
-> first read-only OpenClaw workflow proof
```

The matrix answers, for each surface:

- Can Nova rely on this safely today?
- What proof exists?
- What is blocked?
- What caveats exist?
- What must be proven before OpenClawMediator can use it?

## Authority Boundary

This document does not enable any capability.

This document does not grant OpenClaw authority.

This document does not approve browser/computer-use.

This document does not approve external write actions.

This document does not create OpenClawMediator.

This document does not modify the capability registry, runtime code, tests, generated runtime truth, connectors, voice, installer, Auralis, YouTubeLIS, or workflow automation.

Runtime authority remains:

```text
User -> GovernorMediator -> Governor -> CapabilityRegistry -> SingleActionQueue -> LedgerWriter -> ExecuteBoundary -> Executor
```

Generated runtime truth and code remain authoritative over this human-maintained matrix.

## Status Legend

Use only these statuses:

| Status | Meaning |
| --- | --- |
| `pass` | Existing runtime evidence is strong enough for a future OpenClawMediator to treat this as a required governed boundary or a narrow read-only dependency, after mediator tests bind to it. |
| `fail` | Evidence shows the surface is unsafe or contradicts the required boundary. |
| `blocked` | The surface may exist, but OpenClaw reliance is not approved because it would widen authority, needs missing governance, or is explicitly paused. |
| `setup-dependent` | The surface exists but depends on local credentials, platform setup, user configuration, installed apps, or live-device conditions. |
| `not-yet-tested` | Runtime/docs suggest a surface, but this matrix found no focused proof sufficient for OpenClaw reliance. |
| `not-applicable` | The surface is not relevant to the first read-only OpenClaw workflow proof or must remain outside OpenClaw. |

## Matrix

| Surface | Status | Current evidence | Caveats | Proof required before OpenClaw reliance | OpenClaw reliance allowed |
| --- | --- | --- | --- | --- | --- |
| filesystem read | `setup-dependent` | Cap 63 `openclaw_execute` is described in generated runtime truth as able to run read-only templates through governed network or bounded local-read paths; `project_snapshot` is documented as the current read-only local project-analysis slice. | Evidence is template-specific. It does not prove arbitrary filesystem read, personal folder access, or user-file ingestion. | Mediator proof must bind read scope to an explicit envelope, approved roots, receipt output, and refusal for paths outside the envelope. | no |
| filesystem write | `blocked` | Runtime has local write surfaces such as governed memory and story tracking, but the active lock forbids external write expansion and this matrix does not approve new write use. | OpenClaw write reliance would create durable state changes and broaden the first proof beyond read-only. | Separate write-capability proof with Governor, confirmation, rollback/receipt story, and explicit user approval. Not part of this lock step. | no |
| approved path handling | `pass` | Cap 22 `open_file_folder` is active and generated docs state it opens allowed files/folders inside Nova-approved roots with confirmation; runtime auditor also uses allowlisted read paths for generated runtime docs. | Cap 22 is local navigation, not a general OpenClaw file API. Passing here means the boundary concept exists, not that OpenClaw may read/write paths freely. | Mediator tests must prove path normalization, root containment, denial of traversal/out-of-root paths, and receipts for any accepted path envelope. | yes, as a required boundary only |
| browser launch | `blocked` | Cap 17 `open_website` is active as a governed local browser-launch route. | The active lock explicitly pauses OpenClaw browser/computer-use expansion. Browser launch is not the same as isolated OpenClaw browsing authority. | Future browser proof must distinguish personal browser from isolated OpenClaw, bind domain/navigation scope, require approval where needed, and produce screenshots/receipts. | no |
| screen capture | `not-yet-tested` | Cap 58 `screen_capture` is active and request-time only in generated runtime truth; no background capture loop is documented. | This matrix did not run a fresh live screen-capture proof. Capture stores a snapshot and can expose sensitive visible data. | Fresh explicit-request proof showing no background capture, bounded capture scope, storage location, redaction/evidence hygiene, and receipt. | no |
| screen analysis | `not-yet-tested` | Cap 59 `screen_analysis` and Cap 60 `explain_anything` are active read-only perception/explanation routes. | Analysis depends on a prior/current explicit capture and may include OCR-sensitive content. | Fresh proof that analysis only consumes explicit capture/context, does not trigger actions, and does not leak private/system state into OpenClaw. | no |
| local command execution | `blocked` | Windows BAT launcher work exists for local operator startup/shutdown, but there is no approved OpenClaw general command-execution surface in the active lock. | A general command lane would be high risk and could bypass specific capabilities if not tightly mediated. | Dedicated command capability contract, allowlist, sandbox, timeout/resource limits, confirmation model, and receipts. Not approved for mediator skeleton. | no |
| OpenClaw execute / Cap 63 | `blocked` | Cap 63 is active and generated docs describe read-only OpenClaw templates plus Phase 9 goal-based execution. Code search also shows current OpenClaw approval endpoint language for auto-allowed actions. | Existing Cap 63 behavior must not be treated as the new mediator boundary. The priority lock requires signoff first, then OpenClawMediator skeleton, then read-only proof. | Mediator skeleton must centralize delegation, remove/contain direct chat-to-action reliance for the proof path, bind envelopes, approvals, cancellation, and receipts, and prove blocked actions pause instead of execute. | no |
| NetworkMediator routing | `pass` | Generated runtime truth lists `NetworkMediator` as the enforced outbound HTTP control and governance matrix shows network capabilities routed through `Governor -> NetworkMediator`. | Pass only covers the required network choke point. It does not approve new domains, browser automation, or connector expansion. | Mediator proof must show any OpenClaw network read uses allowed capability scope, logs through the governed path, and refuses direct HTTP bypass. | yes, as a required boundary only |
| ledger / receipt creation | `pass` | Generated runtime truth lists `LedgerWriter` in the governance spine and runtime invariants require all execution logged to ledger. OpenClaw API code logs run-issued/completed/cancel/delivery events. | Existing ledger events are not the same as a complete OpenClawMediator receipt schema. | Define mediator receipt fields for run id, envelope, decision, action boundary, result, blocked actions, and non-action statement; prove they are written. | yes, as a required boundary only |
| confirmation / approval boundary | `setup-dependent` | Generated matrix marks confirm-required capabilities such as Cap 22 and Cap 64; tests cover confirmation requirements for file/folder and Governor confirm-risk handling. | OpenClaw API currently has auto-allow transition language for action approval, so OpenClaw-specific approval is not signed off. | Mediator must prove per-action approval where required, no auto-approval for high-boundary actions, denial path, timeout/cancel behavior, and receipts. | no |
| email draft only / Cap 64 | `blocked` | Cap 64 is active as `send_email_draft`; generated docs state it composes a local `mailto:` draft, requires confirmation, and Nova never sends email autonomously. | Opening a mail client is an external effect and setup-dependent. This lock does not approve autonomous email, inbox access, SMTP, or OpenClaw email workflows. | Separate proof that mediator can only request draft preview under explicit user confirmation, never send, never access inbox, and logs receipt/non-send statement. | no |
| calendar read only | `setup-dependent` | Cap 57 `calendar_snapshot` is active as a read-only local/service inspection route; connector package foundation includes `ics_calendar`. | Calendar truth depends on configured local ICS/package setup. No Google OAuth/runtime connector expansion is allowed by the lock. | Proof with sample/local calendar source, no writes, no OAuth expansion, no scheduling, clear source label, and receipt. | no |
| Shopify read only / Cap 65 | `setup-dependent` | Cap 65 is active as `shopify_intelligence_report`; generated docs state it is Tier 1 read-only via Shopify GraphQL Admin API and requires `NOVA_SHOPIFY_SHOP_DOMAIN` plus `NOVA_SHOPIFY_ACCESS_TOKEN`. | Depends on store credentials and network access. Shopify writes remain explicitly paused. | Fresh read-only proof with scoped env vars, NetworkMediator routing, no mutations, redacted credentials, and receipt. Not needed for first local read-only OpenClaw proof. | no |
| voice input | `setup-dependent` | Runtime reference lists STT transcription as an active supporting surface using local ffmpeg + Vosk, routed into normal chat. | Depends on microphone/audio setup and local model availability. Voice input is not required for OpenClawMediator. | Live-device push-to-talk proof, transcript boundary, no wake-word activation, and no direct execution bypass. | no |
| voice output | `setup-dependent` | Cap 18 `speak_text` is active; generated runtime gaps still recommend live-device spoken-output validation for local TTS. | Local audio stack varies by device. Voice output should not be an OpenClaw dependency for the first proof. | Live-device TTS proof with speech-safe formatting and no raw link/system-token leakage. | no |
| Windows runtime readiness | `pass` | Windows launcher scripts were hardened on main and smoke-tested for start/stop; generated runtime truth reports active dashboard, WebSocket, voice, and capability surfaces. | This is operator readiness, not capability authorization. It does not imply all optional local integrations are configured. | Before mediator proof, run a fresh local startup/status smoke and capture backend health plus relevant proof transcript. | yes, as local operator precondition only |
| installer readiness | `blocked` | Active priority lock explicitly pauses one-click installer work. | Installer state is not needed for mediator or first read-only proof. | Separate installer proof after lock permits installer work. | no |

## Blockers

- OpenClawMediator does not exist yet and must not be skipped.
- Cap 63/OpenClaw has active runtime surfaces, but those are not accepted as the new mediator boundary.
- Browser/computer-use expansion is explicitly paused.
- External write actions are explicitly not approved.
- General local command execution is blocked.
- Email, calendar write, Shopify write, Google OAuth/runtime connector expansion, and workflow automation remain paused.
- OpenClaw-specific human approval is not signed off while auto-allow transition behavior still exists in the current OpenClaw API surface.

## Setup-Dependent Items

- filesystem read: only bounded/template/local-read proof is relevant, not arbitrary read access.
- confirmation / approval boundary: core Governor confirmation evidence exists, but OpenClaw-specific approval needs proof.
- calendar read only: depends on local/service source configuration; no Google connector expansion.
- Shopify read only / Cap 65: depends on Shopify environment variables and live store credentials; read-only only.
- voice input: depends on microphone, ffmpeg, Vosk, and local audio conditions.
- voice output: depends on local TTS/audio output; live-device proof is still recommended.

## Not Approved For OpenClaw Yet

OpenClaw is not approved to rely on:

- arbitrary filesystem reads
- any filesystem writes
- browser launch or browser/computer-use
- screen capture or screen analysis
- local command execution
- direct Cap 63 execution as a substitute for OpenClawMediator
- email drafting
- calendar access
- Shopify access
- voice input or voice output
- installer behavior
- external write actions of any kind

The only surfaces marked as allowable dependencies are foundational boundaries, not user-facing powers:

- `NetworkMediator` as a required outbound network choke point
- `LedgerWriter` / receipts as required proof infrastructure
- approved path handling as a required local-read containment boundary
- Windows runtime readiness as a local operator precondition

## Required Before OpenClawMediator

Before OpenClawMediator work begins, reviewers should approve or edit this matrix and confirm:

1. The first mediator skeleton will not call browser/computer-use.
2. The first mediator skeleton will not add external write authority.
3. The first mediator skeleton will not use Cap 63 direct execution as an unreviewed shortcut.
4. The mediator boundary will require explicit envelopes, policy checks, cancellation, and receipts.
5. The first workflow proof will be read-only and preferably local/sample-data based.
6. Any NetworkMediator reliance will be read-only and scoped.
7. Any ledger reliance will include a non-action statement describing what did not happen.

## Review Verdict

Draft verdict: review required before merge.

Recommended merge condition:

- Merge only if reviewers agree this document is evidence-only and does not overstate OpenClaw readiness.
- Merge only if any wording that appears to approve browser/computer-use, external write actions, or direct OpenClaw delegation is removed.
- After merge, the next allowed step is `OpenClawMediator skeleton`, still without broad automation or browser/computer-use expansion.
