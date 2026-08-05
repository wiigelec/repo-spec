from __future__ import annotations

import copy
from typing import Any


class InitializerError(Exception):
    pass


VALID_CLASSIFICATIONS = frozenset({
    "framework-authoritative",
    "framework-support",
    "derived",
    "profile-source",
    "installed-adapter",
    "product-instance",
    "development-state",
    "excluded",
})

VALID_INVENTORY_FIELDS = frozenset({
    "path",
    "classification",
    "authoritative",
    "installable",
    "profile",
    "exclusion_rationale",
    "derived_from",
})

INSTALLABLE_CLASSIFICATIONS = frozenset({
    "framework-authoritative",
    "framework-support",
    "derived",
})

UNINSTALLABLE_CLASSIFICATIONS = frozenset({
    "profile-source",
    "installed-adapter",
    "product-instance",
    "development-state",
    "excluded",
})


class SourceSelection:
    __slots__ = ("_repository", "_revision", "_frozen")

    def __init__(self, repository: str, revision: str) -> None:
        if not repository or not repository.strip():
            raise InitializerError("source repository must be non-empty")
        if not revision or not revision.strip():
            raise InitializerError("source revision must be non-empty")
        self._repository = repository
        self._revision = revision
        self._frozen = True

    @property
    def repository(self) -> str:
        return self._repository

    @property
    def revision(self) -> str:
        return self._revision

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SourceSelection):
            return NotImplemented
        return self._repository == other._repository and self._revision == other._revision

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((self._repository, self._revision))


class InventoryEntry:
    __slots__ = (
        "_path",
        "_classification",
        "_authoritative",
        "_installable",
        "_profile",
        "_exclusion_rationale",
        "_derived_from",
        "_frozen",
    )

    def __init__(self, raw: dict[str, Any]) -> None:
        self._path = raw.get("path", "")
        self._classification = raw.get("classification", "")
        self._authoritative = bool(raw.get("authoritative", False))
        self._installable = bool(raw.get("installable", False))
        self._profile = raw.get("profile")
        self._exclusion_rationale = raw.get("exclusion_rationale")
        df = raw.get("derived_from")
        self._derived_from = list(df) if isinstance(df, list) else None
        self._frozen = True

    @property
    def path(self) -> str:
        return self._path

    @property
    def classification(self) -> str:
        return self._classification

    @property
    def authoritative(self) -> bool:
        return self._authoritative

    @property
    def installable(self) -> bool:
        return self._installable

    @property
    def profile(self) -> str | None:
        return self._profile

    @property
    def exclusion_rationale(self) -> str | None:
        return self._exclusion_rationale

    @property
    def derived_from(self) -> list[str] | None:
        if self._derived_from is not None:
            return list(self._derived_from)
        return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InventoryEntry):
            return NotImplemented
        return (
            self._path == other._path
            and self._classification == other._classification
            and self._authoritative == other._authoritative
            and self._installable == other._installable
            and self._profile == other._profile
            and self._exclusion_rationale == other._exclusion_rationale
            and self._derived_from == other._derived_from
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._path,
            self._classification,
            self._authoritative,
            self._installable,
            self._profile,
            self._exclusion_rationale,
            tuple(self._derived_from) if self._derived_from is not None else None,
        ))


class ClassifiedInventory:
    __slots__ = ("_entries", "_by_classification", "_by_path", "_frozen")

    def __init__(self, entries: list[InventoryEntry]) -> None:
        sorted_entries = sorted(entries, key=lambda e: (e.classification, e.path))
        self._entries = tuple(sorted_entries)
        by_class: dict[str, list[InventoryEntry]] = {}
        by_path: dict[str, InventoryEntry] = {}
        for e in sorted_entries:
            by_class.setdefault(e.classification, []).append(e)
            by_path[e.path] = e
        self._by_classification = {k: tuple(v) for k, v in by_class.items()}
        self._by_path = by_path
        self._frozen = True

    @property
    def entries(self) -> tuple[InventoryEntry, ...]:
        return self._entries

    @property
    def classifications(self) -> frozenset[str]:
        return frozenset(self._by_classification.keys())

    def entries_by_classification(self, classification: str) -> tuple[InventoryEntry, ...]:
        return self._by_classification.get(classification, ())

    def entry_by_path(self, path: str) -> InventoryEntry | None:
        return self._by_path.get(path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ClassifiedInventory):
            return NotImplemented
        return self._entries == other._entries

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash(self._entries)


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


class InstallationEntryStatus:
    pending = "pending"
    installed = "installed"
    skipped = "skipped"
    rejected = "rejected"


VALID_LIFECYCLE_STATUSES = frozenset({"candidate", "accepted", "superseded", "retired"})

VALID_OVERVIEW_ROLES = frozenset({"initial", "revision", "replacement", "branch"})

PRODUCT_SPEC_LIFECYCLE_STATUSES = frozenset({"candidate", "accepted", "superseded", "retired"})

VALID_LEVEL_ROOTS = frozenset({"specs/product/level-0/", "specs/product/level-1/", "specs/product/level-2/", "specs/product/level-3/"})


class FoundationArtifactStatus:
    created = "created"
    preserved = "preserved"
    omitted = "omitted"
    deferred = "deferred"
    rejected = "rejected"


