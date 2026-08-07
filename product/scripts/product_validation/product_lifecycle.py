"""Product-owned lifecycle and readiness validation."""

from __future__ import annotations

from validation.errors import fail
from validation.repository_checks import (
    ValidationContext,
    expect,
    get_development_document_records,
    repository_reference_specs,
)

from .product_development_documents import _product_development_roots


def check_product_lifecycle_readiness(context: ValidationContext) -> None:
    expect(context.product is not None, "product validation context missing")
    repository_specs = repository_reference_specs(context)
    records = get_development_document_records(
        context,
        development_roots=_product_development_roots(),
    )

    for plan_path, record in records.items():
        metadata = record.metadata
        if metadata["artifact_type"] != "implementation-plan":
            continue
        if metadata.get("lifecycle_status") not in {"accepted", "planning-complete"}:
            continue

        required_specs = metadata.get("applicable_accepted_specifications", [])
        if not required_specs:
            continue

        for spec_ref in required_specs:
            target_spec_id = (
                spec_ref.get("spec_id") if isinstance(spec_ref, dict) else spec_ref
            )
            if target_spec_id in context.product.specs:
                target_spec = context.product.specs[target_spec_id]
                expect(
                    target_spec["status"] == "accepted",
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"non-accepted specification {target_spec_id} "
                    f"(status: {target_spec['status']})",
                )
                manifest_entry = next(
                    (
                        entry
                        for entry in context.product.entries
                        if entry["spec_id"] == target_spec_id
                    ),
                    None,
                )
                expect(
                    manifest_entry is not None,
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"specification {target_spec_id} absent from product manifest",
                )
            elif target_spec_id in repository_specs:
                target_spec = repository_specs[target_spec_id]
                expect(
                    target_spec["status"] == "accepted",
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"non-accepted repository specification {target_spec_id} "
                    f"(status: {target_spec['status']})",
                )
            else:
                fail(
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"unknown specification {target_spec_id}"
                )

    for decomp_path, record in records.items():
        metadata = record.metadata
        if metadata["artifact_type"] != "product-decomposition":
            continue
        if metadata.get("lifecycle_status") not in {"accepted", "candidate"}:
            continue

        expected_spec_families = metadata.get("expected_specification_families", [])
        if not expected_spec_families:
            continue

        for family in expected_spec_families:
            expect(
                isinstance(family, dict),
                "lifecycle decomposition failed: expected_specification_families "
                f"entry must be an object in {decomp_path}",
            )
            expect(
                "level" in family,
                "lifecycle decomposition failed: expected_specification_families "
                f"entry missing level in {decomp_path}",
            )
            expect(
                "responsibility" in family,
                "lifecycle decomposition failed: expected_specification_families "
                f"entry missing responsibility in {decomp_path}",
            )
            expect(
                "dependency_direction" in family,
                "lifecycle decomposition failed: expected_specification_families "
                f"entry missing dependency_direction in {decomp_path}",
            )
