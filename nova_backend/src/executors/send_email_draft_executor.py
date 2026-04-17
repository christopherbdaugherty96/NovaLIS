# src/executors/send_email_draft_executor.py
"""
Send Email Draft Executor — cap 64 (send_email_draft)

Composes an email draft using the local LLM, then opens the system mail
client via a mailto: URI so the user reviews and sends manually.

Nova never transmits email autonomously. The governed path is:
  1. Extract recipient, subject, and body intent from params
  2. Generate a draft body via LLM (falls back to template if LLM unavailable)
  3. Build a mailto: URI and open it with the OS default mail client
  4. Log EMAIL_DRAFT_CREATED to the ledger

Authority class: persistent_change
Risk: confirm — requires explicit user confirmation before execution
External effect: true (opens mail client with pre-filled content)
Reversible: false (once opened the draft is in the mail client)
"""
from __future__ import annotations

import subprocess
import platform
import urllib.parse
from typing import Any

from src.actions.action_result import ActionResult
from src.ledger.writer import LedgerWriter
from src.skills.general_chat import generate_chat


_DRAFT_PROMPT_TEMPLATE = (
    "Write a concise, professional email.\n"
    "To: {to}\n"
    "Subject: {subject}\n"
    "Context / request: {body_intent}\n\n"
    "Return only the email body text. No subject line, no greeting header, "
    "no sign-off unless one is natural. Plain text only."
)

_FALLBACK_BODY = "(Nova could not generate a draft body — please write your message here.)"


class SendEmailDraftExecutor:
    """
    Governed executor for email draft composition.

    Opens the system mail client via mailto: URI after composing a draft
    with the local LLM. The user retains full control — nothing is sent
    automatically.
    """

    def __init__(self, ledger: LedgerWriter | None = None) -> None:
        self._ledger = ledger or LedgerWriter()

    def execute(self, req) -> ActionResult:
        params: dict[str, Any] = dict(req.params or {})
        to = str(params.get("to") or "").strip()
        subject = str(params.get("subject") or "").strip()
        body_intent = str(params.get("body_intent") or params.get("body") or "").strip()
        session_id = str(params.get("session_id") or "")

        # Require at least one of: recipient or subject
        if not to and not subject and not body_intent:
            return ActionResult.failure(
                "I need a bit more to draft an email. "
                "Try: 'draft an email to john@example.com about the project update'.",
                request_id=req.request_id,
            )

        # Generate body via LLM
        body = self._generate_body(to=to, subject=subject, body_intent=body_intent)

        # Build and open mailto: URI
        mailto_uri = self._build_mailto(to=to, subject=subject, body=body)
        open_ok = self._open_mailto(mailto_uri)

        # Log to ledger
        try:
            self._ledger.log_event(
                "EMAIL_DRAFT_CREATED" if open_ok else "EMAIL_DRAFT_FAILED",
                {
                    "capability_id": 64,
                    "request_id": req.request_id,
                    "session_id": session_id,
                    "to": to or "(not specified)",
                    "subject": subject or "(not specified)",
                    "body_length": len(body),
                    "mailto_opened": open_ok,
                },
            )
        except Exception:
            pass  # ledger failure must not block user response

        if not open_ok:
            return ActionResult(
                success=False,
                message=(
                    "I composed a draft but couldn't open your mail client automatically.\n\n"
                    f"**To:** {to or '(fill in)'}\n"
                    f"**Subject:** {subject or '(fill in)'}\n\n"
                    f"{body}"
                ),
                request_id=req.request_id,
                risk_level="confirm",
                authority_class="persistent_change",
                external_effect=True,
                reversible=False,
                data={
                    "to": to,
                    "subject": subject,
                    "body": body,
                    "mailto_opened": False,
                },
            )

        # Success
        summary_parts = []
        if to:
            summary_parts.append(f"to **{to}**")
        if subject:
            summary_parts.append(f"about *{subject}*")
        summary = "Email draft " + (" ".join(summary_parts) if summary_parts else "") + " opened in your mail client. Review and send when ready."

        return ActionResult(
            success=True,
            message=summary,
            request_id=req.request_id,
            risk_level="confirm",
            authority_class="persistent_change",
            external_effect=True,
            reversible=False,
            data={
                "to": to,
                "subject": subject,
                "body": body,
                "mailto_opened": True,
            },
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _generate_body(self, *, to: str, subject: str, body_intent: str) -> str:
        """Ask the local LLM to write the email body. Falls back to a placeholder."""
        prompt = _DRAFT_PROMPT_TEMPLATE.format(
            to=to or "(recipient not specified)",
            subject=subject or "(subject not specified)",
            body_intent=body_intent or "general message",
        )
        try:
            result = generate_chat([{"role": "user", "content": prompt}])
            text = (result or "").strip()
            if text:
                return text
        except Exception:
            pass
        return _FALLBACK_BODY

    def _build_mailto(self, *, to: str, subject: str, body: str) -> str:
        """Build an RFC 6068 mailto: URI."""
        params: dict[str, str] = {}
        if subject:
            params["subject"] = subject
        if body:
            params["body"] = body
        query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        encoded_to = urllib.parse.quote(to) if to else ""
        return f"mailto:{encoded_to}{'?' + query if query else ''}"

    def _open_mailto(self, uri: str) -> bool:
        """Open the mailto: URI in the OS default mail client. Returns True on success."""
        try:
            system = platform.system()
            if system == "Windows":
                import os
                os.startfile(uri)  # type: ignore[attr-defined]
            elif system == "Darwin":
                subprocess.run(["open", uri], check=True, timeout=5)
            else:
                subprocess.run(["xdg-open", uri], check=True, timeout=5)
            return True
        except Exception:
            return False
