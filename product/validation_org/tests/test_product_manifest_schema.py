from __future__ import annotations

import json
from pathlib import Path

from validation.core.schema_subset import validate_instance
from validation.checks.product_state import load_product_schemas

from .mutation_support import expect_failure


FIXTURE_DIR = Path(__file__).resolve().parent


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text())


def assert_valid(schema: dict, name: str) -> None:
        validate_instance(load_fixture(name), schema, f"repo/scripts/validation/tests/fixtures/product-manifest/{name}", schema)


def assert_invalid(schema: dict, name: str, fragment: str) -> None:
    expect_failure(
        name,
            lambda: validate_instance(load_fixture(name), schema, f"repo/scripts/validation/tests/fixtures/product-manifest/{name}", schema),
        fragment,
    )


def run_product_manifest_schema_tests(repo_root: Path) -> None:
    schema = load_product_schemas(repo_root)["product.manifest"]

    # Level agreement stays semantic until a base product-specification schema exists.
    assert_valid(schema, "valid-empty.json")
    assert_valid(schema, "valid-candidate.json")
    assert_valid(schema, "valid-accepted.json")

    assert_invalid(schema, "invalid-missing-required.json", "additionalProperties disallowed: active")
    assert_invalid(schema, "invalid-lifecycle.json", "enum mismatch")
    assert_invalid(schema, "invalid-level.json", "oneOf mismatch")
    assert_invalid(schema, "invalid-registry-entry.json", "oneOf mismatch")
    assert_invalid(schema, "invalid-path.json", "oneOf mismatch")
    assert_invalid(schema, "invalid-derived-path.json", "oneOf mismatch")
