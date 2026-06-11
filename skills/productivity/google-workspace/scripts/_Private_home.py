"""Resolve Private_HOME for standalone skill scripts.

Skill scripts may run outside the Private process (e.g. system Python,
nix env, CI) where ``Private_constants`` is not importable.  This module
provides the same ``get_Private_home()`` and ``display_Private_home()``
contracts as ``Private_constants`` without requiring it on ``sys.path``.

When ``Private_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``Private_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``Private_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from Private_constants import display_Private_home as display_Private_home
    from Private_constants import get_Private_home as get_Private_home
except (ModuleNotFoundError, ImportError):

    def get_Private_home() -> Path:
        """Return the Private home directory (default: ~/.Private).

        Mirrors ``Private_constants.get_Private_home()``."""
        val = os.environ.get("Private_HOME", "").strip()
        return Path(val) if val else Path.home() / ".Private"

    def display_Private_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``Private_constants.display_Private_home()``."""
        home = get_Private_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
