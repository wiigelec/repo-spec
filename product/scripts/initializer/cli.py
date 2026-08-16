from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from initializer.inventory import InventoryError
from initializer.foundations import FoundationPlan, FoundationError
from initializer.models import SourceSelection
from initializer.full_initialization_actions import build_full_initialization_actions
from initializer.human_presentation import present_terminal_result, with_human_progress
from initializer.orchestration import execute_full_initialization
from initializer.validation import (
    ValidationError,
    validate_json_request,
    load_request,
    validate_request,
    validate_product_foundation_prerequisites,
    ValidationResult,
)


def main(argv: list[str]) -> int:
    if len(argv) == 5 and argv[2] == "init" and argv[3] == "--repo":
        return _cmd_init_repo(argv)
    if len(argv) == 5 and argv[2] == "upgrade" and argv[3] == "--repo":
        return _cmd_upgrade_repo(argv)
    if len(argv) >= 4 and argv[2] == "--request":
        return _cmd_initialize(argv)

    if len(argv) < 3:
        print("usage: repo-spec init --repo <destination>", file=sys.stderr)
        print("       repo-spec upgrade --repo <existing-repo>", file=sys.stderr)
        print("developer interface: repo-spec-init --request <request.json>", file=sys.stderr)
        print("diagnostic commands:", file=sys.stderr)
        print("  validate-request    <request.json>", file=sys.stderr)
        print("  inspect-source      <request.json>", file=sys.stderr)
        print("  preflight-request   <request.json>", file=sys.stderr)
        print("  establish-staging   <request.json>", file=sys.stderr)
        print("  realize-materials   <request.json>", file=sys.stderr)
        print("  complete-i2         <request.json>", file=sys.stderr)
        print("  promote             <staging-path> <dest-path>", file=sys.stderr)
        print("  git-preflight       <dest-path>", file=sys.stderr)
        print("  git-establish       <dest-path>", file=sys.stderr)
        return 1

    command = argv[2]
    dispatch = {
        "validate-request": _cmd_validate_request,
        "inspect-source": _cmd_inspect_source,
        "preflight-request": _cmd_preflight_request,
        "establish-staging": _cmd_establish_staging,
        "realize-materials": _cmd_realize_materials,
        "complete-i2": _cmd_complete_i2,
        "promote": _cmd_promote,
        "git-preflight": _cmd_git_preflight,
        "git-establish": _cmd_git_establish,
    }
    if command in {
        "stage-framework",
        "stage-framework-and-foundations",
        "promote-staging",
        "stage-and-promote",
        "stage-promote-and-git",
    }:
        print(f"command unavailable: {command}", file=sys.stderr)
        return 1

    handler = dispatch.get(command)
    if handler is None:
        print(f"unknown command: {command}", file=sys.stderr)
        print("usage: repo-spec init --repo <destination>", file=sys.stderr)
        print("       repo-spec upgrade --repo <existing-repo>", file=sys.stderr)
        print("developer interface: repo-spec-init --request <request.json>", file=sys.stderr)
        return 1
    return handler(argv)


def _cmd_init_repo(argv: list[str]) -> int:
    destination = argv[4]
    stage_parent = Path(destination).expanduser().resolve().parent
    stage_names_before = tuple(sorted(
        p.name for p in stage_parent.iterdir()
        if p.name.startswith("repo-spec-stage-")
    )) if stage_parent.is_dir() else ()
    raw = {"schema_version": "2", "destination": destination}
    try:
        print("Repository bootstrap started.", file=sys.stderr)
        actions = with_human_progress(
            build_full_initialization_actions(argv[1]),
            sys.stderr,
        )
        result = execute_full_initialization(raw, os.getcwd(), actions)
    except Exception as exc:
        print(f"Repository bootstrap failed before workflow completion: {exc}", file=sys.stderr)
        print("Destination was not promoted by a completed workflow.", file=sys.stderr)
        return 1
    present_terminal_result(result, destination, sys.stderr)
    if not result.succeeded and result.lifecycle.terminal_result == "pre-promotion-failure":
        try:
            from initializer.staging import cleanup_failed_staging_for_destination
            removed = cleanup_failed_staging_for_destination(destination, stage_names_before)
            if removed:
                print("Cleaned failed bootstrap staging: " + ", ".join(removed), file=sys.stderr)
        except Exception as exc:
            print(f"Warning: failed bootstrap staging cleanup did not complete: {exc}", file=sys.stderr)
    return 0 if result.succeeded else 1


