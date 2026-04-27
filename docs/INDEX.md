# NovaLIS Documentation Index

Use this page to find the right document quickly. Runtime truth stays in generated docs; product and contributor docs should link to it rather than duplicate exact counts or hashes.

---

## Start Here

- [README](../README.md) - public overview and positioning.
- [Quickstart](../QUICKSTART.md) - install, start, and first commands.
- [Use cases](../USE_CASES.md) - practical workflows Nova can support.
- [Visual proof](product/visual_proof.md) - dashboard, trust, and report screenshots.
- [Introduction](reference/INTRODUCTION.md) - plain-language project introduction.

---

## Audits And Product Truth

- [NovaLIS Audit (2026-04-24)](audits/2026-04-24/NovaLIS_Audit_2026-04-24.md) - architecture, product readiness, launch assessment, and recommendations.
- [NovaLIS Wide Final Audit (2026-04-24)](audits/2026-04-24/NovaLIS_Wide_Final_Audit_2026-04-24.md) - wider final pass covering architecture, launch readiness, contributor readiness, and strategic execution.
- [NovaLIS Second-Pass Code Verification (2026-04-24)](audits/2026-04-24/NovaLIS_Second_Pass_Code_Verification_2026-04-24.md) - verifies prior audit claims against actual repo files and separates confirmed claims from unverified assumptions.
- [NovaLIS Third Final Read-Only Audit (2026-04-24)](audits/2026-04-24/NovaLIS_Third_Final_Readonly_Audit_2026-04-24.md) - final non-destructive pass focused on remaining risks, onboarding clarity, and future cleanup recommendations.
- [Session Update Log (2026-04-24)](audits/2026-04-24/SESSION_UPDATE_LOG_2026-04-24.md) - traceable record of what was completed in this session and what is recommended next.
- [NovaLIS Deep Second-Pass Code Audit (2026-04-25)](audits/2026-04-25/NovaLIS_Deep_Second_Pass_Audit_2026-04-25.md) - code-grounded pass reading actual source files, registry JSON, trust module, test suite, installer, and roadmap; surfaces capability verification gaps and trust module stub state at time of audit.
- [NovaLIS Final Confirmation Pass (2026-04-25)](audits/2026-04-25/NovaLIS_Final_Confirmation_Pass_2026-04-25.md) - confirms claims from prior audit passes against live repo state.
- [NovaLIS Third Deep Wide Audit (2026-04-25)](audits/2026-04-25/NovaLIS_Third_Deep_Wide_Audit_2026-04-25.md) - wide pass covering executors, tests, voice, connectors, security, and governance surfaces.
- [NovaLIS Fourth Pass Audit (2026-04-25)](audits/2026-04-25/NovaLIS_Fourth_Pass_Audit_2026-04-25.md) - fourth pass covering security surface, CI gaps, LLM locking, and module survey.
- [Nova OpenClaw docs-to-code alignment audit (2026-04-26)](audits/2026-04-26/NOVA_OPENCLAW_DOCS_TO_CODE_ALIGNMENT_AUDIT_2026-04-26.md) - current OpenClaw implementation truth, future hands-layer gaps, and required changes to align with the final stack direction.
- [User ready status](product/USER_READY_STATUS.md) - plain-language what works now vs experimental vs not yet ready.
- [Capability maturity model](product/CAPABILITY_MATURITY.md) - better labels than enabled/disabled.

---

## Runtime Truth

- [Current runtime state](current_runtime/CURRENT_RUNTIME_STATE.md)
- [Runtime fingerprint](current_runtime/RUNTIME_FINGERPRINT.md)
- [Governance matrix](current_runtime/GOVERNANCE_MATRIX.md)

When a public doc needs current capability counts or exact enabled IDs, link here instead of copying the values.

---

## Product And User Docs

