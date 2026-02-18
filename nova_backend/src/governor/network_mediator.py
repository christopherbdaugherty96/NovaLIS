# src/governor/network_mediator.py

import ipaddress
import threading
from collections import defaultdict
from time import time
from typing import Dict, Any, Optional, Union
from urllib.parse import urlparse

import requests

from src.governor.exceptions import NetworkMediatorError, CapabilityRegistryError
from src.ledger.writer import LedgerWriter

NETWORK_TIMEOUT = 5  # seconds (default)
ALLOWED_SCHEMES = {"http", "https"}
DISALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}
RATE_LIMIT_PER_MINUTE = 10


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
    - Skills may call with capability_id=None (shared bucket).
    """

    def __init__(self):
        self._registry = None  # lazy-loaded
        self.ledger = LedgerWriter()
        self._request_times: Dict[Union[int, str], list] = defaultdict(list)
        self._lock = threading.Lock()

    @property
    def registry(self):
        if self._registry is None:
            from src.governor.capability_registry import CapabilityRegistry
            self._registry = CapabilityRegistry()
        return self._registry

    def _check_rate_limit(self, key: Union[int, str]) -> None:
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
        """Prevent SSRF and non-HTTP protocols."""
        parsed = urlparse(url)

        if parsed.scheme not in ALLOWED_SCHEMES:
            raise NetworkMediatorError(f"Scheme '{parsed.scheme}' not allowed.")

        host = parsed.hostname
        if host is None:
            raise NetworkMediatorError("URL must have a hostname.")
        if host in DISALLOWED_HOSTS:
            raise NetworkMediatorError("Access to localhost is forbidden.")

        # Block private IP ranges if host is an IP literal
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                raise NetworkMediatorError("Private network access forbidden.")
        except (ValueError, TypeError):
            # Host is a domain name; we do not resolve DNS here.
            pass

    def request(
        self,
        capability_id: Optional[int],
        method: str,
        url: str,
        json_payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        *,
        as_json: bool = True,
        timeout: Optional[float] = None,
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
        if capability_id is not None:
            key: Union[int, str] = capability_id
            try:
                _ = self.registry.get(capability_id)
            except CapabilityRegistryError as e:
                raise NetworkMediatorError(f"Capability check failed: {e}") from e

            if not self.registry.is_enabled(capability_id):
                raise NetworkMediatorError(f"Capability {capability_id} is disabled.")
        else:
            key = "non_capability"  # shared bucket for skills/tools

        self._check_rate_limit(key)

        # 2) URL validation
        self._validate_url(url)

        # 3) Request execution
        req_timeout = float(timeout) if timeout is not None else NETWORK_TIMEOUT
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_payload,
                headers=headers,
                timeout=req_timeout,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            self.ledger.log_event(
                "NETWORK_CALL_FAILED",
                {"capability_id": capability_id, "url": url, "error": str(e)},
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
                "url": url,
                "method": method.upper(),
                "status_code": response.status_code,
            },
        )

        return result


# Global singleton for Phase-4 network authority.
# Skills/tools should import and use this rather than creating their own mediators.
network_mediator = NetworkMediator()