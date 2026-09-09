# Nova Durability and State-Ownership Decision

Status: PROPOSED FOR #408 EXACT-HEAD REVIEW  
Evidence baseline: `main@ca66a06daa2ca41e6b2a20b8942bc7eee8c96b96`  
Decision date: 2026-09-08  
Scope: architecture and implementation ordering only; this document authorizes no storage implementation.

## Decision

Nova will use one canonical production user-data root and retain file-backed stores for the beta durability lane. Backup, restore, migration, and repair will run through a Nova-owned maintenance coordinator that holds an interprocess lock and prevents runtime mutation while it captures or replaces state. SQLite is not selected for the beta lane.

The evidence does not show a need for indexed relational queries, multi-writer runtime access, or atomic mutation across independently authoritative objects. Most authoritative records are small and contained in one JSON document; the ledger is append-only. The immediate durability risks are fragmented path ownership, process-local locking, silent fallback from corrupt files to empty defaults, uncoordinated snapshots, and secret portability. Those risks must be fixed directly before reconsidering storage technology.

## Canonical production locations

The supported Windows installation contract is:

```text
%LOCALAPPDATA%\Nova\
  control\              stable maintenance control plane
    maintenance.lock
    activation-a.json
    activation-b.json
    recovery-journal.json
    staging\
  generations\
    <generation-id>\    validated durable generation selected by activation slot
      data\             durable non-secret operating state
      secrets\          machine-bound protected credentials
      models\           model trust/version state and local model metadata
  cache\                 recreatable state
  logs\                  bounded support logs
  captures\              sensitive user artifacts

user-selected location\
  backups\               encrypted recovery or portable backup artifacts
```

`%LOCALAPPDATA%\Nova` is a stable container and is never swapped as a unit. The exact activation unit is one complete `generations\<generation-id>` directory. Restore or migration prepares and validates a generation under `control\staging`; it remains immutable from final validation through activation. The maintenance lock, two activation slots, and recovery journal remain open and addressable throughout activation because they sit outside every generation. Cache, logs, and captures are also outside activation because they are excluded or independently retained by policy. After a successful process restart binds every store to the selected generation, that generation becomes the sole writable live generation.

Application code and static configuration remain in the install directory and are replaceable. A writable source checkout may use an explicit development override, but writable source code must not implicitly become the production data contract. `NOVA_RUNTIME_DIR` remains a supported explicit override and must resolve to the same stable-container layout. Backup artifacts must not be written inside the live user-data root.

## Current-main inventory and classification

