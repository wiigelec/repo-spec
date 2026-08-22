from __future__ import annotations

import unittest

from initializer.orchestration import (
    FINALIZATION_CLEANUP_FAILURE,
    PROMOTION_INDETERMINATE,
    PROMOTION_PROMOTED,
    STAGE_COMPLETED,
    TERMINAL_INDETERMINATE_PROMOTION,
    TERMINAL_PRE_PROMOTION_FAILURE,
    TERMINAL_PROMOTED_SUCCESS,
    TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
    FullInitializationActions,
    canonical_outcome_inputs_equivalent,
    execute_full_initialization,
)


# validation-metadata: {"role": "helper"}
def raw_request(destination: str = "./out") -> dict[str, object]:
    return {"schema_version": "2", "destination": destination}


# validation-metadata: {"role": "helper"}
def actions(
    *,
    fail_stage=None,
    promotion=PROMOTION_PROMOTED,
    finalization=STAGE_COMPLETED,
    calls=None,
):
    sink = calls if calls is not None else []

    # validation-metadata: {"role": "helper"}
    def make(stage_id):
        # validation-metadata: {"role": "helper"}
        def action(carried):
            sink.append(stage_id)
            if stage_id == fail_stage:
                raise RuntimeError(f"{stage_id} failed")
            if stage_id == "promotion":
                return promotion
            if stage_id == "success-finalization":
                return finalization
            return {"stage": stage_id}

        return action

    return FullInitializationActions(
        request_intake=make("request-intake"),
        source_resolution=make("source-resolution"),
        destination_preflight=make("destination-preflight"),
        staging_establishment=make("staging-establishment"),
        framework_installation=make("framework-installation"),
        direction_evidence_installation=make(
            "direction-evidence-installation"
        ),
        workspace_seeding=make("workspace-seeding"),
        provenance_recording=make("provenance-recording"),
        handoff_assembly=make("handoff-assembly"),
        git_initialization=make("git-initialization"),
        repository_validation=make("repository-validation"),
        promotion=make("promotion"),
        success_finalization=make("success-finalization"),
    )


class I5FullInitializationTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_complete_standard_workflow_returns_promoted_success(self):
        calls = []
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(calls=calls),
        )
        self.assertEqual(
            result.terminal_result,
            TERMINAL_PROMOTED_SUCCESS,
        )
        self.assertTrue(result.succeeded)
        self.assertEqual(len(calls), 13)

    # validation-metadata: {"role": "helper"}
    def test_legacy_profile_executes_no_stage_action(self):
        calls = []
        raw = raw_request()
        raw["profile"] = "dry-run"
        with self.assertRaises(Exception):
            execute_full_initialization(
                raw,
                "/work",
                actions(calls=calls),
            )
        self.assertEqual(calls, [])

    # validation-metadata: {"role": "helper"}
    def test_pre_promotion_failure_stops_lifecycle(self):
        calls = []
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(
                fail_stage="destination-preflight",
                calls=calls,
            ),
        )
        self.assertEqual(
            result.terminal_result,
            TERMINAL_PRE_PROMOTION_FAILURE,
        )
        self.assertNotIn("promotion", calls)

    # validation-metadata: {"role": "helper"}
    def test_indeterminate_promotion_is_terminal(self):
        calls = []
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(
                promotion=PROMOTION_INDETERMINATE,
                calls=calls,
            ),
        )
        self.assertEqual(
            result.terminal_result,
            TERMINAL_INDETERMINATE_PROMOTION,
        )
        self.assertNotIn("success-finalization", calls)

    # validation-metadata: {"role": "helper"}
    def test_cleanup_failure_remains_promoted(self):
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(
                finalization=FINALIZATION_CLEANUP_FAILURE,
            ),
        )
        self.assertEqual(
            result.terminal_result,
            TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
        )

    # validation-metadata: {"role": "helper"}
    def test_lexically_equivalent_destinations_are_equivalent(self):
        left = execute_full_initialization(
            raw_request("./out"),
            "/work",
            actions(),
        )
        right = execute_full_initialization(
            raw_request("/work/out"),
            "/work",
            actions(),
        )
        self.assertTrue(
            canonical_outcome_inputs_equivalent(
                left.entry,
                right.entry,
            )
        )


if __name__ == "__main__":
    unittest.main()
