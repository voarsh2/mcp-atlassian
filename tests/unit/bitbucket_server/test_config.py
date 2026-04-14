"""Tests for the Bitbucket Server config module."""

import os
from unittest.mock import patch

import pytest

from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig


def test_from_env_basic_auth():
    """Test that from_env correctly loads basic auth configuration."""
    with patch.dict(
        os.environ,
        {
            "BITBUCKET_URL": "https://bitbucket.example.com",
            "BITBUCKET_USERNAME": "testuser",
            "BITBUCKET_API_TOKEN": "testtoken",
        },
        clear=True,
    ):
        config = BitbucketServerConfig.from_env()
        assert config.url == "https://bitbucket.example.com"
        assert config.auth_type == "basic"
        assert config.username == "testuser"
        assert config.api_token == "testtoken"
        assert config.personal_token is None
        assert config.ssl_verify is True


def test_from_env_pat_auth():
    """Test that from_env correctly loads personal token auth configuration."""
    with patch.dict(
        os.environ,
        {
            "BITBUCKET_URL": "https://bitbucket.example.com",
            "BITBUCKET_PERSONAL_TOKEN": "testpat",
            "BITBUCKET_SSL_VERIFY": "false",
        },
        clear=True,
    ):
        config = BitbucketServerConfig.from_env()
        assert config.url == "https://bitbucket.example.com"
        assert config.auth_type == "personal_token"
        assert config.personal_token == "testpat"
        assert config.ssl_verify is False


def test_from_env_missing_url():
    """Test that from_env raises ValueError when URL is missing."""
    original_env = os.environ.copy()
    try:
        os.environ.clear()
        with pytest.raises(ValueError, match="BITBUCKET_URL"):
            BitbucketServerConfig.from_env()
    finally:
        os.environ.clear()
        os.environ.update(original_env)


def test_from_env_missing_auth():
    """Test that from_env raises ValueError when no auth credentials found."""
    with patch.dict(
        os.environ,
        {"BITBUCKET_URL": "https://bitbucket.example.com"},
        clear=True,
    ):
        with pytest.raises(ValueError, match="No valid authentication credentials"):
            BitbucketServerConfig.from_env()


def test_is_auth_configured_basic():
    """Test is_auth_configured for basic auth."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="user",
        api_token="token",
    )
    assert config.is_auth_configured() is True


def test_is_auth_configured_pat():
    """Test is_auth_configured for PAT auth."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="personal_token",
        personal_token="pat",
    )
    assert config.is_auth_configured() is True


def test_is_auth_configured_not_configured():
    """Test is_auth_configured returns False when not configured."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username=None,
        api_token=None,
    )
    assert config.is_auth_configured() is False


def test_get_auth_basic():
    """Test get_auth returns tuple for basic auth."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="user",
        api_token="token",
    )
    result = config.get_auth()
    assert result == ("user", "token")


def test_get_auth_pat():
    """Test get_auth returns dict for PAT auth."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="personal_token",
        personal_token="mypat",
    )
    result = config.get_auth()
    assert result == {"Authorization": "Bearer mypat"}


def test_get_auth_unsupported():
    """Test get_auth raises ValueError for unsupported auth type."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="unknown",
    )
    with pytest.raises(ValueError, match="Unsupported auth type"):
        config.get_auth()


def test_projects_filter():
    """Test projects_filter is stored correctly."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="user",
        api_token="token",
        projects_filter="PROJ1,PROJ2",
    )
    assert config.projects_filter == "PROJ1,PROJ2"
