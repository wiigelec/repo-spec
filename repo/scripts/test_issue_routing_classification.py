import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("issue_routing_classification.py")
SPEC = importlib.util.spec_from_file_location("issue_routing_classification", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class IssueRoutingClassificationTests(unittest.TestCase):
    def test_unclassified_without_routing_labels(self):
        result = MODULE.classify_labels([])
        self.assertEqual(result.state, MODULE.ClassificationState.UNCLASSIFIED)
        self.assertEqual(result.routing_labels, frozenset())
        self.assertFalse(result.governed_work)

    def test_bug_fix_only(self):
        result = MODULE.classify_labels(["bug-fix"])
        self.assertEqual(result.state, MODULE.ClassificationState.BUG_FIX)
        self.assertEqual(result.routing_labels, frozenset({"bug-fix"}))
        self.assertTrue(result.has_single_direction)

    def test_feature_request_only(self):
        result = MODULE.classify_labels(["feature-request"])
        self.assertEqual(result.state, MODULE.ClassificationState.FEATURE_REQUEST)
        self.assertEqual(result.routing_labels, frozenset({"feature-request"}))
        self.assertTrue(result.has_single_direction)

    def test_dual_classification_is_representable_but_conflicting(self):
        result = MODULE.classify_labels(["bug-fix", "feature-request"])
        self.assertEqual(result.state, MODULE.ClassificationState.CONFLICT)
        self.assertEqual(result.routing_labels, frozenset({"bug-fix", "feature-request"}))
        self.assertFalse(result.has_single_direction)

    def test_single_direction_request_fails_closed_on_conflict(self):
        with self.assertRaisesRegex(ValueError, "unresolved routing classification conflict"):
            MODULE.require_single_direction(["bug-fix", "feature-request"])

    def test_governed_work_is_orthogonal_to_routing_classification(self):
        result = MODULE.classify_labels(["governed-work", "bug-fix"])
        self.assertEqual(result.state, MODULE.ClassificationState.BUG_FIX)
        self.assertTrue(result.governed_work)
        self.assertEqual(result.routing_labels, frozenset({"bug-fix"}))

    def test_unrelated_labels_do_not_change_routing_state(self):
        result = MODULE.classify_labels(["documentation", "question"])
        self.assertEqual(result.state, MODULE.ClassificationState.UNCLASSIFIED)
        self.assertEqual(result.routing_labels, frozenset())


if __name__ == "__main__":
    unittest.main()
