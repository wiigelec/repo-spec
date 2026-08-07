"""Product-owned generated-document freshness validation."""

from __future__ import annotations

from docgen import SPECIAL_RENDERERS, render_spec_projection

from validation.errors import fail
from validation.repository_checks import ValidationContext, expect, resolve_repo_path


def check_product_generated_freshness(context: ValidationContext) -> None:
    expect(context.product is not None, "product validation context missing")

    specs = context.product.specs
    source_paths = context.product.source_paths
    derived_root = context.repo_root / "product/derived/specs/product"
    expected_markdown_paths: set[str] = set()

    for spec_id in sorted(specs, key=lambda item: source_paths[item]):
        spec = specs[spec_id]
        source_path = source_paths[spec_id]

        for artifact in spec.get("derived_artifacts", []):
            relative_path = artifact["path"]
            path = resolve_repo_path(context.repo_root, relative_path)
            renderer_id = artifact.get("renderer")

            if renderer_id is None:
                expect(
                    artifact["type"] == "markdown",
                    "generated-document freshness failed: "
                    f"unsupported derived artifact type without renderer: "
                    f"{artifact['type']}",
                )
                content = render_spec_projection(
                    spec["title"],
                    source_path,
                    spec,
                    include_authoritative_specs=False,
                )
            else:
                renderer = SPECIAL_RENDERERS.get(renderer_id)
                expect(
                    renderer is not None,
                    "generated-document freshness failed: "
                    f"unsupported renderer: {renderer_id}",
                )
                content = renderer(spec)

            if (
                relative_path.endswith(".md")
                and relative_path.startswith(
                    derived_root.relative_to(context.repo_root).as_posix() + "/"
                )
            ):
                expected_markdown_paths.add(relative_path)

            if not path.exists() or path.read_text() != content:
                fail(
                    "generated-document freshness failed: "
                    f"source {source_path} -> output {relative_path}"
                )

    actual_markdown_paths: set[str] = set()
    if derived_root.exists():
        actual_markdown_paths = {
            path.relative_to(context.repo_root).as_posix()
            for path in derived_root.rglob("*.md")
            if path.is_file()
        }

    missing = sorted(expected_markdown_paths - actual_markdown_paths)
    extra = sorted(actual_markdown_paths - expected_markdown_paths)
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"missing derived markdown: {', '.join(missing)}")
        if extra:
            parts.append(f"orphaned derived markdown: {', '.join(extra)}")
        fail("generated-document freshness failed: " + "; ".join(parts))
