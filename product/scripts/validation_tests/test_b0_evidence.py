from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from product_validation.b0_evidence import BASELINE_PATH, CHUNK_ROOT, check_b0_evidence
from validation.tests.mutation_support import expect_failure, mutate_json


def run_b0_evidence_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-b0-evidence-") as temp_root_name:
        temp_root = Path(temp_root_name)

        def fixture(index: int) -> Path:
            target = temp_root / f"fixture-{index}" / CHUNK_ROOT.parent
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(repo_root / CHUNK_ROOT.parent, target)
            return temp_root / f"fixture-{index}"

        intact = fixture(0)
        check_b0_evidence(intact)

        missing = fixture(1)
        first_chunk = sorted((missing / CHUNK_ROOT).glob("*.json"))[0]
        first_chunk.unlink()
        expect_failure("missing B0 chunk", lambda: check_b0_evidence(missing), "chunk inventory mismatch")

        duplicate = fixture(2)
        level_zero_chunk = duplicate / CHUNK_ROOT / "product.initializer-level-0.json"

        def duplicate_key(chunk: dict) -> dict:
            chunk["entries"][1]["requirement_id"] = chunk["entries"][0]["requirement_id"]
            chunk["entries"][1]["composite_key"] = chunk["entries"][0]["composite_key"]
            return chunk

        mutate_json(level_zero_chunk, duplicate_key)
        expect_failure("duplicate B0 entry", lambda: check_b0_evidence(duplicate), "composite keys are duplicated")

        stale_index = fixture(3)
        mutate_json(
            stale_index / BASELINE_PATH,
            lambda baseline: baseline["entry_partition"]["chunks"][0].__setitem__("requirement_count", 0) or baseline,
        )
        expect_failure("stale B0 index", lambda: check_b0_evidence(stale_index), "requirement count mismatch")
