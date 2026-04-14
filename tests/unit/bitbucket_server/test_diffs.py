"""Tests for Bitbucket Server diff operations."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig
from mcp_atlassian.bitbucket_server.diffs import BitbucketServerDiffs


@pytest.fixture
def diff_ops():
    """Create diff operations with mocked client."""
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
        return BitbucketServerDiffs(client)


def _mock_get_response(ops, data):
    mock_response = MagicMock()
    mock_response.json.return_value = data
    mock_response.raise_for_status = MagicMock()
    ops.client.session.get.return_value = mock_response


def test_get_diff(diff_ops):
    """Test get_diff calls correct endpoint with params."""
    _mock_get_response(diff_ops, {"diffs": []})

    result = diff_ops.get_diff("my-repo", 1, "TESTPROJ")

    diff_ops.client.session.get.assert_called_once()
    call_args = diff_ops.client.session.get.call_args
    assert call_args[0][0].endswith("/projects/TESTPROJ/repos/my-repo/pull-requests/1/diff")
    assert call_args[1]["params"] == {"contextLines": 10}
    assert result == {"diffs": []}


def test_get_diff_with_options(diff_ops):
    """Test get_diff passes optional params."""
    _mock_get_response(diff_ops, {"diffs": []})

    diff_ops.get_diff(
        "my-repo", 1, "TESTPROJ",
        context_lines=5, since_revision="abc123", whitespace=True,
    )

    call_args = diff_ops.client.session.get.call_args
    params = call_args[1]["params"]
    assert params["contextLines"] == 5
    assert params["since"] == "abc123"
    assert params["whitespace"] == "ignore-all"
