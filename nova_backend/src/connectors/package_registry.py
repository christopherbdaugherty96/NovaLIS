from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.governor.exceptions import ConnectorPackageRegistryError

CONNECTOR_PACKAGES_PATH = Path(__file__).resolve().parents[1] / "config" / "connector_packages.json"
CAPABILITY_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "config" / "registry.json"
SOURCE_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCHEMA_VERSION = "1.0"

ALLOWED_PACKAGE_STATUSES = {"design", "active", "deprecated", "retired"}
ALLOWED_INTEGRATION_MODES = {
    "local_file",
    "read_only_feed",
    "official_api",
    "oauth_api",
    "manual_operator",
}
ALLOWED_CREDENTIAL_MODES = {
    "none",
    "local_file",
    "oauth",
    "api_key",
    "session_token",
    "browser_session",
}
ALLOWED_AUTHORITY_CLASSES = {
    "read_only_local",
    "read_only_network",
    "reversible_local",
    "persistent_change",
    "external_effect",
}
PACKAGE_ID_RE = re.compile(r"^[a-z0-9_]+$")


@dataclass(frozen=True)
class ConnectorPackage:
    id: str
    label: str
    status: str
    integration_mode: str
    authority_class: str
    requires_explicit_enable: bool
    uses_official_api: bool
    credential_mode: str
    capability_ids: tuple[int, ...] = tuple()
    module_paths: tuple[str, ...] = tuple()
    description: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "status": self.status,
            "integration_mode": self.integration_mode,
            "authority_class": self.authority_class,
            "requires_explicit_enable": self.requires_explicit_enable,
            "uses_official_api": self.uses_official_api,
            "credential_mode": self.credential_mode,
            "capability_ids": list(self.capability_ids),
            "module_paths": list(self.module_paths),
            "description": self.description,
        }


