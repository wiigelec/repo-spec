import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("issue_authority_routing.py")
SPEC = importlib.util.spec_from_file_location("issue_authority_routing", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class IssueAuthorityRoutingTests(unittest.TestCase):
    def test_bug_fix_routes_to_audit(self):
        result = MODULE.route_labels(["bug-fix"])
        self.assertEqual(result.path, MODULE.AuthorityPath.AUDIT)
        self.assertTrue(result.has_unique_path)
        self.assertFalse(result.mutation_authorized)

    def test_feature_request_routes_to_feature_development(self):
        result = MODULE.route_labels(["feature-request"])
        self.assertEqual(result.path, MODULE.AuthorityPath.FEATURE_DEVELOPMENT)
        self.assertTrue(result.has_unique_path)
        self.assertFalse(result.mutation_authorized)
        self.assertEqual(
            MODULE.FEATURE_DEVELOPMENT_STAGES,
            (
                "whiteboard",
                "analysis",
                "candidate-functional-set",
                "explicit-functional-set-approval",
            ),
        )

    def test_unclassified_has_no_authority_path(self):
        result = MODULE.route_labels([])
        self.assertEqual(result.path, MODULE.AuthorityPath.NO_PATH)
        self.assertFalse(result.has_unique_path)
        self.assertFalse(result.mutation_authorized)

    def test_conflicting_classification_has_no_authority_path(self):
        result = MODULE.route_labels(["bug-fix", "feature-request"])
        self.assertEqual(result.path, MODULE.AuthorityPath.NO_PATH)
        self.assertEqual(result.classification_state, "conflict")
        self.assertFalse(result.has_unique_path)
        self.assertFalse(result.mutation_authorized)

    def test_unique_path_requirement_fails_closed_for_unclassified(self):
        with self.assertRaisesRegex(ValueError, "no unique authority path"):
            MODULE.require_unique_authority_path([])

    def test_unique_path_requirement_fails_closed_for_conflict(self):
        with self.assertRaisesRegex(ValueError, "no unique authority path"):
            MODULE.require_unique_authority_path(["bug-fix", "feature-request"])

    def test_routing_never_represents_direct_implementation_authority(self):
        for labels in (["bug-fix"], ["feature-request"], [], ["bug-fix", "feature-request"]):
            result = MODULE.route_labels(labels)
            self.assertFalse(result.mutation_authorized)
            self.assertNotEqual(result.path.value, "implementation")


if __name__ == "__main__":
    unittest.main()
