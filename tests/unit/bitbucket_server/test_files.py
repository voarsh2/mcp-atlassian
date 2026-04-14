"""Tests for Bitbucket Server file operations."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig
from mcp_atlassian.bitbucket_server.files import BitbucketServerFiles
from mcp_atlassian.exceptions import BitbucketServerApiError


@pytest.fixture
def file_ops():
    """Create file operations with mocked client."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="user",
        api_token="token",
        projects_filter="TESTPROJ",
    )
    mock_session = MagicMock()
    with patch.object(BitbucketServerClient, "_create_session", return_value=mock_session):
        client = BitbucketServerClient(config)
        return BitbucketServerFiles(client)


def test_get_file_content(file_ops):
    """Test get_file_content returns raw text."""
    mock_response = MagicMock()
    mock_response.text = "def hello():\n    print('world')"
    mock_response.raise_for_status = MagicMock()
    file_ops.client.session.get.return_value = mock_response

    result = file_ops.get_file_content("my-repo", "src/main.py", "TESTPROJ")

    file_ops.client.session.get.assert_called_once()
    assert result == "def hello():\n    print('world')"


def test_get_file_content_with_at(file_ops):
    """Test get_file_content passes 'at' param for specific branch."""
    mock_response = MagicMock()
    mock_response.text = "content"
    mock_response.raise_for_status = MagicMock()
    file_ops.client.session.get.return_value = mock_response

    file_ops.get_file_content("my-repo", "README.md", "TESTPROJ", at="develop")

    call_kwargs = file_ops.client.session.get.call_args[1]
    assert call_kwargs["params"] == {"at": "develop"}


def test_get_file_content_uses_config_project(file_ops):
    """Test get_file_content uses project from config when not provided."""
    mock_response = MagicMock()
    mock_response.text = "content"
    mock_response.raise_for_status = MagicMock()
    file_ops.client.session.get.return_value = mock_response

    file_ops.get_file_content("my-repo", "README.md")

    call_url = file_ops.client.session.get.call_args[0][0]
    assert "/projects/TESTPROJ/" in call_url


def test_get_file_content_error(file_ops):
    """Test get_file_content raises on failure."""
    import httpx
    error_response = MagicMock()
    error_response.status_code = 404
    error_response.text = "Not found"
    file_ops.client.session.get.side_effect = httpx.HTTPStatusError(
        "Not found", request=MagicMock(), response=error_response
    )

    with pytest.raises(BitbucketServerApiError, match="Failed to get file content"):
        file_ops.get_file_content("my-repo", "missing.py", "TESTPROJ")
