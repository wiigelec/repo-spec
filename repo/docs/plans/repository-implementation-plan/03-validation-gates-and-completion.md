# Validation, gates, and completion

## Status

Candidate implementation-plan content.

## Validation strategy

Each implementation issue created after plan acceptance must:
- cite one or more stable IRP workstream IDs;
- cite the exact accepted repository specification set declared for those workstreams;
- start from an exact accepted default-branch base;
- define focused validation for its bounded mutation;
- run repository-wide `scripts/validate`;
- preserve source/generated platform-profile authority boundaries where applicable;
- record predecessor evidence for dependent workstreams.

## Workstream transition gates

### IRP-I1 -> IRP-I2
Classification is machine-observable, distinct from governance state, and ambiguous authority directions fail closed.

### IRP-I2 -> IRP-I3
Authority-routing outcomes are explicit, traceable, and cannot directly create mutation authority.

### IRP-I3 -> IRP-I4
Required body/classification provenance is preserved before destructive restructuring and canonical governed state can be established safely.

### IRP-I4 -> IRP-I5
Hosted validation is inactive for ordinary intake and reliably active for canonical governed-work state without invalid intermediate exposure.

### IRP-I5 completion
End-to-end conformance demonstrates successful and unsuccessful routing outcomes against the accepted Level 3 orchestration plus all lower-level contracts.

## Validation classes

Planned implementation validation should include:
- repository-local validation;
- focused unit/regression tests for routing/provenance/state mechanics;
- hosted/profile source-to-installed-adapter freshness checks;
- field-policy event scenarios;
- end-to-end issue lifecycle scenarios;
- negative tests for fail-closed conditions.

## Completion conditions

The implementation plan is execution-complete only when:
- every accepted implementation-authorized workstream has satisfied exit conditions;
- required predecessor relationships were honored;
- conformance evidence is truthful and current;
- product correspondence records are updated only when implementation/test/conformance evidence actually exists;
- repository validation passes at the final proposed revision.

Execution completion does not itself imply merge, release, or plan retirement.

## Successor implementation issue shape

After plan acceptance, each implementation issue must identify:
- exact workstream/stage ID(s);
- exact controlling accepted repository specifications;
- accepted default-branch base;
- predecessor implementation evidence;
- bounded artifact paths/behavior;
- ordered patch plan;
- focused and aggregate validation;
- completion gate.

Implementation issues must not broaden their workstream specification authority.