class ConnectorPackageRegistry:
    """
    Foundation registry for governed connector-package metadata.

    This is intentionally metadata-first:
    - it does not install third-party code
    - it does not widen authority by itself
    - it creates a validated allowlisted package layer for future connector rollout
    """

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        capability_registry_path: str | Path | None = None,
    ) -> None:
        self._path = Path(path) if path else CONNECTOR_PACKAGES_PATH
        self._capability_registry_path = (
            Path(capability_registry_path) if capability_registry_path else CAPABILITY_REGISTRY_PATH
        )
        self._packages = self._load_registry()

    def _load_known_capability_ids(self) -> set[int]:
        if not self._capability_registry_path.exists():
            raise ConnectorPackageRegistryError(
                f"Capability registry missing at {self._capability_registry_path}."
            )
        try:
            payload = json.loads(self._capability_registry_path.read_text(encoding="utf-8"))
        except Exception as error:
            raise ConnectorPackageRegistryError(
                f"Capability registry malformed (JSON error): {error}."
            ) from error

        capabilities = payload.get("capabilities")
        if not isinstance(capabilities, list):
            raise ConnectorPackageRegistryError("Capability registry must contain a capabilities array.")

        known_ids: set[int] = set()
        for entry in capabilities:
            if not isinstance(entry, dict) or "id" not in entry:
                raise ConnectorPackageRegistryError("Capability registry contains an invalid capability entry.")
            try:
                known_ids.add(int(entry["id"]))
            except Exception as error:
                raise ConnectorPackageRegistryError(
                    f"Capability registry contains a non-integer capability id: {entry.get('id')}"
                ) from error
        return known_ids

    @staticmethod
    def _resolve_module_file(module_path: str) -> Path:
        normalized = str(module_path or "").strip()
        if not normalized.startswith("src/"):
            raise ConnectorPackageRegistryError(
                f"module_paths entries must start with 'src/': {module_path!r}"
            )
        relative = normalized.split("/", 1)[1]
        return SOURCE_ROOT / Path(relative)

    def _load_registry(self) -> dict[str, ConnectorPackage]:
        if not self._path.exists():
            raise ConnectorPackageRegistryError(f"Connector package registry missing at {self._path}.")

        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception as error:
            raise ConnectorPackageRegistryError(
                f"Connector package registry malformed (JSON error): {error}."
            ) from error

        if payload.get("schema_version") != EXPECTED_SCHEMA_VERSION:
            raise ConnectorPackageRegistryError("Unsupported connector package registry schema version.")

        package_entries = payload.get("packages")
        if not isinstance(package_entries, list):
            raise ConnectorPackageRegistryError("Connector package registry must contain a packages array.")

        known_capability_ids = self._load_known_capability_ids()
        packages: dict[str, ConnectorPackage] = {}

        for entry in package_entries:
            if not isinstance(entry, dict):
                raise ConnectorPackageRegistryError("Connector package entries must be objects.")

            package_id = str(entry.get("id") or "").strip()
            if not PACKAGE_ID_RE.fullmatch(package_id):
                raise ConnectorPackageRegistryError(
                    f"Connector package id must be lowercase snake_case: {package_id!r}"
                )
            if package_id in packages:
                raise ConnectorPackageRegistryError(f"Duplicate connector package id: {package_id}")

            label = str(entry.get("label") or "").strip()
            if not label:
                raise ConnectorPackageRegistryError(f"Connector package {package_id} is missing label.")

            status = str(entry.get("status") or "").strip().lower()
            if status not in ALLOWED_PACKAGE_STATUSES:
                raise ConnectorPackageRegistryError(f"Invalid connector package status: {status}")

            integration_mode = str(entry.get("integration_mode") or "").strip().lower()
            if integration_mode not in ALLOWED_INTEGRATION_MODES:
                raise ConnectorPackageRegistryError(
                    f"Invalid connector package integration_mode: {integration_mode}"
                )

            authority_class = str(entry.get("authority_class") or "").strip().lower()
            if authority_class not in ALLOWED_AUTHORITY_CLASSES:
                raise ConnectorPackageRegistryError(
                    f"Invalid connector package authority_class: {authority_class}"
                )

            requires_explicit_enable = entry.get("requires_explicit_enable")
            if not isinstance(requires_explicit_enable, bool):
                raise ConnectorPackageRegistryError(
                    f"Connector package {package_id} requires_explicit_enable must be boolean."
                )

            uses_official_api = entry.get("uses_official_api")
            if not isinstance(uses_official_api, bool):
                raise ConnectorPackageRegistryError(
                    f"Connector package {package_id} uses_official_api must be boolean."
                )

            credential_mode = str(entry.get("credential_mode") or "").strip().lower()
            if credential_mode not in ALLOWED_CREDENTIAL_MODES:
                raise ConnectorPackageRegistryError(
                    f"Invalid connector package credential_mode: {credential_mode}"
                )

            capability_ids_raw = entry.get("capability_ids")
            if not isinstance(capability_ids_raw, list) or not capability_ids_raw:
                raise ConnectorPackageRegistryError(
                    f"Connector package {package_id} must declare at least one capability id."
                )
            capability_ids: list[int] = []
            for raw_id in capability_ids_raw:
                try:
                    capability_id = int(raw_id)
                except Exception as error:
                    raise ConnectorPackageRegistryError(
                        f"Connector package {package_id} contains a non-integer capability id: {raw_id!r}"
                    ) from error
                if capability_id not in known_capability_ids:
                    raise ConnectorPackageRegistryError(
                        f"Connector package {package_id} references unknown capability id: {capability_id}"
                    )
                capability_ids.append(capability_id)
            if len(set(capability_ids)) != len(capability_ids):
                raise ConnectorPackageRegistryError(
                    f"Connector package {package_id} contains duplicate capability ids."
                )

            module_paths_raw = entry.get("module_paths")
            if not isinstance(module_paths_raw, list) or not module_paths_raw:
                raise ConnectorPackageRegistryError(
                    f"Connector package {package_id} must declare module_paths."
                )
            module_paths: list[str] = []
            for raw_path in module_paths_raw:
                module_path = str(raw_path or "").strip()
                resolved = self._resolve_module_file(module_path)
                if not resolved.exists() or not resolved.is_file():
                    raise ConnectorPackageRegistryError(
                        f"Connector package {package_id} references missing module path: {module_path}"
                    )
                module_paths.append(module_path)
            if len(set(module_paths)) != len(module_paths):
                raise ConnectorPackageRegistryError(
                    f"Connector package {package_id} contains duplicate module paths."
                )

            description = str(entry.get("description") or "").strip()
            if not description:
                raise ConnectorPackageRegistryError(
                    f"Connector package {package_id} is missing description."
                )

            packages[package_id] = ConnectorPackage(
                id=package_id,
                label=label,
                status=status,
                integration_mode=integration_mode,
                authority_class=authority_class,
                requires_explicit_enable=requires_explicit_enable,
                uses_official_api=uses_official_api,
                credential_mode=credential_mode,
                capability_ids=tuple(capability_ids),
                module_paths=tuple(module_paths),
                description=description,
            )

        return packages

    def get(self, package_id: str) -> ConnectorPackage:
        package = self._packages.get(str(package_id or "").strip())
        if package is None:
            raise ConnectorPackageRegistryError(f"Unknown connector package id: {package_id}")
        return package

    def all_packages(self) -> list[ConnectorPackage]:
        return [package for _, package in sorted(self._packages.items(), key=lambda item: item[0])]

    def active_packages(self) -> list[ConnectorPackage]:
        return [package for package in self.all_packages() if package.status == "active"]

    def packages_for_capability(self, capability_id: int) -> list[ConnectorPackage]:
        target = int(capability_id)
        return [package for package in self.all_packages() if target in package.capability_ids]