- [Human guides](reference/HUMAN_GUIDES/)
- [What Nova can do](reference/HUMAN_GUIDES/03_WHAT_NOVA_CAN_DO.md)
- [Command examples](reference/HUMAN_GUIDES/08_COMMAND_EXAMPLES.md)
- [Safety and trust](reference/HUMAN_GUIDES/06_SAFETY_AND_TRUST.md)
- [Daily workflows](reference/HUMAN_GUIDES/09_DAILY_WORKFLOWS.md)
- [OpenClaw setup and runtime guide](reference/HUMAN_GUIDES/28_OPENCLAW_SETUP_AND_RUNTIME_GUIDE_2026-03-27.md) - plain-language current truth: OpenClaw is active as bounded home-agent/worker foundations today and becomes Nova’s hands only after mediator, envelope, approval, and receipt hardening.
- [Nova Coherence, Memory, and Background Reasoning alignment map](future/NOVA_COHERENCE_MEMORY_BACKGROUND_ARCHITECTURE_ALIGNMENT.md) - umbrella alignment guide for request understanding, coherence, governed learning/memory, and background reasoning under one non-authorizing architecture.
- [Nova Request Understanding Contract](future/NOVA_REQUEST_UNDERSTANDING_CONTRACT.md) - implemented non-authorizing conversation contract that explains what Nova understood, current capability state, safe next step, and what Nova must not do.
- [Nova Conversation Coherence Layer plan](future/NOVA_CONVERSATION_COHERENCE_LAYER_PLAN.md) - safe usability/context plan for improving intent handling, task-state awareness, paused-work awareness, response templates, governed learning, and clarity without widening action authority.
- [Nova Governed Learning plan](future/NOVA_GOVERNED_LEARNING_PLAN.md) - future architecture rule: Nova may learn corrections, preferences, command meanings, and project glossary terms, but learning must remain visible and cannot grant authority.
- [Nova Background Reasoning, Not Background Automation plan](future/NOVA_BACKGROUND_REASONING_NOT_AUTOMATION_PLAN.md) - future architecture rule: Nova may think, summarize, draft, and propose in the background, but must not act in the background without explicit governed approval.
- [Nova Google connector direction final lock](future/NOVA_GOOGLE_CONNECTOR_DIRECTION_FINAL_LOCK_2026-04-26.md) - short final lock for Google onboarding: Google connects data, Nova governs action.
- [Nova Google account and connector onboarding plan](future/NOVA_GOOGLE_ACCOUNT_AND_CONNECTOR_ONBOARDING_PLAN.md) - identity-first Google sign-in and scoped connector plan for Calendar, Gmail, Drive, and Contacts under Nova governance.
- [Nova OpenClaw hands-layer implementation plan](future/NOVA_OPENCLAW_HANDS_LAYER_IMPLEMENTATION_PLAN.md) - build sequence and test gates for turning current OpenClaw foundations into Nova-governed hands without uncontrolled authority.
- [Nova Full Stack Direction final lock](future/NOVA_FULL_STACK_DIRECTION_FINAL_LOCK_2026-04-26.md) - short final lock for the future stack: ElevenLabs speaks, Gemma reasons, OpenClaw acts, Nova governs.
- [Nova Voice Stack operating model](future/NOVA_VOICE_STACK_OPERATING_MODEL_2026-04-26.md) - corrected future truth/goals: Gemma reasons, ElevenLabs speaks, OpenClaw acts, Nova governs, with local voice/text fallback and staged transition after stabilization.
- [Nova Voice-First Assistant direction](future/NOVA_VOICE_FIRST_ASSISTANT_DIRECTION.md) - future direction and TODOs for making voice the primary interface, with text as review/edit fallback and dashboard as approval/action-history control.
- [Nova ElevenLabs Voice Integration Plan](future/NOVA_ELEVENLABS_VOICE_INTEGRATION_PLAN.md) - researched plan for ElevenLabs as Nova's standard online voice path, with local/private fallback, voice budgets, provider interfaces, and governance constraints.
- [Nova Voice-First / ElevenLabs final review](future/NOVA_VOICE_FIRST_ELEVENLABS_FINAL_REVIEW_2026-04-26.md) - final decision summary: voice-first is core, ElevenLabs is the standard online voice experience, and Nova keeps authority, approvals, logs, and execution boundaries.
- [Nova Role-Based Assistant core vision](future/NOVA_ROLE_BASED_ASSISTANT_CORE_VISION.md) - umbrella future direction: home, work, everyday tasks, business roles, and governed authority under user rules.
- [Nova Role-Based Assistant decision record](future/NOVA_ROLE_BASED_ASSISTANT_DECISION_RECORD_2026-04-26.md) - accepted umbrella product decision: Nova is a role-based governed assistant, not only a small-business or CRM product.
- [Nova Everyday Task Service expansion](future/NOVA_EVERYDAY_TASK_SERVICE_EXPANSION_2026-04-26.md) - broader service direction for everyday digital tasks, forms, email review, basic work help, and eventual lightweight CRM.
- [Nova Solo Business Assistant product vision](future/NOVA_SOLO_BUSINESS_ASSISTANT_PRODUCT_VISION.md) - first focused future product direction for independents and small local businesses.
- [Nova Solo Business Assistant implementation notes](future/NOVA_SOLO_BUSINESS_ASSISTANT_IMPLEMENTATION_NOTES.md) - staged build guidance for the Solo Business Assistant MVP without overstating current runtime truth.
- [Nova Solo Business Assistant decision record](future/NOVA_SOLO_BUSINESS_ASSISTANT_DECISION_RECORD_2026-04-26.md) - accepted product decision identifying independents and small local businesses as Nova's first focused market wedge.
- [Nova Everyday Mode product vision](future/NOVA_EVERYDAY_MODE_PRODUCT_VISION.md) - future direction for non-technical everyday users and small-business workflows.
- [Nova Everyday Mode implementation notes](future/NOVA_EVERYDAY_MODE_IMPLEMENTATION_NOTES.md) - grounding and staged implementation notes so the vision is not confused with current runtime truth.
- [Nova Everyday Mode review summary](future/NOVA_EVERYDAY_MODE_REVIEW_SUMMARY_2026-04-26.md) - consolidated summary of the Everyday Mode product direction, staged build order, and guardrails.

