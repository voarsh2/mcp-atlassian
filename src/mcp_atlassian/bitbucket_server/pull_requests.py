"""Pull request operations for Bitbucket Server."""

import logging

from ..models.bitbucket_server import BitbucketServerPullRequest
from .client import BitbucketServerClient

logger = logging.getLogger("mcp-atlassian.bitbucket_server")


class BitbucketServerPullRequests:
    """Bitbucket Server pull request operations."""

    def __init__(self, client: BitbucketServerClient) -> None:
        """Initialize Bitbucket Server pull requests operations.

        Args:
            client: Bitbucket Server client
        """
        self.client = client

    def get_pull_request(
        self, repository: str, pr_id: int, project: str | None = None
    ) -> BitbucketServerPullRequest:
        """Get details of a pull request.

        Args:
            repository: Repository slug
            pr_id: Pull request ID
            project: Project key (can be omitted if provided in config)

        Returns:
            Pull request details

        Raises:
            BitbucketServerApiError: If the API request fails
            ValueError: If required parameters are missing
        """
        project = project or self._resolve_project()

        logger.debug(f"Getting pull request {pr_id} from {project}/{repository}")

        path = f"/projects/{project}/repos/{repository}/pull-requests/{pr_id}"
        response = self.client.get(path)

        return BitbucketServerPullRequest.from_api_response(response)

    def _resolve_project(self) -> str:
        """Resolve project from config or raise."""
        if self.client.config.projects_filter:
            return self.client.config.projects_filter.split(",")[0].strip()
        raise ValueError(
            "Project parameter is required. Provide it explicitly or set "
            "BITBUCKET_PROJECTS_FILTER in the configuration."
        )
