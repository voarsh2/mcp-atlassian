"""Tests for Bitbucket Server comment operations."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.comments import BitbucketServerComments
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig
from mcp_atlassian.models.bitbucket_server import BitbucketServerComment


@pytest.fixture
def comment_ops():
    """Create comment operations with mocked client."""
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
        return BitbucketServerComments(client)


def _mock_post_response(comment_ops, data):
    """Helper to mock a POST response."""
    mock_response = MagicMock()
    mock_response.json.return_value = data
    mock_response.raise_for_status = MagicMock()
    comment_ops.client.session.post.return_value = mock_response


def test_add_comment(comment_ops):
    """Test add_comment calls correct endpoint with body."""
    _mock_post_response(comment_ops, {
        "id": 100, "version": 1, "text": "Nice work!",
        "createdDate": 1700000000000, "updatedDate": 1700000000000,
        "author": {"id": 1, "name": "user1", "displayName": "User One", "emailAddress": "user@example.com", "active": True},
    })

    result = comment_ops.add_comment("my-repo", 1, "Nice work!", "TESTPROJ")

    comment_ops.client.session.post.assert_called_once()
    call_args = comment_ops.client.session.post.call_args
    assert "/projects/TESTPROJ/repos/my-repo/pull-requests/1/comments" in call_args[0][0]
    assert call_args[1]["json"] == {"text": "Nice work!"}
    assert isinstance(result, BitbucketServerComment)
    assert result.id == 100


def test_add_comment_with_parent(comment_ops):
    """Test add_comment includes parent when specified."""
    _mock_post_response(comment_ops, {
        "id": 101, "version": 1, "text": "Reply",
        "createdDate": 1700000000000, "updatedDate": 1700000000000,
        "author": {}, "parent": {"id": 50},
    })

    result = comment_ops.add_comment("my-repo", 1, "Reply", "TESTPROJ", parent_id=50)

    call_args = comment_ops.client.session.post.call_args
    assert call_args[1]["json"] == {"text": "Reply", "parent": {"id": 50}}
    assert result.parent_id == 50


def test_add_comment_uses_config_project(comment_ops):
    """Test add_comment uses project from config when not provided."""
    _mock_post_response(comment_ops, {
        "id": 102, "version": 1, "text": "OK",
        "createdDate": 1700000000000, "updatedDate": 1700000000000, "author": {},
    })

    comment_ops.add_comment("my-repo", 1, "OK")

    call_args = comment_ops.client.session.post.call_args
    assert "/projects/TESTPROJ/" in call_args[0][0]
