from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validation.checks.domain import _load_product_only_context
from validation.checks.specifications import check_product_validation_correspondence_packages_phase
from validation.core.errors import ValidationFailure


class ProductValidationCorrespondencePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[4]

    def _copy_fixture(self) -> Path:
        temp = Path(tempfile.mkdtemp(prefix="product-validation-correspondence-"))
        for rel in ("repo", "product"):
            shutil.copytree(self.repo_root / rel, temp / rel)
        return temp

    def test_current_product_packages_are_valid(self) -> None:
        check_product_validation_correspondence_packages_phase(_load_product_only_context(self.repo_root))

    def test_missing_active_package_fails(self) -> None:
        root = self._copy_fixture()
        try:
            next((root / "product/validation/packages").rglob("*.json")).unlink()
            with self.assertRaises(ValidationFailure):
                check_product_validation_correspondence_packages_phase(_load_product_only_context(root))
        finally:
            shutil.rmtree(root)

    def test_path_binding_mismatch_fails(self) -> None:
        root = self._copy_fixture()
        try:
            victim = next((root / "product/validation/packages").rglob("*.json"))
            data = json.loads(victim.read_text())
            data["normative_reference"]["requirement_id"] = "WRONG-999"
            victim.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
            with self.assertRaises(ValidationFailure):
                check_product_validation_correspondence_packages_phase(_load_product_only_context(root))
        finally:
            shutil.rmtree(root)

    def test_rationale_divergence_fails(self) -> None:
        root = self._copy_fixture()
        try:
            victim = next((root / "product/validation/packages").rglob("*.json"))
            data = json.loads(victim.read_text())
            data["validation_rationale"] = "divergent"
            victim.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
            with self.assertRaises(ValidationFailure):
                check_product_validation_correspondence_packages_phase(_load_product_only_context(root))
        finally:
            shutil.rmtree(root)

    def test_invented_task_ownership_fails(self) -> None:
        root = self._copy_fixture()
        try:
            victim = next((root / "product/validation/packages").rglob("*.json"))
            data = json.loads(victim.read_text())
            data["tasks"] = [{"task_id":"product.fake","source":"product/validation/checks/policy.py","callable":"check_validation_layout"}]
            victim.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
            with self.assertRaises(ValidationFailure):
                check_product_validation_correspondence_packages_phase(_load_product_only_context(root))
        finally:
            shutil.rmtree(root)


if __name__ == "__main__":
    unittest.main()
