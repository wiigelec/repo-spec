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
from initializer.models import SourceSelection
from initializer.validation import validate_json_request, load_request, validate_request


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: repo-spec-init <command> [<args>]", file=sys.stderr)
        print("commands:", file=sys.stderr)
        print("  validate-request  <request.json>                        validate a request", file=sys.stderr)
        print("  inspect-source    <request.json>                        validate request, source, and inventory", file=sys.stderr)
        print("  stage-framework   <request.json> [--staging-parent <d>] stage reusable framework material", file=sys.stderr)
        return 1

    command = argv[2]

    if command == "validate-request":
        return _cmd_validate_request(argv)
    elif command == "inspect-source":
        return _cmd_inspect_source(argv)
    elif command == "stage-framework":
        return _cmd_stage_framework(argv)
    else:
        print(f"unknown command: {command}", file=sys.stderr)
        print("commands: validate-request, inspect-source, stage-framework", file=sys.stderr)
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


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
