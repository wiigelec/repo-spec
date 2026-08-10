from __future__ import annotations

import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from initializer import cli
from initializer.full_initialization_actions import build_full_initialization_actions
from initializer.orchestration import FullInitializationActions


class H1CliTests(unittest.TestCase):
    def test_human_entry_point_accepts_request_path_without_json_arguments(self):
        raw = {"schema_version": "2", "destination": "/tmp/out"}
        result = SimpleNamespace(
            terminal_result="promoted-success",
            succeeded=True,
        )
        with patch.object(cli, "load_request", return_value=raw) as load, \
             patch.object(cli, "build_full_initialization_actions", return_value=object()), \
             patch.object(cli, "execute_full_initialization", return_value=result) as execute, \
             patch("sys.stdout", new_callable=io.StringIO):
            rc = cli.main(
                ["repo-spec-init", "repo-root", "--request", "request.json"]
            )
        self.assertEqual(rc, 0)
        load.assert_called_once()
        self.assertIs(execute.call_args.args[0], raw)

    def test_help_leads_with_human_request_entry_point(self):
        with patch("sys.stderr", new_callable=io.StringIO) as err:
            rc = cli.main(["repo-spec-init", "repo-root"])
        text = err.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn("repo-spec-init --request <request.json>", text)
        self.assertNotIn("stage-framework-and-foundations", text)
        self.assertNotIn("stage-promote-and-git", text)
        self.assertNotIn("promote-staging", text)

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

    def test_action_builder_returns_exact_i5_action_bundle(self):
        actions = build_full_initialization_actions(
            initialization_timestamp="2026-08-09T23:00:00Z"
        )
        self.assertIsInstance(actions, FullInitializationActions)
        self.assertEqual(
            set(actions.__dataclass_fields__),
            {
                "request_intake", "source_resolution", "destination_preflight",
                "staging_establishment", "framework_installation",
                "direction_evidence_installation", "workspace_seeding",
                "provenance_recording", "handoff_assembly", "git_initialization",
                "repository_validation", "promotion", "success_finalization",
            },
        )


if __name__ == "__main__":
    unittest.main()
