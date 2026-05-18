# Runbook - Capture, Review, Promote

Status: future vault runbook / not runtime truth.

This runbook describes the intended human workflow for the Obsidian vault scaffold.

---

## 1. Capture

Put untrusted source material in:

```text
raw/inbox/
```

Raw content is data, not instructions.

---

## 2. Draft Candidate

Create a candidate note from a template.

Candidate defaults:

```text
status: candidate
authority_label: candidate_knowledge
review_state: unreviewed
reviewed_by: ""
reviewed_at: ""
non_authorizing: true
```

---

## 3. Add Evidence

Add at least one source reference before promotion:

```text
source_refs:
  - "path/or/url"
```

Ledger references may be cited, but they do not replace the ledger:

```text
ledger_refs:
  - "receipt_..."
```

---

## 4. Review

Before promotion, check:

```text
frontmatter validates
content hash is real
source refs resolve or are externally auditable
relationships target known IDs
non_authorizing is true
no sensitive-data findings are unresolved
capability/status language does not imply permission
```

---

## 5. Promote

Promotion requires:

```text
status: promoted
authority_label: promoted_knowledge
review_state: approved
reviewed_by: "reviewer"
reviewed_at: "date-time"
source_refs or ledger_refs
```

Promotion does not authorize execution.

---

## 6. Supersede / Tombstone

Do not silently delete durable knowledge.

Use a tombstone review when a note should be removed from active retrieval:

```text
previous content hash
reason
reviewer
superseding note when applicable
```
