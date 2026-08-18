from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SURFACE = ROOT / "product/scripts/test-product"


class VS1ValidationTestSurfaceTests(unittest.TestCase):
    def test_product_test_surface_exists_and_is_executable(self) -> None:
        self.assertTrue(SURFACE.is_file())
        self.assertTrue(os.access(SURFACE, os.X_OK))

    def test_product_test_surface_preserves_stable_identity_after_vs2_activation(self) -> None:
        completed = subprocess.run(
            [str(SURFACE)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        result = json.loads(completed.stdout)
        self.assertEqual(result["applicability"], "zero-applicable")
        self.assertEqual(result["classification"], "successful-zero-applicable")
        self.assertEqual(result["obligations"], [])

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
        self.assertIn("product test error: unknown mode: unexpected-mode", completed.stderr)


if __name__ == "__main__":
    unittest.main()
