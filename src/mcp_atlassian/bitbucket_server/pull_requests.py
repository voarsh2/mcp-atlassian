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

    def list_pull_requests(
        self,
        repository: str,
        project: str | None = None,
        state: str | None = None,
        start: int = 0,
        limit: int = 25,
    ) -> list[dict[str, object]]:
        """List pull requests in a repository.

        Args:
            repository: Repository slug
            project: Project key (can be omitted if provided in config)
            state: Filter by state (OPEN, MERGED, DECLINED)
            start: Starting index for pagination
            limit: Maximum number of results

        Returns:
            List of pull request details
        """
        project = project or self._resolve_project()

        logger.debug(f"Listing pull requests in {project}/{repository}")

        params: dict[str, object] = {"start": start, "limit": limit}
        if state:
            params["state"] = state

        path = f"/projects/{project}/repos/{repository}/pull-requests"
        response = self.client.get(path, params)

        values = response.get("values", [])
        return [
            BitbucketServerPullRequest.from_api_response(pr).to_simplified_dict()
            for pr in values
        ]

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

    def decline_pull_request(
        self,
        repository: str,
        pr_id: int,
        version: int,
        project: str | None = None,
        comment: str | None = None,
    ) -> BitbucketServerPullRequest:
        """Decline a pull request.

        Bitbucket Server/Data Center expects a POST to the decline endpoint with
        the current pull request version. The version may be sent as a query
        parameter or in the JSON body; this implementation sends it in both
        places for compatibility with Server/DC deployments.

        Args:
            repository: Repository slug
            pr_id: Pull request ID
            version: Current pull request version
            project: Project key (can be omitted if provided in config)
            comment: Optional comment to add while declining the pull request

        Returns:
            Updated pull request details
        """
        project = project or self._resolve_project()

        logger.debug(f"Declining pull request {pr_id} from {project}/{repository}")

        path = f"/projects/{project}/repos/{repository}/pull-requests/{pr_id}/decline"
        payload: dict[str, object] = {"version": version}
        if comment:
            payload["comment"] = comment

        response = self.client.post(path, json=payload, params={"version": version})
        return BitbucketServerPullRequest.from_api_response(response)

    def _resolve_project(self) -> str:
        """Resolve project from config or raise."""
        if self.client.config.projects_filter:
            return self.client.config.projects_filter.split(",")[0].strip()
        raise ValueError(
            "Project parameter is required. Provide it explicitly or set "
            "BITBUCKET_PROJECTS_FILTER in the configuration."
        )
