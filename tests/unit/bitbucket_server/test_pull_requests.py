"""Tests for Bitbucket Server pull request operations."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig
from mcp_atlassian.bitbucket_server.pull_requests import BitbucketServerPullRequests
from mcp_atlassian.models.bitbucket_server import BitbucketServerPullRequest


@pytest.fixture
def pr_ops():
    """Create pull request operations with mocked client."""
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
        return BitbucketServerPullRequests(client)


def _mock_get_response(ops, data):
    mock_response = MagicMock()
    mock_response.json.return_value = data
    mock_response.raise_for_status = MagicMock()
    ops.client.session.get.return_value = mock_response


def test_get_pull_request(pr_ops):
    """Test get_pull_request calls correct endpoint."""
    _mock_get_response(pr_ops, {
        "id": 1, "title": "Test PR", "state": "OPEN",
        "fromRef": {"id": "refs/heads/feature", "displayId": "feature"},
        "toRef": {
            "id": "refs/heads/main", "displayId": "main",
            "repository": {"id": 1, "slug": "my-repo", "name": "My Repo", "project": {"key": "TESTPROJ", "name": "Test"}},
        },
        "author": {"id": 1, "name": "user1", "displayName": "User One", "emailAddress": "user@example.com", "active": True},
        "reviewers": [],
    })

    result = pr_ops.get_pull_request("my-repo", 1, "TESTPROJ")

    pr_ops.client.session.get.assert_called_once()
    assert isinstance(result, BitbucketServerPullRequest)
    assert result.id == 1
    assert result.title == "Test PR"


def test_get_pull_request_uses_config_project(pr_ops):
    """Test get_pull_request uses project from config when not provided."""
    _mock_get_response(pr_ops, {
        "id": 1, "title": "PR", "state": "OPEN",
        "fromRef": {}, "toRef": {"repository": {}},
        "author": {}, "reviewers": [],
    })

    pr_ops.get_pull_request("my-repo", 1)

    pr_ops.client.session.get.assert_called_once()
    call_url = pr_ops.client.session.get.call_args[0][0]
    assert "/projects/TESTPROJ/" in call_url


def test_get_pull_request_missing_project():
    """Test get_pull_request raises when no project available."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="user",
        api_token="token",
    )
    mock_session = MagicMock()
    with patch.object(BitbucketServerClient, "_create_session", return_value=mock_session):
        client = BitbucketServerClient(config)
        ops = BitbucketServerPullRequests(client)

        with pytest.raises(ValueError, match="Project parameter is required"):
            ops.get_pull_request("my-repo", 1)
