"""Module for Bitbucket Server file operations."""

import logging

from ..exceptions import BitbucketServerApiError
from .client import BitbucketServerClient

logger = logging.getLogger("mcp-atlassian.bitbucket_server")


class BitbucketServerFiles:
    """Class for Bitbucket Server file operations."""

    def __init__(self, client: BitbucketServerClient) -> None:
        """Initialize BitbucketServerFiles with a client.

        Args:
            client: BitbucketServerClient for API communication
        """
        self.client = client

    def get_file_content(
        self,
        repository: str,
        file_path: str,
        project: str | None = None,
        at: str | None = None,
    ) -> str:
        """Get the content of a file from Bitbucket Server.

        Args:
            repository: Repository slug
            file_path: Path to the file within the repository
            project: Project key (optional if provided in config)
            at: Branch or commit to get the file from

        Returns:
            Raw content of the file as a string

        Raises:
            BitbucketServerApiError: If the API call fails
        """
        project = project or self._resolve_project()

        url = (
            f"{self.client.root_url}/rest/api/1.0/projects/{project}"
            f"/repos/{repository}/raw/{file_path}"
        )

        params = {"at": at} if at else None

        try:
            response = self.client.session.get(url, params=params)
            response.raise_for_status()
            return response.text
        except Exception as e:
            error_msg = f"Failed to get file content: {str(e)}"
            logger.error(error_msg)
            raise BitbucketServerApiError(error_msg) from e

    def _resolve_project(self) -> str:
        """Resolve project from config or raise."""
        if self.client.config.projects_filter:
            return self.client.config.projects_filter.split(",")[0].strip()
        raise ValueError(
            "Project parameter is required. Provide it explicitly or set "
            "BITBUCKET_PROJECTS_FILTER in the configuration."
        )
