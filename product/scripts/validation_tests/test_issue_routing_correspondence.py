from __future__ import annotations

import json
import pathlib
import unittest


SPEC_IDS = (
    "product.issue-routing-governance",
    "product.issue-routing-classification",
    "product.governed-work-provenance",
    "product.issue-authority-routing",
    "product.governed-work-promotion",
    "product.issue-routing-platform-validation",
    "product.issue-intake-governance-routing",
)

EXPECTED_IMPLEMENTATION_PATHS = {
    "product.issue-routing-governance": {
        "product/scripts/issue_intake_governance_routing/classification.py",
        "product/scripts/issue_intake_governance_routing/authority.py",
        "product/scripts/issue_intake_governance_routing/provenance.py",
        "product/scripts/issue_intake_governance_routing/promotion.py",
        "product/scripts/issue_intake_governance_routing/hosted_validation.py",
        "product/scripts/issue_intake_governance_routing/orchestration.py",
    },
    "product.issue-routing-classification": {
        "product/scripts/issue_intake_governance_routing/classification.py",
    },
    "product.governed-work-provenance": {
        "product/scripts/issue_intake_governance_routing/provenance.py",
    },
    "product.issue-authority-routing": {
        "product/scripts/issue_intake_governance_routing/authority.py",
    },
    "product.governed-work-promotion": {
        "product/scripts/issue_intake_governance_routing/promotion.py",
    },
    "product.issue-routing-platform-validation": {
        "product/scripts/issue_intake_governance_routing/hosted_validation.py",
    },
    "product.issue-intake-governance-routing": {
        "product/scripts/issue_intake_governance_routing/orchestration.py",
    },
}

BEHAVIOR_TEST = (
    "product/scripts/validation_tests/test_issue_intake_governance_routing.py"
)


class IssueRoutingCorrespondenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = pathlib.Path(__file__).resolve().parents[3]
        manifest = json.loads(
            (cls.repo_root / "product/specs/product/manifest.json").read_text()
        )
        cls.spec_paths = {
            entry["spec_id"]: entry["path"]
            for entry in manifest["product_specifications"]
            if entry["spec_id"] in SPEC_IDS
        }

    def test_all_seven_specs_have_complete_product_owned_correspondence(self):
        self.assertEqual(set(self.spec_paths), set(SPEC_IDS))

        for spec_id in SPEC_IDS:
            with self.subTest(spec_id=spec_id):
                spec = json.loads(
                    (self.repo_root / self.spec_paths[spec_id]).read_text()
                )
                self.assertEqual(spec["status"], "accepted")

                requirement_ids = {
                    item["id"] for item in spec["normative_requirements"]
                }
                correspondence = spec["correspondence"]

                implementations = correspondence["implementations"]
                tests = correspondence["tests"]
                conformance = correspondence["conformance"]

                self.assertEqual(len(implementations), 1)
                self.assertEqual(len(tests), 1)
                self.assertEqual(
                    set(implementations[0]["paths"]),
                    EXPECTED_IMPLEMENTATION_PATHS[spec_id],
                )
                self.assertEqual(tests[0]["paths"], [BEHAVIOR_TEST])
                self.assertEqual(
                    set(implementations[0]["requirements"]),
                    requirement_ids,
                )
                self.assertEqual(
                    set(tests[0]["requirements"]),
                    requirement_ids,
                )

                self.assertEqual(
                    {item["requirement_id"] for item in conformance},
                    requirement_ids,
                )
                self.assertTrue(
                    all(item["status"] == "covered" for item in conformance)
                )

                implementation_ids = {implementations[0]["id"]}
                test_ids = {tests[0]["id"]}
                for record in conformance:
                    self.assertEqual(
                        set(record["implementation_ids"]),
                        implementation_ids,
                    )
                    self.assertEqual(set(record["test_ids"]), test_ids)

    def test_all_correspondence_paths_are_real_product_owned_files(self):
        for spec_id in SPEC_IDS:
            spec = json.loads(
                (self.repo_root / self.spec_paths[spec_id]).read_text()
            )
            mappings = (
                spec["correspondence"]["implementations"]
                + spec["correspondence"]["tests"]
            )
            for mapping in mappings:
                for path in mapping["paths"]:
                    with self.subTest(spec_id=spec_id, path=path):
                        self.assertTrue(path.startswith("product/scripts/"))
                        self.assertNotIn("/product_validation/", path)
                        resolved = self.repo_root / path
                        self.assertTrue(resolved.is_file())

    def test_level3_correspondence_uses_real_orchestration_and_behavior_test(self):
        spec = json.loads(
            (
                self.repo_root
                / self.spec_paths[
                    "product.issue-intake-governance-routing"
                ]
            ).read_text()
        )
        implementation_paths = {
            path
            for mapping in spec["correspondence"]["implementations"]
            for path in mapping["paths"]
        }
        test_paths = {
            path
            for mapping in spec["correspondence"]["tests"]
            for path in mapping["paths"]
        }
        self.assertEqual(
            implementation_paths,
            {
                "product/scripts/issue_intake_governance_routing/orchestration.py"
            },
        )
        self.assertEqual(test_paths, {BEHAVIOR_TEST})


if __name__ == "__main__":
    unittest.main()
