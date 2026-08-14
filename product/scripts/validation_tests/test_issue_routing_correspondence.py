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

BEHAVIOR_TEST = (
    "product/scripts/validation_tests/test_issue_intake_governance_routing.py"
)
HOSTED_TEST = (
    "product/scripts/validation_tests/test_issue_routing_hosted_conformance.py"
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
        "product/scripts/issue_intake_governance_routing/orchestration.py",
    },
    "product.issue-intake-governance-routing": {
        "product/scripts/issue_intake_governance_routing/orchestration.py",
    },
}


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
        return json.loads(
            (self.repo_root / self.spec_paths[spec_id]).read_text()
        )

    def test_all_seven_specs_have_complete_product_owned_correspondence(self):
        self.assertEqual(set(self.spec_paths), set(SPEC_IDS))

        for spec_id in SPEC_IDS:
            with self.subTest(spec_id=spec_id):
                spec = self.load_spec(spec_id)
                self.assertEqual(spec["status"], "accepted")
                requirement_ids = {
                    item["id"] for item in spec["normative_requirements"]
                }
                correspondence = spec["correspondence"]

                implementation_requirements = set()
                implementation_paths = set()
                implementation_ids = set()
                for mapping in correspondence["implementations"]:
                    implementation_ids.add(mapping["id"])
                    implementation_requirements.update(mapping["requirements"])
                    implementation_paths.update(mapping["paths"])

                test_requirements = set()
                test_ids = set()
                for mapping in correspondence["tests"]:
                    test_ids.add(mapping["id"])
                    test_requirements.update(mapping["requirements"])

                self.assertEqual(
                    implementation_paths,
                    EXPECTED_IMPLEMENTATION_PATHS[spec_id],
                )
                self.assertEqual(implementation_requirements, requirement_ids)
                self.assertEqual(test_requirements, requirement_ids)

                conformance = correspondence["conformance"]
                self.assertEqual(
                    {item["requirement_id"] for item in conformance},
                    requirement_ids,
                )
                self.assertTrue(
                    all(item["status"] == "covered" for item in conformance)
                )
                for record in conformance:
                    self.assertTrue(record["implementation_ids"])
                    self.assertTrue(record["test_ids"])
                    self.assertTrue(
                        set(record["implementation_ids"]).issubset(
                            implementation_ids
                        )
                    )
                    self.assertTrue(
                        set(record["test_ids"]).issubset(test_ids)
                    )

    def test_all_correspondence_paths_are_real_product_owned_files(self):
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
                        self.assertNotIn("/product_validation/", path)
                        self.assertNotIn("repo/scripts/", path)
                        self.assertNotIn(".github/", path)
                        self.assertTrue((self.repo_root / path).is_file())

    def test_promotion_correspondence_distinguishes_product_and_hosted_evidence(self):
        spec = self.load_spec("product.governed-work-promotion")
        tests = {mapping["id"]: mapping for mapping in spec["correspondence"]["tests"]}
        self.assertEqual(
            tests["test.governed-work-promotion.product"]["paths"],
            [BEHAVIOR_TEST],
        )
        self.assertEqual(
            tests["test.governed-work-promotion.hosted-conformance"]["paths"],
            [HOSTED_TEST],
        )
        records = {
            item["requirement_id"]: item
            for item in spec["correspondence"]["conformance"]
        }
        self.assertIn(
            "test.governed-work-promotion.hosted-conformance",
            records["IRG-PROM-002"]["test_ids"],
        )
        self.assertIn(
            "test.governed-work-promotion.hosted-conformance",
            records["IRG-PROM-004"]["test_ids"],
        )

    def test_platform_validation_correspondence_requires_hosted_conformance(self):
        spec = self.load_spec("product.issue-routing-platform-validation")
        records = {
            item["requirement_id"]: item
            for item in spec["correspondence"]["conformance"]
        }
        for requirement_id, record in records.items():
            with self.subTest(requirement_id=requirement_id):
                self.assertIn(
                    "test.issue-routing-platform-validation.hosted-conformance",
                    record["test_ids"],
                )

    def test_level3_host_sensitive_requirements_use_hosted_conformance(self):
        spec = self.load_spec("product.issue-intake-governance-routing")
        records = {
            item["requirement_id"]: item
            for item in spec["correspondence"]["conformance"]
        }
        for requirement_id in ("IRG-E2E-002", "IRG-E2E-005", "IRG-E2E-006", "IRG-E2E-007"):
            self.assertIn(
                "test.issue-intake-governance-routing.hosted-conformance",
                records[requirement_id]["test_ids"],
            )


if __name__ == "__main__":
    unittest.main()
