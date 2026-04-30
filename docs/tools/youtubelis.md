# YouTubeLIS Tool Folder

YouTubeLIS lives at `tools/youtubelis/`.

It is a planning-first content-production tool folder for turning YouTube video ideas into reviewable artifacts: angle, hook, outline, script, claim validation, scene plan, asset list, editing plan, and title/thumbnail options.

---

## Current Status

Current status: planning-only tool folder.

This is not yet a Nova runtime capability.

Do not claim YouTubeLIS has live governed execution, upload, publishing, account access, or background automation until those paths exist in code, pass tests, and are reflected by generated runtime truth.

---

## Allowed Current Use

- Content strategy
- Topic and angle planning
- Script structure
- Claim validation design
- Production planning
- Scene planning
- Packaging ideas
- Planning-run templates

---

## Blocked Current Use

- Uploading videos
- Publishing videos
- Account actions
- Purchases
- Deletions
- Background automation loops
- OpenClaw execution
- YouTube Studio control
- Claiming runtime capability status

---

## Integration Direction

The safe path is:

1. Keep `tools/youtubelis/` as docs and planning templates.
2. Build a planning-only module later under `nova_backend/src/tools/youtubelis/`.
3. Add tests for planning-only behavior.
4. Add connector package metadata as `status: design` only after a real module path exists.
5. Add a real capability only after the planning module is stable and the governance path is implemented.
6. Regenerate runtime docs only after runtime code changes exist.

---

## Governance Rule

Planning may be rich. Authority remains bounded.

Memory, prior runs, or documentation do not grant permission to publish, upload, purchase, or control accounts.

Future execution must go through Nova's governed action path and produce reviewable results.
