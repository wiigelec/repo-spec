from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from product.primitives import normalize_identifier


class PrimitiveTests(unittest.TestCase):
    def test_normalize_identifier(self) -> None:
        self.assertEqual(normalize_identifier("  Reference_Kernel   Primitives  "), "reference-kernel primitives")


if __name__ == "__main__":
    unittest.main()
