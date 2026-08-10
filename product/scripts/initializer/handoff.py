from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .models import InitializerError
from .provenance import PROVENANCE_RELATIVE_PATH
from .staging import I2RealizationResult, validate_staging_workspace


class HandoffError(InitializerError):
    pass


HANDOFF_RELATIVE_PATH = Path("repo/initializer/handoff.json")
NEXT_ACTION = (
    "Develop and accept the product overview and decomposition, then create product "
    "specifications. Create an implementation plan only after the controlling "
    "specifications are accepted."
)
ROOT_FIELD_ORDER = (
    "schema_version",
    "foundations",
    "material",
    "provenance",
    "next_action",
)
FOUNDATION_FIELD_ORDER = ("framework", "product")
MATERIAL_FIELD_ORDER = ("generated", "selected", "omitted", "deferred")


@dataclass(frozen=True)
class HandoffClassifications:
    framework: tuple[str, ...]
    product: tuple[str, ...]
    generated: tuple[str, ...]
    selected: tuple[str, ...]
    omitted: tuple[str, ...]
    deferred: tuple[str, ...]

    def present_paths(self) -> frozenset[str]:
        return frozenset(
            self.framework + self.product + self.generated + self.selected
        )

    def all_paths(self) -> tuple[str, ...]:
        return (
            self.framework
            + self.product
            + self.generated
            + self.selected
            + self.omitted
            + self.deferred
        )


@dataclass(frozen=True)
class HandoffResult:
    path: Path
    byte_length: int
    classifications: HandoffClassifications


def _validate_path(path: str) -> None:
    if (
        not isinstance(path, str)
        or not path
        or path.startswith("/")
        or "\\" in path
        or "%" in path
    ):
        raise HandoffError(f"invalid handoff repository-relative path: {path!r}")
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise HandoffError(f"non-canonical handoff path: {path!r}")


def _sorted_unique(paths: tuple[str, ...] | list[str], label: str) -> tuple[str, ...]:
    for path in paths:
        _validate_path(path)
    if len(set(paths)) != len(paths):
        raise HandoffError(f"duplicate path in {label}")
    return tuple(sorted(paths))


def _regular_files(repository: Path) -> frozenset[str]:
    files: set[str] = set()
    for path in repository.rglob("*"):
        relative = path.relative_to(repository).as_posix()
        if relative == ".git" or relative.startswith(".git/"):
            raise HandoffError("Git administrative state is not allowed before handoff")
        if path.is_symlink():
            raise HandoffError(
                f"handoff prepared repository contains unsupported symlink: {relative}"
            )
        if path.is_file():
            files.add(relative)
    return frozenset(files)


def _is_product_foundation(path: str, product_id: str) -> bool:
    if path in {
        f"product/docs/overview/{product_id}-OVERVIEW.md",
        f"product/docs/decompositions/{product_id}-DECOMPOSITION.md",
        f"product/docs/plans/{product_id}-IMPLEMENTATION-PLAN.md",
        "product/specs/product/level-0/README.md",
        "product/specs/product/level-1/README.md",
        "product/specs/product/level-2/README.md",
        "product/specs/product/level-3/README.md",
    }:
        return True
    return (
        path.startswith(f"product/docs/overview/{product_id}-overview/")
        or path.startswith(f"product/docs/decompositions/{product_id}-decomposition/")
        or path.startswith(f"product/docs/plans/{product_id}-implementation-plan/")
    )


