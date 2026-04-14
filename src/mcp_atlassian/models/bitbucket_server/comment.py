"""Comment models for Bitbucket Server."""

from datetime import datetime, timezone
from typing import Any

from ..base import ApiModel
from .common import BitbucketServerUser


class BitbucketServerComment(ApiModel):
    """Bitbucket Server comment model."""

    id: int
    version: int | None = None
    text: str | None = None
    author: BitbucketServerUser | None = None
    created_date: datetime | None = None
    updated_date: datetime | None = None
    parent_id: int | None = None

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "BitbucketServerComment":
        """Create comment model from raw API data."""
        author_data = data.get("author", {})

        created_date = None
        if created_timestamp := data.get("createdDate"):
            try:
                created_date = datetime.fromtimestamp(
                    created_timestamp / 1000, tz=timezone.utc
                )
            except (ValueError, TypeError):
                pass

        updated_date = None
        if updated_timestamp := data.get("updatedDate"):
            try:
                updated_date = datetime.fromtimestamp(
                    updated_timestamp / 1000, tz=timezone.utc
                )
            except (ValueError, TypeError):
                pass

        parent_id = None
        parent_data = data.get("parent")
        if parent_data:
            parent_id = parent_data.get("id")

        return cls(
            id=data.get("id"),
            version=data.get("version"),
            text=data.get("text"),
            author=BitbucketServerUser.from_api_response(author_data)
            if author_data
            else None,
            created_date=created_date,
            updated_date=updated_date,
            parent_id=parent_id,
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert comment to a simplified dictionary."""
        result = {
            k: v
            for k, v in {
                "id": self.id,
                "text": self.text,
                "parent_id": self.parent_id,
            }.items()
            if v is not None
        }

        if self.created_date:
            result["created_date"] = self.created_date.isoformat()
        if self.updated_date:
            result["updated_date"] = self.updated_date.isoformat()

        if self.author:
            result["author"] = {
                k: v
                for k, v in {
                    "name": self.author.name,
                    "display_name": self.author.display_name,
                    "email_address": self.author.email_address,
                }.items()
                if v is not None
            }

        return result
