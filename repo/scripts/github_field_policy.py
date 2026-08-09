#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


class PolicyError(Exception):
    pass


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
SHA_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])")
ISSUE_RE = re.compile(r"(?:https://github\.com/[^\s]+/issues/\d+|#\d+)")
SPEC_RE = re.compile(r"\b(?:repo|product)\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)*\b")
PATH_RE = re.compile(r"\b(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\b")
IMPLEMENTATION_PLAN_RE = re.compile(r"\b(?:repo|product)/docs/plans/[A-Za-z0-9._/-]+-IMPLEMENTATION-PLAN\.md\b")
PRODUCT_ARTIFACT_IMPLEMENTATION_RE = re.compile(r"\bproduct-artifact implementation\b", re.I)
PLAN_SPEC_ROW_RE = re.compile(r"^\|\s*\d+\s*\|\s*`(product\.[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)*)`\s*\|", re.M)
WORKSTREAM_SECTION_RE = re.compile(r"^## (?:B0|I[1-9][0-9]*)\b[^\n]*\n(.*?)(?=^##\s|\Z)", re.M | re.S)

SUPPORTED_VALIDATION_KINDS = {
    "meaningful",
    "issue-link",
    "commit-sha",
    "spec-reference",
    "path-list",
    "numbered-steps",
    "checklist",
    "default-branch-base",
}


def fail(message: str) -> int:
    print(f"policy error: {message}", file=sys.stderr)
    return 1


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        match = SECTION_RE.match(line)
        if match:
            current = match.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def is_placeholder(text: str) -> bool:
    value = normalize(text).lower()
    return value in {"", ".", "n/a", "na", "none", "todo", "tbd", "placeholder", "unchanged placeholder-style text"} or bool(re.fullmatch(r"[._\- ]+", value))


def require_section(sections: dict[str, str], name: str) -> str:
    value = sections.get(name, "")
    if not value:
        raise PolicyError(f"missing section: {name}")
    return value


def require_meaningful(name: str, value: str) -> None:
    if is_placeholder(value):
        raise PolicyError(f"placeholder response in {name}")
    if len(normalize(value)) < 8:
        raise PolicyError(f"too little content in {name}")


def require_sha(name: str, value: str, count: int = 1) -> None:
    matches = SHA_RE.findall(normalize(value).lower())
    if len(matches) != count:
        raise PolicyError(f"expected exactly {count} SHA{'s' if count != 1 else ''} in {name}")


def require_issue_link(name: str, value: str) -> None:
    if not ISSUE_RE.search(normalize(value)):
        raise PolicyError(f"invalid issue linkage in {name}")


def require_spec_reference(name: str, value: str) -> None:
    if not SPEC_RE.search(value):
        raise PolicyError(f"missing specification reference in {name}")


def require_path_list(name: str, value: str) -> None:
    if not PATH_RE.search(value):
        raise PolicyError(f"missing path inventory in {name}")


def require_numbered_steps(name: str, value: str) -> None:
    if not re.search(r"^\s*1\.\s+", value, re.M):
        raise PolicyError(f"missing ordered steps in {name}")


def is_none_response(value: str) -> bool:
    return re.sub(r"[\s\.,:;!?]+$", "", normalize(value).lower()) == "none"


def require_checklist(name: str, value: str, items: list[str]) -> None:
    lines = [normalize(line) for line in value.splitlines()]
    missing = []
    for item in items:
        pattern = rf"-\s*\[[ xX]\]\s+{re.escape(item)}$"
        if not any(re.fullmatch(pattern, line) for line in lines):
            missing.append(item)
    if missing:
        raise PolicyError(f"missing checklist items in {name}: {', '.join(missing)}")


def is_valid_branch_name(branch: str) -> bool:
    if branch in {"", "@", "HEAD"} or branch.startswith(("-", "/")) or branch.endswith(("/", ".")):
        return False
    if ".." in branch or "//" in branch or "@{" in branch:
        return False
    if any(ord(char) < 32 or ord(char) == 127 or char in " ~^:?*[\\" for char in branch):
        return False
    return all(part and not part.startswith(".") and not part.endswith(".lock") for part in branch.split("/"))


def require_default_branch_base(name: str, value: str) -> None:
    match = re.fullmatch(r"([^\s]+) at ([0-9a-fA-F]{7,40})", normalize(value))
    if match is None or not is_valid_branch_name(match.group(1)):
        raise PolicyError(f"invalid default-branch base in {name}")


