from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
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


class GitObjectIdentity:
    __slots__ = ("_object_format", "_object_id", "_frozen")

    def __init__(self, object_format: str, object_id: str) -> None:
        self._object_format = object_format
        self._object_id = object_id
        self._frozen = True

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError("GitObjectIdentity is immutable")
        object.__setattr__(self, name, value)

    @property
    def object_format(self) -> str:
        return self._object_format

    @property
    def object_id(self) -> str:
        return self._object_id

    def to_dict(self) -> dict[str, str]:
        return {
            "object_format": self._object_format,
            "object_id": self._object_id,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GitObjectIdentity):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        return hash((self._object_format, self._object_id))


class ImmutableRequest:
    __slots__ = (
        "_schema_version",
        "_destination",
        "_repository_name",
        "_canonical_request_bytes",
        "_request_fingerprint",
        "_frozen",
    )

    def __init__(
        self,
        raw: dict[str, Any],
        canonical_request_bytes: bytes,
        request_fingerprint: str,
    ) -> None:
        self._schema_version = raw["schema_version"]
        self._destination = raw["destination"]
        self._repository_name = Path(raw["destination"]).name
        self._canonical_request_bytes = canonical_request_bytes
        self._request_fingerprint = request_fingerprint
        self._frozen = True

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False):
            raise AttributeError("ImmutableRequest is immutable")
        object.__setattr__(self, name, value)

    @property
    def schema_version(self) -> str:
        return self._schema_version

    @property
    def destination(self) -> str:
        return self._destination

    @property
    def repository_name(self) -> str:
        return self._repository_name

    @property
    def canonical_request_bytes(self) -> bytes:
        return self._canonical_request_bytes

    @property
    def request_fingerprint(self) -> str:
        return self._request_fingerprint

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImmutableRequest):
            return NotImplemented
        return (
            self._schema_version == other._schema_version
            and self._destination == other._destination
            and self._repository_name == other._repository_name
            and self._canonical_request_bytes == other._canonical_request_bytes
            and self._request_fingerprint == other._request_fingerprint
        )

    def __hash__(self) -> int:
        return hash((
            self._schema_version,
            self._destination,
            self._repository_name,
            self._canonical_request_bytes,
            self._request_fingerprint,
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


@dataclass(frozen=True)
class I1DestinationPreflight:
    destination: str
    destination_state: str
    destination_parent: str
    filesystem_device: int
    same_filesystem: bool
    decision: str

    def to_dict(self) -> dict[str, object]:
        return {
            "destination": self.destination,
            "destination_state": self.destination_state,
            "destination_parent": self.destination_parent,
            "filesystem_device": self.filesystem_device,
            "same_filesystem": self.same_filesystem,
            "decision": self.decision,
        }


class InstallationEntryStatus:
    pending = "pending"
    installed = "installed"
    skipped = "skipped"
    rejected = "rejected"


VALID_LIFECYCLE_STATUSES = frozenset({"candidate", "accepted", "superseded", "retired"})

VALID_OVERVIEW_ROLES = frozenset({"initial", "revision", "replacement", "branch"})

PRODUCT_SPEC_LIFECYCLE_STATUSES = frozenset({"candidate", "accepted", "superseded", "retired"})

VALID_LEVEL_ROOTS = frozenset({"product/specs/product/level-0/", "product/specs/product/level-1/", "product/specs/product/level-2/", "product/specs/product/level-3/"})


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


class GitEstablishmentPhase:
    preflight = "preflight"
    initialized = "initialized"
    indexed = "indexed"
    committed = "committed"
    verified = "verified"
    failed = "failed"
    cleaned = "cleaned"


class GitPreflight:
    __slots__ = (
        "_destination_path",
        "_git_available",
        "_git_version",
        "_destination_exists",
        "_destination_is_dir",
        "_destination_is_symlink",
        "_is_git_repository",
        "_inside_worktree",
        "_outer_worktree",
        "_content_consistent",
        "_content_inconsistency_reason",
        "_decision",
        "_rejection_reason",
        "_frozen",
    )

    def __init__(
        self,
        destination_path: str,
        git_available: bool,
        git_version: str | None,
        destination_exists: bool,
        destination_is_dir: bool,
        destination_is_symlink: bool,
        is_git_repository: bool,
        inside_worktree: bool,
        outer_worktree: str | None,
        content_consistent: bool,
        content_inconsistency_reason: str | None = None,
        decision: str = "",
        rejection_reason: str | None = None,
    ) -> None:
        self._destination_path = destination_path
        self._git_available = git_available
        self._git_version = git_version
        self._destination_exists = destination_exists
        self._destination_is_dir = destination_is_dir
        self._destination_is_symlink = destination_is_symlink
        self._is_git_repository = is_git_repository
        self._inside_worktree = inside_worktree
        self._outer_worktree = outer_worktree
        self._content_consistent = content_consistent
        self._content_inconsistency_reason = content_inconsistency_reason
        self._decision = decision
        self._rejection_reason = rejection_reason
        self._frozen = True

    @property
    def destination_path(self) -> str:
        return self._destination_path
    @property
    def git_available(self) -> bool:
        return self._git_available
    @property
    def git_version(self) -> str | None:
        return self._git_version
    @property
    def destination_exists(self) -> bool:
        return self._destination_exists
    @property
    def destination_is_dir(self) -> bool:
        return self._destination_is_dir
    @property
    def destination_is_symlink(self) -> bool:
        return self._destination_is_symlink
    @property
    def is_git_repository(self) -> bool:
        return self._is_git_repository
    @property
    def inside_worktree(self) -> bool:
        return self._inside_worktree
    @property
    def outer_worktree(self) -> str | None:
        return self._outer_worktree
    @property
    def content_consistent(self) -> bool:
        return self._content_consistent
    @property
    def content_inconsistency_reason(self) -> str | None:
        return self._content_inconsistency_reason
    @property
    def decision(self) -> str:
        return self._decision
    @property
    def rejection_reason(self) -> str | None:
        return self._rejection_reason

    def to_dict(self) -> dict[str, object]:
        d: dict[str, object] = {
            "destination_path": self._destination_path,
            "git_available": self._git_available,
            "git_version": self._git_version if self._git_version else "",
            "destination_exists": self._destination_exists,
            "destination_is_dir": self._destination_is_dir,
            "destination_is_symlink": self._destination_is_symlink,
            "is_git_repository": self._is_git_repository,
            "inside_worktree": self._inside_worktree,
            "content_consistent": self._content_consistent,
            "decision": self._decision,
        }
        if self._git_version is not None:
            d["git_version"] = self._git_version
        if self._outer_worktree is not None:
            d["outer_worktree"] = self._outer_worktree
        if self._content_inconsistency_reason is not None:
            d["content_inconsistency_reason"] = self._content_inconsistency_reason
        if self._rejection_reason is not None:
            d["rejection_reason"] = self._rejection_reason
        return d

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GitPreflight):
            return NotImplemented
        return (
            self._destination_path == other._destination_path
            and self._git_available == other._git_available
            and self._git_version == other._git_version
            and self._destination_exists == other._destination_exists
            and self._destination_is_dir == other._destination_is_dir
            and self._destination_is_symlink == other._destination_is_symlink
            and self._is_git_repository == other._is_git_repository
            and self._inside_worktree == other._inside_worktree
            and self._outer_worktree == other._outer_worktree
            and self._content_consistent == other._content_consistent
            and self._content_inconsistency_reason == other._content_inconsistency_reason
            and self._decision == other._decision
            and self._rejection_reason == other._rejection_reason
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._destination_path,
            self._git_available,
            self._git_version,
            self._destination_exists,
            self._destination_is_dir,
            self._destination_is_symlink,
            self._is_git_repository,
            self._inside_worktree,
            self._outer_worktree,
            self._content_consistent,
            self._content_inconsistency_reason,
            self._decision,
            self._rejection_reason,
        ))


