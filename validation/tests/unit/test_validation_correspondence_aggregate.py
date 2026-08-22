from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validation.checks.policy import RootValidationError
from validation.checks.specifications import validate


# validation-metadata: {"role": "helper"}
def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


# validation-metadata: {"role": "helper"}
def _build_fixture(root: Path) -> None:
    _write_json(root / "repo/specs/repo/manifest.json", {"authoritative_specs": [{"spec_id": "repo.alpha", "path": "repo/specs/repo/alpha.json"}]})
    _write_json(root / "repo/specs/repo/alpha.json", {"spec_id": "repo.alpha", "status": "accepted", "normative_requirements": [{"id": "RA-001"}]})
    _write_json(root / "product/specs/product/manifest.json", {"product_specifications": [{"spec_id": "product.beta", "path": "product/specs/product/level-0/beta.json"}]})
    _write_json(root / "product/specs/product/level-0/beta.json", {"spec_id": "product.beta", "status": "accepted", "normative_requirements": [{"id": "PB-001"}]})
    _write_json(root / "repo/validation/packages/repo.alpha/RA-001.json", {"normative_reference": {"spec_id": "repo.alpha", "requirement_id": "RA-001"}})
    _write_json(root / "product/validation/packages/product.beta/PB-001.json", {"normative_reference": {"spec_id": "product.beta", "requirement_id": "PB-001"}})


class ValidationCorrespondenceAggregateTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_exact_cross_domain_correspondence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            _build_fixture(root)
            validate(root)

    # validation-metadata: {"role": "helper"}
    def test_missing_product_package_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            _build_fixture(root)
            (root / "product/validation/packages/product.beta/PB-001.json").unlink()
            with self.assertRaisesRegex(RootValidationError, "missing active package"):
                validate(root)

    # validation-metadata: {"role": "helper"}
    def test_cross_domain_duplicate_package_coordinate_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            _build_fixture(root)
            _write_json(root / "product/validation/packages/repo.alpha/RA-001.json", {"normative_reference": {"spec_id": "repo.alpha", "requirement_id": "RA-001"}})
            with self.assertRaisesRegex(RootValidationError, "duplicate package coordinate"):
                validate(root)


if __name__ == "__main__":
    unittest.main()
