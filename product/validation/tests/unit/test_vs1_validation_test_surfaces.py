from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SURFACE = ROOT / "product/scripts/test-validation"
COMMON = ROOT / "scripts/test-validation"

SUCCESS_CLASSES = {
    "successful-zero-applicable",
    "successful-applicable-execution",
}


class VS1ValidationTestSurfaceTests(unittest.TestCase):
    def test_product_test_surface_exists_and_is_executable(self) -> None:
        self.assertTrue(SURFACE.is_file())
        self.assertTrue(os.access(SURFACE, os.X_OK))

    def test_product_test_surface_exposes_vs2_machine_result_without_placeholder(self) -> None:
        completed = subprocess.run(
            [str(SURFACE), "--product"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.stderr, "")
        self.assertNotIn("lifecycle unavailable", completed.stdout)
        result = json.loads(completed.stdout)
        self.assertIn("applicability", result)
        self.assertIn("classification", result)
        self.assertIn("evidence", result)
        expected_returncode = 0 if result["classification"] in SUCCESS_CLASSES else 1
        self.assertEqual(completed.returncode, expected_returncode)

    def test_common_validation_invokes_generic_product_test_surface(self) -> None:
        text = COMMON.read_text(encoding="utf-8")
        self.assertIn('"$root/repo/scripts/test-validation"', text)
        self.assertIn('"$root/product/scripts/test-validation"', text)
        self.assertNotIn('"$root/product/scripts/test-product"', text)

    def test_product_test_surface_rejects_unknown_modes(self) -> None:
        completed = subprocess.run(
            [str(SURFACE), "unexpected-mode"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("validation test error: unknown mode: unexpected-mode", completed.stderr)


if __name__ == "__main__":
    unittest.main()
