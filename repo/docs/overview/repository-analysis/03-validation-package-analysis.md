# Validation-package analysis
## Source evidence
This analysis consumes `repo/docs/overview/repository-whiteboard/03-validation-package-feature-request.md`, issue #550 as preserved provenance, current accepted repository authority, and repository-analysis chunks 01–02.
The request seeks bidirectional correspondence between active normative requirements and maintained validation evidence. Requirement identity, package semantics, task taxonomy, tagging syntax, package location, and migration mechanics remain unresolved.
This analysis identifies candidate boundaries and dependencies only; it does not establish accepted direction.
## Candidate capability grouping
The evidence supports one primary candidate capability:
**Normative Requirement Validation Correspondence**
The candidate covers the durable relationship among an active normative requirement, one validation-correspondence package, its validation disposition, externally identified validation tasks, machine-readable entry-point correspondence, integrity checks, and deterministic subordinate coverage/documentation projections.
It is narrower than validation itself and does not redefine normative semantics, execution, orchestration, or repository workflow.
## Accepted-authority constraints
Any later design is constrained by accepted authority:
- normative requirement identifiers are stable and withdrawn identifiers remain reserved;
- validation is subordinate to accepted authority and cannot manufacture semantics;
- repository structure is closed/default-deny;
- generated artifacts are subordinate to source authority;
- governed workflow requires bounded authorization;
- inseparable authority/artifact changes may require an atomic transition.
Package files, schemas, tags, or validators therefore cannot legitimately create missing correspondence semantics.
## Requirement identity
The audit established identifier stability/reservation but not repository-global uniqueness of a bare `normative_requirement_id`.
Two candidate models remain viable:
1. later authority establishes repository-global bare-ID uniqueness; or
2. correspondence uses a composite normative reference such as specification identity plus requirement identifier.
Analysis recommendation: define correspondence against an abstract canonical normative-requirement reference and avoid assuming bare global uniqueness. A composite normative reference is the safer default unless later authority establishes global uniqueness independently.
This recommendation is not accepted identity policy.
## Validation-package artifact boundary
A package is distinct from the normative specification, executable validation code, generated coverage output, and validation orchestration.
Its candidate role is a durable source correspondence artifact recording normative identity, disposition, and externally identified validation tasks without restating normative semantics.
The illustrated `validation/packages/...` path is not currently structurally authorized.
Analysis recommendation: keep package sources separate from deterministic derived coverage/documentation. Exact artifact type, schema owner, and path remain downstream decisions.
## Cardinality, lifecycle, and disposition
The requested one-package-per-active-requirement rule can be separated from mechanical task count:
- each in-scope active identified requirement has one active package;
- a package may have zero or more executable tasks;
- withdrawn requirements do not retain active package ownership;
- retired correspondence may be preserved without remaining active.
This permits `semantic-review` or `not-applicable` packages without inventing mechanical validators.
The proposed dispositions `mechanical`, `partial`, `semantic-review`, and `not-applicable` are coherent candidate metadata, but exact definitions, exhaustiveness, rationale rules, and transitions remain unresolved.
Analysis recommendation: require rationale whenever full mechanical validation is absent, subject to later functional-set/specification decisions.
## Validation-task classification
The proposed `positive`, `negative`, `boundary`, `regression`, `unit`, and `integration` values mix dimensions.
The first four mostly describe purpose/coverage; `unit` and `integration` describe execution scope.
Analysis recommendation: use separate dimensions rather than one peer taxonomy, for example:
- coverage/purpose: positive, negative, boundary, regression, potentially multi-valued;
- execution level: unit or integration, normally one primary value.
Exact dimensions, vocabulary, and cardinalities remain unresolved.
## Externally identified task identity
Stable identity is needed for tasks represented in packages and aggregate coverage, but not necessarily for every helper.
Candidate boundary:
- externally identified validation tasks have stable identity;
- each belongs through exactly one package to one canonical normative reference;
- each resolves to a maintained source location and execution entry point;
- shared helpers may support multiple tasks without becoming independent correspondence entries;
- entry-point metadata agrees with package ownership and does not become a second registry.
Analysis recommendation: define the invariant at the externally identified task boundary and leave exact tagging syntax downstream.
## Correspondence integrity
Candidate integrity concerns include:
- each in-scope active requirement resolves to exactly one active package;
- each active package resolves to a known active requirement;
- package ownership agrees with the normative owner;
- externally identified task IDs are unique in their accepted scope;
- referenced source/entry points resolve;
- each externally identified task appears in exactly one package;
- entry-point metadata agrees with package ownership;
- derived projections reproduce canonical source deterministically;
- stale or divergent projections are rejected.
These are candidate invariants, not accepted requirements.
## Ownership and migration
Namespace selection should follow authority ownership, not convenience. Structure must explicitly authorize durable package sources, and whole-checkout aggregation should consume canonical sources rather than duplicate mappings.
Whether one physical root can represent repository, product, and whole-checkout packages remains unresolved.
The proposed end state may combine a new completeness invariant with artifacts the current structural envelope forbids.
Analysis recommendation: if approved direction simultaneously adds a new source namespace and repository-wide package completeness, use the accepted atomic-transition workflow to introduce authority and an initially complete package population together.
If staged inactive packages or an already-authorized representation are adopted, atomicity may not be required.
## Candidate boundary
### Candidate: Normative Requirement Validation Correspondence
Included direction for a later candidate functional set:
- establish an unambiguous canonical normative-requirement reference;
- establish one durable active package per in-scope active identified requirement;
- keep package semantics subordinate to normative authority and prohibit semantic restatement;
- record disposition independently from task count;
- identify externally maintained validation tasks with stable identity and resolvable entry points;
- require each externally identified task to correspond through exactly one package to exactly one normative reference;
- require entry-point metadata to agree with package ownership;
- separate task purpose/coverage metadata from execution-level metadata;
- define package lifecycle for active and withdrawn requirements;
- derive coverage/documentation deterministically from canonical correspondence sources;
- enforce correspondence integrity without a second registry;
- govern migration so no invalid intermediate state is required.
Excluded:
- changing normative requirement semantics;
- deciding bare repository-global identifier uniqueness unless separately required;
- exact schema fields, artifact identifiers, paths, or tagging syntax;
- detailed test implementation or migration;
- validation orchestration already governed elsewhere;
- exact generated layouts or CI YAML;
- implementation planning.
## Dependencies and ambiguities
A later candidate functional set depends on normative requirement identity, artifact taxonomy/structure, validation authority, development workflow, generated-artifact governance, and inventory of existing validation behavior.
The following remain unresolved:
- bare global IDs versus composite normative references and owning authority;
- package artifact class, schema owner, source namespace, and completeness scope;
- exact disposition vocabulary and rationale requirements;
- task metadata dimensions, cardinalities, and externally identified-task definition;
- machine-readable entry-point tagging mechanism;
- retired/withdrawn package history;
- mapping shared helpers and parameterized tests;
- physical namespace strategy across repository/product/whole-checkout ownership;
- derived projection locations/formats;
- validators/tests lacking clear normative owners;
- validation behavior pointing at withdrawn requirements;
- whether final migration requires an atomic transition.
## Candidate functional-set conclusion
The collected evidence supports one coherent primary candidate capability: **Normative Requirement Validation Correspondence**.
It is distinct from validation execution because it governs correspondence between normative requirements and validation evidence while accepted validation authority continues to own execution/enforcement mechanics.
The analysis recommends carrying this boundary into a separate candidate functional-set operation, which may revise, split, or reject it before explicit approval.
This analysis does **not** create or approve a functional set and does not authorize decomposition, specification, schema, structure, planning, or implementation work.
