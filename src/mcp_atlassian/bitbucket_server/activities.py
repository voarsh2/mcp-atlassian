"""Pull request activities operations for Bitbucket Server."""

import logging
from typing import Any

from .client import BitbucketServerClient

logger = logging.getLogger("mcp-atlassian.bitbucket_server")


class BitbucketServerActivities:
    """Bitbucket Server pull request activities operations."""

    def __init__(self, client: BitbucketServerClient) -> None:
        """Initialize Bitbucket Server pull request activities operations.

        Args:
            client: Bitbucket Server client
        """
        self.client = client

    def get_activities(
        self,
        repository: str,
        pr_id: int,
        project: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> dict[str, Any]:
        """Get activities for a pull request.

        Args:
            repository: Repository slug
            pr_id: Pull request ID
            project: Project key (can be omitted if provided in config)
            start: Starting index for pagination
            limit: Maximum number of activities to return

        Returns:
            Activities for the pull request
        """
        project = project or self._resolve_project()

        logger.debug(f"Getting activities for PR {pr_id} from {project}/{repository}")

        path = (
            f"/projects/{project}/repos/{repository}/pull-requests/{pr_id}/activities"
        )
        params: dict[str, Any] = {"start": start, "limit": limit}

        response = self.client.get(path, params=params)

        return response

    def get_reviews(
        self,
        repository: str,
        pr_id: int,
        project: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Get reviews for a pull request.

        Args:
            repository: Repository slug
            pr_id: Pull request ID
            project: Project key (can be omitted if provided in config)
            start: Starting index for pagination
            limit: Maximum number of reviews to return

        Returns:
            Reviews for the pull request
        """
        activities_data = self.get_activities(
            repository=repository,
            pr_id=pr_id,
            project=project,
            start=start,
            limit=limit,
        )

        reviews = [
            activity
            for activity in activities_data.get("values", [])
            if activity.get("action") in ["APPROVED", "REVIEWED"]
        ]

        return reviews

    def _resolve_project(self) -> str:
        """Resolve project from config or raise."""
        if self.client.config.projects_filter:
            return self.client.config.projects_filter.split(",")[0].strip()
        raise ValueError(
            "Project parameter is required. Provide it explicitly or set "
            "BITBUCKET_PROJECTS_FILTER in the configuration."
        )
