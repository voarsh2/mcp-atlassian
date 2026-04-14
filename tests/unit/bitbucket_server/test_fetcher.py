"""Tests for the Bitbucket Server fetcher module."""

from unittest.mock import MagicMock, patch

import pytest

from mcp_atlassian.bitbucket_server import BitbucketServerFetcher
from mcp_atlassian.bitbucket_server.client import BitbucketServerClient
from mcp_atlassian.bitbucket_server.config import BitbucketServerConfig


@pytest.fixture
def mock_fetcher():
    """Create a BitbucketServerFetcher with mocked operation classes."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="testuser",
        api_token="testtoken",
        projects_filter="TESTPROJ",
    )
    mock_session = MagicMock()
    with patch.object(BitbucketServerClient, "_create_session", return_value=mock_session):
        fetcher = BitbucketServerFetcher(config)
        # Replace operation instances with mocks
        fetcher.pull_requests = MagicMock()
        fetcher.comments = MagicMock()
        fetcher.diffs = MagicMock()
        fetcher.activities = MagicMock()
        fetcher.search = MagicMock()
        fetcher.files = MagicMock()
        fetcher.branches = MagicMock()
        fetcher.builds = MagicMock()
        fetcher.commits = MagicMock()
        yield fetcher


def test_fetcher_initialization():
    """Test fetcher initializes all operation classes."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="testuser",
        api_token="testtoken",
    )
    mock_session = MagicMock()
    with patch.object(BitbucketServerClient, "_create_session", return_value=mock_session):
        fetcher = BitbucketServerFetcher(config)
    assert fetcher.pull_requests is not None
    assert fetcher.comments is not None
    assert fetcher.diffs is not None
    assert fetcher.activities is not None
    assert fetcher.search is not None
    assert fetcher.files is not None
    assert fetcher.branches is not None
    assert fetcher.builds is not None
    assert fetcher.commits is not None


def test_fetcher_get_pull_request(mock_fetcher):
    """Test fetcher delegates to pull_requests."""
    mock_pr = MagicMock()
    mock_fetcher.pull_requests.get_pull_request.return_value = mock_pr

    result = mock_fetcher.get_pull_request("my-repo", 1, "TESTPROJ")

    mock_fetcher.pull_requests.get_pull_request.assert_called_once_with(
        repository="my-repo", pr_id=1, project="TESTPROJ"
    )
    assert result is mock_pr


def test_fetcher_add_comment(mock_fetcher):
    """Test fetcher delegates to comments."""
    mock_comment = MagicMock()
    mock_fetcher.comments.add_comment.return_value = mock_comment

    result = mock_fetcher.add_comment("my-repo", 1, "Nice work!", "TESTPROJ")

    mock_fetcher.comments.add_comment.assert_called_once_with(
        repository="my-repo", pr_id=1, text="Nice work!", project="TESTPROJ", parent_id=None
    )
    assert result is mock_comment


def test_fetcher_get_diff(mock_fetcher):
    """Test fetcher delegates to diffs."""
    mock_diff = {"diffs": []}
    mock_fetcher.diffs.get_diff.return_value = mock_diff

    result = mock_fetcher.get_diff("my-repo", 1, "TESTPROJ")

    mock_fetcher.diffs.get_diff.assert_called_once_with(
        repository="my-repo", pr_id=1, project="TESTPROJ",
        context_lines=10, since_revision=None, whitespace=False,
    )
    assert result == mock_diff


def test_fetcher_get_reviews(mock_fetcher):
    """Test fetcher delegates to activities."""
    mock_reviews = [{"action": "APPROVED"}]
    mock_fetcher.activities.get_reviews.return_value = mock_reviews

    result = mock_fetcher.get_reviews("my-repo", 1, "TESTPROJ")

    mock_fetcher.activities.get_reviews.assert_called_once_with(
        repository="my-repo", pr_id=1, project="TESTPROJ", start=0, limit=25
    )
    assert result == mock_reviews


def test_fetcher_get_activities(mock_fetcher):
    """Test fetcher delegates to activities."""
    mock_activities = {"values": []}
    mock_fetcher.activities.get_activities.return_value = mock_activities

    result = mock_fetcher.get_activities("my-repo", 1, "TESTPROJ")

    mock_fetcher.activities.get_activities.assert_called_once_with(
        repository="my-repo", pr_id=1, project="TESTPROJ", start=0, limit=25
    )
    assert result == mock_activities


