from __future__ import annotations

import json
from pathlib import Path

from product_validation.schema_subset import validate_instance
from product_validation.product_state import load_product_schemas

from .mutation_support import expect_failure


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "product-validation"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text())


def assert_valid(schema: dict, name: str) -> None:
        validate_instance(load_fixture(name), schema, f"repo/scripts/validation/tests/fixtures/product-validation/{name}", schema)


def assert_invalid(schema: dict, name: str, fragment: str) -> None:
    expect_failure(
        name,
            lambda: validate_instance(load_fixture(name), schema, f"repo/scripts/validation/tests/fixtures/product-validation/{name}", schema),
        fragment,
    )


def run_product_level_schema_tests(repo_root: Path) -> None:
    base_source = json.loads((repo_root / "product/schemas/product/product-spec-base.schema.json").read_text())
    assert "additionalProperties" not in base_source
    assert "correspondence" in base_source["required"]
    assert "correspondence" in base_source["properties"]
    assert base_source["properties"]["correspondence"]["$ref"] == "#/$defs/correspondence"
    assert base_source["$defs"]["correspondence"]["required"] == ["implementations", "tests", "conformance"]

    for level_name in ("product-level-0.schema.json", "product-level-1.schema.json", "product-level-2.schema.json", "product-level-3.schema.json"):
        source = json.loads((repo_root / "product/schemas/product" / level_name).read_text())
        assert source["allOf"][0]["$ref"] == "./product-spec-base.schema.json"
        assert source["unevaluatedProperties"] is False

    schemas = load_product_schemas(repo_root)

    assert_valid(schemas["product.level-0"], "level-0-candidate.json")
    assert_valid(schemas["product.level-1"], "level-1-accepted.json")
    assert_valid(schemas["product.level-2"], "level-2-accepted.json")
    assert_valid(schemas["product.level-3"], "level-3-accepted.json")

    assert_invalid(schemas["product.level-0"], "level-0-invalid-level-constant.json", "const mismatch")
    assert_invalid(schemas["product.level-0"], "level-0-invalid-reserved-field.json", "unevaluatedProperties disallowed: primitives")
    assert_invalid(schemas["product.level-1"], "level-1-invalid-missing-section.json", "missing required property primitives")
    assert_invalid(schemas["product.level-2"], "level-2-invalid-common-field-redefinition.json", "must be a string")
    assert_invalid(schemas["product.level-3"], "level-3-invalid-wrong-constant.json", "const mismatch")
