from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REFERENCE = ROOT / "product/docs/initializer/README.md"
LAUNCHER = ROOT / "product/scripts/repo-spec-init"


class Issue332ReferenceConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = REFERENCE.read_text()

    def test_reference_describes_closed_required_request_shape(self) -> None:
        request_section = self.text[
            self.text.index("### Request schema (version 1)"):
            self.text.index("## Framework inventory and source inspection")
        ]
        for field in ("`schema_version`", "`destination`", "`authority`", "`source`", "`product`"):
            self.assertIn(field, request_section)
        self.assertIn("No other root fields are accepted.", request_section)
        self.assertNotIn("`deferred`", request_section)
        self.assertNotIn("`metadata`", request_section)
        self.assertNotRegex(request_section, r"\| `source` \| object \|[^\n]*Optional")
        self.assertNotRegex(request_section, r"\| `product` \| object \|[^\n]*Optional")

    def test_reference_uses_local_structured_exact_source_identity(self) -> None:
        request_section = self.text[
            self.text.index("### Request schema (version 1)"):
            self.text.index("## Framework inventory and source inspection")
        ]
        self.assertIn('"object_format": "sha1"', request_section)
        self.assertRegex(request_section, r'"object_id": "[0-9a-f]{40}"')
        self.assertIn('"repository": "/work/repo-spec"', request_section)
        self.assertNotRegex(request_section, r'"repository"\s*:\s*"https?://')
        self.assertNotRegex(request_section, r'"revision"\s*:\s*"[0-9a-f]{40}"')

    def test_documented_complete_request_passes_real_intake_validator(self) -> None:
        marker = "#### Complete valid request"
        tail = self.text[self.text.index(marker):]
        match = re.search(r"```json\n(\{.*?\})\n```", tail, flags=re.S)
        self.assertIsNotNone(match)
        request = json.loads(match.group(1))
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

    def test_unavailable_legacy_commands_are_not_presented_as_supported(self) -> None:
        for command in ("stage-framework", "stage-framework-and-foundations"):
            self.assertIn(f"`{command}`", self.text)
        self.assertIn(
            "retained only as explicit unavailable/fail-closed compatibility surfaces",
            self.text,
        )
        self.assertNotIn(
            "product/scripts/repo-spec-init stage-framework <request.json>",
            self.text,
        )
        self.assertNotIn(
            "product/scripts/repo-spec-init stage-framework-and-foundations <request.json>",
            self.text,
        )

    def test_generated_product_foundations_are_product_rooted(self) -> None:
        foundations = self.text[
            self.text.index("## Product foundations"):
            self.text.index("## Destination preflight and promotion")
        ]
        for prefix in (
            "product/docs/direction/evidence/",
            "product/docs/overview/<slug>-OVERVIEW.md",
            "product/docs/decompositions/<slug>-DECOMPOSITION.md",
            "product/docs/plans/<slug>-IMPLEMENTATION-PLAN.md",
        ):
            self.assertIn(prefix, foundations)
        self.assertNotIn("`repo/docs/overview/<slug>-OVERVIEW.md`", foundations)
        self.assertNotIn("`repo/docs/decompositions/<slug>-DECOMPOSITION.md`", foundations)
        self.assertNotIn("`repo/docs/plans/<slug>-IMPLEMENTATION-PLAN.md`", foundations)


if __name__ == "__main__":
    unittest.main()