class GitCommandResult:
    __slots__ = (
        "_command",
        "_returncode",
        "_stdout",
        "_stderr",
        "_frozen",
    )

    def __init__(
        self,
        command: list[str],
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> None:
        self._command = list(command)
        self._returncode = returncode
        self._stdout = stdout
        self._stderr = stderr
        self._frozen = True

    @property
    def command(self) -> list[str]:
        return list(self._command)
    @property
    def returncode(self) -> int:
        return self._returncode
    @property
    def stdout(self) -> str:
        return self._stdout
    @property
    def stderr(self) -> str:
        return self._stderr
    @property
    def succeeded(self) -> bool:
        return self._returncode == 0

    def to_dict(self) -> dict[str, object]:
        return {
            "command": " ".join(self._command),
            "returncode": self._returncode,
            "stdout": self._stdout,
            "stderr": self._stderr,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GitCommandResult):
            return NotImplemented
        return (
            self._command == other._command
            and self._returncode == other._returncode
            and self._stdout == other._stdout
            and self._stderr == other._stderr
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            tuple(self._command),
            self._returncode,
            self._stdout,
            self._stderr,
        ))


class GitEstablishmentPlan:
    __slots__ = (
        "_destination_path",
        "_initial_branch",
        "_commit_message",
        "_author_name",
        "_author_email",
        "_committer_name",
        "_committer_email",
        "_timestamp",
        "_frozen",
    )

    def __init__(
        self,
        destination_path: str,
        initial_branch: str = "main",
        commit_message: str = "Initial repository foundation",
        author_name: str = "Repo-Spec Initializer",
        author_email: str = "initializer@repo-spec.local",
        committer_name: str | None = None,
        committer_email: str | None = None,
        timestamp: str | None = None,
    ) -> None:
        self._destination_path = destination_path
        self._initial_branch = initial_branch
        self._commit_message = commit_message
        self._author_name = author_name
        self._author_email = author_email
        self._committer_name = committer_name if committer_name is not None else author_name
        self._committer_email = committer_email if committer_email is not None else author_email
        self._timestamp = timestamp if timestamp is not None else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self._frozen = True

    @property
    def destination_path(self) -> str:
        return self._destination_path
    @property
    def initial_branch(self) -> str:
        return self._initial_branch
    @property
    def commit_message(self) -> str:
        return self._commit_message
    @property
    def author_name(self) -> str:
        return self._author_name
    @property
    def author_email(self) -> str:
        return self._author_email
    @property
    def committer_name(self) -> str:
        return self._committer_name
    @property
    def committer_email(self) -> str:
        return self._committer_email
    @property
    def timestamp(self) -> str:
        return self._timestamp

    def to_dict(self) -> dict[str, object]:
        return {
            "destination_path": self._destination_path,
            "initial_branch": self._initial_branch,
            "commit_message": self._commit_message,
            "author_name": self._author_name,
            "author_email": self._author_email,
            "committer_name": self._committer_name,
            "committer_email": self._committer_email,
            "timestamp": self._timestamp,
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GitEstablishmentPlan):
            return NotImplemented
        return (
            self._destination_path == other._destination_path
            and self._initial_branch == other._initial_branch
            and self._commit_message == other._commit_message
            and self._author_name == other._author_name
            and self._author_email == other._author_email
            and self._committer_name == other._committer_name
            and self._committer_email == other._committer_email
            and self._timestamp == other._timestamp
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._destination_path,
            self._initial_branch,
            self._commit_message,
            self._author_name,
            self._author_email,
            self._committer_name,
            self._committer_email,
            self._timestamp,
        ))


