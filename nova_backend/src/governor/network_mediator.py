# src/governor/network_mediator.py

import ipaddress
import os
import re
import socket
import threading
from collections import defaultdict
from time import time
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

import requests
from src.governor.exceptions import (
    CapabilityRegistryError,
    NetworkMediatorError,
    ProviderConnectionNetworkError,
)
from src.ledger.writer import LedgerWriter

NETWORK_TIMEOUT = 5  # seconds (default)
ALLOWED_SCHEMES = {"http", "https"}
DISALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}
RATE_LIMIT_PER_MINUTE = 50
MAX_REDIRECT_HOPS = 5
HTTP_EXCEPTION_ENV = "NOVA_HTTP_EXCEPTION_HOSTS"

CONNECTION_OPERATION_ENDPOINTS: dict[str, dict[str, tuple[str, str]]] = {
    "google_workspace": {
        "exchange_code": ("POST", "https://oauth2.googleapis.com/token"),
        "refresh_token": ("POST", "https://oauth2.googleapis.com/token"),
        "fetch_identity": (
            "GET",
            "https://openidconnect.googleapis.com/v1/userinfo",
        ),
        "revoke": ("POST", "https://oauth2.googleapis.com/revoke"),
    }
}
SAFE_CONNECTION_ERROR_RE = re.compile(r"^[a-z0-9_-]{1,64}$")


def _http_exception_hosts() -> set[str]:
    """Comma-delimited HTTP host allowlist for explicit legacy exceptions."""
    raw = os.getenv(HTTP_EXCEPTION_ENV, "")
    return {host.strip().lower() for host in raw.split(",") if host.strip()}


