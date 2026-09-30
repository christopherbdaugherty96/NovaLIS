# Auralis Public-Source Boundary

NovaLIS keeps only the Auralis material required to understand and test Nova's existing
technical behavior. Commercial strategy belongs in a private business workspace.

## Public-safe and retained

| Path | Classification | Reason |
| --- | --- | --- |
| `docs/design/AURALIS_TODAY_C1_DESIGN.md` | Public-safe technical design | Describes a bounded read-only Nova surface. |
| `docs/product/AURALIS_INTERFACE_PLAN.md` | Public-safe product/technical context | Describes interface boundaries without private operating data. |
| `docs/future/auralis_mock_leads/` | Public-safe synthetic fixtures | Clearly labeled mock data; no real clients. |
| `nova_backend/src/brief/auralis_seeds.py` | Public-safe source | Runtime implementation. |
| `nova_backend/src/brief/auralis_today.py` | Public-safe source | Runtime implementation. |
| `nova_backend/src/connectors/shopify_auralis_enrichment.py` | Public-safe source | Read-only governed connector implementation. |
| Corresponding `nova_backend/tests/` files | Public-safe tests | Synthetic verification of retained source. |

## Private-move recommended and removed from the public tree

The removed set covers `docs/business/`, the vault template's `03_BUSINESS/` area, the
`docs/future/auralis_digital/` workflow pack, and the Auralis pricing, funnel, intake,
commercial integration, website-services, operating-model, risk, and execution-plan documents
listed in `PUBLIC_HISTORY_REWRITE_PATHS_2026-09-30.txt`.

These files contain private commercial strategy, internal business operations, prospective
client workflows, sales/package planning, or future commercial positioning. Their removal does
not alter Nova runtime behavior or authorize any Auralis execution capability.

## Preservation

The original history remains in the local forensic mirror. The current-main copies are also
preserved in the private migration archive recorded in
`PUBLIC_EXPOSURE_REMEDIATION_PLAN_2026-09-30.md`. No external private-repository migration has
been performed.