| State surface | Current owner/path | Classification | Portability and recovery decision |
| --- | --- | --- | --- |
| Governed memory | `data/nova_state/memory/items.json` | Portable user state | Required in recovery and portable backup, including deleted/superseded history. IDs and links are preserved. |
| User memory | `data/nova_state/memory/user_memory.json` | Portable user state | Required; migrate intact and validate schema before activation. |
| Nova self-memory | `data/nova_state/memory/nova_self_memory.json` | Portable user state | Required where it contains user-specific learned context; preserve provenance and review state. |
| Quick corrections | `data/nova_state/memory/quick_corrections.jsonl` | Portable user state and mutable authoritative consumption state | Required; preserve record order and each record's `consumed` value. Validate the rewritten file as a whole so consumed corrections cannot replay after restore. There are no deletion/tombstone semantics. |
| User profile | `data/nova_state/profiles/user_profile.json` | Portable user state | Required. |
| Tone profile | `data/nova_state/personality/tone_profile.json` | Portable user state | Required. |
| Runtime settings and permission history | `data/nova_state/settings/runtime_settings.json` | Portable user state and authority configuration | Required. Restore must not silently enable a permission unavailable or locked in the target build. |
| Atomic policies | `data/nova_state/policies/atomic_policies.json` | Authoritative operational state | Required. Validate against target capability locks before activation. |
| Notification schedules and delivery state | `data/nova_state/notifications/schedules.json` | Portable user state and authoritative operational state | Required. Restore paused; resume only after clock, timezone, and policy validation. Never replay missed actions automatically. |
| Pattern-review queue | `data/nova_state/patterns/review_queue.json` | Portable user state | Required when unresolved; resolved history may follow bounded retention. |
| Goals | currently `nova_backend/data/goals.json` | Portable user state | Required. Current source/install-relative location violates the production contract and must move through migration. |
| Story-tracker subscriptions and snapshots | currently `nova_workspace/story_tracker/*.json` | Portable user state; graph/projections partly derived | Preserve tracked topics and source snapshots. Rebuild relationship graphs where possible. Current repository-relative location must move. |
| OpenClaw envelopes | `data/nova_state/openclaw_envelopes.json` | Authoritative operational state | Preserve unresolved/active envelopes and terminal history required for truthful status. Restore paused pending policy and capability validation. |
| OpenClaw agent runtime | `data/nova_state/openclaw/agent_runtime.json` | Authoritative operational state | Preserve schedules, inbox/outcomes, run state, and references. Restore paused; never resume an interrupted run automatically. |
| OpenClaw execution memory | `data/nova_state/openclaw/execution_memory.json` | Portable user state / advisory history | Preserve when it affects learned ordering or visible history; it never restores authority. |
| Ledger and receipts | `data/ledger.jsonl` | Authoritative audit state | Required in recovery backup. Preserve byte order and hashes; never rewrite history during ordinary restore. Portable restore imports it as prior-device history and starts a new device/session boundary. |
| Provider usage | `data/nova_state/usage/provider_usage.json` | Authoritative operational/accounting state | Preserve current budget window and history needed for truthful usage. Expired aggregates may later be compacted by an explicit retention rule. |
| Provider keys and connection health | `data/nova_state/connections/provider_keys.json` | Machine-bound secret plus recreatable health metadata | Raw keys must leave this plaintext store in the authorized implementation. Exclude secrets from portable backup; discard/recompute health metadata. |
| Google credential vault | `data/nova_state/connections/google_workspace_credentials.json` | Machine-bound secret state | DPAPI ciphertext may be included only as an optional same-profile recovery artifact. Restore must prove it decrypts in the current DPAPI context before activation. If it cannot, quarantine the blob, preserve all non-secret user state, and require provider reconnect. Exclude from portable backup. |
| Environment-backed provider secrets | Windows user environment / process environment | Machine-bound secret configuration | Never copy raw environment variables into backup. Restore records only that reconnection is required. |
| Calendar ICS path | `NOVA_CALENDAR_ICS_PATH` and external user file | Machine-specific configuration and externally owned data | Preserve a redacted connection descriptor, not the external calendar file by default. Require path reselection on another machine. |
| Model/provider/runtime selection | environment plus runtime settings | Mixed portable and machine-specific configuration | Portable intent includes setup mode, routing policy, response profile, location, and units. Model path, Ollama URL, host/port, device paths, and runtime tuning are recreated or reconfigured. |
| Model version lock | `models/current_model_hash.txt` | Machine-specific trust state | Include in same-machine recovery. On cross-machine restore, recompute and require the existing explicit model-update confirmation when different. |
| News synthesis cache | `data/nova_state/news_synthesis_cache.json` | Re-creatable derived state | Exclude from backup. |
| Screen captures | `data/captures/*` | Sensitive artifacts | Exclude by default. Allow explicit encrypted opt-in with item count and size shown before backup. |
| Runtime logs | `logs/*` and launcher-specific logs | Sensitive support artifacts | Exclude by default; optional encrypted support bundle with bounded retention. Launcher logs currently outside the runtime contract must be reconciled. |
| PID files, temporary audio, uploaded temporary images | launcher directories and OS temp | Temporary state | Never back up or restore. Clean stale artifacts safely. |
| Working context, thought store, conversation selection, pending confirmations | process/session memory | Temporary state | Do not restore. A restart clears pending authority and confirmations. |
| Analysis documents | session state | Temporary unless explicitly exported | Do not treat as durable operating state. |
| Static registries, capability locks, connector manifests, generated runtime docs | application/repository files | Replaceable application truth | Never source these from a user backup. The installed version supplies them. |

### Evidence map

The inventory above was traced from current-main writers and path resolvers, principally:

