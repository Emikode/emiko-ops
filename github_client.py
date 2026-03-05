"""
GitHub Client — interface to GitHub's API.

Will handle:
- Pushing configuration changes to PythonFX repo
- Reading config files
- Triggering workflows

All methods are placeholders until we connect the GitHub API.
"""

from utils.logger import log

# TODO: set these via .env once GitHub API is connected
GITHUB_TOKEN = None
REPO_OWNER = None
REPO_NAME = None


def push_config(file_path: str, content: str, message: str) -> str:
    """Commit and push a config file change to the repo."""
    log.info("github: push_config requested for %s (placeholder)", file_path)
    return f"[placeholder] Would push {file_path}. Connect GitHub API to enable."


def get_config(file_path: str) -> str:
    """Read a config file from the repo."""
    log.info("github: get_config requested for %s (placeholder)", file_path)
    return f"[placeholder] Would read {file_path}. Connect GitHub API to enable."