---

## Architecture And Governance

- [Architecture landing page](architecture/README.md)
- [Reference architecture](reference/ARCHITECTURE.md)
- [Official architecture map](reference/NOVA_OFFICIAL_ARCHITECTURE_MAP.md)
- [Capability verification framework](capability_verification/FRAMEWORK.md)
- [Capability verification status](capability_verification/STATUS.md)

---

## Development And Testing

- [Developer docs](dev/README.md)
- [Local setup guide](reference/HUMAN_GUIDES/26_LOCAL_SETUP_AND_STARTUP.md)
- [Backend runtime guide](reference/HUMAN_GUIDES/13_BACKEND_RUNTIME_GUIDE.md)
- [Frontend and UI guide](reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md)
- [Testing and validation](reference/HUMAN_GUIDES/16_TESTING_AND_VALIDATION.md)

---

## Roadmap And Planning

- [Current roadmap](../4-15-26%20NEW%20ROADMAP/Now.md) - active blockers and current sprint path.
- [Trust receipt recovery handoff](../4-15-26%20NEW%20ROADMAP/HANDOFF_2026-04-26_TRUST_RECEIPT_RECOVERY.md) - exact recovery steps for the stranded trust receipt / Cap 65 implementation.
- [Cap 64 signoff ready handoff](../4-15-26%20NEW%20ROADMAP/HANDOFF_2026-04-26_CAP64_SIGNOFF_READY.md) - full session close: what landed (trust receipt hardening, runtime docs, drift fix), cap 64 P5 live checklist steps, and sequenced next steps through first role-based shell.
- [Backlog](../4-15-26%20NEW%20ROADMAP/BackLog.md) - follow-up hardening that should not interrupt the active close-out path.
- [Master roadmap](../4-15-26%20NEW%20ROADMAP/MasterRoadMap.md) - broader roadmap context.
- [Repo improvement action plan](future/repo_improvement_action_plan.md)

---

## Auralis Integration

Future commercial surface for NovaLIS. All docs are labeled future planning — none describe live runtime capabilities.

- [Auralis and NovaLIS integration goals](Future/AURALIS_NOVALIS_INTEGRATION_GOALS.md) - staged strategy: Auralis sells websites first, Nova powers lead handling and business intelligence later.
- [Auralis MVP execution plan](Future/AURALIS_MVP_EXECUTION_PLAN.md) - Nova Lead Console v1: website inquiries → lead summaries and draft replies, owner reviews before sending.
- [Auralis client funnel](Future/AURALIS_CLIENT_FUNNEL.md) - prospect to signed client to retention and Nova-backed service upsell.
- [Auralis pricing and packages](Future/AURALIS_PRICING_AND_PACKAGES.md) - tiered package structure from website-only to full Nova business agent layer.
- [Auralis risk and policy](Future/AURALIS_RISK_AND_POLICY.md) - risk register and policy guardrails for commercial Auralis/Nova work.
- [Auralis technical integration spec](Future/AURALIS_TECHNICAL_INTEGRATION_SPEC.md) - connector architecture, data flow, and governance requirements for Auralis-facing Nova surfaces.

---

## Archive

- [Archive](archive/)
