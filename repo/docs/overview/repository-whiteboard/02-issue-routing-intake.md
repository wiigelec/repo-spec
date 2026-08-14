# Issue-routing intake

## Provenance

This collection chunk records repository/process-direction observations from the discussion governed by issue #388.

The material is evidentiary and non-normative. It is input to later repository overview analysis and does not itself authorize workflow, specification, CI, label, or implementation changes.

## Ordinary issue intake

Repository issue intake may begin as an ordinary unformatted GitHub issue.

An intake issue does not need to satisfy the canonical governed-work body structure before it has been reviewed and routed.

## Routing classifications

`bug-fix` and `feature-request` are intended as labels that classify and route issue intake.

They may be applied when an issue is created or later after review rather than requiring separate formatted issue types.

## Bug-fix routing

An issue classified as `bug-fix` should enter the audit process before direct repository mutation.

The audit should compare the reported defect against controlling authority and determine whether a bounded corrective mutation is authorized.

A `bug-fix` classification should not itself bypass audit authority or directly authorize mutation.

## Feature-request routing

An issue classified as `feature-request` represents new or changed product or repository direction rather than a presumed defect in already accepted behavior.

Feature-request material should route into the governed whiteboard collection and functional-set process instead of directly authorizing implementation.

The whiteboard should preserve the feature-request intent as non-normative evidence before overview analysis determines candidate functional-set treatment.

## Governed-work promotion

`governed-work` is intended to represent governance state rather than the original intake classification.

When work reaches the point at which a bounded governed operation is authorized, the issue may be promoted to the canonical governed-work structure appropriate to that operation.

The intake classification and governed-work state therefore serve different purposes.

## Intake preservation

Before an intake issue body is replaced by a canonical governed-work body, the original intake should be preserved in the issue conversation.

The preserved evidence should include the original issue title, original issue body, and the applicable `bug-fix` or `feature-request` classification labels present at promotion.

The current discussion also expects the classification label to remain associated with the issue after `governed-work` is added so both routing classification and governance state remain visible.

The exact accepted label lifecycle remains subject to later analysis.

## Governed-work field validation

Unformatted intake issues should not be required to pass canonical governed-work field validation before promotion.

Once `governed-work` is applied, the issue body should use the canonical governed-work format and become subject to the repository's governed issue field policy.

The safe ordering discussed is to preserve intake evidence, construct and install the canonical body, and only then add `governed-work` so validation does not observe an intentionally unformatted intermediate state.

## Unresolved intent

The following details remain unresolved and are retained for later overview analysis:

- whether `bug-fix` and `feature-request` must be mutually exclusive;
- the exact lifecycle point at which a feature-request issue itself becomes `governed-work`;
- whether later implementation work continues on the original feature-request issue or is represented by successor governed issues;
- the precise automation and CI mechanics used to perform promotion and validation;
- the accepted creation and lifecycle rules for the proposed `bug-fix` and `feature-request` labels.
