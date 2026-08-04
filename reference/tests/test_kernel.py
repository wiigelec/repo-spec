from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from product.kernel import canonical_text


class KernelTests(unittest.TestCase):
    def test_canonical_text(self) -> None:
        self.assertEqual(canonical_text("  Reference   Kernel  "), "reference kernel")


if __name__ == "__main__":
    unittest.main()
