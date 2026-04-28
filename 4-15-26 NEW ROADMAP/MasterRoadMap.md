# Nova – Final Definitive Audit, Roadmap & Operating System (2026-04-15)

**Status:** This document is **frozen**. It is the strategic baseline and long-term plan captured on 2026-04-15, not the authoritative live-state document after that date.

For current roadmap truth, use these instead:

```text
4-15-26 NEW ROADMAP/CURRENT_PRIORITY_OVERRIDE_2026-04-27.md
4-15-26 NEW ROADMAP/NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md
4-15-26 NEW ROADMAP/BackLog.md
docs/current_runtime/
```

`Now.md` is now a superseded sprint-notes file and should not be used as the active priority source.

---

## Second Pass: Regression Check Complete

A thorough second pass compared the merged document against all source inputs and the live repository state. **Zero regressions found.** Every critical gap, honest claim, and roadmap item from both audits is preserved and correctly positioned. The ecosystem and operations sections are integrated without contradiction. The document is now **strategically complete** and ready to serve as a static reference.

---

## Executive Summary

> **Historical current-state baseline**
> The current-state claims in this section reflect the repository as audited on 2026-04-15.
> Later implementation work may have changed capability counts, packaging status, and live mutation support.
> For live status, see `CURRENT_PRIORITY_OVERRIDE_2026-04-27.md`, `NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md`, `BackLog.md`, `docs/current_runtime/`, and current capability verification docs.

Nova is **real, architecturally coherent, and trust‑first**:
- Live governed execution spine (`GovernorMediator → CapabilityRegistry → ExecuteBoundary → NetworkMediator → LedgerWriter`)
- 25 live capabilities — 16 read-only (9 local + 7 network: research, news, weather/calendar snapshot, memory review, second-opinion, screen analysis, etc.), 6 local-device controls (open website, speak, volume, media, brightness, open file/folder), and 3 persistent-change (screen capture, story tracker, memory governance). **Zero external-effect capabilities at audit time** (no email send, no calendar write, no outbound mutations).
- Memory layer with confirmation, append‑only ledger, runtime‑doc drift check
- 234 test files vs 247 source files (~1:1) – real discipline

**But Nova is not yet a product.**  
A stranger cannot install and use it without developer skills. The UI feels like a cockpit (10‑item nav, 7 widgets before first message, token budget bar). Despite "operator" language, **no live capability wrote to an external system at audit time** — what existed was read-only surfaces plus local-device controls. No email send, no calendar write, no file edits, no real-world action beyond the local machine.

**Documentation truthfulness is mixed:** core architecture docs are honest; product‑level promises ("calm presence", "operator", "voice live") are **not yet fulfilled** by the code.

**The gap is not intelligence – it is distribution, simplicity, one real mutation, a retention loop, appliance‑grade trust & ownership, and ecosystem/support readiness.**

This document provides a verified gap analysis and a tiered, actionable roadmap. **It also includes the operating rules to prevent roadmap inflation and sustain real progress.**

---

## 1. What Is Real (Confirmed from Live Repo)

| Area | Evidence | Verdict |
|------|----------|---------|
| Governance spine | All five core files present | ✅ Strong |
| Runtime‑doc closure | Drift check script and doc present | ✅ Excellent |
| Memory layer | Full CRUD with confirmation | ✅ End‑to‑end |
| Second‑opinion review | Advisory lane without execution authority | ✅ Differentiator |
| Test coverage | 234 test files | ✅ Real discipline |
| 25 capabilities | 16 read-only + 6 local-device + 3 persistent-change; zero external effects | ✅ Live, but no external mutation lane |
| Two hot‑path files | `brain_server.py` (3571 lines), `session_handler.py` (3821 lines) | ⚠️ Refactor debt |
| Frontend duplication | Two frontend trees | ⚠️ Maintenance hazard |
| Docs sprawl | 120 design docs across 12 phase folders | ⚠️ Drag multiplier |
| Installer / CI / pyproject.toml | **Not present at audit time** | ❌ Critical gap |
| OAuth / mutation | **Not present** | ❌ Critical gap |
| Backup / uninstaller / offline | **Not present** | ❌ Gap |

---

## 2. Critical Gaps (Ranked by Impact)

1. **No installer** – non‑developer cannot try Nova.
2. **No external-write capability at audit time** — "operator" label unearned (Nova had local-device controls but no way to send, create, or change anything outside the machine).
3. **UI overload** – feels like a cockpit, not calm.
4. **Two oversized hot‑path files** – refactor debt.
5. **Frontend duplication** – maintenance hazard.
6. **Docs drag** – slows execution.
7. **Poor public entry** – no GitHub metadata or 60‑second install path.
8. **No distribution channel** – installer alone doesn't bring users.
9. **No user support model** – friction compounds.
10. **No security update process** – trust erodes over time.
11. **No storage lifecycle policy** – local bloat.
12. **No beta program or success metrics** – hard to know if it's working.