def classify_handoff(
    realization: I2RealizationResult,
    *,
    omitted: tuple[str, ...] = (),
    deferred: tuple[str, ...] = (),
) -> HandoffClassifications:
    workspace = realization.workspace
    validate_staging_workspace(workspace)

    framework = _sorted_unique(list(realization.framework_paths), "foundations.framework")
    foundation_paths = _sorted_unique(
        list(realization.foundation_paths),
        "I2 foundation paths",
    )
    product: list[str] = []
    selected: list[str] = []
    generated: list[str] = []

    for path in foundation_paths:
        if path.startswith("product/docs/direction/evidence/"):
            selected.append(path)
        else:
            generated.append(path)

    provenance = PROVENANCE_RELATIVE_PATH.as_posix()
    handoff = HANDOFF_RELATIVE_PATH.as_posix()
    generated.extend([provenance, handoff])

    classifications = HandoffClassifications(
        framework=_sorted_unique(framework, "foundations.framework"),
        product=_sorted_unique(product, "foundations.product"),
        generated=_sorted_unique(generated, "material.generated"),
        selected=_sorted_unique(selected, "material.selected"),
        omitted=_sorted_unique(list(omitted), "material.omitted"),
        deferred=_sorted_unique(list(deferred), "material.deferred"),
    )

    all_paths = classifications.all_paths()
    if len(set(all_paths)) != len(all_paths):
        raise HandoffError("handoff classification arrays are not mutually disjoint")

    repository_files_before = _regular_files(workspace.repository_path)
    if provenance not in repository_files_before:
        raise HandoffError("provenance record must exist before handoff assembly")
    if handoff in repository_files_before:
        raise HandoffError("handoff manifest destination already exists")

    expected_before = classifications.present_paths() - {handoff}
    if repository_files_before != expected_before:
        missing = sorted(expected_before - repository_files_before)
        undeclared = sorted(repository_files_before - expected_before)
        raise HandoffError(
            f"prepared repository classification mismatch: missing={missing}, "
            f"undeclared={undeclared}"
        )

    absent = set(classifications.omitted) | set(classifications.deferred)
    present_absent = sorted(absent & repository_files_before)
    if present_absent:
        raise HandoffError(
            f"omitted/deferred path is present in prepared repository: {present_absent}"
        )

    return classifications


def build_handoff_manifest(
    classifications: HandoffClassifications,
) -> dict[str, object]:
    manifest: dict[str, object] = {
        "schema_version": "2",
        "foundations": {
            "framework": list(classifications.framework),
            "product": list(classifications.product),
        },
        "material": {
            "generated": list(classifications.generated),
            "selected": list(classifications.selected),
            "omitted": list(classifications.omitted),
            "deferred": list(classifications.deferred),
        },
        "provenance": PROVENANCE_RELATIVE_PATH.as_posix(),
        "next_action": NEXT_ACTION,
    }
    if tuple(manifest.keys()) != ROOT_FIELD_ORDER:
        raise HandoffError("handoff root field order drifted")
    foundations = manifest["foundations"]
    material = manifest["material"]
    if not isinstance(foundations, dict) or tuple(foundations.keys()) != FOUNDATION_FIELD_ORDER:
        raise HandoffError("handoff foundations field order drifted")
    if not isinstance(material, dict) or tuple(material.keys()) != MATERIAL_FIELD_ORDER:
        raise HandoffError("handoff material field order drifted")
    return manifest


def serialize_handoff_manifest(manifest: dict[str, object]) -> bytes:
    if tuple(manifest.keys()) != ROOT_FIELD_ORDER:
        raise HandoffError("handoff contains unknown, missing, or reordered root fields")
    if manifest.get("schema_version") != "2":
        raise HandoffError("unsupported handoff schema_version")
    foundations = manifest.get("foundations")
    material = manifest.get("material")
    if not isinstance(foundations, dict) or tuple(foundations.keys()) != FOUNDATION_FIELD_ORDER:
        raise HandoffError("handoff foundations fields are not closed and ordered")
    if not isinstance(material, dict) or tuple(material.keys()) != MATERIAL_FIELD_ORDER:
        raise HandoffError("handoff material fields are not closed and ordered")
    if manifest.get("provenance") != PROVENANCE_RELATIVE_PATH.as_posix():
        raise HandoffError("handoff provenance path drifted")
    if manifest.get("next_action") != NEXT_ACTION:
        raise HandoffError("handoff next_action drifted")
    return (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_handoff_manifest(
    realization: I2RealizationResult,
    *,
    omitted: tuple[str, ...] = (),
    deferred: tuple[str, ...] = (),
) -> HandoffResult:
    classifications = classify_handoff(
        realization,
        omitted=omitted,
        deferred=deferred,
    )
    manifest = build_handoff_manifest(classifications)
    payload = serialize_handoff_manifest(manifest)

    destination = realization.workspace.repository_path / HANDOFF_RELATIVE_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise HandoffError("handoff manifest destination already exists")
    destination.write_bytes(payload)
    if destination.read_bytes() != payload:
        raise HandoffError("handoff manifest write verification failed")

    final_files = _regular_files(realization.workspace.repository_path)
    if final_files != classifications.present_paths():
        raise HandoffError("final prepared repository is not completely classified")

    return HandoffResult(
        path=destination,
        byte_length=len(payload),
        classifications=classifications,
    )
