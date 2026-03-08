from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from time import time
from urllib.parse import urlparse

import requests

from src.ledger.writer import LedgerWriter

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}
RATE_LIMIT_PER_MINUTE = 120


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

    def __init__(self) -> None:
        self._ledger = LedgerWriter()
        self._request_times: list[float] = []
        self._session = requests.Session()

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_SCHEMES:
            raise ModelNetworkMediatorError(f"Scheme '{parsed.scheme}' not allowed for model IO.")
        host = (parsed.hostname or "").strip().lower()
        if not host:
            raise ModelNetworkMediatorError("Model URL missing hostname.")
        if host not in ALLOWED_HOSTS:
            # Permit only literal private/loopback IPs for local model runtimes.
            try:
                ip = ipaddress.ip_address(host)
                if not (ip.is_private or ip.is_loopback or ip.is_link_local):
                    raise ModelNetworkMediatorError("Non-local model host is not allowed.")
            except ValueError:
                raise ModelNetworkMediatorError("Non-local model host is not allowed.")
        try:
            for info in socket.getaddrinfo(host, None):
                addr = info[4][0]
                resolved = ipaddress.ip_address(addr)
                if not (resolved.is_private or resolved.is_loopback or resolved.is_link_local):
                    raise ModelNetworkMediatorError("Resolved model endpoint is not local/private.")
        except ModelNetworkMediatorError:
            raise
        except Exception:
            # If DNS lookup fails, allow requests layer to emit deterministic error.
            pass

    def _check_rate_limit(self) -> None:
        now = time()
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
        self._validate_url(url)
        correlation: dict[str, str] = {}
        if request_id:
            correlation["request_id"] = request_id
        if session_id:
            correlation["session_id"] = session_id

        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                json=json_payload,
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json() if response.content else {}
        except Exception as error:
            self._ledger.log_event(
                "MODEL_NETWORK_CALL_FAILED",
                {
                    "url": url,
                    "method": method.upper(),
                    "error": str(error),
                    **correlation,
                },
            )
            raise ModelNetworkMediatorError(str(error)) from error

        self._ledger.log_event(
            "MODEL_NETWORK_CALL",
            {
                "url": url,
                "method": method.upper(),
                "status_code": response.status_code,
                **correlation,
            },
        )
        return ModelResponse(status_code=response.status_code, data=payload if isinstance(payload, dict) else {})