- `nova_backend/src/utils/persistent_state.py` and `nova_backend/src/nova_config.py` for runtime-root resolution;
- `nova_backend/src/memory/*`, `profiles/user_profile_store.py`, `personality/tone_profile_store.py`, `settings/runtime_settings_store.py`, `policies/atomic_policy_store.py`, `patterns/pattern_review_store.py`, and `tasks/notification_schedule_store.py` for portable and operational JSON/JSONL stores;
- `nova_backend/src/ledger/writer.py`, `trust/receipt_store.py`, and `usage/provider_usage_store.py` for audit and accounting truth;
- `nova_backend/src/openclaw/agent_runtime_store.py`, `envelope_store.py`, and `execution_memory.py` for OpenClaw state;
- `nova_backend/src/connections/connections_store.py` and `connectors/google_workspace/credential_vault.py` for plaintext provider keys, connection metadata, and DPAPI credentials;
- `nova_backend/src/goals/goal_store.py` and `executors/story_tracker_executor.py` for state that currently bypasses the shared runtime root;
- `nova_backend/src/executors/news_synthesis_cache.py`, `perception/screen_capture.py`, `llm/llm_manager.py`, and launcher scripts for derived, sensitive, model-trust, log, PID, and temporary state;
- `nova_backend/src/websocket/session_handler.py`, `working_context/context_store.py`, `conversation/thought_store.py`, and analysis-document handling for session-only state;
- `installer/README.md` and `scripts/start_daemon.py` for installed-machine paths and launcher behavior.

Observed store behavior also informs the decision: the shared JSON helper writes through a temporary file and atomic replacement, while the shared lock registry is process-local. Several authoritative store readers catch broad exceptions and return default or empty state. Goals and story tracking have separate atomic-write implementations and repository-relative defaults. The ledger independently appends, flushes, and calls `fsync`.

## Behavioral configuration contract

Portable configuration consists of supported user choices stored through Nova: profile and tone preferences, location/units, setup mode, provider-routing preference, usage budget, assistive mode, notification policy, and user-set permission preferences. Restore applies these only after validation against the target build's capability registry and locks.

Machine-specific configuration includes `NOVA_RUNTIME_DIR`, `LOCALAPPDATA`, `NOVA_HOST`, `NOVA_PORT`, Ollama endpoints and model availability, Piper/model paths, calendar paths, browser/application paths, and performance/time-out tuning. It is recreated during setup or explicitly reselected.

Secret configuration includes API keys, bridge tokens, provider tokens, and OAuth credentials. Raw `.env` files and environment-variable dumps are never backup inputs. Re-creatable defaults and diagnostic overrides are not restored.

## Authority and consistency invariants

1. Memory identities, tombstones, and supersession links must remain internally consistent inside each memory store.
2. Capability locks and the target application registry outrank restored permission preferences. Restore cannot grant authority.
3. Pending confirmations, approval grants, and interrupted executions never survive as executable authority.
4. Restored schedules and OpenClaw state start paused until target-time, policy, capability, and provider checks pass.
5. Ledger order is immutable. A restore records a new recovery boundary rather than editing historical entries.
6. A backup represents one quiesced state generation. It must not mix files captured before and after a mutation.
7. Secrets, health probes, caches, and external source files are not authoritative substitutes for user state.
8. A failed migration or restore leaves the previous active root untouched and usable.
9. `openclaw_envelopes.json` and `openclaw/agent_runtime.json` form one restore group because runtime records reference envelope lifecycle by `envelope_id`. They are validated and activated together.
10. Quick-correction consumption state is authoritative: restore must not turn a consumed correction into an unconsumed correction or replay it.
11. No process or store object may survive a generation activation with a cached path. Every writer stops before activation and all stores resolve paths again after restart.

No current user mutation requires an atomic transaction across separate authoritative stores. Where one action updates operational state and appends a ledger receipt, the implementation must use stable operation IDs and reconciliation so an interrupted second write is visible. It must not claim that two independent file writes are one transaction.

## Storage and snapshot decision

