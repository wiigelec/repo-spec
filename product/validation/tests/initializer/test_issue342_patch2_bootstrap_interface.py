from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "product/scripts"))

from initializer.validation import validate_and_normalize, validate_request


class Issue342Patch2BootstrapInterfaceTests(unittest.TestCase):
    def test_destination_only_v2_request_is_canonical(self) -> None:
        ctx = validate_and_normalize(
            {"schema_version": "2", "destination": "./alpha-repo"},
            "/work",
        )
        request = ctx.request
        self.assertEqual(request.destination, "/work/alpha-repo")
        self.assertEqual(request.repository_name, "alpha-repo")
        self.assertEqual(
            request.canonical_request_bytes,
            b'{"schema_version":"2","destination":"/work/alpha-repo"}',
        )
        self.assertEqual(
            request.request_fingerprint,
            hashlib.sha256(request.canonical_request_bytes).hexdigest(),
        )

    def test_old_bootstrap_fields_are_rejected(self) -> None:
        raw = {
            "schema_version": "2",
            "destination": "/work/alpha",
            "authority": {"granted_by": "issue-342"},
            "source": {},
            "product": {},
            "profile": "standard",
        }
        self.assertFalse(validate_request(raw, "/work").is_valid)

    def test_root_destination_is_rejected(self) -> None:
        self.assertFalse(
            validate_request({"schema_version": "2", "destination": "/"}, "/work").is_valid
        )

    def test_repo_spec_wrapper_and_cli_route_exist(self) -> None:
        wrapper = ROOT / "product/scripts/repo-spec"
        self.assertTrue(wrapper.exists())
        self.assertIn("initializer/cli.py", wrapper.read_text())
        cli = (ROOT / "product/scripts/initializer/cli.py").read_text()
        self.assertIn('argv[2] == "init"', cli)
        self.assertIn('argv[3] == "--repo"', cli)
        self.assertIn('{"schema_version": "2", "destination": destination}', cli)


if __name__ == "__main__":
    unittest.main()