def test_fetcher_search_code(mock_fetcher):
    """Test fetcher delegates to search."""
    mock_results = {"entities": {}}
    mock_fetcher.search.search_code.return_value = mock_results

    result = mock_fetcher.search_code("test query", "TESTPROJ", "my-repo")

    mock_fetcher.search.search_code.assert_called_once_with(
        query="test query", project_key="TESTPROJ", repository_slug="my-repo",
        page=1, limit=10,
    )
    assert result == mock_results


def test_fetcher_search_repositories(mock_fetcher):
    """Test fetcher delegates to search."""
    mock_results = {"entities": {}}
    mock_fetcher.search.search_repositories.return_value = mock_results

    result = mock_fetcher.search_repositories("my-repo", "TESTPROJ")

    mock_fetcher.search.search_repositories.assert_called_once_with(
        query="my-repo", project_key="TESTPROJ", page=1, limit=10,
    )
    assert result == mock_results


def test_fetcher_get_file_content(mock_fetcher):
    """Test fetcher delegates to files."""
    mock_fetcher.files.get_file_content.return_value = "file content"

    result = mock_fetcher.get_file_content("my-repo", "src/main.py", "TESTPROJ")

    mock_fetcher.files.get_file_content.assert_called_once_with(
        repository="my-repo", file_path="src/main.py", project="TESTPROJ", at=None
    )
    assert result == "file content"


def test_fetcher_get_branches(mock_fetcher):
    """Test fetcher delegates to branches."""
    mock_branches = {"values": []}
    mock_fetcher.branches.get_branches.return_value = mock_branches

    result = mock_fetcher.get_branches("my-repo", "TESTPROJ")

    mock_fetcher.branches.get_branches.assert_called_once_with(
        repository="my-repo", project="TESTPROJ", filter_text=None, start=0, limit=25
    )
    assert result == mock_branches


def test_fetcher_get_branch_commits(mock_fetcher):
    """Test fetcher delegates to branches."""
    mock_commits = {"values": []}
    mock_fetcher.branches.get_branch_commits.return_value = mock_commits

    result = mock_fetcher.get_branch_commits("my-repo", "main", "TESTPROJ")

    mock_fetcher.branches.get_branch_commits.assert_called_once_with(
        repository="my-repo", branch="main", project="TESTPROJ", start=0, limit=1
    )
    assert result == mock_commits


def test_fetcher_get_commit(mock_fetcher):
    """Test fetcher delegates to commits."""
    mock_commit = {"id": "abc123"}
    mock_fetcher.commits.get_commit.return_value = mock_commit

    result = mock_fetcher.get_commit("my-repo", "abc123", "TESTPROJ")

    mock_fetcher.commits.get_commit.assert_called_once_with(
        repository="my-repo", commit_id="abc123", project="TESTPROJ"
    )
    assert result == mock_commit


def test_fetcher_get_commit_changes(mock_fetcher):
    """Test fetcher delegates to commits."""
    mock_changes = {"changes": []}
    mock_fetcher.commits.get_commit_changes.return_value = mock_changes

    result = mock_fetcher.get_commit_changes("my-repo", "abc123", "TESTPROJ")

    mock_fetcher.commits.get_commit_changes.assert_called_once_with(
        repository="my-repo", commit_id="abc123", project="TESTPROJ"
    )
    assert result == mock_changes


def test_fetcher_get_build_status(mock_fetcher):
    """Test fetcher delegates to builds."""
    mock_build = {"state": "SUCCESSFUL"}
    mock_fetcher.builds.get_build_status.return_value = mock_build

    result = mock_fetcher.get_build_status("abc123")

    mock_fetcher.builds.get_build_status.assert_called_once_with(commit_id="abc123")
    assert result == mock_build


def test_fetcher_close():
    """Test fetcher close delegates to client."""
    config = BitbucketServerConfig(
        url="https://bitbucket.example.com",
        auth_type="basic",
        username="testuser",
        api_token="testtoken",
    )
    mock_session = MagicMock()
    with patch.object(BitbucketServerClient, "_create_session", return_value=mock_session):
        fetcher = BitbucketServerFetcher(config)
        fetcher.close()
        mock_session.close.assert_called_once()
