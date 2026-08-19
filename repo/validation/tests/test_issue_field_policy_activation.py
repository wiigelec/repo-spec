import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


POLICY_PATH = pathlib.Path(__file__).resolve().parents[1] / "github/github_field_policy.py"
SPEC = importlib.util.spec_from_file_location("github_field_policy", POLICY_PATH)
POLICY = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = POLICY
SPEC.loader.exec_module(POLICY)


class IssueFieldPolicyActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = pathlib.Path(__file__).resolve().parents[3]
        cls.fields = POLICY.load_fields(
            cls.repo_root,
            "repo/specs/repo/governing-issue.json",
            "issue_fields",
        )

    def write_event(self, body, labels):
        payload = {
            "issue": {
                "body": body,
                "labels": [{"name": label} for label in labels],
            }
        }
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        json.dump(payload, handle)
        handle.close()
        return pathlib.Path(handle.name)

    def test_ordinary_unformatted_intake_bypasses_governed_field_policy(self):
        path = self.write_event("plain intake prose", ["bug-fix"])
        try:
            body, governed = POLICY.load_issue_from_event(path)
            self.assertEqual(body, "plain intake prose")
            self.assertFalse(governed)
            POLICY.check_issue_event(body, governed, self.fields, self.repo_root)
        finally:
            path.unlink()

    def test_governed_work_requires_canonical_fields(self):
        path = self.write_event("plain intake prose", ["governed-work"])
        try:
            body, governed = POLICY.load_issue_from_event(path)
            self.assertTrue(governed)
            with self.assertRaises(POLICY.PolicyError):
                POLICY.check_issue_event(body, governed, self.fields, self.repo_root)
        finally:
            path.unlink()

    def test_non_governed_issue_with_unrelated_labels_still_bypasses(self):
        path = self.write_event("plain intake prose", ["documentation", "feature-request"])
        try:
            body, governed = POLICY.load_issue_from_event(path)
            self.assertFalse(governed)
            POLICY.check_issue_event(body, governed, self.fields, self.repo_root)
        finally:
            path.unlink()

    def test_explicit_body_validation_remains_strict(self):
        with self.assertRaises(POLICY.PolicyError):
            POLICY.check_issue("plain intake prose", self.fields, self.repo_root)

    def test_pr_event_loader_behavior_is_unchanged(self):
        payload = {"pull_request": {"body": "## Governing issue\n#410"}}
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            json.dump(payload, handle)
            path = pathlib.Path(handle.name)
        try:
            self.assertEqual(
                POLICY.load_body_from_event(path, "pr"),
                "## Governing issue\n#410",
            )
        finally:
            path.unlink()


    def test_profile_workflow_validates_governed_label_transition(self):
        source = self.repo_root / "repo/profiles/github/workflows/github-field-policy.yml"
        installed = self.repo_root / ".github/workflows/github-field-policy.yml"
        source_text = source.read_text()
        installed_text = installed.read_text()
        self.assertEqual(source_text, installed_text)
        self.assertIn(
            "types: [opened, edited, reopened, labeled]",
            source_text,
        )
        self.assertNotIn(
            "types: [opened, edited, reopened]\n",
            source_text,
        )


if __name__ == "__main__":
    unittest.main()
