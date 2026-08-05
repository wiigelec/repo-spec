from __future__ import annotations

import copy
from typing import Any


class InitializerError(Exception):
    pass


class ImmutableRequest:
    __slots__ = (
        "_schema_version",
        "_destination",
        "_authority",
        "_source_repository",
        "_source_revision",
        "_profile",
        "_product_id",
        "_product_direction_material",
        "_deferred",
        "_metadata",
        "_frozen",
    )

    def __init__(self, raw: dict[str, Any]) -> None:
        self._schema_version = raw.get("schema_version", "")
        self._destination = raw.get("destination", "")
        authority = raw.get("authority", {})
        self._authority = dict(authority) if isinstance(authority, dict) else {}
        source = raw.get("source", {})
        if isinstance(source, dict):
            self._source_repository = source.get("repository")
            self._source_revision = source.get("revision")
        else:
            self._source_repository = None
            self._source_revision = None
        self._profile = raw.get("profile")
        product = raw.get("product", {})
        if isinstance(product, dict):
            self._product_id = product.get("id")
            dm = product.get("direction_material")
            if dm is not None and isinstance(dm, list):
                self._product_direction_material = list(dm)
            else:
                self._product_direction_material = dm if dm is not None else None
        else:
            self._product_id = None
            self._product_direction_material = None
        self._deferred = list(raw["deferred"]) if "deferred" in raw else None
        self._metadata = copy.deepcopy(raw.get("metadata")) if "metadata" in raw else None
        self._frozen = True

    @property
    def schema_version(self) -> str:
        return self._schema_version

    @property
    def destination(self) -> str:
        return self._destination

    @property
    def authority(self) -> dict[str, Any]:
        return dict(self._authority)

    @property
    def source_repository(self) -> str | None:
        return self._source_repository

    @property
    def source_revision(self) -> str | None:
        return self._source_revision

    @property
    def profile(self) -> str | None:
        return self._profile

    @property
    def product_id(self) -> str | None:
        return self._product_id

    @property
    def product_direction_material(self) -> list[Any] | None:
        if self._product_direction_material is not None:
            return list(self._product_direction_material)
        return None

    @property
    def deferred(self) -> list[str] | None:
        if self._deferred is not None:
            return list(self._deferred)
        return None

    @property
    def metadata(self) -> Any | None:
        if self._metadata is not None:
            return copy.deepcopy(self._metadata)
        return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImmutableRequest):
            return NotImplemented
        return (
            self._schema_version == other._schema_version
            and self._destination == other._destination
            and self._authority == other._authority
            and self._source_repository == other._source_repository
            and self._source_revision == other._source_revision
            and self._profile == other._profile
            and self._product_id == other._product_id
            and self._product_direction_material == other._product_direction_material
            and self._deferred == other._deferred
            and self._metadata == other._metadata
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._schema_version,
            self._destination,
            frozenset(self._authority.items()) if self._authority else None,
            self._source_repository,
            self._source_revision,
            self._profile,
            self._product_id,
            tuple(self._product_direction_material) if self._product_direction_material is not None else None,
            tuple(self._deferred) if self._deferred is not None else None,
            str(self._metadata) if self._metadata is not None else None,
        ))


class ExecutionContext:
    __slots__ = (
        "_request",
        "_frozen",
    )

    def __init__(self, request: ImmutableRequest) -> None:
        self._request = request
        self._frozen = True

    @property
    def request(self) -> ImmutableRequest:
        return self._request

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExecutionContext):
            return NotImplemented
        return self._request == other._request

    def __hash__(self) -> int:
        return hash(self._request)
