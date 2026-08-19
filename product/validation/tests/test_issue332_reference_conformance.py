from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE = ROOT / "product/docs/initializer/README.md"
LAUNCHER = ROOT / "product/scripts/repo-spec-init"


def documented_internal_request(text: str) -> dict[str, object]:
    start_marker = "## Internal canonical request"
    end_marker = "## Lower-level developer interface"
    section = text[text.index(start_marker):text.index(end_marker)]
    fence = "```json"
    start = section.index(fence) + len(fence)
    end = section.index("```", start)
    payload = section[start:end].strip()
    return json.loads(payload)


class Issue332ReferenceConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REFERENCE.read_text()

    def test_reference_describes_canonical_normal_user_command(self) -> None:
        self.assertIn("repo-spec init --repo /path/to/new/repository-name", self.text)
        self.assertIn("No user-authored JSON is required for the normal workflow.", self.text)

    def test_reference_describes_closed_v2_internal_request_shape(self) -> None:
        request = documented_internal_request(self.text)
        self.assertEqual(
            request,
            {
                "schema_version": "2",
                "destination": "/absolute/path/to/new/repository-name",
            },
        )
        for legacy in ("authority", "source", "product", "profile"):
            self.assertNotIn(legacy, request)
        self.assertIn("Unknown fields are rejected.", self.text)

    def test_documented_v2_request_passes_real_intake_validator(self) -> None:
        request = documented_internal_request(self.text)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "request.json"
            path.write_text(json.dumps(request))
            proc = subprocess.run(
                [str(LAUNCHER), "validate-request", str(path)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_reference_describes_local_exact_framework_provenance(self) -> None:
        start = self.text.index("## Local framework provenance")
        end = self.text.index("## What bootstrap creates")
        section = self.text[start:end]
        self.assertIn("exact clean `HEAD` commit", section)
        self.assertIn("fails closed", section)
        self.assertIn("not a local Git repository", section)
        self.assertIn("unsupported Git object format", section)

    def test_reference_excludes_product_foundations_from_bootstrap(self) -> None:
        start = self.text.index("## What bootstrap does not create")
        end = self.text.index("## Internal canonical request")
        section = self.text[start:end]
        for phrase in (
            "product ID or product identity",
            "product direction material or direction evidence",
            "functional-set lifecycle",
            "product decomposition",
            "product specifications or product manifest authority",
            "product implementation plan",
        ):
            self.assertIn(phrase, section)

    def test_reference_keeps_lower_level_request_interface_subordinate(self) -> None:
        start = self.text.index("## Lower-level developer interface")
        end = self.text.index("## Transaction safety")
        section = self.text[start:end]
        self.assertIn("product/scripts/repo-spec-init --request request.json", section)
        self.assertIn("schema-version-2 request contains only `schema_version` and `destination`", section)
        self.assertIn("not the recommended normal-user workflow", section)
        self.assertNotIn("stage-framework", section)
        self.assertNotIn("stage-framework-and-foundations", section)


if __name__ == "__main__":
    unittest.main()
