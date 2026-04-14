"""Branch operations for Bitbucket Server."""

import logging
from typing import Any

from .client import BitbucketServerClient

logger = logging.getLogger("mcp-atlassian.bitbucket_server")


class BitbucketServerBranches:
    """Bitbucket Server branch operations."""

    def __init__(self, client: BitbucketServerClient) -> None:
        """Initialize Bitbucket Server branch operations.

        Args:
            client: Bitbucket Server client
        """
        self.client = client

    def get_branches(
        self,
        repository: str,
        project: str | None = None,
        filter_text: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Get branches for a repository.

        Args:
            repository: Repository slug
            project: Project key (can be omitted if provided in config)
            filter_text: Optional text to filter branches by name
            start: Starting index for pagination
            limit: Maximum number of branches to return

        Returns:
            Branch data
        """
        project = project or self._resolve_project()

        logger.debug(f"Getting branches for {project}/{repository}")

        path = f"/projects/{project}/repos/{repository}/branches"
        params: dict[str, Any] = {"start": start, "limit": limit}

        if filter_text:
            params["filterText"] = filter_text

        response = self.client.get(path, params=params)

        return response

    def get_branch_commits(
        self,
        repository: str,
        branch: str,
        project: str | None = None,
        start: int = 0,
        limit: int = 1,
    ) -> dict[str, Any]:
        """Get commits for a branch.

        Args:
            repository: Repository slug
            branch: Branch name or ref (e.g., 'master', 'develop')
            project: Project key (can be omitted if provided in config)
            start: Starting index for pagination
            limit: Maximum number of commits to return

        Returns:
            Commit data
        """
        project = project or self._resolve_project()

        branch_ref = branch
        if not branch.startswith("refs/"):
            branch_ref = f"refs/heads/{branch}"

        logger.debug(
            f"Getting commits for branch {branch_ref} in {project}/{repository}"
        )

        path = f"/projects/{project}/repos/{repository}/commits"
        params: dict[str, Any] = {
            "until": branch_ref,
            "start": start,
            "limit": limit,
        }

        response = self.client.get(path, params=params)

        return response

    def _resolve_project(self) -> str:
        """Resolve project from config or raise."""
        if self.client.config.projects_filter:
            return self.client.config.projects_filter.split(",")[0].strip()
        raise ValueError(
            "Project parameter is required. Provide it explicitly or set "
            "BITBUCKET_PROJECTS_FILTER in the configuration."
        )