class NetworkMediator:
    """
    Sole gateway for all external HTTP(S) calls.

    Enforces:
    - Timeouts
    - SSRF protection (scheme/host/IP checks)
    - Rate limiting (thread-safe)
    - Ledger logging (success + failure)

    Notes:
    - This mediator is synchronous (requests). Async callers should use asyncio.to_thread().
    - All calls must be capability-bound.
    """

    def __init__(self):
        self._registry = None  # lazy-loaded
        self.ledger = LedgerWriter()
        self._request_times: Dict[Any, list] = defaultdict(list)
        self._lock = threading.Lock()

    @property
    def registry(self):
        if self._registry is None:
            from src.governor.capability_registry import CapabilityRegistry
            self._registry = CapabilityRegistry()
        return self._registry

    def _check_rate_limit(self, key: Any) -> None:
        now = time()
        with self._lock:
            times = self._request_times[key]
            # Keep only requests in last 60s
            times = [t for t in times if now - t < 60]
            if len(times) >= RATE_LIMIT_PER_MINUTE:
                raise NetworkMediatorError("Rate limit exceeded.")
            times.append(now)
            self._request_times[key] = times

    def _validate_url(self, url: str) -> None:
        """
        Prevent SSRF and non-HTTP protocols.

        Known gap: DNS rebinding is not defended here because we do not resolve
        hostnames at validation time. Private-IP literals are blocked; domain names
        that resolve to private IPs are not. Acceptable for Phase-4 threat model.
        """
        parsed = urlparse(url)

        if parsed.scheme not in ALLOWED_SCHEMES:
            raise NetworkMediatorError(f"Scheme '{parsed.scheme}' not allowed.")

        host = parsed.hostname
        if host is None:
            raise NetworkMediatorError("URL must have a hostname.")
        if host in DISALLOWED_HOSTS:
            raise NetworkMediatorError("Access to localhost is forbidden.")
        if parsed.scheme == "http" and host.lower() not in _http_exception_hosts():
            raise NetworkMediatorError(
                "Plain HTTP is blocked by policy. Use HTTPS or add an explicit HTTP exception host."
            )

        # Block private IP ranges if host is an IP literal
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                raise NetworkMediatorError("Private network access forbidden.")
        except (ValueError, TypeError):
            # Host is a domain name.
            pass

        # DNS rebinding hardening: block domains resolving to private/loopback ranges.
        try:
            for info in socket.getaddrinfo(host, None):
                addr = info[4][0]
                resolved = ipaddress.ip_address(addr)
                if resolved.is_private or resolved.is_loopback or resolved.is_link_local:
                    raise NetworkMediatorError("Resolved private network address forbidden.")
        except NetworkMediatorError:
            raise
        except Exception:
            # If DNS resolution fails, requests layer will raise a deterministic network error.
            pass

    def request(
        self,
        capability_id: int,
        method: str,
        url: str,
        json_payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        *,
        as_json: bool = True,
        timeout: Optional[float] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform an HTTP request on behalf of a capability or skill.

        Returns:
          {
            "status_code": int,
            "data": <json>        # when as_json=True
          }
        or
          {
            "status_code": int,
            "text": "<raw text>"  # when as_json=False
          }

        Raises NetworkMediatorError on failure.
        """
        # 1) Rate limit + capability check
        try:
            _ = self.registry.get(capability_id)
        except CapabilityRegistryError as e:
            raise NetworkMediatorError(f"Capability check failed: {e}") from e

        if not self.registry.is_enabled(capability_id):
            raise NetworkMediatorError(f"Capability {capability_id} is disabled.")

        self._check_rate_limit(capability_id)

        # 2) URL validation
        self._validate_url(url)

        # 3) Request execution
        req_timeout = float(timeout) if timeout is not None else NETWORK_TIMEOUT
        current_url = url
        correlation: Dict[str, Any] = {}
        if request_id:
            correlation["request_id"] = request_id
        if session_id:
            correlation["session_id"] = session_id
        try:
            response = None
            for _ in range(MAX_REDIRECT_HOPS + 1):
                self._validate_url(current_url)
                response = requests.request(
                    method=method.upper(),
                    url=current_url,
                    params=params,
                    json=json_payload,
                    headers=headers,
                    timeout=req_timeout,
                    allow_redirects=False,
                )

                if response.is_redirect or response.is_permanent_redirect:
                    location = response.headers.get("Location")
                    if not location:
                        raise NetworkMediatorError("Redirect response missing Location header.")
                    current_url = urljoin(current_url, location)
                    continue

                response.raise_for_status()
                break
            else:
                raise NetworkMediatorError("Too many redirects.")
        except requests.RequestException as e:
            self.ledger.log_event(
                "NETWORK_CALL_FAILED",
                {
                    "capability_id": capability_id,
                    "url": url,
                    "error": str(e),
                    **correlation,
                },
            )
            raise NetworkMediatorError(f"Network call failed: {e}") from e

        # 4) Return shape based on as_json
        result: Dict[str, Any] = {"status_code": response.status_code}
        if as_json:
            data = None
            if response.content:
                try:
                    data = response.json()
                except ValueError as e:
                    self.ledger.log_event(
                        "NETWORK_CALL_FAILED",
                        {
                            "capability_id": capability_id,
                            "url": url,
                            "error": f"JSON parse failed: {e}",
                            **correlation,
                        },
                    )
                    raise NetworkMediatorError("Response was not valid JSON.") from e
            result["data"] = data
        else:
            result["text"] = response.text

        # 5) Log success (no headers to avoid leaking secrets)
        self.ledger.log_event(
            "EXTERNAL_NETWORK_CALL",
            {
                "capability_id": capability_id,
                "url": current_url,
                "original_url": url,
                "method": method.upper(),
                "status_code": response.status_code,
                **correlation,
            },
        )

        return result

    def connection_request(
        self,
        provider_id: str,
        operation: str,
        method: str,
        url: str,
        *,
        form_payload: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        as_json: bool = True,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Perform one allowlisted, user-initiated provider connection request.

        Connection setup is deliberately separate from capability execution:
        it does not consult the Governor or capability registry and therefore
        cannot grant Nova execution authority. The provider, operation, HTTP
        method, and endpoint must match the static setup allowlist exactly.

        Payloads and headers can contain credentials and are never written to
        the ledger. Only safe request metadata is recorded.
        """
        provider = str(provider_id or "").strip().lower()
        operation_name = str(operation or "").strip().lower()
        method_name = str(method or "").strip().upper()
        expected = CONNECTION_OPERATION_ENDPOINTS.get(provider, {}).get(operation_name)
        if expected is None or expected != (method_name, url):
            raise NetworkMediatorError("Provider connection operation is not allowlisted.")

        self._check_rate_limit(("connection", provider))
        self._validate_url(url)
        request_timeout = float(timeout) if timeout is not None else NETWORK_TIMEOUT

        try:
            response = requests.request(
                method=method_name,
                url=url,
                data=form_payload,
                headers=headers,
                timeout=request_timeout,
                allow_redirects=False,
            )
        except requests.RequestException as error:
            self.ledger.log_event(
                "CONNECTION_NETWORK_CALL_FAILED",
                {
                    "provider_id": provider,
                    "operation": operation_name,
                    "url": url,
                    "method": method_name,
                    "error": type(error).__name__,
                },
            )
            raise NetworkMediatorError("Provider connection request failed.") from error

        if response.is_redirect or response.is_permanent_redirect:
            self.ledger.log_event(
                "CONNECTION_NETWORK_CALL_FAILED",
                {
                    "provider_id": provider,
                    "operation": operation_name,
                    "url": url,
                    "method": method_name,
                    "error": "redirect_rejected",
                },
            )
            raise NetworkMediatorError("Provider connection redirects are not allowed.")

        if response.status_code >= 400:
            safe_error = "http_error"
            try:
                payload = response.json() if response.content else {}
                candidate = str(payload.get("error") or "").strip().lower()
                if SAFE_CONNECTION_ERROR_RE.fullmatch(candidate):
                    safe_error = candidate
            except (AttributeError, TypeError, ValueError):
                pass
            self.ledger.log_event(
                "CONNECTION_NETWORK_CALL_FAILED",
                {
                    "provider_id": provider,
                    "operation": operation_name,
                    "url": url,
                    "method": method_name,
                    "status_code": response.status_code,
                    "error": safe_error,
                },
            )
            raise ProviderConnectionNetworkError(
                status_code=response.status_code,
                error_code=safe_error,
            )

        result: Dict[str, Any] = {"status_code": response.status_code}
        if as_json:
            try:
                result["data"] = response.json() if response.content else None
            except ValueError as error:
                self.ledger.log_event(
                    "CONNECTION_NETWORK_CALL_FAILED",
                    {
                        "provider_id": provider,
                        "operation": operation_name,
                        "url": url,
                        "method": method_name,
                        "error": "invalid_json",
                    },
                )
                raise NetworkMediatorError(
                    "Provider connection response was not valid JSON."
                ) from error
        else:
            result["text"] = response.text

        self.ledger.log_event(
            "CONNECTION_NETWORK_CALL",
            {
                "provider_id": provider,
                "operation": operation_name,
                "url": url,
                "method": method_name,
                "status_code": response.status_code,
            },
        )
        return result
