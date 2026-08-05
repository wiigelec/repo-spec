from __future__ import annotations

import json
import sys
from pathlib import Path

from initializer.inventory import (
    resolve_inventory_path,
    load_inventory,
    validate_and_load_inventory,
    resolve_source_selection_from_request,
    inventory_to_ordered_dict,
    InventoryError,
)
from initializer.foundations import FoundationPlan, FoundationError
from initializer.models import SourceSelection
from initializer.validation import (
    validate_json_request,
    load_request,
    validate_request,
    validate_product_foundation_prerequisites,
    ValidationResult,
)


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: repo-spec-init <command> [<args>]", file=sys.stderr)
        print("commands:", file=sys.stderr)
        print("  validate-request                  <request.json>                        validate a request", file=sys.stderr)
        print("  inspect-source                    <request.json>                        validate request, source, and inventory", file=sys.stderr)
        print("  stage-framework                   <request.json> [--staging-parent <d>] stage reusable framework material", file=sys.stderr)
        print("  stage-framework-and-foundations   <request.json> [--staging-parent <d>] stage framework and establish product foundations", file=sys.stderr)
        print("  preflight-destination             <staging-path> <dest-path>            run destination preflight check", file=sys.stderr)
        print("  promote                           <staging-path> <dest-path>            promote staging result to destination", file=sys.stderr)
        print("  promote-staging                   <request.json>                        promote completed staging result to destination", file=sys.stderr)
        print("  stage-and-promote                 <request.json> [--staging-parent <d>] stage, establish foundations, and promote", file=sys.stderr)
        return 1

    command = argv[2]

    if command == "validate-request":
        return _cmd_validate_request(argv)
    elif command == "inspect-source":
        return _cmd_inspect_source(argv)
    elif command == "stage-framework":
        return _cmd_stage_framework(argv)
    elif command == "stage-framework-and-foundations":
        return _cmd_stage_framework_and_foundations(argv)
    elif command == "preflight-destination":
        return _cmd_preflight_destination(argv)
    elif command == "promote":
        return _cmd_promote(argv)
    elif command == "promote-staging":
        return _cmd_promote_staging(argv)
    elif command == "stage-and-promote":
        return _cmd_stage_and_promote(argv)
    else:
        print(f"unknown command: {command}", file=sys.stderr)
        print("commands: validate-request, inspect-source, stage-framework, stage-framework-and-foundations, preflight-destination, promote, promote-staging, stage-and-promote", file=sys.stderr)
        return 1


