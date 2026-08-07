from __future__ import annotations

import copy
import json
from pathlib import Path

from docgen import render_spec_projection
from validation.tests.mutation_support import expect_render_change


FIXTURE_PATH = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "product-validation"
    / "level-1-accepted.json"
)


def run_product_projection_rendering_tests(repo_root: Path) -> None:
    del repo_root

    correspondence_spec = json.loads(FIXTURE_PATH.read_text())
    renderer = lambda spec: render_spec_projection(
        spec["title"],
        "product/specs/product/level-1/primitive.json",
        spec,
    )

    expect_render_change(
        "product correspondence projected requirement",
        renderer,
        correspondence_spec,
        lambda spec: spec["correspondence"]["conformance"][0].__setitem__(
            "status",
            "not-applicable",
        ),
    )

    correspondence_render = renderer(correspondence_spec)
    shuffled_correspondence = copy.deepcopy(correspondence_spec)
    shuffled_correspondence["correspondence"]["implementations"].reverse()
    shuffled_correspondence["correspondence"]["tests"].reverse()
    shuffled_correspondence["correspondence"]["conformance"].reverse()
    assert renderer(shuffled_correspondence) == correspondence_render

    expect_render_change(
        "product primitive projected requirement",
        renderer,
        correspondence_spec,
        lambda spec: spec["normative_requirements"][0].__setitem__(
            "text",
            "Changed primitive requirement",
        ),
    )

    print("ok: product projection rendering tests")
