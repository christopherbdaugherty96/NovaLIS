# Nova Beta Operations Pack

Status: **planning only — non-authorizing**
Last reviewed: 2026-09-29

## Purpose and boundary

This pack prepares the operational materials required to evaluate a future private-beta candidate.
It does not authorize implementation, distribution, outside-user testing, installer certification,
remote access, telemetry, a new capability, or any change to Nova's authority boundaries.

Reconciled against merged #440, `main@1936014546a5996ad3fd3b9127346cb6242d8109`.
The [current command center](../status/DAILY_COMMAND_CENTER.md) governs current ordering;
the [beta freeze criteria](../decisions/2026-09-03-beta-freeze-criteria.md) govern acceptance.
#438's synthetic cohort and #439's connected-user test correction are complete. Neither is
acceptance evidence for a future artifact; #434 must run again on the frozen candidate.

The present workflow is:

```text
#440 merged -> affected merged-main proof
-> reconcile/review #441 -> separate owner #441 merge decision
-> bounded NOVA_HOST/local-boundary P1 repair
-> fresh security and operational-truth proof
-> installer supply-chain, privacy/Data-Out, and secrets audit
-> new exact installer candidate
-> clean Windows operator proof
-> freeze exact candidate identity
-> rerun #434 and remaining acceptance checks against that frozen candidate
-> owner acceptance/distribution decision
-> 3 outside users -> checkpoint -> up to 5 users -> evidence-selected next lane
```

This is the present workflow order, not an architectural requirement that documentation always
precede security work. This pack starts no implementation lane and grants no merge authority.

The documents below become operative only when their stated evidence gate is satisfied. Until
then, use the words `draft`, `planned`, `not executed`, or `not accepted` rather than `beta ready`.

## Operating model

```text
Engineering evidence + beta-operations materials
                    |
                    v
          exact candidate acceptance decision
                    |
                    v
              controlled tester use
```

The operations pack does not override generated runtime truth, implementation, security proof, or
the owner’s acceptance decision.

## 1. Beta Acceptance and Stop Policy

**Finalize:** after the local-boundary P1 repair and fresh proof; before creation of an installer
candidate.

For every candidate, record the exact source SHA and installer SHA-256 at the top. If either
changes, it is a new candidate and prior acceptance evidence does not transfer.
Freezing identifies the candidate; it does not accept it. Run #434 and every acceptance check
below against the exact frozen source SHA and intended distribution artifact, without changes
during the run. Earlier developer, synthetic, and clean-machine evidence is not a substitute.
Record each result with its evidence location, environment, date, and operator. A missing or
not-executed required check blocks acceptance. A failed hard check means do not distribute:
reopen only the failed lane, correct it, create a new candidate, and rerun exact-candidate
acceptance. Never silently patch a frozen artifact.

### Required binary acceptance checks

| Check | Result |
| --- | --- |
| Candidate source SHA and artifact SHA-256 recorded | pass / fail / not executed |
| Local-boundary security proof passed on the candidate | pass / fail / not executed |
| Installer integrity and supply-chain checks passed | pass / fail / not executed |
| No known P0/P1 beta blocker remains open for this exact candidate | pass / fail / not executed |
| No hard trust/state blocker remains, regardless of severity label | pass / fail / not executed |
| #434 synthetic cohort rerun on the immutable frozen candidate; no fixes during run | pass / fail / not executed |
| Clean supported-Windows install/startup from the intended distribution path passed on the exact artifact; required upgrade proof recorded | pass / fail / not executed |
| Full hero workflow: startup -> awareness -> recommendation -> governed action/outcome -> end-of-day use | pass / fail / not executed |
| Relevant degraded/failure scenarios preserve authority, truthful outcomes, and user-visible limitations | pass / fail / not executed |
| Authority/receipt wording and actual action/outcome agree | pass / fail / not executed |
| Restart/recovery behavior passed, including truthful failed/partial restore | pass / fail / not executed |
| All accepted #408 durability/recovery requirements passed for the state users depend on | pass / fail / not executed |
| Uninstall/reinstall and retained-state behavior verified and documented | pass / fail / not executed |
| Secrets, privacy/Data-Out, and backup/support artifacts reviewed; privacy/support contract matches the candidate | pass / fail / not executed |
| Version/build identity and supported-platform wording match the candidate | pass / fail / not executed |
| Owner acceptance decision recorded | accepted / rejected / deferred |

### Immediate stop conditions

