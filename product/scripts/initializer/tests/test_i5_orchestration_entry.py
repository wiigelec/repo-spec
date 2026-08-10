from __future__ import annotations

import unittest

from initializer.orchestration import (
    STANDARD_PROFILE,
    STANDARD_WORKFLOW_ID,
    canonical_outcome_inputs_equivalent,
    canonical_requests_equivalent,
    prepare_standard_workflow,
)


def request(destination: str = "./out") -> dict[str, object]:
    return {"schema_version": "2", "destination": destination}


class I5OrchestrationEntryTests(unittest.TestCase):
    def test_v2_request_selects_standard_bootstrap_workflow(self):
        entry = prepare_standard_workflow(request(), "/work")
        self.assertEqual(entry.selection.profile, STANDARD_PROFILE)
        self.assertEqual(entry.selection.workflow_id, STANDARD_WORKFLOW_ID)
        self.assertEqual(entry.request.destination, "/work/out")

    def test_legacy_profile_is_rejected_by_closed_request_contract(self):
        raw = request()
        raw["profile"] = "standard"
        with self.assertRaises(Exception):
            prepare_standard_workflow(raw, "/work")

    def test_legacy_source_product_and_authority_are_rejected(self):
        for field, value in (
            ("source", {"repository": "/work/source"}),
            ("product", {"id": "sample"}),
            ("authority", {"granted_by": "issue-old"}),
        ):
            with self.subTest(field=field):
                raw = request()
                raw[field] = value
                with self.assertRaises(Exception):
                    prepare_standard_workflow(raw, "/work")

    def test_lexically_equivalent_destinations_share_canonical_request(self):
        left = prepare_standard_workflow(request("./out"), "/work")
        right = prepare_standard_workflow(request("/work/out"), "/work")
        self.assertTrue(
            canonical_requests_equivalent(left.request, right.request)
        )
        self.assertTrue(canonical_outcome_inputs_equivalent(left, right))

    def test_destination_difference_is_authoritative(self):
        left = prepare_standard_workflow(request("/work/out"), "/work")
        right = prepare_standard_workflow(request("/work/other"), "/work")
        self.assertFalse(
            canonical_requests_equivalent(left.request, right.request)
        )
        self.assertFalse(canonical_outcome_inputs_equivalent(left, right))


if __name__ == "__main__":
    unittest.main()
