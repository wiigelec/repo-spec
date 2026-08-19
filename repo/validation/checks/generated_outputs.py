"""Generated-artifact validation extension point."""

from __future__ import annotations

from pathlib import Path
from docgen import check_generated_outputs, render_all, write_all
from repo_model import RepositoryError
from ..core.errors import fail

from ..core.context import ValidationContext
from ..core.errors import expect, fail
from ..core.paths import resolve_repo_path

def check_generated_document_freshness(repo_root: Path) -> None:
    try:
        check_generated_outputs(repo_root)
    except (RepositoryError, ValueError) as exc:
        fail(f"generated-document freshness failed: {exc}")

def check_generated_document_write_behavior(repo_root: Path) -> None:
    try:
        render_all(repo_root)
        write_all(repo_root)
        check_generated_outputs(repo_root)
    except (RepositoryError, ValueError) as exc:
        fail(f"generated-document write failed: {exc}")

def check_generated_document_freshness_phase(context: ValidationContext) -> None:
    check_generated_document_freshness(context.repo_root)

def _check_repository_generated_freshness(
    context: ValidationContext,
) -> None:
    from docgen import SPECIAL_RENDERERS, render_spec_projection

    specs = context.repository.specs
    source_paths = context.repository.source_paths
    derived_root = context.repo_root / "repo/derived/specs/repo"
    expected_markdown_paths: set[str] = set()

    for spec_id in sorted(specs, key=lambda item: source_paths[item]):
        spec = specs[spec_id]
        source_path = source_paths[spec_id]

        for artifact in spec.get("derived_artifacts", []):
            relative_path = artifact["path"]

            # Repository validation owns only generated outputs under repo/.
            # Cross-domain adapters remain declared and are validated later by
            # root/aggregate validation.
            if not (
                relative_path == "repo"
                or relative_path.startswith("repo/")
            ):
                continue

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
                    include_authoritative_specs=(spec_id == "repo.manifest"),
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
