from __future__ import annotations

import asyncio
import inspect
import json
import os
import threading
import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar, cast

from src.durability.state_layout import canonical_user_data_root

if os.name == "nt":
    import ctypes
    import msvcrt
    from ctypes import wintypes

    class _WindowsOverlapped(ctypes.Structure):
        _fields_ = (
            ("Internal", ctypes.c_size_t),
            ("InternalHigh", ctypes.c_size_t),
            ("Offset", wintypes.DWORD),
            ("OffsetHigh", wintypes.DWORD),
            ("hEvent", wintypes.HANDLE),
        )

    _KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _LOCK_FILE_EX = _KERNEL32.LockFileEx
    _LOCK_FILE_EX.argtypes = (
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.POINTER(_WindowsOverlapped),
    )
    _LOCK_FILE_EX.restype = wintypes.BOOL
    _UNLOCK_FILE_EX = _KERNEL32.UnlockFileEx
    _UNLOCK_FILE_EX.argtypes = (
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.POINTER(_WindowsOverlapped),
    )
    _UNLOCK_FILE_EX.restype = wintypes.BOOL


class MaintenanceActiveError(RuntimeError):
    """Raised when authoritative mutation admission is closed by maintenance."""

    def __init__(self, lock_path: Path) -> None:
        self.lock_path = Path(lock_path)
        super().__init__(
            f"Nova maintenance is active; mutation refused ({self.lock_path})"
        )


class MaintenanceTimeoutError(TimeoutError):
    """Raised when maintenance cannot obtain a fully quiesced boundary in time."""


@dataclass(frozen=True)
class MaintenanceStatus:
    lock_path: Path
    owner_active: bool
    metadata: dict[str, object] | None


_Callable = TypeVar("_Callable", bound=Callable[..., Any])
_ADMISSION_LOCK_OFFSET = 1 << 30
_ACTIVITY_LOCK_OFFSET = _ADMISSION_LOCK_OFFSET + 1


def authoritative_mutation(function: _Callable) -> _Callable:
    """Acquire mutation admission before a logical authoritative operation."""

    if inspect.iscoroutinefunction(function):
        @wraps(function)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with mutation_scope():
                return await function(*args, **kwargs)

        return cast(_Callable, async_wrapper)

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        with mutation_scope():
            return function(*args, **kwargs)

    return cast(_Callable, wrapper)