class GitEstablishmentResult:
    __slots__ = (
        "_status",
        "_phase",
        "_destination_path",
        "_git_version",
        "_initial_branch",
        "_root_commit",
        "_commit_tree",
        "_author_identity",
        "_committer_identity",
        "_timestamps",
        "_commit_message",
        "_staged_path_count",
        "_ignored_path_count",
        "_worktree_clean",
        "_remote_count",
        "_completed_phases",
        "_failure_reason",
        "_frozen",
    )

    def __init__(
        self,
        status: str,
        phase: str,
        destination_path: str,
        git_version: str = "",
        initial_branch: str = "",
        root_commit: str = "",
        commit_tree: str = "",
        author_identity: str = "",
        committer_identity: str = "",
        timestamps: str = "",
        commit_message: str = "",
        staged_path_count: int = 0,
        ignored_path_count: int = 0,
        worktree_clean: bool = False,
        remote_count: int = 0,
        completed_phases: list[str] | None = None,
        failure_reason: str | None = None,
    ) -> None:
        self._status = status
        self._phase = phase
        self._destination_path = destination_path
        self._git_version = git_version
        self._initial_branch = initial_branch
        self._root_commit = root_commit
        self._commit_tree = commit_tree
        self._author_identity = author_identity
        self._committer_identity = committer_identity
        self._timestamps = timestamps
        self._commit_message = commit_message
        self._staged_path_count = staged_path_count
        self._ignored_path_count = ignored_path_count
        self._worktree_clean = worktree_clean
        self._remote_count = remote_count
        self._completed_phases = list(completed_phases) if completed_phases is not None else []
        self._failure_reason = failure_reason
        self._frozen = True

    @property
    def status(self) -> str:
        return self._status
    @property
    def phase(self) -> str:
        return self._phase
    @property
    def destination_path(self) -> str:
        return self._destination_path
    @property
    def git_version(self) -> str:
        return self._git_version
    @property
    def initial_branch(self) -> str:
        return self._initial_branch
    @property
    def root_commit(self) -> str:
        return self._root_commit
    @property
    def commit_tree(self) -> str:
        return self._commit_tree
    @property
    def author_identity(self) -> str:
        return self._author_identity
    @property
    def committer_identity(self) -> str:
        return self._committer_identity
    @property
    def timestamps(self) -> str:
        return self._timestamps
    @property
    def commit_message(self) -> str:
        return self._commit_message
    @property
    def staged_path_count(self) -> int:
        return self._staged_path_count
    @property
    def ignored_path_count(self) -> int:
        return self._ignored_path_count
    @property
    def worktree_clean(self) -> bool:
        return self._worktree_clean
    @property
    def remote_count(self) -> int:
        return self._remote_count
    @property
    def completed_phases(self) -> list[str]:
        return list(self._completed_phases)
    @property
    def failure_reason(self) -> str | None:
        return self._failure_reason

    def to_dict(self) -> dict[str, object]:
        d: dict[str, object] = {
            "status": self._status,
            "phase": self._phase,
            "destination_path": self._destination_path,
            "git_version": self._git_version,
            "initial_branch": self._initial_branch,
            "root_commit": self._root_commit,
            "commit_tree": self._commit_tree,
            "author_identity": self._author_identity,
            "committer_identity": self._committer_identity,
            "timestamps": self._timestamps,
            "commit_message": self._commit_message,
            "staged_path_count": self._staged_path_count,
            "ignored_path_count": self._ignored_path_count,
            "worktree_clean": self._worktree_clean,
            "remote_count": self._remote_count,
            "completed_phases": self._completed_phases,
        }
        if self._failure_reason is not None:
            d["failure_reason"] = self._failure_reason
        return d

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GitEstablishmentResult):
            return NotImplemented
        return (
            self._status == other._status
            and self._phase == other._phase
            and self._destination_path == other._destination_path
            and self._git_version == other._git_version
            and self._initial_branch == other._initial_branch
            and self._root_commit == other._root_commit
            and self._commit_tree == other._commit_tree
            and self._author_identity == other._author_identity
            and self._committer_identity == other._committer_identity
            and self._timestamps == other._timestamps
            and self._commit_message == other._commit_message
            and self._staged_path_count == other._staged_path_count
            and self._ignored_path_count == other._ignored_path_count
            and self._worktree_clean == other._worktree_clean
            and self._remote_count == other._remote_count
            and self._completed_phases == other._completed_phases
            and self._failure_reason == other._failure_reason
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._status,
            self._phase,
            self._destination_path,
            self._git_version,
            self._initial_branch,
            self._root_commit,
            self._commit_tree,
            self._author_identity,
            self._committer_identity,
            self._timestamps,
            self._commit_message,
            self._staged_path_count,
            self._ignored_path_count,
            self._worktree_clean,
            self._remote_count,
            tuple(self._completed_phases),
            self._failure_reason,
        ))


