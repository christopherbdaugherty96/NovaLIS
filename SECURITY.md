# Security Policy

If you discover a security vulnerability in Nova, please report it privately via GitHub Security Advisories. Do not publicly disclose until a fix or mitigation is available.

## Known security and privacy limitations

- **Data-Out is not fully enforced.** Turning off the DeepSeek / “Governed second opinion”
  setting does not currently prevent general chat or capabilities 31, 48, and 54 from contacting
  DeepSeek when a DeepSeek API key is configured. Remove or disable the key if outbound DeepSeek
  access must be prevented.
- **The Windows installer can package runtime data.** The installer copies the backend tree
  broadly, so files present under `nova_backend/src/data` can be included in a built installer.
  Build only from a clean source export and inspect the artifact before distribution.
- **Tests can write into the source tree.** The test configuration does not consistently set
  `NOVA_RUNTIME_DIR`; some runs can create `ledger.jsonl` or `nova_state` under
  `nova_backend/src/data`. Use an isolated checkout and inspect it for generated runtime state
  after testing.

These disclosures do not indicate that the affected behavior has been fixed or mitigated.

Reporting
- Preferred: GitHub Security Advisories (https://docs.github.com/en/code-security/security-advisories)

Do not publicly disclose vulnerabilities until a fix or mitigation is available.

What to include in your report:
- A clear description of the vulnerability
- Steps to reproduce
- Environment (OS, Nova version / commit, dependencies)
- Any exploit PoC (if available)
- Contact info (optional) for follow-up

We will acknowledge receipt within 14 days and may ask for additional information to reproduce and triage the issue.
