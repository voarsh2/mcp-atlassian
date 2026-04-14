"""Tests for Bitbucket Server commit operations."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.commits import BitbucketServerCommits
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig


@pytest.fixture
def commit_ops():
    """Create commit operations with mocked client."""
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
        return BitbucketServerCommits(client)


def _mock_get_response(ops, data):
    mock_response = MagicMock()
    mock_response.json.return_value = data
    mock_response.raise_for_status = MagicMock()
    ops.client.session.get.return_value = mock_response


def test_get_commit(commit_ops):
    """Test get_commit calls correct endpoint."""
    _mock_get_response(commit_ops, {"id": "abc123", "message": "Fix bug"})

    result = commit_ops.get_commit("my-repo", "abc123", "TESTPROJ")

    commit_ops.client.session.get.assert_called_once()
    call_url = commit_ops.client.session.get.call_args[0][0]
    assert call_url.endswith("/projects/TESTPROJ/repos/my-repo/commits/abc123")
    assert result["id"] == "abc123"


def test_get_commit_changes(commit_ops):
    """Test get_commit_changes calls correct endpoint."""
    _mock_get_response(commit_ops, {"changes": [{"path": "src/main.py"}]})

    result = commit_ops.get_commit_changes("my-repo", "abc123", "TESTPROJ")

    commit_ops.client.session.get.assert_called_once()
    call_url = commit_ops.client.session.get.call_args[0][0]
    assert call_url.endswith("/projects/TESTPROJ/repos/my-repo/commits/abc123/changes")
    assert len(result["changes"]) == 1
