# src/governor/exceptions.py

class CapabilityRegistryError(Exception):
    """Raised when registry is missing, malformed, or capability unknown."""
    pass


class ConnectorPackageRegistryError(Exception):
    """Raised when connector package metadata is missing, malformed, or internally inconsistent."""
    pass


class NetworkMediatorError(Exception):
    """Raised for network-related failures (protocol, SSRF, timeouts, etc.)"""
    pass


class NetworkTransportError(NetworkMediatorError):
    """Mediated request failure with safe status metadata."""

    def __init__(self, message: str, *, timed_out: bool = False, status_code: int = 0) -> None:
        super().__init__(message)
        self.timed_out = timed_out
        self.status_code = status_code


class DisclosureDeniedError(NetworkMediatorError):
    """Raised when Data-Out admission denies or cannot verify a request."""

    def __init__(self, reason: str) -> None:
        self.reason = str(reason or "unavailable")
        super().__init__(f"Data-Out denied ({self.reason}).")


class ProviderConnectionNetworkError(NetworkMediatorError):
    """Safe provider-connection failure without response bodies or credentials."""

    def __init__(self, *, status_code: int, error_code: str) -> None:
        self.status_code = int(status_code)
        self.error_code = str(error_code or "http_error")
        super().__init__(
            f"Provider connection request failed ({self.error_code}, HTTP {self.status_code})."
        )


class LedgerWriteFailed(Exception):
    """Raised when a ledger write operation fails."""
    pass
