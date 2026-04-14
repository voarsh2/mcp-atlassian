"""Tests for Bitbucket Server branch operations."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.branches import BitbucketServerBranches
from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig


@pytest.fixture
def branch_ops():
    """Create branch operations with mocked client."""
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
        return BitbucketServerBranches(client)


def _mock_get_response(ops, data):
    mock_response = MagicMock()
    mock_response.json.return_value = data
    mock_response.raise_for_status = MagicMock()
    ops.client.session.get.return_value = mock_response


def test_get_branches(branch_ops):
    """Test get_branches calls correct endpoint."""
    _mock_get_response(branch_ops, {"values": [{"displayId": "main"}]})

    result = branch_ops.get_branches("my-repo", "TESTPROJ")

    branch_ops.client.session.get.assert_called_once()
    call_args = branch_ops.client.session.get.call_args
    assert call_args[0][0].endswith("/projects/TESTPROJ/repos/my-repo/branches")
    assert call_args[1]["params"] == {"start": 0, "limit": 25}
    assert len(result["values"]) == 1


def test_get_branches_with_filter(branch_ops):
    """Test get_branches passes filterText."""
    _mock_get_response(branch_ops, {"values": []})

    branch_ops.get_branches("my-repo", "TESTPROJ", filter_text="feature")

    call_args = branch_ops.client.session.get.call_args
    assert call_args[1]["params"]["filterText"] == "feature"


def test_get_branch_commits(branch_ops):
    """Test get_branch_commits calls correct endpoint."""
    _mock_get_response(branch_ops, {"values": [{"id": "abc123"}]})

    result = branch_ops.get_branch_commits("my-repo", "main", "TESTPROJ")

    branch_ops.client.session.get.assert_called_once()
    call_args = branch_ops.client.session.get.call_args
    assert call_args[0][0].endswith("/projects/TESTPROJ/repos/my-repo/commits")
    assert call_args[1]["params"]["until"] == "refs/heads/main"
    assert len(result["values"]) == 1


def test_get_branch_commits_with_ref(branch_ops):
    """Test get_branch_commits handles full ref names."""
    _mock_get_response(branch_ops, {"values": []})

    branch_ops.get_branch_commits("my-repo", "refs/heads/develop", "TESTPROJ")

    call_args = branch_ops.client.session.get.call_args
    assert call_args[1]["params"]["until"] == "refs/heads/develop"