File-backed storage remains the beta architecture. Each mutable JSON or rewritten JSONL store must use schema validation, integrity metadata, and explicit corruption failure. A write may be acknowledged only after the complete candidate bytes have been written through a write-through handle, the handle has received a durable flush (`fsync` or Windows `FlushFileBuffers`), and a crash-recoverable commit record has also been durably flushed. The implementation must use a tested per-store two-slot or write-ahead/journal protocol on Windows so startup can distinguish the last complete commit from a torn candidate. A rename or replace operation alone is not accepted as proof of metadata durability. Append-only JSONL writes must flush and durably sync before acknowledgement, and rewritten JSONL files follow the same recoverable commit protocol as JSON. Silent `except Exception -> empty/default state` behavior is prohibited for authoritative and portable state because it converts corruption into apparent data loss.

Backup, restore, migration, and repair use a Nova-owned maintenance coordinator:

1. Acquire the OS-visible interprocess lock at `control\maintenance.lock`, outside all replaceable generations.
2. Put Nova into maintenance mode and stop new mutations and scheduled work.
3. Flush and close active writers, stop the runtime process, and record the current state generation. No writer or cached store path survives this boundary.
4. Validate every included store and copy it into `control\staging\<operation-id>`.
5. Build and hash a versioned manifest.
6. Encrypt the completed artifact before it leaves staging.
7. For backup-only work, restart the runtime against the unchanged selected generation after snapshot completion or clean abort. Restore and migration follow the activation protocol below.

External tools must not mutate live Nova state. A second Nova process must refuse mutation while the maintenance lock is held.

For generation activation, the coordinator installs the fully validated generation at `generations\<generation-id>` and verifies its manifest in place. Each activation slot contains a monotonically increasing sequence number, generation ID, manifest hash, and integrity check. The coordinator writes the inactive slot completely through a write-through handle and calls `FlushFileBuffers` before closing it; it never depends on directory rename as the activation commit. Startup reads both slots and selects the highest-sequence slot whose record and referenced generation fully validate. If the newest slot is torn, missing, corrupt, or references an invalid generation, startup deterministically falls back to the prior valid slot and records the failed activation for inspection.

The maintenance lock remains held while old writers stop, the new slot is committed, and the runtime restarts. On restart, every store re-resolves the selected generation rather than retaining a concrete path from the prior process. Startup validates the selected generation and its cross-store groups before mutation or scheduled work becomes available. Only then may the coordinator release maintenance mode. If startup validation fails, the coordinator stops the failed process and restarts against the previous valid slot.

## SQLite decision

SQLite is rejected for the beta durability lane. Current-main evidence does not justify migration cost or the new failure modes of a broad transactional conversion. Reconsider SQLite only if implementation evidence demonstrates at least one of these needs: concurrent writers, a real cross-store atomic invariant that reconciliation cannot satisfy, indexed durable queries that file stores cannot meet, or online snapshots that cannot use bounded maintenance mode.

If such evidence appears, open a separate reviewed migration decision naming the exact tables and invariants. Credentials, captures, logs, caches, models, and large artifacts remain outside SQLite.

## Backup and export boundaries

A recovery backup restores Nova's durable operating state for the original installation profile when available. It contains portable user state, audit/operational state, supported portable configuration, schema/version metadata, and—only when explicitly selected—machine-bound DPAPI blobs. Inclusion never promises credential recovery: restore must test each blob with the current DPAPI context. An undecryptable blob is quarantined and reported as reconnect-required without blocking restoration of non-secret state.

A portable backup moves user state to another machine or Windows identity. It excludes all raw secrets and requires provider reconnect. It restores schedules and unresolved operational state paused. It may include prior-device ledger history with a clear provenance boundary.

Both backup types require authenticated encryption with a user-controlled passphrase or recovery key. The manifest includes product version, backup format version, per-entry schema version, path-independent logical store IDs, sizes, hashes, timestamps, source device identity hash, inclusion choices, and encryption parameters. Users see the inclusion categories before creation.

Export remains separate. It produces human-readable user information and does not promise restorable operating state. Memory export preserves deleted/superseded evidence as already required by #406. Future profile, project, or selected-history exports require their own product decisions.

