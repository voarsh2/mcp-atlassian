"""Bitbucket Server FastMCP server instance and tool definitions."""

import json
import logging
from typing import Annotated

from fastmcp import Context, FastMCP
from pydantic import Field

from mcp_atlassian.servers.dependencies import get_bitbucket_fetcher
from mcp_atlassian.utils.decorators import check_write_access

logger = logging.getLogger(__name__)

bitbucket_mcp = FastMCP(
    name="Bitbucket MCP Service",
    instructions="Tools for Bitbucket Server/Data Center.",
)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_pull_requests"},
    annotations={"title": "List Pull Requests", "readOnlyHint": True},
)
async def list_pull_requests(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    state: Annotated[
        str | None,
        Field(description="Filter by state (OPEN, MERGED, DECLINED)"),
    ] = None,
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[
        int, Field(description="Maximum number of PRs to return")
    ] = 25,
) -> str:
    """List pull requests in a repository."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    prs = bitbucket.list_pull_requests(
        repository=repository,
        project=project,
        state=state,
        start=start,
        limit=limit,
    )
    return json.dumps(prs, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_pull_requests"},
    annotations={"title": "Get Pull Request", "readOnlyHint": True},
)
async def get_pull_request(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    pr_id: Annotated[int, Field(description="Pull request ID")],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
) -> str:
    """Get details of a pull request."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    pr = bitbucket.get_pull_request(
        repository=repository, pr_id=pr_id, project=project
    )
    return json.dumps(pr.to_simplified_dict(), indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_pull_requests"},
    annotations={"title": "Get Pull Request Comments", "readOnlyHint": True},
)
async def get_comments(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    pr_id: Annotated[int, Field(description="Pull request ID")],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[
        int, Field(description="Maximum number of comments to return")
    ] = 25,
) -> str:
    """Get comments on a pull request."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    comments = bitbucket.get_comments(
        repository=repository,
        pr_id=pr_id,
        project=project,
        start=start,
        limit=limit,
    )
    return json.dumps(comments, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "write", "toolset:bitbucket_pull_requests"},
    annotations={"title": "Add Pull Request Comment", "readOnlyHint": False},
)
@check_write_access
async def add_comment(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    pr_id: Annotated[int, Field(description="Pull request ID")],
    text: Annotated[str, Field(description="Comment text")],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    parent_id: Annotated[
        int | None, Field(description="Parent comment ID for replies")
    ] = None,
) -> str:
    """Add a comment to a pull request."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    comment = bitbucket.add_comment(
        repository=repository,
        pr_id=pr_id,
        text=text,
        project=project,
        parent_id=parent_id,
    )
    return json.dumps(comment.to_simplified_dict(), indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "write", "toolset:bitbucket_pull_requests"},
    annotations={"title": "Decline Pull Request", "readOnlyHint": False},
)
@check_write_access
async def decline_pull_request(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    pr_id: Annotated[int, Field(description="Pull request ID")],
    version: Annotated[
        int,
        Field(description="Current pull request version required by Bitbucket"),
    ],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    comment: Annotated[
        str | None,
        Field(description="Optional comment to add when declining the pull request"),
    ] = None,
) -> str:
    """Decline a pull request."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    pr = bitbucket.decline_pull_request(
        repository=repository,
        pr_id=pr_id,
        version=version,
        project=project,
        comment=comment,
    )
    return json.dumps(pr.to_simplified_dict(), indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_pull_requests"},
    annotations={"title": "Get Pull Request Diff", "readOnlyHint": True},
)
async def get_diff(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    pr_id: Annotated[int, Field(description="Pull request ID")],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    context_lines: Annotated[
        int, Field(description="Number of context lines (default 10)")
    ] = 10,
    since_revision: Annotated[
        str | None, Field(description="Only show changes since this revision")
    ] = None,
    *,
    whitespace: Annotated[
        bool, Field(description="Ignore whitespace changes")
    ] = False,
) -> str:
    """Get diff for a pull request."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    diff = bitbucket.get_diff(
        repository=repository,
        pr_id=pr_id,
        project=project,
        context_lines=context_lines,
        since_revision=since_revision,
        whitespace=whitespace,
    )
    return json.dumps(diff, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_pull_requests"},
    annotations={"title": "Get Pull Request Reviews", "readOnlyHint": True},
)
async def get_reviews(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    pr_id: Annotated[int, Field(description="Pull request ID")],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[
        int, Field(description="Maximum number of reviews to return")
    ] = 25,
) -> str:
    """Get reviews for a pull request."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    reviews = bitbucket.get_reviews(
        repository=repository,
        pr_id=pr_id,
        project=project,
        start=start,
        limit=limit,
    )
    return json.dumps(reviews, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_pull_requests"},
    annotations={"title": "Get Pull Request Activities", "readOnlyHint": True},
)
async def get_activities(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    pr_id: Annotated[int, Field(description="Pull request ID")],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[
        int, Field(description="Maximum number of activities to return")
    ] = 25,
) -> str:
    """Get activities for a pull request."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    activities = bitbucket.get_activities(
        repository=repository,
        pr_id=pr_id,
        project=project,
        start=start,
        limit=limit,
    )
    return json.dumps(activities, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_search"},
    annotations={"title": "Search Code", "readOnlyHint": True},
)
async def search_code(
    ctx: Context,
    query: Annotated[str, Field(description="The search query")],
    project_key: Annotated[
        str | None, Field(description="Project key to limit search")
    ] = None,
    repository_slug: Annotated[
        str | None, Field(description="Repository slug to limit search")
    ] = None,
    page: Annotated[int, Field(description="Page number (1-based)")] = 1,
    limit: Annotated[int, Field(description="Maximum results per page")] = 10,
) -> str:
    """Search code content in Bitbucket Server repositories."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    results = bitbucket.search_code(
        query=query,
        project_key=project_key,
        repository_slug=repository_slug,
        page=page,
        limit=limit,
    )
    return json.dumps(results, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_search"},
    annotations={"title": "Search Repositories", "readOnlyHint": True},
)
async def search_repositories(
    ctx: Context,
    query: Annotated[str, Field(description="The search query")],
    project_key: Annotated[
        str | None, Field(description="Project key to limit search")
    ] = None,
    page: Annotated[int, Field(description="Page number (1-based)")] = 1,
    limit: Annotated[int, Field(description="Maximum results per page")] = 10,
) -> str:
    """Search for repositories in Bitbucket Server."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    results = bitbucket.search_repositories(
        query=query,
        project_key=project_key,
        page=page,
        limit=limit,
    )
    return json.dumps(results, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_files"},
    annotations={"title": "Get File Content", "readOnlyHint": True},
)
async def get_file_content(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    file_path: Annotated[
        str, Field(description="Path to the file within the repository")
    ],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    at: Annotated[
        str | None,
        Field(description="Branch or commit to get the file from"),
    ] = None,
) -> str:
    """Get the content of a file from Bitbucket Server."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    content = bitbucket.get_file_content(
        repository=repository,
        file_path=file_path,
        project=project,
        at=at,
    )
    return content


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_branches"},
    annotations={"title": "Get Branches", "readOnlyHint": True},
)
async def get_branches(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    filter_text: Annotated[
        str | None, Field(description="Filter branches by name")
    ] = None,
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[
        int, Field(description="Maximum number of branches to return")
    ] = 25,
) -> str:
    """Get branches for a repository."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    branches = bitbucket.get_branches(
        repository=repository,
        project=project,
        filter_text=filter_text,
        start=start,
        limit=limit,
    )
    return json.dumps(branches, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_branches"},
    annotations={"title": "Get Branch Commits", "readOnlyHint": True},
)
async def get_branch_commits(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    branch: Annotated[
        str, Field(description="Branch name or ref (e.g., 'master', 'develop')")
    ],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[int, Field(description="Maximum number of commits to return")] = 1,
) -> str:
    """Get commits for a branch."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    commits = bitbucket.get_branch_commits(
        repository=repository,
        branch=branch,
        project=project,
        start=start,
        limit=limit,
    )
    return json.dumps(commits, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_commits"},
    annotations={"title": "Get Commit", "readOnlyHint": True},
)
async def get_commit(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    commit_id: Annotated[str, Field(description="Commit ID (SHA)")],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
) -> str:
    """Get a commit by ID."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    commit = bitbucket.get_commit(
        repository=repository, commit_id=commit_id, project=project
    )
    return json.dumps(commit, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_commits"},
    annotations={"title": "Get Commit Changes", "readOnlyHint": True},
)
async def get_commit_changes(
    ctx: Context,
    repository: Annotated[
        str, Field(description="Repository slug (e.g., 'my-repo')")
    ],
    commit_id: Annotated[str, Field(description="Commit ID (SHA)")],
    project: Annotated[
        str | None,
        Field(description="Project key (optional if BITBUCKET_PROJECTS_FILTER set)"),
    ] = None,
) -> str:
    """Get the changes made in a commit."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    changes = bitbucket.get_commit_changes(
        repository=repository, commit_id=commit_id, project=project
    )
    return json.dumps(changes, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_builds"},
    annotations={"title": "Get Build Status", "readOnlyHint": True},
)
async def get_build_status(
    ctx: Context,
    commit_id: Annotated[str, Field(description="Commit ID (SHA)")],
) -> str:
    """Get build status for a commit."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    build_status = bitbucket.get_build_status(commit_id=commit_id)
    return json.dumps(build_status, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_search"},
    annotations={"title": "Get Projects", "readOnlyHint": True},
)
async def get_projects(
    ctx: Context,
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[
        int, Field(description="Maximum number of projects to return")
    ] = 25,
) -> str:
    """List all Bitbucket Server projects."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    projects = bitbucket.get_projects(start=start, limit=limit)
    return json.dumps(projects, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_search"},
    annotations={"title": "Get Repositories", "readOnlyHint": True},
)
async def get_repositories(
    ctx: Context,
    project_key: Annotated[str, Field(description="Project key")],
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[int, Field(description="Maximum number of repos to return")] = 25,
) -> str:
    """List repositories in a Bitbucket Server project."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    repos = bitbucket.get_repositories(
        project_key=project_key, start=start, limit=limit
    )
    return json.dumps(repos, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_search"},
    annotations={"title": "Get Personal Project", "readOnlyHint": True},
)
async def get_personal_project(
    ctx: Context,
) -> str:
    """Get the authenticated user's personal project."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    project = bitbucket.get_personal_project()
    return json.dumps(project, indent=2)


@bitbucket_mcp.tool(
    tags={"bitbucket", "read", "toolset:bitbucket_search"},
    annotations={"title": "Get Personal Repositories", "readOnlyHint": True},
)
async def get_personal_repos(
    ctx: Context,
    start: Annotated[int, Field(description="Starting index for pagination")] = 0,
    limit: Annotated[int, Field(description="Maximum number of repos to return")] = 25,
) -> str:
    """List repositories in the authenticated user's personal project."""
    bitbucket = await get_bitbucket_fetcher(ctx)
    repos = bitbucket.get_personal_repos(start=start, limit=limit)
    return json.dumps(repos, indent=2)