class DestinationState:
    absent = "absent"
    empty_directory = "empty_directory"
    nonempty_directory = "nonempty_directory"
    regular_file = "regular_file"
    symlink = "symlink"
    unsupported = "unsupported"
    inaccessible = "inaccessible"


class PreflightDecision:
    allowed = "allowed"
    rejected = "rejected"


class TransactionPhase:
    preflight = "preflight"
    prepared = "prepared"
    committed = "committed"
    failed = "failed"
    rolled_back = "rolled_back"


class DestinationPreflight:
    __slots__ = (
        "_staging_path",
        "_destination_path",
        "_destination_state",
        "_destination_classification",
        "_same_filesystem",
        "_aliased",
        "_staging_inside_destination",
        "_destination_inside_staging",
        "_decision",
        "_rejection_reason",
        "_frozen",
    )

    def __init__(
        self,
        staging_path: str,
        destination_path: str,
        destination_state: str,
        same_filesystem: bool,
        aliased: bool,
        staging_inside_destination: bool,
        destination_inside_staging: bool,
        decision: str,
        rejection_reason: str | None = None,
    ) -> None:
        self._staging_path = staging_path
        self._destination_path = destination_path
        self._destination_state = destination_state
        self._destination_classification = destination_state
        self._same_filesystem = same_filesystem
        self._aliased = aliased
        self._staging_inside_destination = staging_inside_destination
        self._destination_inside_staging = destination_inside_staging
        self._decision = decision
        self._rejection_reason = rejection_reason
        self._frozen = True

    @property
    def staging_path(self) -> str:
        return self._staging_path

    @property
    def destination_path(self) -> str:
        return self._destination_path

    @property
    def destination_state(self) -> str:
        return self._destination_state

    @property
    def destination_classification(self) -> str:
        return self._destination_classification

    @property
    def same_filesystem(self) -> bool:
        return self._same_filesystem

    @property
    def aliased(self) -> bool:
        return self._aliased

    @property
    def staging_inside_destination(self) -> bool:
        return self._staging_inside_destination

    @property
    def destination_inside_staging(self) -> bool:
        return self._destination_inside_staging

    @property
    def decision(self) -> str:
        return self._decision

    @property
    def rejection_reason(self) -> str | None:
        return self._rejection_reason

    def to_dict(self) -> dict[str, object]:
        d: dict[str, object] = {
            "staging_path": self._staging_path,
            "destination_path": self._destination_path,
            "destination_classification": self._destination_classification,
            "same_filesystem": self._same_filesystem,
            "aliased": self._aliased,
            "staging_inside_destination": self._staging_inside_destination,
            "destination_inside_staging": self._destination_inside_staging,
            "decision": self._decision,
        }
        if self._rejection_reason is not None:
            d["rejection_reason"] = self._rejection_reason
        return d

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DestinationPreflight):
            return NotImplemented
        return (
            self._staging_path == other._staging_path
            and self._destination_path == other._destination_path
            and self._destination_state == other._destination_state
            and self._same_filesystem == other._same_filesystem
            and self._aliased == other._aliased
            and self._staging_inside_destination == other._staging_inside_destination
            and self._destination_inside_staging == other._destination_inside_staging
            and self._decision == other._decision
            and self._rejection_reason == other._rejection_reason
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._staging_path,
            self._destination_path,
            self._destination_state,
            self._same_filesystem,
            self._aliased,
            self._staging_inside_destination,
            self._destination_inside_staging,
            self._decision,
            self._rejection_reason,
        ))


