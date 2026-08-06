from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from validation.generated_outputs import check_generated_document_write_behavior
from validation.repository_checks import validate_repo

from .mutation_support import create_repo_fixture, expect_failure, mutate_json


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "product-validation"


def install_fixture(temp_repo: Path, source_name: str, dest_path: str) -> None:
    source = FIXTURE_DIR / source_name
    target = temp_repo / dest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def configure_spec(
    temp_repo: Path,
    source_name: str,
    dest_path: str,
    *,
    spec_id: str,
    level: int,
    status: str = "candidate",
    dependency_ids: list[str] | None = None,
) -> None:
    install_fixture(temp_repo, source_name, dest_path)
    mutate_json(
        temp_repo / dest_path,
        lambda spec: (
            spec.__setitem__("spec_id", spec_id),
            spec.__setitem__("status", status),
            spec.__setitem__("level", level),
            spec.__setitem__("dependencies", [{"spec_id": dep} for dep in (dependency_ids or [])]),
            spec.__setitem__(
                "derived_artifacts",
                [
                    {"type": "markdown", "path": f"product/derived/specs/product/{Path(dest_path).stem}.md"}
                ]
                if spec.get("derived_artifacts")
                else spec.get("derived_artifacts", []),
            ),
            spec,
        )[-1],
    )


def write_manifest(temp_repo: Path, entries: list[dict[str, object]]) -> None:
    mutate_json(
        temp_repo / "product/specs/product/manifest.json",
        lambda manifest: manifest.__setitem__("product_specifications", entries) or manifest,
    )


def build_case(temp_repo: Path, source: dict[str, object], target: dict[str, object]) -> None:
    install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
    configure_spec(temp_repo, source["fixture"], source["path"], spec_id=source["spec_id"], level=source["level"], status=source["status"], dependency_ids=[target["spec_id"]])
    configure_spec(temp_repo, target["fixture"], target["path"], spec_id=target["spec_id"], level=target["level"], status=target["status"], dependency_ids=[])
    write_manifest(
        temp_repo,
        [
            {"spec_id": source["spec_id"], "path": source["path"], "status": source["status"], "level": source["level"]},
            {"spec_id": target["spec_id"], "path": target["path"], "status": target["status"], "level": target["level"]},
        ],
    )
    check_generated_document_write_behavior(temp_repo)


