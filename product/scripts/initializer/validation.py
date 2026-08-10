from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from .foundations import (
    DECOMPOSITION_CHUNK_COVERAGE,
    OVERVIEW_CHUNK_COVERAGE,
    PLAN_CHUNK_COVERAGE,
)
from .models import ExecutionContext, ImmutableRequest, InitializerError


MISSING_REQUIRED = "missing-required"
EMPTY_AUTHORITY = "empty-authority"
INVALID_STRUCTURE = "invalid-structure"
CONTRADICTORY_COMBINATION = "contradictory-combination"
EXCLUDED_BEHAVIOR = "excluded-behavior"

ROOT_FIELDS = ("schema_version", "destination")
KNOWN_ROOT_FIELDS = frozenset(ROOT_FIELDS)
KNOWN_AUTHORITY_FIELDS = frozenset(("granted_by", "type", "scope"))
KNOWN_SOURCE_FIELDS = frozenset(("repository", "revision"))
KNOWN_REVISION_FIELDS = frozenset(("object_format", "object_id"))
KNOWN_PRODUCT_FIELDS = frozenset(("id", "direction_material"))
PRODUCT_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
URL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
SCP_REMOTE_RE = re.compile(r"^(?:[^/@]+@)?[^/:]+:.+")


class ValidationError(InitializerError):
    def __init__(self, category: str, message: str) -> None:
        self.category = category
        self.message = message

    def __str__(self) -> str:
        return f"{self.category}: {self.message}"


class ValidationResult:
    def __init__(self) -> None:
        self._errors: list[ValidationError] = []

    def add(self, category: str, message: str) -> None:
        self._errors.append(ValidationError(category, message))

    @property
    def errors(self) -> list[ValidationError]:
        return list(self._errors)

    @property
    def is_valid(self) -> bool:
        return not self._errors

    def raise_if_invalid(self) -> None:
        if self._errors:
            raise self._errors[0]


