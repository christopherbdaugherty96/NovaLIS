# NovaLIS Docs

This folder is the documentation home for NovaLIS.

Start with [docs/INDEX.md](INDEX.md). It routes readers by goal:

- product overview and first use
- runtime truth
- architecture and governance
- development and testing
- roadmap and planning
- archive context

## Authority Rule

If explanatory, historical, or design docs conflict with generated runtime truth, the generated runtime docs win.

The primary runtime truth source is [current_runtime/CURRENT_RUNTIME_STATE.md](current_runtime/CURRENT_RUNTIME_STATE.md).

## Main Doc Layers

- [product](product/) - product-facing explanations and positioning.
- [architecture](architecture/) - stable architecture entry points and diagrams.
- [current_runtime](current_runtime/) - generated runtime truth.
- [dev](dev/) - contributor setup, testing, and implementation guidance.
- [reference/HUMAN_GUIDES](reference/HUMAN_GUIDES/) - plain-language guide set.
- [PROOFS](PROOFS/) - implementation evidence and proof packets.
- [design](design/) - future direction and non-authorizing plans.
- [future](future/) - draft action plans and forward-looking proposals.
- [archive](archive/) - historical or superseded material.

## Obsidian Overlay

Nova also supports an Obsidian overlay at the repository root.

Use:

- `C:\Nova-Project` as the Obsidian vault root
- `_MOCs/` as the generated entry point
- `scripts/generate_runtime_docs.py` to refresh runtime docs and the overlay together

Source docs and source code stay as the canonical files. The overlay is generated on top for navigation, graph colors, and map-of-content notes.
