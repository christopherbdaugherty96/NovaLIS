"""
Executor Types

Defines high-level executor categories.
Executors are *clients* that may perform actions when explicitly approved.

Phase-2:
- Types exist only for identification
- No routing or selection logic here
"""

from enum import Enum


class ExecutorType(str, Enum):
    LOCAL = "local"
    REMOTE = "remote"
    MOBILE = "mobile"
    SYSTEM = "system"
