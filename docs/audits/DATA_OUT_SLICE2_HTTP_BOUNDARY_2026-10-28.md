# Data-Out Slice 2 — Final HTTP/model boundary candidate

Date: 2026-10-28

Status: implementation candidate; not merged and not an authorization for Slice 3.

## Scope

This slice adds provider-neutral disclosure admission immediately inside:

- `NetworkMediator.request`
- `NetworkMediator.connection_request`
- `ModelNetworkMediator.request_json`
- `ModelNetworkMediator.request_stream`

The admission runs before URL validation, DNS, HTTP session construction, or
transport. Missing policy, missing evidence storage, missing classification,
classifier failure, and evidence-write failure remain fail-closed.

Governor and capability-registry checks remain independent requirements. This
slice adds no provider, capability, external-model route, or runtime grant.

## Trust boundary

Ordinary request callers cannot assert their own authorization taxonomy. A
composition-owned classifier receives value-free facts derived by the final
transport boundary and returns the typed caller/purpose/provider taxonomy.
Policy and a pre-verified local evidence sink are also constructor-injected.

No production classifier, grant set, or evidence target is created here. The
default production behavior is therefore `UNKNOWN` and zero-attempt denial.
Later slices must provide reviewed mechanism-specific classifications and
grants; they must not weaken this default.

## Transport behavior

- HTTP sessions are created only after admission and use `trust_env=False`.
- Ambient proxies, netrc, and Requests CA-bundle environment settings are not
  inherited by the session.
- `SSLKEYLOGFILE` is represented as `tls_session_secret` data and therefore
  requires an explicit matching grant.
- URL userinfo, authorization/API-key/OAuth field names, and proxy credentials
  are classified without retaining their values.
- Cross-origin redirects remain disabled. Every allowed same-origin redirect
  path receives a new exact-destination decision before its next send.
- Network and model ledger URLs omit userinfo, query, and fragment material.
- Model failure evidence records bounded exception types rather than raw error
  strings.

## Verification evidence

Final focused boundary and mediator regression package:

```text
70 passed
```

Dedicated Slice 2 boundary tests additionally establish:

- `DENY`/`UNKNOWN` before DNS and client construction;
- missing evidence remains fail-closed even when a grant would otherwise match;
- exact destination matching and secret-free evidence;
- disabled ambient proxy discovery;
- credential classification from actual URL/header/form field names;
- TLS key-log classification;
- value-free classifier facts;
- classifier failure becomes secret-free `UNKNOWN` before DNS.

The final full-suite pass completed:

```text
5,735 passed, 6 skipped, 2 expected xfails
```

An earlier pass found five legacy tests whose intended subject was downstream
of the new admission boundary. They now bypass admission only inside those
tests; no production bypass was added. The final full-suite rerun passed.

Additional exact-candidate checks passed:

- Slice 1 policy plus Slice 2 boundary tests: 55 passed;
- source and changed-test Ruff checks;
- dependency consistency;
- operational-truth consistency;
- generated runtime-document drift;
- structural runtime smoke proof.

## Explicit non-claims

This candidate does not claim:

- external-model readiness;
- mechanism-specific provider grants;
- a verified-local production evidence root;
- filesystem, subprocess, browser, application-handoff, or startup closure;
- machine-wide monitoring;
- completion of Data-Out Slices 3–8.
