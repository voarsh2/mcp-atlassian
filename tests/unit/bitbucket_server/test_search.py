"""Tests for Bitbucket Server search operations."""

import json
from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig
from mcp_atlassian.bitbucket_server.search import BitbucketServerSearch
from mcp_atlassian.exceptions import BitbucketServerApiError


@pytest.fixture
def search_ops():
    """Create search operations with mocked client."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="user",
        api_token="token",
    )
    mock_session = MagicMock()
    with patch.object(BitbucketServerClient, "_create_session", return_value=mock_session):
        client = BitbucketServerClient(config)
        return BitbucketServerSearch(client, config)


def _mock_post_url_response(ops, data):
    mock_response = MagicMock()
    mock_response.json.return_value = data
    mock_response.raise_for_status = MagicMock()
    ops.client.session.post.return_value = mock_response


def test_search_code(search_ops):
    """Test search_code sends correct request."""
    _mock_post_url_response(search_ops, {"entities": {"code": {"results": []}}})

    result = search_ops.search_code("test query", "TESTPROJ", "my-repo")

    search_ops.client.session.post.assert_called_once()
    call_args = search_ops.client.session.post.call_args
    assert "rest/search/latest/search" in call_args[0][0]
    data = json.loads(call_args[1]["content"])
    assert "project:TESTPROJ" in data["query"]
    assert "repo:my-repo" in data["query"]
    assert "test query" in data["query"]
    assert data["entities"]["code"]["start"] == 1
    assert data["entities"]["code"]["limit"] == 10
    assert result == {"entities": {"code": {"results": []}}}


def test_search_repositories(search_ops):
    """Test search_repositories sends correct request."""
    _mock_post_url_response(search_ops, {"entities": {"repositories": {"results": []}}})

    result = search_ops.search_repositories("my-repo", "TESTPROJ")

    call_args = search_ops.client.session.post.call_args
    data = json.loads(call_args[1]["content"])
    assert data["query"] == "TESTPROJ"
    assert result == {"entities": {"repositories": {"results": []}}}


def test_search_code_error(search_ops):
    """Test search_code raises on failure."""
    search_ops.client.session.post.side_effect = Exception("Search failed")

    with pytest.raises(BitbucketServerApiError, match="Failed to search code"):
        search_ops.search_code("test")
