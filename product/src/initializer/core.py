from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Sequence


class InitializationError(RuntimeError):
    """Raised when repository initialization cannot complete correctly."""


FRAMEWORK_SOURCE_RECORD = Path("repo/validation/framework-source.json")
GENERIC_PRODUCT_MARKER = Path("product/design/.gitkeep")
SEEDED_USER_PATHS = (Path("user/script-transfer-handoff.json"),)

# These are the maintained source surfaces used to construct the initialized
# repository. Product-owned initializer state is intentionally absent.
SUPPLYING_MATERIAL_PATHS = (
    ".github",
    ".gitignore",
    "AGENTS.md",
    "LICENSE",
    "README.md",
    "repo",
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
        destination = (Path.cwd() / destination).resolve()
    else:
        destination = destination.resolve()

    existed = destination.exists()

    if existed:
        if destination.is_symlink() or not destination.is_dir():
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


def _remove_initializer_product(stage: Path) -> None:
    product = stage / "product"
    if product.exists():
        shutil.rmtree(product)
    marker = stage / GENERIC_PRODUCT_MARKER
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("", encoding="utf-8")


def _reduce_user_material(stage: Path) -> None:
    user_root = stage / "user"
    keep = {path.as_posix() for path in SEEDED_USER_PATHS}

    if user_root.exists():
        for path in sorted(user_root.rglob("*"), reverse=True):
            if path.is_dir():
                continue
            rel = path.relative_to(stage).as_posix()
            if rel not in keep:
                path.unlink()

        # Remove now-empty nested directories without removing user/ itself.
        for path in sorted(
            (p for p in user_root.rglob("*") if p.is_dir()),
            key=lambda p: len(p.parts),
            reverse=True,
        ):
            try:
                path.rmdir()
            except OSError:
                pass

    # The handoff is seed-if-present in the supplying accepted framework.
    handoff = stage / "user/script-transfer-handoff.json"
    if handoff.exists():
        return
    if user_root.exists():
        try:
            user_root.rmdir()
        except OSError:
            pass


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
    _run(
        (
            "git",
            "fetch",
            "--no-tags",
            "--no-write-fetch-head",
            str(source_root),
            source_revision,
        ),
        cwd=stage,
    )
    _run(("git", "checkout", "-B", "main", source_revision), cwd=stage)

    _remove_initializer_product(stage)
    _reduce_user_material(stage)
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
    validator = stage / "repo/scripts/validate"
    if not validator.is_file():
        raise InitializationError("initialized repository is missing canonical validation entrypoint")
    completed = _run((str(validator),), cwd=stage, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise InitializationError(
            "initialized repository canonical validation failed"
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
