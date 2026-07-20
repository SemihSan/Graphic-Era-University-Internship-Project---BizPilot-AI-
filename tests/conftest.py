"""Pytest configuration: make the repository root importable.

Allows tests to `import app` and `from src... import ...` regardless of the
directory pytest is invoked from.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
