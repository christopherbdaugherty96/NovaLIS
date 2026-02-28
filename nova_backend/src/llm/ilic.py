"""Internal Loopback Inference Channel (ILIC) hardening utilities."""

from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import socket
from urllib.parse import urlparse

import requests


ALLOWED_SCHEME = "http"
ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
ALLOWED_PORTS = {11434}
CONNECT_TIMEOUT_S = 1.0
READ_TIMEOUT_METADATA_S = 5.0
READ_TIMEOUT_INFERENCE_S = 30.0


@dataclass(frozen=True)
class LockedILICConfig:
    base_url: str
    host: str
    port: int


class ILICValidationError(ValueError):
    """Raised when ILIC endpoint validation fails."""


def validate_and_lock_base_url(base_url: str) -> LockedILICConfig:
    parsed = urlparse(base_url)

    if parsed.scheme != ALLOWED_SCHEME:
        raise ILICValidationError(f"ILIC requires scheme '{ALLOWED_SCHEME}'.")

    host = parsed.hostname
    if host not in ALLOWED_HOSTS:
        raise ILICValidationError("ILIC host must be localhost or 127.0.0.1.")

    port = parsed.port or 11434
    if port not in ALLOWED_PORTS:
        raise ILICValidationError(f"ILIC port must be one of {sorted(ALLOWED_PORTS)}.")

    if parsed.path not in {"", "/"}:
        raise ILICValidationError("ILIC base_url must not include a path.")

    if parsed.query or parsed.fragment:
        raise ILICValidationError("ILIC base_url must not include query/fragment.")

    _assert_loopback_resolution(host)

    return LockedILICConfig(base_url=f"{ALLOWED_SCHEME}://{host}:{port}", host=host, port=port)


def _assert_loopback_resolution(host: str) -> None:
    # For 127 literal, this is trivial and avoids unnecessary resolver calls.
    if host == "127.0.0.1":
        return

    infos = socket.getaddrinfo(host, None)
    if not infos:
        raise ILICValidationError("ILIC host resolution returned no addresses.")

    for info in infos:
        sockaddr = info[4]
        addr = sockaddr[0]
        ip = ipaddress.ip_address(addr)
        if not ip.is_loopback:
            raise ILICValidationError("ILIC resolution produced non-loopback address.")


def build_hardened_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.proxies = {}
    return session


def metadata_timeout() -> tuple[float, float]:
    return (CONNECT_TIMEOUT_S, READ_TIMEOUT_METADATA_S)


def inference_timeout() -> tuple[float, float]:
    return (CONNECT_TIMEOUT_S, READ_TIMEOUT_INFERENCE_S)
