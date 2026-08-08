from __future__ import annotations

import unittest

from initializer.models import ImmutableRequest
from initializer.orchestration import (
    OrchestrationError,
    STANDARD_PROFILE,
    STANDARD_WORKFLOW_ID,
    canonical_direction_material,
    canonical_outcome_inputs_equivalent,
    canonical_requests_equivalent,
    canonical_source_identity,
    canonical_sources_equivalent,
    prepare_standard_workflow,
    select_standard_workflow,
)


REVISION = {
    "object_format": "sha1",
    "object_id": "0123456789abcdef0123456789abcdef01234567",
}


def request(
    *,
    destination: str = "./out",
    source_repository: str = "./source",
    profile_marker: object = None,
    direction_material: list[str] | None = None,
) -> dict[str, object]:
    raw: dict[str, object] = {
        "schema_version": "1",
        "destination": destination,
        "authority": {"granted_by": "issue-287"},
        "source": {
            "repository": source_repository,
            "revision": dict(REVISION),
        },
        "product": {
            "id": "sample-product",
            "direction_material": (
                list(direction_material)
                if direction_material is not None
                else ["docs/a.md", "docs/a.md", "docs/b.md"]
            ),
        },
    }
    if profile_marker is not None:
        raw["profile"] = profile_marker
    return raw


class I5OrchestrationEntryTests(unittest.TestCase):
    def test_omitted_profile_selects_standard_full_initialization(self) -> None:
        entry = prepare_standard_workflow(request(), "/work")
        self.assertEqual(entry.selection.profile, STANDARD_PROFILE)
        self.assertEqual(entry.selection.workflow_id, STANDARD_WORKFLOW_ID)
        self.assertEqual(entry.request.destination, "/work/out")
        self.assertEqual(entry.request.source_repository, "/work/source")

    def test_explicit_standard_profile_selects_same_workflow(self) -> None:
        entry = prepare_standard_workflow(
            request(profile_marker="standard"),
            "/work",
        )
        self.assertEqual(entry.selection.profile, "standard")
        self.assertEqual(entry.selection.workflow_id, "product.full-initialization")

    def test_unsupported_profile_rejected_before_entry_exists(self) -> None:
        with self.assertRaisesRegex(Exception, "unsupported profile"):
            prepare_standard_workflow(
                request(profile_marker="dry-run"),
                "/work",
            )

    def test_non_string_profile_rejected_before_entry_exists(self) -> None:
        with self.assertRaisesRegex(Exception, "profile must be a string"):
            prepare_standard_workflow(
                request(profile_marker={"mode": "standard"}),
                "/work",
            )

    def test_select_standard_workflow_defensively_rejects_nonstandard_model(self) -> None:
        good = prepare_standard_workflow(
            request(profile_marker="standard"),
            "/work",
        ).request
        forged = ImmutableRequest(
            {
                "schema_version": good.schema_version,
                "destination": good.destination,
                "authority": good.authority,
                "source": {
                    "repository": good.source_repository,
                    "revision": good.source_revision.to_dict(),
                },
                "product": {
                    "id": good.product_id,
                    "direction_material": list(good.product_direction_material),
                },
                "profile": "recovery",
            },
            good.canonical_request_bytes,
            good.request_fingerprint,
        )
        with self.assertRaises(OrchestrationError) as caught:
            select_standard_workflow(forged)
        self.assertEqual(caught.exception.category, "unsupported-execution-profile")

    def test_lexically_distinct_paths_share_canonical_request_when_all_values_match(self) -> None:
        left = prepare_standard_workflow(
            request(destination="./out", source_repository="source/../source"),
            "/work",
        )
        right = prepare_standard_workflow(
            request(destination="/work/out", source_repository="/work/source"),
            "/work",
        )
        self.assertTrue(canonical_requests_equivalent(left.request, right.request))
        self.assertTrue(canonical_sources_equivalent(left.request, right.request))
        self.assertTrue(canonical_outcome_inputs_equivalent(left, right))
        self.assertEqual(left.request_fingerprint, right.request_fingerprint)

    def test_authoritative_value_difference_is_not_equivalent(self) -> None:
        left = prepare_standard_workflow(request(), "/work")
        changed = request()
        changed["authority"] = {"granted_by": "issue-other"}
        right = prepare_standard_workflow(changed, "/work")
        self.assertFalse(canonical_requests_equivalent(left.request, right.request))
        self.assertFalse(canonical_outcome_inputs_equivalent(left, right))

    def test_source_identity_requires_exact_canonical_path_and_object_identity(self) -> None:
        left = prepare_standard_workflow(request(), "/work")
        right_raw = request()
        right_raw["source"] = {
            "repository": "./other-source",
            "revision": dict(REVISION),
        }
        right = prepare_standard_workflow(right_raw, "/work")
        self.assertEqual(
            canonical_source_identity(left.request),
            (
                "/work/source",
                "sha1",
                "0123456789abcdef0123456789abcdef01234567",
            ),
        )
        self.assertFalse(canonical_sources_equivalent(left.request, right.request))

    def test_direction_material_order_and_duplicates_are_preserved(self) -> None:
        left = prepare_standard_workflow(
            request(direction_material=["docs/a.md", "docs/a.md", "docs/b.md"]),
            "/work",
        )
        reordered = prepare_standard_workflow(
            request(direction_material=["docs/a.md", "docs/b.md", "docs/a.md"]),
            "/work",
        )
        self.assertEqual(
            canonical_direction_material(left.request),
            ("docs/a.md", "docs/a.md", "docs/b.md"),
        )
        self.assertFalse(canonical_requests_equivalent(left.request, reordered.request))
        self.assertFalse(canonical_outcome_inputs_equivalent(left, reordered))


if __name__ == "__main__":
    unittest.main()
