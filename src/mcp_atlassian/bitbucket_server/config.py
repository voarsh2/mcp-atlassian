"""Config for Bitbucket Server integration."""

import os
from dataclasses import dataclass

from .constants import (
    AUTH_TYPE_BASIC,
    AUTH_TYPE_PERSONAL_TOKEN,
    DEFAULT_SSL_VERIFY,
    ENV_BITBUCKET_API_TOKEN,
    ENV_BITBUCKET_PERSONAL_TOKEN,
    ENV_BITBUCKET_PROJECTS_FILTER,
    ENV_BITBUCKET_SSL_VERIFY,
    ENV_BITBUCKET_URL,
    ENV_BITBUCKET_USERNAME,
)


@dataclass
class BitbucketServerConfig:
    """Configuration for Bitbucket Server instance."""

    url: str
    auth_type: str
    username: str | None = None
    api_token: str | None = None
    personal_token: str | None = None
    ssl_verify: bool = DEFAULT_SSL_VERIFY
    projects_filter: str | None = None

    @classmethod
    def from_env(cls) -> "BitbucketServerConfig":
        """Create Bitbucket Server config from environment variables.

        Returns:
            BitbucketServerConfig instance

        Raises:
            ValueError: If required environment variables are missing
        """
        url = os.getenv(ENV_BITBUCKET_URL)
        if not url:
            msg = f"Environment variable {ENV_BITBUCKET_URL} is required"
            raise ValueError(msg)

        personal_token = os.getenv(ENV_BITBUCKET_PERSONAL_TOKEN)
        username = os.getenv(ENV_BITBUCKET_USERNAME)
        api_token = os.getenv(ENV_BITBUCKET_API_TOKEN)

        if personal_token:
            auth_type = AUTH_TYPE_PERSONAL_TOKEN
        elif username and api_token:
            auth_type = AUTH_TYPE_BASIC
        else:
            raise ValueError("No valid authentication credentials found in environment")

        ssl_verify_str = os.getenv(ENV_BITBUCKET_SSL_VERIFY, str(DEFAULT_SSL_VERIFY))
        ssl_verify = ssl_verify_str.lower() != "false"

        projects_filter = os.getenv(ENV_BITBUCKET_PROJECTS_FILTER)

        return cls(
            url=url,
            auth_type=auth_type,
            username=username,
            api_token=api_token,
            personal_token=personal_token,
            ssl_verify=ssl_verify,
            projects_filter=projects_filter,
        )

    def is_auth_configured(self) -> bool:
        """Check if authentication is fully configured.

        Returns:
            True if auth is configured, False otherwise.
        """
        if self.auth_type == AUTH_TYPE_BASIC:
            return bool(self.username and self.api_token)
        elif self.auth_type == AUTH_TYPE_PERSONAL_TOKEN:
            return bool(self.personal_token)
        return False

    def get_auth(self) -> tuple[str, str] | dict[str, str]:
        """Get authentication credentials.

        Returns:
            Tuple of (username, token) for basic auth,
            or dict with Authorization header for PAT.
        """
        if self.auth_type == AUTH_TYPE_BASIC:
            if self.username is None or self.api_token is None:
                msg = "Basic auth requires username and api_token"
                raise ValueError(msg)
            return (self.username, self.api_token)
        elif self.auth_type == AUTH_TYPE_PERSONAL_TOKEN:
            if self.personal_token is None:
                msg = "Personal token auth requires a token"
                raise ValueError(msg)
            return {"Authorization": f"Bearer {self.personal_token}"}
        else:
            msg = f"Unsupported auth type: {self.auth_type}"
            raise ValueError(msg)