class _OSFileLease:
    """One shared or exclusive byte-range lease in the maintenance lock file."""

    def __init__(self, path: Path, *, offset: int) -> None:
        requested_path = Path(path)
        self.path = (
            requested_path.with_name(f"{requested_path.name}.activity")
            if os.name != "nt" and offset == _ACTIVITY_LOCK_OFFSET
            else requested_path
        )
        self.offset = offset
        self._handle = None
        self._overlapped = None
        self._locked = False

    def acquire(self, *, exclusive: bool) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("a+b")
        try:
            acquired = self._acquire_windows(exclusive) if os.name == "nt" else self._acquire_posix(exclusive)
        except Exception:
            self._handle.close()
            self._handle = None
            raise
        if not acquired:
            self._handle.close()
            self._handle = None
            return False
        self._locked = True
        return True

    def _acquire_windows(self, exclusive: bool) -> bool:
        flags = 0x00000001 | (0x00000002 if exclusive else 0)
        overlapped = _WindowsOverlapped(Offset=self.offset)
        os_handle = msvcrt.get_osfhandle(self._handle.fileno())
        if _LOCK_FILE_EX(os_handle, flags, 0, 1, 0, ctypes.byref(overlapped)):
            self._overlapped = overlapped
            return True
        error = ctypes.get_last_error()
        if error in {32, 33}:
            return False
        raise OSError(error, os.strerror(error), str(self.path))

    def _acquire_posix(self, exclusive: bool) -> bool:
        import fcntl

        mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        try:
            fcntl.flock(self._handle.fileno(), mode | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        return True

    def write_metadata(self, payload: dict[str, object]) -> None:
        if not self._locked or self._handle is None:
            raise RuntimeError("metadata requires an acquired OS lease")
        encoded = (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")
        self._handle.seek(0)
        self._handle.truncate()
        self._handle.write(encoded)
        self._handle.flush()
        os.fsync(self._handle.fileno())

    def release(self) -> None:
        if self._handle is None:
            return
        try:
            if self._locked:
                if os.name == "nt":
                    self._release_windows()
                else:
                    import fcntl

                    fcntl.flock(self._handle.fileno(), fcntl.LOCK_UN)
        finally:
            self._locked = False
            self._handle.close()
            self._handle = None
            self._overlapped = None

    def _release_windows(self) -> None:
        os_handle = msvcrt.get_osfhandle(self._handle.fileno())
        if not _UNLOCK_FILE_EX(os_handle, 0, 1, 0, ctypes.byref(self._overlapped)):
            error = ctypes.get_last_error()
            raise OSError(error, os.strerror(error), str(self.path))


class MaintenanceCoordinator:
    """Process-local admission tracking backed by an OS-visible shared/exclusive lease."""

    def __init__(self, container_root: Path) -> None:
        self.container_root = Path(container_root).expanduser().resolve()
        self.lock_path = self.container_root / "control" / "maintenance.lock"
        self._condition = threading.Condition(threading.RLock())
        self._maintenance_serial = threading.Lock()
        self._admission_open = True
        self._active_writers = 0
        self._writer_lease: _OSFileLease | None = None
        self._mutation_context: ContextVar[tuple[object, int] | None] = ContextVar(
            f"nova_mutation_{id(self)}", default=None
        )

    @contextmanager
    def mutation(self) -> Iterator[None]:
        owner = _execution_owner()
        current = self._mutation_context.get()
        if current is not None and current[0] is owner:
            nested_token = self._mutation_context.set((owner, current[1] + 1))
            try:
                yield
            finally:
                self._mutation_context.reset(nested_token)
            return

        admission_lease = _OSFileLease(
            self.lock_path, offset=_ADMISSION_LOCK_OFFSET
        )
        if not admission_lease.acquire(exclusive=False):
            raise MaintenanceActiveError(self.lock_path)
        try:
            with self._condition:
                if not self._admission_open:
                    raise MaintenanceActiveError(self.lock_path)
                if self._writer_lease is None:
                    lease = _OSFileLease(
                        self.lock_path, offset=_ACTIVITY_LOCK_OFFSET
                    )
                    if not lease.acquire(exclusive=False):
                        raise MaintenanceActiveError(self.lock_path)
                    self._writer_lease = lease
                self._active_writers += 1
                context_token = self._mutation_context.set((owner, 1))
        finally:
            admission_lease.release()
        try:
            yield
        finally:
            self._mutation_context.reset(context_token)
            with self._condition:
                self._active_writers -= 1
                if self._active_writers == 0:
                    lease = self._writer_lease
                    self._writer_lease = None
                    try:
                        if lease is not None:
                            lease.release()
                    finally:
                        self._condition.notify_all()

    @contextmanager
    def maintenance(self, *, timeout: float = 30.0) -> Iterator[MaintenanceStatus]:
        if timeout < 0:
            raise ValueError("timeout must be non-negative")
        if not self._maintenance_serial.acquire(blocking=False):
            raise MaintenanceActiveError(self.lock_path)
        deadline = time.monotonic() + timeout
        admission_lease = _OSFileLease(
            self.lock_path, offset=_ADMISSION_LOCK_OFFSET
        )
        activity_lease = _OSFileLease(
            self.lock_path, offset=_ACTIVITY_LOCK_OFFSET
        )
        try:
            with self._condition:
                self._admission_open = False

            while not admission_lease.acquire(exclusive=True):
                if time.monotonic() >= deadline:
                    raise MaintenanceTimeoutError(
                        "Timed out closing interprocess Nova mutation admission"
                    )
                time.sleep(min(0.01, max(0.0, deadline - time.monotonic())))

            with self._condition:
                while self._active_writers:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise MaintenanceTimeoutError(
                            "Timed out waiting for admitted Nova mutations to drain"
                        )
                    self._condition.wait(timeout=remaining)

            while not activity_lease.acquire(exclusive=True):
                if time.monotonic() >= deadline:
                    raise MaintenanceTimeoutError(
                        "Timed out waiting for interprocess Nova mutations to drain"
                    )
                time.sleep(min(0.01, max(0.0, deadline - time.monotonic())))

            active_metadata = self._owner_metadata("active")
            admission_lease.write_metadata(active_metadata)
            try:
                yield MaintenanceStatus(self.lock_path, True, active_metadata)
            except BaseException:
                try:
                    admission_lease.write_metadata(self._owner_metadata("failed"))
                except OSError:
                    pass
                raise
            else:
                admission_lease.write_metadata(self._owner_metadata("released"))
        finally:
            try:
                activity_lease.release()
            finally:
                try:
                    admission_lease.release()
                finally:
                    with self._condition:
                        self._admission_open = True
                        self._condition.notify_all()
                    self._maintenance_serial.release()

    def status(self) -> MaintenanceStatus:
        metadata = _read_metadata(self.lock_path)
        probe = _OSFileLease(self.lock_path, offset=_ADMISSION_LOCK_OFFSET)
        acquired = probe.acquire(exclusive=False)
        if acquired:
            probe.release()
        return MaintenanceStatus(self.lock_path, not acquired, metadata)

    @staticmethod
    def _owner_metadata(state: str) -> dict[str, object]:
        return {
            "schema_version": 1,
            "state": state,
            "pid": os.getpid(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


_COORDINATORS_LOCK = threading.Lock()
_COORDINATORS: dict[str, MaintenanceCoordinator] = {}


def maintenance_lock_path(*, container_root: Path | None = None) -> Path:
    root = canonical_user_data_root() if container_root is None else Path(container_root).expanduser().resolve()
    return root / "control" / "maintenance.lock"


def get_maintenance_coordinator(
    *, container_root: Path | None = None
) -> MaintenanceCoordinator:
    lock_path = maintenance_lock_path(container_root=container_root)
    key = str(lock_path).lower() if os.name == "nt" else str(lock_path)
    with _COORDINATORS_LOCK:
        coordinator = _COORDINATORS.get(key)
        if coordinator is None:
            coordinator = MaintenanceCoordinator(lock_path.parents[1])
            _COORDINATORS[key] = coordinator
        return coordinator


@contextmanager
def mutation_scope(*, container_root: Path | None = None) -> Iterator[None]:
    with get_maintenance_coordinator(container_root=container_root).mutation():
        yield


@contextmanager
def maintenance_scope(
    *, container_root: Path | None = None, timeout: float = 30.0
) -> Iterator[MaintenanceStatus]:
    with get_maintenance_coordinator(container_root=container_root).maintenance(
        timeout=timeout
    ) as status:
        yield status


def _read_metadata(path: Path) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, UnicodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _execution_owner() -> object:
    try:
        task = asyncio.current_task()
    except RuntimeError:
        task = None
    return task if task is not None else threading.current_thread()
