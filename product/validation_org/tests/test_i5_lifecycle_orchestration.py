from __future__ import annotations

import unittest

from initializer.orchestration import (
    CANONICAL_STANDARD_STAGES,
    FINALIZATION_CLEANUP_FAILURE,
    PROMOTION_INDETERMINATE,
    PROMOTION_PROMOTED,
    STAGE_COMPLETED,
    TERMINAL_INDETERMINATE_PROMOTION,
    TERMINAL_PRE_PROMOTION_FAILURE,
    TERMINAL_PROMOTED_SUCCESS,
    TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
    OrchestrationError,
    StageStep,
    canonical_standard_stage_ids,
    execute_standard_lifecycle,
)


def steps(
    *,
    fail_stage: str | None = None,
    precondition_fail_stage: str | None = None,
    promotion_outcome: str = PROMOTION_PROMOTED,
    finalization_outcome: str = STAGE_COMPLETED,
    calls: list[str] | None = None,
) -> tuple[StageStep, ...]:
    sink = calls if calls is not None else []
    result = []

    for stage_id in CANONICAL_STANDARD_STAGES:
        def action(stage_id=stage_id):
            sink.append(stage_id)
            if stage_id == fail_stage:
                raise RuntimeError(f"{stage_id} failed")
            if stage_id == "promotion":
                return promotion_outcome
            if stage_id == "success-finalization":
                return finalization_outcome
            return STAGE_COMPLETED

        precondition = None
        if stage_id == precondition_fail_stage:
            precondition = lambda _completed: False

        result.append(StageStep(stage_id, action, precondition))

    return tuple(result)


class I5LifecycleOrchestrationTests(unittest.TestCase):
    def test_canonical_standard_stage_order_is_exactly_thirteen_required_stages(self) -> None:
        self.assertEqual(len(canonical_standard_stage_ids()), 13)
        self.assertEqual(
            canonical_standard_stage_ids(),
            (
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
            ),
        )

    def test_promoted_success_executes_every_stage_once_in_order(self) -> None:
        calls: list[str] = []
        result = execute_standard_lifecycle(steps(calls=calls))
        self.assertEqual(calls, list(CANONICAL_STANDARD_STAGES))
        self.assertEqual(result.terminal_result, TERMINAL_PROMOTED_SUCCESS)
        self.assertEqual(result.completed_stages, CANONICAL_STANDARD_STAGES)
        self.assertEqual(result.promotion_outcome, "promoted")
        self.assertIsNone(result.failed_stage)
        self.assertTrue(result.succeeded)

    def test_pre_promotion_failure_halts_without_later_stage_execution(self) -> None:
        calls: list[str] = []
        result = execute_standard_lifecycle(
            steps(fail_stage="git-initialization", calls=calls)
        )
        self.assertEqual(result.terminal_result, TERMINAL_PRE_PROMOTION_FAILURE)
        self.assertEqual(result.failed_stage, "git-initialization")
        self.assertEqual(result.promotion_outcome, "not-promoted")
        self.assertNotIn("repository-validation", calls)
        self.assertNotIn("promotion", calls)
        self.assertNotIn("success-finalization", calls)

    def test_failed_precondition_halts_before_stage_action(self) -> None:
        calls: list[str] = []
        result = execute_standard_lifecycle(
            steps(precondition_fail_stage="repository-validation", calls=calls)
        )
        self.assertEqual(result.terminal_result, TERMINAL_PRE_PROMOTION_FAILURE)
        self.assertEqual(result.failed_stage, "repository-validation")
        self.assertNotIn("repository-validation", calls)
        self.assertNotIn("promotion", calls)

    def test_indeterminate_promotion_halts_and_never_finalizes_success(self) -> None:
        calls: list[str] = []
        result = execute_standard_lifecycle(
            steps(promotion_outcome=PROMOTION_INDETERMINATE, calls=calls)
        )
        self.assertEqual(result.terminal_result, TERMINAL_INDETERMINATE_PROMOTION)
        self.assertEqual(result.failed_stage, "promotion")
        self.assertEqual(result.promotion_outcome, "indeterminate")
        self.assertNotIn("promotion", result.completed_stages)
        self.assertNotIn("success-finalization", calls)

    def test_promotion_exception_is_indeterminate_and_not_retried(self) -> None:
        calls: list[str] = []
        result = execute_standard_lifecycle(
            steps(fail_stage="promotion", calls=calls)
        )
        self.assertEqual(result.terminal_result, TERMINAL_INDETERMINATE_PROMOTION)
        self.assertEqual(calls.count("promotion"), 1)
        self.assertNotIn("success-finalization", calls)

    def test_cleanup_failure_preserves_promoted_outcome(self) -> None:
        result = execute_standard_lifecycle(
            steps(finalization_outcome=FINALIZATION_CLEANUP_FAILURE)
        )
        self.assertEqual(
            result.terminal_result,
            TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
        )
        self.assertEqual(result.failed_stage, "success-finalization")
        self.assertEqual(result.promotion_outcome, "promoted")
        self.assertIn("promotion", result.completed_stages)
        self.assertNotIn("success-finalization", result.completed_stages)
        self.assertFalse(result.succeeded)

    def test_success_finalization_exception_is_promoted_with_finalization_error(self) -> None:
        result = execute_standard_lifecycle(
            steps(fail_stage="success-finalization")
        )
        self.assertEqual(
            result.terminal_result,
            TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
        )
        self.assertEqual(result.promotion_outcome, "promoted")
        self.assertIn("promotion", result.completed_stages)

    def test_missing_or_reordered_required_stage_sequence_is_rejected(self) -> None:
        canonical = list(steps())
        with self.assertRaises(OrchestrationError):
            execute_standard_lifecycle(tuple(canonical[:-1]))
        reordered = list(canonical)
        reordered[1], reordered[2] = reordered[2], reordered[1]
        with self.assertRaises(OrchestrationError):
            execute_standard_lifecycle(tuple(reordered))

    def test_duplicate_stage_identifier_is_rejected(self) -> None:
        canonical = list(steps())
        canonical[1] = StageStep(
            canonical[0].stage_id,
            canonical[1].action,
        )
        with self.assertRaises(OrchestrationError):
            execute_standard_lifecycle(tuple(canonical))


if __name__ == "__main__":
    unittest.main()
