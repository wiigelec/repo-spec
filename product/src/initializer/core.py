from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Sequence


class InitializationError(RuntimeError):
    """Raised when repository initialization cannot complete correctly."""


class UpgradeError(InitializationError):
    """Raised when repository upgrade cannot complete correctly."""


FRAMEWORK_SOURCE_RECORD = Path("repo/validation/framework-source.json")
PRODUCT_DESIGN_README = Path("product/design/README.md")
PRODUCT_SPECS_README = Path("product/specs/README.md")
PRODUCT_VALIDATION_ENTRYPOINT = Path("product/scripts/validate")
PRODUCT_VALIDATION_MANIFEST = Path("product/validation/requirement-evaluation.json")
PRODUCT_VALIDATOR = Path("product/validation/validate_product.py")
SEEDED_USER_PATHS = (Path("user/script-transfer-handoff.json"),)


# These are the maintained source surfaces used to construct the initialized
# repository. Product-owned initializer state is intentionally absent.
SUPPLYING_MATERIAL_PATHS = (
    ".github",
    ".gitignore",
    "AGENTS.md",
    "LICENSE",
    "README.md",
    "product/src",
    "product/scripts/repo-spec",
    "repo",
    "scripts",
    "user/script-transfer-handoff.json",
)


def _run(
    cmd: Sequence[str],
    *,
    cwd: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(cmd),
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise InitializationError(
            f"command failed ({completed.returncode}): {' '.join(cmd)}"
            + (f": {detail}" if detail else "")
        )
    return completed


def _git(source: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return _run(("git", *args), cwd=source, check=check)


def _scalar(source: Path, *args: str) -> str:
    return _git(source, *args).stdout.rstrip("\r\n")


def _porcelain_entries(output: str) -> list[tuple[str, str]]:
    # Preserve the fixed-width porcelain status columns. Do not strip the
    # complete output before slicing status/path fields.
    entries: list[tuple[str, str]] = []
    for entry in output.split("\0"):
        if not entry:
            continue
        status = entry[:2]
        path = entry[3:] if len(entry) >= 4 else ""
        entries.append((status, path))
    return entries


def _verify_supplying_checkout(
    source_root: Path,
    *,
    require_accepted: bool,
) -> str:
    source_root = source_root.resolve()

    inside = _git(
        source_root,
        "rev-parse",
        "--is-inside-work-tree",
        check=False,
    )
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise InitializationError("supplying source is not a Git working tree")

    observed_root = Path(_scalar(source_root, "rev-parse", "--show-toplevel")).resolve()
    if observed_root != source_root:
        raise InitializationError(
            f"supplying source root mismatch: expected {source_root}, observed {observed_root}"
        )

    head = _scalar(source_root, "rev-parse", "HEAD")
    if len(head) != 40:
        raise InitializationError("supplying source HEAD is not a full Git commit identity")
    _git(source_root, "cat-file", "-e", f"{head}^{{commit}}")

    if require_accepted:
        main_check = _git(
            source_root,
            "show-ref",
            "--verify",
            "--quiet",
            "refs/heads/main",
            check=False,
        )
        if main_check.returncode != 0:
            raise InitializationError("accepted main history is unavailable in supplying checkout")

        accepted_check = _git(
            source_root,
            "merge-base",
            "--is-ancestor",
            head,
            "refs/heads/main",
            check=False,
        )
        if accepted_check.returncode != 0:
            raise InitializationError(
                f"supplying revision {head} is not established as accepted in local main history"
            )

    status = _git(
        source_root,
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=all",
        "--",
        *SUPPLYING_MATERIAL_PATHS,
    ).stdout
    dirty = _porcelain_entries(status)
    if dirty:
        detail = ", ".join(f"{status} {path}" for status, path in dirty)
        raise InitializationError(
            f"supplying maintained framework material is dirty: {detail}"
        )

    return head


def _verify_destination(destination: Path) -> tuple[Path, bool]:
    destination = destination.expanduser()
    if not destination.is_absolute():
        destination = Path.cwd() / destination

    # Check the user-selected destination itself before resolving it. Resolving
    # first would erase the fact that the selected path is a symlink.
    if destination.is_symlink():
        raise InitializationError("destination exists but is not an ordinary directory")

    destination = destination.resolve()
    existed = destination.exists()

    if existed:
        if not destination.is_dir():
            raise InitializationError("destination exists but is not an ordinary directory")
        try:
            next(destination.iterdir())
        except StopIteration:
            pass
        else:
            raise InitializationError("destination must be absent or an existing empty directory")

    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    if not parent.is_dir():
        raise InitializationError("destination parent is not a directory")

    return destination, existed


INSTALLED_MATERIAL_PATHS = (
    Path(".github"),
    Path("AGENTS.md"),
    Path("LICENSE"),
    Path("README.md"),
    Path("repo"),
    Path("scripts"),
    Path("user/script-transfer-handoff.json"),
)


def _copy_installed_material(stage: Path, source_root: Path) -> None:
    for rel in INSTALLED_MATERIAL_PATHS:
        source = source_root / rel
        if not source.exists():
            if rel == Path("user/script-transfer-handoff.json"):
                continue
            raise InitializationError(f"supplying installed material missing: {rel}")
        target = stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)

    planning = stage / "repo" / "planning"
    if planning.exists():
        shutil.rmtree(planning)

    _write_generic_product_scaffold(stage)


def _write_generic_product_scaffold(stage: Path) -> None:
    design = stage / PRODUCT_DESIGN_README
    specs = stage / PRODUCT_SPECS_README
    entrypoint = stage / PRODUCT_VALIDATION_ENTRYPOINT
    manifest = stage / PRODUCT_VALIDATION_MANIFEST
    validator = stage / PRODUCT_VALIDATOR

    design.parent.mkdir(parents=True, exist_ok=True)
    specs.parent.mkdir(parents=True, exist_ok=True)
    entrypoint.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)

    design.write_text('# Product Design\n\nPut human-readable Product Design documents in this directory.\n\nDesign owns product meaning: identity, intended behavior, architecture, boundaries, and other consequential semantic decisions. Do not treat this starter README as Product Design or as authority for a future product.\n', encoding="utf-8")
    specs.write_text('# Product Specifications\n\nPut reviewed product Functional Set normative specifications in this directory after Product Design and Planning establish them.\n\nNormative requirements belong here; mechanical validation bindings belong in `product/validation/requirement-evaluation.json`. This starter README does not define product requirements.\n', encoding="utf-8")
    entrypoint.write_text('#!/usr/bin/env bash\nset -euo pipefail\nrepo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"\nexec python3 "$repo_root/product/validation/validate_product.py" "$@"\n', encoding="utf-8")
    entrypoint.chmod(0o755)
    manifest.write_text(
        json.dumps({"version": 1, "bindings": []}, indent=2) + "\n",
        encoding="utf-8",
    )
    validator.write_text('#!/usr/bin/env python3\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom pathlib import Path\nfrom typing import Callable\n\nROOT = Path(__file__).resolve().parents[2]\nMANIFEST = ROOT / "product" / "validation" / "requirement-evaluation.json"\nTASKS: dict[str, Callable[[], bool | None]] = {}\n\n\ndef fail(message: str) -> int:\n    print(f"FAIL product-validation: {message}", file=sys.stderr)\n    return 1\n\n\ndef load_manifest() -> dict:\n    try:\n        data = json.loads(MANIFEST.read_text(encoding="utf-8"))\n    except (OSError, json.JSONDecodeError) as exc:\n        raise ValueError(f"cannot load product Requirement Evaluation Manifest: {exc}") from exc\n    if data.get("version") != 1 or not isinstance(data.get("bindings"), list):\n        raise ValueError("invalid product Requirement Evaluation Manifest structure")\n    return data\n\n\ndef manifest_tasks() -> list[str]:\n    data = load_manifest()\n    ordered: list[str] = []\n    for binding in data["bindings"]:\n        if not isinstance(binding, dict):\n            raise ValueError("product manifest binding must be an object")\n        tasks = binding.get("tasks")\n        if not isinstance(tasks, list) or not tasks:\n            raise ValueError("product manifest binding requires a non-empty tasks list")\n        for task in tasks:\n            if not isinstance(task, str) or not task:\n                raise ValueError("product validation task identity must be a non-empty string")\n            if task not in TASKS:\n                raise ValueError(f"product manifest references unknown task: {task}")\n            if task not in ordered:\n                ordered.append(task)\n    return ordered\n\n\ndef execute(task: str) -> int:\n    fn = TASKS.get(task)\n    if fn is None:\n        return fail(f"unknown product Validation task: {task}")\n    result = fn()\n    return 1 if result is False else 0\n\n\ndef main(argv: list[str] | None = None) -> int:\n    parser = argparse.ArgumentParser()\n    parser.add_argument("--list-tasks", action="store_true")\n    parser.add_argument("--task")\n    args = parser.parse_args(argv)\n\n    if args.list_tasks and args.task:\n        return fail("--list-tasks and --task are mutually exclusive")\n    if args.list_tasks:\n        for task in sorted(TASKS):\n            print(task)\n        return 0\n    if args.task:\n        return execute(args.task)\n\n    try:\n        tasks = manifest_tasks()\n    except ValueError as exc:\n        return fail(str(exc))\n    for task in tasks:\n        result = execute(task)\n        if result:\n            return result\n    print("Product Validation: PASS")\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n', encoding="utf-8")
    validator.chmod(0o755)


