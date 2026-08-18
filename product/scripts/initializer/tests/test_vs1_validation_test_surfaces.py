from __future__ import annotations

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

    def test_product_test_surface_fails_closed_until_vs2_lifecycle_exists(self) -> None:
        completed = subprocess.run(
            [str(SURFACE)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertIn("product test error: lifecycle unavailable", completed.stderr)
        self.assertIn("separately governed VS2 implementation", completed.stderr)

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
