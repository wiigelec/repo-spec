"""Product-owned lifecycle and readiness validation."""

from __future__ import annotations

from validation.errors import fail
from .context import ValidationContext
from validation.errors import expect
from .development_documents import get_development_document_records

from .product_development_documents import _product_development_roots


def check_product_lifecycle_readiness(context: ValidationContext) -> None:
    product_specs = context.product.specs if context.product is not None else {}
    product_entries = context.product.entries if context.product is not None else []
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
        if context.product is None:
            continue

        authority_entries = metadata.get("workstream_authority", [])
        expect(authority_entries, f"lifecycle plan failed: plan {plan_path} lacks workstream authority")
        seen_ids: set[str] = set()
        for authority in authority_entries:
            workstream_id = authority["id"]
            expect(
                workstream_id not in seen_ids,
                f"lifecycle plan failed: plan {plan_path} has duplicate workstream authority identifier {workstream_id}",
            )
            seen_ids.add(workstream_id)
            for target_spec_id in authority["controlling_product_specifications"]:
                if target_spec_id not in product_specs:
                    fail(
                        f"lifecycle plan failed: plan {plan_path} references "
                        f"unknown specification {target_spec_id}"
                    )
                target_spec = product_specs[target_spec_id]
                expect(
                    target_spec["status"] == "accepted",
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"non-accepted specification {target_spec_id} "
                    f"(status: {target_spec['status']})",
                )
                manifest_entry = next(
                    (entry for entry in product_entries if entry["spec_id"] == target_spec_id),
                    None,
                )
                expect(
                    manifest_entry is not None and manifest_entry.get("status") == "accepted",
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"specification {target_spec_id} without accepted product-manifest registration",
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
