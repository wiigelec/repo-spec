from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from initializer.destination import DestinationError, i1_destination_preflight


class I1DestinationPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.base = Path(self.td.name)

    def tearDown(self) -> None:
        self.td.cleanup()

    def test_allows_absent_destination_without_creating_anything(self) -> None:
        destination = self.base / "new-repository"
        before = set(self.base.iterdir())
        result = i1_destination_preflight(str(destination))
        after = set(self.base.iterdir())
        self.assertEqual(result["decision"], "allowed")
        self.assertEqual(result["destination_state"], "absent")
        self.assertTrue(result["same_filesystem"])
        self.assertEqual(before, after)
        self.assertFalse(destination.exists())

    def test_rejects_every_existing_destination_type(self) -> None:
        regular = self.base / "regular"
        regular.write_text("x")
        empty = self.base / "empty"
        empty.mkdir()
        nonempty = self.base / "nonempty"
        nonempty.mkdir()
        (nonempty / "x").write_text("x")
        target = self.base / "target"
        target.write_text("x")
        link = self.base / "link"
        link.symlink_to(target)
        for path in (regular, empty, nonempty, link):
            with self.subTest(path=path.name):
                with self.assertRaisesRegex(DestinationError, "already exists"):
                    i1_destination_preflight(str(path))

    def test_rejects_missing_or_inaccessible_parent(self) -> None:
        with self.assertRaisesRegex(DestinationError, "parent is inaccessible"):
            i1_destination_preflight(str(self.base / "missing" / "dest"))
        with mock.patch("initializer.destination.os.access", return_value=False):
            with self.assertRaisesRegex(DestinationError, "parent is inaccessible"):
                i1_destination_preflight(str(self.base / "dest"))

    def test_rejects_non_absolute_destination(self) -> None:
        with self.assertRaisesRegex(DestinationError, "intake-resolved absolute"):
            i1_destination_preflight("relative/dest")


if __name__ == "__main__":
    unittest.main()
