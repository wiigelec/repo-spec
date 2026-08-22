from __future__ import annotations

import io
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from initializer import cli
from initializer.human_presentation import (
    present_terminal_result,
    present_upgrade_terminal_result,
    with_human_progress,
)
from initializer.orchestration import (
    FINALIZATION_CLEANUP_FAILURE,
    FullInitializationActions,
    FullInitializationResult,
    LifecycleResult,
    PROMOTION_INDETERMINATE,
    PROMOTION_PROMOTED,
    STAGE_COMPLETED,
    StandardWorkflowEntry,
    TERMINAL_INDETERMINATE_PROMOTION,
    TERMINAL_PRE_PROMOTION_FAILURE,
    TERMINAL_PROMOTED_SUCCESS,
    TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
)


# validation-metadata: {"role": "helper"}
def fake_full_result(
    terminal: str,
    *,
    failed_stage: str | None = None,
    promotion_outcome: str = "not-promoted",
    diagnostic: str | None = None,
) -> SimpleNamespace:
    lifecycle = SimpleNamespace(
        terminal_result=terminal,
        failed_stage=failed_stage,
        promotion_outcome=promotion_outcome,
        diagnostic=diagnostic,
    )
    return SimpleNamespace(
        terminal_result=terminal,
        lifecycle=lifecycle,
        succeeded=terminal == TERMINAL_PROMOTED_SUCCESS,
    )


# validation-metadata: {"role": "helper"}
def inert_actions(calls: list[str]) -> FullInitializationActions:
    names = (
        "request_intake",
        "source_resolution",
        "destination_preflight",
        "staging_establishment",
        "framework_installation",
        "direction_evidence_installation",
        "workspace_seeding",
        "provenance_recording",
        "handoff_assembly",
        "git_initialization",
        "repository_validation",
        "promotion",
        "success_finalization",
    )

    # validation-metadata: {"role": "helper"}
    def make(name):
        # validation-metadata: {"role": "helper"}
        def action(_carried):
            calls.append(name)
            if name == "promotion":
                return PROMOTION_PROMOTED
            if name == "success_finalization":
                return STAGE_COMPLETED
            return name
        return action

    return FullInitializationActions(**{name: make(name) for name in names})


