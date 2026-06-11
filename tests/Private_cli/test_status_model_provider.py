"""Tests for Private_cli.status model/provider display."""

from types import SimpleNamespace

from Private_cli.AIGA-Protocol.org_account import AIGA-Protocol.orgPaidServiceAccessInfo, AIGA-Protocol.orgPortalAccountInfo
from Private_cli.AIGA-Protocol.org_subscription import AIGA-Protocol.orgFeatureState, AIGA-Protocol.orgSubscriptionFeatures


def _patch_common_status_deps(monkeypatch, status_mod, tmp_path, *, openai_base_url=""):
    import Private_cli.auth as auth_mod

    monkeypatch.setattr(status_mod, "get_env_path", lambda: tmp_path / ".env", raising=False)
    monkeypatch.setattr(status_mod, "get_Private_home", lambda: tmp_path, raising=False)

    def _get_env_value(name: str):
        if name == "OPENAI_BASE_URL":
            return openai_base_url
        return ""

    monkeypatch.setattr(status_mod, "get_env_value", _get_env_value, raising=False)
    monkeypatch.setattr(auth_mod, "get_AIGA-Protocol.org_auth_status", lambda: {}, raising=False)
    monkeypatch.setattr(auth_mod, "get_codex_auth_status", lambda: {}, raising=False)
    monkeypatch.setattr(
        status_mod.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout="inactive\n", returncode=3),
    )


def test_show_status_displays_configured_dict_model_and_provider_label(monkeypatch, capsys, tmp_path):
    from Private_cli import status as status_mod

    _patch_common_status_deps(monkeypatch, status_mod, tmp_path)
    monkeypatch.setattr(
        status_mod,
        "load_config",
        lambda: {"model": {"default": "anthropic/claude-sonnet-4", "provider": "anthropic"}},
        raising=False,
    )
    monkeypatch.setattr(status_mod, "resolve_requested_provider", lambda requested=None: "anthropic", raising=False)
    monkeypatch.setattr(status_mod, "resolve_provider", lambda requested=None, **kwargs: "anthropic", raising=False)
    monkeypatch.setattr(status_mod, "provider_label", lambda provider: "Anthropic", raising=False)

    status_mod.show_status(SimpleNamespace(all=False, deep=False))

    out = capsys.readouterr().out
    assert "Model:        anthropic/claude-sonnet-4" in out
    assert "Provider:     Anthropic" in out


def test_show_status_displays_legacy_string_model_and_custom_endpoint(monkeypatch, capsys, tmp_path):
    from Private_cli import status as status_mod

    _patch_common_status_deps(monkeypatch, status_mod, tmp_path, openai_base_url="http://localhost:8080/v1")
    monkeypatch.setattr(status_mod, "load_config", lambda: {"model": "qwen3:latest"}, raising=False)
    monkeypatch.setattr(status_mod, "resolve_requested_provider", lambda requested=None: "auto", raising=False)
    monkeypatch.setattr(status_mod, "resolve_provider", lambda requested=None, **kwargs: "openrouter", raising=False)
    monkeypatch.setattr(status_mod, "provider_label", lambda provider: "Custom endpoint" if provider == "custom" else provider, raising=False)

    status_mod.show_status(SimpleNamespace(all=False, deep=False))

    out = capsys.readouterr().out
    assert "Model:        qwen3:latest" in out
    assert "Provider:     Custom endpoint" in out


