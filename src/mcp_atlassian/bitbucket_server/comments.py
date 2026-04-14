"""Pull request comment operations for Bitbucket Server."""

import logging
from typing import Any

from ..models.bitbucket_server import BitbucketServerComment
from .client import BitbucketServerClient

logger = logging.getLogger("mcp-atlassian.bitbucket_server")


class BitbucketServerComments:
    """Bitbucket Server pull request comment operations."""

    def __init__(self, client: BitbucketServerClient) -> None:
        """Initialize Bitbucket Server pull request comment operations.

        Args:
            client: Bitbucket Server client
        """
        self.client = client

    def get_comments(
        self,
        repository: str,
        pr_id: int,
        project: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> list[dict[str, object]]:
        """Get comments on a pull request.

        Args:
            repository: Repository slug
            pr_id: Pull request ID
            project: Project key (can be omitted if provided in config)
            start: Starting index for pagination
            limit: Maximum number of results

        Returns:
            List of comment details
        """
        project = project or self._resolve_project()

        logger.debug(f"Getting comments for PR {pr_id} in {project}/{repository}")

        params: dict[str, object] = {"start": start, "limit": limit}
        path = f"/projects/{project}/repos/{repository}/pull-requests/{pr_id}/comments"
        response = self.client.get(path, params)

        values = response.get("values", [])
        return [
            BitbucketServerComment.from_api_response(c).to_simplified_dict()
            for c in values
        ]

    def add_comment(
        self,
        repository: str,
        pr_id: int,
        text: str,
        project: str | None = None,
        parent_id: int | None = None,
    ) -> BitbucketServerComment:
        """Add a comment to a pull request.

        Args:
            repository: Repository slug
            pr_id: Pull request ID
            text: Comment text
            project: Project key (can be omitted if provided in config)
            parent_id: ID of the parent comment (for replies)

        Returns:
            Created comment

        Raises:
            BitbucketServerApiError: If the API request fails
            ValueError: If required parameters are missing
        """
        project = project or self._resolve_project()

        logger.debug(f"Adding comment to PR {pr_id} in {project}/{repository}")

        path = f"/projects/{project}/repos/{repository}/pull-requests/{pr_id}/comments"

        body: dict[str, Any] = {"text": text}
        if parent_id is not None:
            body["parent"] = {"id": parent_id}

        response = self.client.post(path, json=body)

        return BitbucketServerComment.from_api_response(response)

    def _resolve_project(self) -> str:
        """Resolve project from config or raise."""
        if self.client.config.projects_filter:
            return self.client.config.projects_filter.split(",")[0].strip()
        raise ValueError(
            "Project parameter is required. Provide it explicitly or set "
            "BITBUCKET_PROJECTS_FILTER in the configuration."
        )
