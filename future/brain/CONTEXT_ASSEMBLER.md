# Brain Context Assembler

Defines how NovaLIS should assemble context for reasoning without becoming uncontrolled or bloated.

---

## Core Principle

> Context must be explicit, minimal, and relevant. More context is not always better context.

---

## Inputs

Possible inputs:

- user message
- session topic
- last intent family
- explicit memory
- recent receipts
- domain records (market, workflows)
- approved strategy rules
- capability contracts
- runtime constraints

---

## Assembly Rules

- prefer recent over old
- prefer explicit memory over inferred
- include constraints before suggestions
- include failures when relevant
- exclude unrelated domains
- cap total size

---

## Output Structure

```text
ContextBundle
- user_intent
- topic
- constraints
- relevant_memory
- domain_records
- recent_receipts
- confidence_notes
```

---

## Exclusion Rules

Do not include:

- raw logs
- full history dumps
- irrelevant domain data
- stale or conflicting data without flagging

---

## Safety Rule

Context must never:

- override governance
- introduce hidden authority
- inject credentials
- fabricate data

---

## Future Integration

This feeds:

- Brain reasoning
- plan generation
- trust surface

It does not feed:

- execution authority