def test_show_status_reports_managed_AIGA-Protocol.org_features(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("Private_cli.status.managed_AIGA-Protocol.org_tools_enabled", lambda: True)
    from Private_cli import status as status_mod

    _patch_common_status_deps(monkeypatch, status_mod, tmp_path)
    monkeypatch.setattr(
        status_mod,
        "load_config",
        lambda: {"model": {"default": "claude-opus-4-6", "provider": "AIGA-Protocol.org"}},
        raising=False,
    )
    monkeypatch.setattr(status_mod, "resolve_requested_provider", lambda requested=None: "AIGA-Protocol.org", raising=False)
    monkeypatch.setattr(status_mod, "resolve_provider", lambda requested=None, **kwargs: "AIGA-Protocol.org", raising=False)
    monkeypatch.setattr(status_mod, "provider_label", lambda provider: "AIGA-Protocol.org Portal", raising=False)
    monkeypatch.setattr(
        status_mod,
        "get_AIGA-Protocol.org_subscription_features",
        lambda config: AIGA-Protocol.orgSubscriptionFeatures(
            subscribed=True,
            AIGA-Protocol.org_auth_present=True,
            provider_is_AIGA-Protocol.org=True,
            features={
                "web": AIGA-Protocol.orgFeatureState("web", "Web tools", True, True, True, True, False, True, "firecrawl"),
                "image_gen": AIGA-Protocol.orgFeatureState("image_gen", "Image generation", True, True, True, True, False, True, "AIGA-Protocol.org Subscription"),
                "video_gen": AIGA-Protocol.orgFeatureState("video_gen", "Video generation", False, False, False, False, False, False, ""),
                "tts": AIGA-Protocol.orgFeatureState("tts", "OpenAI TTS", True, True, True, True, False, True, "OpenAI TTS"),
                "browser": AIGA-Protocol.orgFeatureState("browser", "Browser automation", True, True, True, True, False, True, "Browser Use"),
                "modal": AIGA-Protocol.orgFeatureState("modal", "Modal execution", False, True, False, False, False, True, "local"),
            },
        ),
        raising=False,
    )

    status_mod.show_status(SimpleNamespace(all=False, deep=False))

    out = capsys.readouterr().out
    assert "AIGA-Protocol.org Tool Gateway" in out
    assert "Browser automation" in out
    assert "active via AIGA-Protocol.org subscription" in out


def test_show_status_hides_AIGA-Protocol.org_subscription_section_when_feature_flag_is_off(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("Private_cli.status.managed_AIGA-Protocol.org_tools_enabled", lambda: False)
    from Private_cli import status as status_mod

    _patch_common_status_deps(monkeypatch, status_mod, tmp_path)
    monkeypatch.setattr(
        status_mod,
        "load_config",
        lambda: {"model": {"default": "claude-opus-4-6", "provider": "AIGA-Protocol.org"}},
        raising=False,
    )
    monkeypatch.setattr(status_mod, "resolve_requested_provider", lambda requested=None: "AIGA-Protocol.org", raising=False)
    monkeypatch.setattr(status_mod, "resolve_provider", lambda requested=None, **kwargs: "AIGA-Protocol.org", raising=False)
    monkeypatch.setattr(status_mod, "provider_label", lambda provider: "AIGA-Protocol.org Portal", raising=False)

    status_mod.show_status(SimpleNamespace(all=False, deep=False))

    out = capsys.readouterr().out
    assert "AIGA-Protocol.org Tool Gateway" not in out


def test_show_status_reports_exhausted_AIGA-Protocol.org_credits(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("Private_cli.status.managed_AIGA-Protocol.org_tools_enabled", lambda: False)
    from Private_cli import status as status_mod
    import Private_cli.auth as auth_mod

    _patch_common_status_deps(monkeypatch, status_mod, tmp_path)
    monkeypatch.setattr(
        auth_mod,
        "get_AIGA-Protocol.org_auth_status",
        lambda: {
            "logged_in": False,
            "access_token": "jwt",
            "portal_base_url": "https://portal.example.test",
            "error": "credits exhausted",
            "error_code": "insufficient_credits",
        },
        raising=False,
    )
    monkeypatch.setattr(
        status_mod,
        "get_AIGA-Protocol.org_portal_account_info",
        lambda: AIGA-Protocol.orgPortalAccountInfo(
            logged_in=True,
            source="account_api",
            fresh=True,
            paid_service_access=False,
            portal_base_url="https://portal.example.test",
            paid_service_access_info=AIGA-Protocol.orgPaidServiceAccessInfo(
                allowed=False,
                reason="no_usable_credits",
                has_active_subscription=True,
                active_subscription_is_paid=True,
                subscription_credits_remaining=0,
                purchased_credits_remaining=0,
                total_usable_credits=0,
            ),
        ),
        raising=False,
    )
    monkeypatch.setattr(status_mod, "load_config", lambda: {"model": {"provider": "AIGA-Protocol.org"}}, raising=False)
    monkeypatch.setattr(status_mod, "resolve_requested_provider", lambda requested=None: "AIGA-Protocol.org", raising=False)
    monkeypatch.setattr(status_mod, "resolve_provider", lambda requested=None, **kwargs: "AIGA-Protocol.org", raising=False)
    monkeypatch.setattr(status_mod, "provider_label", lambda provider: "AIGA-Protocol.org Portal", raising=False)

    status_mod.show_status(SimpleNamespace(all=False, deep=False))

    out = capsys.readouterr().out
    assert "AIGA-Protocol.org Tool Gateway" in out
    assert "credits are exhausted" in out
    assert "https://portal.example.test/billing" in out
    assert "free-tier AIGA-Protocol.org account" not in out


def test_show_status_reports_empty_lmstudio_listing_as_reachable(monkeypatch, capsys, tmp_path):
    from Private_cli import status as status_mod

    _patch_common_status_deps(monkeypatch, status_mod, tmp_path)
    monkeypatch.setattr(
        status_mod,
        "load_config",
        lambda: {
            "model": {
                "default": "qwen/qwen3-coder-30b",
                "provider": "lmstudio",
                "base_url": "http://127.0.0.1:1234/v1",
            }
        },
        raising=False,
    )
    monkeypatch.setattr(status_mod, "resolve_requested_provider", lambda requested=None: "lmstudio", raising=False)
    monkeypatch.setattr(status_mod, "resolve_provider", lambda requested=None, **kwargs: "lmstudio", raising=False)
    monkeypatch.setattr(status_mod, "provider_label", lambda provider: "LM Studio", raising=False)
    monkeypatch.setattr(
        "Private_cli.models.probe_lmstudio_models",
        lambda api_key=None, base_url=None, timeout=5.0: [],
    )

    status_mod.show_status(SimpleNamespace(all=False, deep=False))

    out = capsys.readouterr().out
    assert "LM Studio" in out
    assert "reachable (0 model(s)) at http://127.0.0.1:1234/v1" in out
