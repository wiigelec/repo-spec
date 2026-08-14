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

HOSTED_TEST = (
    "product/scripts/validation_tests/test_issue_routing_hosted_conformance.py"
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

    def load_spec(self, spec_id):
        return json.loads((self.repo_root / self.spec_paths[spec_id]).read_text())

    def test_all_correspondence_paths_remain_product_owned(self):
        for spec_id in SPEC_IDS:
            spec = self.load_spec(spec_id)
            mappings = (
                spec["correspondence"]["implementations"]
                + spec["correspondence"]["tests"]
            )
            for mapping in mappings:
                for path in mapping["paths"]:
                    with self.subTest(spec_id=spec_id, path=path):
                        self.assertTrue(path.startswith("product/scripts/"))
                        self.assertNotIn("repo/scripts/", path)
                        self.assertNotIn(".github/", path)
                        self.assertTrue((self.repo_root / path).is_file())

    def test_hosted_authority_sensitive_specs_point_to_real_hosted_test(self):
        expected = {
            "product.governed-work-provenance":
                "test.governed-work-provenance.hosted-conformance",
            "product.issue-authority-routing":
                "test.issue-authority-routing.hosted-conformance",
            "product.governed-work-promotion":
                "test.governed-work-promotion.hosted-conformance",
            "product.issue-routing-platform-validation":
                "test.issue-routing-platform-validation.hosted-conformance",
            "product.issue-intake-governance-routing":
                "test.issue-intake-governance-routing.hosted-conformance",
        }
        for spec_id, test_id in expected.items():
            with self.subTest(spec_id=spec_id):
                spec = self.load_spec(spec_id)
                tests = {
                    mapping["id"]: mapping
                    for mapping in spec["correspondence"]["tests"]
                }
                self.assertIn(test_id, tests)
                self.assertEqual(tests[test_id]["paths"], [HOSTED_TEST])

    def test_authority_hosted_mapping_excludes_audit_redirect_requirement(self):
        spec = self.load_spec("product.issue-authority-routing")
        tests = {
            mapping["id"]: mapping
            for mapping in spec["correspondence"]["tests"]
        }
        hosted = tests["test.issue-authority-routing.hosted-conformance"]
        self.assertNotIn("IRG-ROUTE-003", hosted["requirements"])
        for req in (
            "IRG-ROUTE-001",
            "IRG-ROUTE-002",
            "IRG-ROUTE-004",
            "IRG-ROUTE-005",
            "IRG-ROUTE-006",
        ):
            self.assertIn(req, hosted["requirements"])

    def test_promotion_hosted_mapping_covers_all_promotion_requirements(self):
        spec = self.load_spec("product.governed-work-promotion")
        tests = {
            mapping["id"]: mapping
            for mapping in spec["correspondence"]["tests"]
        }
        hosted = tests["test.governed-work-promotion.hosted-conformance"]
        self.assertEqual(
            set(hosted["requirements"]),
            {
                "IRG-PROM-001",
                "IRG-PROM-002",
                "IRG-PROM-003",
                "IRG-PROM-004",
                "IRG-PROM-005",
            },
        )

    def test_every_covered_record_references_existing_mappings(self):
        for spec_id in SPEC_IDS:
            spec = self.load_spec(spec_id)
            impl_ids = {
                item["id"] for item in spec["correspondence"]["implementations"]
            }
            test_ids = {
                item["id"] for item in spec["correspondence"]["tests"]
            }
            for record in spec["correspondence"]["conformance"]:
                self.assertEqual(record["status"], "covered")
                self.assertTrue(set(record["implementation_ids"]) <= impl_ids)
                self.assertTrue(set(record["test_ids"]) <= test_ids)


if __name__ == "__main__":
    unittest.main()
