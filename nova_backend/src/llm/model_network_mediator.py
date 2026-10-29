from __future__ import annotations

import ipaddress
import json
import os
import socket
import threading
from dataclasses import dataclass
from time import time
from typing import Generator
from urllib.parse import urlparse

import requests
from src.governor.disclosure_policy import (
    DisclosureEvidenceSink,
    DisclosurePolicy,
    DisclosurePolicyEvaluator,
    TransportClass,
)
from src.governor.disclosure_transport import (
    HttpDisclosureClassifier,
    HttpDisclosureContext,
    authorize_http_disclosure,
    disclosure_facts,
)
from src.ledger.writer import LedgerWriter

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}
RATE_LIMIT_PER_MINUTE = 120


def _safe_model_url(url: str) -> str:
    """Return model URL evidence without userinfo, query, or fragment."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        port = parsed.port
        authority = f"{host}:{port}" if port is not None else host
        return parsed._replace(netloc=authority, query="", fragment="").geturl()
    except (TypeError, ValueError):
        return "invalid-url"


class ModelNetworkMediatorError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelResponse:
    status_code: int
    data: dict


class ModelNetworkMediator:
    """
    Local-model network boundary.
    - Strict host allowlist for local model endpoints
    - Bounded rate limit
    - Ledger parity for model-call lifecycle events
    """

    def __init__(
        self,
        *,
        disclosure_policy: DisclosurePolicy | None = None,
        disclosure_evidence_sink: DisclosureEvidenceSink | None = None,
        disclosure_evaluator: DisclosurePolicyEvaluator | None = None,
        disclosure_classifier: HttpDisclosureClassifier | None = None,
    ) -> None:
        self._ledger = LedgerWriter()
        self._request_times: list[float] = []
        self._session = None
        self._default_session = None
        self._thread_local = threading.local()
        self._rate_lock = threading.Lock()
        self._session_lock = threading.Lock()
        self._disclosure_policy = disclosure_policy
        self._disclosure_evidence_sink = disclosure_evidence_sink
        self._disclosure_evaluator = disclosure_evaluator or DisclosurePolicyEvaluator()
        self._disclosure_classifier = disclosure_classifier

    @staticmethod
    def _new_session() -> requests.Session:
        session = requests.Session()
        session.trust_env = False
        return session

    def _request_session(self):
        if self._session is not None and self._session is not self._default_session:
            return self._session
        session = getattr(self._thread_local, "session", None)
        if session is not None:
            return session
        with self._session_lock:
            session = getattr(self._thread_local, "session", None)
            if session is None:
                session = self._new_session()
                self._thread_local.session = session
            return session

    def _authorize_disclosure(
        self,
        *,
        method: str,
        url: str,
        has_body: bool,
        request_id: str | None,
        session_id: str | None,
    ) -> None:
        facts = disclosure_facts(
            transport=TransportClass.LOCAL_PRIVATE_MODEL,
            method=method,
            url=url,
            field_names=tuple(),
            capability_id=None,
        )
        context: HttpDisclosureContext | None = None
        if self._disclosure_classifier is not None:
            try:
                context = self._disclosure_classifier(facts)
            except Exception:
                context = None
        decision = authorize_http_disclosure(
            evaluator=self._disclosure_evaluator,
            policy=self._disclosure_policy,
            evidence_sink=self._disclosure_evidence_sink,
            context=context,
            transport=TransportClass.LOCAL_PRIVATE_MODEL,
            url=url,
            headers=None,
            field_names=tuple(),
            ambient_tls_keylog=bool(os.getenv("SSLKEYLOGFILE")),
            has_body=has_body,
            capability_id=None,
            request_id=request_id or "",
            session_id=session_id or "",
        )
        if not decision.may_proceed:
            raise ModelNetworkMediatorError(f"Data-Out denied ({decision.reason}).")

    def _validate_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_SCHEMES:
            raise ModelNetworkMediatorError(f"Scheme '{parsed.scheme}' not allowed for model IO.")
        host = (parsed.hostname or "").strip().lower()
        if not host:
            raise ModelNetworkMediatorError("Model URL missing hostname.")
        trial_profile = str(os.getenv("NOVA_RUNTIME_PROFILE") or "").strip().lower() == "trial"
        if trial_profile and host not in ALLOWED_HOSTS:
            raise ModelNetworkMediatorError(
                "Trial profile requires a loopback-only local model endpoint."
            )
        if host not in ALLOWED_HOSTS:
            # Permit only literal private/loopback IPs for local model runtimes.
            try:
                ip = ipaddress.ip_address(host)
                if not (ip.is_private or ip.is_loopback or ip.is_link_local):
                    raise ModelNetworkMediatorError("Non-local model host is not allowed.")
            except ValueError:
                raise ModelNetworkMediatorError("Non-local model host is not allowed.")
        resolved_loopbacks: list[str] = []
        try:
            for info in socket.getaddrinfo(host, None):
                addr = info[4][0]
                resolved = ipaddress.ip_address(addr)
                if trial_profile and not resolved.is_loopback:
                    raise ModelNetworkMediatorError(
                        "Trial profile requires model endpoint resolution to remain loopback-only."
                    )
                if trial_profile and str(resolved) not in resolved_loopbacks:
                    resolved_loopbacks.append(str(resolved))
                if not (resolved.is_private or resolved.is_loopback or resolved.is_link_local):
                    raise ModelNetworkMediatorError("Resolved model endpoint is not local/private.")
        except ModelNetworkMediatorError:
            raise
        except Exception as error:
            if trial_profile:
                raise ModelNetworkMediatorError(
                    "Trial profile could not resolve the local model endpoint safely."
                ) from error
            # If DNS lookup fails, allow requests layer to emit deterministic error.
            pass
        if trial_profile:
            if not resolved_loopbacks:
                raise ModelNetworkMediatorError(
                    "Trial profile requires a resolved loopback model endpoint."
                )
            if host == "localhost":
                pinned_loopback = next(
                    (
                        address
                        for address in resolved_loopbacks
                        if ipaddress.ip_address(address).version == 4
                    ),
                    resolved_loopbacks[0],
                )
            else:
                pinned_loopback = str(ipaddress.ip_address(host))
            transport_host = f"[{pinned_loopback}]" if ":" in pinned_loopback else pinned_loopback
            if parsed.port is not None:
                transport_host = f"{transport_host}:{parsed.port}"
            return parsed._replace(netloc=transport_host).geturl()
        return url

    def _check_rate_limit(self) -> None:
        now = time()
        with self._rate_lock:
            self._request_times = [t for t in self._request_times if now - t < 60]
            if len(self._request_times) >= RATE_LIMIT_PER_MINUTE:
                raise ModelNetworkMediatorError("Model network rate limit exceeded.")
            self._request_times.append(now)

    def request_json(
        self,
        *,
        method: str,
        url: str,
        json_payload: dict | None = None,
        timeout: float = 30.0,
        request_id: str | None = None,
        session_id: str | None = None,
    ) -> ModelResponse:
        self._check_rate_limit()
        self._authorize_disclosure(
            method=method,
            url=url,
            has_body=json_payload is not None,
            request_id=request_id,
            session_id=session_id,
        )
        url = self._validate_url(url)
        correlation: dict[str, str] = {}
        if request_id:
            correlation["request_id"] = request_id
        if session_id:
            correlation["session_id"] = session_id

        try:
            response = self._request_session().request(
                method=method.upper(),
                url=url,
                json=json_payload,
                timeout=timeout,
                allow_redirects=False,
            )
            response.raise_for_status()
            payload = response.json() if response.content else {}
        except Exception as error:
            self._ledger.log_event(
                "MODEL_NETWORK_CALL_FAILED",
                {
                    "url": _safe_model_url(url),
                    "method": method.upper(),
                    "error": type(error).__name__,
                    **correlation,
                },
            )
            raise ModelNetworkMediatorError(
                f"Model network call failed ({type(error).__name__})."
            ) from error

        self._ledger.log_event(
            "MODEL_NETWORK_CALL",
            {
                "url": _safe_model_url(url),
                "method": method.upper(),
                "status_code": response.status_code,
                **correlation,
            },
        )
        return ModelResponse(status_code=response.status_code, data=payload if isinstance(payload, dict) else {})

    def request_stream(
        self,
        *,
        url: str,
        json_payload: dict,
        timeout: float = 30.0,
        request_id: str | None = None,
        session_id: str | None = None,
    ) -> Generator[str, None, None]:
        """Stream text chunks from a local model endpoint.

        Same validation, rate-limiting, and ledger discipline as
        request_json. Yields decoded text fragments from Ollama's
        streaming JSON-lines format. Logs a single MODEL_NETWORK_CALL
        on completion (not per-chunk).
        """
        self._check_rate_limit()
        self._authorize_disclosure(
            method="POST",
            url=url,
            has_body=True,
            request_id=request_id,
            session_id=session_id,
        )
        url = self._validate_url(url)
        self._thread_local.last_stream_done_reason = None
        correlation: dict[str, str] = {}
        if request_id:
            correlation["request_id"] = request_id
        if session_id:
            correlation["session_id"] = session_id

        try:
            response = self._request_session().post(
                url,
                json=json_payload,
                timeout=timeout,
                stream=True,
                allow_redirects=False,
            )
            response.raise_for_status()
        except Exception as error:
            self._ledger.log_event(
                "MODEL_NETWORK_CALL_FAILED",
                {"url": _safe_model_url(url), "method": "POST", "error": type(error).__name__,
                 **correlation},
            )
            raise ModelNetworkMediatorError(
                f"Model network call failed ({type(error).__name__})."
            ) from error

        try:
            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue
                try:
                    chunk = json.loads(raw_line)
                except (json.JSONDecodeError, ValueError):
                    continue
                text = (chunk.get("message") or {}).get("content") or ""
                if text:
                    yield text
                if chunk.get("done"):
                    self._thread_local.last_stream_done_reason = str(
                        chunk.get("done_reason") or ""
                    ).strip()
        except Exception as error:
            self._ledger.log_event(
                "MODEL_NETWORK_CALL_FAILED",
                {"url": _safe_model_url(url), "method": "POST",
                 "error": f"stream_read_{type(error).__name__}", **correlation},
            )
            raise ModelNetworkMediatorError(
                f"Model stream read failed ({type(error).__name__})."
            ) from error
        finally:
            response.close()

        if self.last_stream_done_reason is None:
            error = "stream ended without a valid terminal frame"
            self._ledger.log_event(
                "MODEL_NETWORK_CALL_FAILED",
                {"url": _safe_model_url(url), "method": "POST", "error": error, **correlation},
            )
            raise ModelNetworkMediatorError(error)

        self._ledger.log_event(
            "MODEL_NETWORK_CALL",
            {"url": _safe_model_url(url), "method": "POST",
             "status_code": response.status_code, "streamed": True,
             **correlation},
        )

    @property
    def last_stream_done_reason(self) -> str | None:
        """Return the terminal reason for the latest stream on this thread."""
        return getattr(self._thread_local, "last_stream_done_reason", None)
