class MCPAtlassianAuthenticationError(Exception):
    """Raised when Atlassian API authentication fails (401/403)."""

    pass


class BitbucketServerApiError(Exception):
    """Raised when Bitbucket Server API request fails."""

    pass
