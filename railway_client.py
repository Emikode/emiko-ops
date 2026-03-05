"""
Railway Client — interface to Railway's API.

Will handle:
- Restarting services (redeploy a service)
- Triggering deployments
- Fetching deployment status

All methods are placeholders until we connect the Railway API.
Railway API docs: https://docs.railway.com/reference/public-api
"""

from utils.logger import log

# TODO: set these via .env once Railway API is connected
RAILWAY_API_TOKEN = None
RAILWAY_PROJECT_ID = None


def restart_service(service_name: str) -> str:
    """Trigger a redeploy of a specific service on Railway."""
    log.info("railway: restart requested for %s (placeholder)", service_name)
    return f"[placeholder] Restart signal sent to {service_name}. Connect Railway API to enable."


def deploy_latest() -> str:
    """Trigger a deployment of the latest commit."""
    log.info("railway: deploy latest requested (placeholder)")
    return "[placeholder] Deploy triggered. Connect Railway API to enable."


def get_deploy_status() -> str:
    """Check current deployment status."""
    return "[placeholder] Deploy status unknown. Connect Railway API to enable."
