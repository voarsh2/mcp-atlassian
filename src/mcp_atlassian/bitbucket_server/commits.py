"""Commit operations for Bitbucket Server."""

import logging
from typing import Any

from .client import BitbucketServerClient

logger = logging.getLogger("mcp-atlassian.bitbucket_server")


class BitbucketServerCommits:
    """Bitbucket Server commit operations."""

    def __init__(self, client: BitbucketServerClient) -> None:
        """Initialize Bitbucket Server commit operations.

        Args:
            client: Bitbucket Server client
        """
        self.client = client

    def get_commit(
        self, repository: str, commit_id: str, project: str | None = None
    ) -> dict[str, Any]:
        """Get a commit by ID.

        Args:
            repository: Repository slug
            commit_id: Commit ID (SHA)
            project: Project key (can be omitted if provided in config)

        Returns:
            Commit data
        """
        project = project or self._resolve_project()

        logger.debug(f"Getting commit {commit_id} from {project}/{repository}")

        path = f"/projects/{project}/repos/{repository}/commits/{commit_id}"
        response = self.client.get(path)

        return response

    def get_commit_changes(
        self, repository: str, commit_id: str, project: str | None = None
    ) -> dict[str, Any]:
        """Get the changes made in a commit.

        Args:
            repository: Repository slug
            commit_id: Commit ID (SHA)
            project: Project key (can be omitted if provided in config)

        Returns:
            Changes made in the commit
        """
        project = project or self._resolve_project()

        logger.debug(
            f"Getting changes for commit {commit_id} from {project}/{repository}"
        )

        path = f"/projects/{project}/repos/{repository}/commits/{commit_id}/changes"
        response = self.client.get(path)

        return response

    def _resolve_project(self) -> str:
        """Resolve project from config or raise."""
        if self.client.config.projects_filter:
            return self.client.config.projects_filter.split(",")[0].strip()
        raise ValueError(
            "Project parameter is required. Provide it explicitly or set "
            "BITBUCKET_PROJECTS_FILTER in the configuration."
        )
