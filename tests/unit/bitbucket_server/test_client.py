"""Tests for the Bitbucket Server client module."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.exceptions import BitbucketServerApiError


def test_client_initialization(bitbucket_config_basic):
    """Test client initializes with correct base URLs."""
    with patch.object(BitbucketServerClient, "_create_session", return_value=MagicMock()):
        client = BitbucketServerClient(bitbucket_config_basic)
        assert client.base_url == "https://bitbucket.example.com/rest/api/latest"
        assert client.root_url == "https://bitbucket.example.com"


def test_client_basic_auth_session(bitbucket_config_basic):
    """Test client session uses basic auth."""
    with patch.object(BitbucketServerClient, "_create_session", return_value=MagicMock()):
        client = BitbucketServerClient(bitbucket_config_basic)
        assert client.config.auth_type == "basic"


def test_client_pat_auth_session(bitbucket_config_pat):
    """Test client session uses PAT auth."""
    with patch.object(BitbucketServerClient, "_create_session", return_value=MagicMock()):
        client = BitbucketServerClient(bitbucket_config_pat)
        assert client.config.auth_type == "personal_token"


def test_get_request(mock_client):
    """Test GET request forwards to session."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"values": []}
    mock_client.session.get.return_value = mock_response

    result = mock_client.get("/projects/TEST/repos/my-repo/pull-requests/1")

    mock_client.session.get.assert_called_once()
    assert result == {"values": []}


def test_get_request_with_params(mock_client):
    """Test GET request with query params."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"values": []}
    mock_client.session.get.return_value = mock_response

    mock_client.get("/projects/TEST/repos/my-repo/branches", params={"start": 0, "limit": 25})

    mock_client.session.get.assert_called_once()
    call_kwargs = mock_client.session.get.call_args
    assert call_kwargs[1]["params"] == {"start": 0, "limit": 25}


def test_post_request(mock_client):
    """Test POST request forwards to session."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 123}
    mock_client.session.post.return_value = mock_response

    result = mock_client.post(
        "/projects/TEST/repos/my-repo/pull-requests/1/comments",
        json={"text": "Hello"},
    )

    mock_client.session.post.assert_called_once()
    assert result == {"id": 123}


def test_post_request_with_params(mock_client):
    """Test POST request with query params."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 123}
    mock_client.session.post.return_value = mock_response

    mock_client.post(
        "/projects/TEST/repos/my-repo/pull-requests/1/decline",
        json={"version": 3},
        params={"version": 3},
    )

    mock_client.session.post.assert_called_once()
    call_kwargs = mock_client.session.post.call_args
    assert call_kwargs[1]["params"] == {"version": 3}
    assert call_kwargs[1]["json"] == {"version": 3}


def test_post_url_request(mock_client):
    """Test POST to full URL."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": []}
    mock_client.session.post.return_value = mock_response

    result = mock_client.post_url(
        "https://bitbucket.example.com/rest/search/latest/search",
        data='{"query": "test"}',
    )

    assert result == {"results": []}


def test_get_http_error(mock_client):
    """Test GET raises error on HTTP failure."""
    error_response = MagicMock()
    error_response.status_code = 404
    error_response.text = "Not found"
    mock_client.session.get.side_effect = httpx.HTTPStatusError(
        "Not found", request=MagicMock(), response=error_response
    )

    with pytest.raises(BitbucketServerApiError):
        mock_client.get("/projects/TEST/repos/my-repo/pull-requests/999")


def test_close(mock_client):
    """Test close closes the session."""
    mock_client.close()
    mock_client.session.close.assert_called_once()
