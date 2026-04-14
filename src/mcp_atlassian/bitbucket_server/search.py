"""Module for searching Bitbucket Server repositories."""

import json
import logging
from typing import Any

from ..exceptions import BitbucketServerApiError
from .client import BitbucketServerClient
from .config import BitbucketServerConfig

logger = logging.getLogger("mcp-atlassian.bitbucket_server")


class BitbucketServerSearch:
    """Class for searching code and repositories in Bitbucket Server."""

    def __init__(
        self, client: BitbucketServerClient, config: BitbucketServerConfig
    ) -> None:
        """Initialize the BitbucketServerSearch class.

        Args:
            client: A BitbucketServerClient instance for making API calls
            config: A BitbucketServerConfig instance for configuration
        """
        self.client = client
        self.config = config

    def search_code(
        self,
        query: str,
        project_key: str | None = None,
        repository_slug: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search code content in Bitbucket Server repositories.

        Args:
            query: The search query
            project_key: Optional project key to limit search
            repository_slug: Optional repository slug to limit search
            page: Page number to start from (1-based indexing)
            limit: Maximum number of results to return per page

        Returns:
            Search results as a dictionary
        """
        search_query = query

        if project_key:
            search_query = f"project:{project_key} {search_query}"

        if repository_slug:
            search_query = f"repo:{repository_slug} {search_query}"

        data = {
            "query": search_query,
            "entities": {"code": {"start": page, "limit": limit}},
        }

        url = f"{self.client.root_url}/rest/search/latest/search"
        try:
            response = self.client.post_url(url, data=json.dumps(data))
            return response
        except Exception as e:
            logger.error(f"Error searching Bitbucket Server code: {str(e)}")
            msg = f"Failed to search code: {e}"
            raise BitbucketServerApiError(msg) from e

    def search_repositories(
        self,
        query: str,
        project_key: str | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search for repositories in Bitbucket Server.

        Args:
            query: The search query
            project_key: Optional project key to limit search
            page: Page number to start from (1-based indexing)
            limit: Maximum number of results to return per page

        Returns:
            Search results as a dictionary
        """
        search_query = project_key if project_key else query

        data = {
            "query": search_query,
            "entities": {"repositories": {"start": page, "limit": limit}},
        }

        url = f"{self.client.root_url}/rest/search/latest/search"
        try:
            response = self.client.post_url(url, data=json.dumps(data))
            return response
        except Exception as e:
            logger.error(f"Error searching Bitbucket Server repositories: {str(e)}")
            msg = f"Failed to search repositories: {e}"
            raise BitbucketServerApiError(msg) from e
