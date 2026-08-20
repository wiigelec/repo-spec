import pathlib
import unittest


class RoutingOwnershipBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = pathlib.Path(__file__).resolve().parents[4]
        cls.plan_root = (
            cls.repo_root / "repo/docs/plans/REPOSITORY-IMPLEMENTATION-PLAN.md"
        ).read_text()
        cls.scope_chunk = (
            cls.repo_root
            / "repo/docs/plans/repository-implementation-plan/01-authority-scope-and-specification-map.md"
        ).read_text()
        cls.correspondence_validator = (
            cls.repo_root
            / "product/validation/checks/product_correspondence.py"
        ).read_text()

    def test_plan_requires_product_owned_correspondence_evidence(self):
        self.assertIn(
            "Portable implementation, test, and conformance artifacts used as maintained "
            "correspondence evidence for the seven controlling `product.*` specifications "
            "are product-owned",
            self.plan_root,
        )
        self.assertIn(
            "product-owned portable implementation/test/conformance evidence",
            self.scope_chunk,
        )

    def test_plan_preserves_repository_profile_adapter_boundary(self):
        self.assertIn(
            "Repository/framework helpers and hosting-profile source or installed adapters "
            "may remain under their accepted repository/profile-owned locations",
            self.plan_root,
        )
        self.assertIn(
            "repository/profile-owned helper and adapter mechanics",
            self.scope_chunk,
        )

    def test_existing_correspondence_validator_still_rejects_repo_scripts(self):
        self.assertIn(
            '"repo/scripts/"',
            self.correspondence_validator,
        )
        self.assertIn(
            "forbidden_prefixes",
            self.correspondence_validator,
        )


if __name__ == "__main__":
    unittest.main()
