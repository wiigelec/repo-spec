from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

ROUTING_LABELS = frozenset({"bug-fix", "feature-request"})


@dataclass(frozen=True)
class IntakeProvenance:
    intake_issue: str
    governed_operation: str
    original_body: str
    routing_labels: tuple[str, ...]
    captured_before_restructure: bool = True

    def to_comment(self) -> str:
        labels = ", ".join(f"`{label}`" for label in self.routing_labels) or "(none)"
        return (
            "## Intake provenance\n\n"
            f"- Intake issue: {self.intake_issue}\n"
            f"- Governed operation: {self.governed_operation}\n"
            f"- Routing classification labels before promotion: {labels}\n"
            "- Captured before body replacement/restructuring: yes\n\n"
            "### Original unformatted issue body\n\n"
            f"{self.original_body}"
        )


def capture_intake_provenance(
    *,
    intake_issue: str,
    governed_operation: str,
    original_body: str,
    labels: Iterable[str],
) -> IntakeProvenance:
    intake = intake_issue.strip()
    operation = governed_operation.strip()
    if not intake:
        raise ValueError("intake_issue is required")
    if not operation:
        raise ValueError("governed_operation is required")

    routing_labels = tuple(
        sorted(
            {
                str(label).strip()
                for label in labels
                if str(label).strip() in ROUTING_LABELS
            }
        )
    )
    return IntakeProvenance(
        intake_issue=intake,
        governed_operation=operation,
        original_body=original_body,
        routing_labels=routing_labels,
        captured_before_restructure=True,
    )
