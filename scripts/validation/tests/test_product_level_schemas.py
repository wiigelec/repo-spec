from __future__ import annotations

import json
from pathlib import Path

from validation.schema_subset import load_product_schemas, validate_instance

from .mutation_support import expect_failure


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "product-validation"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text())


def assert_valid(schema: dict, name: str) -> None:
    validate_instance(load_fixture(name), schema, f"scripts/validation/tests/fixtures/product-validation/{name}", schema)


def assert_invalid(schema: dict, name: str, fragment: str) -> None:
    expect_failure(
        name,
        lambda: validate_instance(load_fixture(name), schema, f"scripts/validation/tests/fixtures/product-validation/{name}", schema),
        fragment,
    )


def run_product_level_schema_tests(repo_root: Path) -> None:
    schemas = load_product_schemas(repo_root)

    assert_valid(schemas["product.level-0"], "level-0-candidate.json")
    assert_valid(schemas["product.level-1"], "level-1-accepted.json")
    assert_valid(schemas["product.level-2"], "level-2-accepted.json")
    assert_valid(schemas["product.level-3"], "level-3-accepted.json")

    assert_invalid(schemas["product.level-0"], "level-0-invalid-level-constant.json", "const mismatch")
    assert_invalid(schemas["product.level-0"], "level-0-invalid-reserved-field.json", "additionalProperties disallowed: primitives")
    assert_invalid(schemas["product.level-1"], "level-1-invalid-missing-section.json", "missing required property primitives")
    assert_invalid(schemas["product.level-2"], "level-2-invalid-common-field-redefinition.json", "must be a string")
    assert_invalid(schemas["product.level-3"], "level-3-invalid-wrong-constant.json", "const mismatch")
