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
    from initializer.tests.test_foundations import (
        FoundationPlanTests,
        FoundationResultTests,
        BuildFoundationPlanTests,
        EstablishFoundationsTests,
        FoundationDeterminismTests,
        FoundationOverwriteTests,
        FoundationSlugTests,
    )
    from initializer.tests.test_staging import (
        InstallationPlanTests,
        InstallationResultTests,
        BuildInstallationPlanTests,
        ValidateSourcePathTests,
        ResolveEntryTypeTests,
        SymlinkSafetyTests,
        DestinationConflictTests,
        StagingWorkspaceTests,
        CopyEntryTests,
        StageFrameworkTests,
        StagingDeterminismTests,
        PreexistingWorkspaceTests,
    )
    from initializer.tests.test_destination_promotion import (
        DestinationPreflightModelTests,
        PromotionPlanModelTests,
        PromotionResultModelTests,
        PathSafetyTests,
        ClassifyDestinationTests,
        SameFilesystemTests,
        DestinationPreflightFunctionTests,
        BuildPromotionPlanTests,
        ValidateStagingResultTests,
        PrepareDestinationTests,
        RestoreDestinationTests,
        PromoteFunctionTests,
        PromoteWithValidationTests,
        NoGitNoPlatformTests,
    )
    from initializer.tests.test_git import (
        GitPreflightModelTests,
        GitCommandResultTests,
        GitEstablishmentPlanTests,
        GitEstablishmentResultTests,
        GitPreflightFunctionTests,
        GitEstablishmentFunctionTests,
        GitCleanupTests,
        GitDeterminismTests,
        GitInitializePromotedDestinationTests,
        GitEnvironmentIsolationTests,
        GitVersionParsingTests,
        GitCheckAvailableTests,
        GitTreeInventoryTests,
        GitCLIIntegrationTests,
        GitNoGitNoPlatformTests,
    )

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
        FoundationPlanTests,
        FoundationResultTests,
        BuildFoundationPlanTests,
        EstablishFoundationsTests,
        FoundationDeterminismTests,
        FoundationOverwriteTests,
        FoundationSlugTests,
        InstallationPlanTests,
        InstallationResultTests,
        BuildInstallationPlanTests,
        ValidateSourcePathTests,
        ResolveEntryTypeTests,
        SymlinkSafetyTests,
        DestinationConflictTests,
        StagingWorkspaceTests,
        CopyEntryTests,
        StageFrameworkTests,
        StagingDeterminismTests,
        PreexistingWorkspaceTests,
        DestinationPreflightModelTests,
        PromotionPlanModelTests,
        PromotionResultModelTests,
        PathSafetyTests,
        ClassifyDestinationTests,
        SameFilesystemTests,
        DestinationPreflightFunctionTests,
        BuildPromotionPlanTests,
        ValidateStagingResultTests,
        PrepareDestinationTests,
        RestoreDestinationTests,
        PromoteFunctionTests,
        PromoteWithValidationTests,
        NoGitNoPlatformTests,
        GitPreflightModelTests,
        GitCommandResultTests,
        GitEstablishmentPlanTests,
        GitEstablishmentResultTests,
        GitPreflightFunctionTests,
        GitEstablishmentFunctionTests,
        GitCleanupTests,
        GitDeterminismTests,
        GitInitializePromotedDestinationTests,
        GitEnvironmentIsolationTests,
        GitVersionParsingTests,
        GitCheckAvailableTests,
        GitTreeInventoryTests,
        GitCLIIntegrationTests,
        GitNoGitNoPlatformTests,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise AssertionError("initializer tests failed")
    print("ok: initializer tests")
