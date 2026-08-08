from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from initializer.staging import (
    StagingError,
    enumerate_i2_repository,
    i2_repository_digest_input,
)


class I2RepositoryDigestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def digest(self):
        return i2_repository_digest_input(self.root)

    def test_enumeration_is_repository_relative_and_sorted(self) -> None:
        (self.root / "z").mkdir()
        (self.root / "z/b.txt").write_bytes(b"b")
        (self.root / "a.txt").write_bytes(b"a")
        entries = enumerate_i2_repository(self.root)
        paths = [entry.path for entry in entries]
        self.assertEqual(paths, ["a.txt", "z/", "z/b.txt"])

    def test_digest_input_is_byte_deterministic(self) -> None:
        (self.root / "a.txt").write_bytes(b"a\\r\\n")
        first, first_entries = self.digest()
        second, second_entries = self.digest()
        self.assertEqual(first, second)
        self.assertEqual(first_entries, second_entries)

    def test_file_bytes_change_digest_input(self) -> None:
        path = self.root / "a.txt"
        path.write_bytes(b"one")
        first, _ = self.digest()
        path.write_bytes(b"two")
        second, _ = self.digest()
        self.assertNotEqual(first, second)

    def test_executable_bit_changes_digest_input(self) -> None:
        path = self.root / "tool"
        path.write_bytes(b"#!/bin/sh\\n")
        os.chmod(path, 0o644)
        first, _ = self.digest()
        os.chmod(path, 0o755)
        second, _ = self.digest()
        self.assertNotEqual(first, second)

    def test_timestamps_do_not_change_digest_input(self) -> None:
        path = self.root / "a.txt"
        path.write_bytes(b"same")
        first, _ = self.digest()
        os.utime(path, (1, 1))
        second, _ = self.digest()
        self.assertEqual(first, second)

    def test_symlink_target_participates_in_digest(self) -> None:
        (self.root / "one").write_text("one")
        (self.root / "two").write_text("two")
        link = self.root / "link"
        link.symlink_to("one")
        first, _ = self.digest()
        link.unlink()
        link.symlink_to("two")
        second, _ = self.digest()
        self.assertNotEqual(first, second)

    def test_git_state_is_rejected(self) -> None:
        (self.root / ".git").mkdir()
        with self.assertRaises(StagingError):
            self.digest()

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable")
    def test_special_files_are_rejected(self) -> None:
        fifo = self.root / "pipe"
        os.mkfifo(fifo)
        try:
            with self.assertRaises(StagingError):
                self.digest()
        finally:
            fifo.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
