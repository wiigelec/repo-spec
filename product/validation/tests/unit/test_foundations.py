from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from initializer.foundations import (
    FoundationPlan,
    FoundationResult,
    FoundationError,
    build_foundation_plan,
    establish_product_foundations,
    OVERVIEW_CHUNK_COVERAGE,
)
from initializer.models import (
    FoundationArtifactStatus,
    InitializerError,
    _to_slug,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FoundationPlanTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_valid_plan(self):
        plan = FoundationPlan("my-product", ["/path/to/direction.md"], "#195")
        self.assertEqual(plan.product_id, "my-product")
        self.assertEqual(plan.product_slug, "my-product")
        self.assertEqual(plan.direction_material, ["/path/to/direction.md"])
        self.assertEqual(plan.governing_issue, "#195")

    # validation-metadata: {"role": "helper"}
    def test_slug_derivation(self):
        plan = FoundationPlan("My Product!", ["/doc.md"], "#195")
        self.assertEqual(plan.product_slug, "my-product")

    # validation-metadata: {"role": "helper"}
    def test_slug_spaces(self):
        plan = FoundationPlan("  Hello   World  ", ["/doc.md"], "#195")
        self.assertEqual(plan.product_slug, "hello-world")

    # validation-metadata: {"role": "helper"}
    def test_empty_id_rejected(self):
        with self.assertRaises(InitializerError):
            FoundationPlan("   ", ["/doc.md"], "#195")

    # validation-metadata: {"role": "helper"}
    def test_empty_material_rejected(self):
        with self.assertRaises(InitializerError):
            FoundationPlan("p", [], "#195")

    # validation-metadata: {"role": "helper"}
    def test_immutability(self):
        plan = FoundationPlan("p", ["/doc.md"], "#195")
        with self.assertRaises(AttributeError):
            plan.product_id = "other"  # type: ignore

    # validation-metadata: {"role": "helper"}
    def test_equality(self):
        a = FoundationPlan("p", ["/doc.md"], "#195")
        b = FoundationPlan("p", ["/doc.md"], "#195")
        c = FoundationPlan("q", ["/doc.md"], "#195")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    # validation-metadata: {"role": "helper"}
    def test_hash(self):
        a = FoundationPlan("p", ["/doc.md"], "#195")
        b = FoundationPlan("p", ["/doc.md"], "#195")
        self.assertEqual(hash(a), hash(b))

    # validation-metadata: {"role": "helper"}
    def test_to_slug_empty(self):
        slug = _to_slug("")
        self.assertEqual(slug, "product")

    # validation-metadata: {"role": "helper"}
    def test_to_slug_special_chars(self):
        slug = _to_slug("a!b@c#d$")
        self.assertEqual(slug, "a-b-c-d")


class FoundationResultTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_to_dict_structure(self):
        result = FoundationResult(
            product_id="p",
            product_slug="p",
            created=[{"path": "product/docs/overview/p-WHITEBOARD.md", "artifact": "overview-whiteboard-controlling"}],
            preserved=[],
            omitted=[],
            deferred=[],
            rejected=[],
        )
        d = result.to_dict()
        self.assertEqual(d["status"], "foundations_complete")
        self.assertEqual(d["product_id"], "p")
        self.assertEqual(d["product_slug"], "p")
        self.assertEqual(len(d["created"]), 1)
        self.assertEqual(len(d["rejected"]), 0)

    # validation-metadata: {"role": "helper"}
    def test_equality(self):
        a = FoundationResult("p", "p", [{"path": "a", "artifact": "x"}], [], [], [], [])
        b = FoundationResult("p", "p", [{"path": "a", "artifact": "x"}], [], [], [], [])
        c = FoundationResult("p", "p", [{"path": "b", "artifact": "x"}], [], [], [], [])
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class BuildFoundationPlanTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_build_from_valid_input(self):
        plan = build_foundation_plan("my-product", ["/path/to/dir.md"], "#195")
        self.assertIsInstance(plan, FoundationPlan)
        self.assertEqual(plan.product_id, "my-product")

    # validation-metadata: {"role": "helper"}
    def test_build_rejects_empty_product_id(self):
        with self.assertRaises(FoundationError):
            build_foundation_plan("", ["/path/to/dir.md"], "#195")


class Issue337CanonicalFoundationNamesTests(unittest.TestCase):


    # validation-metadata: {"role": "helper"}
    def test_overview_chunk_names_match_accepted_i2_contract(self):
        self.assertEqual(
            [item[0] for item in OVERVIEW_CHUNK_COVERAGE],
            [
                "01-collected-input.md",
                "02-provenance.md",
                "03-unresolved-intent.md",
            ],
        )

    # validation-metadata: {"role": "helper"}
    def test_legacy_chunk03_basename_is_not_present(self):
        self.assertNotIn(
            "03-users-principles-and-boundaries.md",
            [item[0] for item in OVERVIEW_CHUNK_COVERAGE],
        )


class EstablishFoundationsTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.staging = Path(tempfile.mkdtemp())
        self.plan = FoundationPlan("test-product", ["/path/to/direction.md"], "#195")

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.staging, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_no_staging_rejected(self):
        missing = Path(tempfile.mkdtemp())
        shutil.rmtree(missing)
        with self.assertRaises(FoundationError):
            establish_product_foundations(self.plan, missing)


    # validation-metadata: {"role": "helper"}
    def test_creates_overview_controlling(self):
        result = establish_product_foundations(self.plan, self.staging)
        overview = self.staging / "product" / "docs" / "overview" / "test-product-WHITEBOARD.md"
        self.assertTrue(overview.exists())
        content = overview.read_text()
        self.assertIn("Overview Whiteboard", content)
        created_paths = [c["path"] for c in result.created]
        self.assertIn("product/docs/overview/test-product-WHITEBOARD.md", created_paths)


    # validation-metadata: {"role": "helper"}
    def test_creates_overview_chunks(self):
        establish_product_foundations(self.plan, self.staging)
        for filename, title, _ in OVERVIEW_CHUNK_COVERAGE:
            chunk_path = self.staging / "product" / "docs" / "overview" / "test-product-whiteboard" / filename
            self.assertTrue(chunk_path.exists(), f"missing chunk: {filename}")
            self.assertIn(title, chunk_path.read_text())

    # validation-metadata: {"role": "helper"}
    def test_defers_decomposition_controlling(self):
        result = establish_product_foundations(self.plan, self.staging)
        decomp = self.staging / "product" / "docs" / "decompositions" / "test-product-DECOMPOSITION.md"
        self.assertFalse(decomp.exists())
        deferred_paths = [c["path"] for c in result.deferred]
        self.assertIn("product/docs/decompositions/test-product-DECOMPOSITION.md", deferred_paths)

    # validation-metadata: {"role": "helper"}
    def test_does_not_create_decomposition_chunks(self):
        establish_product_foundations(self.plan, self.staging)
        chunk_dir = self.staging / "product" / "docs" / "decompositions" / "test-product-decomposition"
        self.assertFalse(chunk_dir.exists())

    # validation-metadata: {"role": "helper"}
    def test_defers_plan_controlling(self):
        result = establish_product_foundations(self.plan, self.staging)
        plan_path = self.staging / "product" / "docs" / "plans" / "test-product-IMPLEMENTATION-PLAN.md"
        self.assertFalse(plan_path.exists())
        deferred_paths = [c["path"] for c in result.deferred]
        self.assertIn("product/docs/plans/test-product-IMPLEMENTATION-PLAN.md", deferred_paths)

    # validation-metadata: {"role": "helper"}
    def test_does_not_create_plan_chunks(self):
        establish_product_foundations(self.plan, self.staging)
        chunk_dir = self.staging / "product" / "docs" / "plans" / "test-product-implementation-plan"
        self.assertFalse(chunk_dir.exists())

    # validation-metadata: {"role": "helper"}
    def test_creates_product_manifest(self):
        result = establish_product_foundations(self.plan, self.staging)
        manifest_path = self.staging / "product" / "specs" / "product" / "manifest.json"
        self.assertTrue(manifest_path.exists())
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["spec_id"], "product.manifest")
        created_paths = [c["path"] for c in result.created]
        self.assertIn("product/specs/product/manifest.json", created_paths)

    # validation-metadata: {"role": "helper"}
    def test_creates_level_roots(self):
        result = establish_product_foundations(self.plan, self.staging)
        for level in ["level-0", "level-1", "level-2", "level-3"]:
            path = self.staging / "product" / "specs" / "product" / level
            self.assertTrue(path.is_dir(), f"missing level root: {level}")


    # validation-metadata: {"role": "helper"}
    def test_creates_readme_discoverability(self):
        establish_product_foundations(self.plan, self.staging)
        overview_readme = self.staging / "product" / "docs" / "overview" / "README.md"
        self.assertTrue(overview_readme.exists())
        content = overview_readme.read_text()
        self.assertIn("test-product-WHITEBOARD.md", content)


    # validation-metadata: {"role": "helper"}
    def test_rejects_overwrite_of_existing(self):
        existing = self.staging / "product" / "docs" / "overview" / "test-product-WHITEBOARD.md"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("existing content")
        result = establish_product_foundations(self.plan, self.staging)
        rejected_paths = [r["path"] for r in result.rejected]
        self.assertIn("product/docs/overview/test-product-WHITEBOARD.md", rejected_paths)

    # validation-metadata: {"role": "helper"}
    def test_overview_metadata_uses_candidate_lifecycle(self):
        result = establish_product_foundations(self.plan, self.staging)
        overview = self.staging / "product" / "docs" / "overview" / "test-product-WHITEBOARD.md"
        content = overview.read_text()
        import re
        meta_match = re.search(r'\{.*"artifact_type".*\}', content, re.DOTALL)
        self.assertIsNotNone(meta_match)
        meta = json.loads(meta_match.group())
        self.assertEqual(meta["lifecycle_status"], "active")

    # validation-metadata: {"role": "helper"}
    def test_direction_material_preserved_in_overview(self):
        result = establish_product_foundations(self.plan, self.staging)
        overview = self.staging / "product" / "docs" / "overview" / "test-product-WHITEBOARD.md"
        content = overview.read_text()
        self.assertIn("/path/to/direction.md", content)

    # validation-metadata: {"role": "helper"}
    def test_evidence_references_in_overview_metadata(self):
        result = establish_product_foundations(self.plan, self.staging)
        overview = self.staging / "product" / "docs" / "overview" / "test-product-WHITEBOARD.md"
        content = overview.read_text()
        import re
        meta_match = re.search(r'\{.*"artifact_type".*\}', content, re.DOTALL)
        self.assertIsNotNone(meta_match)
        meta = json.loads(meta_match.group())
        self.assertIn("/path/to/direction.md", meta["evidence"])

    # validation-metadata: {"role": "helper"}
    def test_governing_issue_in_overview_metadata(self):
        result = establish_product_foundations(self.plan, self.staging)
        overview = self.staging / "product" / "docs" / "overview" / "test-product-WHITEBOARD.md"
        content = overview.read_text()
        import re
        meta_match = re.search(r'\{.*"artifact_type".*\}', content, re.DOTALL)
        self.assertIsNotNone(meta_match)
        meta = json.loads(meta_match.group())
        self.assertEqual(meta["governing_issue"], "#195")


    # validation-metadata: {"role": "helper"}
    def test_chunks_have_placeholder_content(self):
        establish_product_foundations(self.plan, self.staging)
        chunk = self.staging / "product" / "docs" / "overview" / "test-product-whiteboard" / "01-collected-input.md"
        content = chunk.read_text()
        self.assertIn("evidentiary scaffolding", content)
        self.assertIn("/path/to/direction.md", content)


    # validation-metadata: {"role": "helper"}
    def test_overview_controlling_references_chunks(self):
        establish_product_foundations(self.plan, self.staging)
        overview = self.staging / "product" / "docs" / "overview" / "test-product-WHITEBOARD.md"
        content = overview.read_text()
        self.assertIn("01-collected-input.md", content)
        self.assertIn("02-provenance.md", content)
        self.assertIn("03-unresolved-intent.md", content)


    # validation-metadata: {"role": "helper"}
    def test_decomposition_controlling_references_overview(self):
        result = establish_product_foundations(self.plan, self.staging)
        decomp = self.staging / "product" / "docs" / "decompositions" / "test-product-DECOMPOSITION.md"
        self.assertFalse(decomp.exists())
        deferred = {item["path"]: item["reason"] for item in result.deferred}
        self.assertEqual(
            deferred["product/docs/decompositions/test-product-DECOMPOSITION.md"],
            "requires an approved functional set",
        )


    # validation-metadata: {"role": "helper"}
    def test_plan_controlling_references_overview_and_decomposition(self):
        result = establish_product_foundations(self.plan, self.staging)
        plan_path = self.staging / "product" / "docs" / "plans" / "test-product-IMPLEMENTATION-PLAN.md"
        self.assertFalse(plan_path.exists())
        deferred = {item["path"]: item["reason"] for item in result.deferred}
        self.assertEqual(
            deferred["product/docs/plans/test-product-IMPLEMENTATION-PLAN.md"],
            "requires decomposition",
        )

    # validation-metadata: {"role": "helper"}
    def test_preserves_existing_files(self):
        existing_readme = self.staging / "product" / "docs" / "overview" / "README.md"
        existing_readme.parent.mkdir(parents=True, exist_ok=True)
        existing_readme.write_text("existing readme")
        result = establish_product_foundations(self.plan, self.staging)
        content = existing_readme.read_text()
        self.assertEqual(content, "existing readme")
        created_paths = [c["path"] for c in result.created]
        self.assertNotIn("repo/docs/overview/README.md", created_paths)

    # validation-metadata: {"role": "helper"}
    def test_specs_product_not_under_specs_repo(self):
        result = establish_product_foundations(self.plan, self.staging)
        self.assertFalse((self.staging / "repo" / "specs" / "repo" / "manifest.json").exists())
        self.assertTrue((self.staging / "product" / "specs" / "product" / "manifest.json").exists())

    # validation-metadata: {"role": "helper"}
    def test_level_roots_created(self):
        result = establish_product_foundations(self.plan, self.staging)
        for level in ["level-0", "level-1", "level-2", "level-3"]:
            path = self.staging / "product" / "specs" / "product" / level
            self.assertTrue(path.is_dir())


    # validation-metadata: {"role": "helper"}
    def test_created_artifact_count(self):
        result = establish_product_foundations(self.plan, self.staging)
        self.assertEqual(len(result.created), 11)
        self.assertEqual(len(result.deferred), 4)

class FoundationDeterminismTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.plan = FoundationPlan("test-product", ["/path/to/direction.md"], "#195")

    # validation-metadata: {"role": "helper"}
    def test_equivalent_inputs_equivalent_output(self):
        s1 = Path(tempfile.mkdtemp())
        s2 = Path(tempfile.mkdtemp())
        try:
            r1 = establish_product_foundations(self.plan, s1)
            r2 = establish_product_foundations(self.plan, s2)
            self.assertEqual(r1, r2)
        finally:
            shutil.rmtree(s1, ignore_errors=True)
            shutil.rmtree(s2, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_equivalent_file_contents(self):
        s1 = Path(tempfile.mkdtemp())
        s2 = Path(tempfile.mkdtemp())
        try:
            r1 = establish_product_foundations(self.plan, s1)
            r2 = establish_product_foundations(self.plan, s2)
            for c1, c2 in zip(r1.created, r2.created):
                p1 = s1 / c1["path"]
                p2 = s2 / c2["path"]
                if c1["artifact"].endswith("-chunk") or c1["artifact"].endswith("-controlling") or c1["artifact"] == "product-manifest":
                    self.assertEqual(
                        p1.read_text(),
                        p2.read_text(),
                        f"content mismatch for {c1['path']}",
                    )
        finally:
            shutil.rmtree(s1, ignore_errors=True)
            shutil.rmtree(s2, ignore_errors=True)


class FoundationOverwriteTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.staging = Path(tempfile.mkdtemp())
        self.plan = FoundationPlan("test-product", ["/path/to/direction.md"], "#195")

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.staging, ignore_errors=True)


    # validation-metadata: {"role": "helper"}
    def test_overview_controlling_rejected_if_exists(self):
        existing = self.staging / "product" / "docs" / "overview" / "test-product-WHITEBOARD.md"
        existing.parent.mkdir(parents=True, exist_ok=True)
        existing.write_text("existing")
        result = establish_product_foundations(self.plan, self.staging)
        rejected = [item["path"] for item in result.rejected]
        self.assertIn("product/docs/overview/test-product-WHITEBOARD.md", rejected)

    # validation-metadata: {"role": "helper"}
    def test_manifest_rejected_if_exists(self):
        manifest = self.staging / "product" / "specs" / "product" / "manifest.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text("{}")
        result = establish_product_foundations(self.plan, self.staging)
        rejected = [r["path"] for r in result.rejected]
        self.assertIn("product/specs/product/manifest.json", rejected)

    # validation-metadata: {"role": "helper"}
    def test_level_roots_preserved_if_exist(self):
        level0 = self.staging / "product" / "specs" / "product" / "level-0"
        level0.mkdir(parents=True, exist_ok=True)
        (level0 / "existing.txt").write_text("data")
        result = establish_product_foundations(self.plan, self.staging)
        preserved = [p["path"] for p in result.preserved]
        self.assertIn("product/specs/product/level-0/", preserved)


class FoundationSlugTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_slug_from_product_id(self):
        cases = [
            ("my-product", "my-product"),
            ("My Product", "my-product"),
            ("Hello   World", "hello-world"),
            ("a_b_c", "a-b-c"),
            ("  leading trailing  ", "leading-trailing"),
            ("special!@#chars", "special-chars"),
        ]
        for pid, expected in cases:
            plan = FoundationPlan(pid, ["/doc.md"], "#195")
            self.assertEqual(plan.product_slug, expected, f"failed for {pid!r}")


if __name__ == "__main__":
    unittest.main()