def run_product_dependency_direction_tests(repo_root: Path) -> None:
    cases = [
        ({"fixture": "level-0-candidate.json", "path": "product/specs/product/level-0/src.json", "spec_id": "product.l0-src", "level": 0, "status": "candidate"}, {"fixture": "level-0-candidate.json", "path": "product/specs/product/level-0/tgt.json", "spec_id": "product.l0-tgt", "level": 0, "status": "candidate"}, True),
        ({"fixture": "level-1-accepted.json", "path": "product/specs/product/level-1/src.json", "spec_id": "product.l1-src", "level": 1, "status": "candidate"}, {"fixture": "level-0-candidate.json", "path": "product/specs/product/level-0/tgt.json", "spec_id": "product.l0-tgt", "level": 0, "status": "candidate"}, True),
        ({"fixture": "level-1-accepted.json", "path": "product/specs/product/level-1/src.json", "spec_id": "product.l1-src", "level": 1, "status": "candidate"}, {"fixture": "level-1-accepted.json", "path": "product/specs/product/level-1/tgt.json", "spec_id": "product.l1-tgt", "level": 1, "status": "candidate"}, True),
        ({"fixture": "level-2-accepted.json", "path": "product/specs/product/level-2/src.json", "spec_id": "product.l2-src", "level": 2, "status": "candidate"}, {"fixture": "level-0-candidate.json", "path": "product/specs/product/level-0/tgt.json", "spec_id": "product.l0-tgt", "level": 0, "status": "candidate"}, True),
        ({"fixture": "level-2-accepted.json", "path": "product/specs/product/level-2/src.json", "spec_id": "product.l2-src", "level": 2, "status": "candidate"}, {"fixture": "level-1-accepted.json", "path": "product/specs/product/level-1/tgt.json", "spec_id": "product.l1-tgt", "level": 1, "status": "candidate"}, True),
        ({"fixture": "level-2-accepted.json", "path": "product/specs/product/level-2/src.json", "spec_id": "product.l2-src", "level": 2, "status": "candidate"}, {"fixture": "level-2-accepted.json", "path": "product/specs/product/level-2/tgt.json", "spec_id": "product.l2-tgt", "level": 2, "status": "candidate"}, True),
        ({"fixture": "level-3-accepted.json", "path": "product/specs/product/level-3/src.json", "spec_id": "product.l3-src", "level": 3, "status": "candidate"}, {"fixture": "level-0-candidate.json", "path": "product/specs/product/level-0/tgt.json", "spec_id": "product.l0-tgt", "level": 0, "status": "candidate"}, True),
        ({"fixture": "level-3-accepted.json", "path": "product/specs/product/level-3/src.json", "spec_id": "product.l3-src", "level": 3, "status": "candidate"}, {"fixture": "level-1-accepted.json", "path": "product/specs/product/level-1/tgt.json", "spec_id": "product.l1-tgt", "level": 1, "status": "candidate"}, True),
        ({"fixture": "level-3-accepted.json", "path": "product/specs/product/level-3/src.json", "spec_id": "product.l3-src", "level": 3, "status": "candidate"}, {"fixture": "level-2-accepted.json", "path": "product/specs/product/level-2/tgt.json", "spec_id": "product.l2-tgt", "level": 2, "status": "candidate"}, True),
        ({"fixture": "level-3-accepted.json", "path": "product/specs/product/level-3/src.json", "spec_id": "product.l3-src", "level": 3, "status": "candidate"}, {"fixture": "level-3-accepted.json", "path": "product/specs/product/level-3/tgt.json", "spec_id": "product.l3-tgt", "level": 3, "status": "candidate"}, True),
        ({"fixture": "level-0-candidate.json", "path": "product/specs/product/level-0/src.json", "spec_id": "product.l0-src", "level": 0, "status": "candidate"}, {"fixture": "level-1-accepted.json", "path": "product/specs/product/level-1/tgt.json", "spec_id": "product.l1-tgt", "level": 1, "status": "candidate"}, False),
        ({"fixture": "level-0-candidate.json", "path": "product/specs/product/level-0/src.json", "spec_id": "product.l0-src", "level": 0, "status": "candidate"}, {"fixture": "level-2-accepted.json", "path": "product/specs/product/level-2/tgt.json", "spec_id": "product.l2-tgt", "level": 2, "status": "candidate"}, False),
        ({"fixture": "level-0-candidate.json", "path": "product/specs/product/level-0/src.json", "spec_id": "product.l0-src", "level": 0, "status": "candidate"}, {"fixture": "level-3-accepted.json", "path": "product/specs/product/level-3/tgt.json", "spec_id": "product.l3-tgt", "level": 3, "status": "candidate"}, False),
        ({"fixture": "level-1-accepted.json", "path": "product/specs/product/level-1/src.json", "spec_id": "product.l1-src", "level": 1, "status": "candidate"}, {"fixture": "level-2-accepted.json", "path": "product/specs/product/level-2/tgt.json", "spec_id": "product.l2-tgt", "level": 2, "status": "candidate"}, False),
        ({"fixture": "level-1-accepted.json", "path": "product/specs/product/level-1/src.json", "spec_id": "product.l1-src", "level": 1, "status": "candidate"}, {"fixture": "level-3-accepted.json", "path": "product/specs/product/level-3/tgt.json", "spec_id": "product.l3-tgt", "level": 3, "status": "candidate"}, False),
        ({"fixture": "level-2-accepted.json", "path": "product/specs/product/level-2/src.json", "spec_id": "product.l2-src", "level": 2, "status": "candidate"}, {"fixture": "level-3-accepted.json", "path": "product/specs/product/level-3/tgt.json", "spec_id": "product.l3-tgt", "level": 3, "status": "candidate"}, False),
    ]

    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        for index, (source, target, is_valid) in enumerate(cases):
            temp_repo = create_repo_fixture(repo_root, temp_root, index)
            build_case(temp_repo, source, target)
            if is_valid:
                validate_repo(temp_repo)
            else:
                expect_failure(
                    f"dependency direction {source['spec_id']} -> {target['spec_id']}",
                    lambda temp_repo=temp_repo: validate_repo(temp_repo),
                    f"product dependency direction failed: {source['spec_id']} (level {source['level']}) -> {target['spec_id']} (level {target['level']})",
                )

    print("ok: product dependency direction tests")
