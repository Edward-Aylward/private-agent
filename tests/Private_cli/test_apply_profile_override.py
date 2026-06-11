"""Regression tests for _apply_profile_override Private_HOME guard (issue #22502).

When Private_HOME is set to the Private root (e.g. systemd hardcodes
Private_HOME=/root/.Private), _apply_profile_override must still read
active_profile and update Private_HOME to the profile directory.

When Private_HOME is already a profile directory (.../profiles/<name>),
_apply_profile_override must trust it and return without re-reading
active_profile (child-process inheritance contract).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path



def _run_apply_profile_override(
    tmp_path, monkeypatch, *, Private_home: str | None, active_profile: str | None,
    argv: list[str] | None = None,
):
    """Run _apply_profile_override in isolation.

    Returns the value of os.environ["Private_HOME"] after the call,
    or None if unset.
    """
    Private_root = tmp_path / ".Private"
    Private_root.mkdir(parents=True, exist_ok=True)

    if active_profile is not None:
        (Private_root / "active_profile").write_text(active_profile)

    if active_profile and active_profile != "default":
        (Private_root / "profiles" / active_profile).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    if Private_home is not None:
        monkeypatch.setenv("Private_HOME", Private_home)
    else:
        monkeypatch.delenv("Private_HOME", raising=False)

    monkeypatch.setattr(sys, "argv", argv or ["Private", "gateway", "start"])

    from Private_cli.main import _apply_profile_override
    _apply_profile_override()

    return os.environ.get("Private_HOME")


class TestApplyProfileOverridePrivateHomeGuard:
    """Regression guard for issue #22502.

    Verifies that Private_HOME pointing to the Private root does NOT suppress
    the active_profile check, while Private_HOME already pointing to a
    profile directory IS trusted as-is.
    """

    def test_Private_home_at_root_with_active_profile_is_redirected(
        self, tmp_path, monkeypatch
    ):
        """Private_HOME=/root/.Private + active_profile=coder must redirect
        Private_HOME to .../profiles/coder.

        Bug scenario from #22502: systemd sets Private_HOME to the Private root
        and the user switches to a profile via `Private profile use`.
        Before the fix, the guard returned early and active_profile was ignored.
        """
        Private_root = tmp_path / ".Private"
        Private_root.mkdir(parents=True, exist_ok=True)

        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            Private_home=str(Private_root),
            active_profile="coder",
        )

        assert result is not None, "Private_HOME must be set after profile redirect"
        assert "profiles" in result, (
            f"Expected Private_HOME to point into profiles/ dir, got: {result!r}"
        )
        assert result.endswith("coder"), (
            f"Expected Private_HOME to end with 'coder', got: {result!r}"
        )

    def test_Private_home_already_profile_dir_is_trusted(self, tmp_path, monkeypatch):
        """Private_HOME=.../profiles/coder must not be overridden even when
        active_profile says something different.

        Preserves the child-process inheritance contract: a subprocess spawned
        with Private_HOME already set to a specific profile must stay in that
        profile.
        """
        Private_root = tmp_path / ".Private"
        profile_dir = Private_root / "profiles" / "coder"
        profile_dir.mkdir(parents=True, exist_ok=True)

        (Private_root / "active_profile").write_text("other")

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("Private_HOME", str(profile_dir))
        monkeypatch.setattr(sys, "argv", ["Private", "gateway", "start"])

        from Private_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("Private_HOME") == str(profile_dir), (
            "Private_HOME must remain unchanged when already pointing to a profile dir"
        )

    def test_Private_home_unset_reads_active_profile(self, tmp_path, monkeypatch):
        """Classic case: Private_HOME unset + active_profile=coder must set
        Private_HOME to the profile directory (existing behaviour must not regress).
        """
        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            Private_home=None,
            active_profile="coder",
        )

        assert result is not None
        assert "coder" in result

    def test_Private_home_unset_default_profile_no_redirect(self, tmp_path, monkeypatch):
        """active_profile=default must not redirect Private_HOME."""
        Private_root = tmp_path / ".Private"
        Private_root.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.delenv("Private_HOME", raising=False)
        monkeypatch.setattr(sys, "argv", ["Private", "gateway", "start"])
        (Private_root / "active_profile").write_text("default")

        from Private_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("Private_HOME") is None

    def test_subcommand_profile_flag_is_not_consumed(self, tmp_path, monkeypatch):
        """Command argv flags named --profile must stay with that command.

        Docker Desktop's MCP Toolkit uses `docker mcp gateway run --profile ...`.
        When that argv is passed through `Private mcp add --args`, the early
        profile pre-parser must not interpret the Docker profile as a Private
        profile.
        """
        Private_root = tmp_path / ".Private"
        Private_root.mkdir(parents=True, exist_ok=True)
        argv = [
            "Private",
            "mcp",
            "add",
            "docker-research",
            "--command",
            "docker",
            "--args",
            "mcp",
            "gateway",
            "run",
            "--profile",
            "research",
        ]

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.delenv("Private_HOME", raising=False)
        monkeypatch.setattr(sys, "argv", list(argv))

        from Private_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("Private_HOME") is None
        assert sys.argv == argv

    def test_profile_after_chat_subcommand_is_still_consumed(self, tmp_path, monkeypatch):
        """Profile flags historically work after normal Private subcommands."""
        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            Private_home=None,
            active_profile="coder",
            argv=["Private", "chat", "-p", "coder", "-q", "hello"],
        )

        assert result is not None
        assert result.endswith("coder")
        assert sys.argv == ["Private", "chat", "-q", "hello"]

    def test_top_level_profile_after_value_flag_is_consumed(self, tmp_path, monkeypatch):
        """Top-level --profile still works after other top-level value flags."""
        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            Private_home=None,
            active_profile="coder",
            argv=["Private", "-m", "gpt-5", "--profile", "coder", "chat"],
        )

        assert result is not None
        assert result.endswith("coder")
        assert sys.argv == ["Private", "-m", "gpt-5", "chat"]

    def test_top_level_profile_after_continue_flag_is_consumed(self, tmp_path, monkeypatch):
        """--continue has an optional value, so a following --profile is a flag."""
        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            Private_home=None,
            active_profile="coder",
            argv=["Private", "--continue", "--profile", "coder"],
        )

        assert result is not None
        assert result.endswith("coder")
        assert sys.argv == ["Private", "--continue"]
