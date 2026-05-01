from __future__ import annotations

import json
import logging
import urllib.request
import urllib.error
from typing import Any

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
_USER_AGENT = "ai-knowledge-base/1.0"


def get_repo_info(repo_full_name: str) -> dict[str, Any]:
    """Fetch basic information of a GitHub repository.

    Args:
        repo_full_name: Full repository name in the format "owner/repo".

    Returns:
        A dictionary containing star count, fork count, description,
        full name, and HTML URL of the repository.

    Raises:
        ValueError: If the repo_full_name format is invalid.
        urllib.error.HTTPError: If the GitHub API returns a non-2xx status.
        urllib.error.URLError: If the request fails due to network issues.
    """
    parts = repo_full_name.split("/")
    if len(parts) != 2 or not all(parts):
        msg = f"Invalid repository name format: {repo_full_name!r}, expected 'owner/repo'"
        raise ValueError(msg)

    url = f"{GITHUB_API_BASE}/repos/{repo_full_name}"
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})

    logger.info("Fetching repo info from %s", url)
    with urllib.request.urlopen(req, timeout=10) as response:
        data: dict[str, Any] = json.loads(response.read().decode("utf-8"))

    return {
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "description": data.get("description"),
        "full_name": data["full_name"],
        "html_url": data["html_url"],
    }
