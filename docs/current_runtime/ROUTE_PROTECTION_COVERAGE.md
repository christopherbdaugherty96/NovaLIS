# ROUTE_PROTECTION_COVERAGE

Deterministic route protection coverage derived from allowlisted route modules and `src/utils/route_protection.py`.

This report is separate from the capability governance matrix. A capability can be governed while a non-capability HTTP route still needs its own local-only or token-gated boundary.

## Summary

- local_only: 47
- token_gated_remote: 1
- public: 2
- unclassified: 0

## Local-Only Prefixes

- `/api/goals` - Goal persistence is an operator-local planning surface.
- `/api/memory` - Memory endpoints read and mutate durable local memory.
- `/api/settings` - Settings endpoints read and mutate runtime configuration.
- `/api/trust` - Trust receipts expose local execution history.
- `/api/workspace` - Workspace endpoints expose local project context.
- `/api/openclaw/agent` - OpenClaw agent endpoints manage local runs and delivery state.
- `/api/openclaw/approve-action` - Approval stub state must not be remotely reachable.
- `/api/openclaw/bridge/status` - Bridge status exposes settings and connection state.
- `/api/profile` - Profile endpoints persist identity and mirror it into governed memory.
- `/api/live-screen` - Live-screen analysis accepts sensitive screen images.
- `/api/token/budget` - Token budget status exposes local provider usage.
- `/stt` - Speech-to-text accepts sensitive audio uploads.
- `/phase-status` - Phase status exposes runtime governance state.
- `/system/audit` - Runtime audit endpoints expose internal topology.

## Token-Gated Remote Prefixes

- `/api/openclaw/bridge/message`

## Route Table

| method | path | protection | source |
| --- | --- | --- | --- |
| GET | `/` | public | `nova_backend\src\api\workspace_api.py` |
| GET | `/api/goals` | local_only | `nova_backend\src\api\goals_api.py` |
| POST | `/api/goals` | local_only | `nova_backend\src\api\goals_api.py` |
| GET | `/api/goals/{goal_id}` | local_only | `nova_backend\src\api\goals_api.py` |
| PUT | `/api/goals/{goal_id}` | local_only | `nova_backend\src\api\goals_api.py` |
| POST | `/api/live-screen/analyze` | local_only | `nova_backend\src\api\live_screen_api.py` |
| GET | `/api/memory/context` | local_only | `nova_backend\src\api\memory_api.py` |
| GET | `/api/memory/export` | local_only | `nova_backend\src\api\memory_api.py` |
| GET | `/api/memory/nova` | local_only | `nova_backend\src\api\memory_api.py` |
| GET | `/api/memory/user` | local_only | `nova_backend\src\api\memory_api.py` |
| POST | `/api/memory/user` | local_only | `nova_backend\src\api\memory_api.py` |
| GET | `/api/memory/user/category/{category}` | local_only | `nova_backend\src\api\memory_api.py` |
| GET | `/api/memory/user/search` | local_only | `nova_backend\src\api\memory_api.py` |
| DELETE | `/api/memory/user/{entry_id}` | local_only | `nova_backend\src\api\memory_api.py` |
| POST | `/api/openclaw/agent/delivery/{delivery_id}/dismiss` | local_only | `nova_backend\src\api\openclaw_agent_api.py` |
| POST | `/api/openclaw/agent/goal` | local_only | `nova_backend\src\api\openclaw_agent_api.py` |
| POST | `/api/openclaw/agent/runs/cancel` | local_only | `nova_backend\src\api\openclaw_agent_api.py` |
| GET | `/api/openclaw/agent/status` | local_only | `nova_backend\src\api\openclaw_agent_api.py` |
| POST | `/api/openclaw/agent/templates/{template_id}/delivery` | local_only | `nova_backend\src\api\openclaw_agent_api.py` |
| POST | `/api/openclaw/agent/templates/{template_id}/run` | local_only | `nova_backend\src\api\openclaw_agent_api.py` |
| POST | `/api/openclaw/agent/templates/{template_id}/schedule` | local_only | `nova_backend\src\api\openclaw_agent_api.py` |
| POST | `/api/openclaw/approve-action` | local_only | `nova_backend\src\api\openclaw_agent_api.py` |
| POST | `/api/openclaw/bridge/message` | token_gated_remote | `nova_backend\src\api\bridge_api.py` |
| GET | `/api/openclaw/bridge/status` | local_only | `nova_backend\src\api\bridge_api.py` |
| GET | `/api/profile` | local_only | `nova_backend\src\api\profile_api.py` |
| POST | `/api/profile/identity` | local_only | `nova_backend\src\api\profile_api.py` |
| POST | `/api/profile/preferences` | local_only | `nova_backend\src\api\profile_api.py` |
| POST | `/api/profile/rules` | local_only | `nova_backend\src\api\profile_api.py` |
| GET | `/api/settings/connections` | local_only | `nova_backend\src\api\connections_api.py` |
| DELETE | `/api/settings/connections/all` | local_only | `nova_backend\src\api\connections_api.py` |
| DELETE | `/api/settings/connections/{provider}` | local_only | `nova_backend\src\api\connections_api.py` |
| POST | `/api/settings/connections/{provider}/key` | local_only | `nova_backend\src\api\connections_api.py` |
| POST | `/api/settings/connections/{provider}/test` | local_only | `nova_backend\src\api\connections_api.py` |
| POST | `/api/settings/model/confirm` | local_only | `nova_backend\src\api\settings_api.py` |
| GET | `/api/settings/model/status` | local_only | `nova_backend\src\api\settings_api.py` |
| GET | `/api/settings/runtime` | local_only | `nova_backend\src\api\settings_api.py` |
| POST | `/api/settings/runtime/assistive-mode` | local_only | `nova_backend\src\api\settings_api.py` |
| POST | `/api/settings/runtime/permissions` | local_only | `nova_backend\src\api\settings_api.py` |
| POST | `/api/settings/runtime/provider-policy` | local_only | `nova_backend\src\api\settings_api.py` |
| POST | `/api/settings/runtime/reset` | local_only | `nova_backend\src\api\settings_api.py` |
| POST | `/api/settings/runtime/setup-mode` | local_only | `nova_backend\src\api\settings_api.py` |
| POST | `/api/settings/runtime/usage-budget` | local_only | `nova_backend\src\api\settings_api.py` |
| GET | `/api/token/budget` | local_only | `nova_backend\src\api\settings_api.py` |
| GET | `/api/trust/receipts` | local_only | `nova_backend\src\api\trust_api.py` |
| GET | `/api/trust/receipts/summary` | local_only | `nova_backend\src\api\trust_api.py` |
| GET | `/landing` | public | `nova_backend\src\api\workspace_api.py` |
| GET | `/phase-status` | local_only | `nova_backend\src\api\audit_api.py` |
| POST | `/stt/transcribe` | local_only | `nova_backend\src\routers\stt.py` |
| GET | `/system/audit/runtime-truth` | local_only | `nova_backend\src\api\audit_api.py` |
| GET | `/system/audit/runtime-truth.md` | local_only | `nova_backend\src\api\audit_api.py` |

## Unclassified Routes

- None.
