# Capability Maturity Model

Use this model to describe capabilities more honestly than a simple enabled/disabled state.

## Labels
- **Stable**: Repeatedly tested, expected to work in common environments.
- **Tested**: Implemented and covered by tests, but may have environment caveats.
- **Experimental**: Works in some paths, subject to change.
- **Internal**: Primarily for development, audits, or internal operators.
- **Requires Key**: Needs external credentials.
- **Requires Local Dependency**: Needs local model, binary, or OS integration.
- **Confirmation Required**: Should require explicit user approval before action.
- **Not User-Ready**: Exists technically but should not be relied on by normal users.

## Recommended Next Step
Apply one or more labels to every capability in the registry and surface them in docs/UI.