from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from .models import ExecutionContext, ImmutableRequest, InitializerError


MISSING_REQUIRED = "missing-required"
EMPTY_AUTHORITY = "empty-authority"
INVALID_STRUCTURE = "invalid-structure"
CONTRADICTORY_COMBINATION = "contradictory-combination"
EXCLUDED_BEHAVIOR = "excluded-behavior"

ROOT_FIELDS = ("schema_version", "destination", "authority", "source", "product")
KNOWN_ROOT_FIELDS = frozenset((*ROOT_FIELDS, "profile"))
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
    authority = _required_object(raw, "authority", result)
    source = _required_object(raw, "source", result)
    product = _required_object(raw, "product", result)

    if schema_version is not None and schema_version != "1":
        result.add(EXCLUDED_BEHAVIOR, f"unsupported schema version: {schema_version!r}")

    resolved_destination = _resolve_v1_path(destination, cwd, result, "destination")
    canonical_authority = _validate_authority(authority, result)
    canonical_source = _validate_source(source, cwd, result)
    canonical_product = _validate_product(product, result)

    profile: str | None = None
    if "profile" in raw:
        value = raw["profile"]
        if not isinstance(value, str):
            result.add(INVALID_STRUCTURE, "profile must be a string")
        elif value != "standard":
            result.add(EXCLUDED_BEHAVIOR, f"unsupported profile: {value!r}")
        else:
            profile = value

    if not result.is_valid:
        return result, None

    assert schema_version is not None
    assert resolved_destination is not None
    assert canonical_authority is not None
    assert canonical_source is not None
    assert canonical_product is not None
    canonical: dict[str, Any] = {
        "schema_version": schema_version,
        "destination": resolved_destination,
        "authority": canonical_authority,
        "source": canonical_source,
        "product": canonical_product,
    }
    if profile is not None:
        canonical["profile"] = profile
    return result, canonical


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