---

## 3. Documentation Truthfulness (Code vs. Docs)

✅ **Honest:** governed path, 25 capabilities (16 read-only, 6 local-device, 3 persistent-change), append‑only ledger, test count, memory layer.

⚠️ **Overstated:** "calm presence" (UI is busy), "operator" (no mutations), "voice live" (preview), installation instructions (missing model fetch).

❌ **Needs manual verification:** mutation flagging, governor enforcement, second‑opinion isolation, drift check pass.

**Recommendation:** Run `scripts/generate_runtime_docs.py --check` and `pytest tests/runtime_auditor/`.

---

## 4. Historical Merged Roadmap

This section is historical baseline, not the active build order. For current active sequencing, use `NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md`.

**Original sequence principle:**
1. **Tier 1** – Unlock try‑ability
2. **Tier 2** – Deliver one real mutation
3. **Tier 2.5** – Add reliability & ownership
4. **Tier 3** – Reduce maintenance tax
5. **Tier 4** – Establish ecosystem & operations

### Tier 1 – Immediate (Week 1‑4)
*Goal: Non‑developer installs and runs in 5 minutes.*

- 1.1 One‑click installer (Windows + macOS) with model fetch
- 1.2 Simplify README + GitHub metadata (remove outdated claims)
- 1.3 Reduce UI overload (collapse nav, hide widgets, remove token bar)
- 1.4 Add `pyproject.toml` + CI
- 1.5 Minimal distribution landing page with email waitlist

### Tier 2 – Product Breakthrough (Week 5‑8)
*Goal: Nova can complete one real‑world action daily.*

- 2.1 Ship `send_email_draft` (goal at audit time: one real outbound action)
- 2.2 Fix read‑only ceiling messaging (banner, rename "Agent" page)
- 2.3 Sharpen first‑use "magic moment" (default prompt to news)

### Tier 2.5 – Reliability & Ownership (Week 9‑10)
*Goal: Appliance‑grade trust.*

- 2.5.1 Offline capability awareness
- 2.5.2 Backup & restore (full system state)
- 2.5.3 Uninstaller
- 2.5.4 Log export (sanitised)
- 2.5.5 Resource limits (CPU, memory, time)
- 2.5.6 Version migration safety
- 2.5.7 Privacy modes & transparency dashboard

### Tier 3 – Long‑Term Health (Week 11‑14)
*Goal: Reduce maintenance tax.*

- 3.1 Split giant hot‑path files
- 3.2 Remove frontend duplication
- 3.3 Reduce docs sprawl + add accessibility baseline

### Tier 4 – Ecosystem & Operations (Week 15+)
*Goal: Sustainable distribution, support, security, and product health.*

- 4.1 Distribution plan (GitHub Releases + landing page)
- 4.2 User support model (Issue templates, in‑app report, Discord/GitHub Discussions)
- 4.3 Security maintenance policy (`pip-audit` in CI, OAuth rotation, advisory process)
- 4.4 Storage lifecycle policy (pruning, usage display, warnings)
- 4.5 Beta program & success metrics
- 4.6 Competitive positioning & "Why Nova Exists"
- 4.7 Experience quality principles (clarity, confidence, calmness)
- 4.8 Multi‑device sync direction (manual first)

---

## 5. Execution Controls & Success Criteria

### A. Product KPIs
- Time to first successful run: <5 minutes
- First useful response rate: >80%
- Weekly retained testers (non‑developer): ≥3 after Tier 2
- Mutation success rate: >95%
- User confusion reports: <1 per 10 sessions

### B. Definition of Done per Tier
- **Tier 1:** Clean Windows VM → double‑click installer → "tell me news" works in ≤5 minutes, no terminal opened. Landing page live.
- **Tier 2:** Email draft end‑to‑end works; user understands approval flow; ledger entry clear.
- **Tier 2.5:** Offline badge, backup/restore, uninstaller, log export, resource limits, migration, privacy toggles all work.
- **Tier 3:** No file >1000 lines; one frontend tree; contributor finds truth in ≤3 docs; accessibility baseline passes.
- **Tier 4:** Support templates live; security policy documented; storage lifecycle active; beta program running with defined success metrics; positioning clear.

### C. Non‑Regression Guardrails
- Governor boundaries intact
- Runtime truth docs authoritative
- Memory user‑controlled
- Existing 25 capabilities continue to work