def _write_generic_root_documents(stage: Path) -> None:
    readme = stage / "README.md"
    agents = stage / "AGENTS.md"
    readme.write_text(
        "# Repository\n\n"
        "This repository uses an installed repo-spec lifecycle framework.\n\n"
        "## Lifecycle\n\n"
        "Work proceeds through Design, Planning, Build, Validation, Semantic Review, and Acceptance.\n\n"
        "`main` represents accepted repository state.\n\n"
        "## Repository surfaces\n\n"
        "- `repo/design/` — installed framework Design.\n"
        "- `repo/specs/` — installed framework normative specifications.\n"
        "- `repo/scripts/validate` — framework-owned mechanical Validation entry point.\n"
        "- `scripts/validate` — repository-wide mechanical Validation entry point.\n"
        "- `product/` is the product-owned domain. Product meaning is established independently through Product Design.\n"
        "- `product/design/` — starting surface for Product Design.\n"
        "- `user/` — user-owned operational material outside the framework.\n\n"
        "Begin substantive product work in Product Design.\n\n"
        "The exact repo-spec framework source revision used to initialize this repository is recorded in `repo/validation/framework-source.json`.\n\n"
        "Validation is mechanical evaluation only. Semantic Review evaluates meaning and fidelity. Acceptance is intentional integration of a satisfactory candidate into `main`.\n",
        encoding="utf-8",
    )
    agents.write_text(
        "# Repository Agent Guidance\n\n"
        "This file provides operational guidance and does not independently define normative meaning.\n\n"
        "## Lifecycle ownership\n\n"
        "A missing consequential semantic decision → **Design**.\n\n"
        "A Functional Set, Plan, normative requirement, scope, or evaluation-classification defect → **Planning**.\n\n"
        "An implementation or mechanical-enforcement-construction defect → **Build**.\n\n"
        "Validation does not create Design meaning or normative requirements.\n\n"
        "## Repository ownership\n\n"
        "`repo/` is the reusable repository-development framework.\n\n"
        "`product/` is the generic product-owned domain. Do not assume Product meaning before Product Design establishes it.\n\n"
        "`scripts/` is the narrow repository-wide operational composition role.\n\n"
        "`user/` is user-owned operational material outside the framework.\n\n"
        "Closed architectural boundaries are default-deny. Do not add new direct children or files where the accepted architecture does not allow them.\n\n"
        "## Build discipline\n\n"
        "Consume reviewed Design and Planning. Prefer the simplest implementation that preserves their meaning and satisfies applicable normative requirements.\n\n"
        "Do not infer normative intent from implementation behavior.\n\n"
        "## Validation\n\n"
        "Use `scripts/validate` as the repository-wide mechanical Validation entry point. `repo/scripts/validate` remains authoritative for framework mechanical checks.\n\n"
        "Mechanical Validation passing does not establish semantic acceptance.\n\n"
        "## Semantic Review and Acceptance\n\n"
        "Semantic Review evaluates the realized candidate against the complete applicable Design and Planning result.\n\n"
        "`main` represents accepted state. Acceptance occurs only through intentional integration of a satisfactory candidate into `main`.\n",
        encoding="utf-8",
    )

