import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("issue_intake_provenance.py")
SPEC = importlib.util.spec_from_file_location("issue_intake_provenance", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class IssueIntakeProvenanceTests(unittest.TestCase):
    def test_original_body_is_preserved_verbatim(self):
        body = "plain intake\n\n  keep spacing\nlast line"
        provenance = MODULE.capture_intake_provenance(
            intake_issue="#12",
            governed_operation="#34",
            original_body=body,
            labels=["bug-fix"],
        )
        self.assertEqual(provenance.original_body, body)
        self.assertTrue(provenance.to_comment().endswith(body))

    def test_pre_promotion_routing_labels_are_preserved(self):
        provenance = MODULE.capture_intake_provenance(
            intake_issue="#12",
            governed_operation="#34",
            original_body="body",
            labels=["feature-request", "documentation", "bug-fix"],
        )
        self.assertEqual(provenance.routing_labels, ("bug-fix", "feature-request"))

    def test_unrelated_labels_are_not_part_of_normative_routing_payload(self):
        provenance = MODULE.capture_intake_provenance(
            intake_issue="#12",
            governed_operation="#34",
            original_body="body",
            labels=["documentation", "question"],
        )
        self.assertEqual(provenance.routing_labels, ())

    def test_comment_is_traceable_to_intake_and_governed_operation(self):
        provenance = MODULE.capture_intake_provenance(
            intake_issue="https://github.com/wiigelec/repo-spec/issues/12",
            governed_operation="#34",
            original_body="body",
            labels=["bug-fix"],
        )
        comment = provenance.to_comment()
        self.assertIn("https://github.com/wiigelec/repo-spec/issues/12", comment)
        self.assertIn("#34", comment)

    def test_capture_explicitly_precedes_restructure(self):
        provenance = MODULE.capture_intake_provenance(
            intake_issue="#12",
            governed_operation="#34",
            original_body="body",
            labels=["bug-fix"],
        )
        self.assertTrue(provenance.captured_before_restructure)
        self.assertIn(
            "Captured before body replacement/restructuring: yes",
            provenance.to_comment(),
        )

    def test_empty_original_body_is_preserved_exactly(self):
        provenance = MODULE.capture_intake_provenance(
            intake_issue="#12",
            governed_operation="#34",
            original_body="",
            labels=["feature-request"],
        )
        self.assertEqual(provenance.original_body, "")
        self.assertTrue(provenance.to_comment().endswith("### Original unformatted issue body\n\n"))

    def test_traceability_identifiers_are_required(self):
        with self.assertRaisesRegex(ValueError, "intake_issue is required"):
            MODULE.capture_intake_provenance(
                intake_issue="",
                governed_operation="#34",
                original_body="body",
                labels=["bug-fix"],
            )
        with self.assertRaisesRegex(ValueError, "governed_operation is required"):
            MODULE.capture_intake_provenance(
                intake_issue="#12",
                governed_operation="",
                original_body="body",
                labels=["bug-fix"],
            )


if __name__ == "__main__":
    unittest.main()