### D. Retention Loop
- Default: morning news briefing + intelligence brief on Home page.

### E. Trust UX for Mutations
- Before execution: intent, scope, undo path, data use.
- After execution: ledger entry and clear "Done / Failed" message.

### F. Failure Experience Design
- User‑friendly messages for OAuth expired, network timeout, model unavailable, capability not allowed. Never raw stack traces.

### G. Performance Targets
- App startup <10s
- First response to "tell me news" <5s
- Email draft completion <10s

### H. Post‑Tier 2.5 Re‑evaluation Gate
Pause 1 week to answer: Are users returning? What do they request most? Is email valued? What confuses first‑time users? Did backup/restore work? Then decide next sprint.

---

## 6. Risk Assessment & Dependencies

| Risk | Probability | Mitigation |
|------|-------------|-------------|
| Installer complexity | Medium | Start with Windows `.exe` only; fallback to Docker. |
| OAuth security | Medium | Use `httpx.OAuth2`; store encrypted; provide "revoke" UI. |
| Splitting hot‑path files introduces regressions | High | Do **after** Tier 2.5; run full test suite + Playwright. |
| Lack of discoverability | Medium | Tier 1 includes landing page; Tier 4 formalizes distribution. |
| Security vulnerability in dependency | Medium | Tier 4 adds `pip-audit` and monthly check. |
| Unbounded storage growth | Medium | Tier 4 adds pruning policy. |

**Dependencies:**
- Tier 1 was intended to complete before Tier 2. If execution overlaps, `CURRENT_PRIORITY_OVERRIDE_2026-04-27.md` becomes the controlling document for sequencing.
- Tier 2 email originally assumed an OAuth library; later implementations may choose a narrower draft-only path first.
- Tier 2.5 backup requires stable serialisation format.
- Tier 3 refactors require full test suite.
- Tier 4 depends on having a user base.

---

## 7. What This Roadmap Does NOT Include (Deliberately)

- New phase folders
- Additional connectors beyond email
- Learning / fine‑tuning layers
- Mobile or remote access
- Voice wake‑word beyond "early preview"
- Trading or crypto capabilities
- Business model monetisation

These were distractions under the 2026-04-15 plan. Later future planning docs may cover some of them, but only the current priority override decides active work.

---

## 8. Operating System for Execution

This roadmap is comprehensive. The biggest risk now is **over‑planning and losing focus**. The following rules protect execution.

### 8.1 Change Control & Scope Discipline
- **No new Tier added** until current sprint is closed and reviewed.
- **New ideas go to `BackLog.md`**, not the active plan.
- **Weekly review only** – no mid‑week scope creep.
- **Emergency exceptions** require written justification (e.g., critical security flaw, breaking change in dependency).

### 8.2 Sustainable Cadence
- **Minimum weekly progress target:** 2–4 hours of focused work. Anything above is a bonus.
- **Low‑energy mode:** If a week is impossible, do one tiny thing (update a doc, run tests, reply to an issue) to maintain momentum.
- **Pause without guilt:** Taking a planned week off is fine; communicate it in the project log.
- **Prefer momentum over heroic bursts.** Bursts lead to burnout.

### 8.3 User Research Method (Beta Loop)
After each beta user session, ask **exactly these five questions**:
1. What was confusing?
2. What was valuable?
3. Would you use Nova again tomorrow?
4. What did you expect to happen that didn't?
5. What would make you recommend Nova to a friend?

Store answers in `user_feedback/YYYY-MM-DD-username.md`. This makes feedback actionable.

### 8.4 Emotional Wins Tracking
Keep a separate file `EMOTIONAL_WINS.md`. Log moments like:
- A user said "wow" or "that's cool"
- Nova remembered something useful from a past conversation
- A user trusted a mutation without hesitation
- Someone said the UI felt calm

This file exists to remind you **why** you're building Nova when the work gets hard. It's as important as the bug tracker.

### 8.5 Brand & Naming Standard
Decide once and stick to it:
- **Product name:** Nova
- **Repository / project name:** NovaLIS
- **Tagline (public‑facing):** *Governed local assistant with memory and transparent execution.*
- **Internal descriptor:** "the system" or "Nova"

Use this consistently across README, landing page, and documentation.

### 8.6 Initial Launch Plan (Lightweight)
When Tier 2.5 is complete and beta feedback is positive, announce:
- **Release post** on GitHub Releases and landing page blog.
- **2‑minute demo video** (Loom or similar) showing install → "tell me news" → draft email.
- **Post to 2–3 relevant communities:** r/LocalLLaMA, Hacker News Show HN, maybe a privacy‑focused forum.
- **Email the waitlist** from the landing page.
- **Changelog cadence:** Write a short, human‑readable changelog for each GitHub release.

