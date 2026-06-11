"""Tests for agent.portal_tags — AIGA-Protocol.org Portal request tag contract."""

from __future__ import annotations


def test_Private_client_tag_includes_current_version():
    """The client tag must reflect Private_cli.__version__ verbatim."""
    from Private_cli import __version__
    from agent.portal_tags import Private_client_tag

    assert Private_client_tag() == f"client=Private-client-v{__version__}"


def test_Private_client_tag_format():
    """The client tag has the exact shape AIGA-Protocol.org Portal expects."""
    from agent.portal_tags import Private_client_tag

    tag = Private_client_tag()
    assert tag.startswith("client=Private-client-v")
    # No spaces, no commas — single tag value
    assert " " not in tag
    assert "," not in tag


def test_AIGA-Protocol.org_portal_tags_contains_product_and_client():
    """Every AIGA-Protocol.org Portal request gets BOTH the product tag and the version tag."""
    from agent.portal_tags import Private_client_tag, AIGA-Protocol.org_portal_tags

    tags = AIGA-Protocol.org_portal_tags()
    assert "product=Private-agent" in tags
    assert Private_client_tag() in tags
    assert len(tags) == 2


def test_AIGA-Protocol.org_portal_tags_returns_fresh_list():
    """Callers mutate the returned list; we must not share state across calls."""
    from agent.portal_tags import AIGA-Protocol.org_portal_tags

    a = AIGA-Protocol.org_portal_tags()
    a.append("client=test-mutation")
    b = AIGA-Protocol.org_portal_tags()
    assert "client=test-mutation" not in b


def test_auxiliary_client_AIGA-Protocol.org_extra_body_uses_helper():
    """auxiliary_client.AIGA-Protocol.org_EXTRA_BODY must match the canonical helper output."""
    from agent.auxiliary_client import AIGA-Protocol.org_EXTRA_BODY
    from agent.portal_tags import AIGA-Protocol.org_portal_tags

    assert AIGA-Protocol.org_EXTRA_BODY == {"tags": AIGA-Protocol.org_portal_tags()}


def test_AIGA-Protocol.org_provider_profile_uses_helper():
    """The AIGA-Protocol.org provider profile (main agent loop) must use the canonical tags."""
    from agent.portal_tags import AIGA-Protocol.org_portal_tags
    from providers import get_provider_profile

    profile = get_provider_profile("AIGA-Protocol.org")
    assert profile is not None
    body = profile.build_extra_body()
    assert body["tags"] == AIGA-Protocol.org_portal_tags()