def _write_source_record(stage: Path, source_revision: str) -> None:
    record = stage / FRAMEWORK_SOURCE_RECORD
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "repo_spec_source_revision": source_revision,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _construct_stage(stage: Path, source_root: Path, source_revision: str) -> None:
    _run(("git", "init", "--initial-branch=main"), cwd=stage)
    _copy_installed_material(stage, source_root)
    _write_generic_root_documents(stage)
    _write_source_record(stage, source_revision)

    _run(("git", "add", "-A"), cwd=stage)
    staged = _run(("git", "diff", "--cached", "--quiet"), cwd=stage, check=False)
    if staged.returncode == 0:
        raise InitializationError("initialization produced no maintained repository change")
    if staged.returncode != 1:
        raise InitializationError("could not evaluate initialized repository changes")

    _run(
        (
            "git",
            "-c",
            "user.name=repo-spec initializer",
            "-c",
            "user.email=repo-spec@local.invalid",
            "commit",
            "-m",
            "Initialize repo-spec repository",
        ),
        cwd=stage,
    )


def _validate_stage(stage: Path) -> None:
    validator = stage / "scripts/validate"
    if not validator.is_file():
        raise InitializationError("initialized repository is missing repository-wide validation entrypoint")
    completed = _run((str(validator),), cwd=stage, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise InitializationError(
            "initialized repository repository-wide validation failed"
            + (f": {detail}" if detail else "")
        )


def _promote(stage: Path, destination: Path, destination_existed: bool) -> None:
    if destination_existed:
        destination.rmdir()
    try:
        os.replace(stage, destination)
    except OSError as exc:
        if destination_existed and not destination.exists():
            destination.mkdir(parents=False, exist_ok=True)
        raise InitializationError(f"could not promote initialized repository: {exc}") from exc


def initialize_repository(
    *,
    source_root: Path,
    destination: Path,
    require_accepted: bool = True,
    before_validate: Callable[[Path], None] | None = None,
) -> str:
    """Initialize one repository and return the exact supplying revision.

    ``require_accepted=False`` and ``before_validate`` are controlled internal
    test seams. The normal CLI does not expose either.
    """

    source_root = source_root.resolve()
    source_revision = _verify_supplying_checkout(
        source_root,
        require_accepted=require_accepted,
    )
    destination, destination_existed = _verify_destination(destination)

    stage = Path(
        tempfile.mkdtemp(
            prefix=f".{destination.name}.repo-spec-",
            dir=destination.parent,
        )
    )

    try:
        _construct_stage(stage, source_root, source_revision)
        if before_validate is not None:
            before_validate(stage)
        _validate_stage(stage)
        _promote(stage, destination, destination_existed)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage, ignore_errors=True)
        raise

    return source_revision

