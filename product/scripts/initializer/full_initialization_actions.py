from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .destination import i1_destination_preflight, promote_finalized_repository
from .foundations import build_foundation_plan
from .git import initialize_i3_git_repository
from .handoff import write_handoff_manifest
from .inventory import resolve_source_material
from .orchestration import (
    CANONICAL_STANDARD_STAGES,
    FINALIZATION_CLEANUP_FAILURE,
    STAGE_COMPLETED,
    FullInitializationActions,
)
from .provenance import ProvenanceInputs, write_provenance_record
from .staging import (
    I2StagingInputs,
    establish_staging_workspace,
    finalize_validation_records,
    realize_i2_materials,
)
from .validation import (
    RepositoryValidationInputs,
    validate_repository_v1,
    _i4_repository_digest,
)

INITIALIZER_NAME = "repo-spec-init"
INITIALIZER_VERSION = "1"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_full_initialization_actions(
    *,
    initialization_timestamp: str | None = None,
) -> FullInitializationActions:
    timestamp = initialization_timestamp or _utc_timestamp()

    def request_intake(carried: dict[str, Any]):
        return carried["entry"].request

    def source_resolution(carried: dict[str, Any]):
        request = carried["request-intake"]
        return resolve_source_material(
            request.source_repository,
            request.source_revision.object_id,
            request.product_direction_material,
        )

    def destination_preflight(carried: dict[str, Any]):
        return i1_destination_preflight(carried["request-intake"].destination)

    def staging_establishment(carried: dict[str, Any]):
        return establish_staging_workspace(I2StagingInputs(
            carried["request-intake"],
            carried["source-resolution"],
            carried["destination-preflight"],
        ))

    def framework_installation(carried: dict[str, Any]):
        request = carried["request-intake"]
        plan = build_foundation_plan(
            request.product_id,
            list(carried["source-resolution"].direction_material),
            request.authority["granted_by"],
        )
        return realize_i2_materials(carried["staging-establishment"], plan)

    def direction_evidence_installation(carried: dict[str, Any]):
        return carried["framework-installation"]

    def workspace_seeding(carried: dict[str, Any]):
        return carried["framework-installation"]

    def provenance_recording(carried: dict[str, Any]):
        return write_provenance_record(
            carried["staging-establishment"],
            ProvenanceInputs(
                initializer_name=INITIALIZER_NAME,
                initializer_version=INITIALIZER_VERSION,
                initialization_timestamp=timestamp,
            ),
        )

    def handoff_assembly(carried: dict[str, Any]):
        return write_handoff_manifest(carried["workspace-seeding"])

    def git_initialization(carried: dict[str, Any]):
        return initialize_i3_git_repository(
            carried["staging-establishment"].repository_path
        )

    def repository_validation(carried: dict[str, Any]):
        workspace = carried["staging-establishment"]
        digest = _i4_repository_digest(workspace.repository_path)
        validation_run = validate_repository_v1(
            RepositoryValidationInputs(workspace, digest)
        )
        pair = finalize_validation_records(
            workspace,
            validation_run,
            initializer_version=INITIALIZER_VERSION,
            completed_stages=CANONICAL_STANDARD_STAGES[:10],
        )
        if not pair.promotion_gate_open():
            raise RuntimeError("repository validation failed; promotion gate is closed")
        return pair

    def promotion(carried: dict[str, Any]):
        result = promote_finalized_repository(
            carried["staging-establishment"],
            carried["repository-validation"],
        )
        carried["i4-promotion-result"] = result
        return result.promotion_outcome

    def success_finalization(carried: dict[str, Any]):
        result = carried["i4-promotion-result"]
        if result.completion_status == "promoted-with-finalization-error":
            return FINALIZATION_CLEANUP_FAILURE
        return STAGE_COMPLETED

    return FullInitializationActions(
        request_intake=request_intake,
        source_resolution=source_resolution,
        destination_preflight=destination_preflight,
        staging_establishment=staging_establishment,
        framework_installation=framework_installation,
        direction_evidence_installation=direction_evidence_installation,
        workspace_seeding=workspace_seeding,
        provenance_recording=provenance_recording,
        handoff_assembly=handoff_assembly,
        git_initialization=git_initialization,
        repository_validation=repository_validation,
        promotion=promotion,
        success_finalization=success_finalization,
    )