def load_accepted_product_specs(repo_root: Path) -> set[str]:
    manifest_path = repo_root / "product/specs/product/manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
        entries = manifest["product_specifications"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        raise PolicyError(f"invalid policy source: {manifest_path.relative_to(repo_root)}") from exc
    return {
        entry["spec_id"]
        for entry in entries
        if isinstance(entry, dict) and entry.get("status") == "accepted" and isinstance(entry.get("spec_id"), str)
    }


def read_repo_text(repo_root: Path, relative_path: str) -> str:
    root = repo_root.resolve()
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root)
        return path.read_text()
    except (OSError, ValueError) as exc:
        raise PolicyError(f"invalid policy source: {relative_path}") from exc


def load_document_metadata(text: str, relative_path: str) -> dict:
    match = re.search(r"^## Metadata\s*$\s*^```json\s*$\n(.*?)^```\s*$", text, re.M | re.S)
    if match is None:
        raise PolicyError(f"invalid implementation-plan metadata: {relative_path}")
    try:
        metadata = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise PolicyError(f"invalid implementation-plan metadata: {relative_path}") from exc
    if not isinstance(metadata, dict):
        raise PolicyError(f"invalid implementation-plan metadata: {relative_path}")
    return metadata


def markdown_section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return match.group(1) if match else ""


def load_plan_controlling_spec_sets(repo_root: Path, plan_path: str) -> set[frozenset[str]]:
    plan_text = read_repo_text(repo_root, plan_path)
    metadata = load_document_metadata(plan_text, plan_path)
    if metadata.get("artifact_type") != "implementation-plan" or metadata.get("lifecycle_status") != "accepted":
        raise PolicyError(f"cited implementation plan is not accepted: {plan_path}")

    content_areas = metadata.get("required_content_areas")
    authority_paths = content_areas.get("authority_and_basis") if isinstance(content_areas, dict) else None
    workstream_paths = content_areas.get("workstreams_and_dependencies") if isinstance(content_areas, dict) else None
    if not isinstance(authority_paths, list) or not authority_paths or not all(isinstance(path, str) for path in authority_paths):
        raise PolicyError(f"cited implementation plan lacks canonical authority content: {plan_path}")
    if not isinstance(workstream_paths, list) or not workstream_paths or not all(isinstance(path, str) for path in workstream_paths):
        raise PolicyError(f"cited implementation plan lacks canonical workstream content: {plan_path}")

    plan_specs: set[str] = set()
    for authority_path in authority_paths:
        authority_text = read_repo_text(repo_root, authority_path)
        specification_map = markdown_section(authority_text, "Requirement-to-responsibility map")
        plan_specs.update(PLAN_SPEC_ROW_RE.findall(specification_map))
    if not plan_specs:
        raise PolicyError(f"cited implementation plan lacks controlling product specifications: {plan_path}")

    controlling_sets: set[frozenset[str]] = set()
    for workstream_path in workstream_paths:
        workstream_text = read_repo_text(repo_root, workstream_path)
        for section in WORKSTREAM_SECTION_RE.findall(workstream_text):
            requirements = re.search(r"^Controlling requirements[^:]*:\s*(.*)$", section, re.M)
            if requirements is None:
                continue
            value = requirements.group(1)
            workstream_specs = plan_specs if re.search(r"\ball \d+ accepted specs\b", value) else {
                spec_id for spec_id in SPEC_RE.findall(value) if spec_id.startswith("product.")
            }
            if workstream_specs:
                if not workstream_specs.issubset(plan_specs):
                    raise PolicyError(f"cited implementation plan has workstream specifications outside its authority map: {plan_path}")
                controlling_sets.add(frozenset(workstream_specs))
    if not controlling_sets:
        raise PolicyError(f"cited implementation plan lacks controlling workstream specification sets: {plan_path}")
    return controlling_sets


def require_product_artifact_evidence(sections: dict[str, str], repo_root: Path) -> None:
    change_type = sections.get("Change type", "")
    if not PRODUCT_ARTIFACT_IMPLEMENTATION_RE.search(change_type):
        return

    governing = require_section(sections, "Governing specifications")
    plan_paths = IMPLEMENTATION_PLAN_RE.findall(governing)
    if not plan_paths:
        raise PolicyError("missing canonical implementation-plan citation in Governing specifications")
    if len(set(plan_paths)) != 1:
        raise PolicyError("expected exactly one canonical implementation-plan citation in Governing specifications")

    cited_specs = {
        spec_id
        for spec_id in SPEC_RE.findall(governing)
        if spec_id.startswith("product.") and spec_id != "product.manifest"
    }
    accepted_specs = load_accepted_product_specs(repo_root)
    if not cited_specs or not cited_specs.issubset(accepted_specs):
        raise PolicyError("missing manifest-listed accepted product specification in Governing specifications")
    controlling_sets = load_plan_controlling_spec_sets(repo_root, plan_paths[0])
    if frozenset(cited_specs) not in controlling_sets:
        raise PolicyError("cited product specifications do not match a controlling set in cited implementation plan")

    predecessor = require_section(sections, "Dependencies and predecessor evidence")
    if not ISSUE_RE.search(predecessor) or not SHA_RE.search(predecessor.lower()):
        raise PolicyError("missing predecessor implementation issue and revision evidence")