# Repository upgrade implementation -------------------------------------------------

ROOT_COMPATIBILITY_FILES = (
    Path("scripts/validate"),
)
PRODUCT_COMPATIBILITY_FILES = (
    PRODUCT_VALIDATION_ENTRYPOINT,
    PRODUCT_VALIDATION_MANIFEST,
    PRODUCT_VALIDATOR,
)
PRODUCT_REQUIRED_DIRECTORIES = (
    Path("product/design"),
    Path("product/specs"),
    Path("product/scripts"),
    Path("product/validation"),
)


def _full_revision(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _read_framework_source(root: Path) -> str:
    record = root / FRAMEWORK_SOURCE_RECORD
    try:
        data = json.loads(record.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise UpgradeError("installed framework source record is missing") from exc
    except json.JSONDecodeError as exc:
        raise UpgradeError(f"installed framework source record is malformed: {exc}") from exc

    if not isinstance(data, dict):
        raise UpgradeError("installed framework source record is malformed: expected JSON object")

    revision = data.get("repo_spec_source_revision")
    if not _full_revision(revision):
        raise UpgradeError(
            "installed framework source record does not identify one exact prior supplying revision"
        )
    return revision


def _verify_upgrade_target(target: Path) -> tuple[Path, str]:
    selected = target.expanduser()
    if not selected.is_absolute():
        selected = Path.cwd() / selected
    if selected.is_symlink():
        raise UpgradeError("upgrade target is not an ordinary repository directory")
    target = selected.resolve()
    if not target.is_dir() or not (target / ".git").is_dir():
        raise UpgradeError("upgrade target is not an eligible initialized repository")

    inside = _git(target, "rev-parse", "--is-inside-work-tree", check=False)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise UpgradeError("upgrade target is not a Git working tree")
    observed_root = Path(_scalar(target, "rev-parse", "--show-toplevel")).resolve()
    if observed_root != target:
        raise UpgradeError(
            f"upgrade target root mismatch: expected {target}, observed {observed_root}"
        )

    return target, _read_framework_source(target)


def _candidate_paths(root: Path, prefix: Path) -> set[Path]:
    output = _git(
        root,
        "ls-files",
        "-co",
        "--exclude-standard",
        "-z",
        "--",
        prefix.as_posix(),
    ).stdout
    return {Path(item) for item in output.split("\0") if item}


def _path_state(root: Path, rel: Path):
    path = root / rel
    if path.is_symlink():
        return ("symlink", os.readlink(path))
    if not path.exists():
        return None
    if path.is_dir():
        return ("directory",)
    return ("file", path.stat().st_mode & 0o777, path.read_bytes())


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _apply_state(root: Path, rel: Path, state) -> None:
    path = root / rel
    if state is None:
        if path.exists() or path.is_symlink():
            _remove_path(path)
        return

    if path.exists() or path.is_symlink():
        _remove_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if state[0] == "symlink":
        path.symlink_to(state[1])
    elif state[0] == "directory":
        path.mkdir(parents=True, exist_ok=True)
    else:
        _, mode, content = state
        path.write_bytes(content)
        path.chmod(mode)


def _snapshot_product_and_user_owned(root: Path) -> dict[Path, object]:
    states: dict[Path, object] = {}
    excluded = set(PRODUCT_COMPATIBILITY_FILES)
    for prefix in (Path("product"), Path("user")):
        for rel in _candidate_paths(root, prefix):
            if rel in excluded:
                continue
            states[rel] = _path_state(root, rel)
    return states


def _verify_forward_upgrade_relation(
    source_root: Path,
    installed_revision: str,
    source_revision: str,
) -> None:
    resolved = _git(
        source_root,
        "cat-file",
        "-e",
        f"{installed_revision}^{{commit}}",
        check=False,
    )
    if resolved.returncode != 0:
        raise UpgradeError(
            f"installed supplier revision unavailable for supported reconstruction: {installed_revision}"
        )

    forward = _git(
        source_root,
        "merge-base",
        "--is-ancestor",
        installed_revision,
        source_revision,
        check=False,
    )
    if forward.returncode != 0:
        raise UpgradeError(
            "selected supplying revision is not a later descendant of the installed "
            f"framework revision: {installed_revision} -> {source_revision}"
        )


def _construct_installed_snapshot(stage: Path, source_root: Path, revision: str) -> None:
    stage.mkdir(parents=True, exist_ok=False)
    _construct_stage(stage, source_root, revision)


def _reconstruct_prior_snapshot(
    source_root: Path,
    revision: str,
    destination: Path,
) -> None:
    parent = Path(tempfile.mkdtemp(prefix=".repo-spec-old-source-", dir=source_root.parent))
    worktree = parent / "source"
    try:
        added = _git(
            source_root,
            "worktree",
            "add",
            "--detach",
            str(worktree),
            revision,
            check=False,
        )
        if added.returncode != 0:
            detail = added.stderr.strip() or added.stdout.strip()
            raise UpgradeError(
                "installed supplier revision unavailable for supported reconstruction"
                + (f": {detail}" if detail else "")
            )

        code = (
            "from pathlib import Path; import sys; sys.dont_write_bytecode = True; "
            "sys.path.insert(0, str(Path(sys.argv[1]) / 'product' / 'src')); "
            "from initializer.core import initialize_repository; "
            "initialize_repository(source_root=Path(sys.argv[1]), "
            "destination=Path(sys.argv[2]), require_accepted=False)"
        )
        completed = _run(
            (sys.executable, "-c", code, str(worktree), str(destination)),
            cwd=worktree,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip()
            raise UpgradeError(
                "installed supplier revision could not reconstruct prior expected framework state"
                + (f": {detail}" if detail else "")
            )
    finally:
        if worktree.exists():
            _git(
                source_root,
                "worktree",
                "remove",
                "--force",
                str(worktree),
                check=False,
            )
        shutil.rmtree(parent, ignore_errors=True)


def _reconcile_framework_owned(
    stage: Path,
    target: Path,
    prior: Path,
    prospective: Path,
) -> None:
    prefix = Path("repo")
    paths = (
        _candidate_paths(prior, prefix)
        | _candidate_paths(prospective, prefix)
        | _candidate_paths(target, prefix)
    )
    paths.discard(FRAMEWORK_SOURCE_RECORD)

    conflicts: list[str] = []
    for rel in sorted(paths):
        old = _path_state(prior, rel)
        observed = _path_state(target, rel)
        new = _path_state(prospective, rel)
        if observed != old:
            conflicts.append(rel.as_posix())
            continue
        if new != old:
            _apply_state(stage, rel, new)

    if conflicts:
        raise UpgradeError(
            "local framework modification conflict: " + ", ".join(conflicts)
        )


def _reconcile_framework_source_record(
    target: Path,
    prior: Path,
) -> None:
    old = _path_state(prior, FRAMEWORK_SOURCE_RECORD)
    observed = _path_state(target, FRAMEWORK_SOURCE_RECORD)
    if observed != old:
        raise UpgradeError(
            "local framework modification conflict: "
            + FRAMEWORK_SOURCE_RECORD.as_posix()
        )


def _reconcile_root_compatibility(
    stage: Path,
    target: Path,
    prior: Path,
    prospective: Path,
) -> None:
    for rel in ROOT_COMPATIBILITY_FILES:
        old = _path_state(prior, rel)
        observed = _path_state(target, rel)
        new = _path_state(prospective, rel)

        if observed is None and new is not None:
            _apply_state(stage, rel, new)
        elif observed == old and old != new:
            _apply_state(stage, rel, new)
        elif observed == new:
            continue
        # Independently changed root operational material is preserved.
        # Prospective framework Validation decides whether it remains compatible.


def _reconcile_product_compatibility(
    stage: Path,
    target: Path,
    prior: Path,
    prospective: Path,
) -> None:
    for rel in PRODUCT_REQUIRED_DIRECTORIES:
        if (prospective / rel).is_dir() and not (stage / rel).exists():
            (stage / rel).mkdir(parents=True, exist_ok=True)

    for rel in PRODUCT_COMPATIBILITY_FILES:
        old = _path_state(prior, rel)
        observed = _path_state(target, rel)
        new = _path_state(prospective, rel)

        if observed is None and new is not None:
            _apply_state(stage, rel, new)
        elif observed == old and old != new:
            _apply_state(stage, rel, new)
        elif observed == new:
            continue
        # Divergent product-owned content remains product-owned. Framework
        # Validation below decides whether the preserved interface is compatible.


def _validate_upgrade_stage(
    stage: Path,
    *,
    expected_revision: str,
    preserved_owned_state: dict[Path, object],
    target_head: str,
) -> None:
    observed_revision = _read_framework_source(stage)
    if observed_revision != expected_revision:
        raise UpgradeError(
            f"prospective framework source mismatch: expected {expected_revision}, "
            f"observed {observed_revision}"
        )

    stage_head = _scalar(stage, "rev-parse", "HEAD")
    if stage_head != target_head:
        raise UpgradeError("prospective upgrade changed target repository history")

    for rel, before in preserved_owned_state.items():
        after = _path_state(stage, rel)
        if after != before:
            raise UpgradeError(
                f"prospective upgrade modified preserved repository-owned state: {rel}"
            )

    validator = stage / "repo" / "scripts" / "validate"
    if not validator.is_file():
        raise UpgradeError("prospective framework is missing repo/scripts/validate")
    completed = _run((str(validator),), cwd=stage, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise UpgradeError(
            "prospective framework Validation failed"
            + (f": {detail}" if detail else "")
        )


def _promote_upgrade(stage: Path, target: Path) -> None:
    backup = Path(
        tempfile.mkdtemp(prefix=f".{target.name}.repo-spec-backup-", dir=target.parent)
    )
    backup.rmdir()

    moved_target = False
    try:
        os.replace(target, backup)
        moved_target = True
        os.replace(stage, target)
    except OSError as exc:
        if moved_target and backup.exists() and not target.exists():
            try:
                os.replace(backup, target)
            except OSError as rollback_exc:
                raise UpgradeError(
                    f"upgrade promotion failed and rollback failed: {rollback_exc}"
                ) from exc
        raise UpgradeError(f"upgrade promotion failed: {exc}") from exc
    else:
        shutil.rmtree(backup, ignore_errors=True)


def upgrade_repository(
    *,
    source_root: Path,
    target: Path,
    require_accepted: bool = True,
    before_validate: Callable[[Path], None] | None = None,
) -> str:
    """Upgrade one initialized repository and return the new supplying revision.

    ``require_accepted=False`` and ``before_validate`` are controlled internal
    test seams. The normal CLI exposes neither.
    """

    source_root = source_root.resolve()
    source_revision = _verify_supplying_checkout(
        source_root,
        require_accepted=require_accepted,
    )
    target, installed_revision = _verify_upgrade_target(target)

    if source_revision == installed_revision:
        raise UpgradeError(
            f"selected framework revision is already recorded as installed: {source_revision}"
        )

    _verify_forward_upgrade_relation(
        source_root,
        installed_revision,
        source_revision,
    )

    target_head = _scalar(target, "rev-parse", "HEAD")
    preserved_owned_state = _snapshot_product_and_user_owned(target)

    snapshot_root = Path(tempfile.mkdtemp(prefix=".repo-spec-upgrade-snapshots-"))
    prior = snapshot_root / "prior"
    prospective = snapshot_root / "prospective"

    stage_holder = Path(
        tempfile.mkdtemp(prefix=f".{target.name}.repo-spec-upgrade-", dir=target.parent)
    )
    stage = stage_holder / "repository"

    try:
        _reconstruct_prior_snapshot(source_root, installed_revision, prior)
        _construct_installed_snapshot(prospective, source_root, source_revision)

        shutil.copytree(target, stage, symlinks=True)

        _reconcile_framework_owned(stage, target, prior, prospective)
        _reconcile_framework_source_record(target, prior)
        _reconcile_root_compatibility(stage, target, prior, prospective)
        _reconcile_product_compatibility(stage, target, prior, prospective)
        _write_source_record(stage, source_revision)

        if before_validate is not None:
            before_validate(stage)

        _validate_upgrade_stage(
            stage,
            expected_revision=source_revision,
            preserved_owned_state=preserved_owned_state,
            target_head=target_head,
        )
        _promote_upgrade(stage, target)
    finally:
        shutil.rmtree(snapshot_root, ignore_errors=True)
        if stage_holder.exists():
            shutil.rmtree(stage_holder, ignore_errors=True)

    return source_revision
