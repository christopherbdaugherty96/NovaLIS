# Second Brain Health Check Contract

Status: future planning / not runtime truth.

The second-brain health check is the first safe operational surface because it observes and reports. It should not repair files until a later reviewed repair mode exists.

---

## Command Shape

Possible future commands:

```text
python -m nova_backend.src.second_brain.health --vault second_brain
python scripts/second_brain_health.py --vault second_brain --json
```

Exact command names are future implementation details.

---

## Required Checks

The health report should include:

```text
missing_frontmatter
invalid_frontmatter_schema
duplicate_entry_id
broken_wikilink
missing_relationship_target
missing_source_ref
promoted_without_review
synthesis_marked_runtime_truth
non_authorizing_missing
non_authorizing_false
capability_log_implies_permission
ledger_ref_missing_or_unresolved
stale_without_successor
index_drift
orphan_note
event_sequence_gap
event_duplicate_idempotency_key
event_scope_missing
event_entity_subject_missing
possible_secret_detected
credential_like_value
private_key_detected
env_file_indexed
cloud_export_blocked
embedding_blocked_by_sensitive_data
redaction_required
quarantine_required
template_placeholder_id
template_placeholder_hash
fixture_hash_used
proof_relationship_missing_reference
stale_review_target
tombstone_missing_previous_hash
tombstone_missing_reason
```

---

## Severity Levels

```text
info
warning
error
critical
```

Critical findings:

```text
non_authorizing_false
capability_log_implies_permission
synthesis_marked_runtime_truth
promoted_without_review
event_sequence_gap
event_scope_missing
event_entity_subject_missing
private_key_detected
env_file_indexed
proof_relationship_missing_reference
stale_review_target
tombstone_missing_previous_hash
```

These must block any claim that the second brain is healthy.

---

## Report Shape

```json
{
  "schema_version": 1,
  "checked_at": "2026-05-18T00:00:00Z",
  "vault_root": "second_brain",
  "entry_count": 0,
  "relationship_count": 0,
  "event_count": 0,
  "tombstone_count": 0,
  "redaction_required": false,
  "export_allowed": false,
  "embedding_allowed": false,
  "findings": [
    {
      "severity": "error",
      "code": "missing_frontmatter",
      "path": "second_brain/knowledge/example.md",
      "entry_id": "",
      "message": "Knowledge entry is missing required frontmatter."
    }
  ],
  "healthy": false
}
```

---

## Sensitive Data Lifecycle

Sensitive-data findings should drive concrete gates:

```text
possible_secret_detected -> warning, exclude from export until reviewed
credential_like_value -> error, block export and cloud routing
private_key_detected -> critical, quarantine and block export / embedding
env_file_indexed -> critical, quarantine and block export / embedding
redaction_required -> error, derived snapshots must redact or omit affected content
embedding_blocked_by_sensitive_data -> warning or error, do not create vector chunks
```

Health output should say what is blocked. It should not silently repair or delete source files.

---

## Scaffold / Fixture Handling

The future vault scaffold may contain example notes with fixture hashes such as repeated digits.

Health checks should report:

```text
template_placeholder_id -> template placeholders are still present in a non-template note
template_placeholder_hash -> REPLACE_WITH_SHA256_HASH is present outside templates
fixture_hash_used -> schema-valid scaffold hash is present in a promoted/reviewed non-template note
```

`fixture_hash_used` should be at least a warning in scaffold mode and an error outside scaffold/test fixtures.

---

## Non-Authorizing Invariant

The health check may say:

```text
healthy / not healthy
index matches / drift detected
safe for read-only retrieval / unsafe for retrieval
```

It must not say:

```text
approved for execution
authorized
capability enabled
certified
locked
```

Health is not authority.
