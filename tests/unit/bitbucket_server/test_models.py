"""Tests for Bitbucket Server models."""

from mcp_atlassian.models.bitbucket_server import (
    BitbucketServerComment,
    BitbucketServerPullRequest,
    BitbucketServerPullRequestReviewer,
    BitbucketServerRef,
    BitbucketServerRepository,
    BitbucketServerUser,
)


class TestBitbucketServerUser:
    """Tests for BitbucketServerUser model."""

    def test_from_api_response(self):
        data = {
            "id": 1,
            "name": "jdoe",
            "displayName": "John Doe",
            "emailAddress": "john@example.com",
            "active": True,
        }
        user = BitbucketServerUser.from_api_response(data)
        assert user.id == 1
        assert user.name == "jdoe"
        assert user.display_name == "John Doe"
        assert user.email_address == "john@example.com"
        assert user.active is True

    def test_from_api_response_empty(self):
        user = BitbucketServerUser.from_api_response({})
        assert user.id is None
        assert user.name is None


class TestBitbucketServerRepository:
    """Tests for BitbucketServerRepository model."""

    def test_from_api_response(self):
        data = {
            "id": 1,
            "slug": "my-repo",
            "name": "My Repository",
            "project": {"key": "TEST", "name": "Test Project"},
        }
        repo = BitbucketServerRepository.from_api_response(data)
        assert repo.id == 1
        assert repo.slug == "my-repo"
        assert repo.project_key == "TEST"


class TestBitbucketServerRef:
    """Tests for BitbucketServerRef model."""

    def test_from_api_response(self):
        data = {
            "id": "refs/heads/main",
            "displayId": "main",
            "latestCommit": "abc123",
            "repository": {"id": 1, "slug": "my-repo", "name": "My Repo", "project": {}},
        }
        ref = BitbucketServerRef.from_api_response(data)
        assert ref.id == "refs/heads/main"
        assert ref.display_id == "main"
        assert ref.latest_commit == "abc123"
        assert ref.repository is not None
        assert ref.repository.slug == "my-repo"


class TestBitbucketServerPullRequest:
    """Tests for BitbucketServerPullRequest model."""

    def test_from_api_response(self):
        data = {
            "id": 1,
            "version": 3,
            "title": "Add feature",
            "description": "This adds a feature",
            "state": "OPEN",
            "open": True,
            "closed": False,
            "createdDate": 1700000000000,
            "updatedDate": 1700001000000,
            "fromRef": {"id": "refs/heads/feature", "displayId": "feature"},
            "toRef": {
                "id": "refs/heads/main",
                "displayId": "main",
                "repository": {"id": 1, "slug": "my-repo", "name": "My Repo", "project": {"key": "TEST", "name": "Test"}},
            },
            "author": {"id": 1, "name": "jdoe", "displayName": "John Doe", "emailAddress": "john@example.com", "active": True},
            "reviewers": [{"user": {"id": 2, "name": "reviewer1", "displayName": "Reviewer One"}, "status": "APPROVED"}],
        }
        pr = BitbucketServerPullRequest.from_api_response(data)
        assert pr.id == 1
        assert pr.title == "Add feature"
        assert pr.state == "OPEN"
        assert pr.open is True
        assert len(pr.reviewers) == 1
        assert pr.reviewers[0].status == "APPROVED"

    def test_to_simplified_dict(self):
        data = {
            "id": 1,
            "title": "Test PR",
            "state": "OPEN",
            "fromRef": {"id": "refs/heads/feature", "displayId": "feature"},
            "toRef": {"id": "refs/heads/main", "displayId": "main", "repository": {}},
            "author": {"id": 1, "name": "jdoe", "displayName": "John Doe", "emailAddress": "john@example.com", "active": True},
            "reviewers": [],
        }
        pr = BitbucketServerPullRequest.from_api_response(data)
        simplified = pr.to_simplified_dict()
        assert simplified["id"] == 1
        assert simplified["title"] == "Test PR"
        assert "from_ref" in simplified
        assert "to_ref" in simplified
        assert "author" in simplified

    def test_invalid_id_raises(self):
        data = {"id": "not-an-int", "fromRef": {}, "toRef": {"repository": {}}, "author": {}, "reviewers": []}
        import pytest
        with pytest.raises(ValueError, match="Pull request ID must be an integer"):
            BitbucketServerPullRequest.from_api_response(data)


class TestBitbucketServerComment:
    """Tests for BitbucketServerComment model."""

    def test_from_api_response(self):
        data = {
            "id": 100,
            "version": 1,
            "text": "Nice work!",
            "createdDate": 1700000000000,
            "updatedDate": 1700001000000,
            "author": {"id": 1, "name": "jdoe", "displayName": "John Doe", "emailAddress": "john@example.com", "active": True},
            "parent": {"id": 50},
        }
        comment = BitbucketServerComment.from_api_response(data)
        assert comment.id == 100
        assert comment.text == "Nice work!"
        assert comment.parent_id == 50
        assert comment.author is not None
        assert comment.author.name == "jdoe"

    def test_to_simplified_dict(self):
        data = {
            "id": 100,
            "text": "Comment text",
            "createdDate": 1700000000000,
            "author": {"name": "jdoe", "displayName": "John Doe", "emailAddress": "john@example.com"},
        }
        comment = BitbucketServerComment.from_api_response(data)
        simplified = comment.to_simplified_dict()
        assert simplified["id"] == 100
        assert simplified["text"] == "Comment text"
        assert "created_date" in simplified
        assert "author" in simplified
