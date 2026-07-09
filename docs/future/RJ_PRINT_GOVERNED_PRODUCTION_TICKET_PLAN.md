# RJ Print — Governed Production Ticket System (Phase 1)

Status: future / product design; not implemented runtime truth
Date: 2026-06-03
Scope: Governed production ticket workflow from Shopify order to
human-reviewed print-ready ticket

Generated runtime truth, code, tests, and proof artifacts win if they
conflict with this note.

---

## Purpose

A production ticket is a structured, inert data object that describes
what needs to be manufactured for a Shopify order. It is the bridge
between "customer bought something" and "human decides to start a
print." Nova creates the ticket. A human reviews and acts on it.

This design covers Phase 1 only: Shopify order → production ticket.
No printer control, no fulfillment writes, no automatic chaining.

---

## Non-Goals

This design does not authorize:

- Printer control, printer queuing, or any physical execution
- Shopify writes (order updates, fulfillment, refunds, inventory changes)
- Automatic order fulfillment or shipping label generation
- Automatic chaining from ticket creation to any downstream capability
- Hidden background execution or autonomous agent loops
- New capability locks or changes to existing capability locks
- Any action that bypasses GovernorMediator

This document is planning only.

---

## Governance Invariants

A production ticket is not a print command.

Creating a ticket does not authorize printing.

No capability may start a printer in this phase.

Cap 65 may read Shopify data.

Cap 62 may reason about production.

The new production-ticket capability may create local persistent
tickets from pre-fetched inputs. It does not call Cap 65 or Cap 62
internally.

All real actions pass through GovernorMediator → Governor →
CapabilityRegistry → SingleActionQueue → Executor.

Each step in the workflow is a separate governed invocation. No
capability chains. No multi-action requests.

---

## Workflow

```text
Governed invocation A:
  Cap 65 reads Shopify order data (read-only network)
        ↓
Governed invocation B (optional):
  Cap 62 reasons about production requirements (advisory only)
        ↓
Governed invocation C:
  New cap creates local persistent ticket from provided inputs
        ↓
Ticket visible in Trust UI
        ↓
Human reviews ticket
        ↓
Human decides next step (not Nova)
```

Each governed invocation is independent — its own capability check,
budget gate, and ledger entry. No automatic progression. The new
capability's executor receives pre-fetched order data and optional
reasoning as inputs; it does not call Cap 65, Cap 62, or any other
capability internally.

---

## Capability Metadata Proposal

```text
ID:                  TBD (next available after 65)
Name:                shopify_production_ticket
Status:              active
Phase Introduced:    TBD (follows current registry phase convention)
Risk Level:          low
Authority Class:     persistent_change
External Effect:     false
Data Exfiltration:   false
Cost Posture:        free_tier
Requires Confirm:    false
Reversible:          true
```

### Authority Class Rationale

`persistent_change` because creating a ticket writes a durable local
record to disk. Existing capabilities that persist local data
(story_tracker_update, screen_capture, memory_governance) use this
authority class. `read_only_local` is reserved for capabilities that
return data without writing persistent artifacts.

The ticket may be written only to Nova-local ticket storage. The
ticket is not an approval, not a print command, not a fulfillment
action, and not a Shopify mutation. It does not modify Shopify,
printers, or any external system. It does not send data outside the
device.

This capability is NOT budget-gated because it consumes no external
or metered resources. Cap 65 (Shopify read) and Cap 62 (DeepSeek
reasoning) handle their own budget enforcement in their own governed
invocations before this capability is called.

---

## Ticket Schema

```json
{
  "ticket_id": "PT-2026-0001",
  "created_at": "2026-06-03T14:22:00Z",
  "source": "shopify_order",

  "order": {
    "shopify_order_id": 1043,
    "shopify_order_number": "#1043",
    "customer_name": "Jane Doe",
    "order_date": "2026-06-03T13:15:00Z",
    "line_items": [
      {
        "product_title": "12oz Koozie",
        "variant_title": "Black",
        "sku": "KOOZIE-12OZ-BLK",
        "quantity": 2
      }
    ]
  },

  "production": {
    "suggested_file": "koozie_v2.3mf",
    "estimated_material_grams": 180,
    "material_type": "PLA",
    "estimated_print_time_minutes": 262,
    "color": "Black",
    "notes": ""
  },

  "reasoning": {
    "provider": "DeepSeek",
    "capability_id": 62,
    "summary": "Standard koozie order. No custom artwork. File matches SKU.",
    "risks": [],
    "recommendations": []
  },

  "status": "awaiting_approval",
  "status_history": [
    {
      "status": "created",
      "at": "2026-06-03T14:22:00Z",
      "by": "nova"
    }
  ],

  "approval": {
    "approved": false,
    "approved_by": null,
    "approved_at": null
  }
}
```

### Schema Rules

- `ticket_id` is a local sequential ID, not a Shopify ID
- `status` is one of: `created`, `awaiting_approval`, `approved`,
  `rejected`, `expired`