def load_request(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        detail = exc.msg if isinstance(exc, json.JSONDecodeError) else str(exc)
        raise ValidationError(INVALID_STRUCTURE, f"invalid JSON in request file: {detail}") from exc
    except OSError as exc:
        raise ValidationError(INVALID_STRUCTURE, f"cannot read request file: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValidationError(INVALID_STRUCTURE, "request must be one JSON object")
    return raw


def validate_request(raw: dict[str, Any], cwd: str) -> ValidationResult:
    result, _ = _validate_and_build(raw, cwd)
    return result


def validate_and_normalize(raw: dict[str, Any], cwd: str) -> ExecutionContext:
    result, canonical = _validate_and_build(raw, cwd)
    result.raise_if_invalid()
    assert canonical is not None
    canonical_bytes = canonical_request_bytes(canonical)
    fingerprint = hashlib.sha256(canonical_bytes).hexdigest()
    return ExecutionContext(ImmutableRequest(canonical, canonical_bytes, fingerprint))


def _validate_and_build(
    raw: dict[str, Any], cwd: str
) -> tuple[ValidationResult, dict[str, Any] | None]:
    result = ValidationResult()
    _check_unicode_scalars(raw, result, "request")
    _check_unknown_fields(raw, KNOWN_ROOT_FIELDS, result, "request")
    _check_required_fields(raw, ROOT_FIELDS, result, "request")

    schema_version = _required_string(raw, "schema_version", result)
    destination = _required_string(raw, "destination", result)

    if schema_version is not None and schema_version != "2":
        result.add(EXCLUDED_BEHAVIOR, f"unsupported schema version: {schema_version!r}")

    resolved_destination = _resolve_v1_path(destination, cwd, result, "destination")
    if resolved_destination == "/":
        result.add(INVALID_STRUCTURE, "destination must have a repository-name basename")

    if not result.is_valid:
        return result, None

    assert schema_version is not None
    assert resolved_destination is not None
    return result, {
        "schema_version": schema_version,
        "destination": resolved_destination,
    }


def _check_unicode_scalars(value: Any, result: ValidationResult, context: str) -> None:
    if isinstance(value, str):
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            result.add(INVALID_STRUCTURE, f"{context} contains a non-Unicode-scalar value")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _check_unicode_scalars(item, result, f"{context}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            _check_unicode_scalars(key, result, f"{context} field name")
            _check_unicode_scalars(item, result, f"{context}.{key}")


def _check_unknown_fields(
    data: dict[str, Any], known: frozenset[str], result: ValidationResult, context: str
) -> None:
    for key in data:
        if key not in known:
            result.add(INVALID_STRUCTURE, f"unknown field in {context}: {key!r}")


def _check_required_fields(
    data: dict[str, Any], required: tuple[str, ...], result: ValidationResult, context: str
) -> None:
    for field in required:
        if field not in data:
            result.add(MISSING_REQUIRED, f"missing required field: {context}.{field}")


def _required_string(
    data: dict[str, Any], field: str, result: ValidationResult
) -> str | None:
    if field not in data:
        return None
    value = data[field]
    if not isinstance(value, str):
        result.add(INVALID_STRUCTURE, f"{field} must be a string")
        return None
    if value == "":
        result.add(EMPTY_AUTHORITY, f"{field} must not be empty")
        return None
    return value


def _required_object(
    data: dict[str, Any], field: str, result: ValidationResult
) -> dict[str, Any] | None:
    if field not in data:
        return None
    value = data[field]
    if not isinstance(value, dict):
        result.add(INVALID_STRUCTURE, f"{field} must be an object")
        return None
    return value


def _validate_authority(
    authority: dict[str, Any] | None, result: ValidationResult
) -> dict[str, str] | None:
    if authority is None:
        return None
    _check_unknown_fields(authority, KNOWN_AUTHORITY_FIELDS, result, "authority")
    _check_required_fields(authority, ("granted_by",), result, "authority")
    output: dict[str, str] = {}
    for field in ("granted_by", "type", "scope"):
        if field not in authority:
            continue
        value = authority[field]
        if not isinstance(value, str):
            result.add(INVALID_STRUCTURE, f"authority.{field} must be a string")
        elif not value or value.isspace():
            result.add(EMPTY_AUTHORITY, f"authority.{field} must not be empty or whitespace-only")
        else:
            output[field] = value
    return output


def _validate_source(
    source: dict[str, Any] | None, cwd: str, result: ValidationResult
) -> dict[str, Any] | None:
    if source is None:
        return None
    _check_unknown_fields(source, KNOWN_SOURCE_FIELDS, result, "source")
    _check_required_fields(source, ("repository", "revision"), result, "source")

    repository: str | None = None
    if "repository" in source:
        value = source["repository"]
        if not isinstance(value, str):
            result.add(INVALID_STRUCTURE, "source.repository must be a string")
        elif value == "":
            result.add(EMPTY_AUTHORITY, "source.repository must not be empty")
        else:
            repository = _resolve_v1_path(value, cwd, result, "source.repository")

    revision = source.get("revision")
    canonical_revision: dict[str, str] | None = None
    if "revision" in source:
        if isinstance(revision, str):
            if not revision:
                category = EMPTY_AUTHORITY
            elif len(revision) == 40 and all(
                char in "0123456789abcdef" for char in revision
            ):
                category = INVALID_STRUCTURE
            else:
                category = EXCLUDED_BEHAVIOR
            result.add(category, "source.revision must be a structured SHA-1 Git object identity")
        elif not isinstance(revision, dict):
            result.add(INVALID_STRUCTURE, "source.revision must be an object")
        else:
            canonical_revision = _validate_revision(revision, result)

    if repository is None or canonical_revision is None:
        return None
    return {"repository": repository, "revision": canonical_revision}


def _validate_revision(
    revision: dict[str, Any], result: ValidationResult
) -> dict[str, str] | None:
    _check_unknown_fields(revision, KNOWN_REVISION_FIELDS, result, "source.revision")
    _check_required_fields(
        revision, ("object_format", "object_id"), result, "source.revision"
    )
    object_format = revision.get("object_format")
    object_id = revision.get("object_id")
    if not isinstance(object_format, str):
        if "object_format" in revision:
            result.add(INVALID_STRUCTURE, "source.revision.object_format must be a string")
        return None
    if not isinstance(object_id, str):
        if "object_id" in revision:
            result.add(INVALID_STRUCTURE, "source.revision.object_id must be a string")
        return None
    if not object_format or not object_id:
        result.add(EMPTY_AUTHORITY, "Git object identity fields must not be empty")
        return None
    if object_format != "sha1":
        result.add(EXCLUDED_BEHAVIOR, f"unsupported Git object format: {object_format!r}")
        return None
    if len(object_id) == 64 and all(char in "0123456789abcdef" for char in object_id):
        result.add(
            CONTRADICTORY_COMBINATION,
            "source.revision.object_id length contradicts object_format 'sha1'",
        )
        return None
    if len(object_id) != 40 or any(char not in "0123456789abcdef" for char in object_id):
        if not all(char in "0123456789abcdefABCDEF" for char in object_id):
            result.add(
                EXCLUDED_BEHAVIOR,
                "source.revision.object_id must not be a named reference",
            )
            return None
        result.add(
            INVALID_STRUCTURE,
            "source.revision.object_id must be exactly 40 lowercase hexadecimal characters",
        )
        return None
    return {"object_format": object_format, "object_id": object_id}


def _validate_product(
    product: dict[str, Any] | None, result: ValidationResult
) -> dict[str, Any] | None:
    if product is None:
        return None
    _check_unknown_fields(product, KNOWN_PRODUCT_FIELDS, result, "product")
    _check_required_fields(product, ("id", "direction_material"), result, "product")

    product_id = product.get("id")
    if not isinstance(product_id, str):
        if "id" in product:
            result.add(INVALID_STRUCTURE, "product.id must be a string")
        product_id = None
    elif not product_id:
        result.add(EMPTY_AUTHORITY, "product.id must not be empty")
        product_id = None
    elif PRODUCT_ID_RE.fullmatch(product_id) is None:
        result.add(INVALID_STRUCTURE, "product.id does not match the canonical product identifier pattern")
        product_id = None

    material = product.get("direction_material")
    valid_material: list[str] | None = None
    if not isinstance(material, list):
        if "direction_material" in product:
            result.add(INVALID_STRUCTURE, "product.direction_material must be an array")
    elif not material:
        result.add(EMPTY_AUTHORITY, "product.direction_material must not be empty")
    else:
        valid_material = []
        for index, item in enumerate(material):
            if not isinstance(item, str):
                result.add(INVALID_STRUCTURE, f"product.direction_material[{index}] must be a string")
            elif not item:
                result.add(EMPTY_AUTHORITY, f"product.direction_material[{index}] must not be empty")
            elif "\x00" in item or item.startswith("/"):
                result.add(INVALID_STRUCTURE, f"product.direction_material[{index}] must be repository-relative")
            elif _is_remote_identity(item):
                result.add(EXCLUDED_BEHAVIOR, f"product.direction_material[{index}] must not name a URL or remote identity")
            elif _escapes_repository(item):
                result.add(INVALID_STRUCTURE, f"product.direction_material[{index}] escapes the source repository")
            else:
                valid_material.append(item)

    if product_id is None or valid_material is None:
        return None
    return {"id": product_id, "direction_material": valid_material}


def _resolve_v1_path(
    value: str | None, cwd: str, result: ValidationResult, context: str
) -> str | None:
    if value is None:
        return None
    if not isinstance(cwd, str) or not cwd.startswith("/") or "\x00" in cwd:
        result.add(EXCLUDED_BEHAVIOR, "invoking working directory is not a supported Version 1 absolute path")
        return None
    if any(0xD800 <= ord(char) <= 0xDFFF for char in cwd):
        result.add(EXCLUDED_BEHAVIOR, "invoking working directory is not representable as Unicode scalar values")
        return None
    if "\x00" in value:
        result.add(INVALID_STRUCTURE, f"{context} must not contain U+0000")
        return None
    if _is_remote_identity(value):
        result.add(EXCLUDED_BEHAVIOR, f"{context} must not name a URL or remote identity")
        return None

    retained = [] if value.startswith("/") else _normalize_segments(cwd.split("/"))
    for segment in value.split("/"):
        if not segment or segment == ".":
            continue
        if segment == "..":
            if retained:
                retained.pop()
        else:
            retained.append(segment)
    return "/" + "/".join(retained) if retained else "/"


def _normalize_segments(segments: list[str]) -> list[str]:
    retained: list[str] = []
    for segment in segments:
        if not segment or segment == ".":
            continue
        if segment == "..":
            if retained:
                retained.pop()
        else:
            retained.append(segment)
    return retained


def _is_remote_identity(value: str) -> bool:
    return URL_RE.match(value) is not None or SCP_REMOTE_RE.match(value) is not None


def _escapes_repository(value: str) -> bool:
    depth = 0
    for segment in value.split("/"):
        if not segment or segment == ".":
            continue
        if segment == "..":
            if depth == 0:
                return True
            depth -= 1
        else:
            depth += 1
    return False


def canonical_request_bytes(value: Any) -> bytes:
    return _canonical_json(value).encode("utf-8")


def _canonical_json(value: Any) -> str:
    if isinstance(value, str):
        return _canonical_json_string(value)
    if isinstance(value, list):
        return "[" + ",".join(_canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(
            _canonical_json_string(key) + ":" + _canonical_json(item)
            for key, item in value.items()
        ) + "}"
    raise TypeError(f"unsupported canonical request value: {type(value).__name__}")


def _canonical_json_string(value: str) -> str:
    encoded: list[str] = ['"']
    for char in value:
        codepoint = ord(char)
        if char == '"':
            encoded.append('\\"')
        elif char == "\\":
            encoded.append("\\\\")
        elif codepoint <= 0x1F:
            encoded.append(f"\\u{codepoint:04x}")
        else:
            encoded.append(char)
    encoded.append('"')
    return "".join(encoded)


def validate_product_foundation_prerequisites(
    raw: dict[str, Any], result: ValidationResult
) -> None:
    product = raw.get("product")
    if not isinstance(product, dict):
        result.add(MISSING_REQUIRED, "product block is required for foundation establishment")
        return
    _validate_product(product, result)


def validate_json_request(path: Path, cwd: str) -> int:
    try:
        raw = load_request(path)
        ctx = validate_and_normalize(raw, cwd)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    request = ctx.request
    print(json.dumps({
        "status": "valid",
        "schema_version": request.schema_version,
        "destination": request.destination,
        "authority_granted_by": request.authority["granted_by"],
        "request_fingerprint": request.request_fingerprint,
    }, indent=2, ensure_ascii=False))
    return 0

# I4 PATCH 1: REPOSITORY VALIDATION
#
# Implements accepted Version 1 validation-profile execution, repository
# validation results, and deterministic validation-report construction.
# Durable report/staging-state finalization remains Patch 2 scope.

from dataclasses import dataclass as _dataclass
import os as _os
import subprocess as _subprocess
from collections.abc import Callable as _Callable

from .inventory import (
    MANIFEST_PATH as _MATERIAL_MANIFEST_PATH,
    OUTPUT_INVENTORY_SPEC_PATH as _OUTPUT_INVENTORY_SPEC_PATH,
    InventoryError as _InventoryError,
    _load_json_blob as _load_json_blob,
    _read_commit_blob as _read_commit_blob,
    _tree_entry as _tree_entry,
    validate_material_manifest as _validate_material_manifest,
)
from .staging import StagingWorkspace as _StagingWorkspace, validate_staging_workspace as _validate_staging_workspace


_I4_PROFILE_SPEC = "product/specs/product/level-1/validation-profile.json"
_I4_PROFILE_ALLOWED_SCOPES = frozenset(
    {"request", "source", "material-manifest", "repository-worktree", "git-state"}
)
_I4_RESULT_STATUSES = frozenset({"passed", "failed", "error", "skipped"})
_I4_PHASE_1_MAX_ORDER = 70
_I4_PHASE_2_MIN_ORDER = 80


@_dataclass(frozen=True)
class ValidationProfileCheck:
    check_id: str
    classification: str
    order: int
    applies_to: str
    pass_condition: str
    failure_codes: tuple[str, ...]


@_dataclass(frozen=True)
class RepositoryCheckResult:
    check_id: str
    status: str
    failure_code: str | None = None
    failure_message: str | None = None
    evidence: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        out: dict[str, object] = {"check_id": self.check_id, "status": self.status}
        if self.failure_code is not None:
            out["failure_code"] = self.failure_code
        if self.failure_message is not None:
            out["failure_message"] = self.failure_message
        if self.evidence is not None:
            out["evidence"] = self.evidence
        return out


@_dataclass(frozen=True)
class RepositoryValidationInputs:
    workspace: _StagingWorkspace
    expected_repository_content_digest: str

    @property
    def request(self) -> ImmutableRequest:
        return self.workspace.inputs.request

    @property
    def source_repository(self) -> str:
        return self.workspace.inputs.source.repository

    @property
    def source_revision(self) -> str:
        return self.workspace.inputs.source.commit_id

    @property
    def repository_root(self) -> Path:
        return self.workspace.repository_path


@_dataclass(frozen=True)
class RepositoryValidationRun:
    profile_version: str
    checks: tuple[RepositoryCheckResult, ...]
    overall_status: str
    request_fingerprint: str
    repository_content_digest: str

    def report_dict(self) -> dict[str, object]:
        return {
            "schema_version": "1",
            "report_version": "1",
            "profile_version": self.profile_version,
            "request_fingerprint": self.request_fingerprint,
            "repository_content_digest": self.repository_content_digest,
            "overall_status": self.overall_status,
            "checks": [item.to_dict() for item in self.checks],
        }

    def report_bytes(self) -> bytes:
        return (json.dumps(self.report_dict(), ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _i4_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def load_validation_profile_v1() -> tuple[str, tuple[ValidationProfileCheck, ...]]:
    raw = json.loads((_i4_repo_root() / _I4_PROFILE_SPEC).read_text(encoding="utf-8"))
    if raw.get("status") != "accepted" or raw.get("profile_version") != "v1":
        raise ValidationError(INVALID_STRUCTURE, "accepted validation profile v1 is unavailable")
    raw_checks = raw.get("checks")
    if not isinstance(raw_checks, list) or not raw_checks:
        raise ValidationError(INVALID_STRUCTURE, "validation profile checks must be a non-empty array")
    parsed: list[ValidationProfileCheck] = []
    ids: set[str] = set()
    orders: set[int] = set()
    for index, item in enumerate(raw_checks):
        if not isinstance(item, dict):
            raise ValidationError(INVALID_STRUCTURE, f"validation profile checks[{index}] must be an object")
        check_id = item.get("check_id")
        classification = item.get("classification")
        order = item.get("order")
        applies_to = item.get("applies_to")
        pass_condition = item.get("pass_condition")
        failure_codes = item.get("failure_codes")
        if not isinstance(check_id, str) or not check_id:
            raise ValidationError(INVALID_STRUCTURE, "validation check_id must be non-empty")
        if check_id in ids:
            raise ValidationError(INVALID_STRUCTURE, f"duplicate validation check_id: {check_id}")
        if classification not in {"required", "advisory"}:
            raise ValidationError(INVALID_STRUCTURE, f"invalid classification for {check_id}")
        if not isinstance(order, int) or isinstance(order, bool):
            raise ValidationError(INVALID_STRUCTURE, f"invalid order for {check_id}")
        if order in orders:
            raise ValidationError(INVALID_STRUCTURE, f"duplicate validation order: {order}")
        if applies_to not in _I4_PROFILE_ALLOWED_SCOPES:
            raise ValidationError(INVALID_STRUCTURE, f"invalid applies_to for {check_id}")
        if not isinstance(pass_condition, str) or not pass_condition:
            raise ValidationError(INVALID_STRUCTURE, f"missing pass_condition for {check_id}")
        if (
            not isinstance(failure_codes, list)
            or not failure_codes
            or any(not isinstance(code, str) or not code for code in failure_codes)
            or len(set(failure_codes)) != len(failure_codes)
        ):
            raise ValidationError(INVALID_STRUCTURE, f"invalid failure_codes for {check_id}")
        ids.add(check_id)
        orders.add(order)
        parsed.append(
            ValidationProfileCheck(
                check_id=check_id,
                classification=classification,
                order=order,
                applies_to=applies_to,
                pass_condition=pass_condition,
                failure_codes=tuple(failure_codes),
            )
        )
    parsed.sort(key=lambda item: item.order)
    if any(
        _I4_PHASE_1_MAX_ORDER < item.order < _I4_PHASE_2_MIN_ORDER
        for item in parsed
    ):
        raise ValidationError(INVALID_STRUCTURE, "validation profile contains a check outside Phase 1/2 ranges")
    return "v1", tuple(parsed)


def _i4_git(repo: Path | str, *args: str) -> _subprocess.CompletedProcess[str]:
    env = dict(_os.environ)
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    return _subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=_subprocess.PIPE,
        stderr=_subprocess.PIPE,
        env=env,
        check=False,
    )


def _i4_pass(check: ValidationProfileCheck, **evidence: object) -> RepositoryCheckResult:
    return RepositoryCheckResult(check.check_id, "passed", evidence=evidence or None)


def _i4_fail(check: ValidationProfileCheck, code: str, message: str, **evidence: object) -> RepositoryCheckResult:
    if code not in check.failure_codes:
        raise ValidationError(INVALID_STRUCTURE, f"failure code {code!r} is not declared for {check.check_id}")
    return RepositoryCheckResult(check.check_id, "failed", code, message, evidence or None)


def _i4_error(check: ValidationProfileCheck, code: str, message: str, **evidence: object) -> RepositoryCheckResult:
    if code not in check.failure_codes:
        code = check.failure_codes[0]
    return RepositoryCheckResult(check.check_id, "error", code, message, evidence or None)


def _i4_load_output_inventory() -> dict[str, Any]:
    return json.loads((_i4_repo_root() / _OUTPUT_INVENTORY_SPEC_PATH).read_text(encoding="utf-8"))


def _i4_material_manifest(inputs: RepositoryValidationInputs) -> dict[str, Any]:
    return _load_json_blob(inputs.source_repository, inputs.source_revision, _MATERIAL_MANIFEST_PATH)


def _i4_expected_explicit_paths(output_inventory: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for key in ("fixed_worktree_files", "material_index"):
        values = output_inventory.get(key, [])
        if isinstance(values, list):
            for item in values:
                if isinstance(item, dict):
                    path = item.get("path") or item.get("destination_path")
                    if isinstance(path, str) and path:
                        paths.add(path)
    return paths


def _i4_observed_worktree_files(repository_root: Path) -> set[str]:
    found: set[str] = set()
    for path in repository_root.rglob("*"):
        rel = path.relative_to(repository_root).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        if path.is_file() or path.is_symlink():
            found.add(rel)
    return found


def _i4_dynamic_template_pattern(template_value: str) -> str | None:
    chunk_families = {
        "product/docs/overview/{slug}-overview/chunk-{NN}-{topic}.md":
            tuple("chunk-" + item[0] for item in OVERVIEW_CHUNK_COVERAGE),
        "product/docs/decompositions/{slug}-decomposition/chunk-{NN}-{topic}.md":
            tuple("chunk-" + item[0] for item in DECOMPOSITION_CHUNK_COVERAGE),
        "product/docs/plans/{slug}-implementation-plan/chunk-{NN}-{topic}.md":
            tuple("chunk-" + item[0] for item in PLAN_CHUNK_COVERAGE),
    }
    chunk_basenames = chunk_families.get(template_value)
    if chunk_basenames is not None:
        prefix, marker = template_value.split("chunk-{NN}-{topic}.md", 1)
        if marker:
            return None
        prefix_pattern = re.escape(prefix).replace(
            re.escape("{slug}"),
            PRODUCT_ID_RE.pattern.removeprefix("^").removesuffix("$"),
        )
        basename_pattern = "(?:" + "|".join(
            re.escape(name) for name in chunk_basenames
        ) + ")"
        return prefix_pattern + basename_pattern

    pattern = re.escape(template_value)
    pattern = pattern.replace(
        re.escape("{slug}"),
        PRODUCT_ID_RE.pattern.removeprefix("^").removesuffix("$"),
    )
    pattern = pattern.replace(re.escape("{index:03d}"), r"\d{3}")
    pattern = pattern.replace(re.escape("{basename}"), r"[^/]+")
    if re.search(r"\\\{[^{}]+\\\}", pattern):
        return None
    return pattern


def _i4_match_dynamic(path: str, output_inventory: dict[str, Any]) -> bool:
    families = output_inventory.get("dynamic_path_families", [])
    if not isinstance(families, list):
        return False
    for family in families:
        if not isinstance(family, dict):
            continue
        exact = family.get("path")
        if isinstance(exact, str) and exact == path:
            return True
        for key in ("prefix", "root", "directory", "path_prefix"):
            prefix = family.get(key)
            if isinstance(prefix, str) and prefix and path.startswith(prefix.rstrip("/") + "/"):
                return True
        templates: list[str] = []
        template = family.get("path_template") or family.get("template")
        if isinstance(template, str) and template:
            templates.append(template)
        expansion_pattern = family.get("expansion_pattern")
        if isinstance(expansion_pattern, str) and expansion_pattern:
            templates.extend(
                item.strip()
                for item in expansion_pattern.split(",")
                if item.strip()
            )
        for template_value in templates:
            pattern = _i4_dynamic_template_pattern(template_value)
            if pattern is not None and re.fullmatch(pattern, path):
                return True
    return False


def _i4_repository_digest(repository_root: Path) -> str:
    records: list[bytes] = []
    for path in sorted(repository_root.rglob("*"), key=lambda p: p.relative_to(repository_root).as_posix()):
        rel = path.relative_to(repository_root).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        if path.is_symlink():
            records.append(b"L\0" + rel.encode() + b"\0" + _os.readlink(path).encode() + b"\n")
        elif path.is_file():
            mode = path.stat().st_mode & 0o777
            records.append(
                b"F\0" + rel.encode() + b"\0" + f"{mode:04o}".encode()
                + b"\0" + hashlib.sha256(path.read_bytes()).hexdigest().encode() + b"\n"
            )
    return hashlib.sha256(b"".join(records)).hexdigest()


def _i4_check_request_schema(check, inputs):
    try:
        raw = json.loads(inputs.request.canonical_request_bytes.decode("utf-8"))
    except Exception as exc:
        return _i4_fail(check, "invalid-json", f"canonical request is not valid JSON: {exc}")
    if not isinstance(raw, dict) or raw.get("schema_version") != "1":
        return _i4_fail(check, "schema-mismatch", "canonical request schema mismatch")
    required = {"schema_version", "destination", "authority", "source", "product"}
    missing = sorted(required - set(raw))
    if missing:
        return _i4_fail(check, "missing-field", "canonical request missing fields", missing=missing)
    unknown = sorted(set(raw) - (required | {"profile"}))
    if unknown:
        return _i4_fail(check, "unknown-field", "canonical request unknown fields", unknown=unknown)
    return _i4_pass(check, field_count=len(raw))


def _i4_check_request_canonicalization(check, inputs):
    request = inputs.request
    if not request.destination.startswith("/") or not workspace.inputs.source.repository.startswith("/"):
        return _i4_fail(check, "canonicalization-error", "canonical paths are not absolute")
    canonical = canonical_request_bytes(json.loads(request.canonical_request_bytes.decode("utf-8")))
    if canonical != request.canonical_request_bytes:
        return _i4_fail(check, "canonicalization-error", "carried request bytes are not canonical")
    return _i4_pass(check, request_fingerprint=request.request_fingerprint)


def _i4_check_request_authority(check, inputs):
    granted_by = inputs.request.authority.get("granted_by")
    if granted_by is None:
        return _i4_fail(check, "missing-authority", "authority.granted_by is absent")
    if not isinstance(granted_by, str) or not granted_by.strip():
        return _i4_fail(check, "empty-authority", "authority.granted_by is empty")
    return _i4_pass(check, granted_by=granted_by)


def _i4_check_source_repository(check, inputs):
    source = Path(inputs.source_repository)
    if not source.exists():
        return _i4_fail(check, "path-not-found", "source repository path does not exist")
    if not source.is_dir():
        return _i4_fail(check, "path-not-directory", "source repository path is not a directory")
    if _i4_git(source, "rev-parse", "--git-dir").returncode:
        return _i4_fail(check, "not-a-repository", "source path is not a Git repository")
    return _i4_pass(check, repository=str(source))


def _i4_check_source_object_format(check, inputs):
    proc = _i4_git(inputs.source_repository, "rev-parse", "--show-object-format")
    if proc.returncode or proc.stdout.strip() != "sha1":
        return _i4_fail(check, "unsupported-object-format", "source object format is not sha1")
    return _i4_pass(check, object_format="sha1")


def _i4_check_source_revision(check, inputs):
    proc = _i4_git(inputs.source_repository, "rev-parse", "--verify", f"{inputs.source_revision}^{{commit}}")
    if proc.returncode:
        return _i4_fail(check, "revision-not-found", "source revision unavailable")
    if proc.stdout.strip() != inputs.source_revision:
        return _i4_fail(check, "ambiguous-reference", "resolved source commit differs")
    return _i4_pass(check, commit_id=inputs.source_revision)


def _i4_check_source_objects(check, inputs):
    try:
        manifest = _i4_material_manifest(inputs)
        entries = manifest.get("entries")
        if not isinstance(entries, list):
            return _i4_fail(check, "object-missing", "material entries unavailable")
        for item in entries:
            if not isinstance(item, dict):
                return _i4_fail(check, "object-missing", "invalid material entry")
            if item.get("source_type") == "tree":
                return _i4_fail(check, "tree-type-rejected", "tree-valued source rejected")
            source_path = item.get("source_path")
            if not isinstance(source_path, str):
                return _i4_fail(check, "source-path-not-resolved", "source_path invalid")
            _tree_entry(inputs.source_repository, inputs.source_revision, source_path)
        return _i4_pass(check, source_paths_checked=len(entries))
    except Exception as exc:
        return _i4_fail(check, "source-path-not-resolved", str(exc))


def _i4_check_manifest_schema(check, inputs):
    try:
        parsed = _validate_material_manifest(_i4_material_manifest(inputs), _i4_load_output_inventory())
        return _i4_pass(check, material_entries=len(parsed))
    except _InventoryError as exc:
        text = str(exc)
        if "required field" in text:
            code = "missing-field"
        elif "duplicate" in text:
            code = "duplicate-key"
        elif "unavailable" in text or "not found" in text:
            code = "manifest-not-found"
        elif "schema_version" in text or "unknown" in text:
            code = "schema-mismatch"
        else:
            code = "invalid-entry"
        return _i4_fail(check, code, text)


def _i4_check_manifest_source_paths(check, inputs):
    try:
        parsed = _validate_material_manifest(_i4_material_manifest(inputs), _i4_load_output_inventory())
        for entry in parsed:
            if entry.source_type == "tree":
                return _i4_fail(check, "tree-type-rejected", f"tree source: {entry.source_path}")
            mode, obj_type = _tree_entry(inputs.source_repository, inputs.source_revision, entry.source_path)
            if obj_type != "blob":
                return _i4_fail(check, "source-type-mismatch", f"type mismatch: {entry.source_path}")
            if entry.source_type == "symlink" and mode != "120000":
                return _i4_fail(check, "source-type-mismatch", f"symlink mode mismatch: {entry.source_path}")
        return _i4_pass(check, source_paths_checked=len(parsed))
    except Exception as exc:
        return _i4_fail(check, "source-path-missing", str(exc))


def _i4_check_manifest_key_coverage(check, inputs):
    try:
        parsed = _validate_material_manifest(_i4_material_manifest(inputs), _i4_load_output_inventory())
        output = _i4_load_output_inventory()
        if any(isinstance(item, dict) and item.get("mode") == "040000" for item in output.get("material_index", [])):
            return _i4_fail(check, "tree-valued-entry", "tree-valued material_index entry")
        return _i4_pass(check, material_keys=len(parsed))
    except _InventoryError as exc:
        text = str(exc)
        code = "orphan-material-key" if "unused material_key" in text else "missing-material-key" if "missing from material manifest" in text else "key-mismatch"
        return _i4_fail(check, code, text)


def _i4_check_inventory_complete(check, inputs):
    output = _i4_load_output_inventory()
    expected = _i4_expected_explicit_paths(output)
    observed = _i4_observed_worktree_files(inputs.repository_root)
    missing = sorted(expected - observed)
    if missing:
        return _i4_fail(check, "missing-path", "required inventory paths are absent", missing=missing)
    return _i4_pass(check, explicit_expected=len(expected), observed_files=len(observed))


def _i4_check_no_undeclared(check, inputs):
    output = _i4_load_output_inventory()
    expected = _i4_expected_explicit_paths(output)
    observed = _i4_observed_worktree_files(inputs.repository_root)
    undeclared = sorted(path for path in observed if path not in expected and not _i4_match_dynamic(path, output))
    if undeclared:
        return _i4_fail(check, "undeclared-path", "repository contains undeclared paths", paths=undeclared)
    return _i4_pass(check, observed_files=len(observed))


def _i4_check_level_readmes(check, inputs):
    candidates = sorted(inputs.repository_root.glob("product/specs/product/level-*/README.md"))
    if not candidates:
        return _i4_fail(check, "missing-readme", "no Level workspace README files are present")
    for path in candidates:
        text = path.read_text(encoding="utf-8")
        if path.parent.name not in text and path.parent.name.replace("level-", "Level ") not in text:
            return _i4_fail(check, "content-mismatch", f"Level identity absent: {path}")
    return _i4_pass(check, readmes=len(candidates))


def _i4_check_copied_bytes(check, inputs):
    try:
        manifest = _validate_material_manifest(_i4_material_manifest(inputs), _i4_load_output_inventory())
        output = _i4_load_output_inventory()
        destinations = {
            item["material_key"]: item["destination_path"]
            for item in output.get("material_index", [])
            if isinstance(item, dict) and isinstance(item.get("material_key"), str) and isinstance(item.get("destination_path"), str)
        }
        checked = 0
        for entry in manifest:
            if entry.operation != "copy-verbatim":
                continue
            dest = destinations.get(entry.material_key)
            if dest is None:
                return _i4_fail(check, "material-key-unresolved", f"unresolved key: {entry.material_key}")
            path = inputs.repository_root / dest
            source = _read_commit_blob(inputs.source_repository, inputs.source_revision, entry.source_path)
            actual = _os.readlink(path).encode("utf-8") if path.is_symlink() else path.read_bytes()
            if actual != source:
                return _i4_fail(check, "byte-mismatch", f"copied bytes differ: {dest}")
            checked += 1
        return _i4_pass(check, copied_entries_checked=checked)
    except Exception as exc:
        return _i4_error(check, "source-blob-not-found", str(exc))


def _i4_check_direction_evidence(check, inputs):
    evidence_root = inputs.repository_root / "product/docs/direction/evidence"
    manifest_path = inputs.repository_root / "product/docs/direction/manifest.json"
    if not evidence_root.is_dir() or not manifest_path.is_file():
        return _i4_fail(check, "evidence-missing", "direction evidence root or manifest missing")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return _i4_fail(check, "manifest-entry-mismatch", f"invalid direction manifest: {exc}")
    observed = sorted(p.relative_to(evidence_root).as_posix() for p in evidence_root.rglob("*") if p.is_file())
    text = json.dumps(manifest, sort_keys=True)
    orphan = [p for p in observed if p not in text]
    if orphan:
        return _i4_fail(check, "orphan-evidence", "orphan direction evidence", paths=orphan)
    return _i4_pass(check, evidence_files=len(observed))


def _i4_check_generated_records(check, inputs):
    paths = (
        "product/specs/product/manifest.json",
        "repo/initializer/provenance.json",
        "repo/initializer/handoff.json",
        "product/docs/direction/manifest.json",
    )
    for rel in paths:
        path = inputs.repository_root / rel
        if not path.is_file():
            return _i4_fail(check, "missing-field", f"missing generated record: {rel}")
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return _i4_fail(check, "schema-mismatch", f"invalid generated JSON {rel}: {exc}")
        if not isinstance(raw, dict):
            return _i4_fail(check, "invalid-value", f"generated record is not an object: {rel}")
    return _i4_pass(check, generated_records=list(paths))


def _i4_check_generated_templates(check, inputs):
    inspected = 0
    for path in inputs.repository_root.rglob("*.md"):
        rel = path.relative_to(inputs.repository_root).as_posix()
        if rel.startswith("product/docs/") and (
            "/overview/" in rel or "/decompositions/" in rel or "/plans/" in rel or rel.endswith("/README.md")
        ):
            text = path.read_text(encoding="utf-8")
            if '"lifecycle_status": "accepted"' in text:
                return _i4_fail(check, "incorrect-status", f"generated template accepted instead of candidate: {rel}")
            inspected += 1
    return _i4_pass(check, templates_inspected=inspected)


def _i4_check_digest(check, inputs):
    actual = _i4_repository_digest(inputs.repository_root)
    if not inputs.expected_repository_content_digest:
        return _i4_fail(check, "digest-not-computed", "expected repository digest absent")
    if actual != inputs.expected_repository_content_digest:
        return _i4_fail(check, "digest-mismatch", "repository digest differs", expected=inputs.expected_repository_content_digest, actual=actual)
    return _i4_pass(check, repository_content_digest=actual)


def _i4_check_provenance(check, inputs):
    path = inputs.repository_root / "repo/initializer/provenance.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return _i4_fail(check, "provenance-mismatch", f"cannot read provenance: {exc}")
    granted_by = inputs.request.authority.get("granted_by")
    if raw.get("request_identifier") != granted_by:
        return _i4_fail(check, "authority-propagation-failure", "provenance authority mismatch")
    if inputs.source_revision not in json.dumps(raw, sort_keys=True):
        return _i4_fail(check, "source-revision-mismatch", "provenance source revision mismatch")
    return _i4_pass(check, request_identifier=granted_by)


def _i4_check_handoff(check, inputs):
    path = inputs.repository_root / "repo/initializer/handoff.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return _i4_fail(check, "handoff-mismatch", f"cannot read handoff: {exc}")
    arrays = [value for value in raw.values() if isinstance(value, list) and all(isinstance(v, str) for v in value)]
    seen: set[str] = set()
    for values in arrays:
        if values != sorted(values):
            return _i4_fail(check, "ordering-violation", "handoff array ordering is not lexicographic")
        overlap = seen.intersection(values)
        if overlap:
            return _i4_fail(check, "duplicate-array-entry", "handoff arrays overlap", duplicates=sorted(overlap))
        seen.update(values)
    return _i4_pass(check, classified_paths=len(seen))


def _i4_check_git_branch(check, inputs):
    proc = _i4_git(inputs.repository_root, "symbolic-ref", "--short", "HEAD")
    if proc.returncode:
        return _i4_fail(check, "no-branch", "repository has no active branch")
    branch = proc.stdout.strip()
    if branch != "main":
        return _i4_fail(check, "branch-mismatch", f"expected main, observed {branch}")
    return _i4_pass(check, branch=branch)


def _i4_check_git_roots(check, inputs):
    roots = _i4_git(inputs.repository_root, "rev-list", "--max-parents=0", "HEAD")
    root_ids = [line for line in roots.stdout.splitlines() if line] if roots.returncode == 0 else []
    if len(root_ids) != 1:
        return _i4_fail(check, "wrong-commit-count", "repository does not contain exactly one root commit", root_commits=root_ids)
    return _i4_pass(check, root_commit=root_ids[0])


def _i4_bootstrap_profile() -> dict[str, Any]:
    return json.loads((_i4_repo_root() / "product/specs/product/level-1/git-bootstrap-profile.json").read_text(encoding="utf-8"))


def _i4_profile_constant(raw: dict[str, Any], name: str) -> str:
    text = json.dumps(raw)
    match = re.search(rf'"{re.escape(name)}"\s*:\s*"([^"]*)"', text)
    return match.group(1) if match else ""


def _i4_check_git_author(check, inputs):
    profile = _i4_bootstrap_profile()
    expected_name = _i4_profile_constant(profile, "author_name")
    expected_email = _i4_profile_constant(profile, "author_email")
    proc = _i4_git(inputs.repository_root, "show", "-s", "--format=%an%n%ae", "HEAD")
    if proc.returncode:
        return _i4_error(check, "author-name-mismatch", "cannot inspect commit author")
    lines = proc.stdout.splitlines()
    name = lines[0] if lines else ""
    email = lines[1] if len(lines) > 1 else ""
    if expected_name and name != expected_name:
        return _i4_fail(check, "author-name-mismatch", "author name mismatch", expected=expected_name, actual=name)
    if expected_email and email != expected_email:
        return _i4_fail(check, "author-email-mismatch", "author email mismatch", expected=expected_email, actual=email)
    return _i4_pass(check, author_name=name, author_email=email)


def _i4_check_git_message(check, inputs):
    expected = _i4_profile_constant(_i4_bootstrap_profile(), "commit_message")
    proc = _i4_git(inputs.repository_root, "show", "-s", "--format=%B", "HEAD")
    if proc.returncode:
        return _i4_error(check, "commit-message-mismatch", "cannot inspect commit message")
    actual = proc.stdout.rstrip("\n")
    if expected and actual != expected:
        return _i4_fail(check, "commit-message-mismatch", "commit message mismatch", expected=expected, actual=actual)
    return _i4_pass(check, commit_message=actual)


def _i4_check_git_clean(check, inputs):
    proc = _i4_git(inputs.repository_root, "status", "--porcelain=v1", "--untracked-files=all")
    if proc.returncode:
        return _i4_error(check, "worktree-dirty", "cannot inspect worktree")
    lines = [line for line in proc.stdout.splitlines() if line]
    if any(line.startswith("??") for line in lines):
        return _i4_fail(check, "untracked-files", "worktree contains untracked files", status=lines)
    if lines:
        return _i4_fail(check, "worktree-dirty", "worktree is dirty", status=lines)
    return _i4_pass(check)


def _i4_check_git_remotes(check, inputs):
    proc = _i4_git(inputs.repository_root, "remote")
    remotes = [line for line in proc.stdout.splitlines() if line] if proc.returncode == 0 else []
    if proc.returncode or remotes:
        return _i4_fail(check, "remote-count-mismatch", "repository remote count is not zero", remotes=remotes)
    return _i4_pass(check, remote_count=0)


_I4_CHECK_HANDLERS: dict[str, _Callable] = {
    "request.schema": _i4_check_request_schema,
    "request.canonicalization": _i4_check_request_canonicalization,
    "request.authority-propagation": _i4_check_request_authority,
    "source.repository-local": _i4_check_source_repository,
    "source.object-format": _i4_check_source_object_format,
    "source.revision-commit": _i4_check_source_revision,
    "source.objects-complete": _i4_check_source_objects,
    "material-manifest.schema": _i4_check_manifest_schema,
    "material-manifest.source-paths": _i4_check_manifest_source_paths,
    "material-manifest.key-coverage": _i4_check_manifest_key_coverage,
    "output.inventory-complete": _i4_check_inventory_complete,
    "output.no-undeclared-paths": _i4_check_no_undeclared,
    "output.level-readmes": _i4_check_level_readmes,
    "output.copied-bytes-match": _i4_check_copied_bytes,
    "output.direction-evidence-match": _i4_check_direction_evidence,
    "output.generated-records-valid": _i4_check_generated_records,
    "output.generated-templates-match": _i4_check_generated_templates,
    "output.repository-digest-match": _i4_check_digest,
    "provenance.consistent": _i4_check_provenance,
    "handoff.consistent": _i4_check_handoff,
    "git.initial-branch": _i4_check_git_branch,
    "git.root-commit-count": _i4_check_git_roots,
    "git.author-identity": _i4_check_git_author,
    "git.commit-message": _i4_check_git_message,
    "git.worktree-clean": _i4_check_git_clean,
    "git.remote-count": _i4_check_git_remotes,
}


def validate_repository_v1(inputs: RepositoryValidationInputs) -> RepositoryValidationRun:
    _validate_staging_workspace(inputs.workspace)
    profile_version, profile = load_validation_profile_v1()
    expected_ids = {item.check_id for item in profile}
    if expected_ids != set(_I4_CHECK_HANDLERS):
        raise ValidationError(INVALID_STRUCTURE, "validation implementation/profile mismatch")
    results: list[RepositoryCheckResult] = []
    for check in profile:
        try:
            result = _I4_CHECK_HANDLERS[check.check_id](check, inputs)
        except Exception as exc:
            result = _i4_error(check, check.failure_codes[0], f"{type(exc).__name__}: {exc}")
        if result.status not in _I4_RESULT_STATUSES:
            raise ValidationError(INVALID_STRUCTURE, f"invalid result status for {check.check_id}")
        if result.failure_code is not None and result.failure_code not in check.failure_codes:
            raise ValidationError(INVALID_STRUCTURE, f"invalid failure code for {check.check_id}")
        results.append(result)
    required = {item.check_id for item in profile if item.classification == "required"}
    overall = "pass" if all(item.status == "passed" for item in results if item.check_id in required) else "fail"
    return RepositoryValidationRun(
        profile_version,
        tuple(results),
        overall,
        inputs.request.request_fingerprint,
        inputs.expected_repository_content_digest,
    )


def validate_validation_report_v1(
    report: dict[str, Any],
    *,
    expected_request_fingerprint: str,
    expected_repository_content_digest: str,
) -> None:
    allowed_root = (
        "schema_version",
        "report_version",
        "profile_version",
        "request_fingerprint",
        "repository_content_digest",
        "overall_status",
        "checks",
    )
    if tuple(report) != allowed_root:
        raise ValidationError(INVALID_STRUCTURE, "validation report root field order/closure is invalid")
    if report.get("schema_version") != "1" or report.get("report_version") != "1":
        raise ValidationError(INVALID_STRUCTURE, "validation report version is invalid")
    if report.get("profile_version") != "v1":
        raise ValidationError(INVALID_STRUCTURE, "validation report profile_version is invalid")
    if report.get("request_fingerprint") != expected_request_fingerprint:
        raise ValidationError(INVALID_STRUCTURE, "validation report request_fingerprint linkage mismatch")
    if report.get("repository_content_digest") != expected_repository_content_digest:
        raise ValidationError(INVALID_STRUCTURE, "validation report repository_content_digest linkage mismatch")
    if report.get("overall_status") not in {"pass", "fail"}:
        raise ValidationError(INVALID_STRUCTURE, "validation report overall_status is invalid")

    _version, profile = load_validation_profile_v1()
    checks = report.get("checks")
    if not isinstance(checks, list) or len(checks) != len(profile):
        raise ValidationError(INVALID_STRUCTURE, "validation report must contain exactly one result per profile check")
    by_id = {item.check_id: item for item in profile}
    observed: list[str] = []
    for index, raw in enumerate(checks):
        if not isinstance(raw, dict):
            raise ValidationError(INVALID_STRUCTURE, f"checks[{index}] must be an object")
        allowed_fields = ("check_id", "status", "failure_code", "failure_message", "evidence")
        if any(key not in allowed_fields for key in raw):
            raise ValidationError(INVALID_STRUCTURE, f"checks[{index}] has unknown field")
        present = tuple(key for key in allowed_fields if key in raw)
        if tuple(raw) != present:
            raise ValidationError(INVALID_STRUCTURE, f"checks[{index}] field order is invalid")
        check_id = raw.get("check_id")
        if not isinstance(check_id, str) or check_id not in by_id or check_id in observed:
            raise ValidationError(INVALID_STRUCTURE, f"checks[{index}] check_id is invalid or duplicate")
        observed.append(check_id)
        if raw.get("status") not in _I4_RESULT_STATUSES:
            raise ValidationError(INVALID_STRUCTURE, f"invalid status for {check_id}")
        failure_code = raw.get("failure_code")
        if failure_code is not None and failure_code not in by_id[check_id].failure_codes:
            raise ValidationError(INVALID_STRUCTURE, f"invalid failure_code for {check_id}")
        if "evidence" in raw and not isinstance(raw["evidence"], dict):
            raise ValidationError(INVALID_STRUCTURE, f"evidence must be an object for {check_id}")
    if observed != [item.check_id for item in profile]:
        raise ValidationError(INVALID_STRUCTURE, "validation report checks are not in profile order")
    required = {item.check_id for item in profile if item.classification == "required"}
    computed = "pass" if all(raw["status"] == "passed" for raw in checks if raw["check_id"] in required) else "fail"
    if report["overall_status"] != computed:
        raise ValidationError(INVALID_STRUCTURE, "validation report overall_status mismatch")
