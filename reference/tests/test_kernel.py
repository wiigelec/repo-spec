from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from product.kernel import kernel_identity


class KernelTests(unittest.TestCase):
    def test_kernel_identity(self) -> None:
        self.assertEqual(kernel_identity(), "reference-kernel")


if __name__ == "__main__":
    unittest.main()
