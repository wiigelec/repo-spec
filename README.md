# repo-spec

This repository develops a small repository lifecycle for turning human intent into correct working software while keeping the process understandable and bounded.

## Lifecycle

Work progresses through:

1. **Design** — owns system meaning and intent.
2. **Planning** — selects a bounded Functional Set, resolves consequential technical intent, and derives normative requirements.
3. **Build** — realizes the reviewed Planning result and constructs required mechanical enforcement.
4. **Validation** — mechanically evaluates requirements that Planning classified as mechanically decidable.
5. **Semantic Review** — checks Design, Planning, and Build for fidelity, completeness, drift, and unnecessary complexity.
6. **Acceptance** — intentionally integrates a satisfactory development candidate into `main`.

The lifecycle describes responsibilities and control flow. It does not require every lifecycle stage to have a matching repository directory.

## Repository surfaces

- `repo/` — reusable repository/framework ownership domain.
- `repo/design/` — canonical human-readable framework Design corpus.
- `repo/planning/` — durable framework Functional Set scope and technical Planning artifacts.
- `repo/specs/` — canonical framework normative specifications.
- `repo/scripts/validate` — canonical framework-owned mechanical Validation entry point.
- `product/` — generic product-owned domain for whatever product a repository develops.
- `product/scripts/validate` — product-owned mechanical Validation entry point when the product has one.
- `scripts/` — narrow repository-root operational composition role; it owns no framework or product normative meaning.
- `scripts/validate` — repository-wide mechanical Validation entry point that composes applicable domain validators.
- `repo/validation/requirement-evaluation.json` — current framework mechanical requirement-to-Validation-task bindings.
- `user/` — user-owned operational material outside the repository framework.

Planning artifacts preserve the exact Design revision they consumed. A retained `design_revision` is an exact identifier of that consumed Design state; when framework Planning is carried into an independently rooted repository, the identifier does not imply that the originating Git object or supplier ancestry must exist locally.

Normative specifications under `repo/specs/` are the normative source for requirement text and evaluation classification. Build, parsers, manifests, root operational scripts, and Validation do not create new Design meaning or normative requirements merely through implementation behavior.

## Validation

Run repository-wide Validation with:

```bash
scripts/validate
```

The root entry point first runs framework Validation and then runs product Validation when `product/scripts/validate` exists. Domain validators remain independently owned:

```bash
repo/scripts/validate
product/scripts/validate
```

A repository without product mechanical Validation may omit the product entry point. Passing Validation does not establish semantic completeness or Acceptance. CI delegates mechanical gating to `scripts/validate` rather than independently selecting or recreating domain checks.

## Portable repository history

The reusable framework remains operational when installed into a repository with Git history independent from the framework-supplying repository.

Preserved source or Design revision identifiers retain their exact historical meaning without requiring imported supplier commits, ancestry, remotes, grafts, or replace refs merely for ordinary lifecycle use.

## Accepted state

Development branches contain candidate work. `main` represents accepted repository state.

A candidate is eligible for Acceptance only after required mechanical Validation passes and required Semantic Review converges. For this single-developer repository, intentional integration of the satisfactory candidate into `main` is Acceptance; no parallel acceptance record is required.

## License

This repository is licensed under the GNU General Public License, version 3. See `LICENSE`.