class PromotionPlan:
    __slots__ = (
        "_staging_path",
        "_destination_path",
        "_destination_state",
        "_requires_preparation",
        "_same_filesystem",
        "_backup_path",
        "_frozen",
    )

    def __init__(
        self,
        staging_path: str,
        destination_path: str,
        destination_state: str,
        requires_preparation: bool,
        same_filesystem: bool,
        backup_path: str | None = None,
    ) -> None:
        self._staging_path = staging_path
        self._destination_path = destination_path
        self._destination_state = destination_state
        self._requires_preparation = requires_preparation
        self._same_filesystem = same_filesystem
        self._backup_path = backup_path
        self._frozen = True

    @property
    def staging_path(self) -> str:
        return self._staging_path

    @property
    def destination_path(self) -> str:
        return self._destination_path

    @property
    def destination_state(self) -> str:
        return self._destination_state

    @property
    def requires_preparation(self) -> bool:
        return self._requires_preparation

    @property
    def same_filesystem(self) -> bool:
        return self._same_filesystem

    @property
    def backup_path(self) -> str | None:
        return self._backup_path

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PromotionPlan):
            return NotImplemented
        return (
            self._staging_path == other._staging_path
            and self._destination_path == other._destination_path
            and self._destination_state == other._destination_state
            and self._requires_preparation == other._requires_preparation
            and self._same_filesystem == other._same_filesystem
            and self._backup_path == other._backup_path
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._staging_path,
            self._destination_path,
            self._destination_state,
            self._requires_preparation,
            self._same_filesystem,
            self._backup_path,
        ))


