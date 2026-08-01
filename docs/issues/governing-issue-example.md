# Governing Issue Example

## Canonical fields

### Change type

- Field ID: `change_type`
- Required: yes
- Input type: `textarea`

What kind of bounded governed change is this?

Placeholder:
> Standardization, feature, maintenance, documentation, migration, or other bounded change.

### Problem statement

- Field ID: `problem_statement`
- Required: yes
- Input type: `textarea`

What problem or gap does this issue address?

Placeholder:
> Explain the need in repository terms.

### Intended outcome

- Field ID: `intended_outcome`
- Required: yes
- Input type: `textarea`

What outcome should be true when the work is complete?

Placeholder:
> State the expected end state.

### Governing specifications

- Field ID: `governing_specifications`
- Required: yes
- Input type: `textarea`

List the authoritative specifications and relevant records.

Placeholder:
> repo.manifest, repo.development-workflow, and any other governing specs.

### Accepted default-branch base

- Field ID: `accepted_default_branch_base`
- Required: yes
- Input type: `input`

Exact accepted default-branch revision or reference.

Placeholder:
> main at <commit>

### In-scope behavior and paths

- Field ID: `in_scope_behavior_and_paths`
- Required: yes
- Input type: `textarea`

What behavior and repository paths are explicitly in scope?

Placeholder:
> List files, directories, and behavior to change.

### Explicit exclusions

- Field ID: `explicit_exclusions`
- Required: yes
- Input type: `textarea`

What is explicitly out of scope?

Placeholder:
> List excluded behaviors, files, or follow-up work.

### Dependencies and predecessor evidence

- Field ID: `dependencies_and_predecessor_evidence`
- Required: yes
- Input type: `textarea`

What must exist first, and what evidence supports this work?

Placeholder:
> Prior issues, commits, specs, validation evidence, or other predecessors.

### Ordered patch plan

- Field ID: `ordered_patch_plan`
- Required: yes
- Input type: `textarea`

State the implementation steps in order.

Placeholder:
> 1. ... 2. ... 3. ...

### Validation plan

- Field ID: `validation_plan`
- Required: yes
- Input type: `textarea`

How will the change be validated?

Placeholder:
> scripts/validate, focused checks, evidence capture.

### Acceptance criteria

- Field ID: `acceptance_criteria`
- Required: yes
- Input type: `textarea`

What must be true for this issue to be accepted?

Placeholder:
> List concrete acceptance checks.

### Completion gate

- Field ID: `completion_gate`
- Required: yes
- Input type: `textarea`

What must be satisfied before this issue can close?

Placeholder:
> State the closure condition.

### Open decisions or authority conflicts

- Field ID: `open_decisions_or_authority_conflicts`
- Required: yes
- Input type: `textarea`

Record any unresolved authority questions or conflicts.

Placeholder:
> None, or list conflicts explicitly.

### Successor work explicitly not authorized

- Field ID: `successor_work_not_authorized`
- Required: yes
- Input type: `textarea`

What follow-on work does this issue not authorize?

Placeholder:
> List unrelated or deferred successor work.

### Optional context

- Field ID: `optional_context`
- Required: no
- Input type: `textarea`

Optional notes that help with session recovery or review.

Placeholder:
> Related links, assumptions, risks, or recovery notes.
