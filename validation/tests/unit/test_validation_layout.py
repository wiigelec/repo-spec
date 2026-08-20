from __future__ import annotations
import tempfile, unittest
from pathlib import Path
from validation.checks.policy import RootValidationError, _check_exact_validation_layout

CHECKS={"development_documents.py","domain.py","generated_outputs.py","policy.py","specifications.py"}
CORE={"context.py","errors.py","invariants.py","paths.py","schema_subset.py"}
RUNNERS={"validate_impl.py","test_validation_impl.py"}

def build(root: Path, github: bool):
    root.mkdir()
    (root/"README.md").write_text("")
    (root/"manifest.json").write_text("{}")
    for name,files in (("checks",CHECKS),("core",CORE),("runners",RUNNERS)):
        d=root/name; d.mkdir()
        for f in files: (d/f).write_text("")
    for d in ("unit","self","fixtures"): (root/"tests"/d).mkdir(parents=True,exist_ok=True)
    if github: (root/"github").mkdir()
    return root

class LayoutTests(unittest.TestCase):
    def test_test_contents_unconstrained(self):
        with tempfile.TemporaryDirectory() as td:
            d=build(Path(td)/"v",True)
            (d/"tests/unit/anything.py").write_text("x")
            (d/"tests/fixtures/nested").mkdir()
            _check_exact_validation_layout(d,require_github=True,label="root")
    def test_missing_github_fails_when_required(self):
        with tempfile.TemporaryDirectory() as td:
            d=build(Path(td)/"v",True); (d/"github").rmdir()
            with self.assertRaises(RootValidationError): _check_exact_validation_layout(d,require_github=True,label="root")
    def test_product_does_not_require_github(self):
        with tempfile.TemporaryDirectory() as td:
            d=build(Path(td)/"v",False)
            _check_exact_validation_layout(d,require_github=False,label="product")
    def test_extra_fixed_file_fails(self):
        with tempfile.TemporaryDirectory() as td:
            d=build(Path(td)/"v",True); (d/"checks/extra.py").write_text("")
            with self.assertRaises(RootValidationError): _check_exact_validation_layout(d,require_github=True,label="root")
    def test_extra_test_subdir_fails(self):
        with tempfile.TemporaryDirectory() as td:
            d=build(Path(td)/"v",True); (d/"tests/integration").mkdir()
            with self.assertRaises(RootValidationError): _check_exact_validation_layout(d,require_github=True,label="root")