class PromotionResult:
    __slots__ = (
        "_status",
        "_transaction_state",
        "_destination_classification",
        "_staging_path",
        "_requested_destination",
        "_committed_destination",
        "_preserved_state",
        "_cleanup_state",
        "_failure_reason",
        "_frozen",
    )

    def __init__(
        self,
        status: str,
        transaction_state: str,
        destination_classification: str,
        staging_path: str,
        requested_destination: str,
        committed_destination: str | None = None,
        preserved_state: str | None = None,
        cleanup_state: str | None = None,
        failure_reason: str | None = None,
    ) -> None:
        self._status = status
        self._transaction_state = transaction_state
        self._destination_classification = destination_classification
        self._staging_path = staging_path
        self._requested_destination = requested_destination
        self._committed_destination = committed_destination
        self._preserved_state = preserved_state
        self._cleanup_state = cleanup_state
        self._failure_reason = failure_reason
        self._frozen = True

    @property
    def status(self) -> str:
        return self._status

    @property
    def transaction_state(self) -> str:
        return self._transaction_state

    @property
    def destination_classification(self) -> str:
        return self._destination_classification

    @property
    def staging_path(self) -> str:
        return self._staging_path

    @property
    def requested_destination(self) -> str:
        return self._requested_destination

    @property
    def committed_destination(self) -> str | None:
        return self._committed_destination

    @property
    def preserved_state(self) -> str | None:
        return self._preserved_state

    @property
    def cleanup_state(self) -> str | None:
        return self._cleanup_state

    @property
    def failure_reason(self) -> str | None:
        return self._failure_reason

    def to_dict(self) -> dict[str, object]:
        d: dict[str, object] = {
            "status": self._status,
            "transaction_state": self._transaction_state,
            "destination_classification": self._destination_classification,
            "staging_path": self._staging_path,
            "requested_destination": self._requested_destination,
        }
        if self._committed_destination is not None:
            d["committed_destination"] = self._committed_destination
        if self._preserved_state is not None:
            d["preserved_state"] = self._preserved_state
        if self._cleanup_state is not None:
            d["cleanup_state"] = self._cleanup_state
        if self._failure_reason is not None:
            d["failure_reason"] = self._failure_reason
        return d

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PromotionResult):
            return NotImplemented
        return (
            self._status == other._status
            and self._transaction_state == other._transaction_state
            and self._destination_classification == other._destination_classification
            and self._staging_path == other._staging_path
            and self._requested_destination == other._requested_destination
            and self._committed_destination == other._committed_destination
            and self._preserved_state == other._preserved_state
            and self._cleanup_state == other._cleanup_state
            and self._failure_reason == other._failure_reason
        )

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        return not result

    def __hash__(self) -> int:
        return hash((
            self._status,
            self._transaction_state,
            self._destination_classification,
            self._staging_path,
            self._requested_destination,
            self._committed_destination,
            self._preserved_state,
            self._cleanup_state,
            self._failure_reason,
        ))
