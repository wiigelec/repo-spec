from __future__ import annotations

import sys
import unittest
from pathlib import Path


def run_initializer_tests(repo_root: Path) -> None:
    from initializer.tests.test_models import ImmutableRequestTests
    from initializer.tests.test_validation import ValidationTests, DeterminismTests, SafetyTests
    from initializer.tests.test_inventory import (
        InventoryValidationTests,
        InventoryLoadTests,
        InventoryDeterminismTests,
        SourceSelectionTests,
        InventoryOutputTests,
        InventoryEntryTests,
        SafetyTests as InventoryFinalSafetyTests,
    )
    from initializer.tests.test_cli import CliTests

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in [
        ImmutableRequestTests,
        ValidationTests,
        DeterminismTests,
        SafetyTests,
        InventoryValidationTests,
        InventoryLoadTests,
        InventoryDeterminismTests,
        SourceSelectionTests,
        InventoryOutputTests,
        InventoryEntryTests,
        InventoryFinalSafetyTests,
        CliTests,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise AssertionError("initializer tests failed")
    print("ok: initializer tests")
