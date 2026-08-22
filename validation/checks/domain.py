"""Aggregate production validation for the root/whole-checkout domain."""
from __future__ import annotations
from pathlib import Path
from . import development_documents, generated_outputs, policy, specifications

# validation-metadata: {"role": "helper"}
def validate_root(repo_root: Path) -> bool:
    specifications.validate(repo_root)
    development_documents.validate(repo_root)
    generated_outputs.validate(repo_root)
    return policy.validate(repo_root)
