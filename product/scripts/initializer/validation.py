from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ImmutableRequest, InitializerError, ExecutionContext


SUPPORTED_SCHEMA_VERSIONS = {"1"}
KNOWN_FIELDS = {
    "schema_version",
    "destination",
    "authority",
    "source",
    "profile",
    "product",
    "deferred",
    "metadata",
}
KNOWN_AUTHORITY_FIELDS = {"granted_by", "scope"}
KNOWN_SOURCE_FIELDS = {"repository", "revision"}
KNOWN_PRODUCT_FIELDS = {"id", "direction_material"}
REQUIRED_FIELDS = {"schema_version", "destination", "authority"}
OPTIONAL_FIELDS = {"source", "profile", "product", "deferred", "metadata"}


def is_canonical_object_id(value: str) -> bool:
    if len(value) == 40:
        return all(c in "0123456789abcdef" for c in value)
    if len(value) == 64:
        return all(c in "0123456789abcdef" for c in value)
    return False

VALID_PROFILES = {"standard"}


class ValidationError(InitializerError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class ValidationResult:
    def __init__(self) -> None:
        self._errors: list[ValidationError] = []

    def add(self, message: str) -> None:
        self._errors.append(ValidationError(message))

    @property
    def errors(self) -> list[ValidationError]:
        return list(self._errors)

    @property
    def is_valid(self) -> bool:
        return len(self._errors) == 0

    def raise_if_invalid(self) -> None:
        if self._errors:
            raise ValidationError(self._errors[0].message)


def load_request(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in request file: {exc.msg}") from exc
    except OSError as exc:
        raise ValidationError(f"cannot read request file: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValidationError("request must be a JSON object")
    return raw


def validate_request(raw: dict[str, Any]) -> ValidationResult:
    result = ValidationResult()

    _check_unknown_fields(raw, KNOWN_FIELDS, result, "request")
    _check_required_fields(raw, REQUIRED_FIELDS, result)
    _check_field_types(raw, result)
    _check_schema_version(raw.get("schema_version"), result)
    _check_destination(raw.get("destination"), result)
    _check_authority(raw.get("authority"), result)
    _check_source(raw.get("source"), result)
    _check_profile(raw.get("profile"), result)
    _check_product(raw.get("product"), result)
    _check_deferred(raw, result)

    return result


def validate_and_normalize(raw: dict[str, Any]) -> ExecutionContext:
    result = validate_request(raw)
    result.raise_if_invalid()
    request = ImmutableRequest(raw)
    return ExecutionContext(request)


def _check_unknown_fields(
    data: dict[str, Any],
    known: set[str],
    result: ValidationResult,
    context: str,
) -> None:
    for key in data:
        if key not in known:
            result.add(f"unknown field in {context}: {key!r}")


def _check_required_fields(
    data: dict[str, Any],
    required: set[str],
    result: ValidationResult,
) -> None:
    for field in sorted(required):
        if field not in data:
            result.add(f"missing required field: {field!r}")


def _check_field_types(raw: dict[str, Any], result: ValidationResult) -> None:
    if "schema_version" in raw and not isinstance(raw["schema_version"], str):
        result.add("schema_version must be a string")
    if "destination" in raw and not isinstance(raw["destination"], str):
        result.add("destination must be a string")
    if "authority" in raw and not isinstance(raw["authority"], dict):
        result.add("authority must be an object")
    if "source" in raw and not isinstance(raw["source"], dict):
        result.add("source must be an object")
    if "profile" in raw and not isinstance(raw["profile"], str):
        result.add("profile must be a string")
    if "product" in raw and not isinstance(raw["product"], dict):
        result.add("product must be an object")
    if "deferred" in raw and not isinstance(raw["deferred"], list):
        result.add("deferred must be a list")
    if "metadata" in raw and not isinstance(raw["metadata"], dict):
        result.add("metadata must be an object")


def _check_schema_version(version: Any, result: ValidationResult) -> None:
    if version is None:
        return
    if not isinstance(version, str):
        return
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        result.add(f"unsupported schema version: {version!r}")


def _check_destination(dest: Any, result: ValidationResult) -> None:
    if dest is None:
        return
    if not isinstance(dest, str):
        return
    if not dest.strip():
        result.add("destination must not be empty")


def _check_authority(auth: Any, result: ValidationResult) -> None:
    if auth is None:
        return
    if not isinstance(auth, dict):
        return
    _check_unknown_fields(auth, KNOWN_AUTHORITY_FIELDS, result, "authority")
    granted_by = auth.get("granted_by")
    if not granted_by:
        result.add("authority.granted_by is required and must be non-empty")
    elif not isinstance(granted_by, str):
        result.add("authority.granted_by must be a string")
    scope = auth.get("scope")
    if scope is not None and not isinstance(scope, str):
        result.add("authority.scope must be a string")
    if granted_by and isinstance(granted_by, str) and scope and isinstance(scope, str):
        if not scope.strip():
            result.add("authority.scope must not be empty")
    if "granted" in auth and auth["granted"] is False:
        result.add("contradictory authority: authority.granted is false while authority block is present")


def _check_source(source: Any, result: ValidationResult) -> None:
    if source is None:
        return
    if not isinstance(source, dict):
        return
    _check_unknown_fields(source, KNOWN_SOURCE_FIELDS, result, "source")
    repo = source.get("repository")
    rev = source.get("revision")
    if repo is not None and not isinstance(repo, str):
        result.add("source.repository must be a string")
    elif repo is not None and not repo.strip():
        result.add("source.repository must not be empty")
    if rev is not None and not isinstance(rev, str):
        result.add("source.revision must be a string")
    elif rev is not None and is_canonical_object_id(rev):
        pass
    elif rev is not None and not rev.strip():
        result.add("source.revision must not be empty")
    if rev and not repo:
        result.add("contradictory source: revision supplied without repository")
    if repo and not repo.strip():
        result.add("contradictory source: repository reference is empty")
    if rev and not rev.strip():
        result.add("contradictory source: revision reference is empty")


def _check_profile(profile: Any, result: ValidationResult) -> None:
    if profile is None:
        return
    if not isinstance(profile, str):
        return
    if profile not in VALID_PROFILES:
        result.add(f"unsupported profile: {profile!r}")


def _check_product(product: Any, result: ValidationResult) -> None:
    if product is None:
        return
    if not isinstance(product, dict):
        return
    _check_unknown_fields(product, KNOWN_PRODUCT_FIELDS, result, "product")
    pid = product.get("id")
    if pid is not None and not isinstance(pid, str):
        result.add("product.id must be a string")
    elif pid is not None and not pid.strip():
        result.add("product.id must not be empty")
    dm = product.get("direction_material")
    if dm is not None:
        if not isinstance(dm, list):
            result.add("product.direction_material must be a list")
        else:
            for i, item in enumerate(dm):
                if not isinstance(item, str):
                    result.add(f"product.direction_material[{i}] must be a string")
                elif not item.strip():
                    result.add(f"product.direction_material[{i}] must not be empty")


def _check_deferred(raw: dict[str, Any], result: ValidationResult) -> None:
    deferred = raw.get("deferred")
    if deferred is None:
        return
    if not isinstance(deferred, list):
        return
    all_optional = OPTIONAL_FIELDS | set()
    for item in deferred:
        if not isinstance(item, str):
            result.add(f"deferred item must be a string, got {type(item).__name__}")
            continue
        if not item.strip():
            result.add("deferred item must not be empty")
            continue
        if item in REQUIRED_FIELDS:
            result.add(f"required field cannot be deferred: {item!r}")
        elif item not in all_optional:
            result.add(f"unknown field in deferred: {item!r}")


def validate_product_foundation_prerequisites(
    raw: dict[str, Any],
    result: ValidationResult,
) -> None:
    product = raw.get("product")
    if product is None:
        result.add("product block is required for foundation establishment")
        return
    if not isinstance(product, dict):
        result.add("product must be an object")
        return
    pid = product.get("id")
    if not pid:
        result.add("product.id is required and must be non-empty")
    elif not isinstance(pid, str):
        result.add("product.id must be a string")
    dm = product.get("direction_material")
    if not dm:
        result.add("product.direction_material is required and must be non-empty")
    elif not isinstance(dm, list):
        result.add("product.direction_material must be a list")
    else:
        for i, item in enumerate(dm):
            if not isinstance(item, str):
                result.add(f"product.direction_material[{i}] must be a string")
            elif not item.strip():
                result.add(f"product.direction_material[{i}] must not be empty")


def validate_json_request(path: Path) -> int:
    try:
        raw = load_request(path)
    except ValidationError as exc:
        print(f"error: {exc}", file=__import__("sys").stderr)
        return 1
    result = validate_request(raw)
    result.raise_if_invalid()
    ctx = validate_and_normalize(raw)
    print(json.dumps({
        "status": "valid",
        "destination": ctx.request.destination,
        "schema_version": ctx.request.schema_version,
        "authority_granted_by": ctx.request.authority.get("granted_by", ""),
    }, indent=2))
    return 0
