"""Bitbucket Server integration for MCP Atlassian."""

import logging
from typing import Any

from ..models.bitbucket_server import (
    BitbucketServerComment,
    BitbucketServerPullRequest,
)
from .activities import BitbucketServerActivities
from .branches import BitbucketServerBranches
from .builds import BitbucketServerBuilds
from .client import BitbucketServerClient
from .comments import BitbucketServerComments
from .commits import BitbucketServerCommits
from .config import BitbucketServerConfig
from .diffs import BitbucketServerDiffs
from .files import BitbucketServerFiles
from .pull_requests import BitbucketServerPullRequests
from .search import BitbucketServerSearch

logger = logging.getLogger("mcp-atlassian.bitbucket_server")


class BitbucketServerFetcher:
    """Main interface for Bitbucket Server operations."""

    def __init__(self, config: BitbucketServerConfig) -> None:
        """Initialize Bitbucket Server fetcher.

        Args:
            config: Bitbucket Server configuration
        """
        self.config = config
        self.client = BitbucketServerClient(config)
        self.pull_requests = BitbucketServerPullRequests(self.client)
        self.comments = BitbucketServerComments(self.client)
        self.diffs = BitbucketServerDiffs(self.client)
        self.activities = BitbucketServerActivities(self.client)
        self.search = BitbucketServerSearch(self.client, config)
        self.files = BitbucketServerFiles(self.client)
        self.branches = BitbucketServerBranches(self.client)
        self.builds = BitbucketServerBuilds(self.client)
        self.commits = BitbucketServerCommits(self.client)

    def list_pull_requests(
        self,
        repository: str,
        project: str | None = None,
        state: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> list[dict[str, object]]:
        """List pull requests in a repository."""
        return self.pull_requests.list_pull_requests(
            repository=repository,
            project=project,
            state=state,
            start=start,
            limit=limit,
        )

    def get_pull_request(
        self, repository: str, pr_id: int, project: str | None = None
    ) -> BitbucketServerPullRequest:
        """Get details of a pull request."""
        return self.pull_requests.get_pull_request(
            repository=repository, pr_id=pr_id, project=project
        )

    def decline_pull_request(
        self,
        repository: str,
        pr_id: int,
        version: int,
        project: str | None = None,
        comment: str | None = None,
    ) -> BitbucketServerPullRequest:
        """Decline a pull request."""
        return self.pull_requests.decline_pull_request(
            repository=repository,
            pr_id=pr_id,
            version=version,
            project=project,
            comment=comment,
        )

    def get_comments(
        self,
        repository: str,
        pr_id: int,
        project: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> list[dict[str, object]]:
        """Get comments on a pull request."""
        return self.comments.get_comments(
            repository=repository,
            pr_id=pr_id,
            project=project,
            start=start,
            limit=limit,
        )

    def add_comment(
        self,
        repository: str,
        pr_id: int,
        text: str,
        project: str | None = None,
        parent_id: int | None = None,
    ) -> BitbucketServerComment:
        """Add a comment to a pull request."""
        return self.comments.add_comment(
            repository=repository,
            pr_id=pr_id,
            text=text,
            project=project,
            parent_id=parent_id,
        )

    def get_diff(
        self,
        repository: str,
        pr_id: int,
        project: str | None = None,
        context_lines: int = 10,
        since_revision: str | None = None,
        *,
        whitespace: bool = False,
    ) -> dict[str, Any]:
        """Get diff for a pull request."""
        return self.diffs.get_diff(
            repository=repository,
            pr_id=pr_id,
            project=project,
            context_lines=context_lines,
            since_revision=since_revision,
            whitespace=whitespace,
        )

    def get_reviews(
        self,
        repository: str,
        pr_id: int,
        project: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Get reviews for a pull request."""
        return self.activities.get_reviews(
            repository=repository,
            pr_id=pr_id,
            project=project,
            start=start,
            limit=limit,
        )

    def get_activities(
        self,
        repository: str,
        pr_id: int,
        project: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Get activities for a pull request."""
        return self.activities.get_activities(
            repository=repository,
            pr_id=pr_id,
            project=project,
            start=start,
            limit=limit,
        )

    def search_code(
        self,
        query: str,
        project_key: str | None = None,
        repository_slug: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search code content in repositories."""
        return self.search.search_code(
            query=query,
            project_key=project_key,
            repository_slug=repository_slug,
            page=page,
            limit=limit,
        )

    def search_repositories(
        self,
        query: str,
        project_key: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search for repositories."""
        return self.search.search_repositories(
            query=query,
            project_key=project_key,
            page=page,
            limit=limit,
        )

    def get_file_content(
        self,
        repository: str,
        file_path: str,
        project: str | None = None,
        at: str | None = None,
    ) -> str:
        """Get the content of a file from Bitbucket Server."""
        return self.files.get_file_content(
            repository=repository,
            file_path=file_path,
            project=project,
            at=at,
        )

    def get_branches(
        self,
        repository: str,
        project: str | None = None,
        filter_text: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Get branches for a repository."""
        return self.branches.get_branches(
            repository=repository,
            project=project,
            filter_text=filter_text,
            start=start,
            limit=limit,
        )

    def get_branch_commits(
        self,
        repository: str,
        branch: str,
        project: str | None = None,
        start: int = 0,
        limit: int = 1,
    ) -> dict[str, Any]:
        """Get commits for a branch."""
        return self.branches.get_branch_commits(
            repository=repository,
            branch=branch,
            project=project,
            start=start,
            limit=limit,
        )

    def get_commit(
        self, repository: str, commit_id: str, project: str | None = None
    ) -> dict[str, Any]:
        """Get a commit by ID."""
        return self.commits.get_commit(
            repository=repository, commit_id=commit_id, project=project
        )

    def get_commit_changes(
        self, repository: str, commit_id: str, project: str | None = None
    ) -> dict[str, Any]:
        """Get the changes made in a commit."""
        return self.commits.get_commit_changes(
            repository=repository, commit_id=commit_id, project=project
        )

    def get_build_status(self, commit_id: str) -> dict[str, Any]:
        """Get build status for a commit."""
        return self.builds.get_build_status(commit_id=commit_id)

    def get_projects(
        self,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """List all Bitbucket Server projects."""
        return self.client.get("/projects", {"start": start, "limit": limit})

    def get_repositories(
        self,
        project_key: str,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """List repositories in a project."""
        return self.client.get(
            f"/projects/{project_key}/repos",
            {"start": start, "limit": limit},
        )

    def get_personal_project(
        self,
    ) -> dict[str, Any]:
        """Get the authenticated user's personal project."""
        username = self.config.username
        if not username:
            msg = "Username not configured — cannot fetch personal project"
            raise ValueError(msg)
        return self.client.get(f"/projects/~{username}")

    def get_personal_repos(
        self,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """List repositories in the authenticated user's personal project."""
        username = self.config.username
        if not username:
            msg = "Username not configured — cannot fetch personal repos"
            raise ValueError(msg)
        return self.client.get(
            f"/projects/~{username}/repos",
            {"start": start, "limit": limit},
        )

    def close(self) -> None:
        """Close the client connection."""
        self.client.close()


__all__ = ["BitbucketServerFetcher", "BitbucketServerConfig"]
