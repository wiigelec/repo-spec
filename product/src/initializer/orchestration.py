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
    if request.schema_version != "2":
        raise OrchestrationError(
            "unsupported-execution-profile",
            f"schema version {request.schema_version!r} maps to no supported bootstrap workflow",
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


def canonical_outcome_inputs_equivalent(
    left: StandardWorkflowEntry,
    right: StandardWorkflowEntry,
) -> bool:
    return (
        left.selection == right.selection
        and canonical_requests_equivalent(left.request, right.request)
    )


CANONICAL_STANDARD_STAGES = (
    "request-intake",
    "source-resolution",
    "destination-preflight",
    "staging-establishment",
    "framework-installation",
    "direction-evidence-installation",
    "workspace-seeding",
    "provenance-recording",
    "handoff-assembly",
    "git-initialization",
    "repository-validation",
    "promotion",
    "success-finalization",
)

PROMOTION_STAGE = "promotion"
SUCCESS_FINALIZATION_STAGE = "success-finalization"

TERMINAL_PRE_PROMOTION_FAILURE = "pre-promotion-failure"
TERMINAL_PROMOTED_SUCCESS = "promoted-success"
TERMINAL_INDETERMINATE_PROMOTION = "indeterminate-promotion"
TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR = "promoted-with-finalization-error"

STAGE_COMPLETED = "completed"
PROMOTION_PROMOTED = "promoted"
PROMOTION_INDETERMINATE = "indeterminate"
FINALIZATION_CLEANUP_FAILURE = "cleanup-failure"


@dataclass(frozen=True)
class StageStep:
    stage_id: str
    action: Any
    precondition: Any = None


@dataclass(frozen=True)
class LifecycleResult:
    terminal_result: str
    completed_stages: tuple[str, ...]
    failed_stage: str | None
    promotion_outcome: str
    diagnostic: str | None

    @property
    def succeeded(self) -> bool:
        return self.terminal_result == TERMINAL_PROMOTED_SUCCESS


def canonical_standard_stage_ids() -> tuple[str, ...]:
    return CANONICAL_STANDARD_STAGES


def _validate_standard_steps(steps: tuple[StageStep, ...]) -> None:
    ids = tuple(step.stage_id for step in steps)
    if ids != CANONICAL_STANDARD_STAGES:
        raise OrchestrationError(
            "invalid-stage-sequence",
            "standard workflow must contain all 13 required canonical stages in exact order",
        )
    if len(set(ids)) != len(ids):
        raise OrchestrationError(
            "invalid-stage-sequence",
            "standard workflow stage identifiers must be unique",
        )


def execute_standard_lifecycle(steps: tuple[StageStep, ...]) -> LifecycleResult:
    _validate_standard_steps(steps)

    completed: list[str] = []
    promotion_outcome = "not-promoted"

    for step in steps:
        if step.precondition is not None and not bool(step.precondition(tuple(completed))):
            return LifecycleResult(
                terminal_result=TERMINAL_PRE_PROMOTION_FAILURE,
                completed_stages=tuple(completed),
                failed_stage=step.stage_id,
                promotion_outcome=promotion_outcome,
                diagnostic="stage precondition failed",
            )

        try:
            outcome = step.action()
        except Exception as exc:
            if step.stage_id == PROMOTION_STAGE:
                return LifecycleResult(
                    terminal_result=TERMINAL_INDETERMINATE_PROMOTION,
                    completed_stages=tuple(completed),
                    failed_stage=PROMOTION_STAGE,
                    promotion_outcome=PROMOTION_INDETERMINATE,
                    diagnostic=str(exc),
                )
            if step.stage_id == SUCCESS_FINALIZATION_STAGE:
                return LifecycleResult(
                    terminal_result=TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
                    completed_stages=tuple(completed),
                    failed_stage=SUCCESS_FINALIZATION_STAGE,
                    promotion_outcome=PROMOTION_PROMOTED,
                    diagnostic=str(exc),
                )
            return LifecycleResult(
                terminal_result=TERMINAL_PRE_PROMOTION_FAILURE,
                completed_stages=tuple(completed),
                failed_stage=step.stage_id,
                promotion_outcome=promotion_outcome,
                diagnostic=str(exc),
            )

        if step.stage_id == PROMOTION_STAGE:
            if outcome == PROMOTION_INDETERMINATE:
                return LifecycleResult(
                    terminal_result=TERMINAL_INDETERMINATE_PROMOTION,
                    completed_stages=tuple(completed),
                    failed_stage=PROMOTION_STAGE,
                    promotion_outcome=PROMOTION_INDETERMINATE,
                    diagnostic="promotion outcome is indeterminate",
                )
            if outcome != PROMOTION_PROMOTED:
                return LifecycleResult(
                    terminal_result=TERMINAL_PRE_PROMOTION_FAILURE,
                    completed_stages=tuple(completed),
                    failed_stage=PROMOTION_STAGE,
                    promotion_outcome="not-promoted",
                    diagnostic="promotion did not commit",
                )
            promotion_outcome = PROMOTION_PROMOTED
            completed.append(step.stage_id)
            continue

        if step.stage_id == SUCCESS_FINALIZATION_STAGE:
            if promotion_outcome != PROMOTION_PROMOTED:
                raise OrchestrationError(
                    "invalid-terminal-transition",
                    "success-finalization cannot execute before committed promotion",
                )
            if outcome == FINALIZATION_CLEANUP_FAILURE:
                return LifecycleResult(
                    terminal_result=TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
                    completed_stages=tuple(completed),
                    failed_stage=SUCCESS_FINALIZATION_STAGE,
                    promotion_outcome=PROMOTION_PROMOTED,
                    diagnostic="post-promotion cleanup failed",
                )
            if outcome != STAGE_COMPLETED:
                return LifecycleResult(
                    terminal_result=TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
                    completed_stages=tuple(completed),
                    failed_stage=SUCCESS_FINALIZATION_STAGE,
                    promotion_outcome=PROMOTION_PROMOTED,
                    diagnostic="success-finalization did not complete",
                )
            completed.append(step.stage_id)
            return LifecycleResult(
                terminal_result=TERMINAL_PROMOTED_SUCCESS,
                completed_stages=tuple(completed),
                failed_stage=None,
                promotion_outcome=PROMOTION_PROMOTED,
                diagnostic=None,
            )

        if outcome != STAGE_COMPLETED:
            return LifecycleResult(
                terminal_result=TERMINAL_PRE_PROMOTION_FAILURE,
                completed_stages=tuple(completed),
                failed_stage=step.stage_id,
                promotion_outcome=promotion_outcome,
                diagnostic=f"stage returned non-completed outcome: {outcome!r}",
            )
        completed.append(step.stage_id)

    raise OrchestrationError(
        "invalid-terminal-transition",
        "canonical workflow exhausted without success-finalization result",
    )


@dataclass(frozen=True)
class FullInitializationActions:
    request_intake: Any
    source_resolution: Any
    destination_preflight: Any
    staging_establishment: Any
    framework_installation: Any
    direction_evidence_installation: Any
    workspace_seeding: Any
    provenance_recording: Any
    handoff_assembly: Any
    git_initialization: Any
    repository_validation: Any
    promotion: Any
    success_finalization: Any


@dataclass(frozen=True)
class FullInitializationResult:
    entry: StandardWorkflowEntry
    lifecycle: LifecycleResult

    @property
    def terminal_result(self) -> str:
        return self.lifecycle.terminal_result

    @property
    def succeeded(self) -> bool:
        return self.lifecycle.succeeded


def _full_initialization_steps(
    entry: StandardWorkflowEntry,
    actions: FullInitializationActions,
) -> tuple[StageStep, ...]:
    carried: dict[str, Any] = {"entry": entry}

    def stage(name: str, action: Any, predecessor_keys: tuple[str, ...] = ()) -> StageStep:
        def precondition(_completed: tuple[str, ...]) -> bool:
            return all(key in carried for key in predecessor_keys)

        def invoke():
            value = action(carried)
            carried[name] = value
            if name == PROMOTION_STAGE:
                return value
            if name == SUCCESS_FINALIZATION_STAGE:
                return value
            return STAGE_COMPLETED

        return StageStep(name, invoke, precondition)

    return (
        stage("request-intake", actions.request_intake),
        stage("source-resolution", actions.source_resolution, ("request-intake",)),
        stage("destination-preflight", actions.destination_preflight, ("request-intake",)),
        stage("staging-establishment", actions.staging_establishment, ("destination-preflight",)),
        stage("framework-installation", actions.framework_installation, ("staging-establishment",)),
        stage(
            "direction-evidence-installation",
            actions.direction_evidence_installation,
            ("framework-installation",),
        ),
        stage("workspace-seeding", actions.workspace_seeding, ("direction-evidence-installation",)),
        stage("provenance-recording", actions.provenance_recording, ("workspace-seeding",)),
        stage("handoff-assembly", actions.handoff_assembly, ("workspace-seeding",)),
        stage(
            "git-initialization",
            actions.git_initialization,
            ("provenance-recording", "handoff-assembly"),
        ),
        stage("repository-validation", actions.repository_validation, ("git-initialization",)),
        stage("promotion", actions.promotion, ("repository-validation",)),
        stage("success-finalization", actions.success_finalization, ("promotion",)),
    )


def execute_full_initialization(
    raw_request: dict[str, Any],
    cwd: str,
    actions: FullInitializationActions,
) -> FullInitializationResult:
    """Execute the complete accepted standard bounded workflow.

    Request validation/profile selection occurs before any stage action. The
    action bundle adapts maintained I1-I4 stage implementations into the I5
    canonical lifecycle without reinterpreting their owned semantics.
    """
    entry = prepare_standard_workflow(raw_request, cwd)
    lifecycle = execute_standard_lifecycle(_full_initialization_steps(entry, actions))
    return FullInitializationResult(entry=entry, lifecycle=lifecycle)
