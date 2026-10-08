# Controlled technical-alpha validation

Status: proposed protocol amendment; effective only after review and owner merge decision.
Distribution requires the separate artifact-specific decision below.

## Current sequence alignment — 2026-10-08 (Issue #457)

The current work order is `OWNER_OPERATING_SEQUENCE_2026_10_08` (Issue #457), recorded at the
top of `.agent_context/current_priority.md` and the canonical status surfaces:

```text
NEXT: egress inventory
THEN: provider-neutral Data-Out enforcement at the common outbound boundary
THEN: zero-attempt denial proof (deny -> zero transmission, zero attempted external connection, explicit local result, durable decision/disclosure evidence)
THEN: clean attributable Alpha-0 Windows artifact (exact-SHA clean export + forbidden-content scan)
THEN: one defined external technical-operator workflow against that exact artifact
THEN: evidence-driven blocker-only fixes
THEN: frozen private-beta candidate
THEN: three real users
THEN: minimal Continuity only if product evidence earns it
```

Where this protocol names an older current workflow (the #441/#443 review, then the bounded
local-boundary repair), that wording is historical. The local-boundary P1 was completed by PR #447;
its entry requirement is met only by fresh security and operational-truth proof on the exact
artifact source SHA. The privacy/Data-Out entry requirement is met only by the zero-attempt denial
proof above; disclosure of the gap is not a substitute.

This protocol is the defined external technical-operator workflow: one named technical operator
first, against the exact Alpha-0 artifact identity. Expansion still follows the delivery rules below.

Recovery reconciliation: the Lane 5A recovery foundations (PRs #424 through #430) remain preserved
work, but recovery adoption and full recovery proof are no longer ordered before the private-beta
candidate. The Alpha-0 artifact makes no recovery, restore, or upgrade claim and exposes no
reachable restore activation. For that artifact, the recovery items below (development-machine
#408 recovery checks, recovery instructions, and operator step 5) are recorded as NOT APPLICABLE
with that explicit limitation; they are not silently reactivated, and an unproven recovery claim
remains a stop condition. Restoring a recovery requirement needs a later explicit owner decision
or evidence-backed need.

## Purpose and boundary

An external Windows operator may supply clean-machine evidence on hardware the owner does not
own. Start with one named technical tester, then at most three after reviewing the first report.
Participants knowingly evaluate experimental installation, startup, and recovery behavior.
They do not count toward the later product cohort or demonstrate product usefulness.

This is a narrow exception to the pre-distribution acceptance requirement in
[Beta Freeze Criteria](2026-09-03-beta-freeze-criteria.md). Only designated technical operators
may receive a validation artifact before clean-Windows proof and frozen-candidate acceptance.
All hard blockers remain binding. General product distribution still requires full acceptance.

The current workflow remains #441/#443 review and owner decisions, then the bounded
local-boundary repair and fresh proof. This document does not start that repair or change its scope.
NovaLIS remains private. Nova remains the public overview; source publication remains held for
separate license review. No license changes or historical installer publication are authorized.

## Entry requirements before any external artifact delivery

The owner must record evidence for every item against an exact source revision and artifact:

- Local-boundary P1 repaired and reviewed, with fresh security and operational-truth proof.
- No known hard trust/state blocker or P0/P1 beta blocker remains open.
- Installer integrity, dependencies/supply chain, secrets, privacy/Data-Out, and support-artifact
  checks complete. Distribution permissions for Nova, bundled dependencies, assets, and any
  model weights are established; do not assume the current license resolves these permissions.
- Installation/startup and applicable #408 recovery checks pass in the development environment,
  clearly labeled as development-machine evidence. Clean external proof may remain NOT EXECUTED.
- Exact source SHA, build procedure/environment, version, artifact filename and SHA-256 recorded.
  Every recipient receives identical identified bytes; corrections produce a new identity.
- Document prerequisites and expected resource needs with their evidence and uncertainties.
  Do not present unmeasured RAM requirements or untested Windows versions as validated support.
- Working installation, removal, recovery, reporting, and stop-use instructions accompany the build.
- Private security-reporting contact and access-controlled delivery method are verified before use.
- Each named tester agrees to the procedure and use of disposable test data on a machine they
  control. Tests must stay within their own environment and explicitly agreed provider scope.
- Owner records artifact-specific authorization, named recipients, date, and any remaining
  non-blocking limitations. Merging this protocol alone does not authorize delivery.

## Delivery and expansion

Deliver privately to the first named tester. Review their installation and reporting experience
before extending access to two more named technical testers. A public GitHub prerelease is
publicly downloadable and cannot enforce the required pre-acceptance access boundary.

Before product acceptance, every artifact delivery must remain private and access-controlled
to named technical operators within the one-to-three-tester limit. No public artifact listing,
download, or release is permitted until clean-Windows proof, normal frozen-candidate acceptance,
and the owner acceptance/distribution decision are complete for that exact artifact. A separate
technical-alpha expansion decision or prerelease label cannot waive these gates. The public
project overview may remain visible with its installer-unavailable status.

## Required operator procedure and report

Before delivery, select the exact supported-Windows target and write repeatable steps with
expected results. For clean-machine evidence, document a fresh supported Windows installation
or a documented clean physical-machine baseline with no prior Nova installation/state, project
checkout, developer environment dependencies, or preconfigured Nova model setup. Record any
preexisting prerequisites; an environment that depends on undeclared developer setup cannot pass.

Record PASS / FAIL / NOT EXECUTED with evidence for:

1. Verify installer checksum; record Windows edition/build, CPU, RAM, GPU, free storage,
   permissions, relevant security software, and all prerequisites.
2. Install from the intended delivery package using only supplied instructions. Record installer
   warnings, prerequisite/model downloads, setup time, and every intervention with duration.
3. Launch; inspect truthful model/provider readiness and unavailable-feature behavior. Exercise
   one supported workflow and inspect its receipt and actual outcome.
4. Close and restart Nova, then reboot Windows; inspect retained test state and startup behavior.
5. Perform the applicable accepted #408 backup/recovery procedure using disposable fixtures.
   Include failure/partial-restore truth checks; preserve before/after evidence.
6. Exercise removal/reinstallation and documented retained-state behavior. If the candidate
   supports upgrades, upgrade proof is a mandatory clean-Windows gate: identify the supported
   prior-version fixture and its artifact/state baseline, upgrade to the exact candidate, and
   record PASS / FAIL / NOT EXECUTED with startup and retained-state evidence for each supported
   upgrade path. FAIL, NOT EXECUTED, or a missing fixture/result prevents this report from
   satisfying the freeze gate. Fresh installation does not substitute for upgrade proof.
   If upgrades are unsupported, record that explicit candidate limitation in the report and
   installation instructions; do not imply upgrade support or count an untested upgrade as PASS.
7. Report reproduction steps, expected/actual result, identity, assistance, and sanitized evidence.
   Missing evidence or a required NOT EXECUTED item leaves the corresponding gate incomplete.

The owner reviews the complete report against the existing clean-Windows requirements and
records accepted evidence or remaining gaps. A different machine or a tester's general approval
alone does not satisfy the gate. Record environment scope; one machine proves only that environment.

Use minimal manual evidence with tester consent. Logs/screenshots must be inspected and redacted
before sharing. Route sensitive security findings privately; public reports must omit secrets and
private user data. No silent telemetry or automatic support uploads are added by this protocol.

## Stop and correction rules

Immediately stop affected testing and further distribution for unauthorized effects, false success,
secret exposure, boundary failure, silent authoritative-state loss/corruption, failed restore
represented as success, materially misleading capability/authority wording, artifact mismatch,
or any newly confirmed P0/P1 beta blocker. Notify recipients to stop using the affected artifact,
preserve sanitized evidence, and record who may authorize resumption.

A single consequential reproduced defect can warrant repair. Correct only authorized findings;
generate a new identified artifact and repeat affected proof, including clean Windows installation
for the replacement artifact. Never patch an artifact in place or carry an old artifact's PASS
forward as certification. Keep reports grouped by artifact identity.

## Transition to product testing

After required clean-Windows proof passes, freeze exact candidate identity, rerun #434 and all
remaining frozen-candidate acceptance checks, then obtain the owner acceptance/distribution
decision. A candidate awaits acceptance; only a passing, owner-accepted artifact is accepted.

Run three target non-developer users, checkpoint, then potentially five under the beta criteria.
All five use the same frozen, accepted candidate. If identity changes, restart the product cohort;
retain earlier observations separately and do not mix denominators across builds. Technical-alpha
reports and prompted return do not substitute for product completion or voluntary-return evidence.
