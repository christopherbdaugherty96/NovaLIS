# Templates

Status: future vault templates / not runtime truth.

Use these templates for consistent frontmatter and review state.

Every template is non-authorizing. Replace placeholder IDs and hashes before validation.

## Placeholder Rules

Placeholders are allowed only in this folder.

Before moving a copied template into a knowledge folder:

```text
replace kb_REPLACE_ID
replace REPLACE_TITLE
replace REPLACE_WITH_SHA256_HASH
set created_at / updated_at
add source_refs when available
keep reviewed_by and reviewed_at blank until review
```

Promoted notes must not use placeholder or fixture hashes.
