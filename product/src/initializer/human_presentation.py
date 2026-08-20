from __future__ import annotations

from dataclasses import replace
from typing import TextIO

from .orchestration import (
    FullInitializationActions,
    FullInitializationResult,
    TERMINAL_INDETERMINATE_PROMOTION,
    TERMINAL_PRE_PROMOTION_FAILURE,
    TERMINAL_PROMOTED_SUCCESS,
    TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
)


_PROGRESS = {
    "request_intake": "Reading and validating initialization request...",
    "source_resolution": "Resolving source material...",
    "staging_establishment": "Preparing initialization workspace...",
    "framework_installation": "Preparing repository contents...",
    "git_initialization": "Creating initial Git repository...",
    "repository_validation": "Validating prepared repository...",
    "promotion": "Promoting prepared repository to destination...",
}

_UPGRADE_PROGRESS = {
    "resolution": "Resolving accepted baseline and upgrade set...",
    "reconciliation": "Preparing staged managed reconciliation...",
    "reanchoring": "Materializing framework authority and preparing lineage...",
    "validation": "Validating staged repository...",
    "promotion": "Promoting validated repository...",
}


def present_upgrade_progress(phase: str, stream: TextIO) -> None:
    try:
        message = _UPGRADE_PROGRESS[phase]
    except KeyError as exc:
        raise ValueError(f"unsupported upgrade progress phase: {phase}") from exc
    print(message, file=stream)



def with_human_progress(
    actions: FullInitializationActions,
    stream: TextIO,
) -> FullInitializationActions:
    # Keep injected test doubles transparent. Production uses the exact
    # FullInitializationActions bundle built by H1 Patch 1; presentation
    # must not make dependency-injection seams semantically significant.
    if not isinstance(actions, FullInitializationActions):
        return actions

    replacements = {}
    for field_name, message in _PROGRESS.items():
        action = getattr(actions, field_name)

        def wrapped(carried, *, _action=action, _message=message):
            print(_message, file=stream)
            return _action(carried)

        replacements[field_name] = wrapped
    return replace(actions, **replacements)


def present_upgrade_terminal_result(
    result,
    target_repository: str,
    stream: TextIO,
) -> None:
    terminal = result.terminal_result
    reason = getattr(result, "failure_reason", None)

    if terminal == "promoted-success":
        print(f"Upgrade complete: {target_repository}", file=stream)
        print("Repository was promoted successfully.", file=stream)
        return

    if terminal in {
        "pre-promotion-failure",
        "rejected",
        "non-promoted",
    }:
        print("Upgrade did not complete successfully.", file=stream)
        if reason:
            print(f"Reason: {reason}", file=stream)
        print("Repository was not promoted.", file=stream)
        return

    if terminal == "indeterminate":
        print("Upgrade failed during promotion.", file=stream)
        if reason:
            print(f"Reason: {reason}", file=stream)
        print(
            "Promotion outcome is indeterminate; inspect the repository "
            "before retrying.",
            file=stream,
        )
        return

    if terminal == "promoted-with-finalization-error":
        print(f"Repository was promoted to: {target_repository}", file=stream)
        print("Upgrade finalization did not complete cleanly.", file=stream)
        if reason:
            print(f"Reason: {reason}", file=stream)
        print(
            "Repository was promoted; do not treat this as a pre-promotion failure.",
            file=stream,
        )
        return

    raise ValueError(
        f"unsupported upgrade terminal result for human presentation: {terminal}"
    )



def present_terminal_result(
    result: FullInitializationResult,
    destination: str,
    stream: TextIO,
) -> None:
    terminal = result.terminal_result
    lifecycle = getattr(result, "lifecycle", None)

    # Preserve the Patch 1 dependency-injection seam. Production full
    # initialization results always carry lifecycle detail; focused CLI tests
    # may inject the smaller public result shape established by Patch 1.
    if lifecycle is None:
        if terminal == TERMINAL_PROMOTED_SUCCESS:
            print(f"Initialization complete: {destination}", file=stream)
            print("Destination was promoted successfully.", file=stream)
            return
        print(f"Initialization ended: {terminal}", file=stream)
        return

    if terminal == TERMINAL_PROMOTED_SUCCESS:
        print(f"Initialization complete: {destination}", file=stream)
        print("Destination was promoted successfully.", file=stream)
        return

    if terminal == TERMINAL_PRE_PROMOTION_FAILURE:
        print("Initialization failed before promotion.", file=stream)
        if lifecycle.failed_stage:
            print(f"Failed step: {lifecycle.failed_stage}", file=stream)
        if lifecycle.diagnostic:
            print(f"Reason: {lifecycle.diagnostic}", file=stream)
        print("Destination was not promoted.", file=stream)
        return

    if terminal == TERMINAL_INDETERMINATE_PROMOTION:
        print("Initialization failed during promotion.", file=stream)
        if lifecycle.diagnostic:
            print(f"Reason: {lifecycle.diagnostic}", file=stream)
        print(
            "Promotion outcome is indeterminate; inspect the destination and "
            "canonical execution records before retrying.",
            file=stream,
        )
        return

    if terminal == TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR:
        print(f"Repository was promoted to: {destination}", file=stream)
        print("Initialization finalization did not complete cleanly.", file=stream)
        if lifecycle.diagnostic:
            print(f"Reason: {lifecycle.diagnostic}", file=stream)
        print(
            "Destination was promoted; do not treat this as a pre-promotion failure.",
            file=stream,
        )
        return

    raise ValueError(f"unsupported terminal result for human presentation: {terminal}")
