#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
SHA_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])")
ISSUE_RE = re.compile(r"(?:https://github\.com/[^\s]+/issues/\d+|#\d+)")
SPEC_RE = re.compile(r"\b(?:repo|product)\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)*\b")
PATH_RE = re.compile(r"\b(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\b")

ALLOW_NONE = {
    "Open decisions or authority conflicts",
    "Known limitations or questions",
    "Successor work explicitly not authorized",
    "Successor work not included",
    "Generated-artifact effects",
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
        raise ValueError(f"missing section: {name}")
    return value


def require_meaningful(name: str, value: str) -> None:
    if is_placeholder(value):
        raise ValueError(f"placeholder response in {name}")
    if len(normalize(value)) < 8:
        raise ValueError(f"too little content in {name}")


def require_sha(name: str, value: str) -> None:
    matches = SHA_RE.findall(normalize(value).lower())
    if len(matches) != 1:
        raise ValueError(f"expected exactly one SHA in {name}")


def require_issue_link(name: str, value: str) -> None:
    if not ISSUE_RE.search(normalize(value)):
        raise ValueError(f"invalid issue linkage in {name}")


def require_spec_reference(name: str, value: str) -> None:
    if not SPEC_RE.search(value):
        raise ValueError(f"missing specification reference in {name}")


def require_path_list(name: str, value: str) -> None:
    if not PATH_RE.search(value):
        raise ValueError(f"missing path inventory in {name}")


def require_numbered_steps(name: str, value: str) -> None:
    if not re.search(r"^\s*1\.\s+", value, re.M):
        raise ValueError(f"missing ordered steps in {name}")


def load_required_labels(repo_root: Path, spec_path: str, collection_key: str) -> list[str]:
    spec = json.loads((repo_root / spec_path).read_text())
    return [field["label"] for field in spec[collection_key] if field.get("required") is True]


def check_issue(body: str, required_labels: list[str]) -> None:
    sections = parse_sections(body)
    for name in required_labels:
        value = require_section(sections, name)
        if name == "Accepted default-branch base":
            if not re.fullmatch(r"main at [0-9a-f]{7,40}", normalize(value)):
                raise ValueError(f"invalid default-branch base in {name}")
        elif name == "Governing specifications":
            require_spec_reference(name, value)
        elif name == "Ordered patch plan":
            require_numbered_steps(name, value)
        elif name == "Validation plan":
            require_meaningful(name, value)
        elif name == "Dependencies and predecessor evidence":
            require_meaningful(name, value)
        elif name in ALLOW_NONE:
            if normalize(value).lower() == "none":
                continue
            require_meaningful(name, value)
        else:
            require_meaningful(name, value)


def check_pr(body: str, required_labels: list[str]) -> None:
    sections = parse_sections(body)
    for name in required_labels:
        value = require_section(sections, name)
        if name == "Governing issue":
            require_issue_link(name, value)
        elif name in {"Accepted base revision", "Proposed head revision", "Exact revision validated"}:
            require_sha(name, value)
        elif name == "Controlling specifications":
            require_spec_reference(name, value)
        elif name == "Changed-path inventory":
            require_path_list(name, value)
        elif name == "Patch or commit summary":
            require_numbered_steps(name, value)
        elif name == "Validation commands and results":
            require_meaningful(name, value)
        elif name in ALLOW_NONE:
            if normalize(value).lower() == "none":
                continue
            require_meaningful(name, value)
        else:
            require_meaningful(name, value)


def load_body_from_event(event_path: Path, mode: str) -> str:
    payload = json.loads(event_path.read_text())
    if mode == "issue":
        return payload.get("issue", {}).get("body", "")
    if mode == "pr":
        return payload.get("pull_request", {}).get("body", "")
    raise ValueError(f"unknown mode: {mode}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root")
    parser.add_argument("--mode", choices=["issue", "pr"], required=True)
    parser.add_argument("--body-file")
    parser.add_argument("--event-path", default=os.environ.get("GITHUB_EVENT_PATH", ""))
    args = parser.parse_args(argv[1:])

    try:
        repo_root = Path(args.repo_root)
        issue_required_labels = load_required_labels(repo_root, "specs/repo/governing-issue.json", "issue_fields")
        pr_required_labels = load_required_labels(repo_root, "specs/repo/review-proposal.json", "review_fields")

        if args.body_file:
            body = Path(args.body_file).read_text()
        else:
            event_path = Path(args.event_path)
            body = load_body_from_event(event_path, args.mode)

        if args.mode == "issue":
            check_issue(body, issue_required_labels)
        else:
            check_pr(body, pr_required_labels)
        return 0
    except Exception as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
