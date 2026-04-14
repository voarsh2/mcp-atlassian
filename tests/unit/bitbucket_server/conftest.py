"""Test fixtures for Bitbucket Server unit tests."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig


@pytest.fixture
def bitbucket_config_basic():
    """BitbucketServerConfig with basic auth."""
    return BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="testuser",
        api_token="testtoken",
    )


@pytest.fixture
def bitbucket_config_pat():
    """BitbucketServerConfig with personal access token auth."""
    return BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="personal_token",
        personal_token="testpat",
    )


@pytest.fixture
def bitbucket_config_with_filter():
    """BitbucketServerConfig with projects filter."""
    return BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="testuser",
        api_token="testtoken",
        projects_filter="TESTPROJ",
    )


@pytest.fixture
def mock_client(bitbucket_config_basic):
    """Mocked BitbucketServerClient with mocked session."""
    mock_session = MagicMock()
    with patch.object(BitbucketServerClient, "_create_session", return_value=mock_session):
        client = BitbucketServerClient(bitbucket_config_basic)
        yield client