- `approval.approved` can only be set by a human action, never by
  Nova or DeepSeek
- `reasoning` section is advisory only — it never contains executable
  tool calls, confirmed params, or dispatchable actions (enforced by
  Cap 62 stripping)
- The ticket is immutable after creation except for status transitions
  and approval fields

---

## Executor Contract

### `ShopifyProductionTicketExecutor`

```text
Inputs (provided by caller, not fetched by executor):
  - order_data: normalized Shopify order data already retrieved
    through a prior Cap 65 governed invocation
  - reasoning: optional advisory reasoning already retrieved
    through a prior Cap 62 governed invocation
  - line_item_index: optional, defaults to all items

Steps:
  1. Validate order_data is present and well-formed
  2. For each line item, look up SKU → file mapping from local config
  3. Merge optional reasoning into production notes
  4. Construct ticket object
  5. Persist ticket to local ticket store
  6. Return ActionResult with ticket data for Trust UI

Must NOT:
  - Call Shopify (Cap 65 or ShopifyConnector directly)
  - Call DeepSeek (Cap 62 or DeepSeekBridge directly)
  - Call any printer or physical execution system
  - Internally dispatch any other capability
  - Mutate any external system
  - Auto-approve the ticket

Returns:
  - ActionResult.ok with ticket data on success
  - ActionResult.failure with clear reason on any step failure
```

### Fail-Closed Behavior

- If order_data is missing or malformed → ticket creation fails
- If reasoning is absent → ticket is created without reasoning
  section (degraded but safe — reasoning is advisory, not required)
- If SKU has no file mapping → ticket is created with
  `suggested_file: null` and a warning note

---

## DeepSeek's Role

DeepSeek (Cap 62) provides advisory production analysis:

- Production summary (standard vs custom, complexity estimate)
- Risk detection (unusual quantities, missing artwork, SKU mismatch)
- Material estimation (weight, type, color)
- Print time recommendations

DeepSeek does NOT:

- Start, stop, or control any printer
- Modify Shopify orders or inventory
- Approve or reject tickets
- Chain to any downstream capability
- Return executable tool calls (enforced by provider stripping)

---

## Local Data Storage

Tickets are stored locally in a JSON file or SQLite database at:

```text
nova_backend/data/production_tickets/
```

No tickets are sent to external systems. No ticket data leaves the
device unless a future capability with appropriate authority class
and governance is added.

---

## Trust UI Surface

The ticket should appear in the Trust Center as a new section:

```text
Production Tickets
  - Active tickets awaiting approval
  - Recently approved/rejected tickets
  - Ticket detail view with order info, production details,
    reasoning summary, and approve/reject buttons
```

The approve/reject buttons are human-only actions. Nova surfaces
the ticket; the human decides.

---

## SKU → File Mapping

A local configuration file maps Shopify SKUs to print files:

```json
{
  "KOOZIE-12OZ-BLK": {
    "file": "koozie_v2.3mf",
    "material": "PLA",
    "estimated_grams": 90,
    "estimated_minutes": 131,
    "color": "Black"
  },
  "KOOZIE-12OZ-WHT": {
    "file": "koozie_v2.3mf",
    "material": "PLA",
    "estimated_grams": 90,
    "estimated_minutes": 131,
    "color": "White"
  }
}
```

This file is manually maintained. Nova does not modify it.

---

## Future Phases (Out of Scope)

These are listed for context only. None are authorized by this design.

### Phase 2: Printer Queue

- Approved ticket → printer queue entry
- New capability with appropriate authority class
- Requires its own governance review

### Phase 3: Printer Assignment and Scheduling

- Multi-printer farm support
- Filament tracking
- Job scheduling and priority

### Phase 4: End-to-End

- Print completion → Shopify fulfillment
- Shipping integration
- Customer notifications

Each phase requires its own design doc, governance review, capability
registration, and test coverage before implementation.

---

## Implementation Sequence

```text
1. ✓ Design doc (this document)
2.   Review/audit doc for governance drift
3.   Registry proposal (add capability to registry.json)
4.   Executor scaffold (ShopifyProductionTicketExecutor)
5.   SKU config schema and loader
6.   Ticket store (local persistence)
7.   Trust UI section
8.   Tests (unit, governance boundary, adversarial)
9.   Runtime docs generation
10.  Drift check
```

---

## Governance Audit Checklist

Before implementation, verify:

- [ ] New capability does not grant printer control
- [ ] New capability does not write to Shopify
- [ ] New capability does not chain to other capabilities
- [ ] Ticket approval is human-only
- [ ] DeepSeek reasoning is stripped of tool calls before inclusion
- [ ] Ticket data stays local
- [ ] Executor imports no authority surfaces or other capability executors
- [ ] Tests cover governance boundaries
- [ ] Budget-gated set is not modified (this cap is local/free)
- [ ] Runtime docs regenerated and drift check passes
