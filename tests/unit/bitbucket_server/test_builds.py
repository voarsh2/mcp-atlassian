"""Tests for Bitbucket Server build status operations."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.builds import BitbucketServerBuilds
from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig
from mcp_atlassian.exceptions import BitbucketServerApiError


@pytest.fixture
def build_ops():
    """Create build status operations with mocked client."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="user",
        api_token="token",
    )
    mock_session = MagicMock()
    with patch.object(BitbucketServerClient, "_create_session", return_value=mock_session):
        client = BitbucketServerClient(config)
        return BitbucketServerBuilds(client)


def test_get_build_status(build_ops):
    """Test get_build_status calls correct endpoint."""
    mock_response = MagicMock()
    mock_response.json.return_value = [{"state": "SUCCESSFUL", "key": "ci-1"}]
    mock_response.raise_for_status = MagicMock()
    build_ops.client.session.get.return_value = mock_response

    result = build_ops.get_build_status("abc123")

    build_ops.client.session.get.assert_called_once()
    call_url = build_ops.client.session.get.call_args[0][0]
    assert "rest/build-status/1.0/commits/abc123" in call_url
    assert result == [{"state": "SUCCESSFUL", "key": "ci-1"}]


def test_get_build_status_error(build_ops):
    """Test get_build_status raises on failure."""
    import httpx
    error_response = MagicMock()
    error_response.status_code = 500
    error_response.text = "Server error"
    build_ops.client.session.get.side_effect = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=error_response
    )

    with pytest.raises(BitbucketServerApiError, match="Failed to get build status"):
        build_ops.get_build_status("abc123")
