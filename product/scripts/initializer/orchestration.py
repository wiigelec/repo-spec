from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import GitObjectIdentity, ImmutableRequest, InitializerError
from .validation import validate_and_normalize


STANDARD_PROFILE = "standard"
STANDARD_WORKFLOW_ID = "product.full-initialization"


class OrchestrationError(InitializerError):
    def __init__(self, category: str, message: str) -> None:
        self.category = category
        self.message = message

    def __str__(self) -> str:
        return f"{self.category}: {self.message}"


@dataclass(frozen=True)
class WorkflowSelection:
    profile: str
    workflow_id: str


@dataclass(frozen=True)
class StandardWorkflowEntry:
    selection: WorkflowSelection
    request: ImmutableRequest

    @property
    def request_fingerprint(self) -> str:
        return self.request.request_fingerprint

    @property
    def canonical_request_bytes(self) -> bytes:
        return self.request.canonical_request_bytes


def select_standard_workflow(request: ImmutableRequest) -> WorkflowSelection:
    profile = request.profile if request.profile is not None else STANDARD_PROFILE
    if profile != STANDARD_PROFILE:
        raise OrchestrationError(
            "unsupported-execution-profile",
            f"execution profile {profile!r} maps to no supported Level 3 workflow",
        )
    if request.schema_version != "1":
        raise OrchestrationError(
            "unsupported-execution-profile",
            f"schema version {request.schema_version!r} maps to no supported Level 3 workflow",
        )
    return WorkflowSelection(
        profile=STANDARD_PROFILE,
        workflow_id=STANDARD_WORKFLOW_ID,
    )


def prepare_standard_workflow(raw_request: dict[str, Any], cwd: str) -> StandardWorkflowEntry:
    context = validate_and_normalize(raw_request, cwd)
    selection = select_standard_workflow(context.request)
    return StandardWorkflowEntry(selection=selection, request=context.request)


def canonical_requests_equivalent(left: ImmutableRequest, right: ImmutableRequest) -> bool:
    return left.canonical_request_bytes == right.canonical_request_bytes


def canonical_source_identity(request: ImmutableRequest) -> tuple[str, str, str]:
    revision: GitObjectIdentity = request.source_revision
    return (
        request.source_repository,
        revision.object_format,
        revision.object_id,
    )


def canonical_sources_equivalent(left: ImmutableRequest, right: ImmutableRequest) -> bool:
    return canonical_source_identity(left) == canonical_source_identity(right)


def canonical_direction_material(request: ImmutableRequest) -> tuple[str, ...]:
    return request.product_direction_material


def canonical_outcome_inputs_equivalent(
    left: StandardWorkflowEntry,
    right: StandardWorkflowEntry,
) -> bool:
    return (
        left.selection == right.selection
        and canonical_requests_equivalent(left.request, right.request)
        and canonical_sources_equivalent(left.request, right.request)
        and canonical_direction_material(left.request)
        == canonical_direction_material(right.request)
    )
