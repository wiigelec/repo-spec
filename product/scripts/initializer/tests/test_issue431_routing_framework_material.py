from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
REQUIRED_PATHS = ['repo/specs/repo/issue-routing-governance.json', 'repo/derived/specs/repo/issue-routing-governance.md', 'repo/specs/repo/issue-routing-classification.json', 'repo/derived/specs/repo/issue-routing-classification.md', 'repo/specs/repo/governed-work-provenance.json', 'repo/derived/specs/repo/governed-work-provenance.md', 'repo/specs/repo/issue-authority-routing.json', 'repo/derived/specs/repo/issue-authority-routing.md', 'repo/specs/repo/governed-work-promotion.json', 'repo/derived/specs/repo/governed-work-promotion.md', 'repo/specs/repo/issue-routing-platform-validation.json', 'repo/derived/specs/repo/issue-routing-platform-validation.md', 'repo/specs/repo/issue-intake-governance-routing.json', 'repo/derived/specs/repo/issue-intake-governance-routing.md', 'repo/scripts/github_issue_promotion.py', 'repo/scripts/canonical-governed-state-validator', 'repo/scripts/repository-governance-authorization-validator', 'repo/scripts/issue_intake_governance_routing/__init__.py', 'repo/scripts/issue_intake_governance_routing/authority.py', 'repo/scripts/issue_intake_governance_routing/classification.py', 'repo/scripts/issue_intake_governance_routing/hosted_validation.py', 'repo/scripts/issue_intake_governance_routing/orchestration.py', 'repo/scripts/issue_intake_governance_routing/promotion.py', 'repo/scripts/issue_intake_governance_routing/provenance.py', 'repo/profiles/github/ISSUE_TEMPLATE/governing-issue.yml', '.github/ISSUE_TEMPLATE/governing-issue.yml', 'repo/profiles/github/PULL_REQUEST_TEMPLATE.md', '.github/PULL_REQUEST_TEMPLATE.md', 'repo/profiles/github/workflows/github-field-policy.yml', '.github/workflows/github-field-policy.yml', 'repo/profiles/github/workflows/governed-work-promotion.yml', '.github/workflows/governed-work-promotion.yml', 'repo/profiles/github/workflows/validation.yml', '.github/workflows/validation.yml', 'repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md', 'repo/docs/decompositions/repository-decomposition/01-intake-classification.md', 'repo/docs/decompositions/repository-decomposition/02-authority-routing.md', 'repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md', 'repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md', 'repo/docs/overview/REPOSITORY-ANALYSIS.md', 'repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md', 'repo/docs/overview/REPOSITORY-WHITEBOARD.md', 'repo/docs/overview/repository-analysis/01-migration-analysis.md', 'repo/docs/overview/repository-analysis/02-issue-routing-analysis.md', 'repo/docs/overview/repository-functional-set/01-product-direction.md', 'repo/docs/overview/repository-functional-set/02-decomposition-model-part-1.md', 'repo/docs/overview/repository-functional-set/03-decomposition-model-part-2.md', 'repo/docs/overview/repository-functional-set/04-development-and-specifications-part-1.md', 'repo/docs/overview/repository-functional-set/05-development-and-specifications-part-2.md', 'repo/docs/overview/repository-functional-set/06-development-and-specifications-part-3.md', 'repo/docs/overview/repository-functional-set/07-git-and-change-workflow.md', 'repo/docs/overview/repository-functional-set/08-human-ai-continuity.md', 'repo/docs/overview/repository-functional-set/09-governance-and-evolution.md', 'repo/docs/overview/repository-functional-set/10-issue-intake-and-governance-routing.md', 'repo/docs/overview/repository-whiteboard/01-migration-input.md', 'repo/docs/overview/repository-whiteboard/02-issue-routing-intake.md']


class Issue431RoutingFrameworkMaterialTests(unittest.TestCase):
    def test_routing_framework_material_is_closed_over_initializer_output(self):
        output_spec = json.loads((ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json").read_text())
        framework = json.loads((ROOT / "product/scripts/initializer/framework-inventory.json").read_text())
        destinations = {item["destination_path"] for item in output_spec["material_index"]}
        sources = {item["source_path"] for item in framework["entries"]}
        self.assertTrue(set(REQUIRED_PATHS) <= destinations)
        self.assertTrue(set(REQUIRED_PATHS) <= sources)

    def test_routing_runtime_sources_are_repository_owned(self):
        framework = json.loads((ROOT / "product/scripts/initializer/framework-inventory.json").read_text())
        routing_sources = [
            item["source_path"] for item in framework["entries"]
            if item["material_key"].startswith("repo-routing-")
        ]
        self.assertTrue(routing_sources)
        for path in routing_sources:
            self.assertFalse(path.startswith("product/scripts/issue_intake_governance_routing"), path)


if __name__ == "__main__":
    unittest.main()
