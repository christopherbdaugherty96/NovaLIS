# Minimal Continuity Consumer Acceptance Contract

Status: product north star and future acceptance contract; not implemented runtime truth.

This contract defines what Nova must prove before minimal Continuity can be described as a
consumer-ready personal follow-through experience. It authorizes no implementation and does not
change the current owner operating sequence.

## Consumer promise

> **Nova keeps important things from slipping through the cracks.**
>
> Nova remembers what matters, shows you what needs attention, helps you deal with it, and keeps
> track of what actually happened.

The intended consumer projection is:

```text
Today      What needs me now?
Waiting    What am I waiting for?
Done       What actually happened?
Ask Nova   Tell, ask, decide, or act naturally
```

The architecture remains:

```text
Continuity
     |
Awareness -> Decision -> Authority -> Execution -> Outcome
     ^                                      |
     +------------ Reconciliation ----------+
```

## Acceptance proofs

Minimal Continuity is not consumer-ready until all ten behaviors are demonstrated against the
same reviewed candidate:

1. **Natural capture without invention** — "I need to call insurance Friday" creates a
   proposed commitment with provenance and a date. It becomes active only through direct owner
   confirmation or an applicable owner-approved standing capture preference.
2. **Waiting-state correctness** — "The dentist said they'll call next week" creates a proposed
   waiting item, not a fabricated fact or silently authoritative record.
3. **Useful attention projection** — `Today` contains the small set that genuinely needs the
   user's attention. Future, resolved, and low-relevance items stay out of the way.
4. **Appropriate resurfacing** — an unresolved item returns at its review trigger. Nova does not
   claim an expected event failed to occur unless evidence establishes that fact.
5. **Governed help** — Nova can propose or prepare the permitted next step while making the
   approval boundary clear. Continuity state never grants execution authority.
6. **Execution/outcome distinction** — proposed, authorized, attempted, completed-unverified,
   and verified remain distinct. A draft receipt is not evidence that a message was sent.
7. **Reconciliation** — new owner statements or external evidence can advance, close, reopen, or
   supersede an item without deleting its provenance or silently rewriting history.
8. **Durability** — confirmed state survives restart and supported lifecycle operations without
   silent loss, corruption, or identity collision.
9. **Custody** — when provider-neutral Data-Out policy denies disclosure, Nova makes zero
   external connection attempts and records an explicit local decision/evidence result.
10. **Cheap correction** — a mistaken capture, date, status, or relationship is easy to inspect,
    correct, dismiss, or revoke without leaving hidden authoritative residue.

## Standing capture preference

Nova may offer a preference such as:

> Automatically keep track of things I clearly say I need to do or am waiting for.

The preference must:

- be opt-in, inspectable, and revocable;
- preserve that capture occurred under a standing owner preference;
- remain narrower than execution permission;
- leave ambiguous or materially consequential interpretations pending confirmation;
- support correction without erasing the original evidence trail.

## Product measures

Primary measure:

> **Did the user voluntarily return because Nova remembered something useful they otherwise
> would have had to remember themselves?**

Supporting measures:

- false-capture rate;
- stale or unwanted item rate;
- right-time resurfacing rate;
- manual maintenance burden;
- outcome-classification accuracy;
- false completion claims;
- time from opening Nova to understanding what needs attention;
- voluntary return days per week.

Prompt count, token count, model count, capability count, and repository popularity are not
substitutes for evidence that Nova reduced personal follow-through burden.

## Ordering boundary

This contract does not move Continuity ahead of the active sequence:

```text
egress inventory
-> provider-neutral Data-Out enforcement
-> zero-attempt denial proof
-> clean attributable Alpha-0 Windows artifact
-> one external technical operator
-> evidence-driven blocker-only fixes
-> frozen private-beta candidate
-> three real users
-> minimal Continuity only if product evidence earns it
```

No connector expansion, mobile implementation, broad UI redesign, background autonomy, or new
execution capability is authorized by this document. If product evidence earns the Continuity
lane, the smallest useful consumer slice is the acceptance contract above, projected through
`Today`, `Waiting`, and `Done`, with ordinary conversation through `Ask Nova`.
