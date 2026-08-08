"""Structural validation for the chunked B0 conformance baseline."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from validation.repository_checks import expect
from validation.schema_subset import load_json


BASELINE_PATH = Path("product/evidence/b0/initializer-conformance-baseline.json")
CHUNK_ROOT = Path("product/evidence/b0/initializer-conformance-baseline")
MAX_ARTIFACT_BYTES = 128 * 1024


def _classification_counts(entries: list[dict[str, Any]], vocabulary: list[str]) -> dict[str, int]:
    counts = Counter(entry.get("classification") for entry in entries)
    expect(set(counts) <= set(vocabulary), "B0 evidence contains an unknown classification")
    return {classification: counts[classification] for classification in vocabulary}


def check_b0_evidence(repo_root: Path) -> None:
    baseline_path = repo_root / BASELINE_PATH
    if not baseline_path.exists():
        return

    baseline = load_json(baseline_path)
    expect(isinstance(baseline, dict), "B0 evidence root must be an object")
    expect("entries" not in baseline, "B0 evidence root must not contain monolithic entries")
    expect(
        baseline_path.stat().st_size <= MAX_ARTIFACT_BYTES,
        "B0 evidence root exceeds the context-size limit",
    )

    vocabulary = baseline.get("classification_vocabulary")
    partition = baseline.get("entry_partition")
    specifications = baseline.get("specification_counts")
    expect(isinstance(vocabulary, list), "B0 evidence classification vocabulary missing")
    expect(isinstance(partition, dict), "B0 evidence entry partition missing")
    expect(isinstance(specifications, list), "B0 evidence specification counts missing")
    chunk_index = partition.get("chunks")
    expect(isinstance(chunk_index, list), "B0 evidence chunk index missing")
    expect(
        [item.get("spec_id") for item in chunk_index]
        == [item.get("spec_id") for item in specifications],
        "B0 evidence chunk order does not match specification order",
    )

    indexed_paths = [item.get("path") for item in chunk_index]
    expect(all(isinstance(path, str) for path in indexed_paths), "B0 evidence chunk path missing")
    expect(len(indexed_paths) == len(set(indexed_paths)), "B0 evidence chunk paths are duplicated")
    actual_paths = sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / CHUNK_ROOT).glob("*.json")
    )
    expect(sorted(indexed_paths) == actual_paths, "B0 evidence chunk inventory mismatch")

    all_entries: list[dict[str, Any]] = []
    for specification, indexed in zip(specifications, chunk_index):
        relative_path = Path(indexed["path"])
        expect(relative_path.parent == CHUNK_ROOT, "B0 evidence chunk path escapes its root")
        chunk_path = repo_root / relative_path
        expect(chunk_path.stat().st_size <= MAX_ARTIFACT_BYTES, "B0 evidence chunk exceeds the context-size limit")
        expect(chunk_path.stat().st_size == indexed.get("byte_count"), "B0 evidence chunk byte count mismatch")
        chunk = load_json(chunk_path)
        entries = chunk.get("entries")
        expect(isinstance(entries, list), "B0 evidence chunk entries missing")
        expect(chunk.get("parent_artifact") == BASELINE_PATH.as_posix(), "B0 evidence parent artifact mismatch")
        expect(chunk.get("specification") == specification, "B0 evidence chunk specification mismatch")
        expect(indexed.get("level") == specification.get("level"), "B0 evidence chunk level mismatch")
        expect(
            len(entries) == specification.get("requirement_count") == indexed.get("requirement_count"),
            "B0 evidence chunk requirement count mismatch",
        )
        spec_id = specification.get("spec_id")
        expect(all(entry.get("spec_id") == spec_id for entry in entries), "B0 evidence entry specification mismatch")
        expect(
            all(entry.get("composite_key") == f"{spec_id}::{entry.get('requirement_id')}" for entry in entries),
            "B0 evidence composite key mismatch",
        )
        counts = _classification_counts(entries, vocabulary)
        blockers = sum(bool(entry.get("blocker", {}).get("is_blocker")) for entry in entries)
        expect(chunk.get("classification_counts") == counts == indexed.get("classification_counts"), "B0 evidence chunk classification counts mismatch")
        expect(chunk.get("blocker_count") == blockers == indexed.get("blocker_count"), "B0 evidence chunk blocker count mismatch")
        all_entries.extend(entries)

    composite_keys = [entry.get("composite_key") for entry in all_entries]
    expect(len(composite_keys) == len(set(composite_keys)), "B0 evidence composite keys are duplicated")
    inventory = baseline.get("inventory", {})
    aggregate_counts = _classification_counts(all_entries, vocabulary)
    expect(len(all_entries) == inventory.get("composite_keys"), "B0 evidence aggregate requirement count mismatch")
    expect(len(composite_keys) == inventory.get("unique_composite_keys"), "B0 evidence unique key count mismatch")
    expect(len(specifications) == inventory.get("accepted_specifications"), "B0 evidence aggregate specification count mismatch")
    expect(sum(bool(entry.get("blocker", {}).get("is_blocker")) for entry in all_entries) == inventory.get("blocker_count"), "B0 evidence aggregate blocker count mismatch")
    expect(
        all(inventory.get("classification_counts", {}).get(key) == value for key, value in aggregate_counts.items()),
        "B0 evidence aggregate classification counts mismatch",
    )
    completion = baseline.get("completion_summary", {})
    expect(completion.get("classification_counts") == aggregate_counts, "B0 evidence completion counts mismatch")
    expect(completion.get("classification_total") == len(all_entries), "B0 evidence completion total mismatch")
