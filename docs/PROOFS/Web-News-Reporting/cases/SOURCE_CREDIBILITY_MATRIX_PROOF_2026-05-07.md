# Source Credibility Matrix Proof - 2026-05-07

Status: pass / matrix remains conservative

## Request Coverage

- strong source signal
- weak source signal
- untrusted/fake-looking source signal
- unknown source signal
- confidence lowering under weak/untrusted sources

## What Happened

The focused search evidence regression suite now emits a conservative `source_credibility` matrix in the structured search evidence payload.

Current labels:

- `strong`: recognized source-of-record or government/education domain signal
- `weak`: weak, user-generated, rumor, or unverified-source signal
- `untrusted`: fake-looking or hoax-like source/domain signal
- `unknown`: no durable credibility signal in the local matrix

The proof fixture verifies that weak and fake-looking sources lower confidence and add a caveat:

```text
Source credibility signals are weak or unknown; treat claims as lower confidence.
```

Unknown sources are labeled for inspection, but unknown alone is not treated as proof of unreliability. That avoids over-blocking normal web results while still making the absence of a durable credibility signal visible.

Focused verification:

```text
24 passed in 5.40s
```

## What Did Not Happen

- Nova did not claim a definitive truth score for a source.
- Nova did not add a new capability.
- Nova did not call browser/computer-use.
- Nova did not execute OpenClaw.
- Nova did not perform external writes.
- Nova did not use a direct Cap 63 shortcut.

## Governance Boundary

The matrix is a local evidence signal for confidence/caveat rendering. It is not an authorization system, a fact-checking authority, or a substitute for source review.

## Evidence

- `docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/stale_provider_credibility_payload.json`
- `docs/PROOFS/Web-News-Reporting/evidence/2026-05-07/raw/stale_provider_credibility_pytest_results.txt`
- `nova_backend/tests/brain/test_search_synthesis.py`

## Remaining Follow-Up

- Add a broader outlet fixture set once the desired source taxonomy is reviewed.
- Add UI rendering proof for credibility rows once dashboard evidence capture is working.
- Keep source credibility conservative until there is stronger governance review.