Stop candidate testing, preserve evidence, and do not continue distribution if any of the following
is observed:

- unauthorized external effect;
- false executed or success claim;
- secret or credential exposure;
- local-only boundary failure;
- silent loss or corruption of authoritative user state, or unrecoverable authoritative-state loss;
- failed recovery represented as success;
- materially false authority or capability claim;
- installer or artifact integrity mismatch.

An explicitly confirmed user deletion is not state loss. Unexpected loss of authoritative state is.
Hard blockers cannot be averaged away by positive feedback or other passing tests. Any known
P0/P1 beta blocker also prevents acceptance and distribution.

## 2. Beta Incident and Recovery Playbook

**Finalize:** before outside-user distribution.

The live playbook must specify:

1. how to stop use of a candidate without deleting evidence;
2. how to preserve and redact logs, screenshots, receipts, and the artifact identity;
3. how to classify the event against the stop policy;
4. how to restore or roll back only through documented, verified paths;
5. who decides whether testing resumes; and
6. how testers receive a clear, non-speculative status update.

Never ask a tester to send credentials, tokens, private inbox content, or unredacted logs. A
support bundle must be an explicit user action and user-reviewed/redacted where practical.

## 3. Beta Tester Protocol

**Finalize:** before recruiting testers.

Recruit non-developers with comparable problem shapes: real responsibilities spanning more than
one day that require reconstructing context. They need not share a profession. Give every tester
the same supported hero journey, then allow natural use. Select responsibilities the existing
candidate can help with; do not promise unavailable provider access or automatic Continuity.

### Rollout gate

1. Only after owner acceptance/distribution approval, run the first 3 testers on one frozen,
   accepted candidate.
2. Review all findings and stop immediately on any hard blocker.
3. If all three show no meaningful value or voluntary return, pause expansion and review the
   workflow/product hypothesis. Weak demand is not automatically an engineering defect.
4. For mixed results, identify the uncertainty and let the owner decide whether additional
   observation is warranted. For positive results, consider expansion to five total.
5. Add testers 4–5 only after a recorded owner checkpoint and only if blocker-free. Favorable
   product feedback never waives the acceptance/stop policy.

All five testers must use the same frozen source SHA and intended distribution artifact as
testers 1–3. If either identity changes, obtain acceptance for the replacement candidate and
restart the cohort. Retain earlier observations separately; never combine different candidates
in the 4/5 completion/comprehension or 3/5 voluntary-return thresholds.

This staged gate does not override the acceptance/stop policy or convert a desirable unsupported
request into a beta failure.

### Shared baseline journey

1. Install and launch the exact candidate.
2. Confirm the local-first/setup and provider-boundary information is understandable.
3. Start a real supported responsibility: run awareness, obtain a recommendation, and follow a
   governed action through its actual outcome. Record refusals/failures honestly, not as completion.
4. Save, review, and remove an explicit memory item where the candidate supports it.
5. Inspect Trust/recent activity and explain what did or did not happen.
6. Attempt one clearly bounded/approval-gated flow when available.
7. Record whether the user understands a limitation without being coached by internal docs.
8. Revisit the responsibility at end of day and on a later day; record what context remained
   useful, what had to be supplied again, and whether the user returned without prompting.

### Manual evidence per journey and responsibility

Use consented, minimal, redacted local notes; no silent telemetry. Record:

- install success and every researcher/developer intervention (including duration and reason);
- setup time and time to first useful answer, with start/end definitions fixed before the cohort;
- the responsibility, normal alternative, relevant known information and its source, and external
  changes Nova could or could not observe;
- information retained, reconstructed, missing, or incorrect; repeated context/corrections;
- hero stages attempted/completed, actual outcome or progress, and authority prompts;
- rephrased requests / total requests, confusion points, and missing-evidence expectations;
- the user's uncoached explanation of what happened, did not happen, and was not permitted;
- return date, reason, and whether spontaneous, researcher-prompted, or assisted; count only
  voluntary return toward the return-use gate, and report assistance separately;
- support effort and whether the user would entrust Nova with another responsibility.

Human reminders are not evidence of Nova proactivity. Only an observed system-generated cue
supports a claim about that cue. This cohort evaluates existing workflow value, retained context,
comprehension, and outcome honesty, not full automated long-horizon Continuity or external-state
reconciliation.

### Post-five-user checkpoint

After five completed journeys, record numerators, denominators, evidence, and the owner decision:

| Provisional signal | Required observation |
| --- | --- |
| Installation | At least 4/5 install without direct developer intervention |
| Hero workflow | At least 4/5 complete the full hero workflow |
| Comprehension | At least 4/5 correctly explain what Nova did and did not do |
| Voluntary return | At least 3/5 voluntarily use Nova again within several days |
| Diagnostic completeness | Setup time, time to first useful answer, rephrase rate, confusion, missing evidence, and interventions recorded |

Choose and record the follow-up window before recruitment so every tester gets the same
opportunity to return. With fewer than five completed journeys, report preliminary observations
only; do not claim these thresholds were evaluated. These are small-pilot decision gates, not
statistical proof of product-market fit. Failed signals require an explicit product/workflow
assessment, not automatic expansion or implementation. Positive signals support a decision to
expand the cohort before architecture. No outcome overrides a hard blocker.

### Evidence required for future implementation

Preserve Nova's authority and evidence principles (`memory != permission`,
`recommendation != authority`, `request accepted != verified outcome`). Implementation choices
and product shape remain testable, including routing, schemas, persistence, and UI.

A future Continuity proposal must show: repeated consequential problem -> current Nova delivers
some value addressing it -> one identifiable missing evidence/reconciliation step -> separately
authorized bounded implementation -> measurable improvement or failure. Define the expected
change and failure criterion before building. Without this chain, weak beta results do not justify
more Continuity. Consider workflow/usability failure or a weak product hypothesis instead.

### Feedback taxonomy

| Classification | Meaning |
| --- | --- |
| `DEFECT` | Nova violated an existing contract. |
| `UX / COMPREHENSION` | Nova behaved correctly but the person could not understand it. |
| `UNSUPPORTED EXPECTATION` | The person expected behavior Nova did not claim to support. |
| `PRODUCT OPPORTUNITY` | Repeated demand may justify future work but is not a current defect. |

Do not convert an unsupported request into an engineering failure merely because it is desirable.

## 4. Beta Privacy and Support Contract

**Decide:** before clean Windows proof; publish only once the statements are verified against the
candidate.

The contract must answer, in plain language:

- what data stays local and what runtime state persists;
- storage locations and supported export/delete paths;
- uninstall behavior and any data it intentionally preserves;
- which feature-specific paths may use external providers;
- what is logged locally and how a user can inspect it;
- how credentials are stored, disconnected, and redacted from support evidence;
- how to report bugs and security concerns; and
- the supported environment and known limitations.

### Default diagnostics posture for beta planning

```text
Product analytics telemetry: OFF
Background diagnostic upload: OFF
Crash/log upload: OFF
Local diagnostic collection: bounded and documented
Diagnostic export: explicit user action
Support bundle: user-reviewed/redacted where practical
External provider traffic: feature-specific and visible
```

This is a planning default, not a claim about current runtime behavior. Any deviation needs a
separate, visible product and privacy decision.

## 5. Candidate Evidence Packet Template

**Create the template now; populate it only for a specific candidate.**

```text
Candidate name/version:
Source SHA:
Installer filename:
Installer SHA-256:
Build environment:
Windows environment/operator:

Executed evidence:
- focused test output:
- security/local-boundary proof:
- installer/supply-chain proof:
- clean Windows operator proof:
- frozen-candidate #434 run (immutable; no fixes during run):
- full hero workflow, degraded/failure, and restart checks:
- user-visible screenshots/video (UI evidence only):
- recovery/state evidence:
- secrets/privacy/support-artifact and version/platform review:

Freeze identity/date:
Acceptance checklist results and evidence locations:

Known limitations and not-executed checks:

Acceptance decision: accepted / rejected / deferred
Decision owner/date:
```

Screenshots demonstrate the recorded product experience only. They do not certify security,
provenance, authorization correctness, state durability, or external outcomes without the relevant
separate evidence.

## Readiness gates

| Artifact | Draft now | Becomes usable |
| --- | --- | --- |
| Acceptance and stop policy | yes | after local-boundary P1 proof, before candidate build |
| Incident and recovery playbook | yes | before outside-user distribution |
| Tester protocol | yes | before recruitment |
| Privacy and support contract | decisions only | after candidate facts are verified, before Windows proof/signoff |
| Candidate evidence packet | yes | populated per exact candidate |

## Non-goals

This pack does not create a beta release, certify an installer, authorize telemetry, claim a
supported platform, activate external providers, or expand Nova’s capabilities. It is operational
preparation for rejecting or accepting a future candidate based on evidence.