def validate_field_definition(field: dict, spec_path: str) -> None:
    validation = field.get("validation")
    if validation is None:
        return
    kind = validation.get("kind")
    if kind not in SUPPORTED_VALIDATION_KINDS:
        raise PolicyError(f"unsupported validation kind in {spec_path}: {field.get('label', field.get('id', '<unknown>'))}")
    if kind == "commit-sha":
        count = validation.get("count", 1)
        if not isinstance(count, int) or count < 1:
            raise PolicyError(f"invalid commit-sha count in {spec_path}: {field.get('label', field.get('id', '<unknown>'))}")
    if kind == "checklist":
        items = validation.get("items")
        if not isinstance(items, list) or not items or not all(isinstance(item, str) and item for item in items):
            raise PolicyError(f"invalid checklist items in {spec_path}: {field.get('label', field.get('id', '<unknown>'))}")


def load_fields(repo_root: Path, spec_path: str, collection_key: str) -> list[dict]:
    try:
        spec = json.loads((repo_root / spec_path).read_text())
        fields = spec[collection_key]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        raise PolicyError(f"invalid policy source: {spec_path}") from exc
    for field in fields:
        validate_field_definition(field, spec_path)
    return fields


def validate_field_value(field: dict, value: str) -> None:
    validation = field.get("validation", {"kind": "meaningful"})
    if validation.get("allow_none") and is_none_response(value):
        return

    kind = validation.get("kind", "meaningful")
    if kind == "meaningful":
        require_meaningful(field["label"], value)
    elif kind == "issue-link":
        require_issue_link(field["label"], value)
    elif kind == "commit-sha":
        require_sha(field["label"], value, validation.get("count", 1))
    elif kind == "spec-reference":
        require_spec_reference(field["label"], value)
    elif kind == "path-list":
        require_path_list(field["label"], value)
    elif kind == "numbered-steps":
        require_numbered_steps(field["label"], value)
    elif kind == "checklist":
        require_checklist(field["label"], value, validation["items"])
    elif kind == "default-branch-base":
        require_default_branch_base(field["label"], value)
    else:
        raise PolicyError(f"unsupported validation kind for {field['label']}: {kind}")


def check_issue(body: str, fields: list[dict], repo_root: Path) -> None:
    sections = parse_sections(body)
    for field in fields:
        if field.get("required") is not True:
            continue
        value = require_section(sections, field["label"])
        validate_field_value(field, value)
    require_product_artifact_evidence(sections, repo_root)


def check_pr(body: str, fields: list[dict]) -> None:
    sections = parse_sections(body)
    for field in fields:
        if field.get("required") is not True:
            continue
        value = require_section(sections, field["label"])
        validate_field_value(field, value)


def load_body_from_event(event_path: Path, mode: str) -> str:
    try:
        payload = json.loads(event_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise PolicyError(f"invalid event payload: {event_path}") from exc
    if mode == "issue":
        return payload.get("issue", {}).get("body", "")
    if mode == "pr":
        return payload.get("pull_request", {}).get("body", "")
    raise PolicyError(f"unknown mode: {mode}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root")
    parser.add_argument("--mode", choices=["issue", "pr"], required=True)
    parser.add_argument("--body-file")
    parser.add_argument("--event-path", default=os.environ.get("GITHUB_EVENT_PATH", ""))
    args = parser.parse_args(argv[1:])

    try:
        repo_root = Path(args.repo_root)
        issue_fields = load_fields(repo_root, "repo/specs/repo/governing-issue.json", "issue_fields")
        pr_fields = load_fields(repo_root, "repo/specs/repo/review-proposal.json", "review_fields")

        if args.body_file:
            try:
                body = Path(args.body_file).read_text()
            except OSError as exc:
                raise PolicyError(f"invalid body file: {args.body_file}") from exc
        else:
            event_path = Path(args.event_path)
            body = load_body_from_event(event_path, args.mode)

        if args.mode == "issue":
            check_issue(body, issue_fields, repo_root)
        else:
            check_pr(body, pr_fields)
        return 0
    except PolicyError as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
