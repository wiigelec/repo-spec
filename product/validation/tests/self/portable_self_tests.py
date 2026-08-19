"""Portable validation-framework self-test extension point."""

from __future__ import annotations

import tempfile
from pathlib import Path

from validation.core.errors import ValidationFailure
from validation.checks.domain import validate_product


def run_product_portable_self_tests(repo_root: Path) -> None:
    del repo_root

    with tempfile.TemporaryDirectory(prefix="product-validation-self-test-") as temp_name:
        inactive_repo = Path(temp_name)
        validate_product(inactive_repo)

    with tempfile.TemporaryDirectory(prefix="product-validation-self-test-") as temp_name:
        invalid_repo = Path(temp_name)
        product_specs = invalid_repo / "product/specs"
        product_specs.mkdir(parents=True)
        (product_specs / "product").write_text("not-a-directory\n", encoding="utf-8")
        try:
            validate_product(invalid_repo)
        except ValidationFailure:
            pass
        else:
            raise ValidationFailure(
                "product validation self-test failed: invalid product root was accepted"
            )

    print("ok: portable product validation self-tests")
