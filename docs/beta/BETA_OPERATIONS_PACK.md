# Nova Beta Operations Pack

Status: **planning only — non-authorizing**  
Last reviewed: 2026-09-28

## Purpose and boundary

This pack prepares the operational materials required to evaluate a future private-beta candidate.
It does not authorize implementation, distribution, outside-user testing, installer certification,
remote access, telemetry, a new capability, or any change to Nova's authority boundaries.

The governing engineering sequence remains:

```text
#440 merge
-> bounded NOVA_HOST/local-boundary P1 repair
-> fresh security proof
-> beta repository presentation pass
-> new exact installer candidate
-> clean Windows operator proof
```

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

### Required binary acceptance checks

| Check | Result |
| --- | --- |
| Candidate source SHA and artifact SHA-256 recorded | pass / fail / not executed |
| Local-boundary security proof passed on the candidate | pass / fail / not executed |
| Installer integrity and supply-chain checks passed | pass / fail / not executed |
| No known P0/P1 beta blocker remains open for this exact candidate | pass / fail / not executed |
| Clean Windows operator proof passed against the exact artifact | pass / fail / not executed |
| Core governed workflow and authority/receipt wording checked | pass / fail / not executed |
| Durable-state and recovery evidence checked where applicable | pass / fail / not executed |
| Uninstall/reinstall and retained-state behavior verified and documented | pass / fail / not executed |
| Privacy/support contract matches the candidate | pass / fail / not executed |
| Owner acceptance decision recorded | accepted / rejected / deferred |

### Immediate stop conditions

Stop candidate testing, preserve evidence, and do not continue distribution if any of the following
is observed:

- unauthorized external effect;
- false executed or success claim;
- secret or credential exposure;
- local-only boundary failure;
- silent or unrecoverable authoritative-state loss;
- failed recovery represented as success; or
- materially false authority or capability claim; or
- installer or artifact integrity mismatch.

An explicitly confirmed user deletion is not state loss. Unexpected loss of authoritative state is.

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

Recruit a small staged cohort with distinct use cases. Give every tester the same minimum journey
so evidence is comparable, then allow natural use afterward.

### Rollout gate

1. Run the first 3 testers.
2. Review all findings and stop immediately on any hard blocker.
3. Add testers 4–5 only if the first 3 are blocker-free.

This staged gate does not override the acceptance/stop policy or convert a desirable unsupported
request into a beta failure.

### Shared baseline journey

1. Install and launch the exact candidate.
2. Confirm the local-first/setup and provider-boundary information is understandable.
3. Run one useful information or reasoning request.
4. Save, review, and remove an explicit memory item where the candidate supports it.
5. Inspect Trust/recent activity and explain what did or did not happen.
6. Attempt one clearly bounded/approval-gated flow when available.
7. Record whether the user understands a limitation without being coached by internal docs.

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
- user-visible screenshots/video (UI evidence only):
- recovery/state evidence:

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