def _cmd_upgrade_repo(argv: list[str]) -> int:
    target_repository = argv[4]
    try:
        from initializer.upgrade_orchestration import execute_repository_upgrade

        result = execute_repository_upgrade(target_repository, argv[1])
    except Exception as exc:
        print(f"Repository upgrade failed before workflow completion: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0 if result.succeeded else 1


def _cmd_initialize(argv: list[str]) -> int:
    if len(argv) != 4 or argv[2] != "--request":
        print("usage: repo-spec-init --request <request.json>", file=sys.stderr)
        return 1
    try:
        raw = load_request(Path(argv[3]))
        destination = raw.get("destination")
        print("Initialization started.", file=sys.stderr)
        actions = with_human_progress(
            build_full_initialization_actions(argv[1]),
            sys.stderr,
        )
        result = execute_full_initialization(
            raw,
            os.getcwd(),
            actions,
        )
    except Exception as exc:
        print(f"Initialization failed before workflow completion: {exc}", file=sys.stderr)
        print("Destination was not promoted by a completed workflow.", file=sys.stderr)
        return 1

    present_terminal_result(result, str(destination), sys.stderr)
    return 0 if result.succeeded else 1


def _cmd_validate_request(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init validate-request <request.json>", file=sys.stderr)
        return 1
    request_path = Path(argv[3])
    return validate_json_request(request_path, os.getcwd())


def _cmd_inspect_source(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init inspect-source <request.json>", file=sys.stderr)
        return 1

    request_path = Path(argv[3])

    try:
        raw = load_request(request_path)
    except (InventoryError, ValidationError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    result = validate_request(raw, os.getcwd())
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw, os.getcwd())
    request = ctx.request
    from initializer.inventory import resolve_source_material
    try:
        resolved = resolve_source_material(
            request.source_repository,
            request.source_revision.object_id,
            request.product_direction_material,
        )
    except InventoryError as exc:
        print(f"source selection error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({
        "status": "resolved",
        "repository": resolved.repository,
        "revision": resolved.commit_id,
        "request_fingerprint": request.request_fingerprint,
        "manifest_entries": len(resolved.manifest),
        "direction_material": list(resolved.direction_material),
    }, indent=2, ensure_ascii=False))
    return 0


def _cmd_preflight_request(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        return 1
    request_path = Path(argv[3])
    try:
        raw = load_request(request_path)
        from initializer.validation import validate_and_normalize
        request = validate_and_normalize(raw, os.getcwd()).request
        from initializer.inventory import resolve_source_material
        source = resolve_source_material(
            request.source_repository,
            request.source_revision.object_id,
            request.product_direction_material,
        )
        from initializer.destination import i1_destination_preflight
        destination = i1_destination_preflight(request.destination)
    except Exception as exc:
        print(f"preflight error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "status": "i1-preflight-passed",
        "request_fingerprint": request.request_fingerprint,
        "source_repository": source.repository,
        "source_revision": source.commit_id,
        "manifest_entries": len(source.manifest),
        "direction_material": list(source.direction_material),
        "destination": destination.to_dict(),
    }, indent=2, ensure_ascii=False))
    return 0


