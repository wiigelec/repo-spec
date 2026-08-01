#!/usr/bin/env python3

"""Compatibility wrapper for mutation validation."""

from __future__ import annotations

import sys

from validate_mutations import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
