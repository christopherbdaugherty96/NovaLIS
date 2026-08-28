from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Protocol

from src.connectors.google_workspace.models import GoogleStoredCredential
from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic


class GoogleCredentialVaultError(RuntimeError):
    pass


class SecretProtector(Protocol):
    protection_name: str

    def protect(self, plaintext: bytes) -> bytes: ...

    def unprotect(self, ciphertext: bytes) -> bytes: ...


class WindowsDpapiProtector:
    """Protect secrets for the current Windows user with native DPAPI."""

    protection_name = "windows_dpapi_current_user"
    _DESCRIPTION = "Nova Google Workspace credentials"
    _UI_FORBIDDEN = 0x01

    @staticmethod
    def _require_windows() -> None:
        if os.name != "nt":
            raise GoogleCredentialVaultError(
                "Secure Google credential storage requires Windows DPAPI on this build."
            )

    def protect(self, plaintext: bytes) -> bytes:
        self._require_windows()
        return self._crypt(plaintext, decrypt=False)

    def unprotect(self, ciphertext: bytes) -> bytes:
        self._require_windows()
        return self._crypt(ciphertext, decrypt=True)

    def _crypt(self, value: bytes, *, decrypt: bool) -> bytes:
        import ctypes
        from ctypes import wintypes

        class DataBlob(ctypes.Structure):
            _fields_ = [
                ("cbData", wintypes.DWORD),
                ("pbData", ctypes.POINTER(ctypes.c_ubyte)),
            ]

        buffer = ctypes.create_string_buffer(value, len(value))
        input_blob = DataBlob(
            len(value),
            ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)),
        )
        output_blob = DataBlob()
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32

        if decrypt:
            ok = crypt32.CryptUnprotectData(
                ctypes.byref(input_blob),
                None,
                None,
                None,
                None,
                self._UI_FORBIDDEN,
                ctypes.byref(output_blob),
            )
        else:
            ok = crypt32.CryptProtectData(
                ctypes.byref(input_blob),
                ctypes.c_wchar_p(self._DESCRIPTION),
                None,
                None,
                None,
                self._UI_FORBIDDEN,
                ctypes.byref(output_blob),
            )
        if not ok:
            raise GoogleCredentialVaultError("Windows could not protect Google credentials.")
        try:
            return ctypes.string_at(output_blob.pbData, output_blob.cbData)
        finally:
            kernel32.LocalFree(output_blob.pbData)


class EncryptedGoogleCredentialVault:
    """Single-account encrypted vault using Nova's atomic runtime-state path."""

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        protector: SecretProtector | None = None,
    ) -> None:
        self._path = Path(path) if path else runtime_path(
            __file__,
            "data",
            "nova_state",
            "connections",
            "google_workspace_credentials.json",
        )
        self._protector = protector or WindowsDpapiProtector()
        self._lock = shared_path_lock(self._path)

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> GoogleStoredCredential | None:
        with self._lock:
            if not self._path.exists():
                return None
            try:
                wrapper = json.loads(self._path.read_text(encoding="utf-8"))
                if wrapper.get("schema_version") != self.SCHEMA_VERSION:
                    raise GoogleCredentialVaultError(
                        "Unsupported Google credential vault schema."
                    )
                if wrapper.get("protection") != self._protector.protection_name:
                    raise GoogleCredentialVaultError(
                        "Google credential vault protection does not match this runtime."
                    )
                ciphertext = base64.b64decode(
                    str(wrapper.get("ciphertext") or ""),
                    validate=True,
                )
                plaintext = self._protector.unprotect(ciphertext)
                payload = json.loads(plaintext.decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError("Credential payload must be an object.")
                return GoogleStoredCredential.from_secret_payload(payload)
            except GoogleCredentialVaultError:
                raise
            except Exception as error:
                raise GoogleCredentialVaultError(
                    "Google credential vault could not be read safely."
                ) from error

    def save(self, credential: GoogleStoredCredential) -> None:
        plaintext = json.dumps(
            credential.to_secret_payload(),
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
        ciphertext = self._protector.protect(plaintext)
        wrapper = {
            "schema_version": self.SCHEMA_VERSION,
            "provider": "google_workspace",
            "protection": self._protector.protection_name,
            "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        }
        with self._lock:
            write_json_atomic(self._path, wrapper)

    def delete(self) -> None:
        with self._lock:
            if self._path.exists():
                self._path.unlink()
