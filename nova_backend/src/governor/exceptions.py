# src/governor/exceptions.py

class CapabilityRegistryError(Exception):
    """Raised when registry is missing, malformed, or capability unknown."""
    pass


class NetworkMediatorError(Exception):
    """Raised for network-related failures (protocol, SSRF, timeouts, etc.)"""
    pass


class LedgerWriteFailed(Exception):
    """Raised when a ledger write operation fails."""
    pass