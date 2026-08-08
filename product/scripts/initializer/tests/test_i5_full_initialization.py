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


REVISION = {
    "object_format": "sha1",
    "object_id": "0123456789abcdef0123456789abcdef01234567",
}


def raw_request(
    *,
    destination: str = "./out",
    source_repository: str = "./source",
    revision: object = None,
    profile: object = None,
) -> dict[str, object]:
    raw: dict[str, object] = {
        "schema_version": "1",
        "destination": destination,
        "authority": {"granted_by": "issue-287"},
        "source": {
            "repository": source_repository,
            "revision": dict(REVISION) if revision is None else revision,
        },
        "product": {
            "id": "sample-product",
            "direction_material": ["docs/a.md", "docs/a.md"],
        },
    }
    if profile is not None:
        raw["profile"] = profile
    return raw


def actions(
    *,
    fail_stage: str | None = None,
    promotion: str = PROMOTION_PROMOTED,
    finalization: str = STAGE_COMPLETED,
    calls: list[str] | None = None,
) -> FullInitializationActions:
    sink = calls if calls is not None else []

    def make(stage_id: str):
        def action(carried):
            sink.append(stage_id)
            if stage_id == fail_stage:
                raise RuntimeError(f"{stage_id} failed")
            if stage_id == "promotion":
                return promotion
            if stage_id == "success-finalization":
                return finalization
            return {"stage": stage_id, "request": carried["entry"].request_fingerprint}
        return action

    return FullInitializationActions(
        request_intake=make("request-intake"),
        source_resolution=make("source-resolution"),
        destination_preflight=make("destination-preflight"),
        staging_establishment=make("staging-establishment"),
        framework_installation=make("framework-installation"),
        direction_evidence_installation=make("direction-evidence-installation"),
        workspace_seeding=make("workspace-seeding"),
        provenance_recording=make("provenance-recording"),
        handoff_assembly=make("handoff-assembly"),
        git_initialization=make("git-initialization"),
        repository_validation=make("repository-validation"),
        promotion=make("promotion"),
        success_finalization=make("success-finalization"),
    )


class I5FullInitializationTests(unittest.TestCase):
    def test_complete_standard_workflow_returns_promoted_success(self) -> None:
        calls: list[str] = []
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(calls=calls),
        )
        self.assertEqual(result.terminal_result, TERMINAL_PROMOTED_SUCCESS)
        self.assertTrue(result.succeeded)
        self.assertEqual(len(calls), 13)
        self.assertEqual(calls[0], "request-intake")
        self.assertEqual(calls[-1], "success-finalization")

    def test_rejected_profile_executes_no_stage_action(self) -> None:
        calls: list[str] = []
        with self.assertRaisesRegex(Exception, "unsupported profile"):
            execute_full_initialization(
                raw_request(profile="dry-run"),
                "/work",
                actions(calls=calls),
            )
        self.assertEqual(calls, [])

    def test_remote_source_executes_no_stage_action(self) -> None:
        calls: list[str] = []
        with self.assertRaises(Exception):
            execute_full_initialization(
                raw_request(source_repository="https://example.invalid/repo.git"),
                "/work",
                actions(calls=calls),
            )
        self.assertEqual(calls, [])

    def test_named_reference_executes_no_stage_action(self) -> None:
        calls: list[str] = []
        with self.assertRaises(Exception):
            execute_full_initialization(
                raw_request(revision="main"),
                "/work",
                actions(calls=calls),
            )
        self.assertEqual(calls, [])

    def test_existing_destination_preflight_failure_is_pre_promotion(self) -> None:
        calls: list[str] = []
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(fail_stage="destination-preflight", calls=calls),
        )
        self.assertEqual(result.terminal_result, TERMINAL_PRE_PROMOTION_FAILURE)
        self.assertEqual(result.lifecycle.failed_stage, "destination-preflight")
        self.assertNotIn("staging-establishment", calls)
        self.assertNotIn("promotion", calls)

    def test_cross_device_preflight_failure_is_pre_promotion(self) -> None:
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(fail_stage="staging-establishment"),
        )
        self.assertEqual(result.terminal_result, TERMINAL_PRE_PROMOTION_FAILURE)
        self.assertEqual(result.lifecycle.failed_stage, "staging-establishment")
        self.assertEqual(result.lifecycle.promotion_outcome, "not-promoted")

    def test_indeterminate_promotion_is_terminal_without_success_finalization(self) -> None:
        calls: list[str] = []
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(promotion=PROMOTION_INDETERMINATE, calls=calls),
        )
        self.assertEqual(result.terminal_result, TERMINAL_INDETERMINATE_PROMOTION)
        self.assertNotIn("success-finalization", calls)

    def test_cleanup_failure_remains_promoted(self) -> None:
        result = execute_full_initialization(
            raw_request(),
            "/work",
            actions(finalization=FINALIZATION_CLEANUP_FAILURE),
        )
        self.assertEqual(
            result.terminal_result,
            TERMINAL_PROMOTED_WITH_FINALIZATION_ERROR,
        )
        self.assertEqual(result.lifecycle.promotion_outcome, "promoted")

    def test_equivalent_lexical_paths_produce_equivalent_workflow_entries(self) -> None:
        left = execute_full_initialization(
            raw_request(destination="./out", source_repository="./source"),
            "/work",
            actions(),
        )
        right = execute_full_initialization(
            raw_request(destination="/work/out", source_repository="source/../source"),
            "/work",
            actions(),
        )
        self.assertTrue(canonical_outcome_inputs_equivalent(left.entry, right.entry))
        self.assertEqual(left.entry.request_fingerprint, right.entry.request_fingerprint)

    def test_authority_difference_breaks_equivalence(self) -> None:
        left_raw = raw_request()
        right_raw = raw_request()
        right_raw["authority"] = {"granted_by": "issue-other"}
        left = execute_full_initialization(left_raw, "/work", actions())
        right = execute_full_initialization(right_raw, "/work", actions())
        self.assertFalse(canonical_outcome_inputs_equivalent(left.entry, right.entry))


if __name__ == "__main__":
    unittest.main()
