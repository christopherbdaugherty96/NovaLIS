# Graph Health

Status: future health map / not runtime truth.

The future health command should check:

```text
missing frontmatter
invalid schema
duplicate IDs
broken wikilinks
missing relationship targets
promoted entries without review metadata
synthesis marked as runtime truth
non_authorizing missing or false
capability logs implying permission
event sequence gaps
sensitive data findings
stale review targets
tombstones missing prior hash or reason
```

Critical findings must block any claim that the vault is healthy.
