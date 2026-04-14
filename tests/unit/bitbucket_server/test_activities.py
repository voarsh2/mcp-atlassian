"""Tests for Bitbucket Server activities operations."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server.activities import BitbucketServerActivities
from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig


@pytest.fixture
def activity_ops():
    """Create activities operations with mocked client."""
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
        return BitbucketServerActivities(client)


def test_get_activities(activity_ops):
    """Test get_activities calls correct endpoint."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "values": [
            {"action": "COMMENTED", "comment": {"text": "Nice!"}},
            {"action": "APPROVED"},
        ],
        "isLastPage": True,
    }
    activity_ops.client.session.get.return_value = mock_response

    result = activity_ops.get_activities("my-repo", 1, "TESTPROJ")

    activity_ops.client.session.get.assert_called_once()
    assert len(result["values"]) == 2


def test_get_reviews_filters_approved(activity_ops):
    """Test get_reviews filters for APPROVED/REVIEWED actions."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "values": [
            {"action": "COMMENTED"},
            {"action": "APPROVED"},
            {"action": "REVIEWED"},
            {"action": "OPENED"},
        ],
    }
    activity_ops.client.session.get.return_value = mock_response

    reviews = activity_ops.get_reviews("my-repo", 1, "TESTPROJ")

    assert len(reviews) == 2
    assert all(r["action"] in ["APPROVED", "REVIEWED"] for r in reviews)
