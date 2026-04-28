# Nova Release Readiness Checklist

Date: 2026-04-28

Status: Future product checklist / not proof of release readiness

Purpose: provide a concrete checklist for deciding when Nova is ready for broader user testing or release without overstating what works.

---

## Core Rule

> **Do not call Nova release-ready until a non-developer can install it, understand its limits, get a useful result, and trust what it did or did not do.**

---

## Runtime Truth

```text
Generated runtime truth docs are current.
Runtime fingerprint generated.
Governance matrix generated.
Runtime doc drift check passes.
Capability counts are not copied into public docs except by link/reference.
```

---

## Install / First Run

```text
Clean Windows VM install tested.
Startup works without manual developer intervention.
Required dependencies are checked clearly.
Local model setup is documented or automated.
Startup failure log is easy to find.
Uninstaller exists or uninstall instructions are clear.
```

---

## First Useful Experience

```text
User can ask a simple question.
User can ask current project/status question.
Trust/action card is visible where relevant.
Nova clearly labels read-only, draft-only, approval-required, or blocked states.
Nova does not overclaim actions.
```

---

## Governance / Trust

```text
RequestUnderstanding card visible.
Non-action statements appear where relevant.
Ledger/trust receipts are accessible.
Capabilities route through governed path.
Paused work is not presented as active.
High-risk integrations are not enabled by default.
```

---

## Capability Readiness

```text
Local capability signoff matrix started or complete for advertised local actions.
Known limits documented.
Failure behavior documented.
Live signoff status is not overstated.
External writes are approval-gated or disabled.
```

---

## Security / Privacy

```text
No secrets committed.
Security policy exists.
Sensitive data routing policy exists or limitations are stated.
Connector scopes are visible if connectors exist.
Cloud provider use is disclosed where applicable.
Dependency/security scan process exists or is planned.
```

---

## Support / Feedback

```text
Issue templates or support path exists.
Known limitations are documented.
Beta feedback questions are prepared.
Changelog/release note process exists.
Privacy policy exists if collecting emails or telemetry.
```

---

## Do Not Claim Release Ready If

```text
installer has not been clean-VM tested
trust/action visibility is missing
paused work appears active
email/calendar/browser/connector writes can occur without approval
known major failures are hidden
runtime docs are stale
user cannot tell what Nova did or did not do
```

---

## Final Rule

> **Release readiness is a user-trust state, not a roadmap label.**