def _cmd_establish_staging(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init establish-staging <request.json>", file=sys.stderr)
        return 1
    try:
        raw = load_request(Path(argv[3]))
        from initializer.validation import validate_and_normalize
        request = validate_and_normalize(raw, os.getcwd()).request
        from initializer.inventory import resolve_source_material
        source = resolve_source_material(
            request.source_repository,
            request.source_revision.object_id,
            request.product_direction_material,
        )
        from initializer.destination import i1_destination_preflight
        destination = i1_destination_preflight(request.destination)
        from initializer.staging import I2StagingInputs, establish_staging_workspace
        workspace = establish_staging_workspace(
            I2StagingInputs(request, source, destination)
        )
    except Exception as exc:
        print(f"staging error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(workspace.to_dict(), indent=2, ensure_ascii=False))
    return 0

def _cmd_realize_materials(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init realize-materials <request.json>", file=sys.stderr)
        return 1

    workspace = None
    try:
        raw = load_request(Path(argv[3]))
        from initializer.validation import validate_and_normalize
        request = validate_and_normalize(raw, os.getcwd()).request
        from initializer.inventory import resolve_source_material
        source = resolve_source_material(
            request.source_repository,
            request.source_revision.object_id,
            request.product_direction_material,
        )
        from initializer.destination import i1_destination_preflight
        destination = i1_destination_preflight(request.destination)
        from initializer.staging import (
            I2StagingInputs,
            establish_staging_workspace,
            realize_i2_materials,
            _cleanup_staging,
        )
        workspace = establish_staging_workspace(
            I2StagingInputs(request, source, destination)
        )
        from initializer.foundations import build_foundation_plan
        foundation_plan = build_foundation_plan(
            request.product_id,
            list(source.direction_material),
            request.authority["granted_by"],
        )
        result = realize_i2_materials(workspace, foundation_plan)
    except Exception as exc:
        if workspace is not None:
            try:
                _cleanup_staging(workspace.root)
            except Exception:
                pass
        print(f"material realization error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_complete_i2(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init complete-i2 <request.json>", file=sys.stderr)
        return 1

    workspace = None
    try:
        raw = load_request(Path(argv[3]))
        from initializer.validation import validate_and_normalize
        request = validate_and_normalize(raw, os.getcwd()).request
        from initializer.inventory import resolve_source_material
        source = resolve_source_material(
            request.source_repository,
            request.source_revision.object_id,
            request.product_direction_material,
        )
        from initializer.destination import i1_destination_preflight
        destination = i1_destination_preflight(request.destination)
        from initializer.staging import (
            I2StagingInputs,
            establish_staging_workspace,
            realize_i2_materials,
            build_i2_exit_state,
            _cleanup_staging,
        )
        workspace = establish_staging_workspace(I2StagingInputs(request, source, destination))
        from initializer.foundations import build_foundation_plan
        foundation_plan = build_foundation_plan(
            request.product_id,
            list(source.direction_material),
            request.authority["granted_by"],
        )
        realization = realize_i2_materials(workspace, foundation_plan)
        exit_state = build_i2_exit_state(realization)
    except Exception as exc:
        if workspace is not None:
            try:
                _cleanup_staging(workspace.root)
            except Exception:
                pass
        print(f"I2 completion error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(exit_state.to_dict(), indent=2, ensure_ascii=False))
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

    result = validate_request(raw, os.getcwd())
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw, os.getcwd())
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
                request.source_repository, request.source_revision.object_id,
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

    result = validate_request(raw, os.getcwd())
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw, os.getcwd())
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
                request.source_repository, request.source_revision.object_id,
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
    governing_issue = request.authority["granted_by"]

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

    result = validate_request(raw, os.getcwd())
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw, os.getcwd())

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

    result = validate_request(raw, os.getcwd())
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw, os.getcwd())
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
                request.source_repository, request.source_revision.object_id,
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
        governing_issue = request.authority["granted_by"]
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


def _cmd_git_preflight(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing destination path", file=sys.stderr)
        print("usage: repo-spec-init git-preflight <dest-path>", file=sys.stderr)
        return 1

    dest_path = argv[3]
    from initializer.git import git_preflight
    preflight = git_preflight(dest_path)
    output = preflight.to_dict()
    output["_type"] = "git_preflight"
    print(json.dumps(output, indent=2))

    if preflight.decision != "allowed":
        return 1
    return 0


def _cmd_git_establish(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing destination path", file=sys.stderr)
        print("usage: repo-spec-init git-establish <dest-path>", file=sys.stderr)
        return 1

    dest_path = argv[3]

    from initializer.git import initialize_promoted_destination as _init_promoted

    result = _init_promoted(dest_path)
    output = result.to_dict()
    output["_type"] = "git_establishment"
    print(json.dumps(output, indent=2))

    if result.status != "success":
        return 1
    return 0


def _cmd_stage_promote_and_git(argv: list[str]) -> int:
    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init stage-promote-and-git <request.json> [--staging-parent <dir>]", file=sys.stderr)
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

    result = validate_request(raw, os.getcwd())
    if not result.is_valid:
        for err in result.errors:
            print(f"validation error: {err}", file=sys.stderr)
        return 1

    from initializer.validation import validate_and_normalize
    ctx = validate_and_normalize(raw, os.getcwd())
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
                request.source_repository, request.source_revision.object_id,
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
        governing_issue = request.authority["granted_by"]
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

    prom_output = prom_result.to_dict()

    git_result = None
    if prom_result.status == "success":
        dest_path = prom_result.committed_destination or request.destination
        from initializer.git import initialize_promoted_destination
        git_result = initialize_promoted_destination(dest_path, prom_output)

    output: dict[str, object] = {
        "status": "stage_promote_git_complete" if (prom_result.status == "success" and git_result is not None and git_result.status == "success") else "stage_promote_git_failed",
        "installation": inst_result.to_dict(),
    }
    if fnd_result is not None:
        output["foundations"] = fnd_result.to_dict()
    output["promotion"] = prom_output
    if git_result is not None:
        output["git_establishment"] = git_result.to_dict()
    else:
        output["git_establishment"] = None

    print(json.dumps(output, indent=2))

    if git_result is not None and git_result.status != "success":
        return 1
    if prom_result.status != "success":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
