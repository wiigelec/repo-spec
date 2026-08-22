from __future__ import annotations

import io
import unittest
from unittest.mock import patch

from initializer import cli
from initializer.full_initialization_actions import build_full_initialization_actions
from initializer.orchestration import FullInitializationActions


class H1CliTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_help_presents_lower_level_request_interface(self):
        with patch("sys.stderr", new_callable=io.StringIO) as err:
            rc = cli.main(["repo-spec-init", "repo-root"])
        text = err.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn("repo-spec-init --request <request.json>", text)
        self.assertNotIn("stage-framework-and-foundations", text)

    # validation-metadata: {"role": "helper"}
    def test_superseded_command_remains_explicitly_unavailable(self):
        with patch("sys.stderr", new_callable=io.StringIO) as err:
            rc = cli.main([
                "repo-spec-init",
                "repo-root",
                "stage-promote-and-git",
                "request.json",
            ])
        self.assertEqual(rc, 1)
        self.assertIn("unavailable", err.getvalue())

    # validation-metadata: {"role": "helper"}
    def test_action_builder_returns_exact_i5_action_bundle(self):
        actions = build_full_initialization_actions(
            "/tmp/framework",
            initialization_timestamp="2026-08-09T23:00:00Z",
        )
        self.assertIsInstance(actions, FullInitializationActions)
        self.assertEqual(len(actions.__dataclass_fields__), 13)


if __name__ == "__main__":
    unittest.main()