class FoundationPlan:
    __slots__ = ("_product_id", "_product_slug", "_direction_material", "_governing_issue", "_frozen")

    def __init__(
        self,
        product_id: str,
        direction_material: list[str],
        governing_issue: str,
    ) -> None:
        if not product_id or not product_id.strip():
            raise InitializerError("product_id must be non-empty")
        if not direction_material:
            raise InitializerError("direction_material must be non-empty")
        self._product_id = product_id
        self._product_slug = self._to_slug(product_id)
        self._direction_material = list(direction_material)
        self._governing_issue = governing_issue
        self._frozen = True

    @staticmethod
    def _to_slug(product_id: str) -> str:
        slug = product_id.lower().strip()
        result = []
        for ch in slug:
            if ch.isalnum():
                result.append(ch)
            elif ch in (" ", "-", "_"):
                if result and result[-1] != "-":
                    result.append("-")
            else:
                if result and result[-1] != "-":
                    result.append("-")
        slug_str = "".join(result).strip("-")
        return slug_str if slug_str else "product"

    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def product_slug(self) -> str:
        return self._product_slug

    @property
    def direction_material(self) -> list[str]:
        return list(self._direction_material)

    @property
    def governing_issue(self) -> str:
        return self._governing_issue

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FoundationPlan):
            return NotImplemented
        return (
            self._product_id == other._product_id
            and self._product_slug == other._product_slug
            and self._direction_material == other._direction_material
            and self._governing_issue == other._governing_issue
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._product_id,
            self._product_slug,
            tuple(self._direction_material),
            self._governing_issue,
        ))


def _to_slug(ident: str) -> str:
    result = []
    for ch in ident.lower().strip():
        if ch.isalnum():
            result.append(ch)
        elif ch in (" ", "-", "_"):
            if result and result[-1] != "-":
                result.append("-")
        else:
            if result and result[-1] != "-":
                result.append("-")
    return "".join(result).strip("-") or "product"


class FoundationResult:
    __slots__ = (
        "_product_id",
        "_product_slug",
        "_created",
        "_preserved",
        "_omitted",
        "_deferred",
        "_rejected",
        "_frozen",
    )

    def __init__(
        self,
        product_id: str,
        product_slug: str,
        created: list[dict[str, str]],
        preserved: list[dict[str, str]],
        omitted: list[dict[str, str]],
        deferred: list[dict[str, str]],
        rejected: list[dict[str, str]],
    ) -> None:
        self._product_id = product_id
        self._product_slug = product_slug
        self._created = list(created)
        self._preserved = list(preserved)
        self._omitted = list(omitted)
        self._deferred = list(deferred)
        self._rejected = list(rejected)
        self._frozen = True

    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def product_slug(self) -> str:
        return self._product_slug

    @property
    def created(self) -> list[dict[str, str]]:
        return list(self._created)

    @property
    def preserved(self) -> list[dict[str, str]]:
        return list(self._preserved)

    @property
    def omitted(self) -> list[dict[str, str]]:
        return list(self._omitted)

    @property
    def deferred(self) -> list[dict[str, str]]:
        return list(self._deferred)

    @property
    def rejected(self) -> list[dict[str, str]]:
        return list(self._rejected)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "foundations_complete",
            "product_id": self._product_id,
            "product_slug": self._product_slug,
            "created": self._created,
            "preserved": self._preserved,
            "omitted": self._omitted,
            "deferred": self._deferred,
            "rejected": self._rejected,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FoundationResult):
            return NotImplemented
        return (
            self._product_id == other._product_id
            and self._product_slug == other._product_slug
            and self._created == other._created
            and self._preserved == other._preserved
            and self._omitted == other._omitted
            and self._deferred == other._deferred
            and self._rejected == other._rejected
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._product_id,
            self._product_slug,
            tuple(tuple(d.items()) for d in self._created),
            tuple(tuple(d.items()) for d in self._preserved),
            tuple(tuple(d.items()) for d in self._omitted),
            tuple(tuple(d.items()) for d in self._deferred),
            tuple(tuple(d.items()) for d in self._rejected),
        ))


class InstallationPlan:
    __slots__ = ("_entries", "_frozen")

    def __init__(self, classified_inventory: ClassifiedInventory) -> None:
        sorted_entries = sorted(
            [e for e in classified_inventory.entries if e.installable],
            key=lambda e: e.path,
        )
        self._entries = tuple(sorted_entries)
        self._frozen = True

    @property
    def entries(self) -> tuple[InventoryEntry, ...]:
        return self._entries

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InstallationPlan):
            return NotImplemented
        return self._entries == other._entries

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash(self._entries)


class InstallationResult:
    __slots__ = (
        "_source_selection",
        "_staging_workspace",
        "_installed",
        "_skipped",
        "_rejected",
        "_frozen",
    )

    def __init__(
        self,
        source_selection: SourceSelection | None,
        staging_workspace: str,
        installed: list[dict[str, Any]],
        skipped: list[dict[str, Any]],
        rejected: list[dict[str, Any]],
    ) -> None:
        self._source_selection = source_selection
        self._staging_workspace = staging_workspace
        self._installed = list(installed)
        self._skipped = list(skipped)
        self._rejected = list(rejected)
        self._frozen = True

    @property
    def source_selection(self) -> SourceSelection | None:
        return self._source_selection

    @property
    def staging_workspace(self) -> str:
        return self._staging_workspace

    @property
    def installed(self) -> list[dict[str, Any]]:
        return list(self._installed)

    @property
    def skipped(self) -> list[dict[str, Any]]:
        return list(self._skipped)

    @property
    def rejected(self) -> list[dict[str, Any]]:
        return list(self._rejected)

    def to_dict(self) -> dict[str, Any]:
        output: dict[str, Any] = {
            "status": "staging_complete",
            "source_selection": None,
            "staging_workspace": self._staging_workspace,
            "installed": self._installed,
            "skipped": self._skipped,
            "rejected": self._rejected,
        }
        if self._source_selection is not None:
            output["source_selection"] = {
                "repository": self._source_selection.repository,
                "revision": self._source_selection.revision,
            }
        return output