### 8.7 Legal Basics (Lightweight)
When you collect emails (waitlist) or have a website:
- **Privacy policy:** State you only collect email for updates and never share it.
- **Terms of use:** Basic disclaimer that Nova is local software, use at your own risk.
- **License attributions:** Ensure all third‑party libraries are credited (automated tools can help).
- **Export compliance:** If you bundle a model with the installer, include a note about its origin and license.

These are not urgent for Tier 1, but add to `BackLog.md` for Tier 2.5 completion.

---

## 9. The Current Roadmap Files

Use these files now:

1. `CURRENT_PRIORITY_OVERRIDE_2026-04-27.md` — active owner priority.
2. `NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md` — clean human-readable roadmap.
3. `BackLog.md` — paused scopes and future follow-up work.
4. `docs/current_runtime/` — generated runtime truth.

This `MasterRoadMap.md` file is frozen historical baseline, not active sprint control.

---

## 10. Final Verdict

> Nova's governance spine, memory, and second‑opinion lane are production‑grade differentiators.  
> But the product is currently a **technical product not yet consumer‑ready** – a stranger cannot install and use it without developer skills.  
> **The gap is not intelligence—it is installation, one real mutation, UI calm, a retention loop, appliance‑grade trust & ownership, ecosystem readiness, and execution discipline.**

**If you execute Tier 1, Tier 2, and Tier 2.5, Nova becomes a real, trustworthy product.** The operating rules in Section 8 ensure you ship instead of planning forever.

**One sentence to remember:**
*Stop designing phases; start shipping an installer, one email draft, backup, uninstaller, offline awareness, and a support channel—then measure whether users return.*

This final verdict reflects the 2026-04-15 audit baseline. Current active work is governed by the current priority override and consolidated roadmap.

---

## Appendix: Files to Change by Tier

| Tier | Files to create/edit | Lines estimate |
|------|----------------------|----------------|
| 1.1 | `installer/windows/*.iss`, `scripts/fetch_models.py`, `scripts/start_daemon.py` | 400 |
| 1.2 | `README.md`, `docs/INTRODUCTION.md`, `docs/ARCHITECTURE.md` | 200 |
| 1.3 | `index.html`, `dashboard-config.js` | 150 |
| 1.4 | `pyproject.toml`, `.github/workflows/ci.yml` | 100 |
| 1.5 | Landing page (HTML/CSS) | 100 |
| 2.1 | `send_email_draft` implementation, draft-open flow, integration test | 800 |
| 2.2 | `dashboard-control-center.js`, `CURRENT_RUNTIME_STATE.md` | 50 |
| 2.3 | `index.html` (first prompt), `intro` page tour | 100 |
| 2.5.1 | `connection_monitor.py`, UI offline badge | 200 |
| 2.5.2 | `backup.py`, `restore.py`, Settings UI | 400 |
| 2.5.3 | Uninstaller script (part of installer) | 100 |
| 2.5.4 | `log_export.py`, Settings UI | 150 |
| 2.5.5 | `resource_limiter.py`, capability wrapper | 200 |
| 2.5.6 | Migration scripts for each version | 300 |
| 2.5.7 | Privacy mode toggles in Settings, Trust page update | 150 |
| 3.1 | `src/routing/*.py`, `src/api/*.py`, delete from old files | 2000 (refactor) |
| 3.2 | Delete `Nova-Frontend-Dashboard/` | 0 |
| 3.3 | Move folders, create `docs/decisions/`, `docs/retired/`, accessibility fixes | 150 |
| 4.x | Issue templates, security policy, storage pruning, beta program docs, positioning copy | 400 |

**Total new code (excluding refactor): ~3650 lines.**  
**Total refactor: ~2000 lines (deletions + moves).**

**Cadence note:** Section 8.2 sets sustainable pace at 2–4 focused hours/week.
5650 lines of production-grade code (installer, dual-provider OAuth, backup,
uninstaller, resource limiter, migrations, accessibility) at that cadence is
optimistic. Realistic envelope is 24–32 weeks at 2–4 hrs/week, or 16–18 weeks
at 5–8 hrs/week. Pick the cadence; the timeline follows. Do not treat the
16–18 week figure as a commitment under Section 8.2's low-energy rule.

---

*Audit completed and verified against live repository 2026-04-15.*  
*This document is frozen historical baseline. Current active roadmap is `NOVA_CONSOLIDATED_ROADMAP_2026-04-28.md`.*