def _cmd_validate_request(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init validate-request <request.json>", file=sys.stderr)
        return 1
    request_path = Path(argv[3])
    return validate_json_request(request_path)


def _cmd_inspect_source(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init inspect-source <request.json>", file=sys.stderr)
        return 1

    request_path = Path(argv[3])

    try:
        raw = load_request(request_path)
    except InventoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = validate_request(raw)
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw)
    request = ctx.request

    repo_root = Path(argv[1]).resolve()
    inventory_path = resolve_inventory_path(repo_root)
    try:
        inv_raw = load_inventory(inventory_path)
    except InventoryError as exc:
        print(f"inventory error: {exc}", file=sys.stderr)
        return 1

    source_sel = None
    if request.source_repository is not None or request.source_revision is not None:
        try:
            source_sel = resolve_source_selection_from_request(
                request.source_repository, request.source_revision,
            )
        except InventoryError as exc:
            print(f"source selection error: {exc}", file=sys.stderr)
            return 1

    try:
        classified = validate_and_load_inventory(inv_raw, source_sel)
    except InventoryError as exc:
        print(f"inventory validation error: {exc}", file=sys.stderr)
        return 1

    output = inventory_to_ordered_dict(classified, source_sel)
    output["status"] = "inspection_complete"
    print(json.dumps(output, indent=2))
    return 0


def _cmd_stage_framework(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init stage-framework <request.json> [--staging-parent <dir>]", file=sys.stderr)
        return 1

    request_path = Path(argv[3])

    staging_parent: Path | None = None
    if len(argv) >= 6 and argv[4] == "--staging-parent":
        staging_parent = Path(argv[5])

    try:
        raw = load_request(request_path)
    except (InventoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = validate_request(raw)
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw)
    request = ctx.request

    repo_root = Path(argv[1]).resolve()
    inventory_path = resolve_inventory_path(repo_root)
    try:
        inv_raw = load_inventory(inventory_path)
    except InventoryError as exc:
        print(f"inventory error: {exc}", file=sys.stderr)
        return 1

    source_sel: SourceSelection | None = None
    if request.source_repository is not None or request.source_revision is not None:
        try:
            source_sel = resolve_source_selection_from_request(
                request.source_repository, request.source_revision,
            )
        except InventoryError as exc:
            print(f"source selection error: {exc}", file=sys.stderr)
            return 1

    try:
        classified = validate_and_load_inventory(inv_raw, source_sel)
    except InventoryError as exc:
        print(f"inventory validation error: {exc}", file=sys.stderr)
        return 1

    from initializer.staging import stage_framework, StagingError, resolve_source_root

    if source_sel is None:
        print("error: source selection is required for framework staging", file=sys.stderr)
        return 1

    source_root = resolve_source_root(source_sel.revision, repo_root)

    try:
        inst_result = stage_framework(
            classified=classified,
            source_selection=source_sel,
            source_root=source_root,
            staging_parent=staging_parent,
        )
    except StagingError as exc:
        print(f"staging error: {exc}", file=sys.stderr)
        return 1

    output = inst_result.to_dict()
    output["status"] = "staging_complete"
    print(json.dumps(output, indent=2))
    return 0


def _cmd_stage_framework_and_foundations(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init stage-framework-and-foundations <request.json> [--staging-parent <dir>]", file=sys.stderr)
        return 1

    request_path = Path(argv[3])

    staging_parent: Path | None = None
    if len(argv) >= 6 and argv[4] == "--staging-parent":
        staging_parent = Path(argv[5])

    try:
        raw = load_request(request_path)
    except (InventoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = validate_request(raw)
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw)
    request = ctx.request

    # Validate product-foundation prerequisites
    foundation_result_outer = ValidationResult()
    validate_product_foundation_prerequisites(raw, foundation_result_outer)
    if not foundation_result_outer.is_valid:
        for err in foundation_result_outer.errors:
            print(f"foundation validation error: {err}", file=sys.stderr)
        return 1

    repo_root = Path(argv[1]).resolve()
    inventory_path = resolve_inventory_path(repo_root)
    try:
        inv_raw = load_inventory(inventory_path)
    except InventoryError as exc:
        print(f"inventory error: {exc}", file=sys.stderr)
        return 1

    source_sel: SourceSelection | None = None
    if request.source_repository is not None or request.source_revision is not None:
        try:
            source_sel = resolve_source_selection_from_request(
                request.source_repository, request.source_revision,
            )
        except InventoryError as exc:
            print(f"source selection error: {exc}", file=sys.stderr)
            return 1

    try:
        classified = validate_and_load_inventory(inv_raw, source_sel)
    except InventoryError as exc:
        print(f"inventory validation error: {exc}", file=sys.stderr)
        return 1

    from initializer.staging import stage_framework_and_foundations, StagingError, resolve_source_root

    if source_sel is None:
        print("error: source selection is required for framework staging", file=sys.stderr)
        return 1

    source_root = resolve_source_root(source_sel.revision, repo_root)

    product_id = request.product_id or ""
    direction_material = request.product_direction_material or []
    governing_issue = request.authority.get("granted_by", "issue-195")

    try:
        fplan = FoundationPlan(
            product_id=product_id,
            direction_material=direction_material,
            governing_issue=governing_issue,
        )
    except FoundationError as exc:
        print(f"foundation plan error: {exc}", file=sys.stderr)
        return 1

    try:
        inst_result, fnd_result = stage_framework_and_foundations(
            classified=classified,
            source_selection=source_sel,
            source_root=source_root,
            foundation_plan=fplan,
            staging_parent=staging_parent,
        )
    except (StagingError, FoundationError) as exc:
        print(f"stage error: {exc}", file=sys.stderr)
        return 1

    output: dict[str, object] = {
        "status": "stage_and_foundations_complete",
        "installation": inst_result.to_dict(),
    }
    if fnd_result is not None:
        output["foundations"] = fnd_result.to_dict()

    print(json.dumps(output, indent=2))
    return 0


def _cmd_preflight_destination(argv: list[str]) -> int:
    if len(argv) < 5:
        print("error: missing staging-path and dest-path", file=sys.stderr)
        print("usage: repo-spec-init preflight-destination <staging-path> <dest-path>", file=sys.stderr)
        return 1

    staging_path = argv[3]
    dest_path = argv[4]

    from initializer.destination import destination_preflight

    preflight = destination_preflight(staging_path, dest_path)
    output = preflight.to_dict()
    output["_type"] = "preflight"
    print(json.dumps(output, indent=2))

    if preflight.decision == "rejected":
        return 1
    return 0


def _cmd_promote(argv: list[str]) -> int:
    if len(argv) < 5:
        print("error: missing staging-path and dest-path", file=sys.stderr)
        print("usage: repo-spec-init promote <staging-path> <dest-path>", file=sys.stderr)
        return 1

    staging_path = argv[3]
    dest_path = argv[4]

    from initializer.promotion import promote

    result = promote(staging_path, dest_path)
    output = result.to_dict()
    output["_type"] = "promotion"
    print(json.dumps(output, indent=2))

    if result.status == "failed":
        return 1
    return 0


def _cmd_promote_staging(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init promote-staging <request.json> [--staging-path <dir>]", file=sys.stderr)
        return 1

    request_path = Path(argv[3])

    explicit_staging_path: str | None = None
    if len(argv) >= 6 and argv[4] == "--staging-path":
        explicit_staging_path = argv[5]

    try:
        raw = load_request(request_path)
    except (InventoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = validate_request(raw)
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw)

    from initializer.models import ImmutableRequest
    request = ctx.request

    if explicit_staging_path is not None:
        staging_path = explicit_staging_path
    else:
        from initializer.staging import STAGING_PREFIX
        print("error: --staging-path is required when auto-detection is not available", file=sys.stderr)
        return 1

    from initializer.promotion import promote
    result = promote(staging_path, request.destination)
    output = result.to_dict()
    output["_type"] = "promotion"
    print(json.dumps(output, indent=2))

    if result.status == "failed":
        return 1
    return 0


def _cmd_stage_and_promote(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init stage-and-promote <request.json> [--staging-parent <dir>]", file=sys.stderr)
        return 1

    request_path = Path(argv[3])

    staging_parent: Path | None = None
    if len(argv) >= 6 and argv[4] == "--staging-parent":
        staging_parent = Path(argv[5])

    try:
        raw = load_request(request_path)
    except (InventoryError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = validate_request(raw)
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw)
    request = ctx.request

    validate_product_foundation_prerequisites(raw, result)
    has_product = result.is_valid
    result_outer = ValidationResult()
    if has_product:
        validate_product_foundation_prerequisites(raw, result_outer)

    repo_root = Path(argv[1]).resolve()
    inventory_path = resolve_inventory_path(repo_root)
    try:
        inv_raw = load_inventory(inventory_path)
    except InventoryError as exc:
        print(f"inventory error: {exc}", file=sys.stderr)
        return 1

    source_sel: SourceSelection | None = None
    if request.source_repository is not None or request.source_revision is not None:
        try:
            source_sel = resolve_source_selection_from_request(
                request.source_repository, request.source_revision,
            )
        except InventoryError as exc:
            print(f"source selection error: {exc}", file=sys.stderr)
            return 1

    try:
        classified = validate_and_load_inventory(inv_raw, source_sel)
    except InventoryError as exc:
        print(f"inventory validation error: {exc}", file=sys.stderr)
        return 1

    from initializer.staging import stage_framework_and_foundations, StagingError, resolve_source_root

    if source_sel is None:
        print("error: source selection is required for staging", file=sys.stderr)
        return 1

    source_root = resolve_source_root(source_sel.revision, repo_root)

    fplan: FoundationPlan | None = None
    if has_product:
        product_id = request.product_id or ""
        direction_material = request.product_direction_material or []
        governing_issue = request.authority.get("granted_by", "issue-197")
        try:
            fplan = FoundationPlan(
                product_id=product_id,
                direction_material=direction_material,
                governing_issue=governing_issue,
            )
        except FoundationError as exc:
            print(f"foundation plan error: {exc}", file=sys.stderr)
            return 1

    try:
        inst_result, fnd_result = stage_framework_and_foundations(
            classified=classified,
            source_selection=source_sel,
            source_root=source_root,
            foundation_plan=fplan,
            staging_parent=staging_parent,
        )
    except (StagingError, FoundationError) as exc:
        print(f"stage error: {exc}", file=sys.stderr)
        return 1

    from initializer.promotion import promote

    staging_workspace = inst_result.staging_workspace
    prom_result = promote(staging_workspace, request.destination)

    output: dict[str, object] = {
        "status": "stage_and_promotion_complete" if prom_result.status == "success" else "stage_and_promotion_failed",
        "installation": inst_result.to_dict(),
    }
    if fnd_result is not None:
        output["foundations"] = fnd_result.to_dict()
    output["promotion"] = prom_result.to_dict()

    print(json.dumps(output, indent=2))

    if prom_result.status == "failed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