class H1TerminalPresentationTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_minimal_patch1_result_shape_remains_supported(self):
        result = SimpleNamespace(
            terminal_result=TERMINAL_PROMOTED_SUCCESS,
            succeeded=True,
        )
        stream = io.StringIO()
        present_terminal_result(result, "/tmp/out", stream)
        text = stream.getvalue()
        self.assertIn("Initialization complete: /tmp/out", text)
        self.assertIn("promoted successfully", text)

    # validation-metadata: {"role": "helper"}
    def test_cli_announces_start_and_success_destination(self):
        raw = {"schema_version": "2", "destination": "/tmp/created"}
        result = fake_full_result(
            TERMINAL_PROMOTED_SUCCESS,
            promotion_outcome=PROMOTION_PROMOTED,
        )
        with patch.object(cli, "load_request", return_value=raw), \
             patch.object(cli, "build_full_initialization_actions", return_value=inert_actions([])), \
             patch.object(cli, "execute_full_initialization", return_value=result), \
             patch("sys.stderr", new_callable=io.StringIO) as err:
            rc = cli.main(
                ["repo-spec-init", "repo-root", "--request", "request.json"]
            )
        self.assertEqual(rc, 0)
        text = err.getvalue()
        self.assertIn("Initialization started.", text)
        self.assertIn("Initialization complete: /tmp/created", text)
        self.assertIn("promoted successfully", text)

    # validation-metadata: {"role": "helper"}
    def test_pre_promotion_failure_says_destination_not_promoted(self):
        result = fake_full_result(
            TERMINAL_PRE_PROMOTION_FAILURE,
            failed_stage="repository-validation",
            diagnostic="validation failed",
        )
        stream = io.StringIO()
        present_terminal_result(result, "/tmp/out", stream)
        text = stream.getvalue()
        self.assertIn("failed before promotion", text)
        self.assertIn("repository-validation", text)
        self.assertIn("validation failed", text)
        self.assertIn("not promoted", text)

    # validation-metadata: {"role": "helper"}
    def test_indeterminate_promotion_never_claims_destination_state(self):
        result = fake_full_result(
            TERMINAL_INDETERMINATE_PROMOTION,
            failed_stage="promotion",
            promotion_outcome=PROMOTION_INDETERMINATE,
            diagnostic="rename outcome indeterminate",
        )
        stream = io.StringIO()
        present_terminal_result(result, "/tmp/out", stream)
        text = stream.getvalue()
        self.assertIn("indeterminate", text)
        self.assertIn("inspect the destination", text)
        self.assertNotIn("Destination was not promoted.", text)
        self.assertNotIn("promoted successfully", text)

    # validation-metadata: {"role": "helper"}
    def test_promoted_finalization_error_explicitly_preserves_promotion(self):
        result = fake_full_result(
            TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
            failed_stage="success-finalization",
            promotion_outcome=PROMOTION_PROMOTED,
            diagnostic="post-promotion cleanup failed",
        )
        stream = io.StringIO()
        present_terminal_result(result, "/tmp/out", stream)
        text = stream.getvalue()
        self.assertIn("Repository was promoted to: /tmp/out", text)
        self.assertIn("finalization did not complete cleanly", text)
        self.assertIn("Destination was promoted", text)


    # validation-metadata: {"role": "helper"}
    def test_upgrade_success_presentation_matches_public_cli_style(self):
        result = SimpleNamespace(
            terminal_result="promoted-success",
            succeeded=True,
            failure_reason=None,
        )
        stream = io.StringIO()
        present_upgrade_terminal_result(result, "/tmp/repo", stream)
        text = stream.getvalue()
        self.assertIn("Upgrade complete: /tmp/repo", text)
        self.assertIn("promoted successfully", text)
        self.assertNotIn("{", text)
        self.assertNotIn("upgrade_set_fingerprint", text)

    # validation-metadata: {"role": "helper"}
    def test_upgrade_pre_promotion_failure_reports_reason_and_no_promotion(self):
        result = SimpleNamespace(
            terminal_result="pre-promotion-failure",
            succeeded=False,
            failure_reason="validation failed",
        )
        stream = io.StringIO()
        present_upgrade_terminal_result(result, "/tmp/repo", stream)
        text = stream.getvalue()
        self.assertIn("did not complete successfully", text)
        self.assertIn("validation failed", text)
        self.assertIn("not promoted", text)

    # validation-metadata: {"role": "helper"}
    def test_upgrade_indeterminate_does_not_claim_final_state(self):
        result = SimpleNamespace(
            terminal_result="indeterminate",
            succeeded=False,
            failure_reason="rename outcome indeterminate",
        )
        stream = io.StringIO()
        present_upgrade_terminal_result(result, "/tmp/repo", stream)
        text = stream.getvalue()
        self.assertIn("indeterminate", text)
        self.assertIn("inspect the repository", text)
        self.assertNotIn("promoted successfully", text)
        self.assertNotIn("Repository was not promoted.", text)

    # validation-metadata: {"role": "helper"}
    def test_upgrade_promoted_finalization_error_preserves_promotion_fact(self):
        result = SimpleNamespace(
            terminal_result="promoted-with-finalization-error",
            succeeded=False,
            failure_reason="cleanup failed",
        )
        stream = io.StringIO()
        present_upgrade_terminal_result(result, "/tmp/repo", stream)
        text = stream.getvalue()
        self.assertIn("Repository was promoted to: /tmp/repo", text)
        self.assertIn("finalization did not complete cleanly", text)
        self.assertIn("Repository was promoted", text)

    # validation-metadata: {"role": "helper"}
    def test_progress_wrapper_preserves_action_return_values_and_order(self):
        calls = []
        base = inert_actions(calls)
        stream = io.StringIO()
        wrapped = with_human_progress(base, stream)
        carried = {}
        self.assertEqual(wrapped.source_resolution(carried), "source_resolution")
        self.assertEqual(wrapped.repository_validation(carried), "repository_validation")
        self.assertEqual(calls, ["source_resolution", "repository_validation"])
        text = stream.getvalue()
        self.assertIn("Resolving source material", text)
        self.assertIn("Validating prepared repository", text)

    # validation-metadata: {"role": "helper"}
    def test_human_presentation_does_not_mutate_terminal_result(self):
        result = fake_full_result(
            TERMINAL_PRE_PROMOTION_FAILURE,
            failed_stage="git-initialization",
            diagnostic="git failed",
        )
        before = (
            result.lifecycle.terminal_result,
            result.lifecycle.failed_stage,
            result.lifecycle.promotion_outcome,
            result.lifecycle.diagnostic,
        )
        stream = io.StringIO()
        present_terminal_result(result, "/tmp/out", stream)
        after = (
            result.lifecycle.terminal_result,
            result.lifecycle.failed_stage,
            result.lifecycle.promotion_outcome,
            result.lifecycle.diagnostic,
        )
        self.assertEqual(before, after)

    # validation-metadata: {"role": "helper"}
    def test_no_interactive_or_field_defaulting_surface_is_added(self):
        stderr = io.StringIO()
        with patch("sys.stderr", stderr):
            rc = cli.main([
                "repo-spec-init",
                "repo-root",
                "--destination",
                "/tmp/out",
            ])
        self.assertEqual(rc, 1)
        self.assertIn("unknown command", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