## Restore, migration, corruption, and rollback

Restore never writes directly over the active generation. It decrypts into control-plane staging, verifies authentication and every manifest hash, validates all schemas and cross-store invariants, computes a restore plan, and requires explicit user confirmation. It then installs the fully prepared generation under `generations` and commits the inactive activation slot while maintenance mode is active. The previous valid slot and generation remain available for deterministic fallback and rollback until the selected generation passes startup validation.

Partial restore is allowed only for explicitly independent logical groups. It reports every included, skipped, incompatible, and reconnect-required group. It never reports success for a partially activated group. Audit/operational state cannot be cherry-picked in a way that creates false execution history.

OpenClaw envelope lifecycle and agent runtime are one indivisible partial-restore group. Before activation, every `envelope_id` reference in active, recent, delivery, or other retained agent-runtime records must resolve to a compatible restored envelope. Missing, duplicate, or contradictory lifecycle records reject that group and preserve it in quarantine for inspection; they are never silently dropped or synthesized. OpenClaw execution memory is advisory and may be restored separately only after validating that it cannot grant authority or create executable lifecycle state.

Quick corrections require conservative replay protection. Restored records remain available as evidence, including their original `consumed` values, but restored `consumed: false` records are not automatically injected after rollback or restore. They may become eligible only when a stable identity or canonical record digest can be reconciled against newer surviving consumption evidence. Current pre-ID or ambiguous records are quarantined from injection and reported for inspection; the restore path does not invent IDs or launch a correction-ID migration. A consumed record always remains consumed when either generation records it as consumed.

Existing source-tree and repository-relative state migrates once into the canonical root. Migration inventories both source and target, refuses ambiguous dual ownership, stages and validates the result, records provenance, and leaves the source untouched until activation succeeds. When both locations contain divergent authoritative data, migration stops for explicit resolution.

Corrupt authoritative state causes a visible safe failure. Nova preserves the original bytes, identifies the affected logical store, disables dependent mutation, and offers validated restore or bounded repair. It must not silently initialize an empty replacement. Corrupt caches are discarded and rebuilt. Corrupt optional captures/logs are isolated without blocking unrelated core state.

## Privacy and threat model

Backups must resist accidental cloud-sync disclosure, local unauthorized access, stolen media, ransomware collection, and inspection of personal content in captures or logs. Authenticated encryption is mandatory before a backup artifact reaches its selected destination. Passphrases and recovery keys are never stored inside the artifact or live state root.

Raw provider secrets, environment dumps, captures, logs, caches, temp files, and support artifacts are excluded by default. Optional sensitive artifacts show category, count, and size before inclusion. Backup creation and restore write redacted audit events without secret values, passphrases, or content hashes that expose personal data.

## Proposed durability implementation dependency order — non-authorizing

1. Canonical root and logical store registry, including migration detection for goals, story state, launcher logs, and existing runtime-root layouts.
2. Corruption-safe readers for authoritative and portable stores; preserve evidence and fail visibly.
3. Stable control plane, interprocess maintenance lock, mutation quiescence, and state validation.
4. Versioned manifest and consistent local snapshot staging.
5. Authenticated encryption and explicit recovery/portable inclusion policies.
6. Staged restore, target-build validation, paused operational activation, and rollback.
7. Restart, crash, corruption, migration, cross-identity, and no-silent-loss proof.

Each item would be a separately reviewable bounded lane if separately authorized. This dependency order and #408 acceptance do not authorize any implementation lane.

## Non-goals

- No SQLite migration in #408.
- No backup/restore code in the decision PR.
- No automatic duplicate repair or identity rewriting.
- No restoration of pending authority, approvals, or interrupted execution.
- No Google/provider, Continuity, voice, capability, OpenClaw, or broad UI expansion.
- No telemetry or public-beta work.

## Acceptance consequence

After exact-head review, owner acceptance, and merge, #408 can close as a decision gate. No implementation lane opens automatically. A separate owner-reviewed priority lock or implementation warrant must explicitly authorize the first bounded durability lane and name its scope. Any implementation that changes this contract requires a new reviewed decision rather than an incidental code choice.
