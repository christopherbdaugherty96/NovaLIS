# Runbook - Health And Lint

Status: future vault runbook / not runtime truth.

The health command does not exist yet. This runbook records the intended checks for the future implementation.

---

## Health Modes

```text
scaffold mode: allows example fixture hashes, reports them as warnings
strict mode: fixture hashes and placeholders are errors outside templates
runtime mode: blocks retrieval/export/embedding on critical findings
```

---

## Required Checks

```text
schema validation
duplicate IDs
placeholder IDs outside templates
placeholder hashes outside templates
fixture hashes outside scaffold mode
broken wikilinks
missing typed relationship targets
promoted notes without review metadata
promoted notes without source_refs or ledger_refs
synthesis marked as runtime truth
non_authorizing missing or false
capability logs implying permission
sensitive data findings
event sequence gaps
tombstones missing prior hash or reason
```

---

## Expected Output

The future health report should say:

```text
healthy / not healthy
safe for read-only retrieval / unsafe for retrieval
export allowed / blocked
embedding allowed / blocked
redaction required / not required
```

It must not say:

```text
approved for execution
authorized
capability enabled
certified
locked
```
